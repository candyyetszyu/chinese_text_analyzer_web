#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chinese Text Analyzer - New Features Demo
演示新功能：文本相似度、高級視覺化、任務隊列、GPU加速、多格式支持
"""

import os
import sys
import time
import json
from pathlib import Path

# Add src to path
sys.path.append('src')

def demo_text_similarity():
    """演示文本相似度分析功能"""
    print("\n" + "="*60)
    print("🔍 文本相似度分析演示")
    print("="*60)
    
    try:
        from src.core.similarity import TextSimilarityAnalyzer
        
        # 示例文本
        texts = [
            "今天天氣很好，陽光明媚，適合出門散步。",
            "今日天氣晴朗，陽光燦爛，很適合外出運動。", 
            "昨天下雨了，路上很濕滑，出行不便。",
            "昨日下了大雨，道路濕滑，交通受阻。",
            "我喜歡吃中國菜，特別是川菜和粵菜。"
        ]
        
        labels = ["文本1", "文本2", "文本3", "文本4", "文本5"]
        
        print("📝 分析文本:")
        for i, text in enumerate(texts):
            print(f"  {labels[i]}: {text}")
        
        # 初始化相似度分析器
        print("\n🚀 初始化相似度分析器...")
        similarity_analyzer = TextSimilarityAnalyzer(use_gpu=False)
        
        # 綜合相似度分析
        print("\n📊 執行綜合相似度分析...")
        results = similarity_analyzer.comprehensive_similarity_analysis(texts, labels)
        
        print(f"\n✅ 分析完成！共分析 {results['text_count']} 個文本")
        print(f"📈 生成 {len(results['pairwise_comparisons'])} 個兩兩比較結果")
        
        # 顯示最相似的文本對
        print("\n🏆 最相似的文本對（語義相似度）:")
        similar_pairs = similarity_analyzer.find_most_similar_pairs(
            texts, labels, method='semantic', top_k=3
        )
        
        for i, pair in enumerate(similar_pairs):
            print(f"  {i+1}. {pair['text1_label']} ↔ {pair['text2_label']}")
            print(f"     相似度: {pair['similarity']:.3f}")
        
        # 聚類相似文本
        print("\n🎯 文本聚類結果（閾值=0.7）:")
        clusters = similarity_analyzer.cluster_similar_texts(
            texts, labels, method='semantic', threshold=0.7
        )
        
        for i, cluster in enumerate(clusters):
            print(f"  集群 {i+1}: {[item['label'] for item in cluster]}")
        
        return results
        
    except ImportError as e:
        print(f"❌ 文本相似度功能不可用: {e}")
        print("💡 請安裝: pip install sentence-transformers torch")
        return None

def demo_advanced_visualization(similarity_results=None):
    """演示高級視覺化功能"""
    print("\n" + "="*60) 
    print("📊 高級視覺化演示")
    print("="*60)
    
    try:
        from src.core.advanced_visualization import AdvancedVisualizer
        import numpy as np
        
        print("🚀 初始化高級視覺化器...")
        adv_viz = AdvancedVisualizer()
        
        # 示例詞頻數據
        word_freq = {
            '天氣': 15, '陽光': 12, '散步': 8, '運動': 10,
            '下雨': 6, '道路': 5, '交通': 4, '中國菜': 7,
            '川菜': 3, '粵菜': 3, '今天': 8, '昨天': 6,
            '出門': 5, '外出': 4, '濕滑': 3, '晴朗': 6
        }
        
        print("📈 生成詞頻樹狀圖...")
        if adv_viz.plotly_available:
            treemap_fig = adv_viz.plot_word_frequency_treemap(word_freq)
            treemap_fig.write_html("visualizations/treemap.html")
            print("✅ 樹狀圖已保存到: visualizations/treemap.html")
        else:
            print("❌ Plotly不可用，跳過樹狀圖生成")
        
        # 相似度熱力圖
        if similarity_results and adv_viz.plotly_available:
            print("\n🔥 生成相似度熱力圖...")
            similarity_matrix = np.array(similarity_results['similarities']['semantic'])
            labels = similarity_results['labels']
            
            # 靜態熱力圖
            os.makedirs("visualizations", exist_ok=True)
            adv_viz.plot_similarity_heatmap(
                similarity_matrix, labels, 
                save_path="visualizations/similarity_heatmap.png"
            )
            print("✅ 靜態熱力圖已保存到: visualizations/similarity_heatmap.png")
            
            # 交互式熱力圖
            interactive_heatmap = adv_viz.plot_interactive_similarity_heatmap(
                similarity_matrix, labels
            )
            interactive_heatmap.write_html("visualizations/interactive_heatmap.html")
            print("✅ 交互式熱力圖已保存到: visualizations/interactive_heatmap.html")
            
            # 網絡圖
            print("\n🌐 生成文本相似度網絡圖...")
            if adv_viz.networkx_available:
                adv_viz.plot_text_network(
                    similarity_matrix, labels, threshold=0.5,
                    save_path="visualizations/similarity_network.png"
                )
                print("✅ 網絡圖已保存到: visualizations/similarity_network.png")
                
                # 交互式網絡圖
                interactive_network = adv_viz.plot_interactive_network(
                    similarity_matrix, labels, threshold=0.5
                )
                interactive_network.write_html("visualizations/interactive_network.html")
                print("✅ 交互式網絡圖已保存到: visualizations/interactive_network.html")
            else:
                print("❌ NetworkX不可用，跳過網絡圖生成")
        
        # 交互式詞頻分析
        if adv_viz.plotly_available:
            print("\n📊 生成交互式詞頻分析...")
            interactive_analysis = adv_viz.plot_interactive_word_cloud_data(word_freq)
            interactive_analysis.write_html("visualizations/interactive_word_analysis.html")
            print("✅ 交互式詞頻分析已保存到: visualizations/interactive_word_analysis.html")
        
        # 創建儀表板
        if adv_viz.plotly_available:
            print("\n📋 創建綜合儀表板...")
            figures = {
                "詞頻樹狀圖": adv_viz.plot_word_frequency_treemap(word_freq),
                "交互式詞頻分析": adv_viz.plot_interactive_word_cloud_data(word_freq)
            }
            
            if similarity_results:
                similarity_matrix = np.array(similarity_results['similarities']['semantic'])
                labels = similarity_results['labels']
                figures["相似度熱力圖"] = adv_viz.plot_interactive_similarity_heatmap(
                    similarity_matrix, labels
                )
                if adv_viz.networkx_available:
                    figures["文本網絡圖"] = adv_viz.plot_interactive_network(
                        similarity_matrix, labels
                    )
            
            dashboard_path = adv_viz.create_dashboard_html(
                figures, "visualizations/dashboard.html"
            )
            print(f"✅ 綜合儀表板已保存到: {dashboard_path}")
        
    except ImportError as e:
        print(f"❌ 高級視覺化功能不可用: {e}")
        print("💡 請安裝: pip install plotly networkx")

def demo_extended_file_support():
    """演示擴展文件格式支持"""
    print("\n" + "="*60)
    print("📁 擴展文件格式支持演示") 
    print("="*60)
    
    try:
        from src.utils.file_parsers import ExtendedFileParser
        
        parser = ExtendedFileParser()
        
        print("🚀 文件解析器初始化完成")
        print("📋 支持的文件格式:")
        for ext in parser.get_supported_extensions():
            print(f"  ✓ .{ext}")
        
        print("\n🔧 功能可用性:")
        for feature, available in parser.capabilities.items():
            status = "✅" if available else "❌"
            print(f"  {status} {feature}")
        
        # 創建示例文件進行測試
        test_dir = Path("test_files")
        test_dir.mkdir(exist_ok=True)
        
        # 創建示例文本文件
        sample_text = "這是一個測試文件。\n包含中文文本內容。\n用於演示文件解析功能。"
        
        test_files = []
        
        # TXT文件
        txt_file = test_dir / "sample.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(sample_text)
        test_files.append(str(txt_file))
        
        # Markdown文件
        md_file = test_dir / "sample.md"
        md_content = f"""# 測試文檔
        
