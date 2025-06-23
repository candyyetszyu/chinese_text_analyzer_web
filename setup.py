#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Setup script for Chinese Text Analyzer
Includes new features: text similarity, advanced visualization, task queue, GPU acceleration, multi-format support
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

def run_command(command, description, optional=False):
    """Run command and handle errors"""
    print(f"🔧 {description}...")
    try:
        if isinstance(command, list):
            subprocess.run(command, check=True)
        else:
            subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        if optional:
            print(f"⚠️ {description} skipped: {e}")
            return True
        else:
            print(f"❌ {description} failed: {e}")
            return False

def create_virtual_environment():
    """Create enhanced virtual environment"""
    print("🐍 Creating virtual environment...")
    
    if Path("venv").exists():
        print("⚠️ Virtual environment already exists, skipping creation")
        if platform.system() == "Windows":
            return os.path.join("venv", "Scripts", "pip"), os.path.join("venv", "Scripts", "python")
        else:
            return os.path.join("venv", "bin", "pip"), os.path.join("venv", "bin", "python")
    
    # Check Python version
    python_version = platform.python_version()
    major, minor = python_version.split('.')[:2]
    if int(major) < 3 or (int(major) == 3 and int(minor) < 8):
        print("❌ Python 3.8 or higher is required")
        return None, None
    
    if platform.system() == "Windows":
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        pip_path = os.path.join("venv", "Scripts", "pip")
        python_path = os.path.join("venv", "Scripts", "python")
    else:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        pip_path = os.path.join("venv", "bin", "pip")
        python_path = os.path.join("venv", "bin", "python")
    
    print("✅ Virtual environment created successfully")
    return pip_path, python_path

def install_basic_requirements(pip_path):
    """Install basic requirements"""
    print("📦 Installing basic dependencies...")
    
    # Upgrade pip
    run_command([pip_path, "install", "--upgrade", "pip"], "Upgrading pip")
    
    # Install basic dependencies from requirements.txt
    if Path("requirements.txt").exists():
        run_command([pip_path, "install", "-r", "requirements.txt"], "Installing basic dependencies")
    else:
        # Manually install core dependencies
        core_deps = [
            "Flask>=2.3.0", "Flask-CORS>=4.0.0", "jieba>=0.42.1",
            "matplotlib>=3.7.0", "seaborn>=0.12.0", "numpy>=1.24.0",
            "pandas>=2.0.0", "scikit-learn>=1.3.0", "Pillow>=10.0.0"
        ]
        for dep in core_deps:
            run_command([pip_path, "install", dep], f"Installing {dep.split('>=')[0]}")

def install_enhanced_features(pip_path):
    """Install enhanced features dependencies"""
    print("\n🚀 Installing new feature dependencies...")
    
    # Advanced visualization
    print("📊 Installing visualization dependencies...")
    viz_deps = ["plotly>=5.15.0", "networkx>=3.1", "dash>=2.14.0"]
    for dep in viz_deps:
        run_command([pip_path, "install", dep], f"Installing {dep.split('>=')[0]}", optional=True)
    
    # File parsing
    print("📁 Installing file parsing dependencies...")
    file_deps = [
        "PyPDF2>=3.0.0", "python-docx>=0.8.11", "beautifulsoup4>=4.12.0",
        "requests>=2.31.0", "pdfplumber>=0.9.0"
    ]
    for dep in file_deps:
        run_command([pip_path, "install", dep], f"Installing {dep.split('>=')[0]}", optional=True)
    
    # Task queue
    print("⚙️ Installing task queue dependencies...")
    queue_deps = ["celery>=5.3.0", "redis>=4.6.0"]
    for dep in queue_deps:
        run_command([pip_path, "install", dep], f"Installing {dep.split('>=')[0]}", optional=True)
    
    # AI/ML dependencies
    print("🤖 Installing AI dependencies...")
    
    # PyTorch (choose version based on system)
    try:
        # Detect GPU
        gpu_available = False
        if platform.system() != "Darwin":  # Non-macOS
            try:
                subprocess.run("nvidia-smi", capture_output=True, check=True)
                gpu_available = True
                print("✅ NVIDIA GPU detected")
            except:
                pass
        
        if gpu_available:
            torch_cmd = [pip_path, "install", "torch>=2.0.0", "--index-url", 
                        "https://download.pytorch.org/whl/cu118"]
            run_command(torch_cmd, "Installing GPU PyTorch", optional=True)
        else:
            run_command([pip_path, "install", "torch>=2.0.0"], "Installing CPU PyTorch", optional=True)
    except:
        run_command([pip_path, "install", "torch>=2.0.0"], "Installing PyTorch", optional=True)
    
    # Other AI dependencies
    ai_deps = [
        "transformers>=4.30.0", "sentence-transformers>=2.2.0", 
        "accelerate>=0.20.0"
    ]
    for dep in ai_deps:
        run_command([pip_path, "install", dep], f"Installing {dep.split('>=')[0]}", optional=True)

