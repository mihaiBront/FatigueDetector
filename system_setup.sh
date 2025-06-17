#!/bin/bash

# Exit on error
set -e

echo "Updating package lists..."
sudo apt update

echo "Installing system dependencies..."
echo "Installing python 3.9"
sudo apt install -y python3.9
sudo apt install -y python3.9-venv python3.9-dev python3.9-distutils
while read -r package; do
    echo "Installing $package..."
    sudo apt install -y "$package"
done < system_requirements.txt

echo "Setting up Python virtual environment..."
# Remove existing virtual environment if it's incomplete
if [ -d ".venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf .venv
fi

# Create virtual environment
echo "Creating new virtual environment..."
python3.9 -m venv .venv

# Check if virtual environment was created successfully
if [ ! -f ".venv/bin/activate" ]; then
    echo "Error: Virtual environment creation failed!"
    exit 1
fi

# Use virtual environment binaries directly instead of sourcing activate
echo "Using virtual environment..."
VENV_PYTHON=".venv/bin/python"
VENV_PIP=".venv/bin/pip"

# Verify virtual environment is working
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment Python not found!"
    exit 1
fi

echo "Upgrading pip..."
"$VENV_PIP" install --upgrade pip

echo "Installing Python packages..."
"$VENV_PIP" install -r requirements.txt

echo "Installing PyBluez..."
"$VENV_PIP" install git+https://github.com/pybluez/pybluez.git

echo "Setup complete!" 