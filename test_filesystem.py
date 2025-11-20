#!/usr/bin/env python3
"""Test filesystem functionality"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.fs.models import Directory, User
from core.fs.permissions import PermissionSet
from core.services import FsService

def test_filesystem():
    """Test basic filesystem operations"""
    print("Testing Virtual Filesystem")
    print("=" * 50)
    
    # Create user and root directory
    user = User(username="testuser")
    root = Directory(
        name="",
        owner=user,
        permissions=PermissionSet.from_string("rwx")
    )
    
    # Create service
    fs_service = FsService(root=root, user=user)
    
    # Test commands
    commands = [
        ("pwd", []),
        ("ls", []),
        ("mkdir", ["documents"]),
        ("ls", []),
        ("cd", ["documents"]),
        ("pwd", []),
        ("touch", ["readme.txt"]),
        ("write", ["readme.txt", "Hello, World!"]),
        ("cat", ["readme.txt"]),
        ("ls", []),
        ("cd", [".."]),
        ("tree", []),
        ("rm", ["documents/readme.txt"]),
        ("tree", []),
    ]
    
    for cmd, args in commands:
        try:
            print(f"\n> {cmd} {' '.join(args)}")
            result = fs_service.execute(cmd, args)
            if result:
                print(result)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_filesystem()