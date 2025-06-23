# -*- coding: utf-8 -*-
"""
Task Queue System
使用Celery和Redis實現的批量任務處理系統
"""

import os
import sys
import uuid
import json
import time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from enum import Enum

# Celery imports
try:
    from celery import Celery
    from celery.result import AsyncResult
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

# Redis imports
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.analyzer import ChineseTextAnalyzer
from src.utils.file_parsers import ExtendedFileParser

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"

class TaskType(Enum):
    TEXT_ANALYSIS = "text_analysis"
    SIMILARITY_ANALYSIS = "similarity_analysis"
    BATCH_FILE_PROCESSING = "batch_file_processing"
    VISUALIZATION_GENERATION = "visualization_generation"
    FORMAT_CONVERSION = "format_conversion"

@dataclass
class Task:
    id: str
    type: TaskType
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: int = 0
    parameters: Dict[str, Any] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    estimated_duration: Optional[int] = None

class TaskQueue:
    """任務隊列管理器"""
    
    def __init__(self, redis_url='redis://localhost:6379/0', enable_celery=True):
        self.redis_url = redis_url
        self.enable_celery = enable_celery and CELERY_AVAILABLE
        
        # 初始化Redis連接
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
                self.redis_available = True
                print("Redis連接成功")
            except Exception as e:
                print(f"Redis連接失敗: {e}")
                self.redis_available = False
        else:
            self.redis_available = False
        
        # 初始化Celery
        if self.enable_celery:
            self.celery_app = Celery('text_analyzer_tasks', broker=redis_url, backend=redis_url)
            self.celery_app.conf.update(
                task_serializer='json',
                accept_content=['json'],
                result_serializer='json',
                timezone='UTC',
                enable_utc=True,
                task_track_started=True,
                task_time_limit=30 * 60,  # 30分鐘超時
                task_soft_time_limit=25 * 60,  # 25分鐘軟超時
            )
            print("Celery配置完成")
        else:
            self.celery_app = None
            print("Celery不可用，使用本地處理")
        
        # 內存任務存儲（如果Redis不可用）
        self.local_tasks = {}
        
        # 初始化分析器
        self.analyzer = ChineseTextAnalyzer()
        self.file_parser = ExtendedFileParser()
    
    def create_task(self, task_type: TaskType, parameters: Dict[str, Any], 
                   estimated_duration: Optional[int] = None) -> str:
        """創建新任務"""
        task_id = str(uuid.uuid4())
        
        task = Task(
            id=task_id,
            type=task_type,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            parameters=parameters,
            estimated_duration=estimated_duration
        )
        
        # 保存任務
        self._save_task(task)
        
        # 如果Celery可用，提交到隊列
        if self.enable_celery and self.celery_app:
            try:
                self._submit_celery_task(task)
            except Exception as e:
                print(f"提交Celery任務失敗: {e}")
                # 回退到本地處理
                self._process_task_locally(task_id)
        else:
            # 本地處理
            self._process_task_locally(task_id)
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Task]:
        """獲取任務狀態"""
        if self.redis_available:
            try:
                task_data = self.redis_client.get(f"task:{task_id}")
                if task_data:
                    task_dict = json.loads(task_data)
                    # 轉換日期字符串回datetime對象
                    for date_field in ['created_at', 'started_at', 'completed_at']:
                        if task_dict.get(date_field):
                            task_dict[date_field] = datetime.fromisoformat(task_dict[date_field])
                    task_dict['type'] = TaskType(task_dict['type'])
                    task_dict['status'] = TaskStatus(task_dict['status'])
                    return Task(**task_dict)
            except Exception as e:
                print(f"從Redis獲取任務失敗: {e}")
        
        return self.local_tasks.get(task_id)
    
    def list_tasks(self, status_filter: Optional[TaskStatus] = None, 
                  type_filter: Optional[TaskType] = None, limit: int = 50) -> List[Task]:
        """列出任務"""
        tasks = []
        
        if self.redis_available:
            try:
                keys = self.redis_client.keys("task:*")
                for key in keys[:limit]:
                    task_data = self.redis_client.get(key)
                    if task_data:
                        task_dict = json.loads(task_data)
                        for date_field in ['created_at', 'started_at', 'completed_at']:
                            if task_dict.get(date_field):
                                task_dict[date_field] = datetime.fromisoformat(task_dict[date_field])
                        task_dict['type'] = TaskType(task_dict['type'])
                        task_dict['status'] = TaskStatus(task_dict['status'])
                        task = Task(**task_dict)
                        
                        # 應用過濾器
                        if status_filter and task.status != status_filter:
                            continue
                        if type_filter and task.type != type_filter:
                            continue
                        
                        tasks.append(task)
            except Exception as e:
                print(f"從Redis列出任務失敗: {e}")
        else:
            for task in self.local_tasks.values():
                if status_filter and task.status != status_filter:
                    continue
                if type_filter and task.type != type_filter:
                    continue
                tasks.append(task)
        
        # 按創建時間排序
        tasks.sort(key=lambda x: x.created_at, reverse=True)
        return tasks[:limit]
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任務"""
        task = self.get_task_status(task_id)
        if not task:
            return False
        
        if task.status in [TaskStatus.SUCCESS, TaskStatus.FAILURE, TaskStatus.CANCELLED]:
            return False
        
        # 更新任務狀態
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now()
        self._save_task(task)
        
        # 如果使用Celery，撤銷任務
        if self.enable_celery and self.celery_app:
            try:
                self.celery_app.control.revoke(task_id, terminate=True)
            except Exception as e:
                print(f"撤銷Celery任務失敗: {e}")
        
        return True
    
    def _save_task(self, task: Task):
        """保存任務"""
        task_dict = asdict(task)
        
        # 轉換datetime對象為字符串
        for date_field in ['created_at', 'started_at', 'completed_at']:
            if task_dict.get(date_field):
                task_dict[date_field] = task_dict[date_field].isoformat()
        
        # 轉換枚舉為字符串
        task_dict['type'] = task.type.value
        task_dict['status'] = task.status.value
        
        if self.redis_available:
            try:
                self.redis_client.setex(
                    f"task:{task.id}", 
                    7 * 24 * 3600,  # 7天過期
                    json.dumps(task_dict, ensure_ascii=False)
                )
            except Exception as e:
                print(f"保存任務到Redis失敗: {e}")
                self.local_tasks[task.id] = task
        else:
            self.local_tasks[task.id] = task
    
    def _submit_celery_task(self, task: Task):
        """提交任務到Celery"""
        # 根據任務類型選擇處理函數
        if task.type == TaskType.TEXT_ANALYSIS:
            self.celery_app.send_task('analyze_text', args=[task.id, task.parameters])
        elif task.type == TaskType.SIMILARITY_ANALYSIS:
            self.celery_app.send_task('analyze_similarity', args=[task.id, task.parameters])
        elif task.type == TaskType.BATCH_FILE_PROCESSING:
            self.celery_app.send_task('process_batch_files', args=[task.id, task.parameters])
        elif task.type == TaskType.VISUALIZATION_GENERATION:
            self.celery_app.send_task('generate_visualizations', args=[task.id, task.parameters])
        elif task.type == TaskType.FORMAT_CONVERSION:
            self.celery_app.send_task('convert_format', args=[task.id, task.parameters])
    
    def _process_task_locally(self, task_id: str):
        """本地處理任務"""
        import threading
        
        def process():
            task = self.get_task_status(task_id)
            if not task:
                return
            
            try:
                # 更新任務狀態
                task.status = TaskStatus.PROCESSING
                task.started_at = datetime.now()
                self._save_task(task)
                
                # 根據任務類型處理
                if task.type == TaskType.TEXT_ANALYSIS:
                    result = self._analyze_text_local(task.parameters)
                elif task.type == TaskType.SIMILARITY_ANALYSIS:
                    result = self._analyze_similarity_local(task.parameters)
                elif task.type == TaskType.BATCH_FILE_PROCESSING:
                    result = self._process_batch_files_local(task.parameters)
                elif task.type == TaskType.VISUALIZATION_GENERATION:
                    result = self._generate_visualizations_local(task.parameters)
                elif task.type == TaskType.FORMAT_CONVERSION:
                    result = self._convert_format_local(task.parameters)
                else:
                    raise ValueError(f"不支持的任務類型: {task.type}")
                
                # 任務成功完成
                task.status = TaskStatus.SUCCESS
                task.result = result
                task.progress = 100
                task.completed_at = datetime.now()
                
            except Exception as e:
                # 任務失敗
                task.status = TaskStatus.FAILURE
                task.error_message = str(e)
                task.completed_at = datetime.now()
                print(f"任務 {task_id} 處理失敗: {e}")
            
            finally:
                self._save_task(task)
        
        # 在新線程中處理任務
        thread = threading.Thread(target=process)
        thread.daemon = True
        thread.start()
    
    def _analyze_text_local(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """本地文本分析"""
        text = parameters.get('text', '')
        options = parameters.get('options', {})
        
        result = self.analyzer.analyze_text(text)
        
        if options.get('include_sentiment', True):
            sentiment = self.analyzer.analyze_sentiment(text)
            result['sentiment'] = sentiment
        
        if options.get('include_keywords', True):
            keywords = self.analyzer.keyword_extraction(text)
            result['keywords'] = keywords
        
        if options.get('include_entities', True):
            entities = self.analyzer.extract_entities(text)
            result['entities'] = entities
        
        if options.get('include_ngrams', True):
            ngrams = self.analyzer.extract_ngrams(text)
            result['ngrams'] = ngrams
        
        return result
    
    def _analyze_similarity_local(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """本地相似度分析"""
        from src.core.similarity import TextSimilarityAnalyzer
        
        texts = parameters.get('texts', [])
        labels = parameters.get('labels')
        method = parameters.get('method', 'semantic')
        
        similarity_analyzer = TextSimilarityAnalyzer()
        result = similarity_analyzer.comprehensive_similarity_analysis(texts, labels)
        
        return result
    
    def _process_batch_files_local(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """本地批量文件處理"""
        file_paths = parameters.get('file_paths', [])
        analysis_options = parameters.get('analysis_options', {})
        
        results = {}
        
        for i, file_path in enumerate(file_paths):
            try:
                # 解析文件
                parsed = self.file_parser.parse_file(file_path)
                text = parsed['content']
                
                # 分析文本
                analysis_result = self._analyze_text_local({
                    'text': text,
                    'options': analysis_options
                })
                
                analysis_result['file_metadata'] = parsed['metadata']
                results[file_path] = analysis_result
                
                # 更新進度
                progress = int((i + 1) / len(file_paths) * 100)
                task = self.get_task_status(parameters.get('task_id'))
                if task:
                    task.progress = progress
                    self._save_task(task)
                
            except Exception as e:
                results[file_path] = {'error': str(e)}
        
        return results
    
    def _generate_visualizations_local(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """本地生成視覺化"""
        from src.core.visualization import Visualizer
        from src.core.advanced_visualization import AdvancedVisualizer
        
        analysis_results = parameters.get('analysis_results', {})
        output_dir = parameters.get('output_dir', 'visualizations')
        viz_types = parameters.get('visualization_types', ['basic'])
        
        os.makedirs(output_dir, exist_ok=True)
        
        generated_files = []
        
        if 'basic' in viz_types:
            # 基本視覺化
            report_files = Visualizer.create_visualization_report(
                analysis_results, output_dir, prefix='basic_'
            )
            generated_files.extend(report_files)
        
        if 'advanced' in viz_types:
            # 高級視覺化
            adv_viz = AdvancedVisualizer()
            # 這裡可以添加高級視覺化邏輯
        
        return {
            'generated_files': generated_files,
            'output_directory': output_dir
        }
    
    def _convert_format_local(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """本地格式轉換"""
        from src.utils.convert_chinese import ConversionUtils
        
        text = parameters.get('text', '')
        conversion_type = parameters.get('conversion_type', 's2t')
        
        converter = ConversionUtils()
        
        if conversion_type == 's2t':
            converted_text = converter.simplified_to_traditional(text)
        elif conversion_type == 't2s':
            converted_text = converter.traditional_to_simplified(text)
        else:
            raise ValueError(f"不支持的轉換類型: {conversion_type}")
        
        return {
            'original_text': text,
            'converted_text': converted_text,
            'conversion_type': conversion_type
        }

# Celery任務定義（如果Celery可用）
if CELERY_AVAILABLE:
    # 這些任務函數會在Celery worker中執行
    task_queue_instance = None
    
    def get_task_queue():
        global task_queue_instance
        if task_queue_instance is None:
            task_queue_instance = TaskQueue()
        return task_queue_instance
    
    @get_task_queue().celery_app.task(bind=True, name='analyze_text')
    def analyze_text_celery(self, task_id, parameters):
        tq = get_task_queue()
        return tq._analyze_text_local(parameters)
    
    @get_task_queue().celery_app.task(bind=True, name='analyze_similarity')
    def analyze_similarity_celery(self, task_id, parameters):
        tq = get_task_queue()
        return tq._analyze_similarity_local(parameters)
    
    @get_task_queue().celery_app.task(bind=True, name='process_batch_files')
    def process_batch_files_celery(self, task_id, parameters):
        tq = get_task_queue()
        return tq._process_batch_files_local(parameters)
    
    @get_task_queue().celery_app.task(bind=True, name='generate_visualizations')
    def generate_visualizations_celery(self, task_id, parameters):
        tq = get_task_queue()
        return tq._generate_visualizations_local(parameters)
    
    @get_task_queue().celery_app.task(bind=True, name='convert_format')
    def convert_format_celery(self, task_id, parameters):
        tq = get_task_queue()
        return tq._convert_format_local(parameters) 