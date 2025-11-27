#!/usr/bin/env python3
"""Demo script showcasing the enhanced CLI capabilities."""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def demo_scheduler():
    """Demonstrate scheduler functionality with real data."""
    print("🚀 TESTING ENHANCED SCHEDULER")
    print("=" * 60)
    
    algorithms = [
        ("fcfs", None),
        ("rr", 2),
        ("sjf", None)
    ]
    
    scenarios = [
        "data/examples/scenario1.csv",
        "data/examples/scenario2.json"
    ]
    
    for scenario in scenarios:
        print(f"\n📊 Testing with {scenario}:")
        print("-" * 40)
        
        for algo, quantum in algorithms:
            print(f"\n🔄 Algorithm: {algo.upper()}" + (f" (quantum={quantum})" if quantum else ""))
            
            cmd_parts = [
                "python", "-m", "adapters.cli.main", "sim",
                "--algo", algo,
                "--input", scenario
            ]
            
            if quantum:
                cmd_parts.extend(["--quantum", str(quantum)])
            
            cmd = " ".join(cmd_parts)
            print(f"Command: {cmd}")
            print()
            
            os.system(cmd)

def demo_filesystem():
    """Demonstrate enhanced filesystem functionality."""
    print("\n\n🗂️  TESTING ENHANCED FILESYSTEM")
    print("=" * 60)
    
    commands = [
        "python -m adapters.cli.main fs --user alice",
        # The commands below would be executed inside the fs shell:
        # pwd
        # mkdir documents projects
        # cd documents  
        # touch readme.txt notes.md
        # write readme.txt 'Welcome to the enhanced filesystem!'
        # write notes.md '# My Notes\\nThis filesystem now supports tree rendering!'
        # cat readme.txt
        # cd ..
        # tree
        # ls
    ]
    
    print("Enhanced filesystem features:")
    print("✅ pwd - Show current directory")
    print("✅ tree - Display directory tree structure")  
    print("✅ Enhanced shell prompt with current directory")
    print("✅ help command for assistance")
    print("✅ rm -r for recursive deletion")
    print()
    print("To test interactively, run:")
    print(f"  {commands[0]}")
    print()
    print("Then try these commands in the fs shell:")
    print("  help")
    print("  pwd")
    print("  mkdir docs")
    print("  cd docs")
    print("  touch readme.txt")
    print("  write readme.txt 'Hello World!'")
    print("  cat readme.txt")
    print("  cd ..")
    print("  tree")

def show_summary():
    """Show summary of new features."""
    print("\n\n🎉 ENHANCED FEATURES SUMMARY")
    print("=" * 60)
    
    print("\n📈 Scheduler Enhancements:")
    print("  ✅ Complete algorithm implementations (FCFS, RR, SJF)")
    print("  ✅ Real CSV/JSON data loading")
    print("  ✅ Detailed metrics display (per-process + aggregate)")
    print("  ✅ I/O blocking simulation")
    print("  ✅ Context switching tracking")
    print("  ✅ CPU utilization and throughput metrics")
    
    print("\n🗂️  Filesystem Enhancements:")
    print("  ✅ Complete POSIX-like operations")
    print("  ✅ Tree rendering with Unicode connectors")
    print("  ✅ Enhanced shell with pwd/tree commands")
    print("  ✅ Better error handling and help system")
    print("  ✅ Recursive directory removal")
    
    print("\n🖥️  GUI Available:")
    print("  ✅ PyWebview interface with Bootstrap UI")
    print("  ✅ Real-time scheduler simulation")
    print("  ✅ Interactive filesystem terminal")
    print("  ✅ To launch GUI: python -m adapters.gui_webview.run")
    
    print("\n📚 Available Commands:")
    print("  Scheduler: python -m adapters.cli.main sim --algo [fcfs|rr|sjf] --input <file>")
    print("  Filesystem: python -m adapters.cli.main fs --user <username>")
    print("  GUI: python -m adapters.gui_webview.run")

if __name__ == "__main__":
    print("🎯 ENHANCED CLI DEMONSTRATION")
    print("Project: CPU Scheduler + Virtual Filesystem")
    print("=" * 60)
    
    demo_scheduler()
    demo_filesystem()
    show_summary()