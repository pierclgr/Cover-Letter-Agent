#!/bin/bash

# Shell script to run Ollama with llama3.2:3b and execute main.py in a virtual environment

# Set up error handling
set -e

# Default virtual environment name
VENV_NAME="venv"

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check if Ollama is installed
if ! command_exists ollama; then
    echo "Error: Ollama is not installed. Please run the installation script first."
    exit 1
fi

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found in the current directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$VENV_NAME" ]; then
    echo "Error: Virtual environment '$VENV_NAME' not found."
    echo "Please run the installation script first or specify the correct virtual environment."
    exit 1
fi

echo "===== Starting Agent Application ====="

# Start Ollama service in the background
echo "Step 1: Starting Ollama service..."
# Check if Ollama is already running
if pgrep -x "ollama" > /dev/null; then
    echo "Ollama is already running."
else
    ollama serve &
    OLLAMA_PID=$!
    # Wait for Ollama service to initialize
    echo "Waiting for Ollama service to initialize..."
    sleep 5
fi

# Check if the model is already pulled
echo "Step 2: Checking llama3.2:3b model..."
if ollama list | grep -q "llama3.2:3b"; then
    echo "Model llama3.2:3b is already available."
else
    echo "Model llama3.2:3b not found. Pulling now..."
    ollama pull llama3.2:3b

    if [ $? -ne 0 ]; then
        echo "Failed to pull the llama3.2:3b model."
        # Kill the Ollama service process if we started it
        if [ -n "$OLLAMA_PID" ]; then
            kill $OLLAMA_PID 2>/dev/null || true
        fi
        exit 1
    fi

    echo "llama3.2:3b model has been successfully pulled!"
fi

# Run main.py using the virtual environment
echo "Step 3: Running main.py in the virtual environment..."
source "$VENV_NAME/bin/activate"

if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    # Kill the Ollama service process if we started it
    if [ -n "$OLLAMA_PID" ]; then
        kill $OLLAMA_PID 2>/dev/null || true
    fi
    exit 1
fi

echo "Virtual environment activated. Running main.py..."
python main.py

# Capture the exit code of the Python script
PYTHON_EXIT_CODE=$?

# Deactivate the virtual environment
deactivate

# Check if the Python script executed successfully
if [ $PYTHON_EXIT_CODE -ne 0 ]; then
    echo "main.py exited with error code: $PYTHON_EXIT_CODE"
else
    echo "main.py executed successfully."
fi

echo "===== Application Execution Complete ====="

# If we started Ollama in this script, ask if the user wants to keep it running
if [ -n "$OLLAMA_PID" ]; then
    echo "Stopping Ollama service..."
    kill $OLLAMA_PID
    echo "Ollama service stopped."
fi

exit $PYTHON_EXIT_CODE