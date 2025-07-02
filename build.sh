#!/usr/bin/env bash

# Set Python version
PYTHON_VERSION=3.11.8

# Install pyenv and Python
curl https://pyenv.run | bash

export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

pyenv install -s $PYTHON_VERSION
pyenv global $PYTHON_VERSION

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# ✅ Verify streamlit is installed and callable
echo "Checking streamlit..."
which streamlit
streamlit --version
