#!/bin/bash

# Default environment
environment="local.env"

# Parse command-line options
while getopts "e:" flag
do
    case "${flag}" in
        e) environment=${OPTARG};;
    esac
done

echo "Using environment: $environment"

# Load Environment variables
set -a
source "$environment"
set +a

# Activate the virtual environment
echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Install dependencies from the requirements file
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the Python script
echo "Running the script..."
python3 "$SCRIPT_PATH"
