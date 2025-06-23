#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility script to convert simplified Chinese to traditional Chinese
in the test visualization script
"""

import sys
import opencc

def convert_to_traditional(text):
    """Convert simplified Chinese to traditional Chinese"""
    converter = opencc.OpenCC('s2t')
    return converter.convert(text)

def main():
    # Process test_chinese.py
    try:
        with open('test_chinese.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert simplified Chinese to traditional
        traditional_content = convert_to_traditional(content)
        
        with open('test_chinese.py', 'w', encoding='utf-8') as f:
            f.write(traditional_content)
        
        print("已更新 test_chinese.py 為繁體中文")
    except Exception as e:
        print(f"更新 test_chinese.py 時出錯: {str(e)}")
    
    # Process test_visualization.py
    try:
        with open('test_visualization.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert simplified Chinese to traditional
        traditional_content = convert_to_traditional(content)
        
        with open('test_visualization.py', 'w', encoding='utf-8') as f:
            f.write(traditional_content)
        
        print("已更新 test_visualization.py 為繁體中文")
    except Exception as e:
        print(f"更新 test_visualization.py 時出錯: {str(e)}")

if __name__ == "__main__":
    try:
        import opencc
    except ImportError:
        print("請先安裝 OpenCC: pip install opencc-python-reimplemented")
        sys.exit(1)
    
    main()
    print("繁體中文轉換完成")