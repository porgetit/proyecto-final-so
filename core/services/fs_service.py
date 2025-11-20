"""Service facade for filesystem operations."""

from __future__ import annotations

from typing import Iterable, Mapping

from ..fs.models import Directory, User
from ..fs.ops import FileSystemOps


class FsService:
    """Dispatches CLI commands to the filesystem domain layer."""

    def __init__(self, root: Directory, user: User) -> None:
        self.ops = FileSystemOps(root=root, user=user)
        self._command_map: Mapping[str, str] = {
            "ls": "ls",
            "cd": "cd",
            "pwd": "pwd",
            "mkdir": "mkdir",
            "touch": "touch",
            "cat": "cat",
            "write": "write",
            "rm": "rm",
            "tree": "tree",
        }

    def execute(self, command: str, args: Iterable[str]) -> str:
        """
        Execute a filesystem command and return a user-facing string.

        # TODO: Implement richer argument parsing and error handling.
        """
        normalized = command.lower()
        handler_name = self._command_map.get(normalized)
        if handler_name is None:
            raise ValueError(f"Command '{command}' is not supported.")

        handler = getattr(self.ops, handler_name)
        result = handler(*args)
        if result is None:
            return ""
        if isinstance(result, list):
            return "\n".join(map(str, result))
        return str(result)
