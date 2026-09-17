#!/usr/bin/env python3
"""
把 stdio MCP 转到网关的 streamable-http。

方法用途与业务含义：
插件只收用户名密码明文，在本地做 Base64 后填标准 `Authorization: Basic <base64>`，
MCP 服务端鉴权方式不变。

参数说明：
- --port: 网关端口。
- --auth: mcp / langfuse / gitlab / jumpserver / none。

异常或错误说明：
- 缺少主机或凭据时向 stderr 报错并以非 0 退出。
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request


def encode_basic(user: str, password: str) -> str:
    """
    将用户名密码编码为 HTTP Basic 的 Base64 凭据部分。

    方法用途与业务含义：
    生成 MCP 服务端仍在使用的 `Basic <base64(user:pass)>` 格式，不把明文 user:pass 直接发给网关。

    参数说明：
    - user: 用户名，不能为空。
    - password: 密码，不能为空。

    返回值说明：
    - 不含 `Basic ` 前缀的 Base64 字符串。

    异常或错误说明：
    - 用户名或密码为空时抛出 ValueError。
    """

    if not user or not password:
        raise ValueError("username/password 不能为空")
    return base64.b64encode(f"{user}:{password}".encode("utf-8")).decode("ascii")


def _auth_header(auth: str) -> str | None:
    if auth == "none":
        return None
    if auth == "gitlab":
        token = (os.environ.get("AIHELP_GITLAB_MCP_TOKEN") or "").strip()
        if not token:
            raise ValueError("缺少 AIHELP_GITLAB_MCP_TOKEN")
        return f"Bearer {token}"
    if auth == "jumpserver":
        key = (os.environ.get("JUMPSERVER_MCP_ACCESSKEY") or "").strip()
        if not key:
            raise ValueError("缺少 JUMPSERVER_MCP_ACCESSKEY")
        return f"AccessKey {key}"
    if auth == "langfuse":
        user = (os.environ.get("AIHELP_LANGFUSE_MCP_USER") or "").strip()
        password = (os.environ.get("AIHELP_LANGFUSE_MCP_PASS") or "").strip()
        return f"Basic {encode_basic(user, password)}"
    user = (os.environ.get("AIHELP_MCP_USER") or "").strip()
    password = (os.environ.get("AIHELP_MCP_PASS") or "").strip()
    return f"Basic {encode_basic(user, password)}"


def _read_stdio_message() -> bytes | None:
    first = sys.stdin.buffer.readline()
    if not first:
        return None
    if first.lstrip().startswith(b"{"):
        return first.strip()
    headers = first
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        headers += line
        if line in (b"\r\n", b"\n"):
            break
    length = 0
    for raw in headers.splitlines():
        if raw.lower().startswith(b"content-length:"):
            length = int(raw.split(b":", 1)[1].strip())
            break
    if length <= 0:
        return None
    body = sys.stdin.buffer.read(length)
    return body if body else None


def _write_stdio_message(payload: bytes) -> None:
    sys.stdout.buffer.write(f"Content-Length: {len(payload)}\r\n\r\n".encode("ascii"))
    sys.stdout.buffer.write(payload)
    sys.stdout.buffer.flush()


def _read_sse_data(resp) -> bytes:
    """
    从 streamable-http 的 SSE 响应中读取第一条 message。

    方法用途与业务含义：
    FastMCP 的 POST /mcp 常返回 `text/event-stream`，连接会保持打开。
    不能 `read()` 等到 EOF，否则会卡到 MCP 启动超时。读到第一条 `data:` 事件即可。

    参数说明：
    - resp: urllib 响应对象，需支持 readline。

    返回值说明：
    - SSE `data:` 字段的原始 JSON 字节。没有 data 时返回空字节。
    """

    chunks: list[str] = []
    while True:
        line = resp.readline()
        if not line:
            break
        text = line.decode("utf-8", errors="replace").rstrip("\r\n")
        if text.startswith("data:"):
            chunks.append(text[5:].lstrip())
        elif text == "" and chunks:
            break
    return "\n".join(chunks).encode("utf-8")


def _post_json(url: str, body: bytes, headers: dict[str, str], session_id: str | None) -> tuple[bytes, str | None]:
    req_headers = dict(headers)
    if session_id:
        req_headers["Mcp-Session-Id"] = session_id
    request = urllib.request.Request(url, data=body, headers=req_headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=120) as resp:
            new_session = resp.headers.get("Mcp-Session-Id") or session_id
            content_type = resp.headers.get("Content-Type") or ""
            if "text/event-stream" in content_type.lower():
                payload = _read_sse_data(resp)
            else:
                payload = resp.read()
            return payload, new_session
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        error = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32000, "message": f"MCP HTTP {exc.code}: {detail[:500]}"},
        }
        try:
            parsed = json.loads(body.decode("utf-8"))
            if isinstance(parsed, dict) and "id" in parsed:
                error["id"] = parsed["id"]
        except Exception:
            pass
        return json.dumps(error).encode("utf-8"), session_id


def main() -> int:
    parser = argparse.ArgumentParser(description="AIHelp Bridge stdio 到 HTTP MCP 转发")
    parser.add_argument("--port", required=True, type=int)
    parser.add_argument("--auth", default="mcp", choices=["mcp", "langfuse", "gitlab", "jumpserver", "none"])
    args = parser.parse_args()

    host = (os.environ.get("AIHELP_MCP_HOST") or "").strip()
    if not host:
        print("缺少 AIHELP_MCP_HOST", file=sys.stderr)
        return 1
    try:
        authorization = _auth_header(args.auth)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    url = f"http://{host}:{args.port}/mcp"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if authorization:
        headers["Authorization"] = authorization

    session_id = None
    while True:
        message = _read_stdio_message()
        if message is None:
            return 0
        payload, session_id = _post_json(url, message, headers, session_id)
        try:
            parsed = json.loads(message.decode("utf-8"))
        except Exception:
            parsed = None
        if isinstance(parsed, dict) and parsed.get("id") is None:
            continue
        _write_stdio_message(payload)


if __name__ == "__main__":
    raise SystemExit(main())
