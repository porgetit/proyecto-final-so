# FLUJO COMPLETO DE EJECUCIÓN
## Simulador de Planificación de Procesos + Sistema de Archivos Virtual

---

## 📋 PREPARACIÓN INICIAL

### 1. Activar Entorno Virtual
```powershell
& "C:\Users\isabe\OneDrive\Documentos\Proyecto SO (simulador de planificación de procesos)\venv\Scripts\Activate.ps1"
```

### 2. Navegar al Directorio del Proyecto
```powershell
cd "C:\Users\isabe\OneDrive\Documentos\Proyecto SO (simulador de planificación de procesos)\proyecto-final-so"
```

### 3. Ver Ayuda General
```powershell
python -m adapters.cli.main --help
```

**Salida esperada:**
```
CPU scheduler simulator and virtual filesystem shell.

positional arguments:
  {sim,fs}
    sim       Run a scheduling simulation.
    fs        Start an interactive shell for the virtual filesystem.

options:
  -h, --help  show this help message and exit
```

---

## 🔄 SIMULADOR DE PLANIFICACIÓN DE PROCESOS

### Ver Ayuda del Simulador
```powershell
python -m adapters.cli.main sim --help
```

**Salida esperada:**
```
usage: main.py sim [-h] --algo {fcfs,rr,sjf} [--quantum QUANTUM] --input INPUT

options:
  -h, --help            show this help message and exit
  --algo {fcfs,rr,sjf}  Scheduling algorithm to use.
  --quantum QUANTUM     Quantum for Round Robin (ignored otherwise).
  --input INPUT         Path to the scenario file (CSV/JSON).
```

### Comandos de Simulación

#### FCFS (First Come First Served)
```powershell
# Con archivo CSV
python -m adapters.cli.main sim --algo fcfs --input data/examples/scenario1.csv

# Con archivo JSON
python -m adapters.cli.main sim --algo fcfs --input data/examples/scenario2.json
```

#### Round Robin
```powershell
# Con quantum = 2
python -m adapters.cli.main sim --algo rr --quantum 2 --input data/examples/scenario1.csv

# Con quantum = 3
python -m adapters.cli.main sim --algo rr --quantum 3 --input data/examples/scenario2.json
```

#### SJF (Shortest Job First)
```powershell
# Con archivo CSV
python -m adapters.cli.main sim --algo sjf --input data/examples/scenario1.csv

# Con archivo JSON
python -m adapters.cli.main sim --algo sjf --input data/examples/scenario2.json
```

### Ejemplo de Salida de Simulación
```
============================================================
SIMULATION RESULTS
============================================================

Per-Process Metrics:
----------------------------------------
PID  Wait     Turnaround Response
----------------------------------------
1    0.0      8.0        0.0     
2    6.0      10.0       6.0     
3    8.0      10.0       8.0     
4    9.0      10.0       9.0     

Aggregate Metrics:
----------------------------------------
Average Waiting Time:     5.75
Average Turnaround Time:  9.50
Average Response Time:    5.75
Throughput:               0.250 jobs/tick
CPU Utilization:          93.8%
Context Switches:         3
============================================================
```

---

## 🗂️ SISTEMA DE ARCHIVOS VIRTUAL

### Ver Ayuda del Sistema de Archivos
```powershell
python -m adapters.cli.main fs --help
```

### Iniciar Sistema de Archivos
```powershell
# Con usuario por defecto
python -m adapters.cli.main fs

# Con usuario específico
python -m adapters.cli.main fs --user alice
python -m adapters.cli.main fs --user admin
python -m adapters.cli.main fs --user guest
```

### Sesión Interactiva Completa

```bash
# Al ejecutar: python -m adapters.cli.main fs --user alice
# Se inicia el shell interactivo:

fs:/> help
Available commands:
  ls [path]          - List directory contents
  cd <path>          - Change directory
  mkdir <path>       - Create directory
  touch <file>       - Create/update file
  cat <file>         - Display file content
  write <file> <text> - Write text to file
  rm [-r] <path>     - Remove file/directory
  tree               - Display directory tree
  pwd                - Show current directory
  exit, quit         - Leave shell

fs:/> pwd
/

fs:/> mkdir documents projects temp

fs:/> ls
documents  projects  temp

fs:/> cd documents

fs:/documents> touch readme.txt notes.md plan.txt

fs:/documents> write readme.txt "Bienvenido al simulador de SO!"

fs:/documents> write notes.md "# Notas del Proyecto\n\nSimulador de planificación de procesos"

fs:/documents> cat readme.txt
Bienvenido al simulador de SO!

fs:/documents> ls
notes.md  plan.txt  readme.txt

fs:/documents> cd ..

fs:/> cd projects

fs:/projects> mkdir src docs tests

fs:/projects> cd src

fs:/projects/src> touch main.py utils.py

fs:/projects/src> cd ../docs

fs:/projects/docs> touch manual.txt

fs:/projects/docs> cd ../..

fs:/> tree
/
├── documents/
│   ├── notes.md
│   ├── plan.txt
│   └── readme.txt
├── projects/
│   ├── docs/
│   │   └── manual.txt
│   ├── src/
│   │   ├── main.py
│   │   └── utils.py
│   └── tests/
└── temp/

fs:/> rm -r temp

fs:/> tree
/
├── documents/
│   ├── notes.md
│   ├── plan.txt
│   └── readme.txt
└── projects/
    ├── docs/
    │   └── manual.txt
    ├── src/
    │   ├── main.py
    │   └── utils.py
    └── tests/

fs:/> exit
```

