"""Entry point for python -m mcp_justwatch."""

import sys

from mcp_justwatch.server import main

if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback

        traceback.print_exc()
        sys.exit(1)
