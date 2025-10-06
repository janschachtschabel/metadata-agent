@echo off
REM Windows start script for metadata agent

echo ========================================
echo   Metadaten-Extraktion Agent
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [!] Virtual environment not found
    echo [*] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
echo [*] Checking dependencies...
python -c "import gradio" 2>nul
if errorlevel 1 (
    echo [!] Dependencies not installed
    echo [*] Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check for .env file
if not exist ".env" (
    echo.
    echo [!] .env file not found
    echo [*] Please create .env file with your OpenAI API key
    echo [*] Example: copy .env.example .env
    echo.
    pause
    exit /b 1
)

REM Start the application
echo.
echo [*] Starting Gradio UI...
echo [*] Open browser: http://127.0.0.1:7860
echo.
python app.py

pause
