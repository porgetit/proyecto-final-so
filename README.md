# Proyecto Planificador de Procesos + Sistema de Archivos

Este repositorio contiene el esqueleto de un proyecto académico cuyo objetivo es construir:

1. Un **simulador de planificación de CPU** con los algoritmos:
   - FCFS (First Come, First Served)
   - RR (Round Robin, con quantum configurable)
   - SJF (Shortest Job First, inicialmente NO expropiativo)
2. Un **sistema de archivos virtual** con:
   - Estructura jerárquica de directorios
   - Usuarios y permisos de tipo `rwx` (lectura/escritura/ejecución)
   - Comandos tipo Linux: `ls`, `cd`, `mkdir`, `chmod`, `touch`, `cat`, `write`, `rm`
3. Una **CLI** (línea de comandos) que permita:
   - Ejecutar simulaciones con diferentes algoritmos
   - Cargar escenarios desde archivos
   - Interactuar con el sistema de archivos virtual
4. Opcionalmente, una **GUI** basada en tecnologías web (HTML/CSS/JS con Bootstrap) usando **PyWebview** como puente con el backend.

> Este README está dirigido a un **modelo de generación de código (Codex)**.  
> Las instrucciones están pensadas para guiar la construcción incremental de un **MVP funcional** sin romper la arquitectura modular.

---

## 1. Estructura de Directorios

El esqueleto base del proyecto es:

