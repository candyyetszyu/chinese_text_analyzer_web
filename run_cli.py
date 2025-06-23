#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for the Chinese Text Analyzer CLI Application
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli.menu import TextAnalyzerMenu

if __name__ == '__main__':
    print("Starting Chinese Text Analyzer CLI...")
    menu = TextAnalyzerMenu()
    menu.run() 