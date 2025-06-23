# -*- coding: utf-8 -*-
import os
import sys
import time

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.core.analyzer import ChineseTextAnalyzer
from src.utils.file_utils import FileUtils
from src.core.visualization import Visualizer
from src.utils.convert_chinese import convert_text

class TextAnalyzerMenu:
    def __init__(self):
        self.analyzer = ChineseTextAnalyzer()
        self.output_dir = 'results'
        self.export_formats = ['json']
        self.visualize = True
        self.advanced_viz = []
        self.dpi = 300
        self.font_path = None
        
    def clear_screen(self):
        """清除屏幕"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def display_header(self):
        """顯示程序頭部信息"""
        self.clear_screen()
        print("=== 中文文本分析工具 ===")
        print("版本：1.0.0")
        print("=" * 25)
        print()
        
    def display_main_menu(self):
        """顯示主菜單"""
        self.display_header()
        print("主菜單:")
        print("1. 分析單個文件")
        print("2. 批量分析文件")
        print("3. 繁簡體轉換")
        print("4. 設置選項")
        print("5. 查看當前設置")
        print("0. 退出程序")
        print()
        
    def display_settings_menu(self):
        """顯示設置菜單"""
        self.display_header()
        print("設置選項:")
        print("1. 設置輸出目錄")
        print("2. 設置輸出格式")
        print("3. 設置視覺化選項")
        print("4. 設置圖像解析度 (DPI)")
        print("5. 設置中文字體")
        print("6. 設置自定義詞典")
        print("7. 設置停用詞表")
        print("0. 返回主菜單")
        print()
        
    def display_visualization_menu(self):
        """顯示視覺化設置菜單"""
        self.display_header()
        print("視覺化設置:")
        print("1. 啟用/禁用視覺化 (當前: {})".format("啟用" if self.visualize else "禁用"))
        print("2. 設置進階詞頻視覺化選項")
        print("0. 返回設置菜單")
        print()
        
    def display_advanced_viz_menu(self):
        """顯示進階視覺化選項菜單"""
        current_options = "無" if not self.advanced_viz else ", ".join(self.advanced_viz)
        self.display_header()
        print("進階詞頻視覺化選項:")
        print("當前選項: {}".format(current_options))
        print("1. 詞頻分布餅圖 (pie)")
        print("2. 詞頻垂直條形圖 (vertical)")
        print("3. 按詞長度排序的詞頻圖 (length)")
        print("4. 全部選擇")
        print("5. 清除選擇")
        print("0. 返回視覺化菜單")
        print()
        
    def handle_main_menu(self):
        """處理主菜單選項"""
        while True:
            self.display_main_menu()
            choice = input("請選擇操作 [0-5]: ").strip()
            
            if choice == '0':
                print("感謝使用中文文本分析工具！")
                sys.exit(0)
            elif choice == '1':
                self.analyze_single_file()
            elif choice == '2':
                self.analyze_batch_files()
            elif choice == '3':
                self.convert_chinese_text()
            elif choice == '4':
                self.handle_settings_menu()
            elif choice == '5':
                self.display_current_settings()
            else:
                input("無效選項，請重新選擇。按Enter繼續...")
                
    def handle_settings_menu(self):
        """處理設置菜單選項"""
        while True:
            self.display_settings_menu()
            choice = input("請選擇設置選項 [0-7]: ").strip()
            
            if choice == '0':
                return
            elif choice == '1':
                self.set_output_directory()
            elif choice == '2':
                self.set_export_formats()
            elif choice == '3':
                self.handle_visualization_menu()
            elif choice == '4':
                self.set_dpi()
            elif choice == '5':
                self.set_font_path()
            elif choice == '6':
                self.set_custom_dict()
            elif choice == '7':
                self.set_stopwords()
            else:
                input("無效選項，請重新選擇。按Enter繼續...")
                
    def handle_visualization_menu(self):
        """處理視覺化菜單選項"""
        while True:
            self.display_visualization_menu()
            choice = input("請選擇視覺化設置 [0-2]: ").strip()
            
            if choice == '0':
                return
            elif choice == '1':
                self.toggle_visualization()
            elif choice == '2':
                self.handle_advanced_viz_menu()
            else:
                input("無效選項，請重新選擇。按Enter繼續...")
                
    def handle_advanced_viz_menu(self):
        """處理進階視覺化菜單選項"""
        while True:
            self.display_advanced_viz_menu()
            choice = input("請選擇進階視覺化選項 [0-5]: ").strip()
            
            if choice == '0':
                return
            elif choice == '1':
                self.toggle_advanced_viz_option('pie')
            elif choice == '2':
                self.toggle_advanced_viz_option('vertical')
            elif choice == '3':
                self.toggle_advanced_viz_option('length')
            elif choice == '4':
                self.advanced_viz = ['pie', 'vertical', 'length']
                print("已選擇全部進階視覺化選項")
                input("按Enter繼續...")
            elif choice == '5':
                self.advanced_viz = []
                print("已清除所有進階視覺化選項")
                input("按Enter繼續...")
            else:
                input("無效選項，請重新選擇。按Enter繼續...")
                
    def toggle_advanced_viz_option(self, option):
        """切換進階視覺化選項"""
        if option in self.advanced_viz:
            self.advanced_viz.remove(option)
            print(f"已禁用 {option} 視覺化")
        else:
            self.advanced_viz.append(option)
            print(f"已啟用 {option} 視覺化")
        input("按Enter繼續...")
        
    def toggle_visualization(self):
        """切換是否生成視覺化圖表"""
        self.visualize = not self.visualize
        message = "已啟用視覺化圖表生成" if self.visualize else "已禁用視覺化圖表生成"
        print(message)
        input("按Enter繼續...")
        
    def set_output_directory(self):
        """設置輸出目錄"""
        self.display_header()
        print("當前輸出目錄: {}".format(self.output_dir))
        new_dir = input("請輸入新的輸出目錄 (留空使用當前設置): ").strip()
        
        if new_dir:
            self.output_dir = new_dir
            print(f"輸出目錄已設置為: {self.output_dir}")
        input("按Enter繼續...")
        
    def set_export_formats(self):
        """設置輸出格式"""
        self.display_header()
        print("可用格式: json, csv, excel")
        print("當前格式: {}".format(", ".join(self.export_formats)))
        
        formats = input("請輸入輸出格式（用逗號分隔，例如 json,csv）: ").strip()
        if formats:
            self.export_formats = [f.strip() for f in formats.split(',')]
            print(f"輸出格式已設置為: {', '.join(self.export_formats)}")
        input("按Enter繼續...")
        
    def set_dpi(self):
        """設置圖像解析度"""
        self.display_header()
        print("圖像解析度 (DPI) 影響視覺化圖表的質量和生成時間")
        print("推薦值: 72 (快速預覽), 150 (一般用途), 300 (高質量)")
        print(f"當前設置: {self.dpi}")
        
        try:
            new_dpi = input("請輸入新的DPI值 (留空使用當前設置): ").strip()
            if new_dpi:
                self.dpi = int(new_dpi)
                print(f"圖像解析度已設置為: {self.dpi} DPI")
        except ValueError:
            print("錯誤：請輸入有效的數字")
        
        input("按Enter繼續...")
        
    def set_font_path(self):
        """設置中文字體路徑"""
        self.display_header()
        print("中文字體路徑用於生成包含中文的視覺化圖表")
        print(f"當前設置: {self.font_path or '默認系統字體'}")
        
        macOS_fonts = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/Songti.ttc"
        ]
        
        if sys.platform == 'darwin':  # macOS
            print("\n以下是常見的macOS中文字體路徑:")
            for i, font in enumerate(macOS_fonts, 1):
                exists = "✓" if os.path.exists(font) else "✗"
                print(f"{i}. {font} {exists}")
            
            print("\n輸入數字選擇上述字體，或輸入完整的字體路徑:")
            font_choice = input("選擇 (留空使用當前設置): ").strip()
            
            if font_choice.isdigit() and 1 <= int(font_choice) <= len(macOS_fonts):
                self.font_path = macOS_fonts[int(font_choice) - 1]
                print(f"字體路徑已設置為: {self.font_path}")
            elif font_choice:
                self.font_path = font_choice
                print(f"字體路徑已設置為: {self.font_path}")
        else:
            new_font = input("請輸入中文字體路徑 (留空使用當前設置): ").strip()
            if new_font:
                self.font_path = new_font
                print(f"字體路徑已設置為: {self.font_path}")
        
        input("按Enter繼續...")
        
    def set_custom_dict(self):
        """設置自定義詞典"""
        self.display_header()
        print("自定義詞典可以提高分詞精確度")
        current_dict = "資源目錄下的 custom_dict.txt"
        print(f"當前設置: {current_dict}")
        
        default_dict = os.path.join("resources", "custom_dict.txt")
        if os.path.exists(default_dict):
            print(f"發現默認詞典: {default_dict}")
            
        new_dict = input("請輸入自定義詞典路徑 (留空使用當前設置): ").strip()
        if new_dict:
            if os.path.exists(new_dict):
                self.analyzer.load_user_dict(new_dict)
                print(f"已加載自定義詞典: {new_dict}")
            else:
                print(f"錯誤: 找不到詞典文件 {new_dict}")
                
        input("按Enter繼續...")
        
    def set_stopwords(self):
        """設置停用詞表"""
        self.display_header()
        print("停用詞表用於過濾常見但無意義的詞語")
        current_stopwords = self.analyzer.stopwords_path or "未設置"
        print(f"當前設置: {current_stopwords}")
        
        default_stopwords = os.path.join("resources", "chinese_stopwords.txt")
        if os.path.exists(default_stopwords):
            print(f"發現默認停用詞表: {default_stopwords}")
            
        new_stopwords = input("請輸入停用詞表路徑 (留空使用當前設置): ").strip()
        if new_stopwords:
            if os.path.exists(new_stopwords):
                self.analyzer.load_stopwords(new_stopwords)
                print(f"已加載停用詞表: {new_stopwords}")
            else:
                print(f"錯誤: 找不到停用詞表文件 {new_stopwords}")
                
        input("按Enter繼續...")
        
    def display_current_settings(self):
        """顯示當前所有設置"""
        self.display_header()
        print("當前設置:")
        print("-" * 25)
        print(f"輸出目錄: {self.output_dir}")
        print(f"輸出格式: {', '.join(self.export_formats)}")
        print(f"視覺化圖表: {'啟用' if self.visualize else '禁用'}")
        
        adv_viz = "無" if not self.advanced_viz else ", ".join(self.advanced_viz)
        print(f"進階詞頻視覺化: {adv_viz}")
        print(f"圖像解析度: {self.dpi} DPI")
        print(f"中文字體: {self.font_path or '默認系統字體'}")
        
        # 使用預設路徑顯示，而不是嘗試訪問不存在的屬性
        default_dict = os.path.join("resources", "custom_dict.txt")
        if os.path.exists(default_dict):
            print(f"自定義詞典: {default_dict}")
        else:
            print(f"自定義詞典: 未設置")
            
        default_stopwords = os.path.join("resources", "chinese_stopwords.txt")
        if os.path.exists(default_stopwords):
            print(f"停用詞表: {default_stopwords}")
        else:
            print(f"停用詞表: 未設置")
            
        print("-" * 25)
        
        input("按Enter返回主菜單...")
        
    def analyze_single_file(self):
        """分析單個文件"""
        self.display_header()
        print("分析單個文件")
        print("-" * 25)
        
        # 提示用戶輸入文件路徑
        file_path = input("請輸入要分析的文件路徑: ").strip()
        
        if not file_path:
            print("錯誤: 未提供文件路徑")
            input("按Enter返回主菜單...")
            return
            
        if not os.path.isfile(file_path):
            print(f"錯誤: 找不到文件 {file_path}")
            input("按Enter返回主菜單...")
            return
            
        # 創建輸出目錄
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"\n開始分析文件: {file_path}")
        print("-" * 50)
        
        # 讀取文件
        text = FileUtils.read_file(file_path)
        filename = os.path.basename(file_path)
        base_name = os.path.splitext(filename)[0]
        
        # 計算文本基本信息
        total_chars = len(text)
        chinese_chars = self.analyzer.count_chinese_characters(text)
        
        print(f"文件大小: {total_chars} 字符")
        print(f"中文字符數: {chinese_chars} 個")
        print(f"中文字符比例: {chinese_chars/total_chars*100:.2f}%")
        print("正在進行分詞和基礎分析...")
        
        # 進行基本分析
        try:
            results = self.analyzer.analyze_text(text)
            
            # 添加文本字符統計信息
            results['total_characters'] = total_chars
            results['chinese_characters'] = chinese_chars
            results['chinese_character_ratio'] = round(chinese_chars/total_chars*100, 2)
            
            # 添加高級分析
            print("正在進行情感分析...")
            results['sentiment'] = self.analyzer.analyze_sentiment(text)
            
            print("正在提取關鍵詞...")
            results['keywords'] = self.analyzer.keyword_extraction(text)
            
            print("正在識別命名實體...")
            results['entities'] = self.analyzer.extract_entities(text)
            
            print("正在分析詞組 (N-grams)...")
            results['ngrams'] = self.analyzer.extract_ngrams(text)
            
            print("正在生成文本摘要...")
            results['summary'] = self.analyzer.generate_summary(text)
            
            # 導出結果
            output_path = os.path.join(self.output_dir, base_name)
            print(f"正在保存分析結果...")
            FileUtils.export_results(results, output_path, self.export_formats)
            
            print(f"\n已將分析結果保存至: {output_path}")
            
            # 可視化
            if self.visualize:
                print("\n正在生成視覺化圖表...")
                viz_folder = os.path.join(self.output_dir, 'visualizations')
                viz_path = Visualizer.create_visualization_report(
                    results, 
                    output_dir=viz_folder, 
                    prefix=base_name,
                    font_path=self.font_path,
                    dpi=self.dpi
                )
                print(f"已將視覺化圖表保存至: {viz_folder}")
                
                # 進階詞頻可視化
                if self.advanced_viz and 'word_frequency' in results:
                    print("正在生成進階詞頻視覺化...")
                    
                    # 創建高級詞頻視覺化目錄
                    advanced_viz_folder = os.path.join(viz_folder, 'advanced')
                    os.makedirs(advanced_viz_folder, exist_ok=True)
                    
                    # 詞頻統計餅圖
                    if 'pie' in self.advanced_viz:
                        pie_path = os.path.join(advanced_viz_folder, f"{base_name}_word_freq_pie.png")
                        Visualizer.plot_advanced_word_frequency(
                            results['word_frequency'],
                            top_n=15,
                            title='詞頻分布餅圖',
                            save_path=pie_path,
                            plot_type='pie',
                            dpi=self.dpi
                        )
                        print(f"已生成詞頻餅圖: {pie_path}")
                    
                    # 詞頻垂直條形圖
                    if 'vertical' in self.advanced_viz:
                        vert_path = os.path.join(advanced_viz_folder, f"{base_name}_word_freq_vertical.png")
                        Visualizer.plot_advanced_word_frequency(
                            results['word_frequency'],
                            title='詞頻垂直條形圖',
                            save_path=vert_path,
                            plot_type='vertical',
                            color_map='plasma',
                            dpi=self.dpi
                        )
                        print(f"已生成詞頻垂直條形圖: {vert_path}")
                    
                    # 按詞長度排序的詞頻圖
                    if 'length' in self.advanced_viz:
                        len_path = os.path.join(advanced_viz_folder, f"{base_name}_word_by_length.png")
                        Visualizer.plot_advanced_word_frequency(
                            results['word_frequency'],
                            title='按詞長度排序的詞頻圖',
                            save_path=len_path,
                            sort_by='length',
                            color_map='magma',
                            dpi=self.dpi
                        )
                        print(f"已生成按詞長度排序的詞頻圖: {len_path}")
                
            print("\n分析完成！")
            
        except Exception as e:
            print(f"分析過程中發生錯誤: {str(e)}")
            
        input("\n按Enter返回主菜單...")
        
    def analyze_batch_files(self):
        """批量分析文件"""
        self.display_header()
        print("批量分析文件")
        print("-" * 25)
        
        # 提示用戶輸入目錄路徑
        dir_path = input("請輸入包含待分析文件的目錄路徑: ").strip()
        
        if not dir_path:
            print("錯誤: 未提供目錄路徑")
            input("按Enter返回主菜單...")
            return
            
        if not os.path.isdir(dir_path):
            print(f"錯誤: 找不到目錄 {dir_path}")
            input("按Enter返回主菜單...")
            return
            
        # 詢問文件擴展名
        extensions = input("請輸入要處理的文件擴展名（逗號分隔，例如 .txt,.md，留空默認為.txt）: ").strip()
        if not extensions:
            extensions = ".txt"
        
        file_extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions.split(',')]
        
        # 獲取文件列表
        file_list = FileUtils.get_file_list(dir_path, extensions=file_extensions)
        
        if not file_list:
            print(f"在 {dir_path} 中未找到可分析的文本文件")
            input("按Enter返回主菜單...")
            return
            
        print(f"\n找到 {len(file_list)} 個待分析的文件:")
        for i, file_path in enumerate(file_list[:10], 1):
            print(f"{i}. {os.path.basename(file_path)}")
        
        if len(file_list) > 10:
            print(f"... 以及 {len(file_list) - 10} 個其他文件")
            
        # 詢問是否使用並行處理
        use_parallel = input("\n是否使用並行處理以加快大量文件的處理速度？(y/n，默認: n): ").strip().lower()
        use_parallel = use_parallel == 'y'
        
        print("\n" + "-" * 50)
        print(f"開始批量分析 {len(file_list)} 個文件...")
        
        # 創建輸出目錄
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 根據參數選擇串行或並行處理
        start_time = time.time()
        if use_parallel:
            print("使用並行處理模式...")
            results = self.analyzer.analyze_files_parallel(file_list)
        else:
            print("使用串行處理模式...")
            results = self.analyzer.analyze_files(file_list)
        
        # 保存結果
        for file_path, result in results.items():
            filename = os.path.basename(file_path)
            base_name = os.path.splitext(filename)[0]
            output_path = os.path.join(self.output_dir, base_name)
            
            # 添加高級分析結果（如果沒有錯誤）
            if 'error' not in result:
                try:
                    # 讀取文件
                    text = FileUtils.read_file(file_path)
                    
                    # 計算文本字符統計信息
                    total_chars = len(text)
                    chinese_chars = self.analyzer.count_chinese_characters(text)
                    result['total_characters'] = total_chars
                    result['chinese_characters'] = chinese_chars
                    result['chinese_character_ratio'] = round(chinese_chars/total_chars*100, 2)
                    
                    print(f"{filename}: 總字符 {total_chars}, 中文字符 {chinese_chars} ({result['chinese_character_ratio']}%)")
                    
                    # 添加高級分析
                    result['sentiment'] = self.analyzer.analyze_sentiment(text)
                    result['keywords'] = self.analyzer.keyword_extraction(text)
                    result['entities'] = self.analyzer.extract_entities(text)
                    result['ngrams'] = self.analyzer.extract_ngrams(text)
                    result['summary'] = self.analyzer.generate_summary(text)
                except Exception as e:
                    print(f"為 {filename} 添加高級分析時出錯: {str(e)}")
            
            # 導出結果
            FileUtils.export_results(result, output_path, self.export_formats)
            print(f"已保存 {filename} 分析結果")
            
            # 生成可視化
            if self.visualize and 'error' not in result:
                viz_folder = os.path.join(self.output_dir, 'visualizations')
                Visualizer.create_visualization_report(
                    result, 
                    output_dir=viz_folder, 
                    prefix=base_name,
                    font_path=self.font_path,
                    dpi=self.dpi
                )
                
                # 進階詞頻可視化
                if self.advanced_viz and 'word_frequency' in result:
                    # 創建高級詞頻視覺化目錄
                    advanced_viz_folder = os.path.join(viz_folder, 'advanced')
                    os.makedirs(advanced_viz_folder, exist_ok=True)
                    
                    # 詞頻統計餅圖
                    if 'pie' in self.advanced_viz:
                        pie_path = os.path.join(advanced_viz_folder, f"{base_name}_word_freq_pie.png")
                        Visualizer.plot_advanced_word_frequency(
                            result['word_frequency'],
                            top_n=15,
                            title='詞頻分布餅圖',
                            save_path=pie_path,
                            plot_type='pie',
                            dpi=self.dpi
                        )
                    
                    # 詞頻垂直條形圖
                    if 'vertical' in self.advanced_viz:
                        vert_path = os.path.join(advanced_viz_folder, f"{base_name}_word_freq_vertical.png")
                        Visualizer.plot_advanced_word_frequency(
                            result['word_frequency'],
                            title='詞頻垂直條形圖',
                            save_path=vert_path,
                            plot_type='vertical',
                            color_map='plasma',
                            dpi=self.dpi
                        )
                    
                    # 按詞長度排序的詞頻圖
                    if 'length' in self.advanced_viz:
                        len_path = os.path.join(advanced_viz_folder, f"{base_name}_word_by_length.png")
                        Visualizer.plot_advanced_word_frequency(
                            result['word_frequency'],
                            title='按詞長度排序的詞頻圖',
                            save_path=len_path,
                            sort_by='length',
                            color_map='magma',
                            dpi=self.dpi
                        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "-" * 50)
        print(f"批量分析完成！共處理了 {len(file_list)} 個文件")
        print(f"總耗時: {duration:.2f} 秒")
        print(f"平均每個文件: {duration/len(file_list):.2f} 秒")
        print(f"結果已保存到: {self.output_dir}")
        
        input("\n按Enter返回主菜單...")
        
    def convert_chinese_text(self):
        """處理繁簡體轉換"""
        self.display_header()
        print("繁簡體中文轉換")
        print("-" * 25)
        
        # 詢問轉換方向
        print("轉換方向:")
        print("1. 簡體 -> 繁體")
        print("2. 繁體 -> 簡體")
        
        direction = input("請選擇轉換方向 [1-2]: ").strip()
        
        if direction not in ['1', '2']:
            print("無效選項")
            input("按Enter返回主菜單...")
            return
            
        # 詢問轉換對象
        print("\n轉換對象:")
        print("1. 轉換文本")
        print("2. 轉換文件")
        
        target = input("請選擇轉換對象 [1-2]: ").strip()
        
        if target not in ['1', '2']:
            print("無效選項")
            input("按Enter返回主菜單...")
            return
        
        # 設置轉換設置
        conversion = 's2t' if direction == '1' else 't2s'
        
        if target == '1':
            # 文本轉換
            print("\n請輸入要轉換的文本 (輸入完成後按Enter兩次):")
            lines = []
            while True:
                line = input()
                if not line.strip():
                    break
                lines.append(line)
                
            if not lines:
                print("未輸入文本")
                input("按Enter返回主菜單...")
                return
                
            text = "\n".join(lines)
            result = convert_text(text, conversion)
            
            print("\n轉換結果:")
            print("-" * 50)
            print(result)
            print("-" * 50)
        else:
            # 文件轉換
            file_path = input("\n請輸入要轉換的文件路徑: ").strip()
            
            if not file_path:
                print("錯誤: 未提供文件路徑")
                input("按Enter返回主菜單...")
                return
                
            if not os.path.isfile(file_path):
                print(f"錯誤: 找不到文件 {file_path}")
                input("按Enter返回主菜單...")
                return
                
            output_path = input("請輸入輸出文件路徑 (留空使用原檔名加後綴): ").strip()
            
            if not output_path:
                file_dir = os.path.dirname(file_path)
                file_name, file_ext = os.path.splitext(os.path.basename(file_path))
                suffix = "_tc" if direction == '1' else "_sc"
                output_path = os.path.join(file_dir, f"{file_name}{suffix}{file_ext}")
                
            try:
                # 讀取文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 轉換
                result = convert_text(content, conversion)
                
                # 寫入輸出文件
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result)
                    
                print(f"\n轉換完成，已保存到: {output_path}")
            except Exception as e:
                print(f"轉換過程中發生錯誤: {str(e)}")
        
        input("\n按Enter返回主菜單...")
        
    def run(self):
        """運行菜單系統"""
        self.handle_main_menu()

if __name__ == "__main__":
    menu = TextAnalyzerMenu()
    menu.run()