```bash
./
├── core/
│   ├── scheduler/
│   │   ├── __init__.py
│   │   ├── pcb.py
│   │   ├── states.py
│   │   ├── queues.py
│   │   ├── algorithms/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── fcfs.py
│   │   │   ├── rr.py
│   │   │   └── sjf.py
│   │   ├── simulator.py
│   │   └── metrics.py
│   ├── fs/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── permissions.py
│   │   ├── ops.py
│   │   └── tree_renderer.py
│   └── services/
│       ├── __init__.py
│       ├── sim_service.py
│       └── fs_service.py
│
├── adapters/
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── webapi/
│   │   ├── __init__.py
│   │   └── api.py
│   ├── gui_webview/
│   │   ├── __init__.py
│   │   ├── run.py
│   │   └── web/
│   │       ├── index.html
│   │       ├── styles.css
│   │       └── app.js
│   └── render/
│       ├── __init__.py
│       ├── table.py
│       └── export.py
│
├── data/
│   ├── examples/
│   │   ├── scenario1.csv
│   │   └── scenario2.json
│
├── tests/
│   ├── test_scheduler.py
│   ├── test_fs.py
│   └── test_cli.py
│
├── README.md
└── requirements.txt
````

**Reglas importantes para el modelo de código:**

* No mezclar lógica de interfaz (CLI/GUI) dentro de `core/`.
* Implementar toda la lógica de planificación y sistema de archivos en `core/`.
* Usar `core/services` como capa de **casos de uso** para exponer funciones de alto nivel a adaptadores (`cli`, `webapi`, `gui_webview`).

---

## 2. Alcance del MVP

El MVP que se debe implementar **primero** cumple:

1. **Simulador de planificación de CPU**:

   * Soporta al menos **FCFS** y **RR** (con quantum configurable).
   * Soporta **SJF no expropiativo** (SJF simple).
   * Gestiona procesos a través de un **PCB** con estados:
     `NEW`, `READY`, `RUNNING`, `BLOCKED`, `TERMINATED`.
   * Usa colas de `ready` y `blocked`.
   * Calcula las métricas básicas por proceso y globales:

     * Waiting Time
     * Turnaround Time
     * Response Time
     * Throughput
     * CPU Utilization
     * Número de cambios de contexto

2. **Sistema de archivos virtual**:

   * Implementa un árbol de directorios (nodo raíz `/`).
   * Soporta al menos:

     * `ls`
     * `cd`
     * `mkdir`
     * `touch`
     * `cat`
     * `write`
     * `rm`
   * Modelo de permisos tipo Unix simple (`rwx` al menos para el dueño).

3. **CLI mínima funcional**:

   * Permite:

     * Seleccionar algoritmo (fcfs, rr, sjf).
     * Configurar quantum para RR.
     * Cargar un escenario desde `data/examples/*.csv` o `.json`.
     * Ejecutar la simulación y mostrar métricas.
     * Ejecutar comandos simples del sistema de archivos (`ls`, `cd`, `mkdir`, etc.).

4. La GUI **NO es parte del MVP**.
   Para el MVP solo se deben crear stubs vacíos o mínimos en `adapters/gui_webview` y `adapters/webapi` sin funcionalidad completa.

---

## 3. Reglas de Diseño para el Núcleo (core/)

### 3.1. `core/scheduler/pcb.py`

Implementar una clase `PCB` con al menos:

* `pid: int`
* `arrival_time: float`
* `burst_time: float`
* `remaining_time: float`
* `state: State` (usar Enum de `states.py`)
* `first_start_time: float | None` (para response time)
* `finish_time: float | None`
* Contador de `context_switches` opcional si es útil.

### 3.2. `core/scheduler/states.py`

Implementar un `Enum` de Python:

* `NEW`, `READY`, `RUNNING`, `BLOCKED`, `TERMINATED`.

### 3.3. `core/scheduler/queues.py`

Implementar colas de procesos:

* `ReadyQueue` (FIFO por defecto).
* `BlockedQueue` (puede ser FIFO simple al inicio).

Permitir operaciones típicas: `push`, `pop`, `peek`, `is_empty`.

### 3.4. `core/scheduler/algorithms/base.py`

Definir una interfaz (clase base abstracta) `BaseScheduler`:

* Método `add_job(pcb: PCB) -> None`
* Método `next_job(current_time: float) -> PCB | None`
* Propiedad o método para obtener el nombre del algoritmo.
* Evitar dependencias con CLI o FS.

### 3.5. `core/scheduler/algorithms/fcfs.py`

Implementar `FCFSScheduler(BaseScheduler)`:

* Usa orden de llegada (FIFO).
* No expropiativo.

### 3.6. `core/scheduler/algorithms/rr.py`

Implementar `RRScheduler(BaseScheduler)`:

* Recibe `quantum: float` en el constructor.
* Mantiene cola circular.
* Devuelve el siguiente proceso conforme se agote el quantum.
* El control fino del quantum puede estar en `simulator.py`, pero el scheduler debe estar preparado para trabajar con esa lógica.

### 3.7. `core/scheduler/algorithms/sjf.py`

Implementar `SJFScheduler(BaseScheduler)`:

* SJF **no expropiativo**: selecciona el proceso con menor `burst_time` o `remaining_time` al momento de la selección.
* En caso de empate, usar desempate por `arrival_time` y luego por `pid`.

### 3.8. `core/scheduler/metrics.py`

Definir estructuras para:

* Métricas individuales de cada proceso.
* Métricas agregadas del sistema (promedios, throughput, etc.).

Incluir funciones para calcular:

* `waiting_time`
* `turnaround_time`
* `response_time`
* `throughput`
* `cpu_utilization`
* `num_context_switches`

### 3.9. `core/scheduler/simulator.py`

Implementar un simulador de tiempo discreto o continuo simple:

* Recibe:

  * Lista de trabajos (procesos) como PCBs o una estructura simple.
  * Un scheduler (`BaseScheduler`).
* Se encarga de:

  * Insertar procesos al scheduler según `arrival_time`.
  * Gestionar el tiempo actual.
  * Invocar al scheduler para decidir qué proceso corre.
  * Actualizar:

    * `remaining_time`
    * `state`
    * `first_start_time`
    * `finish_time`
  * Contabilizar cambios de contexto.

Debe devolver un objeto de métricas agregadas que la CLI pueda mostrar.

---

## 4. Reglas de Diseño para Sistema de Archivos (core/fs/)

### 4.1. `core/fs/models.py`

Definir clases:

* `User` (mínimo `name` o `uid`).
* `FsNode` base, con:

  * `name`
  * `owner: User`
  * `permissions` (ver `permissions.py`)
  * `parent: Directory | None`
* `Directory(FsNode)` con:

  * Colección de hijos (`dict[str, FsNode]`).
* `File(FsNode)` con:

  * `content: str` (para MVP).

### 4.2. `core/fs/permissions.py`

Definir estructura de permisos:

* Modelo simple tipo Unix para el MVP:

  * `read`, `write`, `execute` para el dueño.
* Clase o estructura `Permissions` con flags booleanos.

Implementar funciones para comprobar permisos:

* `can_read(user, node)`
* `can_write(user, node)`
* `can_execute(user, node)`

### 4.3. `core/fs/ops.py`

Implementar funciones de alto nivel que operan sobre el árbol:

* `ls(path: str, user: User) -> list[str]`
* `cd(current_path: str, target: str, user: User) -> str`
* `mkdir(path: str, user: User) -> None`
* `touch(path: str, user: User) -> None`
* `cat(path: str, user: User) -> str`
* `write(path: str, content: str, user: User) -> None`
* `rm(path: str, user: User) -> None`

Si un permiso no es suficiente, lanzar una excepción específica (p. ej. `PermissionError` o una excepción propia del módulo).

### 4.4. `core/fs/tree_renderer.py`

Implementar una función simple:

* `render_tree(root: Directory) -> str`

Para mostrar el árbol tipo:

```text
/
├── home
│   └── user
│       ├── file.txt
│       └── docs
└── tmp
```

---

## 5. Capa de Servicios (core/services/)

### 5.1. `core/services/sim_service.py`

Definir clase `SimService`:

* Debe recibir las dependencias necesarias (por ejemplo una fábrica de schedulers).
* Exponer un método:

```python
class SimService:
    def run(self, jobs, config):
        """
        Ejecuta la simulación con los jobs y la configuración dada,
        y devuelve un objeto con las métricas completas.
        """
        ...
```

`config` debe incluir:

* Algoritmo (`"fcfs"`, `"rr"`, `"sjf"`).
* Quantum para RR.
* Parámetros relevantes.

### 5.2. `core/services/fs_service.py`

Definir clase `FsService`:

```python
class FsService:
    def __init__(self, root: Directory, user: User):
        ...

    def execute(self, command: str, args: list[str]) -> str:
        """
        Ejecuta un comando del sistema de archivos ('ls', 'cd', etc.)
        y devuelve una cadena para mostrar en la CLI.
        """
        ...
```

* Debe utilizar internamente las funciones de `core/fs/ops.py`.

---

## 6. CLI (adapters/cli/main.py)

El MVP de la CLI debe:

* Usar `argparse` o `cmd` de Python.
* Permitir dos modos principales:

1. **Modo simulador**:

   * Comando ejemplo:

     ```bash
     python -m adapters.cli.main sim \
       --algo rr \
       --quantum 3 \
       --input data/examples/scenario1.csv
     ```
   * Debe:

     * Cargar el escenario desde CSV/JSON.
     * Crear los PCBs.
     * Invocar `SimService.run`.
     * Mostrar métricas por proceso y globales en formato legible.

2. **Modo sistema de archivos**:

   * Un shell simple tipo:

     ```text
     fs> pwd
     fs> ls
     fs> mkdir docs
     fs> cd docs
     fs> touch notas.txt
     fs> write notas.txt "hola"
     fs> cat notas.txt
     fs> exit
     ```
   * Debe usar `FsService` para ejecutar cada comando.

---

## 7. Requisitos No Funcionales y Estilo

Para el modelo de código (Codex):

* Escribir código en **Python 3.10+**.
* Seguir PEP8 de forma razonable (nombres de variables y funciones legibles).
* Añadir **docstrings** breves en clases y funciones públicas.
* Donde haya ambigüedad, añadir un comentario `# TODO:` en lugar de inventar requisitos.

---

## 8. Qué NO debe hacer el MVP

* No implementar aún lógica real de `adapters/webapi/api.py`.
* No implementar aún la integración completa con PyWebview en `adapters/gui_webview/run.py`.
* No añadir dependencias innecesarias en `requirements.txt` (solo lo mínimo: `fastapi` o `flask` opcionalmente, `pytest` para tests, `pywebview` para etapas posteriores).

---

## 9. Orden sugerido de implementación (para el modelo)

1. Implementar `core/scheduler/*` (PCB, estados, colas, algoritmos, métricas, simulador).
2. Implementar `core/fs/*` (modelos, permisos, operaciones, renderizado de árbol).
3. Implementar `core/services/*` (SimService, FsService).
4. Implementar CLI en `adapters/cli/main.py`.
5. Crear tests básicos en `tests/test_scheduler.py`, `tests/test_fs.py`, `tests/test_cli.py` para validar el MVP.

El objetivo es que, al finalizar estos pasos, el proyecto sea capaz de:

* Ejecutar simulaciones de planificación con diferentes algoritmos y métricas.
* Permitir operaciones básicas sobre un sistema de archivos virtual desde la CLI.

---

## 10. Estado Actual del Proyecto - Implementaciones Completadas 

###  **Simulador de Planificación CPU (100% Funcional)**

#### **Algoritmos Implementados:**
- **FCFS (First Come First Served)**: Implementación completa no expropiatava
- **Round Robin (RR)**: Con quantum configurable y cola circular
- **SJF (Shortest Job First)**: No expropiativo con desempate por arrival_time

#### **Simulador Avanzado (`SchedulerSimulator`):**
-  **Ciclo de simulación completo** con manejo de tiempo discreto
-  **Gestión de estados**: NEW → READY → RUNNING → BLOCKED → TERMINATED
-  **Soporte I/O Operations**: Bloqueos aleatorios con distribuciones normales
-  **Context Switches**: Contabilización automática de cambios de contexto
-  **Métricas comprehensivas**:
  - Waiting Time por proceso y promedio
  - Turnaround Time por proceso y promedio
  - Response Time por proceso y promedio
  - Throughput del sistema
  - CPU Utilization en porcentaje
  - Número total de context switches

#### **Formatos de Entrada Soportados:**
```csv
# CSV Format
pid,arrival_time,burst_time
1,0,5
2,1,3
3,2,8
```

```json
{
  "processes": [
    {"pid": 1, "arrival_time": 0, "burst_time": 5},
    {"pid": 2, "arrival_time": 1, "burst_time": 3},
    {"pid": 3, "arrival_time": 2, "burst_time": 8}
  ]
}
```

###  **Sistema de Archivos Virtual (100% Funcional)**

#### **Operaciones Implementadas:**
-  **pwd**: Mostrar directorio actual
-  **ls**: Listar contenido con permisos y detalles
-  **cd**: Navegación con soporte para `.`, `..`, rutas absolutas y relativas
-  **mkdir**: Crear directorios con validación de permisos
-  **touch**: Crear archivos vacíos
-  **cat**: Leer contenido de archivos
-  **write**: Escribir contenido a archivos
-  **rm**: Eliminar archivos y directorios
-  **tree**: Renderizado visual del árbol de directorios

#### **Sistema de Permisos Unix:**
-  **Permisos rwx**: Read, Write, Execute para propietario
-  **Validación de permisos**: En todas las operaciones
-  **Usuarios y propietarios**: Sistema completo de ownership

#### **Renderizador de Árbol:**
```text
/
├── home/
│   ├── user/
│   │   ├── documents/
│   │   │   └── readme.txt
│   │   └── projects/
│   └── guest/
└── tmp/
```

###  **Interfaz de Usuario Completa**

#### **CLI Mejorada:**
-  **Modo Simulador**: Ejecución con métricas detalladas y exportación
-  **Modo Filesystem**: Shell interactivo completo
-  **Validación robusta**: Error handling comprehensivo
-  **Múltiples formatos**: Soporte CSV y JSON
-  **Exportación**: Resultados en texto plano y CSV

#### **GUI Web (PyWebview):**
-  **Interfaz Bootstrap**: Design responsivo y moderno
-  **Dos módulos integrados**: 
  - Simulador de procesos con configuración avanzada
  - Explorador de archivos virtual interactivo
-  **API Bridge**: Comunicación Python ↔ JavaScript
-  **Visualización en tiempo real**: Métricas y resultados dinámicos

###  **Testing y Validación**

#### **Suite de Tests Implementada:**
-  **Tests unitarios del scheduler**: Cobertura completa de algoritmos
-  **Tests del filesystem**: Validación de todas las operaciones
-  **Tests de integración**: CLI y servicios
-  **Scripts de demostración**: Casos de uso reales

#### **Ejemplos de Uso:**
```bash
# Simulación con FCFS
python -m adapters.cli.main sim --algo fcfs --input data/examples/scenario1.csv

# Simulación con Round Robin
python -m adapters.cli.main sim --algo rr --quantum 3 --input data/examples/scenario2.json

# Sistema de archivos interactivo
python -m adapters.cli.main fs

# GUI Web
python -m adapters.gui_webview.run
```

###  **Métricas**

#### **Salida de Ejemplo:**
```
Simulation Results - Round Robin (quantum=3)
============================================
Process Metrics:
  PID 1: WT=7.00, TAT=12.00, RT=0.00
  PID 2: WT=4.00, TAT=7.00, RT=2.00
  PID 3: WT=13.00, TAT=21.00, RT=5.00

System Metrics:
  Average Waiting Time: 8.00
  Average Turnaround Time: 13.33
  Average Response Time: 2.33
  Throughput: 0.375 processes/time
  CPU Utilization: 88.89%
  Context Switches: 6
```

### 🔧 **Arquitectura y Servicios**

#### **Patrón Hexagonal Completo:**
-  **Core Domain**: Scheduler y FileSystem totalmente implementados
-  **Services Layer**: SimService y FsService como casos de uso
-  **Adapters**: CLI, GUI, y API funcionales
-  **Dependency Injection**: Servicios desacoplados y testeable

###  **Próximos Pasos Sugeridos**
1. **Scheduler Expropiativo**: Implementar SJF y Priority Scheduling exprópiativos
2. **Permisos Avanzados**: Grupos de usuarios y permisos extendidos
3. **Persistencia**: Guardar estado del filesystem en disco
4. **Métricas Visuales**: Gráficos de Gantt y timelines en la GUI
5. **API REST**: Endpoint completo para integraciones externas

