@echo off
REM Quick Start Script for University Chatbot (Windows)
REM Run this batch file to set up and start the chatbot

setlocal enabledelayedexpansion

echo ================================
echo University Chatbot - Quick Start
echo ================================
echo.

REM Check Python version
echo Checking Python version...
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip > nul 2>&1
pip install -q -r requirements.txt
echo Dependencies installed
echo.

REM Initialize setup
echo Initializing chatbot...
python init_setup.py
echo.

REM Start chatbot
echo ================================
echo Setup complete!
echo ================================
echo.
echo Starting Streamlit app...
echo The chatbot will open in your browser at: http://localhost:8501
echo.
echo To stop: Press Ctrl+C
echo.

streamlit run app.py

endlocal
