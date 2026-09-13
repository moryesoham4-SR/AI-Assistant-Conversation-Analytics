@echo off
title AI Assistant Conversation Analytics - GUI Launcher
echo ============================================================
echo AI ASSISTANT CONVERSATION ANALYTICS - GUI LAUNCHER
echo Course: B.Sc. Data Science (Sem 5) - Data Engineering
echo ============================================================
echo.

cd /d "%~dp0"

REM Activate virtual environment if available
if exist venv\Scripts\activate.bat (
    echo Activating Python Virtual Environment...
    call venv\Scripts\activate.bat
)

REM Verify streamlit is installed
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Streamlit and dependencies...
    pip install streamlit pandas matplotlib seaborn
)

echo.
echo Launching GUI in browser...
echo.
streamlit run app.py
pause
