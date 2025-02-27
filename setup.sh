#!/bin/bash

echo "Setting up AgentricGUI..."

# Check if Git is installed
if ! command -v git &> /dev/null
then
    echo "Git is not installed. Please install Git."
    exit 1
fi

# Clone the repository (if the directory doesn't already exist)
if [ ! -d "AgentricGUI" ]; then
    echo "Cloning the repository..."
    git clone https://github.com/BAMmyers/AgentricGUI.git
fi

# Navigate to the directory
cd AgentricGUI

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python 3 is not installed. Please install Python 3."
    exit 1
fi

# Create a virtual environment (if it doesn't already exist)
if [ ! -d "venv" ]; then
    echo "Creating a virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create settings file if it does not exist
if [ ! -f "settings.json" ]; then
    echo '{
        "api_key": "",
        "experience_level": "Novice",
        "installation_id": ""
    }' > settings.json
fi
# Install Server Requirements

if [ ! -d "AgentricGUI-Server/venv" ]; then
    echo "Creating a virtual environment..."
    python3 -m venv AgentricGUI-Server/venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source AgentricGUI-Server/venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r AgentricGUI-Server/requirements.txt

# Run the Server (in the background)
echo "Starting server..."
python3 AgentricGUI-Server/server.py &

# Inform the user
echo "Setup complete. You can now run the application by running:"
echo "  python main.py"
echo "The server has also been started."

read -p "Press Enter to continue..."