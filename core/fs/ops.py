"""High level filesystem operations invoked by the CLI/services."""

from __future__ import annotations

from dataclasses import dataclass

from .models import Directory, File, FileSystemEntity, User


@dataclass
class FileSystemOps:
    """Stateful helper that exposes POSIX-like commands."""

    root: Directory
    user: User
    cwd: Directory | None = None

    def __post_init__(self) -> None:
        if self.cwd is None:
            self.cwd = self.root

    def ls(self, path: str | None = None) -> list[str]:
        """List the contents of the given path."""
        # TODO: Implement ls command logic.
        raise NotImplementedError

    def cd(self, path: str) -> Directory:
        """Change current directory."""
        # TODO: Implement path resolution and permission checks.
        raise NotImplementedError

    def mkdir(self, path: str) -> Directory:
        """Create a directory."""
        # TODO: Implement mkdir logic.
        raise NotImplementedError

    def touch(self, path: str) -> File:
        """Create an empty file or update its timestamps."""
        # TODO: Implement touch logic.
        raise NotImplementedError

    def cat(self, path: str) -> str:
        """Return the contents of a file."""
        # TODO: Implement cat logic.
        raise NotImplementedError

    def write(self, path: str, content: str, *, append: bool = False) -> File:
        """Write content to a file."""
        # TODO: Implement write logic.
        raise NotImplementedError

    def rm(self, path: str, *, recursive: bool = False) -> None:
        """Remove a file or directory."""
        # TODO: Implement rm logic.
        raise NotImplementedError

    def resolve(self, path: str) -> FileSystemEntity:
        """Resolve an absolute or relative path to an entity."""
        # TODO: Implement path resolution.
        raise NotImplementedError
