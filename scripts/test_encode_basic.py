#!/usr/bin/env python3
from __future__ import annotations

import base64
import unittest

from mcp_http_stdio import encode_basic


class TestEncodeBasic(unittest.TestCase):
    def test_matches_standard_basic(self) -> None:
        token = encode_basic("alice", "s3cret")
        self.assertEqual(token, base64.b64encode(b"alice:s3cret").decode("ascii"))
        self.assertNotIn(":", token)

    def test_rejects_empty(self) -> None:
        with self.assertRaises(ValueError):
            encode_basic("", "x")
        with self.assertRaises(ValueError):
            encode_basic("x", "")
