#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for the Chinese Text Analyzer Web Application
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.web.app import app

if __name__ == '__main__':
    print("Starting Chinese Text Analyzer Web Application...")
    print("Visit: http://localhost:3000")
    app.run(debug=True, host='0.0.0.0', port=3000) 