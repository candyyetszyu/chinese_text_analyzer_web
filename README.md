# Chinese Text Analyzer

A comprehensive Chinese text analysis application with both web and CLI interfaces. Provides word frequency analysis, sentiment analysis, part-of-speech tagging, named entity recognition, and text conversion between Traditional and Simplified Chinese.

## 📖 Complete Documentation

**👉 For comprehensive documentation, tutorials, and API reference:**  
**[Open docs/documentation.html](documentation.html) in your browser**

*Or view it online by opening the file directly: `docs/documentation.html`*

## 🚀 Quick Start

The application runs on **port 3000** by default. To start:

```bash
python run_web.py
```

Visit: http://localhost:3000

## ✨ Key Features

### Core Features
- **Text Analysis**: Word frequency, POS tagging, sentiment analysis, NER
- **Visualizations**: Word clouds, interactive charts, advanced analytics  
- **Text Conversion**: Traditional ↔ Simplified Chinese conversion
- **Data Export**: JSON, CSV, Excel, HTML reports with ZIP downloads
- **Dual Interface**: Web UI and command-line tools

### 🆕 Advanced Features
- **📊 Text Similarity Analysis**: Multi-text comparison with semantic analysis and similarity matrices
- **🎯 Interactive Visualizations**: Plotly-powered heatmaps, network graphs, treemaps, dashboards
- **⚡ Task Queue System**: Celery-based distributed processing for batch operations
- **🚀 GPU Acceleration**: CUDA support for large-scale text processing (when available)
- **📄 Multi-Format Support**: Direct parsing of PDF, DOCX, HTML, Markdown, CSV, JSON files

## 📁 Project Structure

```
chinese_text_analyzer_web/
├── src/                          # Source code
│   ├── core/                     # Core analysis modules
│   │   ├── analyzer.py           # Main text analysis engine
│   │   ├── visualization.py      # Chart and graph generation
│   │   ├── advanced_visualization.py # Interactive Plotly charts
│   │   ├── similarity.py         # Text similarity analysis
│   │   └── task_queue.py         # Celery task queue system
│   ├── web/                      # Web application
│   │   ├── app.py               # Flask web server
│   │   ├── static/              # CSS, JS, and result files
│   │   └── templates/           # HTML templates
│   ├── cli/                      # Command-line interface
│   │   ├── main.py              # CLI main entry point
│   │   └── menu.py              # Interactive CLI menu
│   └── utils/                    # Utility modules
│       └── file_parsers.py      # Multi-format file parsing
├── data/                         # Data directories
│   ├── input/                   # Sample texts and input files
│   └── output/                  # Analysis results and uploads
├── config/                       # Configuration files
│   ├── chinese_stopwords.txt   # Chinese stopwords list
│   ├── custom_dict.txt         # Custom jieba dictionary
│   ├── positive_words.txt      # Positive sentiment words
│   ├── negative_words.txt      # Negative sentiment words
│   └── mappings/               # Label mapping files
├── docs/                        # Documentation
├── requirements.txt             # Python dependencies
├── setup.py                    # Installation script
├── run_web.py                  # Web app launcher
└── run_cli.py                  # CLI app launcher
```

## 🔧 How to Change Port

### Method 1: Environment Variable (Recommended)

Set the `PORT` environment variable before running:

```bash
# On macOS/Linux:
export PORT=8080
python run_web.py

# On Windows:
set PORT=8080
python run_web.py
```

### Method 2: Edit run_web.py

1. Open `run_web.py`:
   ```python
   # Change this line:
   port = int(os.environ.get('PORT', 3000))
   
   # To your desired port:
   port = int(os.environ.get('PORT', 8080))  # Example: port 8080
   ```

2. Save and run:
   ```bash
   python run_web.py
   ```

### Method 3: Direct Flask App Configuration

1. Open `src/web/app.py`
2. Find the bottom of the file:
   ```python
   if __name__ == '__main__':
       app.run(debug=True, port=3000)  # Change 3000 to your port
   ```

### Method 4: Command Line Argument

You can also pass the port directly when starting:

```bash
python -c "
import os
os.environ['PORT'] = '8080'
exec(open('run_web.py').read())
"
```

## 🚨 Port Conflicts

**Common port conflicts:**
- **Port 5000**: Used by macOS Control Center (AirPlay Receiver)
- **Port 8080**: Often used by development servers
- **Port 3000**: Default for many React/Node.js apps

**Safe ports to use:**
- 3001, 3002, 8081, 8082, 9000, 9001

## ⚠️ Important Notes

1. **Always restart** the application after changing the port
2. **Update browser URL** to match the new port
3. **Check firewall settings** if accessing from other devices
4. **JavaScript API calls** will automatically use the correct port

## 📖 For Complete Documentation

Visit: [docs/documentation.html](documentation.html) 