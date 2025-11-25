#!/usr/bin/env python3
"""
Demo script for the CLI functionality.
This script demonstrates how to use both the scheduler simulator and filesystem.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root)) #Add this directory to the path to allow importing modules of the project

from adapters.cli.main import main


def run_scheduler_demos():
    """Demonstrate scheduler functionality."""
    print("=" * 80)
    print("SCHEDULER SIMULATION DEMOS")
    print("=" * 80)
    
    examples_dir = project_root / "data" / "examples"
    
    # Demo 1: FCFS with scenario1.csv
    print("\n1. Running FCFS algorithm with scenario1.csv...")
    try:
        exit_code = main(['sim', '--algo', 'fcfs', '--input', str(examples_dir / 'scenario1.csv')])
        if exit_code != 0:
            print("FCFS simulation failed!")
    except Exception as e:
        print(f"Error running FCFS: {e}")
    
    # Demo 2: Round Robin with scenario2.json
    print("\n2. Running Round Robin (quantum=3) with scenario2.json...")
    try:
        exit_code = main(['sim', '--algo', 'rr', '--quantum', '3', '--input', str(examples_dir / 'scenario2.json')])
        if exit_code != 0:
            print("Round Robin simulation failed!")
    except Exception as e:
        print(f"Error running Round Robin: {e}")
    
    # Demo 3: SJF with scenario3.csv
    print("\n3. Running SJF algorithm with scenario3.csv...")
    try:
        exit_code = main(['sim', '--algo', 'sjf', '--input', str(examples_dir / 'scenario3.csv')])
        if exit_code != 0:
            print("SJF simulation failed!")
    except Exception as e:
        print(f"Error running SJF: {e}")


def print_filesystem_demo():
    """Print instructions for filesystem demo."""
    print("\n" + "=" * 80)
    print("FILESYSTEM DEMO INSTRUCTIONS")
    print("=" * 80)
    print("To test the filesystem functionality, run:")
    print(f"python {project_root}/adapters/cli/main.py fs --user testuser")
    print("\nOnce in the filesystem shell, try these commands:")
    print("  pwd                    # Show current directory")
    print("  ls                     # List contents")
    print("  mkdir documents        # Create directory")
    print("  cd documents          # Change directory")
    print("  touch readme.txt      # Create file")
    print("  write readme.txt 'Hello World!'  # Write to file")
    print("  cat readme.txt        # Read file")
    print("  tree                  # Show directory tree")
    print("  cd ..                 # Go back")
    print("  rm documents/readme.txt # Remove file")
    print("  help                  # Show help")
    print("  exit                  # Exit shell")


if __name__ == "__main__":
    print("CLI Demo for Process Scheduler + Virtual Filesystem")
    print("Note: The scheduler algorithms are not yet fully implemented.")
    print("This demo shows the CLI interface and data loading capabilities.")
    
    run_scheduler_demos()
    print_filesystem_demo()