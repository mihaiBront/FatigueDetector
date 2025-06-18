#!/bin/bash

# Exit on error
set -e

# Add local bin to PATH
export PATH="$HOME/.local/bin:$PATH"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Verify requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found in $SCRIPT_DIR"
    exit 1
fi

echo "Updating package lists..."
sudo apt update
sudo apt upgrade -y

echo "Installing build dependencies..."
sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget libsqlite3-dev libbz2-dev

echo "Downloading and installing Python 3.9..."
cd /tmp
wget https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tgz
tar -xf Python-3.9.18.tgz
cd Python-3.9.18
./configure --enable-optimizations
make -j $(nproc)
sudo make altinstall

echo "Installing pip for Python 3.9..."
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3.9 get-pip.py

# Return to the project directory
cd "$SCRIPT_DIR"

echo "Installing system dependencies..."
sudo apt install -y bluetooth libbluetooth-dev pkg-config libboost-python-dev libboost-thread-dev build-essential

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