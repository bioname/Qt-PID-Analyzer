#!/usr/bin/env python3
"""Top-level launcher — run from the project root: python run.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.main import main

main()
