"""Entry point for python -m mcp_justwatch."""

import logging
import os
import sys
import traceback

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

try:
    from mcp_justwatch.server import main

    logger.info("Starting mcp-justwatch server...")
    main()
except Exception:
    traceback.print_exc()
    sys.exit(1)
