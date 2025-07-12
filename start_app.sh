#!/bin/bash
# Script to start the Flask application for Linux/macOS

# Navigate to the directory where the script is located
cd "$(dirname "$0")"

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Starting Flask application..."
# Set FLASK_APP and run the app
export FLASK_APP=app.py
python app.py