#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Check that Streamlit is installed and callable
echo "✅ Streamlit path: $(which streamlit)"
echo "✅ Streamlit version:"
streamlit --version
