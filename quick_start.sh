#!/bin/bash
# Quick Start Script for University Chatbot
# Run this script to set up and start the chatbot

set -e  # Exit on error

echo "================================"
echo "University Chatbot - Quick Start"
echo "================================"
echo ""

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "  Python version: $python_version"

# Create virtual environment
echo "✓ Creating virtual environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "  Virtual environment created"
else
    echo "  Virtual environment already exists"
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || . venv/bin/activate

# Install dependencies
echo "✓ Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "  Dependencies installed"

# Initialize setup
echo "✓ Initializing chatbot..."
python init_setup.py

# Start chatbot
echo ""
echo "================================"
echo "✅ Setup complete!"
echo "================================"
echo ""
echo "Starting Streamlit app..."
echo "The chatbot will open in your browser at: http://localhost:8501"
echo ""
echo "To stop: Press Ctrl+C"
echo ""

streamlit run app.py

exit 0
