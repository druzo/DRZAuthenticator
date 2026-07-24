#!/bin/bash

# DEV ONLY — use install.sh for end-user install
# Setup script for TOTP Application
# Install required dependencies

echo "Installing required Python packages..."

# Install required packages with --break-system-packages flag
pip3 install pyotp rich --break-system-packages

echo "Setup complete!"
echo "You can now run the application with: python3 src/main.py"