## 概述
{sample_text}

**重點**: 這是markdown格式的文件。

- 列表項目1
- 列表項目2
"""
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        test_files.append(str(md_file))
        
        # JSON文件
        json_file = test_dir / "sample.json"
        json_content = {
            "title": "測試數據",
            "content": sample_text,
            "metadata": {
                "author": "系統",
                "date": "2024-01-01"
            }
        }
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_content, f, ensure_ascii=False, indent=2)
        test_files.append(str(json_file))
        
        print(f"\n📂 創建了 {len(test_files)} 個測試文件")
        
        # 批量解析文件
        print("\n🔄 批量解析文件...")
        results = parser.batch_parse_files(test_files)
        
        for file_path, result in results.items():
            file_name = Path(file_path).name
            if 'error' in result.get('metadata', {}):
                print(f"❌ {file_name}: {result['metadata']['error']}")
            else:
                content_preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                print(f"✅ {file_name}: {result['metadata']['file_type']} - {len(result['content'])} 字符")
                print(f"   預覽: {content_preview}")
        
        # 演示URL解析（如果網絡可用）
        print("\n🌐 測試網頁解析...")
        if parser.capabilities['web_scraping']:
            try:
                # 解析一個簡單的網頁
                url_result = parser.parse_url("https://httpbin.org/html")
                print(f"✅ 網頁解析成功: {len(url_result['content'])} 字符")
                print(f"   標題: {url_result['metadata'].get('title', 'N/A')}")
            except Exception as e:
                print(f"❌ 網頁解析失敗: {e}")
        
        return results
        
    except ImportError as e:
        print(f"❌ 擴展文件格式功能不可用: {e}")
        print("💡 請安裝: pip install PyPDF2 python-docx beautifulsoup4 pdfplumber")
        return None

def demo_task_queue():
    """演示任務隊列系統"""
    print("\n" + "="*60)
    print("⚙️ 任務隊列系統演示")
    print("="*60)
    
    try:
        from src.core.task_queue import TaskQueue, TaskType, TaskStatus
        
        print("🚀 初始化任務隊列...")
        task_queue = TaskQueue(enable_celery=False)  # 使用本地處理進行演示
        
        # 創建文本分析任務
        print("\n📝 創建文本分析任務...")
        analysis_params = {
            'text': '這是一個測試文本，用來演示任務隊列系統的文本分析功能。我們將分析這段文本的詞頻、情感和關鍵詞。',
            'options': {
                'include_sentiment': True,
                'include_keywords': True,
                'include_entities': True,
                'include_ngrams': True
            }
        }
        
        task_id = task_queue.create_task(
            TaskType.TEXT_ANALYSIS, 
            analysis_params,
            estimated_duration=30
        )
        print(f"✅ 任務已創建，ID: {task_id}")
        
        # 監控任務進度
        print("\n⏳ 監控任務進度...")
        for i in range(10):  # 最多等待10秒
            task = task_queue.get_task_status(task_id)
            if task:
                print(f"  狀態: {task.status.value} | 進度: {task.progress}%")
                
                if task.status == TaskStatus.SUCCESS:
                    print("✅ 任務完成！")
                    if task.result:
                        print(f"   詞頻統計: {len(task.result.get('word_frequency', {}))} 個詞")
                        print(f"   情感分析: {task.result.get('sentiment', {}).get('sentiment_label', 'N/A')}")
                        print(f"   關鍵詞: {len(task.result.get('keywords', []))} 個")
                    break
                elif task.status == TaskStatus.FAILURE:
                    print(f"❌ 任務失敗: {task.error_message}")
                    break
            
            time.sleep(1)
        
        # 創建相似度分析任務
        print("\n🔍 創建相似度分析任務...")
        similarity_params = {
            'texts': [
                '今天天氣很好，適合出去玩。',
                '今日天氣晴朗，很適合戶外活動。',
                '昨天下雨了，路上很濕。'
            ],
            'labels': ['文本A', '文本B', '文本C'],
            'method': 'tfidf'  # 使用TF-IDF以避免需要大型模型
        }
        
        similarity_task_id = task_queue.create_task(
            TaskType.SIMILARITY_ANALYSIS,
            similarity_params,
            estimated_duration=20
        )
        print(f"✅ 相似度分析任務已創建，ID: {similarity_task_id}")
        
        # 列出所有任務
        print("\n📋 當前任務列表:")
        tasks = task_queue.list_tasks(limit=10)
        for task in tasks:
            duration = ""
            if task.completed_at and task.started_at:
                duration = f" ({(task.completed_at - task.started_at).total_seconds():.1f}s)"
            print(f"  {task.id[:8]}... | {task.type.value} | {task.status.value}{duration}")
        
        # 等待相似度任務完成
        print(f"\n⏳ 等待相似度分析任務完成...")
        for i in range(10):
            task = task_queue.get_task_status(similarity_task_id)
            if task and task.status in [TaskStatus.SUCCESS, TaskStatus.FAILURE]:
                if task.status == TaskStatus.SUCCESS:
                    print("✅ 相似度分析完成！")
                    if task.result:
                        pairwise_count = len(task.result.get('pairwise_comparisons', []))
                        print(f"   生成了 {pairwise_count} 個兩兩比較結果")
                else:
                    print(f"❌ 相似度分析失敗: {task.error_message}")
                break
            time.sleep(1)
        
        return task_queue
        
    except ImportError as e:
        print(f"❌ 任務隊列功能不可用: {e}")
        print("💡 請安裝: pip install celery redis")
        return None

def demo_gpu_acceleration():
    """演示GPU加速功能"""
    print("\n" + "="*60)
    print("🚀 GPU加速功能演示")
    print("="*60)
    
    try:
        # 檢查GPU可用性
        try:
            import torch
            gpu_available = torch.cuda.is_available()
            device_count = torch.cuda.device_count()
            
            print(f"🔍 CUDA可用性: {'✅' if gpu_available else '❌'}")
            if gpu_available:
                print(f"📊 GPU設備數量: {device_count}")
                for i in range(device_count):
                    gpu_name = torch.cuda.get_device_name(i)
                    print(f"  GPU {i}: {gpu_name}")
            else:
                print("💡 未檢測到CUDA GPU，將使用CPU處理")
            
        except ImportError:
            print("❌ PyTorch未安裝，無法檢查GPU狀態")
            gpu_available = False
        
        # 演示相似度分析的GPU加速
        print("\n🔍 測試相似度分析GPU加速...")
        from src.core.similarity import TextSimilarityAnalyzer
        
        # 測試文本
        test_texts = [
            "人工智能是計算機科學的一個分支，致力於創建能夠執行通常需要人類智能的任務的系統。",
            "機器學習是人工智能的一個子領域，專注於開發能夠從數據中學習的算法。",
            "深度學習是機器學習的一個分支，使用多層神經網絡來處理複雜的數據模式。",
            "自然語言處理是人工智能的一個領域，專門處理人類語言的理解和生成。",
            "計算機視覺是人工智能的一個分支，專注於讓計算機能夠理解和分析視覺信息。"
        ]
        
        # CPU處理
        print("\n⚡ CPU處理測試...")
        start_time = time.time()
        cpu_analyzer = TextSimilarityAnalyzer(use_gpu=False)
        cpu_results = cpu_analyzer.comprehensive_similarity_analysis(test_texts)
        cpu_time = time.time() - start_time
        print(f"✅ CPU處理完成，耗時: {cpu_time:.2f}秒")
        
        # GPU處理（如果可用）
        if gpu_available:
            print("\n🚀 GPU處理測試...")
            start_time = time.time()
            gpu_analyzer = TextSimilarityAnalyzer(use_gpu=True)
            gpu_results = gpu_analyzer.comprehensive_similarity_analysis(test_texts)
            gpu_time = time.time() - start_time
            print(f"✅ GPU處理完成，耗時: {gpu_time:.2f}秒")
            
            if cpu_time > 0 and gpu_time > 0:
                speedup = cpu_time / gpu_time
                print(f"🏃‍♂️ GPU加速倍數: {speedup:.2f}x")
        else:
            print("⚠️ GPU不可用，跳過GPU測試")
            
        # 測試批量處理的性能差異
        print("\n📊 批量處理性能對比...")
        larger_texts = test_texts * 3  # 增加文本數量
        
        print(f"📝 測試文本數量: {len(larger_texts)}")
        
        # CPU批量處理
        start_time = time.time()
        cpu_analyzer.comprehensive_similarity_analysis(larger_texts)
        cpu_batch_time = time.time() - start_time
        print(f"⚡ CPU批量處理耗時: {cpu_batch_time:.2f}秒")
        
        if gpu_available:
            # GPU批量處理
            start_time = time.time()
            gpu_analyzer.comprehensive_similarity_analysis(larger_texts)
            gpu_batch_time = time.time() - start_time
            print(f"🚀 GPU批量處理耗時: {gpu_batch_time:.2f}秒")
            
            if cpu_batch_time > 0 and gpu_batch_time > 0:
                batch_speedup = cpu_batch_time / gpu_batch_time
                print(f"🏃‍♂️ 批量處理GPU加速倍數: {batch_speedup:.2f}x")
        
    except ImportError as e:
        print(f"❌ GPU加速功能不可用: {e}")
        print("💡 請安裝: pip install torch sentence-transformers")
    except Exception as e:
        print(f"❌ GPU測試過程中出錯: {e}")

def main():
    """主演示函數"""
    print("🌟 Chinese Text Analyzer - 新功能演示")
    print("🔧 展示文本相似度、高級視覺化、任務隊列、GPU加速、多格式支持")
    print("📅 " + "="*80)
    
    # 創建輸出目錄
    os.makedirs("visualizations", exist_ok=True)
    os.makedirs("test_files", exist_ok=True)
    
    # 依次演示各個功能
    similarity_results = demo_text_similarity()
    demo_advanced_visualization(similarity_results)
    demo_extended_file_support()
    demo_task_queue()
    demo_gpu_acceleration()
    
    print("\n" + "="*80)
    print("🎉 所有新功能演示完成！")
    print("📁 生成的文件:")
    print("   📊 visualizations/ - 視覺化文件")
    print("   📂 test_files/ - 測試文件")
    print("\n💡 使用提示:")
    print("   1. 在瀏覽器中打開 visualizations/dashboard.html 查看交互式儀表板")
    print("   2. 安裝完整依賴後可獲得更多功能")
    print("   3. 配置Redis和Celery可啟用分佈式任務處理")
    print("   4. 安裝CUDA和PyTorch可啟用GPU加速")

if __name__ == "__main__":
    main() 