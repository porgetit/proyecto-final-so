# Proyecto – Sistema de Archivos Virtual (core/fs)

Este módulo implementa un sistema de archivos virtual simplificado, con operaciones tipo POSIX y un renderizador de árbol similar al comando `tree`.

## Archivos implementados en este trabajo

Como parte del proyecto final, se completaron **dos archivos principales**:

### ✔ `tree_renderer.py`
Implementa la función:
- `render_tree(root: Directory) -> str`

La función realiza:
- Recorrido DFS del árbol de directorios.
- Uso de conectores Unicode (`├──`, `└──`, `│`) para representar niveles.
- Directorios terminan en `/`.
- Archivos no llevan `/`.

### ✔ `ops.py`
Implementa todas las operaciones del sistema de archivos:
- `ls(path)`
- `cd(path)`
- `mkdir(path)` (comportamiento tipo `mkdir -p`)
- `touch(path)`
- `cat(path)`
- `write(path, content, append=False)`
- `rm(path, recursive=False)`
- `resolve(path)`

Incluye soporte para:
- Rutas absolutas `/`
- Rutas relativas
- `.` y `..`
- Creación automática de directorios padres
- Escritura y lectura de archivos
- Eliminación recursiva

## 📁 Estructura del sistema de archivos

El modelo está definido en `models.py`:
- `Directory`
- `File`
- `FileSystemEntity`
- `User`

Los permisos se manejan con `PermissionSet` desde `permissions.py`.

## 📌 Ejemplos de uso

```python
from core.fs.models import Directory, User
from core.fs.permissions import PermissionSet
from core.fs.ops import FileSystemOps
from core.fs.tree_renderer import render_tree

user = User(username="alice", home="/home/alice")
root = Directory(name="", owner=user, permissions=PermissionSet.from_string("rwx"))
fs = FileSystemOps(root=root, user=user)

# Crear directorios y archivos
fs.mkdir("/home/alice")
fs.mkdir("projects")
fs.write("/home/alice/readme.txt", "Hello Alice")
fs.write("projects/todo.txt", "1. terminar proyecto")

print(render_tree(root))
print(fs.ls("/home/alice"))
print(fs.cat("/home/alice/readme.txt"))

# Borrado
fs.rm("projects", recursive=True)

Ejemplo de salida de render_tree:
/
├── home/
│   └── alice/
│       └── readme.txt
└── projects/
    ├── todo.txt
    └── subdir/
        └── empty.md