---

## 🎯 FLUJOS DE TRABAJO TÍPICOS

### 1. Análisis Comparativo de Algoritmos
```powershell
# Comparar los tres algoritmos con el mismo dataset
echo "=== FCFS ==="
python -m adapters.cli.main sim --algo fcfs --input data/examples/scenario1.csv

echo ""
echo "=== Round Robin (quantum=2) ==="
python -m adapters.cli.main sim --algo rr --quantum 2 --input data/examples/scenario1.csv

echo ""
echo "=== SJF ==="
python -m adapters.cli.main sim --algo sjf --input data/examples/scenario1.csv
```

### 2. Gestión de Configuraciones
```powershell
# Crear y gestionar archivos de configuración del sistema
python -m adapters.cli.main fs --user admin

# Dentro del shell interactivo:
# mkdir config
# cd config
# touch scheduler.conf system.ini
# write scheduler.conf "algorithm=rr\nquantum=3\npreemptive=true"
# cat scheduler.conf
# exit
```

### 3. Demo Completa del Sistema
```powershell
# Ejecutar demo completa con todas las funcionalidades
python enhanced_demo.py
```

---

## 📊 FORMATOS DE ARCHIVOS DE ENTRADA

### Formato CSV (scenario1.csv)
```csv
pid,arrival,burst,priority
1,0,8,1
2,2,4,2
3,4,2,3
4,6,1,1
```

### Formato JSON (scenario2.json)
```json
[
  {
    "pid": 1,
    "arrival": 0,
    "burst": 6,
    "priority": 2
  },
  {
    "pid": 2,
    "arrival": 1,
    "burst": 8,
    "priority": 1
  },
  {
    "pid": 3,
    "arrival": 2,
    "burst": 7,
    "priority": 3
  },
  {
    "pid": 4,
    "arrival": 3,
    "burst": 3
  }
]
```

---

## 🔧 COMANDOS DE DIAGNÓSTICO

### Verificar Estructura del Proyecto
```powershell
# Ver archivos de ejemplo disponibles
Get-ChildItem data/examples/ | Format-Table Name,Length -AutoSize

# Verificar estructura de directorios
tree /f
```

### Verificar Instalación
```powershell
# Verificar que Python puede importar los módulos
python -c "import adapters.cli.main; print('CLI disponible')"

# Verificar archivos de prueba
python -c "import pandas as pd; print('Dependencias OK')"
```

---

## 🚨 SOLUCIÓN DE PROBLEMAS

### Error de Módulo No Encontrado
```powershell
# Asegurar que estás en el directorio correcto
pwd

# Verificar que el entorno virtual está activado
where python
```

### Error de Archivo No Encontrado
```powershell
# Verificar que los archivos de ejemplo existen
ls data/examples/

# Crear archivo de prueba personalizado
echo "pid,arrival,burst,priority" > test_scenario.csv
echo "1,0,5,1" >> test_scenario.csv
echo "2,1,3,2" >> test_scenario.csv
```

### Problemas con el Sistema de Archivos Virtual
```powershell
# Si el shell no responde, usar Ctrl+C para salir
# Reiniciar con usuario diferente
python -m adapters.cli.main fs --user test
```

---

## 📈 MÉTRICAS IMPORTANTES

### Simulador de Planificación
- **Tiempo de Espera**: Tiempo que un proceso espera en la cola de listos
- **Tiempo de Retorno**: Tiempo desde llegada hasta finalización
- **Tiempo de Respuesta**: Tiempo desde llegada hasta primera ejecución
- **Throughput**: Procesos completados por unidad de tiempo
- **Utilización de CPU**: Porcentaje de tiempo que la CPU está ocupada
- **Cambios de Contexto**: Número de intercambios entre procesos

### Sistema de Archivos
- **Operaciones POSIX**: `ls`, `cd`, `mkdir`, `touch`, `cat`, `rm`
- **Funciones Avanzadas**: `tree`, `pwd`, escritura de archivos
- **Permisos**: Sistema básico de usuarios y permisos
- **Navegación**: Soporte para rutas relativas y absolutas

---

## 🎉 FUNCIONALIDADES DESTACADAS

### ✅ Simulador
- Implementación completa de algoritmos FCFS, RR y SJF
- Soporte para archivos CSV y JSON
- Métricas detalladas por proceso y agregadas
- Simulación de bloqueo por I/O
- Tracking de cambios de contexto

### ✅ Sistema de Archivos
- Shell interactivo con prompt contextual
- Renderizado de árboles con caracteres Unicode
- Operaciones recursivas (`rm -r`)
- Sistema de ayuda integrado
- Manejo robusto de errores

### ✅ Arquitectura
- Clean Architecture con separación de capas
- Servicios desacoplados (SimService, FsService)
- Adaptadores intercambiables (CLI, GUI, Web API)
- Extensible para nuevos algoritmos y funcionalidades