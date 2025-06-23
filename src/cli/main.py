# -*- coding: utf-8 -*-
import os
import argparse
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.core.analyzer import ChineseTextAnalyzer
from src.utils.file_utils import FileUtils
from src.core.visualization import Visualizer

def analyze_single_file(file_path, analyzer, output_folder, export_formats, visualize=True, font_path=None, advanced_viz=None):
    """分析單個文件並保存結果"""
    try:
        # 讀取文件
        text = FileUtils.read_file(file_path)
        filename = os.path.basename(file_path)
        base_name = os.path.splitext(filename)[0]
        
        # 進行基本分析
        results = analyzer.analyze_text(text)
        
        # 添加高級分析
        # 情感分析
        results['sentiment'] = analyzer.analyze_sentiment(text)
        
        # 關鍵詞提取
        results['keywords'] = analyzer.keyword_extraction(text)
        
        # 命名實體識別
        results['entities'] = analyzer.extract_entities(text)
        
        # N-gram分析
        results['ngrams'] = analyzer.extract_ngrams(text)
        
        # 文本摘要
        results['summary'] = analyzer.generate_summary(text)
        
        # 導出結果
        output_path = os.path.join(output_folder, base_name)
        FileUtils.export_results(results, output_path, export_formats)
        print(f"已分析 {filename} 並保存結果")
        
        # 可視化
        if visualize:
            viz_folder = os.path.join(output_folder, 'visualizations')
            Visualizer.create_visualization_report(
                results, 
                output_dir=viz_folder, 
                prefix=base_name,
                font_path=font_path
            )
            
            # 進階詞頻可視化
            if advanced_viz and 'word_frequency' in results:
                # 創建高級詞頻視覺化目錄
                advanced_viz_folder = os.path.join(viz_folder, 'advanced')
                os.makedirs(advanced_viz_folder, exist_ok=True)
                
                # 詞頻統計餅圖
                if 'pie' in advanced_viz:
                    pie_path = os.path.join(advanced_viz_folder, f"{base_name}_word_freq_pie.png")
                    Visualizer.plot_advanced_word_frequency(
                        results['word_frequency'],
                        top_n=15,
                        title='詞頻分布餅圖',
                        save_path=pie_path,
                        plot_type='pie'
                    )
                    print(f"已生成詞頻餅圖: {pie_path}")
                
                # 詞頻垂直條形圖
                if 'vertical' in advanced_viz:
                    vert_path = os.path.join(advanced_viz_folder, f"{base_name}_word_freq_vertical.png")
                    Visualizer.plot_advanced_word_frequency(
                        results['word_frequency'],
                        title='詞頻垂直條形圖',
                        save_path=vert_path,
                        plot_type='vertical',
                        color_map='plasma'
                    )
                    print(f"已生成詞頻垂直條形圖: {vert_path}")
                
                # 按詞長度排序的詞頻圖
                if 'length' in advanced_viz:
                    len_path = os.path.join(advanced_viz_folder, f"{base_name}_word_by_length.png")
                    Visualizer.plot_advanced_word_frequency(
                        results['word_frequency'],
                        title='按詞長度排序的詞頻圖',
                        save_path=len_path,
                        sort_by='length',
                        color_map='magma'
                    )
                    print(f"已生成按詞長度排序的詞頻圖: {len_path}")
        
        return results
    except Exception as e:
        print(f"處理 {file_path} 時出錯: {str(e)}")
        return {"error": str(e)}

