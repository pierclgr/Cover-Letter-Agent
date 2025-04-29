#!/bin/bash

# Shell script to download and install Ollama, pull the llama3.2:3b model,
# and set up a Python virtual environment

# Set up error handling
set -e

echo "===== Starting Agent Installation and Setup ====="

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check for Python
if ! command_exists python3; then
    echo "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "Warning: requirements.txt not found in the current directory."
    echo "Will create a virtual environment but cannot install requirements."
    SKIP_REQUIREMENTS=true
else
    SKIP_REQUIREMENTS=false
fi

# Install Ollama based on the operating system
echo "Step 1: Installing Ollama..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux system. Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS system. Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Unsupported operating system: $OSTYPE"
    echo "Ollama supports Linux and macOS. For Windows, please refer to Ollama documentation."
    exit 1
fi

# Verify Ollama installation
if ! command_exists ollama; then
    echo "Ollama installation failed. Please check for any errors above."
    exit 1
fi

echo "Ollama installed successfully!"

# Start Ollama service in the background
echo "Step 2: Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama service to start
echo "Waiting for Ollama service to initialize..."
sleep 10

# Pull the llama3.2:3b model
echo "Step 3: Pulling the llama3.2:3b model..."
ollama pull llama3.2:3b

# Check if model was installed successfully
if [ $? -ne 0 ]; then
    echo "Failed to pull the llama3.2:3b model."
    # Kill the Ollama service process if it's still running
    kill $OLLAMA_PID 2>/dev/null || true
    exit 1
fi

echo "llama3.2:3b model has been successfully pulled!"

# Set up Python virtual environment
echo "Step 4: Setting up Python virtual environment..."

# Create a virtual environment
VENV_NAME="venv"
python3 -m venv $VENV_NAME

if [ ! -d "$VENV_NAME" ]; then
    echo "Failed to create virtual environment."
    # Kill the Ollama service process if it's still running
    kill $OLLAMA_PID 2>/dev/null || true
    exit 1
fi

echo "Virtual environment '$VENV_NAME' created."

# Activate the virtual environment and install requirements
if [ "$SKIP_REQUIREMENTS" = false ]; then
    echo "Installing requirements from requirements.txt..."
    source $VENV_NAME/bin/activate
    pip install -r requirements.txt

    if [ $? -ne 0 ]; then
        echo "Failed to install requirements."
        deactivate
        # Kill the Ollama service process if it's still running
        kill $OLLAMA_PID 2>/dev/null || true
        exit 1
    fi

    echo "Requirements installed successfully!"
    deactivate
fi

# Stop Ollama
kill $OLLAMA_PID

echo "===== Setup Complete! ====="


# If you want to keep the script running until Ollama is manually stopped,
# uncomment the following line:
# wait $OLLAMA_PID