#!/bin/bash

# ERD Viewer Run Script

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: bash setup.sh"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if required packages are installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "❌ Dependencies not installed!"
    echo "Please run: bash setup.sh"
    exit 1
fi

echo "🚀 Starting ERD Viewer..."
echo ""
echo "📊 Open your browser to: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Run the Streamlit app
streamlit run app.py
