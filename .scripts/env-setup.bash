#!/bin/bash
echo off
# Name of the directory to check
VENV_DIR="./.venv" # Replace 'venv' with your specific virtual environment folder name if different.
PYTHON_VERSION=""

# Check if the virtual environment exists
if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/pyvenv.cfg" ]; then
    echo "Virtual environment found in $VENV_DIR."
else
    echo "No virtual environment found in $VENV_DIR, creating environment"
    python -m venv .venv
    echo 'Virtual environment created'
fi

echo "Activating the virtual environment..."
. $VENV_DIR/bin/activate

# Install necessary dependencies
if [ -f "requirements.txt" ]; then
  echo "Installing dependencies from requirements.txt..."
  pip install -U pip
  pip install -r requirements.txt
else
  echo "requirements.txt not found. Skipping installation."
fi