def create_enhanced_directories():
    """Create enhanced directory structure"""
    print("📁 Creating enhanced directory structure...")
    
    directories = [
        "data/input", "data/output/uploads", "data/output/results",
        "data/output/similarity", "data/output/visualizations",
        "src/web/static/results", "logs", "config/mappings",
        "visualizations", "test_files", "models", "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {directory}")

def create_enhanced_config():
    """Create enhanced configuration files"""
    print("⚙️ Creating enhanced configuration files...")
    
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    mappings_dir = config_dir / "mappings"
    mappings_dir.mkdir(exist_ok=True)
    
    # Create mapping files
    mappings = {
        "pos_mapping.json": {
            "n": "Noun", "v": "Verb", "a": "Adjective", "d": "Adverb",
            "p": "Preposition", "c": "Conjunction", "u": "Auxiliary", "m": "Number",
            "q": "Quantifier", "r": "Pronoun", "t": "Time", "s": "Location"
        },
        "entity_mapping.json": {
            "PERSON": "Person", "LOCATION": "Location", "ORGANIZATION": "Organization",
            "TIME": "Time", "DATE": "Date", "MONEY": "Money"
        },
        "sentiment_mapping.json": {
            "positive": "Positive", "negative": "Negative", "neutral": "Neutral"
        }
    }
    
    for filename, mapping in mappings.items():
        filepath = mappings_dir / filename
        if not filepath.exists():
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(mapping, f, ensure_ascii=False, indent=2)
            print(f"   ✓ {filepath}")
    
    # Create dictionary files
    files_content = {
        "chinese_stopwords.txt": [
            "的", "了", "在", "是", "我", "有", "和", "就", "不", "人",
            "都", "一", "一個", "上", "也", "很", "到", "說", "要", "去"
        ],
        "positive_words.txt": [
            "好", "優秀", "棒", "讚", "喜歡", "滿意", "開心", "快樂",
            "美好", "完美", "成功", "順利", "幸福", "愉快", "舒服"
        ],
        "negative_words.txt": [
            "壞", "差", "糟糕", "失敗", "問題", "錯誤", "困難", "痛苦",
            "悲傷", "生氣", "憤怒", "討厭", "失望", "沮喪", "煩惱"
        ],
        "custom_dict.txt": [
            "# Custom Dictionary", "# Format: Word Frequency POS",
            "機器學習 100 n", "人工智能 200 n", "自然語言處理 150 n"
        ]
    }
    
    for filename, content in files_content.items():
        filepath = config_dir / filename
        if not filepath.exists():
            with open(filepath, 'w', encoding='utf-8') as f:
                for line in content:
                    f.write(line + '\n')
            print(f"   ✓ {filepath}")

