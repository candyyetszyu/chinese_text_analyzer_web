# -*- coding: utf-8 -*-
import numpy as np
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import os
import sys

# Conditional imports for advanced similarity
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TextSimilarityAnalyzer:
    def __init__(self, use_gpu=False, model_name='paraphrase-multilingual-MiniLM-L12-v2'):
        """
        初始化文本相似度分析器
        
        Args:
            use_gpu (bool): 是否使用GPU加速（需要CUDA支持）
            model_name (str): 使用的預訓練模型名稱
        """
        self.use_gpu = use_gpu and TORCH_AVAILABLE and torch.cuda.is_available()
        self.device = 'cuda' if self.use_gpu else 'cpu'
        
        # 初始化語義相似度模型
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.semantic_model = SentenceTransformer(model_name, device=self.device)
                self.semantic_available = True
                print(f"已載入語義相似度模型: {model_name} (使用設備: {self.device})")
            except Exception as e:
                print(f"無法載入語義相似度模型: {e}")
                self.semantic_available = False
        else:
            self.semantic_available = False
            
        # 初始化TF-IDF向量化器
        self.tfidf_vectorizer = TfidfVectorizer(tokenizer=self._jieba_tokenizer, lowercase=False)
        
    def _jieba_tokenizer(self, text):
        """使用jieba進行分詞"""
        return list(jieba.cut(text))
    
    def jaccard_similarity(self, text1, text2):
        """計算Jaccard相似度"""
        words1 = set(jieba.cut(text1))
        words2 = set(jieba.cut(text2))
        
        intersection = words1 & words2
        union = words1 | words2
        
        if len(union) == 0:
            return 0.0
        return len(intersection) / len(union)
    
    def cosine_similarity_tfidf(self, texts):
        """
        使用TF-IDF計算文本間的余弦相似度
        
        Args:
            texts (list): 文本列表
            
        Returns:
            numpy.ndarray: 相似度矩陣
        """
        try:
            # 計算TF-IDF矩陣
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            # 計算余弦相似度
            similarity_matrix = cosine_similarity(tfidf_matrix)
            return similarity_matrix
        except Exception as e:
            print(f"TF-IDF相似度計算錯誤: {e}")
            return np.zeros((len(texts), len(texts)))
    
    def semantic_similarity(self, texts):
        """
        使用語義模型計算文本間的相似度
        
        Args:
            texts (list): 文本列表
            
        Returns:
            numpy.ndarray: 相似度矩陣
        """
        if not self.semantic_available:
            print("語義相似度模型不可用，使用TF-IDF替代")
            return self.cosine_similarity_tfidf(texts)
        
        try:
            # 編碼文本
            embeddings = self.semantic_model.encode(texts, convert_to_tensor=True)
            
            # 計算余弦相似度
            similarity_matrix = cosine_similarity(embeddings.cpu().numpy())
            return similarity_matrix
        except Exception as e:
            print(f"語義相似度計算錯誤: {e}")
            return self.cosine_similarity_tfidf(texts)
    
    def edit_distance_similarity(self, text1, text2):
        """計算編輯距離相似度（字符級別）"""
        def levenshtein_distance(s1, s2):
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        max_len = max(len(text1), len(text2))
        if max_len == 0:
            return 1.0
        
        distance = levenshtein_distance(text1, text2)
        return 1.0 - (distance / max_len)
    
    def word_overlap_similarity(self, text1, text2):
        """計算詞重疊相似度"""
        words1 = Counter(jieba.cut(text1))
        words2 = Counter(jieba.cut(text2))
        
        # 計算共同詞的頻率
        overlap = sum((words1 & words2).values())
        total = sum(words1.values()) + sum(words2.values())
        
        if total == 0:
            return 0.0
        return (2 * overlap) / total
    
    def comprehensive_similarity_analysis(self, texts, labels=None):
        """
        綜合相似度分析
        
        Args:
            texts (list): 文本列表
            labels (list): 文本標籤列表（可選）
            
        Returns:
            dict: 包含各種相似度指標的結果
        """
        if labels is None:
            labels = [f"文本{i+1}" for i in range(len(texts))]
        
        results = {
            'labels': labels,
            'text_count': len(texts),
            'similarities': {}
        }
        
        # TF-IDF余弦相似度
        tfidf_sim = self.cosine_similarity_tfidf(texts)
        results['similarities']['tfidf_cosine'] = tfidf_sim.tolist()
        
        # 語義相似度
        semantic_sim = self.semantic_similarity(texts)
        results['similarities']['semantic'] = semantic_sim.tolist()
        
        # 計算兩兩相似度的詳細結果
        pairwise_results = []
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                pair_result = {
                    'text1_index': i,
                    'text2_index': j,
                    'text1_label': labels[i],
                    'text2_label': labels[j],
                    'jaccard_similarity': self.jaccard_similarity(texts[i], texts[j]),
                    'edit_distance_similarity': self.edit_distance_similarity(texts[i], texts[j]),
                    'word_overlap_similarity': self.word_overlap_similarity(texts[i], texts[j]),
                    'tfidf_cosine_similarity': tfidf_sim[i][j],
                    'semantic_similarity': semantic_sim[i][j]
                }
                pairwise_results.append(pair_result)
        
        results['pairwise_comparisons'] = pairwise_results
        
        # 計算平均相似度
        avg_similarities = {}
        for method in ['jaccard_similarity', 'edit_distance_similarity', 'word_overlap_similarity', 
                      'tfidf_cosine_similarity', 'semantic_similarity']:
            values = [pair[method] for pair in pairwise_results]
            avg_similarities[method] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values)
            }
        
        results['average_similarities'] = avg_similarities
        
        return results
    
    def find_most_similar_pairs(self, texts, labels=None, method='semantic', top_k=5):
        """
        找出最相似的文本對
        
        Args:
            texts (list): 文本列表
            labels (list): 文本標籤列表
            method (str): 相似度計算方法
            top_k (int): 返回前k個最相似的對
            
        Returns:
            list: 最相似的文本對
        """
        if labels is None:
            labels = [f"文本{i+1}" for i in range(len(texts))]
        
        pairs = []
        
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                if method == 'semantic':
                    similarity = self.semantic_similarity([texts[i], texts[j]])[0][1]
                elif method == 'tfidf':
                    similarity = self.cosine_similarity_tfidf([texts[i], texts[j]])[0][1]
                elif method == 'jaccard':
                    similarity = self.jaccard_similarity(texts[i], texts[j])
                elif method == 'word_overlap':
                    similarity = self.word_overlap_similarity(texts[i], texts[j])
                else:
                    similarity = self.edit_distance_similarity(texts[i], texts[j])
                
                pairs.append({
                    'text1_index': i,
                    'text2_index': j,
                    'text1_label': labels[i],
                    'text2_label': labels[j],
                    'similarity': similarity,
                    'method': method
                })
        
        # 按相似度排序並返回前k個
        pairs.sort(key=lambda x: x['similarity'], reverse=True)
        return pairs[:top_k]
    
    def cluster_similar_texts(self, texts, labels=None, method='semantic', threshold=0.7):
        """
        根據相似度聚類文本
        
        Args:
            texts (list): 文本列表
            labels (list): 文本標籤列表
            method (str): 相似度計算方法
            threshold (float): 相似度閾值
            
        Returns:
            list: 聚類結果
        """
        if labels is None:
            labels = [f"文本{i+1}" for i in range(len(texts))]
        
        # 計算相似度矩陣
        if method == 'semantic':
            sim_matrix = self.semantic_similarity(texts)
        else:
            sim_matrix = self.cosine_similarity_tfidf(texts)
        
        # 簡單的相似度聚類
        visited = [False] * len(texts)
        clusters = []
        
        for i in range(len(texts)):
            if visited[i]:
                continue
            
            cluster = [{'index': i, 'label': labels[i], 'text': texts[i]}]
            visited[i] = True
            
            for j in range(i + 1, len(texts)):
                if not visited[j] and sim_matrix[i][j] >= threshold:
                    cluster.append({'index': j, 'label': labels[j], 'text': texts[j]})
                    visited[j] = True
            
            clusters.append(cluster)
        
        return clusters 