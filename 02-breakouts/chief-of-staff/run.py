#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "claude-agent-sdk>=0.1.41",
#     "python-dotenv>=1.0.0",
# ]
# ///
"""Entry point for the Chief of Staff breakout. Don't edit this — edit config.py."""

import sys
from pathlib import Path

# Make _shared importable regardless of where you run this from.
sys.path.insert(0, str(Path(__file__).parent.parent))

import config  # noqa: E402
from _shared.agent_base import run  # noqa: E402

run(config)
