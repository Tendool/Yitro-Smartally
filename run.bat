@echo off
REM SmartAlly Quick Start Script for Windows
REM This script sets up and runs the SmartAlly application

echo ============================================
echo SmartAlly - Document Data Extractor
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed.
    echo Please install Python 3.8 or higher and try again.
    pause
    exit /b 1
)

echo Python found.
echo.

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

if errorlevel 1 (
    echo Error installing dependencies
    pause
    exit /b 1
)

echo Dependencies installed successfully
echo.
echo Starting SmartAlly...
echo.
echo The application will open in your browser at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the application.
echo.

REM Run Streamlit
streamlit run smartally.py

pause
