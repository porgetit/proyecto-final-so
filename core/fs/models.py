"""Domain models for the virtual filesystem."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from .permissions import PermissionSet


@dataclass(slots=True)
class User:
    """Represents a user interacting with the virtual filesystem."""

    username: str
    home: str = "/"


@dataclass
class FileSystemEntity:
    """Base node shared by files and directories."""

    name: str
    owner: User
    permissions: PermissionSet
    parent: "Directory | None" = None

    def path(self) -> str:
        """Return the absolute path for this entity."""
        if self.parent is None:
            return "/"
        if self.parent.parent is None:
            return f"/{self.name}"
        return f"{self.parent.path().rstrip('/')}/{self.name}"


@dataclass
class File(FileSystemEntity):
    """Represents a file with textual content."""

    content: str = ""


@dataclass
class Directory(FileSystemEntity):
    """Represents a directory node in the tree."""

    children: Dict[str, FileSystemEntity] = field(default_factory=dict)

    def add_child(self, node: FileSystemEntity) -> None:
        """Attach a new node to the directory."""
        self.children[node.name] = node
        node.parent = self

    def get_child(self, name: str) -> Optional[FileSystemEntity]:
        """Return the child node by name."""
        return self.children.get(name)

    def remove_child(self, name: str) -> Optional[FileSystemEntity]:
        """Remove and return the child node."""
        return self.children.pop(name, None)
