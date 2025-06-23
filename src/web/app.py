from flask import Flask, request, jsonify, render_template, send_file
import os
import uuid
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_cors import CORS  # Add CORS support
from src.core.analyzer import ChineseTextAnalyzer
from src.core.visualization import Visualizer
from src.core.similarity import TextSimilarityAnalyzer
from src.core.advanced_visualization import AdvancedVisualizer
from src.core.task_queue import TaskQueue
from src.utils.file_parsers import ExtendedFileParser
from src.utils.convert_chinese import convert_text

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize advanced components
try:
    similarity_analyzer = TextSimilarityAnalyzer()
    advanced_visualizer = AdvancedVisualizer()
    task_queue = TaskQueue()
    file_parser = ExtendedFileParser()
    GPU_AVAILABLE = True
    try:
        import torch
        GPU_AVAILABLE = torch.cuda.is_available()
    except:
        GPU_AVAILABLE = False
except Exception as e:
    print(f"Warning: Some advanced features may not be available: {e}")
    similarity_analyzer = None
    advanced_visualizer = None
    task_queue = None
    file_parser = None
    GPU_AVAILABLE = False

# Create directories for storing temporary results
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_FOLDER = os.path.join(project_root, 'data', 'output', 'uploads')
RESULTS_FOLDER = os.path.join('src', 'web', 'static', 'results')
INPUT_FOLDER = os.path.join(project_root, 'data', 'input')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Initialize analyzer
analyzer = ChineseTextAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/input_texts/<path:filename>', methods=['GET'])
def serve_sample_text(filename):
    """Serve sample text files from the input_texts directory"""
    try:
        return send_file(os.path.join(INPUT_FOLDER, filename))
    except Exception as e:
        print(f"Error serving sample text: {str(e)}")
        return jsonify({'error': str(e)}), 404

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    if request.method == 'POST':
        try:
            data = request.json
            if not data:
                # Try form data if JSON parsing fails
                text = request.form.get('text', '')
            else:
                text = data.get('text', '')
            
            if not text:
                return jsonify({'error': '未提供文本'}), 400
                
            # Generate a unique ID for this analysis
            analysis_id = str(uuid.uuid4())
            result_dir = os.path.join(RESULTS_FOLDER, analysis_id)
            os.makedirs(result_dir, exist_ok=True)
            
            # Perform analysis
            analyzer_results = analyzer.analyze_text(text)
            
            # Store the original text for report generation
            analyzer_results['original_text'] = text
            
            # Add sentiment analysis
            sentiment_results = analyzer.analyze_sentiment(text)
            analyzer_results['sentiment'] = sentiment_results
            
            # Add entity extraction
            entity_results = analyzer.extract_entities(text)
            analyzer_results['entities'] = entity_results
            
            # Add keyword extraction
            keywords = analyzer.keyword_extraction(text, top_k=20)
            analyzer_results['keywords'] = keywords
            
            # Add n-gram analysis
            ngrams = analyzer.extract_ngrams(text, n=2)  # Bigrams
            analyzer_results['ngrams'] = dict(ngrams.most_common(20))
            
            # IMPORTANT: Fix the key name mismatch
            # The analyzer returns 'pos_frequency' but the web app expects 'pos_distribution'
            if 'pos_frequency' in analyzer_results:
                analyzer_results['pos_distribution'] = analyzer_results['pos_frequency']
            
            # Generate visualizations
            viz_paths = {}
            
            # Generate wordcloud (basic)
            wc_path = os.path.join(result_dir, 'wordcloud.png')
            Visualizer.generate_wordcloud(
                analyzer_results['word_frequency'], 
                title='詞頻雲圖',
                save_path=wc_path
            )
            viz_paths['wordcloud'] = f"/static/results/{analysis_id}/wordcloud.png"
            
            # Generate word frequency chart (basic)
            wf_path = os.path.join(result_dir, 'word_freq.png')
            Visualizer.plot_word_frequency(
                analyzer_results['word_frequency'],
                top_n=15,
                title='詞頻分布',
                save_path=wf_path
            )
            viz_paths['word_frequency'] = f"/static/results/{analysis_id}/word_freq.png"
            
            # Generate POS distribution chart (basic)
            pos_path = os.path.join(result_dir, 'pos_distribution.png')
            Visualizer.plot_pos_distribution(
                analyzer_results['pos_distribution'],
                title='詞性分布',
                save_path=pos_path
            )
            viz_paths['pos_distribution'] = f"/static/results/{analysis_id}/pos_distribution.png"
            
            # Generate sentiment chart (basic)
            if 'sentiment' in analyzer_results:
                sent_path = os.path.join(result_dir, 'sentiment.png')
                Visualizer.plot_sentiment_analysis(
                    analyzer_results['sentiment'],
                    title='情感分析',
                    save_path=sent_path
                )
                viz_paths['sentiment'] = f"/static/results/{analysis_id}/sentiment.png"
            
            # Generate entity chart (basic)
            if 'entities' in analyzer_results and any(analyzer_results['entities'].values()):
                entity_path = os.path.join(result_dir, 'entities.png')
                Visualizer.plot_entities(
                    analyzer_results['entities'],
                    title='命名實體統計',
                    save_path=entity_path
                )
                viz_paths['entities'] = f"/static/results/{analysis_id}/entities.png"
            
            # Generate n-gram chart (advanced)
            if 'ngrams' in analyzer_results and analyzer_results['ngrams']:
                ngrams_path = os.path.join(result_dir, 'ngrams.png')
                Visualizer.plot_ngrams(
                    analyzer_results['ngrams'],
                    title='常見詞組 (Bigrams)',
                    save_path=ngrams_path
                )
                viz_paths['ngrams'] = f"/static/results/{analysis_id}/ngrams.png"
            
            # Generate keyword weights chart (advanced)
            if 'keywords' in analyzer_results and analyzer_results['keywords']:
                keywords_path = os.path.join(result_dir, 'keywords.png')
                Visualizer.plot_keyword_weights(
                    analyzer_results['keywords'],
                    title='關鍵詞權重',
                    save_path=keywords_path
                )
                viz_paths['keywords'] = f"/static/results/{analysis_id}/keywords.png"
            
            # Generate advanced word frequency visualizations (advanced)
            # 1. Vertical bar chart
            adv_vertical_path = os.path.join(result_dir, 'word_freq_vertical.png')
            Visualizer.plot_advanced_word_frequency(
                analyzer_results['word_frequency'],
                top_n=15,
                title='詞頻統計 (垂直條形圖)',
                save_path=adv_vertical_path,
                plot_type='vertical'
            )
            viz_paths['word_frequency_vertical'] = f"/static/results/{analysis_id}/word_freq_vertical.png"
            
            # 2. Pie chart
            adv_pie_path = os.path.join(result_dir, 'word_freq_pie.png')
            Visualizer.plot_advanced_word_frequency(
                analyzer_results['word_frequency'],
                top_n=10,  # Fewer for pie chart
                title='詞頻統計 (餅圖)',
                save_path=adv_pie_path,
                plot_type='pie'
            )
            viz_paths['word_frequency_pie'] = f"/static/results/{analysis_id}/word_freq_pie.png"
            
            # 3. Words sorted by length
            adv_length_path = os.path.join(result_dir, 'word_by_length.png')
            Visualizer.plot_advanced_word_frequency(
                analyzer_results['word_frequency'],
                top_n=15,
                title='詞頻統計 (按詞長排序)',
                save_path=adv_length_path,
                sort_by='length'
            )
            viz_paths['word_by_length'] = f"/static/results/{analysis_id}/word_by_length.png"
            
            # Add visualization paths to results
            analyzer_results['visualizations'] = viz_paths
            
            # Save all results to a JSON file for future reference
            with open(os.path.join(result_dir, 'results.json'), 'w', encoding='utf-8') as f:
                json.dump(analyzer_results, f, ensure_ascii=False, indent=2)
            
            viz_paths['results_json'] = f"/static/results/{analysis_id}/results.json"
            
            return jsonify(analyzer_results)
        except Exception as e:
            print(f"Error in analyze_text: {str(e)}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/convert', methods=['POST'])
def convert_chinese_text():
    try:
        data = request.json
        if not data:
            # Try form data if JSON parsing fails
            text = request.form.get('text', '')
            direction = request.form.get('direction', 'to_traditional')
        else:
            text = data.get('text', '')
            direction = data.get('direction', 'to_traditional')  # 'to_traditional' or 'to_simplified'
        
        if not text:
            return jsonify({'error': '未提供文本'}), 400
        
        conversion = 's2t' if direction == 'to_traditional' else 't2s'
        result = convert_text(text, conversion)
        
        return jsonify({'converted_text': result})
    except Exception as e:
        print(f"Error in convert_chinese_text: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/save_file', methods=['POST'])
def save_file():
    try:
        data = request.json
        if not data:
            # Try form data if JSON parsing fails
            text = request.form.get('text', '')
            filename = request.form.get('filename', f"converted_{uuid.uuid4()}.txt")
        else:
            text = data.get('text', '')
            filename = data.get('filename', f"converted_{uuid.uuid4()}.txt")
        
        if not text:
            return jsonify({'error': '未提供文本'}), 400
        
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return jsonify({'success': True, 'file_path': file_path})
    except Exception as e:
        print(f"Error in save_file: {str(e)}")
        return jsonify({'error': f'儲存檔案時發生錯誤: {str(e)}'}), 500

@app.route('/uploads/<path:filename>', methods=['GET'])
def download_file(filename):
    """Route to allow downloading files from the uploads directory"""
    try:
        return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)
    except Exception as e:
        print(f"Error in download_file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download_all_visualizations', methods=['POST'])
def download_all_visualizations():
    """Download all visualizations for an analysis as a zip file"""
    try:
        analysis_id = request.form.get('analysis_id')
        if not analysis_id:
            return jsonify({'error': 'No analysis ID provided'}), 400
        
        result_dir = os.path.join(RESULTS_FOLDER, analysis_id)
        if not os.path.exists(result_dir):
            return jsonify({'error': 'Analysis results not found'}), 404
        
        # Create a zip file with all visualizations
        import zipfile
        from io import BytesIO
        
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            # Add all png and html files from the results directory
            for filename in os.listdir(result_dir):
                if filename.endswith(('.png', '.html')):
                    file_path = os.path.join(result_dir, filename)
                    zf.write(file_path, filename)
        
        memory_file.seek(0)
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            attachment_filename=f'chinese_text_analysis_{analysis_id}.zip'
        )
    except Exception as e:
        print(f"Error in download_all_visualizations: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    """Generate a comprehensive HTML report with all visualizations and data"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        text = data.get('text', '')
        options = data.get('options', {})
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Generate a unique ID for this report
        report_id = str(uuid.uuid4())
        report_dir = os.path.join(RESULTS_FOLDER, report_id)
        os.makedirs(report_dir, exist_ok=True)
        
        # Perform complete analysis
        analyzer_results = analyzer.analyze_text(text)
        
        # Store the original text for report generation
        analyzer_results['original_text'] = text
        
        # Add sentiment analysis
        sentiment_results = analyzer.analyze_sentiment(text)
        analyzer_results['sentiment'] = sentiment_results
        
        # Add entity extraction
        entity_results = analyzer.extract_entities(text)
        analyzer_results['entities'] = entity_results
        
        # Add n-grams analysis
        ngrams_results = analyzer.extract_ngrams(text, n=2)  # Extract bigrams
        analyzer_results['ngrams'] = dict(ngrams_results.most_common(20))  # Top 20 bigrams
        
        # Add keyword extraction
        keyword_results = analyzer.keyword_extraction(text, top_k=20)
        analyzer_results['keywords'] = keyword_results
        
        # Generate text summary
        analyzer_results['summary'] = analyzer.generate_summary(text, sentence_count=3)
        
        # Fix key name mismatch
        if 'pos_frequency' in analyzer_results:
            analyzer_results['pos_distribution'] = analyzer_results['pos_frequency']
        
        # Generate all visualizations
        viz_paths = {}
        
        # Basic visualizations
        if options.get('basic', True):
            # Generate wordcloud
            wc_path = os.path.join(report_dir, 'wordcloud.png')
            Visualizer.generate_wordcloud(
                analyzer_results['word_frequency'], 
                title='詞頻雲圖',
                save_path=wc_path
            )
            viz_paths['wordcloud'] = f"/static/results/{report_id}/wordcloud.png"
            
            # Generate word frequency chart
            wf_path = os.path.join(report_dir, 'word_freq.png')
            Visualizer.plot_advanced_word_frequency(
                analyzer_results['word_frequency'],
                top_n=15,
                title='詞頻分布',
                save_path=wf_path
            )
            viz_paths['word_frequency'] = f"/static/results/{report_id}/word_freq.png"
            
            # Generate POS distribution chart
            pos_path = os.path.join(report_dir, 'pos_distribution.png')
            Visualizer.plot_pos_distribution(
                analyzer_results['pos_distribution'],
                title='詞性分布',
                save_path=pos_path
            )
            viz_paths['pos_distribution'] = f"/static/results/{report_id}/pos_distribution.png"
            
            # Generate sentiment chart
            sent_path = os.path.join(report_dir, 'sentiment.png')
            Visualizer.plot_sentiment_analysis(
                analyzer_results['sentiment'],
                title='情感分析',
                save_path=sent_path
            )
            viz_paths['sentiment'] = f"/static/results/{report_id}/sentiment.png"
            
            # Generate entities chart
            entity_path = os.path.join(report_dir, 'entities.png')
            Visualizer.plot_entities(
                analyzer_results['entities'],
                title='命名實體統計',
                save_path=entity_path
            )
            viz_paths['entities'] = f"/static/results/{report_id}/entities.png"
        
        # Advanced visualizations
        if options.get('advanced', True):
            # Generate advanced word frequency visualizations
            wf_vertical_path = os.path.join(report_dir, 'word_freq_vertical.png')
            Visualizer.plot_advanced_word_frequency(
                analyzer_results['word_frequency'],
                top_n=15,
                title='詞頻垂直分布',
                save_path=wf_vertical_path,
                plot_type='vertical'
            )
            viz_paths['word_freq_vertical'] = f"/static/results/{report_id}/word_freq_vertical.png"
            
            wf_pie_path = os.path.join(report_dir, 'word_freq_pie.png')
            Visualizer.plot_advanced_word_frequency(
                analyzer_results['word_frequency'],
                top_n=10, # Limit to top 10 for pie chart clarity
                title='詞頻餅圖',
                save_path=wf_pie_path,
                plot_type='pie'
            )
            viz_paths['word_freq_pie'] = f"/static/results/{report_id}/word_freq_pie.png"
            
            # Generate n-grams chart
            ngrams_path = os.path.join(report_dir, 'ngrams.png')
            Visualizer.plot_ngrams(
                analyzer_results['ngrams'],
                title='N-gram詞組分析',
                save_path=ngrams_path
            )
            viz_paths['ngrams'] = f"/static/results/{report_id}/ngrams.png"
            
            # Generate keywords chart
            keywords_path = os.path.join(report_dir, 'keywords.png')
            Visualizer.plot_keyword_weights(
                analyzer_results['keywords'],
                title='關鍵詞權重',
                save_path=keywords_path
            )
            viz_paths['keywords'] = f"/static/results/{report_id}/keywords.png"
        
        # Generate interactive visualizations if advanced visualizer is available
        if options.get('interactive', True) and advanced_visualizer:
            try:
                # Generate single-text interactive heatmap
                single_heatmap = advanced_visualizer.plot_single_text_heatmap(
                    analyzer_results,
                    title='詞性-詞頻分布熱力圖'
                )
                if single_heatmap:
                    heatmap_path = os.path.join(report_dir, 'interactive_heatmap.html')
                    single_heatmap.write_html(heatmap_path)
                    viz_paths['interactive_heatmap'] = f"/static/results/{report_id}/interactive_heatmap.html"
                
                # Generate single-text interactive network
                single_network = advanced_visualizer.plot_single_text_network(
                    analyzer_results,
                    title='詞語關聯網絡圖'
                )
                if single_network:
                    network_path = os.path.join(report_dir, 'interactive_network.html')
                    single_network.write_html(network_path)
                    viz_paths['interactive_network'] = f"/static/results/{report_id}/interactive_network.html"
                
                # Generate treemap
                treemap = advanced_visualizer.plot_word_frequency_treemap(
                    analyzer_results['word_frequency']
                )
                if treemap:
                    treemap_path = os.path.join(report_dir, 'treemap.html')
                    treemap.write_html(treemap_path)
                    viz_paths['treemap'] = f"/static/results/{report_id}/treemap.html"
                
                # Generate interactive word analysis
                word_analysis = advanced_visualizer.plot_interactive_word_cloud_data(
                    analyzer_results['word_frequency']
                )
                if word_analysis:
                    word_analysis_path = os.path.join(report_dir, 'interactive_word_analysis.html')
                    word_analysis.write_html(word_analysis_path)
                    viz_paths['interactive_word_analysis'] = f"/static/results/{report_id}/interactive_word_analysis.html"
                
                # Generate dashboard with all interactive visualizations
                figures = {}
                if single_heatmap:
                    figures['詞性-詞頻分布熱力圖'] = single_heatmap
                if single_network:
                    figures['詞語關聯網絡圖'] = single_network
                if treemap:
                    figures['詞頻樹狀圖'] = treemap
                if word_analysis:
                    figures['交互式詞頻分析'] = word_analysis
                
                if figures:
                    dashboard_path = os.path.join(report_dir, 'dashboard.html')
                    advanced_visualizer.create_dashboard_html(figures, dashboard_path)
                    viz_paths['dashboard'] = f"/static/results/{report_id}/dashboard.html"
                    
            except Exception as e:
                print(f"Interactive visualization generation failed in report: {e}")
        
        # Add visualization paths to results
        analyzer_results['visualizations'] = viz_paths
        
        # Generate HTML report
        report_title = options.get('title', '中文文本分析報告')
        include_json = options.get('json', True)
        include_data = options.get('data', True)
        include_summary = options.get('summary', True)
        include_interactive = options.get('interactive', True)
        
        # Save the report data to a JSON file
        json_path = os.path.join(report_dir, 'report_data.json')
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(analyzer_results, json_file, ensure_ascii=False, indent=2)
        
        # Generate HTML report
        html_path = os.path.join(report_dir, 'report.html')
        generate_html_report(
            analyzer_results, 
            html_path,
            title=report_title,
            include_json=include_json,
            include_data=include_data,
            include_summary=include_summary,
            include_interactive=include_interactive
        )
        
        return jsonify({
            'success': True,
            'report_id': report_id,
            'report_path': f"/static/results/{report_id}/report.html"
        })
    except Exception as e:
        print(f"Error in generate_report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_comprehensive_report', methods=['POST'])
def generate_comprehensive_report():
    """Generate a comprehensive report including analysis results, interactive charts, and similarity analysis"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        analysis_data = data.get('analysis_data', {})
        similarity_data = data.get('similarity_data', {})
        interactive_data = data.get('interactive_data', {})
        options = data.get('options', {})
        
        if not analysis_data:
            return jsonify({'error': 'No analysis data provided'}), 400
        
        # Generate a unique ID for this comprehensive report
        report_id = str(uuid.uuid4())
        report_dir = os.path.join(RESULTS_FOLDER, report_id)
        os.makedirs(report_dir, exist_ok=True)
        
        # Combine all data
        comprehensive_data = analysis_data.copy()
        
        # Ensure we have the original text for report generation
        if 'original_text' not in comprehensive_data and 'text' in data:
            comprehensive_data['original_text'] = data['text']
        
        # Add similarity analysis if available
        if similarity_data:
            comprehensive_data['similarity_analysis'] = similarity_data
        
        # Add interactive visualizations if available
        if interactive_data:
            comprehensive_data['interactive_visualizations'] = interactive_data
        
        # Generate basic visualizations if they don't exist
        if 'visualizations' not in analysis_data or not analysis_data['visualizations']:
            # Generate basic visualizations in the report directory
            viz_paths = {}
            
            # Generate wordcloud
            if 'word_frequency' in comprehensive_data:
                wc_path = os.path.join(report_dir, 'wordcloud.png')
                try:
                    Visualizer.generate_wordcloud(
                        comprehensive_data['word_frequency'], 
                        title='詞頻雲圖',
                        save_path=wc_path
                    )
                    viz_paths['wordcloud'] = f"/static/results/{report_id}/wordcloud.png"
                except Exception as e:
                    print(f"Error generating wordcloud: {e}")
                
                # Generate word frequency chart
                wf_path = os.path.join(report_dir, 'word_freq.png')
                try:
                    Visualizer.plot_advanced_word_frequency(
                        comprehensive_data['word_frequency'],
                        top_n=15,
                        title='詞頻分布',
                        save_path=wf_path
                    )
                    viz_paths['word_frequency'] = f"/static/results/{report_id}/word_freq.png"
                except Exception as e:
                    print(f"Error generating word frequency chart: {e}")
            
            # Generate POS distribution chart
            if 'pos_distribution' in comprehensive_data:
                pos_path = os.path.join(report_dir, 'pos_distribution.png')
                try:
                    Visualizer.plot_pos_distribution(
                        comprehensive_data['pos_distribution'],
                        title='詞性分布',
                        save_path=pos_path
                    )
                    viz_paths['pos_distribution'] = f"/static/results/{report_id}/pos_distribution.png"
                except Exception as e:
                    print(f"Error generating POS distribution chart: {e}")
            
            # Generate sentiment chart
            if 'sentiment' in comprehensive_data:
                sent_path = os.path.join(report_dir, 'sentiment.png')
                try:
                    Visualizer.plot_sentiment_analysis(
                        comprehensive_data['sentiment'],
                        title='情感分析',
                        save_path=sent_path
                    )
                    viz_paths['sentiment'] = f"/static/results/{report_id}/sentiment.png"
                except Exception as e:
                    print(f"Error generating sentiment chart: {e}")
            
            # Generate entities chart
            if 'entities' in comprehensive_data:
                entity_path = os.path.join(report_dir, 'entities.png')
                try:
                    Visualizer.plot_entities(
                        comprehensive_data['entities'],
                        title='命名實體統計',
                        save_path=entity_path
                    )
                    viz_paths['entities'] = f"/static/results/{report_id}/entities.png"
                except Exception as e:
                    print(f"Error generating entities chart: {e}")
            
            comprehensive_data['visualizations'] = viz_paths
        
        # Copy all existing visualizations to the new directory
        all_visualizations = comprehensive_data.get('visualizations', {}).copy()
        
        # Copy from analysis data
        if 'visualizations' in analysis_data:
            for viz_key, viz_path in analysis_data['visualizations'].items():
                if viz_path:
                    try:
                        # Extract analysis ID from path
                        source_analysis_id = viz_path.split('/')[-2]
                        source_file = viz_path.split('/')[-1]
                        source_path = os.path.join(RESULTS_FOLDER, source_analysis_id, source_file)
                        
                        if os.path.exists(source_path):
                            dest_path = os.path.join(report_dir, source_file)
                            import shutil
                            shutil.copy2(source_path, dest_path)
                            all_visualizations[viz_key] = f"/static/results/{report_id}/{source_file}"
                    except Exception as e:
                        print(f"Error copying visualization {viz_key}: {e}")
        
        # Copy similarity visualizations if available
        if similarity_data and 'visualizations' in similarity_data:
            for viz_key, viz_path in similarity_data['visualizations'].items():
                if viz_path and 'similarity' in viz_key:
                    try:
                        source_analysis_id = viz_path.split('/')[-2]
                        source_file = viz_path.split('/')[-1]
                        source_path = os.path.join(RESULTS_FOLDER, source_analysis_id, source_file)
                        
                        if os.path.exists(source_path):
                            dest_path = os.path.join(report_dir, source_file)
                            import shutil
                            shutil.copy2(source_path, dest_path)
                            all_visualizations[viz_key] = f"/static/results/{report_id}/{source_file}"
                    except Exception as e:
                        print(f"Error copying similarity visualization {viz_key}: {e}")
        
        # Copy interactive visualizations if available
        if interactive_data and 'visualizations' in interactive_data:
            for viz_key, viz_path in interactive_data['visualizations'].items():
                if viz_path:
                    try:
                        source_analysis_id = viz_path.split('/')[-2]
                        source_file = viz_path.split('/')[-1]
                        source_path = os.path.join(RESULTS_FOLDER, source_analysis_id, source_file)
                        
                        if os.path.exists(source_path):
                            dest_path = os.path.join(report_dir, source_file)
                            import shutil
                            shutil.copy2(source_path, dest_path)
                            all_visualizations[viz_key] = f"/static/results/{report_id}/{source_file}"
                    except Exception as e:
                        print(f"Error copying interactive visualization {viz_key}: {e}")
        
        # Update comprehensive data with all visualizations
        comprehensive_data['visualizations'] = all_visualizations
        
        # Generate comprehensive HTML report
        report_title = options.get('title', '中文文本分析完整報告')
        include_json = options.get('json', True)
        include_data = options.get('data', True)
        include_summary = options.get('summary', True)
        include_interactive = options.get('interactive', True)
        include_similarity = bool(similarity_data)
        
        # Save the comprehensive data to a JSON file
        json_path = os.path.join(report_dir, 'report_data.json')
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(comprehensive_data, json_file, ensure_ascii=False, indent=2)
        
        # Generate comprehensive HTML report
        html_path = os.path.join(report_dir, 'report.html')
        generate_comprehensive_html_report(
            comprehensive_data,
            html_path,
            title=report_title,
            include_json=include_json,
            include_data=include_data,
            include_summary=include_summary,
            include_interactive=include_interactive,
            include_similarity=include_similarity
        )
        
        return jsonify({
            'success': True,
            'report_id': report_id,
            'report_path': f"/static/results/{report_id}/report.html"
        })
        
    except Exception as e:
        print(f"Error in generate_comprehensive_report: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download_report/<report_id>', methods=['GET'])
def download_report(report_id):
    """Download a generated report"""
    try:
        report_path = os.path.join(RESULTS_FOLDER, report_id, 'report.html')
        if not os.path.exists(report_path):
            return jsonify({'error': 'Report not found'}), 404
        
        return send_file(
            report_path,
            mimetype='text/html',
            as_attachment=True,
            attachment_filename='chinese_text_analysis_report.html'
        )
    except Exception as e:
        print(f"Error in download_report: {str(e)}")
        return jsonify({'error': str(e)}), 500

def generate_html_report(data, output_path, title='中文文本分析報告', include_json=True, include_data=True, include_summary=True, include_interactive=True):
    """Generate an HTML report with all visualizations and data"""
    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 
                        'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3 {{
            color: #0066cc;
        }}
        .content-section {{
            margin-bottom: 40px;
            padding: 20px;
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .visualizations-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: center;
        }}
        .visualization-card {{
            flex: 0 0 calc(50% - 20px);
            max-width: 600px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 20px;
        }}
        .visualization-card h3 {{
            padding: 10px 15px;
            margin: 0;
            background-color: #f5f5f5;
            border-bottom: 1px solid #ddd;
            font-size: 16px;
        }}
        .visualization-card img {{
            width: 100%;
            display: block;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        .data-table th, .data-table td {{
            padding: 8px 12px;
            border: 1px solid #ddd;
            text-align: left;
        }}
        .data-table th {{
            background-color: #f5f5f5;
        }}
        .summary-box {{
            background-color: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #0066cc;
            margin-bottom: 20px;
        }}
        pre {{
            background-color: #f5f5f5;
            padding: 15px;
            overflow-x: auto;
            border-radius: 4px;
            font-size: 14px;
        }}
        footer {{
            margin-top: 50px;
            text-align: center;
            color: #777;
            font-size: 14px;
        }}
        .entity-tag {{
            display: inline-block;
            padding: 2px 8px;
            margin: 2px;
            border-radius: 12px;
            font-size: 14px;
        }}
        .entity-person {{
            background-color: #ffcccc;
        }}
        .entity-location {{
            background-color: #ccffcc;
        }}
        .entity-organization {{
            background-color: #ccccff;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    
    <div class="content-section">
        <h2>文本內容</h2>
        <div class="text-content">
            <p>{data.get('original_text', '未提供原始文本')}</p>
        </div>
    </div>
    """
    
    # Add summary section if requested
    if include_summary and 'summary' in data:
        html += f"""
    <div class="content-section">
        <h2>文本摘要</h2>
        <div class="summary-box">
            <p>{data.get('summary', '無法生成摘要')}</p>
        </div>
    </div>
        """
    
    # Add basic statistics
    html += f"""
    <div class="content-section">
        <h2>基本統計</h2>
        <ul>
            <li><strong>總詞數:</strong> {data.get('total_words', 0)}</li>
            <li><strong>平均詞長:</strong> {data.get('avg_word_length', 0)} 字</li>
            <li><strong>情感傾向:</strong> {data.get('sentiment', {}).get('sentiment_label', '未知')}</li>
            <li><strong>正面詞數量:</strong> {data.get('sentiment', {}).get('positive_count', 0)}</li>
            <li><strong>負面詞數量:</strong> {data.get('sentiment', {}).get('negative_count', 0)}</li>
        </ul>
    </div>
    """
    
    # Add visualizations section
    if 'visualizations' in data and data['visualizations']:
        html += """
    <div class="content-section">
        <h2>視覺化分析</h2>
        <div class="visualizations-container">
        """
        
        # Map of visualization types to display names
        viz_names = {
            'wordcloud': '詞頻雲圖',
            'word_frequency': '詞頻分布',
            'pos_distribution': '詞性分布',
            'sentiment': '情感分析',
            'entities': '命名實體統計',
            'ngrams': 'N-gram詞組分析',
            'keywords': '關鍵詞權重',
            'word_freq_vertical': '詞頻垂直分布',
            'word_freq_pie': '詞頻餅圖'
        }
        
        for viz_type, viz_path in data['visualizations'].items():
            if viz_type in viz_names:
                # Extract just the filename from the full path for relative linking
                filename = viz_path.split('/')[-1] if viz_path else ''
                html += f"""
            <div class="visualization-card">
                <h3>{viz_names[viz_type]}</h3>
                <img src="{filename}" alt="{viz_names[viz_type]}">
            </div>
                """
        
        html += """
        </div>
    </div>
        """
    
    # Add interactive visualizations section
    if include_interactive and 'visualizations' in data and data['visualizations']:
        # Check if there are any interactive visualizations
        interactive_viz = {k: v for k, v in data['visualizations'].items() 
                          if k in ['interactive_heatmap', 'interactive_network', 'treemap', 'interactive_word_analysis', 'dashboard']}
        
        if interactive_viz:
            html += """
    <div class="content-section">
        <h2>交互式圖表</h2>
        <div class="visualizations-container">
            """
            
            # Map of interactive visualization types to display names
            interactive_viz_names = {
                'interactive_heatmap': '交互式詞性-詞頻熱力圖',
                'interactive_network': '交互式詞語關聯網絡圖',
                'treemap': '詞頻樹狀圖',
                'interactive_word_analysis': '交互式詞頻分析',
                'dashboard': '綜合分析儀表板'
            }
            
            for viz_type, viz_path in interactive_viz.items():
                viz_name = interactive_viz_names.get(viz_type, viz_type)
                filename = viz_path.split('/')[-1] if viz_path else ''
                html += f"""
            <div class="visualization-card" style="flex: 0 0 100%; max-width: 100%;">
                <h3>{viz_name}</h3>
                <iframe src="{filename}" width="100%" height="600" frameborder="0"></iframe>
            </div>
                """
            
            html += """
        </div>
    </div>
            """
    
    # Add data tables if requested
    if include_data:
        html += """
    <div class="content-section">
        <h2>詳細數據</h2>
        """
        
        # Word frequency table
        if 'word_frequency' in data:
            html += """
        <h3>詞頻統計</h3>
        <table class="data-table">
            <thead>
                <tr>
                    <th>詞語</th>
                    <th>頻率</th>
                </tr>
            </thead>
            <tbody>
            """
            
            # Get top 30 words by frequency
            top_words = sorted(data['word_frequency'].items(), key=lambda x: x[1], reverse=True)[:30]
            
            for word, freq in top_words:
                html += f"""
                <tr>
                    <td>{word}</td>
                    <td>{freq}</td>
                </tr>
                """
            
            html += """
            </tbody>
        </table>
            """
        
        # POS distribution table
        if 'pos_distribution' in data:
            html += """
        <h3>詞性分布</h3>
        <table class="data-table">
            <thead>
                <tr>
                    <th>詞性</th>
                    <th>數量</th>
                </tr>
            </thead>
            <tbody>
            """
            
            pos_items = sorted(data['pos_distribution'].items(), key=lambda x: x[1], reverse=True)
            
            for pos, count in pos_items:
                html += f"""
                <tr>
                    <td>{pos}</td>
                    <td>{count}</td>
                </tr>
                """
            
            html += """
            </tbody>
        </table>
            """
        
        # Named entities
        if 'entities' in data:
            html += """
        <h3>命名實體</h3>
            """
            
            entity_types = {
                'person': '人名',
                'location': '地名',
                'organization': '機構名'
            }
            
            for entity_type, entities in data['entities'].items():
                if entities:
                    entity_type_display = entity_types.get(entity_type, entity_type)
                    html += f"""
        <h4>{entity_type_display}</h4>
        <div>
            """
                    
                    for entity in entities:
                        html += f"""
            <span class="entity-tag entity-{entity_type}">{entity}</span>
                        """
                    
                    html += """
        </div>
                    """
        
        html += """
    </div>
        """
    
    # Add JSON data if requested
    if include_json:
        import json
        
        # Create a copy of data without original_text to avoid excessive size
        json_data = {k: v for k, v in data.items() if k != 'original_text'}
        # Remove image paths as they won't be valid outside the server context
        if 'visualizations' in json_data:
            # Use relative paths for the report
            json_data['visualizations'] = {k: '.' + v for k, v in json_data['visualizations'].items()}
        
        html += """
    <div class="content-section">
        <h2>JSON 數據</h2>
        <pre>""" + json.dumps(json_data, ensure_ascii=False, indent=2) + """</pre>
    </div>
        """
    
    # Add footer
    from datetime import datetime
    
    html += f"""
    <footer>
        <p>生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Chinese Text Analyzer © {datetime.now().year}</p>
    </footer>
</body>
</html>
    """
    
    # Write the HTML to the output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

def generate_comprehensive_html_report(data, output_path, title='中文文本分析完整報告', include_json=True, include_data=True, include_summary=True, include_interactive=True, include_similarity=True):
    """Generate a comprehensive HTML report with all visualizations, interactive charts, and similarity analysis"""
    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 
                        'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3 {{
            color: #0066cc;
        }}
        .content-section {{
            margin-bottom: 40px;
            padding: 20px;
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .visualizations-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: center;
        }}
        .visualization-card {{
            flex: 0 0 calc(50% - 20px);
            max-width: 600px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 20px;
        }}
        .visualization-card.full-width {{
            flex: 0 0 100%;
            max-width: 100%;
        }}
        .visualization-card h3 {{
            padding: 10px 15px;
            margin: 0;
            background-color: #f5f5f5;
            border-bottom: 1px solid #ddd;
            font-size: 16px;
        }}
        .visualization-card img {{
            width: 100%;
            display: block;
        }}
        .visualization-card iframe {{
            width: 100%;
            border: none;
            display: block;
        }}
        .nav-tabs {{
            border-bottom: 2px solid #0066cc;
            margin-bottom: 20px;
        }}
        .nav-tab {{
            display: inline-block;
            padding: 10px 20px;
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            border-bottom: none;
            margin-right: 5px;
            cursor: pointer;
            text-decoration: none;
            color: #333;
        }}
        .nav-tab.active {{
            background-color: #0066cc;
            color: white;
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}
    </style>
    <script>
        function showTab(tabId) {{
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Remove active class from all nav tabs
            document.querySelectorAll('.nav-tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Show selected tab content
            document.getElementById(tabId).classList.add('active');
            
            // Add active class to clicked nav tab
            event.target.classList.add('active');
        }}
    </script>
</head>
<body>
    <h1>{title}</h1>
    
    <div class="content-section">
        <h2>文本內容</h2>
        <div class="text-content">
            <p>{data.get('original_text', '未提供原始文本')}</p>
        </div>
    </div>
    
    <div class="content-section">
        <h2>視覺化分析</h2>
        
        <div class="nav-tabs">
            <a href="#" class="nav-tab active" onclick="showTab('basic-viz')">基礎分析圖表</a>
            <a href="#" class="nav-tab" onclick="showTab('interactive-viz')">交互式圖表</a>
            <a href="#" class="nav-tab" onclick="showTab('similarity-viz')">相似度分析</a>
        </div>
        
        <div id="basic-viz" class="tab-content active">
            <h3>基礎分析圖表</h3>
            <div class="visualizations-container">
    """
    
    # Add basic visualizations
    basic_viz_count = 0
    if 'visualizations' in data and data['visualizations']:
        basic_viz_names = {
            'wordcloud': '詞頻雲圖',
            'word_frequency': '詞頻分布',
            'pos_distribution': '詞性分布',
            'sentiment': '情感分析',
            'entities': '命名實體統計',
            'ngrams': 'N-gram詞組分析',
            'keywords': '關鍵詞權重',
            'word_freq_vertical': '詞頻垂直分布',
            'word_freq_pie': '詞頻餅圖'
        }
        
        for viz_type, viz_path in data['visualizations'].items():
            if viz_type in basic_viz_names:
                filename = viz_path.split('/')[-1] if viz_path else ''
                html += f"""
                <div class="visualization-card">
                    <h3>{basic_viz_names[viz_type]}</h3>
                    <img src="{filename}" alt="{basic_viz_names[viz_type]}">
                </div>
                """
                basic_viz_count += 1
    
    if basic_viz_count == 0:
        html += '<p class="text-muted">暫無基礎分析圖表</p>'
    
    html += """
            </div>
        </div>
        
        <div id="interactive-viz" class="tab-content">
            <h3>交互式圖表</h3>
            <div class="visualizations-container">
    """
    
    # Add interactive visualizations
    interactive_viz_count = 0
    if 'visualizations' in data:
        interactive_viz = {k: v for k, v in data['visualizations'].items() 
                          if k in ['interactive_heatmap', 'interactive_network', 'treemap', 'interactive_word_analysis', 'dashboard']}
        
        interactive_viz_names = {
            'interactive_heatmap': '交互式詞性-詞頻熱力圖',
            'interactive_network': '交互式詞語關聯網絡圖',
            'treemap': '詞頻樹狀圖',
            'interactive_word_analysis': '交互式詞頻分析',
            'dashboard': '綜合分析儀表板'
        }
        
        for viz_type, viz_path in interactive_viz.items():
            viz_name = interactive_viz_names.get(viz_type, viz_type)
            # For interactive visualizations, use the filename only since they're copied to the same directory
            filename = viz_path.split('/')[-1] if viz_path else ''
            html += f"""
            <div class="visualization-card full-width">
                <h3>{viz_name}</h3>
                <iframe src="{filename}" height="600"></iframe>
            </div>
            """
            interactive_viz_count += 1
    
    if interactive_viz_count == 0:
        html += '<p class="text-muted">暫無交互式圖表</p>'
    
    html += """
            </div>
        </div>
        
        <div id="similarity-viz" class="tab-content">
            <h3>相似度分析</h3>
    """
    
    # Add similarity analysis section
    if 'similarity_analysis' in data:
        similarity_data = data['similarity_analysis']
        
        # Add similarity visualizations
        if 'visualizations' in similarity_data:
            html += '<div class="visualizations-container">'
            
            similarity_viz_names = {
                'similarity_heatmap': '相似度熱力圖',
                'similarity_network': '相似度網絡圖',
                'interactive_heatmap': '交互式相似度熱力圖',
                'interactive_network': '交互式相似度網絡圖'
            }
            
            for viz_type, viz_path in similarity_data['visualizations'].items():
                if viz_type in similarity_viz_names:
                    viz_name = similarity_viz_names[viz_type]
                    filename = viz_path.split('/')[-1] if viz_path else ''
                    
                    if filename.endswith('.html'):
                        html += f"""
                        <div class="visualization-card full-width">
                            <h3>{viz_name}</h3>
                            <iframe src="{filename}" height="600"></iframe>
                        </div>
                        """
                    else:
                        html += f"""
                        <div class="visualization-card">
                            <h3>{viz_name}</h3>
                            <img src="{filename}" alt="{viz_name}">
                        </div>
                        """
            
            html += '</div>'
    else:
        html += '<p class="text-muted">未進行相似度分析</p>'
    
    html += """
        </div>
    </div>
    
    <footer>
        <p>Chinese Text Analyzer 完整報告</p>
    </footer>
</body>
</html>
    """
    
    # Write the HTML to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

# Add new endpoint for system capabilities
@app.route('/api/system/capabilities', methods=['GET'])
def get_system_capabilities():
    """Get available system capabilities for advanced features"""
    capabilities = {
        'similarity_analysis': similarity_analyzer is not None,
        'advanced_visualization': advanced_visualizer is not None,
        'task_queue': task_queue is not None,
        'file_parsing': file_parser is not None,
        'gpu_acceleration': GPU_AVAILABLE,
        'supported_formats': file_parser.get_supported_extensions() if file_parser else ['txt']
    }
    return jsonify(capabilities)

# Add new endpoint for text similarity analysis
@app.route('/api/similarity/analyze', methods=['POST'])
def analyze_similarity():
    """Analyze similarity between multiple texts"""
    if not similarity_analyzer:
        return jsonify({'error': 'Similarity analysis not available'}), 400
    
    try:
        data = request.json
        texts = data.get('texts', [])
        
        if len(texts) < 2:
            return jsonify({'error': 'At least 2 texts are required for similarity analysis'}), 400
        
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        result_dir = os.path.join(RESULTS_FOLDER, analysis_id)
        os.makedirs(result_dir, exist_ok=True)
        
        # Perform similarity analysis
        similarity_results = similarity_analyzer.comprehensive_similarity_analysis(texts)
        
        # Generate advanced visualizations if available
        if advanced_visualizer:
            viz_paths = {}
            
            # Extract similarity matrix (use semantic similarity as default)
            similarity_matrix = similarity_results['similarities']['semantic']
            
            # Similarity heatmap
            heatmap_path = os.path.join(result_dir, 'similarity_heatmap.png')
            advanced_visualizer.plot_similarity_heatmap(
                similarity_matrix,
                labels=similarity_results['labels'],
                save_path=heatmap_path
            )
            viz_paths['similarity_heatmap'] = f"/static/results/{analysis_id}/similarity_heatmap.png"
            
            # Interactive heatmap
            try:
                interactive_heatmap = advanced_visualizer.plot_interactive_similarity_heatmap(
                    similarity_matrix,
                    labels=similarity_results['labels']
                )
                heatmap_html_path = os.path.join(result_dir, 'interactive_heatmap.html')
                interactive_heatmap.write_html(heatmap_html_path)
                viz_paths['interactive_heatmap'] = f"/static/results/{analysis_id}/interactive_heatmap.html"
            except:
                pass
            
            # Network graph
            network_path = os.path.join(result_dir, 'similarity_network.png')
            advanced_visualizer.plot_text_network(
                similarity_matrix,
                labels=similarity_results['labels'],
                save_path=network_path
            )
            viz_paths['similarity_network'] = f"/static/results/{analysis_id}/similarity_network.png"
            
            # Interactive network
            try:
                interactive_network = advanced_visualizer.plot_interactive_network(
                    similarity_matrix,
                    labels=similarity_results['labels']
                )
                network_html_path = os.path.join(result_dir, 'interactive_network.html')
                interactive_network.write_html(network_html_path)
                viz_paths['interactive_network'] = f"/static/results/{analysis_id}/interactive_network.html"
            except:
                pass
            
            similarity_results['visualizations'] = viz_paths
            
            # Add the similarity matrix for frontend display
            similarity_results['similarity_matrix'] = similarity_matrix
        else:
            # If no advanced visualizer, still add similarity matrix
            similarity_results['similarity_matrix'] = similarity_results['similarities']['semantic']
        
        # Save results
        with open(os.path.join(result_dir, 'similarity_results.json'), 'w', encoding='utf-8') as f:
            json.dump(similarity_results, f, ensure_ascii=False, indent=2)
        
        return jsonify(similarity_results)
        
    except Exception as e:
        print(f"Error in similarity analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add new endpoint for advanced visualizations
@app.route('/api/visualizations/advanced', methods=['POST'])
def generate_advanced_visualizations():
    """Generate advanced interactive visualizations"""
    if not advanced_visualizer:
        return jsonify({'error': 'Advanced visualization not available'}), 400
    
    try:
        data = request.json
        analysis_data = data.get('analysis_data', {})
        
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        result_dir = os.path.join(RESULTS_FOLDER, analysis_id)
        os.makedirs(result_dir, exist_ok=True)
        
        viz_paths = {}
        
        # Generate word frequency treemap
        if 'word_frequency' in analysis_data:
            try:
                treemap = advanced_visualizer.plot_word_frequency_treemap(
                    analysis_data['word_frequency']
                )
                treemap_path = os.path.join(result_dir, 'treemap.html')
                treemap.write_html(treemap_path)
                viz_paths['treemap'] = f"/static/results/{analysis_id}/treemap.html"
            except Exception as e:
                print(f"Treemap generation failed: {e}")
        
        # Generate interactive word cloud data
        if 'word_frequency' in analysis_data:
            try:
                word_analysis = advanced_visualizer.plot_interactive_word_cloud_data(
                    analysis_data['word_frequency']
                )
                word_analysis_path = os.path.join(result_dir, 'interactive_word_analysis.html')
                word_analysis.write_html(word_analysis_path)
                viz_paths['interactive_word_analysis'] = f"/static/results/{analysis_id}/interactive_word_analysis.html"
            except Exception as e:
                print(f"Interactive word analysis generation failed: {e}")
        
        # Generate single-text interactive heatmap
        try:
            single_heatmap = advanced_visualizer.plot_single_text_heatmap(
                analysis_data,
                title='詞性-詞頻分布熱力圖'
            )
            if single_heatmap:
                heatmap_path = os.path.join(result_dir, 'interactive_heatmap.html')
                single_heatmap.write_html(heatmap_path)
                viz_paths['interactive_heatmap'] = f"/static/results/{analysis_id}/interactive_heatmap.html"
        except Exception as e:
            print(f"Single text heatmap generation failed: {e}")
        
        # Generate single-text interactive network
        try:
            single_network = advanced_visualizer.plot_single_text_network(
                analysis_data,
                title='詞語關聯網絡圖'
            )
            if single_network:
                network_path = os.path.join(result_dir, 'interactive_network.html')
                single_network.write_html(network_path)
                viz_paths['interactive_network'] = f"/static/results/{analysis_id}/interactive_network.html"
        except Exception as e:
            print(f"Single text network generation failed: {e}")
        
        # Generate dashboard
        if len(viz_paths) > 0:
            try:
                figures = {}
                if 'word_frequency' in analysis_data:
                    figures['Word Frequency Treemap'] = advanced_visualizer.plot_word_frequency_treemap(
                        analysis_data['word_frequency']
                    )
                    figures['Interactive Word Analysis'] = advanced_visualizer.plot_interactive_word_cloud_data(
                        analysis_data['word_frequency']
                    )
                    
                    # Add single-text visualizations to dashboard
                    single_heatmap = advanced_visualizer.plot_single_text_heatmap(
                        analysis_data,
                        title='詞性-詞頻分布熱力圖'
                    )
                    if single_heatmap:
                        figures['POS-Word Frequency Heatmap'] = single_heatmap
                    
                    single_network = advanced_visualizer.plot_single_text_network(
                        analysis_data,
                        title='詞語關聯網絡圖'
                    )
                    if single_network:
                        figures['Word Association Network'] = single_network
                
                dashboard_path = os.path.join(result_dir, 'dashboard.html')
                advanced_visualizer.create_dashboard_html(figures, dashboard_path)
                viz_paths['dashboard'] = f"/static/results/{analysis_id}/dashboard.html"
            except Exception as e:
                print(f"Dashboard generation failed: {e}")
        
        return jsonify({'visualizations': viz_paths})
        
    except Exception as e:
        print(f"Error in advanced visualization: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add new endpoint for file upload and parsing
@app.route('/api/file/upload', methods=['POST'])
def upload_and_parse_file():
    """Upload and parse various file formats"""
    if not file_parser:
        return jsonify({'error': 'File parsing not available'}), 400
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file
        filename = str(uuid.uuid4()) + '_' + file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Parse file
        parsed_data = file_parser.parse_file(file_path)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return jsonify({
            'content': parsed_data['content'],
            'metadata': parsed_data['metadata'],
            'filename': file.filename
        })
        
    except Exception as e:
        print(f"Error in file parsing: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add new endpoint for task queue operations
@app.route('/api/tasks/create', methods=['POST'])
def create_task():
    """Create a new analysis task"""
    if not task_queue:
        return jsonify({'error': 'Task queue not available'}), 400
    
    try:
        data = request.json
        task_type = data.get('task_type', 'text_analysis')
        task_data = data.get('task_data', {})
        
        task_id = task_queue.create_task(task_type, task_data)
        
        return jsonify({
            'task_id': task_id,
            'status': 'created'
        })
        
    except Exception as e:
        print(f"Error creating task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<task_id>/status', methods=['GET'])
def get_task_status(task_id):
    """Get task status"""
    if not task_queue:
        return jsonify({'error': 'Task queue not available'}), 400
    
    try:
        status = task_queue.get_task_status(task_id)
        return jsonify(status)
        
    except Exception as e:
        print(f"Error getting task status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<task_id>/result', methods=['GET'])
def get_task_result(task_id):
    """Get task result"""
    if not task_queue:
        return jsonify({'error': 'Task queue not available'}), 400
    
    try:
        result = task_queue.get_task_result(task_id)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error getting task result: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)