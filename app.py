"""Entry point for Render deployment."""

import os
import sys

# Add src to path so mcp_justwatch can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mcp_justwatch.server import mcp  # noqa: E402

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "10000")),
    )
