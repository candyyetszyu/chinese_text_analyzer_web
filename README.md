# Chinese Text Analyzer (Web Version)

A comprehensive web application for analyzing Chinese text with visualizations, sentiment analysis, and text conversion tools.

## Overview

Chinese Text Analyzer is a Flask-based web application that provides a user-friendly interface for analyzing Chinese text. It offers a suite of text analysis tools, visualizations, and conversion utilities designed specifically for processing Chinese language content.

## Features

### Text Analysis
- **Word Frequency Analysis**: Identify the most common words in your text with visualizations
- **Part-of-Speech Distribution**: Analyze the grammatical structure of your text
- **Named Entity Recognition**: Automatically extract people, locations, and organizations
- **Sentiment Analysis**: Determine if text sentiment is positive, negative, or neutral
- **Keyword Extraction**: Extract the most important terms from your text
- **N-gram Analysis**: Identify common word combinations and phrases

### Visualizations
- **Word Cloud**: Visual representation of word frequency with more frequent words appearing larger
- **Word Frequency Charts**: Multiple visualization options for word frequency (horizontal bars, vertical bars, pie charts)
- **POS Distribution Charts**: Visualize the distribution of different parts of speech
- **Sentiment Analysis Charts**: Visual breakdown of positive/negative sentiment
- **Entity Charts**: Visual representation of extracted named entities
- **Advanced Charts**: Word length distribution, keyword weights, and n-gram frequency

### Data Export
- Export analysis results as JSON or CSV
- Download visualizations as PNG images
- Bundle all visualizations as a zip file
- Generate and download comprehensive analysis reports

### Text Conversion
- Convert between Traditional and Simplified Chinese
- Copy or download converted text

## Getting Started

### Prerequisites
- Python 3.6 or higher
- Flask
- jieba (Chinese text segmentation library)
- Other Python packages: see requirements.txt

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/chinese_text_analyzer_web.git
   cd chinese_text_analyzer_web
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Open your browser and navigate to http://localhost:5000

## Usage

### Text Analysis
1. Enter or paste Chinese text in the text area on the left panel
2. Click "分析文本" (Analyze Text) button
3. View the analysis results in the right panel tabs
4. Toggle between different visualization types using the tabs

### Simplified/Traditional Chinese Conversion
1. Select the "繁簡轉換" (Conversion) tab in the left panel
2. Enter text to convert
3. Select conversion direction (Simplified to Traditional or vice versa)
4. Click "轉換" (Convert) button
5. Copy or download the converted text

### Sample Analysis
- Click "載入範例" (Load Sample) to analyze a sample text

## Project Structure

- `app.py`: Main Flask application
- `analyzer.py`: Core analysis functionality
- `visualization.py`: Chart generation utilities
- `convert_chinese.py`: Chinese text conversion functions
- `static/`: CSS, JavaScript, and result files
- `templates/`: HTML templates for the web interface
- `resources/`: Dictionaries, stopwords, and sentiment lexicons
- `input_texts/`: Sample texts for demonstration

## Advanced Usage

### Custom Dictionaries
The system uses resources in the `resources/` directory:
- `custom_dict.txt`: Custom word dictionary for the jieba tokenizer
- `chinese_stopwords.txt`: Stopwords list
- `positive_words.txt` & `negative_words.txt`: Sentiment analysis lexicons

## Technical Details

The application uses:
- **Flask**: Web framework
- **Jieba**: Chinese text segmentation
- **Matplotlib/Seaborn**: Visualization generation
- **OpenCC**: Chinese text conversion
- **Bootstrap**: Frontend UI framework
- **JavaScript**: Interactive frontend functionality

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Jieba](https://github.com/fxsjy/jieba) - Chinese text segmentation library
- [OpenCC](https://github.com/BYVoid/OpenCC) - Chinese text conversion library
- [Bootstrap](https://getbootstrap.com/) - Frontend framework# chinese_text_analyzer_web
