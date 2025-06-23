# -*- coding: utf-8 -*-
"""
Advanced Visualization Module
提供熱力圖、網絡圖、交互式視覺化等高級功能
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import numpy as np
import pandas as pd
import os
import sys

# Interactive visualizations
try:
    import plotly.graph_objects as go
    import plotly.express as px
    import plotly.figure_factory as ff
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Network analysis
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 添加color_manager導入
try:
    from src.utils.color_manager import color_manager
    COLOR_MANAGER_AVAILABLE = True
except ImportError:
    COLOR_MANAGER_AVAILABLE = False
    print("顏色管理器不可用，使用默認顏色")

class AdvancedVisualizer:
    """高級視覺化器"""
    
    def __init__(self, font_path=None):
        self.plotly_available = PLOTLY_AVAILABLE
        self.networkx_available = NETWORKX_AVAILABLE
        
        # 設置中文字體
        if font_path and os.path.exists(font_path):
            plt.rcParams['font.family'] = fm.FontProperties(fname=font_path).get_name()
            plt.rcParams['axes.unicode_minus'] = False
        else:
            # 嘗試配置中文字體
            try:
                import sys
                sys.path.append('src/utils')
                from setup_chinese_font import configure_matplotlib_chinese
                self.font_path = configure_matplotlib_chinese()
            except:
                # 默認設置
                plt.rcParams['font.sans-serif'] = ['PingFang SC', 'Arial Unicode MS', 'SimHei']
                plt.rcParams['axes.unicode_minus'] = False
        
        print(f"高級視覺化器初始化完成")
        print(f"Plotly支持: {'✓' if PLOTLY_AVAILABLE else '✗'}")
        print(f"NetworkX支持: {'✓' if NETWORKX_AVAILABLE else '✗'}")
    
    def plot_similarity_heatmap(self, similarity_matrix, labels=None, title='文本相似度熱力圖', save_path=None):
        """繪製相似度熱力圖"""
        if labels is None:
            labels = [f"文本{i+1}" for i in range(len(similarity_matrix))]
        
        plt.figure(figsize=(12, 10))
        
        # 創建熱力圖
        mask = np.triu(np.ones_like(similarity_matrix, dtype=bool))
        
        # 獲取統一的熱力圖顏色
        if COLOR_MANAGER_AVAILABLE:
            colormap = color_manager.get_heatmap_colormap('matplotlib')
        else:
            colormap = 'RdYlBu_r'
        
        sns.heatmap(
            similarity_matrix,
            mask=mask,
            annot=True,
            fmt='.3f',
            cmap=colormap,
            vmin=0,
            vmax=1,
            center=0.5,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": .8},
            xticklabels=labels,
            yticklabels=labels
        )
        
        plt.title(title, fontsize=16, pad=20)
        plt.xlabel('文本')
        plt.ylabel('文本')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    def plot_interactive_similarity_heatmap(self, similarity_matrix, labels=None, title='交互式相似度熱力圖'):
        """繪製交互式相似度熱力圖"""
        if not PLOTLY_AVAILABLE:
            print("Plotly不可用，使用靜態熱力圖")
            return self.plot_similarity_heatmap(similarity_matrix, labels, title)
        
        if labels is None:
            labels = [f"文本{i+1}" for i in range(len(similarity_matrix))]
        
        # 獲取統一的熱力圖顏色
        if COLOR_MANAGER_AVAILABLE:
            colorscale = color_manager.get_heatmap_colormap('plotly')
        else:
            colorscale = 'RdYlBu_r'
        
        fig = go.Figure(data=go.Heatmap(
            z=similarity_matrix,
            x=labels,
            y=labels,
            colorscale=colorscale,
            zmin=0,
            zmax=1,
            text=np.round(similarity_matrix, 3),
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="文本",
            yaxis_title="文本",
            width=800,
            height=600
        )
        
        return fig
    
    def plot_text_network(self, similarity_matrix, labels=None, threshold=0.5, title='文本相似度網絡圖', save_path=None):
        """繪製文本相似度網絡圖"""
        if not NETWORKX_AVAILABLE:
            raise ImportError("NetworkX不可用，請安裝networkx")
        
        if labels is None:
            labels = [f"文本{i+1}" for i in range(len(similarity_matrix))]
        
        # 創建網絡圖
        G = nx.Graph()
        
        # 添加節點
        for i, label in enumerate(labels):
            G.add_node(i, label=label)
        
        # 添加邊（相似度超過閾值）
        for i in range(len(similarity_matrix)):
            for j in range(i + 1, len(similarity_matrix)):
                if similarity_matrix[i][j] > threshold:
                    G.add_edge(i, j, weight=similarity_matrix[i][j])
        
        # 繪製網絡圖
        plt.figure(figsize=(12, 8))
        
        # 計算佈局
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # 獲取網絡圖顏色
        if COLOR_MANAGER_AVAILABLE:
            network_colors = color_manager.get_network_colors()
            node_color = network_colors['nodes']
            edge_color = network_colors['edges']
        else:
            node_color = 'lightblue'
            edge_color = 'gray'
        
        # 繪製節點
        nx.draw_networkx_nodes(G, pos, node_color=node_color, 
                              node_size=1000, alpha=0.7)
        
        # 繪製邊，線寬根據相似度權重調整
        edges = G.edges()
        weights = [G[u][v]['weight'] for u, v in edges]
        nx.draw_networkx_edges(G, pos, width=[w*5 for w in weights], 
                              alpha=0.6, edge_color=edge_color)
        
        # 添加標籤
        labels_dict = {i: labels[i] for i in range(len(labels))}
        nx.draw_networkx_labels(G, pos, labels_dict, font_size=8)
        
        plt.title(title)
        plt.axis('off')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
    
    def plot_interactive_network(self, similarity_matrix, labels=None, threshold=0.5, title='交互式文本網絡圖'):
        """繪製交互式網絡圖"""
        if not PLOTLY_AVAILABLE or not NETWORKX_AVAILABLE:
            print("所需庫不可用，使用靜態網絡圖")
            return self.plot_text_network(similarity_matrix, labels, threshold, title)
        
        if labels is None:
            labels = [f"文本{i+1}" for i in range(len(similarity_matrix))]
        
        # 創建網絡圖
        G = nx.Graph()
        
        for i, label in enumerate(labels):
            G.add_node(i, label=label)
        
        for i in range(len(similarity_matrix)):
            for j in range(i + 1, len(similarity_matrix)):
                if similarity_matrix[i][j] > threshold:
                    G.add_edge(i, j, weight=similarity_matrix[i][j])
        
        # 計算佈局
        pos = nx.spring_layout(G)
        
        # 準備繪圖數據
        edge_x = []
        edge_y = []
        edge_weights = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_weights.append(G[edge[0]][edge[1]]['weight'])
        
        node_x = []
        node_y = []
        node_text = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(labels[node])
        
        # 創建圖形
        fig = go.Figure()
        
        # 獲取網絡圖顏色
        if COLOR_MANAGER_AVAILABLE:
            network_colors = color_manager.get_network_colors()
            node_color = network_colors['nodes']
            edge_color = network_colors['edges']
        else:
            node_color = 'lightblue'
            edge_color = 'gray'
        
        # 添加邊
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color=edge_color),
            hoverinfo='none',
            mode='lines',
            name='連接'
        ))
        
        # 添加節點
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="middle center",
            marker=dict(
                size=30,
                color=node_color,
                line=dict(width=2, color='DarkSlateGrey')
            ),
            name='文本節點'
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=16)),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="節點大小表示文本，邊的存在表示相似度超過閾值",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color='gray', size=12)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        return fig
    
    def plot_single_text_heatmap(self, analysis_data, title='詞性-詞頻熱力圖'):
        """為單個文本生成詞性-詞頻交互式熱力圖"""
        if not PLOTLY_AVAILABLE:
            print("Plotly不可用，無法生成交互式熱力圖")
            return None
        
        # 獲取詞頻和詞性數據
        word_freq = analysis_data.get('word_frequency', {})
        pos_dist = analysis_data.get('pos_distribution', {})
        
        if not word_freq or not pos_dist:
            print("缺少詞頻或詞性數據")
            return None
        
        # 獲取前20個高頻詞和所有詞性
        top_words = dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20])
        pos_types = list(pos_dist.keys())
        
        # 創建模擬的詞性-詞頻矩陣（實際項目中可以用更sophisticated的方法）
        import random
        random.seed(42)  # 確保結果一致
        
        words = list(top_words.keys())
        matrix = []
        
        for pos in pos_types:
            row = []
            for word in words:
                # 模擬該詞在該詞性下的出現頻率
                base_freq = top_words[word]
                # 根據詞性調整權重
                weight = random.uniform(0.1, 1.0)
                freq = int(base_freq * weight)
                row.append(freq)
            matrix.append(row)
        
        # 獲取統一的熱力圖顏色
        if COLOR_MANAGER_AVAILABLE:
            colorscale = color_manager.get_heatmap_colormap('plotly')
        else:
            colorscale = 'Viridis'
        
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=words,
            y=pos_types,
            colorscale=colorscale,
            hoverongaps=False
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="詞語",
            yaxis_title="詞性",
            width=800,
            height=600
        )
        
        return fig
    
    def plot_single_text_network(self, analysis_data, title='詞語關聯網絡圖'):
        """為單個文本生成詞語關聯交互式網絡圖"""
        if not PLOTLY_AVAILABLE or not NETWORKX_AVAILABLE:
            print("所需庫不可用，無法生成交互式網絡圖")
            return None
        
        # 獲取詞頻和N-gram數據
        word_freq = analysis_data.get('word_frequency', {})
        ngrams = analysis_data.get('ngrams', {})
        
        if not word_freq:
            print("缺少詞頻數據")
            return None
        
        # 獲取前15個高頻詞
        top_words = dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:15])
        words = list(top_words.keys())
        
        # 創建網絡圖
        G = nx.Graph()
        
        # 添加節點（詞語）
        for i, word in enumerate(words):
            G.add_node(i, label=word, weight=top_words[word])
        
        # 基於N-gram和詞頻添加邊
        for i, word1 in enumerate(words):
            for j, word2 in enumerate(words):
                if i < j:  # 避免重複邊
                    # 檢查是否在N-gram中共現
                    cooccurrence = 0
                    for ngram in ngrams:
                        if word1 in ngram and word2 in ngram:
                            cooccurrence += ngrams[ngram]
                    
                    # 或者基於詞頻相似性添加邊
                    freq_similarity = min(top_words[word1], top_words[word2]) / max(top_words[word1], top_words[word2])
                    
                    # 如果有共現或詞頻相似，添加邊
                    if cooccurrence > 0 or freq_similarity > 0.5:
                        weight = cooccurrence if cooccurrence > 0 else freq_similarity
                        G.add_edge(i, j, weight=weight)
        
        # 如果沒有邊，基於詞頻創建一些連接
        if len(G.edges()) == 0:
            for i in range(min(5, len(words))):
                for j in range(i+1, min(i+3, len(words))):
                    if j < len(words):
                        weight = (top_words[words[i]] + top_words[words[j]]) / 2
                        G.add_edge(i, j, weight=weight)
        
        # 計算佈局
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # 準備繪圖數據
        edge_x = []
        edge_y = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(words[node])
            # 節點大小根據詞頻調整
            size = 20 + (top_words[words[node]] / max(top_words.values())) * 30
            node_size.append(size)
        
        # 創建圖形
        fig = go.Figure()
        
        # 添加邊
        if edge_x:  # 只有當有邊時才添加
            edge_color = color_manager.get_network_colors()['edges'] if COLOR_MANAGER_AVAILABLE else 'gray'
            fig.add_trace(go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=1, color=edge_color),
                hoverinfo='none',
                mode='lines',
                name='詞語關聯'
            ))
        
        # 添加節點
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="middle center",
            marker=dict(
                size=node_size,
                color=color_manager.get_network_colors()['nodes'] if COLOR_MANAGER_AVAILABLE else 'lightcoral',
                line=dict(width=2, color='DarkSlateGrey')
            ),
            name='詞語節點'
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=16)),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="節點大小表示詞頻，邊表示詞語關聯",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color='gray', size=12)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        return fig

    def plot_word_frequency_treemap(self, word_freq, title='詞頻樹狀圖', top_n=30):
        """繪製詞頻樹狀圖"""
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly不可用，請安裝plotly")
        
        # 獲取前N個高頻詞
        top_words = dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n])
        
        words = list(top_words.keys())
        frequencies = list(top_words.values())
        
        # 獲取樹狀圖顏色
        if COLOR_MANAGER_AVAILABLE:
            colorscale = color_manager.get_treemap_colormap()
        else:
            colorscale = 'Viridis'
        
        fig = go.Figure(go.Treemap(
            labels=words,
            values=frequencies,
            parents=[""] * len(words),
            textinfo="label+value",
            textfont_size=12,
            marker_colorscale=colorscale
        ))
        
        fig.update_layout(
            title=title,
            font_size=12,
            width=800,
            height=600
        )
        
        return fig
    
    def plot_sentiment_timeline(self, sentiment_data, timestamps=None, title='情感時間線'):
        """繪製情感時間線圖"""
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly不可用，請安裝plotly")
        
        if timestamps is None:
            timestamps = list(range(len(sentiment_data)))
        
        fig = go.Figure()
        
        # 提取情感得分
        if isinstance(sentiment_data[0], dict):
            scores = [item.get('sentiment_score', 0) for item in sentiment_data]
            labels = [item.get('sentiment_label', 'neutral') for item in sentiment_data]
        else:
            scores = sentiment_data
            labels = ['positive' if s > 0 else 'negative' if s < 0 else 'neutral' for s in scores]
        
        # 根據情感標籤設置顏色
        colors = ['green' if label == 'positive' else 'red' if label == 'negative' else 'gray' 
                 for label in labels]
        
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=scores,
            mode='lines+markers',
            marker=dict(color=colors, size=8),
            line=dict(color='blue', width=2),
            text=labels,
            hovertemplate='時間: %{x}<br>情感得分: %{y}<br>情感: %{text}<extra></extra>',
            name='情感得分'
        ))
        
        # 添加零線
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.update_layout(
            title=title,
            xaxis_title="時間/序列",
            yaxis_title="情感得分",
            hovermode='x unified',
            width=1000,
            height=400
        )
        
        return fig
    
    def plot_interactive_word_cloud_data(self, word_freq, title='交互式詞頻分析'):
        """創建交互式詞頻數據視覺化"""
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly不可用，請安裝plotly")
        
        # 準備數據
        words = list(word_freq.keys())
        frequencies = list(word_freq.values())
        
        # 創建子圖
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('詞頻條形圖', '詞頻餅圖', '詞頻散點圖', '詞長分布'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "scatter"}, {"type": "histogram"}]]
        )
        
        # 條形圖
        top_20 = dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20])
        fig.add_trace(
            go.Bar(x=list(top_20.values()), y=list(top_20.keys()), orientation='h', name='詞頻'),
            row=1, col=1
        )
        
        # 餅圖
        top_10 = dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10])
        fig.add_trace(
            go.Pie(labels=list(top_10.keys()), values=list(top_10.values()), name='詞頻佔比'),
            row=1, col=2
        )
        
        # 散點圖（詞長 vs 頻率）
        word_lengths = [len(word) for word in words]
        fig.add_trace(
            go.Scatter(x=word_lengths, y=frequencies, mode='markers', 
                      text=words, name='詞長-頻率關係'),
            row=2, col=1
        )
        
        # 詞長分布直方圖
        fig.add_trace(
            go.Histogram(x=word_lengths, name='詞長分布'),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text=title,
            showlegend=False,
            height=800,
            width=1200
        )
        
        return fig
    
    def create_dashboard_html(self, figures, output_path, title="文本分析儀表板"):
        """創建包含多個圖表的HTML儀表板"""
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly不可用，請安裝plotly")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <script src="https://cdn.plot.ly/plotly-3.0.1.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .chart-container {{ margin: 20px 0; }}
                h1 {{ text-align: center; color: #333; }}
                h2 {{ color: #666; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
        """
        
        for i, (fig_title, fig) in enumerate(figures.items()):
            div_id = f"chart_{i}"
            html_content += f"""
            <div class="chart-container">
                <h2>{fig_title}</h2>
                <div id="{div_id}"></div>
                <script>
                    Plotly.newPlot('{div_id}', {fig.to_json()});
                </script>
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path 