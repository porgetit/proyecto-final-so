# CLI - Interfaz de Línea de Comandos

## Descripción

La CLI proporciona dos interfaces principales:
1. **Simulador de Planificación de CPU** - Para ejecutar algoritmos de planificación
2. **Shell de Sistema de Archivos Virtual** - Para interactuar con un sistema de archivos simulado

## Uso General

```bash
python -m adapters.cli.main <comando> [opciones]
```

## Comandos Disponibles

### 1. Simulador de Planificación (`sim`)

Ejecuta simulaciones de algoritmos de planificación de CPU.

```bash
python -m adapters.cli.main sim --algo <algoritmo> --input <archivo> [--quantum <valor>]
```

**Parámetros:**
- `--algo`: Algoritmo a usar (`fcfs`, `rr`, `sjf`)
- `--input`: Archivo de escenario (CSV o JSON)
- `--quantum`: Quantum para Round Robin (solo requerido para `rr`)

**Ejemplos:**
```bash
# FCFS con archivo CSV
python -m adapters.cli.main sim --algo fcfs --input data/examples/scenario1.csv

# Round Robin con quantum 3
python -m adapters.cli.main sim --algo rr --quantum 3 --input data/examples/scenario2.json

# SJF con archivo CSV
python -m adapters.cli.main sim --algo sjf --input data/examples/scenario3.csv
```

### 2. Sistema de Archivos Virtual (`fs`)

Inicia un shell interactivo para el sistema de archivos virtual.

```bash
python -m adapters.cli.main fs [--user <nombre_usuario>]
```

**Parámetros:**
- `--user`: Nombre de usuario (por defecto: "user")

**Ejemplo:**
```bash
python -m adapters.cli.main fs --user miusuario
```

## Formatos de Archivo de Escenarios

### Formato CSV
```csv
# Comentarios empiezan con #
# Formato: pid,arrival_time,burst_time[,priority]
1,0,8,1
2,1,4,2
3,2,9,3
4,3,5,1
```

### Formato JSON
```json
[
  {
    "pid": 1,
    "arrival": 0,
    "burst": 8,
    "priority": 1
  },
  {
    "pid": 2,
    "arrival": 1,
    "burst": 4,
    "priority": 2
  }
]
```

**Nota:** El campo `priority` es opcional y solo se usa en algoritmos que lo requieran.

## Comandos del Sistema de Archivos

Una vez dentro del shell (`fs`), puedes usar los siguientes comandos:

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `pwd` | Mostrar directorio actual | `pwd` |
| `ls [ruta]` | Listar contenido del directorio | `ls`, `ls documents` |
| `cd <ruta>` | Cambiar directorio | `cd documents`, `cd ..`, `cd /` |
| `mkdir <nombre>` | Crear directorio | `mkdir proyectos` |
| `touch <archivo>` | Crear archivo vacío | `touch readme.txt` |
| `cat <archivo>` | Mostrar contenido del archivo | `cat readme.txt` |
| `write <archivo> <contenido>` | Escribir en archivo | `write readme.txt "Hola Mundo"` |
| `rm <ruta>` | Eliminar archivo/directorio | `rm readme.txt` |
| `tree [ruta]` | Mostrar estructura en árbol | `tree`, `tree documents` |
| `help` | Mostrar ayuda | `help` |
| `exit` | Salir del shell | `exit` |

## Ejemplos de Sesión del Sistema de Archivos

```
fs:/> pwd
/

fs:/> mkdir documentos
fs:/> mkdir proyectos
fs:/> ls
documentos/
proyectos/

fs:/> cd documentos
fs:/documentos> touch readme.txt
fs:/documentos> write readme.txt "Este es mi archivo de documentación"
fs:/documentos> cat readme.txt
Este es mi archivo de documentación

fs:/documentos> cd ..
fs:/> tree
├── documentos/
│   └── readme.txt
└── proyectos/

fs:/> rm documentos/readme.txt
fs:/> tree
├── documentos/
└── proyectos/

fs:/> exit
Goodbye!
```

## Algoritmos de Planificación Soportados

### FCFS (First Come First Served)
- **No expropiativo**
- Los procesos se ejecutan en orden de llegada
- Simple pero puede causar efecto convoy

### Round Robin (RR)
- **Expropiativo**
- Cada proceso recibe un quantum de tiempo
- Requiere especificar `--quantum`
- Bueno para sistemas interactivos

### SJF (Shortest Job First)
- **No expropiativo** (en esta implementación)
- Selecciona el proceso con menor tiempo de ráfaga
- Óptimo para minimizar tiempo de espera promedio

## Métricas Reportadas

Para cada simulación se calculan:

**Por proceso:**
- Tiempo de espera (Waiting Time)
- Tiempo de respuesta (Response Time)
- Tiempo de retorno (Turnaround Time)

**Del sistema:**
- Throughput (procesos por unidad de tiempo)
- Utilización de CPU
- Número de cambios de contexto
- Promedios de todas las métricas

## Notas Importantes

1. **Estado actual**: Los algoritmos de planificación están parcialmente implementados. La CLI carga correctamente los datos pero las simulaciones retornan métricas vacías.

2. **Permisos**: El sistema de archivos implementa permisos básicos tipo Unix (rwx) solo para el propietario.

3. **Persistencia**: Los datos del sistema de archivos solo existen durante la sesión actual.

4. **Errores**: Todos los errores se manejan gracefully y se muestran mensajes informativos.

## Solución de Problemas

### Error "No module named 'core'"
Ejecuta desde el directorio raíz del proyecto:
```bash
cd proyecto-final-so
python -m adapters.cli.main
```

### Archivo de escenario no encontrado
Verifica que la ruta sea correcta respecto al directorio de trabajo:
```bash
python -m adapters.cli.main sim --algo fcfs --input data/examples/scenario1.csv
```

### Error de permisos en sistema de archivos
El usuario solo puede operar en archivos/directorios que posee con permisos apropiados.