def create_service_scripts():
    """Create service scripts for advanced features"""
    print("📜 Creating service scripts...")
    
    os_name = platform.system()
    
    # Redis startup script
    if os_name != "Windows":
        redis_script = Path("start_redis.sh")
        if not redis_script.exists():
            with open(redis_script, 'w') as f:
                f.write('''#!/bin/bash
echo "🚀 Starting Redis server..."
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis not installed, please install Redis first"
    exit 1
fi
redis-server &
echo "✅ Redis server started"
''')
            redis_script.chmod(0o755)
            print(f"   ✓ {redis_script}")
    
    # Celery Worker script
    if os_name == "Windows":
        celery_script = Path("start_celery.bat")
        content = '''@echo off
echo 🚀 Starting Celery Worker...
call venv\\Scripts\\activate
celery -A src.core.task_queue worker --loglevel=info
'''
    else:
        celery_script = Path("start_celery.sh")
        content = '''#!/bin/bash
echo "🚀 Starting Celery Worker..."
source venv/bin/activate
celery -A src.core.task_queue worker --loglevel=info
'''
    
    if not celery_script.exists():
        with open(celery_script, 'w') as f:
            f.write(content)
        if os_name != "Windows":
            celery_script.chmod(0o755)
        print(f"   ✓ {celery_script}")

def initialize_models(python_path):
    """Initialize language models"""
    print("🤖 Initializing language models...")
    
    # Initialize jieba
    init_script = '''
import jieba
jieba.cut("Test")
print("✅ jieba initialization completed")

try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    print("✅ Semantic model download completed")
except:
    print("⚠️ Semantic model download skipped")
'''
    
    run_command([python_path, "-c", init_script], "Initializing models", optional=True)

def show_enhanced_instructions():
    """Show enhanced usage instructions"""
    print("\n" + "="*80)
    print("🎉 Chinese Text Analyzer Enhanced Version Installation Complete!")
    print("="*80)
    
    os_name = platform.system()
    if os_name == "Windows":
        activate_cmd = "venv\\Scripts\\activate"
    else:
        activate_cmd = "source venv/bin/activate"
    
    print(f"\n📖 Basic Usage:")
    print(f"1. Activate environment: {activate_cmd}")
    print("2. Run Web version: python run_web.py")
    print("3. Run CLI version: python run_cli.py")
    print("4. Demo new features: python demo_new_features.py")
    
    print("\n🆕 New Features:")
    print("🔍 Text Similarity Analysis - Multi-text correlation comparison")
    print("📊 Advanced Visualization - Heatmaps, network graphs, interactive charts")
    print("⚙️ Task Queue System - Batch processing management")
    print("🚀 GPU Acceleration Support - Large text processing acceleration")
    print("📁 Multi-format Support - PDF, Word, web page parsing")
    
    print("\n🌐 Web Port:")
    print("Application now runs on: http://localhost:3000")
    print("(To modify port, check docs/README.md)")
    
    print("\n📚 Documentation:")
    print("📖 Complete documentation: docs/documentation.html")
    print("🔧 Port configuration: docs/README.md")
    
    print("\n💡 Advanced features require additional configuration:")
    print("🔥 GPU Acceleration: Requires CUDA and PyTorch GPU version")
    print("⚙️ Task Queue: Requires Redis server")
    print("📊 Interactive Visualization: Requires Plotly and NetworkX")

def setup():
    """Enhanced setup function"""
    print("🌟 Chinese Text Analyzer Enhanced Setup v2.0")
    print("🚀 New Features: Similarity Analysis, Advanced Visualization, Task Queue, GPU Acceleration")
    print("=" * 80)
    
    try:
        # 1. Create virtual environment
        pip_path, python_path = create_virtual_environment()
        if not pip_path:
            return
        
        # 2. Install basic dependencies
        install_basic_requirements(pip_path)
        
        # 3. Install enhanced feature dependencies
        install_enhanced_features(pip_path)
        
        # 4. Create enhanced directory structure
        create_enhanced_directories()
        
        # 5. Create enhanced configuration
        create_enhanced_config()
        
        # 6. Create service scripts
        create_service_scripts()
        
        # 7. Initialize models
        initialize_models(python_path)
        
        # 8. Show usage instructions
        show_enhanced_instructions()
        
        print(f"\n✅ Installation complete! Run {activate_cmd} immediately to start using")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during installation: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup() 