#!/usr/bin/env python3
"""Entry point. Edit config.py, not this. Don't forget to update the path
below if you move this to a deeper directory level."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import config  # noqa: E402
from _shared.agent_base import run  # noqa: E402

run(config)
