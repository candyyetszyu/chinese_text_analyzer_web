# -*- coding: utf-8 -*-
import matplotlib
# Use the Agg backend which doesn't require a GUI
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from wordcloud import WordCloud
import seaborn as sns
import os
import numpy as np
import json

# Configure matplotlib to use Chinese font
CHINESE_FONT_PATH = '/System/Library/Fonts/STHeiti Light.ttc'
if os.path.exists(CHINESE_FONT_PATH):
    plt.rcParams['font.family'] = fm.FontProperties(fname=CHINESE_FONT_PATH).get_name()
    plt.rcParams['axes.unicode_minus'] = False  # Correctly display minus sign
    DEFAULT_CHINESE_FONT = CHINESE_FONT_PATH
else:
    # Fallback to other Chinese fonts on macOS
    mac_font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Songti.ttc",
        "/Library/Fonts/Arial Unicode.ttf"
    ]
    
    DEFAULT_CHINESE_FONT = None
    for font_path in mac_font_paths:
        if os.path.exists(font_path):
            plt.rcParams['font.family'] = fm.FontProperties(fname=font_path).get_name()
            plt.rcParams['axes.unicode_minus'] = False
            DEFAULT_CHINESE_FONT = font_path
            break
    
    if DEFAULT_CHINESE_FONT is None:
        pass

# 定義資源文件的基礎路徑
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESOURCES_PATH = os.path.join(project_root, 'config')

