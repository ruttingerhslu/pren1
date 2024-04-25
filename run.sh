
#!/bin/bash

# Define the path to the virtual environment
VENV_PATH="venv/bin/activate"

# Define the path to your Python script
SCRIPT_PATH="/home/pren/workspace/pren1/cube_detection/cube_calculator.py"

# Activate the virtual environment
echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Install dependencies from the requirements file
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the Python script
echo "Running the script..."
python3 "$SCRIPT_PATH"

