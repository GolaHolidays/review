#!/bin/bash
set -e

cd "$(dirname "$0")"

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

echo "🚀 Starting review system..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