# 從資源文件加載映射
def load_mapping_from_json(filename):
    # 首先嘗試從 mappings 子目錄加載
    filepath = os.path.join(RESOURCES_PATH, 'mappings', filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"無法從 mappings 目錄加載映射文件 {filename}: {e}")
            # 如果從 mappings 目錄加載失敗，嘗試從根目錄加載（向後兼容）
            root_filepath = os.path.join(RESOURCES_PATH, filename)
            if os.path.exists(root_filepath):
                try:
                    with open(root_filepath, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    print(f"無法加載映射文件 {filename}: {e}")
                    return {}
            return {}
    else:
        # 如果 mappings 目錄中沒有找到，嘗試從根目錄加載（向後兼容）
        root_filepath = os.path.join(RESOURCES_PATH, filename)
        if os.path.exists(root_filepath):
            try:
                with open(root_filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"無法加載映射文件 {filename}: {e}")
                return {}
        else:
            print(f"映射文件不存在: {filepath} 或 {root_filepath}")
            return {}

# 載入詞性、實體和情感標籤映射
POS_MAPPING = load_mapping_from_json('pos_mapping.json')
ENTITY_MAPPING = load_mapping_from_json('entity_mapping.json')
SENTIMENT_MAPPING = load_mapping_from_json('sentiment_mapping.json')

class Visualizer:
    @staticmethod
    def plot_word_frequency(word_freq, top_n=20, title='詞頻統計', save_path=None, figsize=(12, 6)):
        """繪製詞頻條形圖"""
        top_words = dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n])
        
        plt.figure(figsize=figsize)
        # 使用更高效的繪圖設置
        with plt.style.context('fast'):
            ax = sns.barplot(x=list(top_words.values()), y=list(top_words.keys()))
        
        # 在每個條形上顯示數值
        for i, v in enumerate(list(top_words.values())):
            ax.text(v + 0.1, i, str(v), va='center')
            
        plt.title(title)
        plt.xlabel('頻率')
        plt.ylabel('詞語')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.close()
    
    @staticmethod
    def generate_wordcloud(word_freq, title='詞雲圖', save_path=None, figsize=(10, 8), 
                          font_path=None, background_color='white', max_words=200):
        """生成詞雲"""
        # 使用全局中文字體設置，除非指定了其他字體
        if font_path is None:
            # 首先嘗試使用我們已確認的全局中文字體
            if 'DEFAULT_CHINESE_FONT' in globals() and DEFAULT_CHINESE_FONT:
                font_path = DEFAULT_CHINESE_FONT
            else:
                # 嘗試其他常見的中文字體路徑
                possible_fonts = [
                    '/System/Library/Fonts/STHeiti Light.ttc',
                    '/System/Library/Fonts/PingFang.ttc',
                    '/System/Library/Fonts/Hiragino Sans GB.ttc',
                    '/System/Library/Fonts/Songti.ttc',
                    '/Library/Fonts/Arial Unicode.ttf',
                    None
                ]
                
                for font in possible_fonts:
                    if font is None or os.path.exists(font):
                        font_path = font
                        break
        else:
            if not os.path.exists(font_path):
                if 'DEFAULT_CHINESE_FONT' in globals() and DEFAULT_CHINESE_FONT:
                    font_path = DEFAULT_CHINESE_FONT
                else:
                    font_path = None
        
        # 生成詞雲的核心代碼
        try:
            # 設置詞雲參數
            wc_kwargs = {
                'background_color': background_color,
                'width': 800,
                'height': 600,
                'max_words': max_words,
                'collocations': False,
                'mode': 'RGBA'  # 使用RGBA模式，支持透明背景
            }
            
            # 如果確實有字體存在，則使用它
            if font_path and os.path.exists(font_path):
                wc_kwargs['font_path'] = font_path
                
            wc = WordCloud(**wc_kwargs).generate_from_frequencies(word_freq)
            
            plt.figure(figsize=figsize)
            plt.imshow(wc, interpolation='bilinear')
            plt.axis('off')
            plt.title(title)
            
            if save_path:
                os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                
            plt.close()
            return True
            
        except Exception as e:
            try:
                # 備用方法：創建一個非常簡單的詞雲，不使用任何字體
                wc = WordCloud(background_color=background_color, width=800, height=600, 
                               max_words=max_words, collocations=False).generate_from_frequencies(word_freq)
                
                plt.figure(figsize=figsize)
                plt.imshow(wc, interpolation='bilinear')
                plt.axis('off')
                plt.title("詞雲圖 (簡化版)")
                
                if save_path:
                    plt.savefig(save_path, dpi=300, bbox_inches='tight')
                
                plt.close()
                return True
                
            except Exception as e2:
                return False
    
    @staticmethod
    def plot_pos_distribution(pos_freq, title='詞性分布', save_path=None, figsize=(10, 6)):
        """繪製詞性分布圖"""
        # 將詞性標籤轉換為繁體中文
        pos_freq_translated = {}
        for pos, freq in pos_freq.items():
            translated_pos = POS_MAPPING.get(pos, pos)  # 如果找不到映射，保留原始標籤
            pos_freq_translated[translated_pos] = freq
        
        plt.figure(figsize=figsize)
        with plt.style.context('fast'):
            ax = sns.barplot(x=list(pos_freq_translated.values()), y=list(pos_freq_translated.keys()))
        
        # 在每個條形上顯示數值
        for i, v in enumerate(list(pos_freq_translated.values())):
            ax.text(v + 0.1, i, str(v), va='center')
            
        plt.title(title)
        plt.xlabel('頻率')
        plt.ylabel('詞性')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        plt.close()
    
    @staticmethod
    def plot_sentiment_analysis(sentiment_data, title='情感分析', save_path=None, figsize=(8, 5)):
        """繪製情感分析結果圖表"""
        # 從情感分析結果中提取數據
        positive = sentiment_data.get('positive_count', 0)
        negative = sentiment_data.get('negative_count', 0)
        
        # 新增中性情感的顯示
        neutral = 0
        if sentiment_data.get('sentiment_label') == 'neutral':
            neutral = 1
        
        # 繪製條形圖 - 移除情感得分
        plt.figure(figsize=figsize)
        categories = [SENTIMENT_MAPPING.get('positive', '正面情感'), 
                     SENTIMENT_MAPPING.get('negative', '負面情感'), 
                     SENTIMENT_MAPPING.get('neutral', '中性情感')]
        values = [positive, negative, neutral]
        colors = ['green', 'red', 'blue']
        
        with plt.style.context('fast'):
            bars = plt.bar(categories, values, color=colors)
        
        # 添加數值標籤
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height}', ha='center', va='bottom')
        
        plt.title(title)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        plt.close()
    
    @staticmethod
    def plot_ngrams(ngrams, top_n=15, title='常見詞組', save_path=None, figsize=(12, 6)):
        """繪製n-gram頻率圖"""
        top_ngrams = dict(sorted(ngrams.items(), key=lambda x: x[1], reverse=True)[:top_n])
        
        plt.figure(figsize=figsize)
        with plt.style.context('fast'):
            ax = sns.barplot(x=list(top_ngrams.values()), y=list(top_ngrams.keys()))
        
        # 在每個條形上顯示數值
        for i, v in enumerate(list(top_ngrams.values())):
            ax.text(v + 0.1, i, str(v), va='center')
            
        plt.title(title)
        plt.xlabel('頻率')
        plt.ylabel('詞組')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        plt.close()
    
    @staticmethod
    def plot_entities(entities, title='命名實體統計', save_path=None, figsize=(12, 8)):
        """繪製命名實體統計圖"""
        # 轉換實體類型名稱為繁體中文
        entity_counts = {}
        for entity_type, entity_list in entities.items():
            if entity_list:  # 只處理非空列表
                # 將英文實體類型轉換為繁體中文
                translated_type = ENTITY_MAPPING.get(entity_type, entity_type)
                entity_counts[translated_type] = len(entity_list)
        
        if not entity_counts:
            return
        
        # 繪製餅圖
        plt.figure(figsize=figsize)
        with plt.style.context('fast'):
            plt.pie(entity_counts.values(), labels=entity_counts.keys(), autopct='%1.1f%%')
        
        plt.title(title)
        plt.axis('equal')  # 使餅圖為正圓形
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        plt.close()
    
    @staticmethod
    def plot_keyword_weights(keywords, top_n=15, title='關鍵詞權重', save_path=None, figsize=(12, 6)):
        """繪製關鍵詞權重圖"""
        top_keywords = dict(sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:top_n])
        
        plt.figure(figsize=figsize)
        with plt.style.context('fast'):
            ax = sns.barplot(x=list(top_keywords.values()), y=list(top_keywords.keys()))
        
        # 在每個條形上顯示數值
        for i, v in enumerate(list(top_keywords.values())):
            ax.text(v + 0.01, i, f'{v:.3f}', va='center')
            
        plt.title(title)
        plt.xlabel('權重')
        plt.ylabel('關鍵詞')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        plt.close()
    
    @staticmethod
    def create_visualization_report(results, output_dir='visualization', prefix='', font_path=None, dpi=300):
        """創建完整的可視化報告
        
        將所有分析結果圖表保存到指定目錄
        """
        # 創建輸出目錄
        os.makedirs(output_dir, exist_ok=True)
        
        # 為避免文件名衝突，添加前綴（例如，文件名）
        if prefix and not prefix.endswith('_'):
            prefix = prefix + '_'
        
        # 詞頻分析
        if 'word_frequency' in results:
            word_freq_path = os.path.join(output_dir, f"{prefix}word_frequency.png")
            Visualizer.plot_word_frequency(
                results['word_frequency'], 
                title='詞頻統計', 
                save_path=word_freq_path
            )
        
        # 詞雲
        if 'word_frequency' in results:
            wordcloud_path = os.path.join(output_dir, f"{prefix}wordcloud.png")
            Visualizer.generate_wordcloud(
                results['word_frequency'], 
                title='詞雲圖', 
                save_path=wordcloud_path,
                font_path=font_path
            )
        
        # 詞性分布
        if 'pos_frequency' in results:
            pos_path = os.path.join(output_dir, f"{prefix}pos_distribution.png")
            Visualizer.plot_pos_distribution(
                results['pos_frequency'], 
                title='詞性分布', 
                save_path=pos_path
            )
        
        # 情感分析
        if 'sentiment' in results:
            sentiment_path = os.path.join(output_dir, f"{prefix}sentiment.png")
            Visualizer.plot_sentiment_analysis(
                results['sentiment'], 
                title='情感分析結果', 
                save_path=sentiment_path
            )
        
        # N-gram分析
        if 'ngrams' in results:
            ngrams_path = os.path.join(output_dir, f"{prefix}ngrams.png")
            Visualizer.plot_ngrams(
                results['ngrams'], 
                title='常見詞組', 
                save_path=ngrams_path
            )
        
        # 命名實體分析
        if 'entities' in results:
            entities_path = os.path.join(output_dir, f"{prefix}entities.png")
            Visualizer.plot_entities(
                results['entities'], 
                title='命名實體統計', 
                save_path=entities_path
            )
        
        # 關鍵詞分析
        if 'keywords' in results:
            keywords_path = os.path.join(output_dir, f"{prefix}keywords.png")
            Visualizer.plot_keyword_weights(
                results['keywords'], 
                title='關鍵詞權重', 
                save_path=keywords_path
            )
        
        return output_dir
    
    @staticmethod
    def plot_advanced_word_frequency(word_freq, top_n=20, title='詞頻統計', save_path=None, 
                                    figsize=(12, 6), plot_type='horizontal', sort_by='frequency'):
        """
        繪製進階詞頻條形圖
        
        Parameters:
        - word_freq: 詞頻統計字典
        - top_n: 顯示的詞語數量
        - title: 圖表標題
        - save_path: 保存路徑
        - figsize: 圖表尺寸
        - plot_type: 圖表類型 ('horizontal', 'vertical', 'pie')
        - sort_by: 排序方式 ('frequency', 'alphabetical', 'length')
        """
        # 根據排序方式處理詞頻數據
        if sort_by == 'frequency':
            sorted_items = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
        elif sort_by == 'alphabetical':
            sorted_items = sorted(word_freq.items(), key=lambda x: x[0])[:top_n]
        elif sort_by == 'length':
            sorted_items = sorted(word_freq.items(), key=lambda x: len(x[0]), reverse=True)[:top_n]
        else:
            sorted_items = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        words = [item[0] for item in sorted_items]
        freqs = [item[1] for item in sorted_items]
        
        plt.figure(figsize=figsize)
        
        if plot_type == 'horizontal':
            # 使用Seaborn繪製水平條形圖
            plt.barh(words, freqs)
            plt.xlabel('頻率')
            plt.ylabel('詞語')
            
            # 在每個條形上顯示數值
            for i, v in enumerate(freqs):
                plt.text(v + 0.1, i, str(v), va='center')
                
        elif plot_type == 'vertical':
            # 繪製垂直條形圖
            plt.bar(words, freqs)
            plt.xlabel('詞語')
            plt.ylabel('頻率')
            plt.xticks(rotation=45, ha='right')  # 旋轉x軸標籤
            
            # 在每個條形上顯示數值
            for i, v in enumerate(freqs):
                plt.text(i, v + 0.1, str(v), ha='center')
                
        elif plot_type == 'pie':
            # 繪製餅圖
            plt.pie(
                freqs, 
                labels=words, 
                autopct='%1.1f%%',
                shadow=False, 
                startangle=90,
                wedgeprops={'edgecolor': 'w', 'linewidth': 1}
            )
            plt.axis('equal')  # 確保餅圖是圓形的
        
        plt.title(title)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        plt.close()
    
    @staticmethod
    def plot_entities(entity_data, title='命名實體分析', save_path=None, figsize=(10, 6)):
        """繪製命名實體分析圖表"""
        # 計算每種實體類型的數量
        entity_counts = {}
        for entity_type, entities in entity_data.items():
            if entities:  # 確保實體列表非空
                entity_counts[entity_type] = len(entities)
        
        if not entity_counts:
            # 如果沒有命名實體，創建一個空圖表
            plt.figure(figsize=figsize)
            plt.title(title)
            plt.text(0.5, 0.5, '未檢測到命名實體', ha='center', va='center', fontsize=14)
            plt.axis('off')
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                
            plt.close()
            return
        
        # 實體類型顯示名稱映射
        entity_type_names = {
            'person': '人名',
            'location': '地名',
            'organization': '機構名',
            'time': '時間'
        }
        
        # 準備數據
        labels = [entity_type_names.get(et, et) for et in entity_counts.keys()]
        sizes = list(entity_counts.values())
        
        # 顏色映射
        colors = {
            'person': '#ff9999',
            'location': '#99ff99',
            'organization': '#9999ff',
            'time': '#ffff99'
        }
        color_list = [colors.get(et, '#dddddd') for et in entity_counts.keys()]
        
        # 繪製餅圖
        plt.figure(figsize=figsize)
        plt.pie(
            sizes, 
            labels=labels, 
            autopct='%1.1f%%',
            colors=color_list,
            shadow=False, 
            startangle=90,
            wedgeprops={'edgecolor': 'w', 'linewidth': 1}
        )
        plt.axis('equal')  # 確保餅圖是圓形的
        plt.title(title)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        plt.close()
    
    @staticmethod
    def plot_ngrams(ngram_freq, title='N-gram分析', save_path=None, figsize=(12, 6)):
        """繪製N-gram分析條形圖"""
        if not ngram_freq:
            # 如果沒有N-gram數據，創建一個空圖表
            plt.figure(figsize=figsize)
            plt.title(title)
            plt.text(0.5, 0.5, '未檢測到有效的N-gram', ha='center', va='center', fontsize=14)
            plt.axis('off')
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                
            plt.close()
            return
        
        # 準備數據
        sorted_items = sorted(ngram_freq.items(), key=lambda x: x[1], reverse=True)
        ngrams = [' '.join(item[0]) if isinstance(item[0], tuple) else item[0] for item in sorted_items]
        freqs = [item[1] for item in sorted_items]
        
        plt.figure(figsize=figsize)
        plt.barh(ngrams, freqs)
        
        # 在每個條形上顯示數值
        for i, v in enumerate(freqs):
            plt.text(v + 0.1, i, str(v), va='center')
            
        plt.xlabel('頻率')
        plt.ylabel('詞組')
        plt.title(title)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        plt.close()
    
    @staticmethod
    def plot_keyword_weights(keywords, title='關鍵詞權重', save_path=None, figsize=(12, 6)):
        """繪製關鍵詞權重條形圖"""
        if not keywords:
            # 如果沒有關鍵詞數據，創建一個空圖表
            plt.figure(figsize=figsize)
            plt.title(title)
            plt.text(0.5, 0.5, '未檢測到關鍵詞', ha='center', va='center', fontsize=14)
            plt.axis('off')
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                
            plt.close()
            return
        
        # 準備數據
        words = list(keywords.keys())
        weights = list(keywords.values())
        
        plt.figure(figsize=figsize)
        plt.barh(words, weights)
        
        # 在每個條形上顯示權重值（保留3位小數）
        for i, v in enumerate(weights):
            plt.text(v + 0.01, i, f"{v:.3f}", va='center')
            
        plt.xlabel('權重')
        plt.ylabel('關鍵詞')
        plt.title(title)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        plt.close()
    
    @staticmethod
    def plot_word_frequency_comparison(word_freq_list, labels, title='詞頻對比', 
                                      save_path=None, figsize=(14, 8), top_n=20):
        """比較多個文本的詞頻"""
        if not word_freq_list or len(word_freq_list) < 2:
            # 至少需要兩個詞頻分布來進行比較
            plt.figure(figsize=figsize)
            plt.title(title)
            plt.text(0.5, 0.5, '至少需要兩個詞頻分布來進行比較', ha='center', va='center', fontsize=14)
            plt.axis('off')
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                
            plt.close()
            return
        
        # 獲取所有文本中的詞彙
        all_words = set()
        for word_freq in word_freq_list:
            all_words.update(word_freq.keys())
        
        # 獲取頻率最高的top_n個詞
        word_freq_sum = {}
        for word in all_words:
            word_freq_sum[word] = sum(word_freq.get(word, 0) for word_freq in word_freq_list)
        
        top_words = [word for word, _ in sorted(word_freq_sum.items(), key=lambda x: x[1], reverse=True)[:top_n]]
        
        # 準備熱圖數據
        heatmap_data = []
        for word_freq in word_freq_list:
            heatmap_data.append([word_freq.get(word, 0) for word in top_words])
        
        # 繪製熱圖
        plt.figure(figsize=figsize)
        ax = sns.heatmap(
            heatmap_data, 
            annot=True, 
            fmt="d",
            cmap="YlGnBu", 
            xticklabels=top_words, 
            yticklabels=labels
        )
        
        plt.title(title)
        plt.xlabel('詞語')
        plt.ylabel('文本')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        plt.close()
    
    @staticmethod
    def plot_word_frequency_trends(word_freq_dict, x_labels, selected_words=None, 
                                 title='詞頻趨勢', save_path=None, figsize=(12, 6)):
        """繪製詞頻隨時間/順序的變化趨勢"""
        if not word_freq_dict or len(word_freq_dict) < 2:
            # 至少需要兩個時間點/順序的詞頻數據
            plt.figure(figsize=figsize)
            plt.title(title)
            plt.text(0.5, 0.5, '至少需要兩個時間點的詞頻數據', ha='center', va='center', fontsize=14)
            plt.axis('off')
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                
            plt.close()
            return
        
        # 如果沒有指定要追蹤的詞語，則選擇頻率總和最高的5個詞
        if not selected_words:
            all_words = set()
            for word_freq in word_freq_dict.values():
                all_words.update(word_freq.keys())
            
            word_freq_sum = {}
            for word in all_words:
                word_freq_sum[word] = sum(word_freq.get(word, 0) for word_freq in word_freq_dict.values())
            
            selected_words = [word for word, _ in sorted(word_freq_sum.items(), key=lambda x: x[1], reverse=True)[:5]]
        
        # 準備繪圖數據
        plt.figure(figsize=figsize)
        
        for word in selected_words:
            trend_data = [word_freq.get(word, 0) for word_freq in word_freq_dict.values()]
            plt.plot(x_labels, trend_data, marker='o', label=word)
        
        plt.title(title)
        plt.xlabel('時間/順序')
        plt.ylabel('詞頻')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        plt.close()
    
    @staticmethod
    def create_visualization_report(analyzer_results, output_dir, prefix='report_', include_advanced=True):
        """生成一個完整的可視化報告，包含多個圖表"""
        os.makedirs(output_dir, exist_ok=True)
        
        viz_paths = {}
        
        # 詞雲
        if 'word_frequency' in analyzer_results:
            wc_path = os.path.join(output_dir, f"{prefix}wordcloud.png")
            Visualizer.generate_wordcloud(
                analyzer_results['word_frequency'], 
                title='詞頻雲圖',
                save_path=wc_path
            )
            viz_paths['wordcloud'] = wc_path
        
        # 詞頻分析
        if 'word_frequency' in analyzer_results:
            wf_path = os.path.join(output_dir, f"{prefix}word_frequency.png")
            Visualizer.plot_word_frequency(
                analyzer_results['word_frequency'],
                top_n=15,
                title='詞頻分布',
                save_path=wf_path
            )
            viz_paths['word_frequency'] = wf_path
        
        # 詞性分析
        if 'pos_frequency' in analyzer_results or 'pos_distribution' in analyzer_results:
            pos_data = analyzer_results.get('pos_distribution', analyzer_results.get('pos_frequency', {}))
            pos_path = os.path.join(output_dir, f"{prefix}pos_distribution.png")
            Visualizer.plot_pos_distribution(
                pos_data,
                title='詞性分布',
                save_path=pos_path
            )
            viz_paths['pos_distribution'] = pos_path
        
        # 情感分析
        if 'sentiment' in analyzer_results:
            sent_path = os.path.join(output_dir, f"{prefix}sentiment.png")
            Visualizer.plot_sentiment_analysis(
                analyzer_results['sentiment'],
                title='情感分析',
                save_path=sent_path
            )
            viz_paths['sentiment'] = sent_path
        
        # 命名實體
        if 'entities' in analyzer_results:
            entity_path = os.path.join(output_dir, f"{prefix}entities.png")
            Visualizer.plot_entities(
                analyzer_results['entities'],
                title='命名實體統計',
                save_path=entity_path
            )
            viz_paths['entities'] = entity_path
        
        # 進階可視化
        if include_advanced:
            # 進階詞頻可視化
            if 'word_frequency' in analyzer_results:
                # 垂直條形圖
                wf_vertical_path = os.path.join(output_dir, f"{prefix}word_freq_vertical.png")
                Visualizer.plot_advanced_word_frequency(
                    analyzer_results['word_frequency'],
                    top_n=15,
                    title='詞頻垂直分布',
                    save_path=wf_vertical_path,
                    plot_type='vertical'
                )
                viz_paths['word_freq_vertical'] = wf_vertical_path
                
                # 詞頻餅圖
                wf_pie_path = os.path.join(output_dir, f"{prefix}word_freq_pie.png")
                Visualizer.plot_advanced_word_frequency(
                    analyzer_results['word_frequency'],
                    top_n=10,
                    title='詞頻餅圖',
                    save_path=wf_pie_path,
                    plot_type='pie'
                )
                viz_paths['word_freq_pie'] = wf_pie_path
            
            # N-gram分析
            if 'ngrams' in analyzer_results:
                ngrams_path = os.path.join(output_dir, f"{prefix}ngrams.png")
                Visualizer.plot_ngrams(
                    analyzer_results['ngrams'],
                    title='N-gram詞組分析',
                    save_path=ngrams_path
                )
                viz_paths['ngrams'] = ngrams_path
            
            # 關鍵詞權重
            if 'keywords' in analyzer_results:
                keywords_path = os.path.join(output_dir, f"{prefix}keywords.png")
                Visualizer.plot_keyword_weights(
                    analyzer_results['keywords'],
                    title='關鍵詞權重',
                    save_path=keywords_path
                )
                viz_paths['keywords'] = keywords_path
        
        return viz_paths