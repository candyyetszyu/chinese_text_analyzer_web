#!/bin/bash
echo "🚀 啟動 Celery Worker..."
source venv/bin/activate
celery -A src.core.task_queue worker --loglevel=info
