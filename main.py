#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entrypoint for Immobiliare Giancani - Bot Pillole Immobiliari e Legali.
Direzione Tecnica, Regia e Personal Branding: IMMOBILIARE GIANCANI
"""
import sys
import subprocess

if __name__ == "__main__":
    cmd = [sys.executable, "bot_pillole_immobiliari_video.py"] + sys.argv[1:]
    sys.exit(subprocess.call(cmd))
