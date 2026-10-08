#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entrypoint for Antonio Giancani Mindset Reels Bot.
"""
import sys
import subprocess

if __name__ == "__main__":
    cmd = [sys.executable, "bot_mindset_antonio_giancani.py", "--auto-publish"] + sys.argv[1:]
    sys.exit(subprocess.call(cmd))
