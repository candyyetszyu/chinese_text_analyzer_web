#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configure matplotlib to properly display Chinese characters
"""

import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

def find_chinese_font():
    """
    Find an available Chinese font in the system.
    Returns font path or None if no suitable font found.
    """
    # Common Chinese font paths on macOS
    mac_font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Songti.ttc",
        "/Library/Fonts/Arial Unicode.ttf"
    ]
    
    # Check which fonts exist
    for font_path in mac_font_paths:
        if os.path.exists(font_path):
            print(f"Found Chinese font: {font_path}")
            return font_path
    
    # If none of the predefined paths work, try to find any Chinese font
    print("Searching for other Chinese fonts...")
    all_fonts = fm.findSystemFonts()
    for font in all_fonts:
        # Look for font files that might contain Chinese characters
        font_lower = font.lower()
        if any(name in font_lower for name in ['ping', 'hei', 'song', 'ming', 'kaiti', 'fangsong', 'yahei', 'simhei', 'simsun']):
            print(f"Found potential Chinese font: {font}")
            return font
    
    return None

def configure_matplotlib_chinese():
    """
    Configure matplotlib to use Chinese fonts and return the font path used.
    """
    # Find a suitable Chinese font
    font_path = find_chinese_font()
    
    if font_path:
        # Create font properties object
        font_prop = fm.FontProperties(fname=font_path)
        
        # Configure matplotlib global settings
        plt.rcParams['font.family'] = font_prop.get_name()
        plt.rcParams['axes.unicode_minus'] = False  # Correctly display minus sign
        
        # Add the font to matplotlib's font manager
        font_list = fm.fontManager.ttflist
        font_list.extend([fm.FontEntry(fname=font_path, name=font_prop.get_name())])
        
        print(f"Successfully configured matplotlib to use {font_path}")
        return font_path
    else:
        print("Warning: No suitable Chinese font found. Chinese characters may not display properly.")
        return None

def test_chinese_plot(font_path=None):
    """
    Create a test plot with Chinese characters
    """
    plt.figure(figsize=(10, 6))
    
    # Create sample data
    x = np.linspace(0, 2*np.pi, 100)
    y = np.sin(x)
    
    # Plot with Chinese labels
    plt.plot(x, y)
    plt.title("中文顯示測試 / Chinese Display Test", fontproperties=fm.FontProperties(fname=font_path) if font_path else None)
    plt.xlabel("橫軸 (X-Axis)", fontproperties=fm.FontProperties(fname=font_path) if font_path else None)
    plt.ylabel("縱軸 (Y-Axis)", fontproperties=fm.FontProperties(fname=font_path) if font_path else None)
    
    # Add some Chinese text annotations
    plt.annotate("這是一個測試", xy=(np.pi, 0), xytext=(np.pi, 0.5), 
                fontproperties=fm.FontProperties(fname=font_path) if font_path else None,
                arrowprops=dict(arrowstyle="->"))
    
    # Save and show the figure
    plt.savefig("chinese_font_test.png", dpi=100)
    print("Test image saved as 'chinese_font_test.png'")
    
    # Show font information
    if font_path:
        print(f"Used font: {font_path}")
        font_prop = fm.FontProperties(fname=font_path)
        print(f"Font name: {font_prop.get_name()}")
    else:
        print("No specific font was used.")

if __name__ == "__main__":
    # Configure matplotlib for Chinese display
    font_path = configure_matplotlib_chinese()
    
    # Test the configuration
    test_chinese_plot(font_path)
    
    print("\nTo use this font in your scripts, add these lines at the beginning:")
    print("import matplotlib.pyplot as plt")
    print("import matplotlib.font_manager as fm")
    if font_path:
        print(f"plt.rcParams['font.family'] = fm.FontProperties(fname=r'{font_path}').get_name()")
        print("plt.rcParams['axes.unicode_minus'] = False")
    else:
        print("# No suitable Chinese font was found on your system.")