#!/bin/bash

# Exit on error
set -e

echo "Updating package lists..."
sudo apt update

echo "Installing system dependencies..."
while read -r package; do
    echo "Installing $package..."
    sudo apt install -y "$package"
done < system_requirements.txt

echo "Setting up Python virtual environment..."
# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python3.11 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing Python packages..."
pip install -r requirements.txt

echo "Setup complete!" 