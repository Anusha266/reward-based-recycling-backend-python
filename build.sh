#!/bin/bash
set -eux  # Exit on error, print commands

# Install system dependencies
apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev

# Upgrade pip and install Python packages
pip install --upgrade pip
pip install -r requirements.txt