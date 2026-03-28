"""ASGI app entry point for Render deployment."""

import os
import sys

# Add src to path so mcp_justwatch can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mcp_justwatch.server import mcp  # noqa: E402

app = mcp.http_app()
