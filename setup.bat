@echo off
echo Setting up AgentricGUI...

:: Check if Git is installed
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo Git is not installed. Please install Git from https://git-scm.com/downloads
    pause
    exit /b 1
)

:: Clone the repository (if the directory doesn't already exist)
if not exist AgentricGUI (
    echo Cloning the repository...
    git clone https://github.com/BAMmyers/AgentricGUI.git
)

:: Navigate to the directory
cd AgentricGUI

:: Check if Python is installed
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3 from https://www.python.org/downloads
    pause
    exit /b 1
)

:: Create a virtual environment (if it doesn't already exist)
if not exist venv (
    echo Creating a virtual environment...
    python -m venv venv
)

:: Activate the virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

:: Create settings file if it does not exist
if not exist settings.json (
echo {
    "api_key": "",
        "experience_level": "Novice",
            "installation_id": ""
} > settings.json
)

:: Install Server Requirements

if not exist AgentricGUI-Server\venv (
    echo Creating a virtual environment...
    python -m venv AgentricGUI-Server\venv
)

:: Activate the virtual environment
echo Activating virtual environment...
call AgentricGUI-Server\venv\Scripts\activate.bat

:: Install dependencies
echo Installing dependencies...
pip install -r AgentricGUI-Server/requirements.txt
:: Run the Server (in the background)
echo Starting server...
start "AgentricServer" python AgentricGUI-Server\server.py

:: Inform the user
echo Setup complete. You can now run the application by running:
echo   python main.py
echo The Server has also been started in the background.

pause