#!/usr/bin/env python3
"""Entry point for the Warmup breakout. Edit config.py, not this."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import config  # noqa: E402
from _shared.agent_base import run  # noqa: E402

run(config)
