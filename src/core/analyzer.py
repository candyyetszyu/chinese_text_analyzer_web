# -*- coding: utf-8 -*-
import jieba
import jieba.posseg as pseg
import jieba.analyse
from collections import Counter
import re
import os
import sys
import multiprocessing as mp

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.utils.file_utils import FileUtils

class ChineseTextAnalyzer:
    def __init__(self, custom_dict_path=None, stopwords_path=None):
        """初始化分析器"""
        # 設置資源文件的基礎路徑
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.resources_path = os.path.join(project_root, 'config')
        
        # 記錄路徑
        self.custom_dict_path = None
        self.stopwords_path = None
        
        # 載入自訂詞典或默認詞典
        if custom_dict_path:
            jieba.load_userdict(custom_dict_path)
            self.custom_dict_path = custom_dict_path
            # 計算預設詞典詞數
            dict_words = self._count_words_in_dict(custom_dict_path)
            print(f"已載入預設詞典: {custom_dict_path}, 共 {dict_words} 個詞")
        else:
            default_dict_path = os.path.join(self.resources_path, 'custom_dict.txt')
            if os.path.exists(default_dict_path):
                jieba.load_userdict(default_dict_path)
                self.custom_dict_path = default_dict_path
                # 計算預設詞典詞數
                dict_words = self._count_words_in_dict(default_dict_path)
                print(f"已載入預設詞典: {default_dict_path}, 共 {dict_words} 個詞")
        
        # 載入停用詞
        self.stopwords = set()
        if stopwords_path:
            self.load_stopwords(stopwords_path)
            self.stopwords_path = stopwords_path
            print(f"已載入預設停用詞表: {stopwords_path}, 共 {len(self.stopwords)} 個詞")
        else:
            default_stopwords_path = os.path.join(self.resources_path, 'chinese_stopwords.txt')
            if os.path.exists(default_stopwords_path):
                self.load_stopwords(default_stopwords_path)
                self.stopwords_path = default_stopwords_path
                print(f"已載入預設停用詞表: {default_stopwords_path}, 共 {len(self.stopwords)} 個詞")
        
        # 載入情感詞典
        self.positive_words = self._load_sentiment_words('positive_words.txt')
        self.negative_words = self._load_sentiment_words('negative_words.txt')
    
    def _count_words_in_dict(self, dict_path):
        """計算詞典中的詞數（排除註釋行）"""
        count = 0
        with open(dict_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳過空行和以#開頭的註釋行
                if line and not line.startswith('#'):
                    count += 1
        return count
    
    def _load_sentiment_words(self, filename):
        """載入情感詞典"""
        filepath = os.path.join(self.resources_path, filename)
        words = set()
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        words.add(line)
            print(f"已載入情感詞典: {filepath}, 共 {len(words)} 個詞")
        return words
    
    def load_stopwords(self, file_path):
        """載入停用詞表"""
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    self.stopwords.add(line)
        # 更新停用詞表路徑
        self.stopwords_path = file_path
    
    def preprocess_text(self, text):
        """文本預處理：分詞、去除停用詞、標點符號等"""
        # 移除特殊字符和標點
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        
        # 分詞和詞性標注
        words = pseg.cut(text)
        
        # 過濾停用詞和單字
        filtered = [
            (word, flag) for word, flag in words 
            if word not in self.stopwords and len(word) > 1
        ]
        return filtered
    
    def analyze_text(self, text):
        """分析文本並返回統計結果"""
        processed = self.preprocess_text(text)
        
        # 詞頻統計
        word_freq = Counter([word for word, _ in processed])
        
        # 詞性統計
        pos_freq = Counter([flag for _, flag in processed])
        
        # 詞性-詞對應關係
        pos_word_mapping = {}
        for word, pos in processed:
            if pos not in pos_word_mapping:
                pos_word_mapping[pos] = set()
            pos_word_mapping[pos].add(word)
        
        # 計算平均詞長
        avg_word_len = sum(len(word) for word, _ in processed) / len(processed) if processed else 0
        
        return {
            'word_frequency': dict(word_freq.most_common()),
            'pos_frequency': dict(pos_freq.most_common()),
            'pos_word_mapping': {k: list(v) for k, v in pos_word_mapping.items()},
            'avg_word_length': round(avg_word_len, 2),
            'total_words': len(processed)
        }
    
    def analyze_files(self, file_paths):
        """批量分析多個文件"""
        results = {}
        for file_path in file_paths:
            try:
                text = FileUtils.read_file(file_path)
                results[file_path] = self.analyze_text(text)
            except Exception as e:
                results[file_path] = {"error": str(e)}
                print(f"Error processing {file_path}: {e}")
        return results
    
    def analyze_files_parallel(self, file_paths):
        """使用多進程並行分析多個文件"""
        with mp.Pool(processes=mp.cpu_count()) as pool:
            results_list = pool.map(self._analyze_single_file, file_paths)
        
        return {file_path: result for file_path, result in zip(file_paths, results_list)}
    
    def _analyze_single_file(self, file_path):
        """分析單個文件（用於並行處理）"""
        try:
            text = FileUtils.read_file(file_path)
            return self.analyze_text(text)
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_sentiment(self, text):
        """分析文本情感傾向 (positive, negative, neutral)
        
        使用載入的情感詞典來分析文本的情感傾向
        """
        words = [word for word, _ in self.preprocess_text(text)]
        
        # 將未分詞的文本也進行分析，可能有些情感詞在預處理中被過濾掉了
        raw_words = jieba.cut(text)
        
        # 計算正面詞和負面詞的出現次數
        positive_count = sum(1 for word in words if word in self.positive_words)
        positive_count += sum(1 for word in raw_words if word in self.positive_words and word not in words)
        
        negative_count = sum(1 for word in words if word in self.negative_words)
        negative_count += sum(1 for word in raw_words if word in self.negative_words and word not in words)
        
        # 計算情感得分
        sentiment_score = positive_count - negative_count
        
        # 確定情感標籤
        if sentiment_score > 0:
            sentiment_label = 'positive'
        elif sentiment_score < 0:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        return {
            'sentiment_score': sentiment_score,
            'sentiment_label': sentiment_label,
            'positive_count': positive_count,
            'negative_count': negative_count
        }
    
    def generate_summary(self, text, sentence_count=3):
        """生成文本摘要"""
        # 分句
        sentences = re.split(r'[。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return "無法生成摘要：文本為空或不包含完整句子"
        
        if len(sentences) <= sentence_count:
            return '。'.join(sentences) + '。'
        
        # 提取關鍵詞
        keywords = jieba.analyse.extract_tags(text, topK=10)
        
        # 根據關鍵詞對句子評分
        sentence_scores = []
        for sentence in sentences:
            score = sum(1 for kw in keywords if kw in sentence)
            sentence_scores.append((sentence, score))
        
        # 獲取得分最高的句子
        top_sentences = sorted(sentence_scores, key=lambda x: x[1], reverse=True)[:sentence_count]
        
        # 按照原文順序排列句子
        original_order = sorted(
            [s for s in top_sentences if s[1] > 0],
            key=lambda x: sentences.index(x[0])
        )
        
        if not original_order:
            original_order = top_sentences
        
        summary = '。'.join(s[0] for s in original_order) + '。'
        return summary
    
    def extract_ngrams(self, text, n=2):
        """提取文本中的n-gram詞組"""
        words = [word for word, _ in self.preprocess_text(text)]
        
        if len(words) < n:
            return Counter()
        
        ngrams = []
        for i in range(len(words) - n + 1):
            ngrams.append(''.join(words[i:i+n]))
        
        return Counter(ngrams)
    
    def extract_entities(self, text):
        """提取命名實體（人名、地名、機構名等）"""
        words = pseg.cut(text)
        
        entities = {
            'person': [],      # 人名
            'location': [],    # 地名
            'organization': [] # 機構名
        }
        
        pos_mapping = {
            'nr': 'person',
            'ns': 'location',
            'nt': 'organization'
        }
        
        for word, flag in words:
            if flag in pos_mapping and len(word) > 1:
                entities[pos_mapping[flag]].append(word)
        
        return {k: list(Counter(v).keys()) for k, v in entities.items()}
    
    def convert_text(self, text, to_traditional=True):
        """繁簡體中文轉換"""
        try:
            import opencc
            converter = opencc.OpenCC('s2t' if to_traditional else 't2s')
            return converter.convert(text)
        except ImportError:
            print("請安裝OpenCC: pip install opencc-python-reimplemented")
            return text
    
    def count_chinese_characters(self, text):
        """計算文本中的中文字符數量"""
        # 使用正則表達式匹配中文字符 (Unicode 範圍: \u4e00-\u9fff)
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        return len(chinese_chars)
    
    def keyword_extraction(self, text, top_k=20):
        """提取文本關鍵詞"""
        keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=True)
        return {word: float(weight) for word, weight in keywords}