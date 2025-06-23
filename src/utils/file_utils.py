# -*- coding: utf-8 -*-
import os
import json
import csv
import shutil

class FileUtils:
    @staticmethod
    def read_file(file_path, encoding='utf-8'):
        """讀取文本文件"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read()
    
    @staticmethod
    def save_results(results, output_path):
        """保存分析結果為JSON文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def save_results_as_csv(results, output_path):
        """保存分析結果為CSV文件"""
        try:
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                
                # 保存詞頻分析結果
                writer.writerow(['Word', 'Frequency'])
                for word, freq in results.get('word_frequency', {}).items():
                    writer.writerow([word, freq])
                
                writer.writerow([])  # 空行做分隔
                
                # 保存詞性統計結果
                writer.writerow(['POS', 'Count'])
                for pos, count in results.get('pos_frequency', {}).items():
                    writer.writerow([pos, count])
                
                # 保存其他統計信息
                writer.writerow([])
                writer.writerow(['Metric', 'Value'])
                for key, value in results.items():
                    if key not in ['word_frequency', 'pos_frequency', 'pos_word_mapping']:
                        writer.writerow([key, value])
            
            return True
        except Exception as e:
            print(f"保存CSV時出錯: {e}")
            return False
    
    @staticmethod
    def save_results_as_excel(results, output_path):
        """保存分析結果為Excel文件"""
        try:
            import pandas as pd
            
            # 創建一個Excel writer對象
            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                # 詞頻分析結果
                if 'word_frequency' in results:
                    word_df = pd.DataFrame(list(results['word_frequency'].items()), 
                                          columns=['Word', 'Frequency'])
                    word_df.sort_values('Frequency', ascending=False, inplace=True)
                    word_df.to_excel(writer, sheet_name='Word Frequency', index=False)
                
                # 詞性統計結果
                if 'pos_frequency' in results:
                    pos_df = pd.DataFrame(list(results['pos_frequency'].items()),
                                         columns=['POS', 'Count'])
                    pos_df.to_excel(writer, sheet_name='POS Statistics', index=False)
                
                # 命名實體結果（如果有）
                if 'entities' in results:
                    entities = results['entities']
                    dfs = []
                    for entity_type, entity_list in entities.items():
                        if entity_list:  # 如果列表不為空
                            df = pd.DataFrame({entity_type: entity_list})
                            dfs.append(df)
                    
                    if dfs:
                        # 合併所有dataframe
                        entity_df = pd.concat(dfs, axis=1)
                        entity_df.to_excel(writer, sheet_name='Named Entities', index=False)
                
                # 情感分析結果（如果有）
                if 'sentiment' in results:
                    sentiment = results['sentiment']
                    sentiment_df = pd.DataFrame(list(sentiment.items()),
                                               columns=['Metric', 'Value'])
                    sentiment_df.to_excel(writer, sheet_name='Sentiment Analysis', index=False)
                
                # 摘要信息頁面
                summary_data = []
                for key, value in results.items():
                    if key not in ['word_frequency', 'pos_frequency', 'pos_word_mapping', 
                                 'entities', 'sentiment']:
                        if not isinstance(value, dict) and not isinstance(value, list):
                            summary_data.append([key, value])
                
                if summary_data:
                    summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            return True
        except ImportError:
            print("保存Excel需要安裝pandas和xlsxwriter: pip install pandas xlsxwriter")
            return False
        except Exception as e:
            print(f"保存Excel時出錯: {e}")
            return False
    
    @staticmethod
    def export_results(results, output_path, formats=None):
        """導出分析結果為多種格式
        
        Args:
            results: 分析結果字典
            output_path: 輸出文件路徑（不包含擴展名）
            formats: 導出格式列表，例如 ['json', 'csv', 'excel']
        """
        if formats is None:
            formats = ['json']
        
        success = {}
        
        # 創建輸出目錄
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 導出為不同格式
        base_filename = os.path.basename(output_path)
        
        for fmt in formats:
            fmt = fmt.lower()
            if fmt == 'json':
                json_path = f"{output_path}.json"
                success['json'] = FileUtils.save_results(results, json_path)
            elif fmt == 'csv':
                csv_path = f"{output_path}.csv"
                success['csv'] = FileUtils.save_results_as_csv(results, csv_path)
            elif fmt == 'excel':
                excel_path = f"{output_path}.xlsx"
                success['excel'] = FileUtils.save_results_as_excel(results, excel_path)
        
        return success
    
    @staticmethod
    def backup_file(file_path, backup_suffix='.bak'):
        """備份文件"""
        if os.path.exists(file_path):
            backup_path = file_path + backup_suffix
            shutil.copy2(file_path, backup_path)
            return backup_path
        return None
    
    @staticmethod
    def get_file_encoding(file_path):
        """檢測文件編碼"""
        try:
            import chardet
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read())
            return result['encoding']
        except ImportError:
            print("檢測編碼需要安裝chardet: pip install chardet")
            return None
        except Exception as e:
            print(f"檢測文件編碼時出錯: {e}")
            return None
    
    @staticmethod
    def get_file_list(folder_path, extensions=['.txt', '.csv']):
        """獲取文件夾中指定擴展名的文件列表"""
        return [os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                if os.path.splitext(f)[1].lower() in extensions]