"""Operaciones de alto nivel del sistema de archivos invocadas por la CLI/servicios."""

from __future__ import annotations
from dataclasses import dataclass

from .models import Directory, File, FileSystemEntity, User
from .permissions import PermissionSet


@dataclass
class FileSystemOps:
    """Implementa operaciones de archivos de alto nivel similares a POSIX."""

    root: Directory
    user: User
    cwd: Directory | None = None

    def __post_init__(self):
        if self.cwd is None:
            self.cwd = self.root

    # -------------------------
    # ls
    # -------------------------
    def ls(self, path: str | None = None) -> list[str]:
        target = self.cwd if path is None else self.resolve(path)
        if isinstance(target, Directory):
            return sorted(target.children.keys())
        return [target.name]

    # -------------------------
    # cd
    # -------------------------
    def cd(self, path: str) -> Directory:
        target = self.resolve(path)
        if not isinstance(target, Directory):
            raise NotADirectoryError(f"Not a directory: {path}")
        self.cwd = target
        return target

    # -------------------------
    # mkdir
    # -------------------------
    def mkdir(self, path: str) -> Directory:
        if path.startswith("/"):
            current = self.root
            components = [p for p in path.split("/") if p]
        else:
            current = self.cwd
            components = [p for p in path.split("/") if p]

        for comp in components:
            existing = current.get_child(comp)
            if existing is None:
                new_dir = Directory(
                    name=comp,
                    owner=self.user,
                    permissions=PermissionSet.from_string("rwx")
                )
                current.add_child(new_dir)
                current = new_dir
            else:
                if isinstance(existing, Directory):
                    current = existing
                else:
                    raise FileExistsError(f"File exists: {comp}")
        return current

    # -------------------------
    # touch
    # -------------------------
    def touch(self, path: str) -> File:
        parent_path, _, name = path.rstrip("/").rpartition("/")
        parent = (
            self.root if (path.startswith("/") and not parent_path)
            else self.resolve(parent_path) if parent_path
            else self.cwd
        )

        existing = parent.get_child(name)
        if existing and isinstance(existing, File):
            return existing

        if existing:
            raise IsADirectoryError(f"{path} is a directory")

        new_file = File(
            name=name,
            owner=self.user,
            permissions=PermissionSet.from_string("rw"),
            content=""
        )
        parent.add_child(new_file)
        return new_file

    # -------------------------
    # cat
    # -------------------------
    def cat(self, path: str) -> str:
        node = self.resolve(path)
        if not isinstance(node, File):
            raise IsADirectoryError(f"{path} is a directory")
        return node.content

    # -------------------------
    # write
    # -------------------------
    def write(self, path: str, content: str, *, append=False) -> File:
        parent_path, _, name = path.rstrip("/").rpartition("/")
        parent = (
            self.root if (path.startswith("/") and not parent_path)
            else self.resolve(parent_path) if parent_path
            else self.cwd
        )

        existing = parent.get_child(name)

        if existing is None:
            new_file = File(
                name=name,
                owner=self.user,
                permissions=PermissionSet.from_string("rw"),
                content=content
            )
            parent.add_child(new_file)
            return new_file

        if not isinstance(existing, File):
            raise IsADirectoryError(f"{path} is a directory")

        if append:
            existing.content += content
        else:
            existing.content = content

        return existing

    # -------------------------
    # rm
    # -------------------------
    def rm(self, path: str, *, recursive=False):
        node = self.resolve(path)

        if node.parent is None:
            raise PermissionError("Cannot remove root directory")

        if isinstance(node, Directory) and node.children and not recursive:
            raise IsADirectoryError("Directory not empty (use recursive=True)")

        node.parent.remove_child(node.name)

    # -------------------------
    # resolve
    # -------------------------
    def resolve(self, path: str) -> FileSystemEntity:
        if path in ("", "."):
            return self.cwd

        if path.startswith("/"):
            current = self.root
            components = [p for p in path.split("/") if p]
        else:
            current = self.cwd
            components = [p for p in path.split("/") if p]

        for comp in components:
            if comp == ".":
                continue
            if comp == "..":
                if current.parent:
                    current = current.parent
                continue

            if not isinstance(current, Directory):
                raise FileNotFoundError(f"Not a directory: {current.name}")

            child = current.get_child(comp)
            if child is None:
                raise FileNotFoundError(f"Path not found: {path}")

            current = child

        return current
