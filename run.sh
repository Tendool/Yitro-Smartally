#!/bin/bash

# SmartAlly Quick Start Script
# This script sets up and runs the SmartAlly application

echo "🤖 SmartAlly - Rule-Based Document Data Extractor"
echo "=================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip is not installed."
    echo "Please install pip and try again."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Error installing dependencies"
    exit 1
fi

echo ""
echo "🚀 Starting SmartAlly..."
echo ""
echo "The application will open in your browser at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application."
echo ""

# Run Streamlit
streamlit run smartally.py
