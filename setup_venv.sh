#!/bin/bash
# Create virtual environment and install requirements
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