def main():
    # 解析命令行參數
    parser = argparse.ArgumentParser(description='中文文本分析工具')
    parser.add_argument('--input', '-i', required=True, help='輸入文件或目錄路徑')
    parser.add_argument('--output', '-o', default='results', help='輸出目錄路徑')
    parser.add_argument('--dict', '-d', help='自定義詞典路徑')
    parser.add_argument('--stopwords', '-s', help='停用詞表路徑')
    parser.add_argument('--formats', '-f', default='json', help='輸出格式，逗號分隔 (json,csv,excel)')
    parser.add_argument('--no-viz', action='store_true', help='不生成可視化圖表')
    parser.add_argument('--batch', '-b', action='store_true', help='批量處理模式')
    parser.add_argument('--parallel', '-p', action='store_true', help='使用並行處理（對於大量文件）')
    parser.add_argument('--extensions', '-e', default='.txt,.csv,.html,.md', help='要處理的文件擴展名（批量模式下），逗號分隔')
    parser.add_argument('--font', help='中文字體路徑 (用於詞雲圖生成)')
    parser.add_argument('--debug', action='store_true', help='啟用調試模式，顯示詳細錯誤信息')
    parser.add_argument('--advanced-viz', '-av', help='進階詞頻可視化選項，逗號分隔 (pie,vertical,length)')
    
    # 顯示幫助
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    
    # 初始化分析器
    analyzer = ChineseTextAnalyzer(
        custom_dict_path=args.dict,
        stopwords_path=args.stopwords
    )
    
    # 創建輸出目錄
    os.makedirs(args.output, exist_ok=True)
    
    # 解析輸出格式
    export_formats = args.formats.split(',')
    
    # 解析文件擴展名
    file_extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in args.extensions.split(',')]
    
    # 解析進階詞頻可視化選項
    advanced_viz = args.advanced_viz.split(',') if args.advanced_viz else None
    
    # 判斷輸入是文件還是目錄
    if os.path.isfile(args.input):
        # 處理單個文件
        results = analyze_single_file(args.input, analyzer, args.output, export_formats, not args.no_viz, args.font, advanced_viz)
        
        # 可視化（如果需要）
        if not args.no_viz and 'error' not in results:
            viz_folder = os.path.join(args.output, 'visualizations')
            # 使用用戶指定的字體（如果有）
            Visualizer.create_visualization_report(
                results, 
                output_dir=viz_folder, 
                prefix=os.path.basename(os.path.splitext(args.input)[0]),
                font_path=args.font
            )
    elif os.path.isdir(args.input) and args.batch:
        # 批量處理目錄中的文件
        file_list = FileUtils.get_file_list(args.input, extensions=file_extensions)
        
        if not file_list:
            print(f"在 {args.input} 中未找到可分析的文本文件")
            return
        
        print(f"找到 {len(file_list)} 個待分析的文件")
        
        # 根據參數選擇串行或並行處理
        if args.parallel:
            results = analyzer.analyze_files_parallel(file_list)
        else:
            results = analyzer.analyze_files(file_list)
        
        # 保存結果
        for file_path, result in results.items():
            filename = os.path.basename(file_path)
            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(args.output, base_name)
            
            # 添加高級分析結果（如果沒有錯誤）
            if 'error' not in result:
                try:
                    # 讀取文件
                    text = FileUtils.read_file(file_path)
                    
                    # 添加高級分析
                    result['sentiment'] = analyzer.analyze_sentiment(text)
                    result['keywords'] = analyzer.keyword_extraction(text)
                    result['entities'] = analyzer.extract_entities(text)
                    result['ngrams'] = analyzer.extract_ngrams(text)
                    result['summary'] = analyzer.generate_summary(text)
                except Exception as e:
                    print(f"為 {file_path} 添加高級分析時出錯: {str(e)}")
            
            # 導出結果
            FileUtils.export_results(result, output_path, export_formats)
            print(f"已保存分析結果到: {output_path}")
            
            # 生成可視化
            if not args.no_viz and 'error' not in result:
                viz_folder = os.path.join(args.output, 'visualizations')
                Visualizer.create_visualization_report(
                    result, 
                    output_dir=viz_folder, 
                    prefix=base_name,
                    font_path=args.font
                )
    else:
        print(f"錯誤: 輸入路徑 {args.input} 不存在或不是有效的文件/目錄，或者未指定批量處理模式")

if __name__ == "__main__":
    main()