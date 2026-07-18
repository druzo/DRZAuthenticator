#!/usr/bin/env python3
"""
TOTP (Time-based One-Time Password) Application
A command-line tool for managing TOTP authentication keys and viewing dynamic passwords.
"""

import sys
import os
import argparse

# Add src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from totp_app import TOTPApp

def main():
    """Main entry point for the TOTP application."""
    parser = argparse.ArgumentParser(description="DRZ Authenticator")
    parser.add_argument("--password", help="Master password (for scripting)")
    
    args = parser.parse_args()
    
    try:
        app = TOTPApp(password=args.password)
        app.run()
    except KeyboardInterrupt:
        print("\n\n[yellow]Application interrupted by user.[/yellow]")
    except Exception as e:
        print(f"[red]An unexpected error occurred: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()