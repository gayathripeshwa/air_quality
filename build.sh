#!/usr/bin/env bash

# Install pyenv to control Python version
curl https://pyenv.run | bash

export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Install and use Python 3.11
PYTHON_VERSION=3.11.8
pyenv install -s $PYTHON_VERSION
pyenv global $PYTHON_VERSION

# Upgrade pip and install dependencies
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
