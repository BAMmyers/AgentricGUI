@echo off
:: Activate main virtual environment
call venv\Scripts\activate.bat

:: Start the server in the background (if server repo is specified)
if ""%AGENTRICGUI_SERVER_DIR%""=="" (
  start ""AgentricServer"" python AgentricGUI-Server\server.py
)

:: Run the main application
python main.py

pause
