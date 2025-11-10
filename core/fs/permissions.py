"""Unix-like permission helpers for the virtual filesystem."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Set


class Permission(str, Enum):
    """Supported rwx permission flags."""

    READ = "r"
    WRITE = "w"
    EXECUTE = "x"


@dataclass
class PermissionSet:
    """Simple permission set focused on the owner user."""

    owner: Set[Permission] = field(default_factory=set)

    @classmethod
    def from_string(cls, spec: str) -> "PermissionSet":
        """Parse a string like 'rw' or 'rwx'."""
        return cls(owner={Permission(char) for char in spec})

    def allows(self, permission: Permission) -> bool:
        """Return True when the granted permissions include the requested one."""
        return permission in self.owner

    def to_string(self) -> str:
        """Serialize the permission set back to its string representation."""
        granted = "".join(permission.value for permission in sorted(self.owner, key=str))
        return granted or "-"
