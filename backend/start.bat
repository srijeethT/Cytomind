@echo off
echo Starting Cytomind ML Backend...
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt -q
echo.

REM Start the server
echo Starting FastAPI server on http://127.0.0.1:8000
echo Press Ctrl+C to stop
echo.
python main.py
