# -*- coding: utf-8 -*-
"""
Color Manager Module
統一管理所有視覺化的顏色配置
"""

import json
import os
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from typing import Dict, List, Any

class ColorManager:
    """統一顏色管理器"""
    
    def __init__(self, config_path=None):
        if config_path is None:
            # 默認配置文件路徑
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            config_path = os.path.join(project_root, 'config', 'color_scheme.json')
        
        self.config_path = config_path
        self.colors = self._load_color_config()
    
    def _load_color_config(self) -> Dict[str, Any]:
        """載入顏色配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"顏色配置文件未找到: {self.config_path}")
            return self._get_default_colors()
        except json.JSONDecodeError:
            print(f"顏色配置文件格式錯誤: {self.config_path}")
            return self._get_default_colors()
    
    def _get_default_colors(self) -> Dict[str, Any]:
        """獲取默認顏色配置"""
        return {
            "primary_palette": {
                "primary": "#2E86AB",
                "secondary": "#A23B72", 
                "tertiary": "#F18F01",
                "quaternary": "#C73E1D",
                "quinary": "#592E83"
            },
            "sentiment_colors": {
                "positive": "#27AE60",
                "negative": "#E74C3C", 
                "neutral": "#5D6D7E"
            },
            "entity_colors": {
                "person": "#E74C3C",
                "location": "#27AE60", 
                "organization": "#3498DB",
                "time": "#F39C12",
                "default": "#95A5A6"
            },
            "matplotlib_palettes": {
                "categorical": ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#592E83", "#27AE60", "#E74C3C", "#3498DB", "#F39C12", "#95A5A6"],
                "sequential": "Blues",
                "diverging": "RdYlBu_r"
            },
            "plotly_palettes": {
                "categorical": ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#592E83", "#27AE60", "#E74C3C", "#3498DB", "#F39C12", "#95A5A6"],
                "sequential": "Blues", 
                "diverging": "RdYlBu_r",
                "heatmap": "RdYlBu_r",
                "treemap": "Viridis",
                "network_nodes": "#2E86AB",
                "network_edges": "#95A5A6"
            },
            "wordcloud_colors": {
                "colormap": "Blues",
                "background": "white"
            }
        }
    
    def get_primary_palette(self) -> List[str]:
        """獲取主色板"""
        return list(self.colors["primary_palette"].values())
    
    def get_categorical_colors(self, library='matplotlib') -> List[str]:
        """獲取分類顏色"""
        if library == 'matplotlib':
            return self.colors["matplotlib_palettes"]["categorical"]
        elif library == 'plotly':
            return self.colors["plotly_palettes"]["categorical"]
        else:
            return self.colors["matplotlib_palettes"]["categorical"]
    
    def get_sentiment_colors(self) -> Dict[str, str]:
        """獲取情感分析顏色"""
        return self.colors["sentiment_colors"]
    
    def get_entity_colors(self) -> Dict[str, str]:
        """獲取實體類型顏色"""
        return self.colors["entity_colors"]
    
    def get_entity_color(self, entity_type: str) -> str:
        """獲取特定實體類型的顏色"""
        entity_colors = self.get_entity_colors()
        return entity_colors.get(entity_type, entity_colors["default"])
    
    def get_sequential_colormap(self, library='matplotlib') -> str:
        """獲取順序顏色映射"""
        if library == 'matplotlib':
            return self.colors["matplotlib_palettes"]["sequential"]
        elif library == 'plotly':
            return self.colors["plotly_palettes"]["sequential"]
        else:
            return self.colors["matplotlib_palettes"]["sequential"]
    
    def get_diverging_colormap(self, library='matplotlib') -> str:
        """獲取發散顏色映射"""
        if library == 'matplotlib':
            return self.colors["matplotlib_palettes"]["diverging"]
        elif library == 'plotly':
            return self.colors["plotly_palettes"]["diverging"]
        else:
            return self.colors["matplotlib_palettes"]["diverging"]
    
    def get_heatmap_colormap(self, library='plotly') -> str:
        """獲取熱力圖顏色映射"""
        if library == 'plotly':
            return self.colors["plotly_palettes"]["heatmap"]
        else:
            return self.get_diverging_colormap('matplotlib')
    
    def get_treemap_colormap(self) -> str:
        """獲取樹狀圖顏色映射"""
        return self.colors["plotly_palettes"]["treemap"]
    
    def get_network_colors(self) -> Dict[str, str]:
        """獲取網絡圖顏色"""
        return {
            "nodes": self.colors["plotly_palettes"]["network_nodes"],
            "edges": self.colors["plotly_palettes"]["network_edges"]
        }
    
    def get_wordcloud_config(self) -> Dict[str, str]:
        """獲取詞雲顏色配置"""
        return self.colors["wordcloud_colors"]
    
    def create_matplotlib_colormap(self, colors: List[str], name: str = 'custom'):
        """創建matplotlib自定義顏色映射"""
        return mcolors.LinearSegmentedColormap.from_list(name, colors)
    
    def apply_style_to_plot(self, ax=None, style='categorical'):
        """為matplotlib圖表應用顏色樣式"""
        if ax is None:
            ax = plt.gca()
        
        if style == 'categorical':
            colors = self.get_categorical_colors('matplotlib')
            ax.set_prop_cycle('color', colors)
        
        return ax
    
    def get_color_cycle(self, n_colors: int, style='categorical') -> List[str]:
        """獲取指定數量的顏色循環"""
        colors = self.get_categorical_colors()
        
        if n_colors <= len(colors):
            return colors[:n_colors]
        else:
            # 如果需要的顏色數量超過可用顏色，重複顏色
            repeated_colors = []
            for i in range(n_colors):
                repeated_colors.append(colors[i % len(colors)])
            return repeated_colors

# 創建全局顏色管理器實例
color_manager = ColorManager()

# 提供便捷函數
def get_categorical_colors(n_colors=None, library='matplotlib'):
    """獲取分類顏色的便捷函數"""
    colors = color_manager.get_categorical_colors(library)
    if n_colors is not None:
        return color_manager.get_color_cycle(n_colors)
    return colors

def get_sentiment_colors():
    """獲取情感顏色的便捷函數"""
    return color_manager.get_sentiment_colors()

def get_entity_colors():
    """獲取實體顏色的便捷函數"""
    return color_manager.get_entity_colors() 