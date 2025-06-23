#!/bin/bash
echo "🚀 啟動 Redis 服務器..."
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis 未安裝，請先安裝Redis"
    exit 1
fi
redis-server &
echo "✅ Redis 服務器已啟動"
