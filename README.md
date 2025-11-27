# Informe tecnico - simulador de planificacion de CPU y sistema de archivos virtual

Este informe documenta el repositorio `proyecto-final-so`, que integra un simulador discreto de planificacion de procesos (FCFS, SJF y Round Robin) y un sistema de archivos virtual operado via CLI. Se incluyen detalles de arquitectura, decisiones de diseno, flujo de ejecucion y evidencias de prueba. La GUI referenciada en algunos demos (PyWebview) no se encuentra en este arbol.

## Objetivo y alcance

- Desarrollar un entorno didactico para estudiar algoritmos clasicos de planificacion y un sistema de archivos simplificado con permisos basicos.
- Proveer un adaptador CLI unificado que permita ejecutar simulaciones y explorar el sistema de archivos virtual.
- Incluir escenarios de ejemplo, scripts de demostracion y pruebas automatizadas para validar los modulos nucleares.

## Arquitectura general

- **Dominio core (`core/`)**: dos subdominios aislados (`scheduler` y `fs`) que contienen modelos y logica de negocio.
- **Servicios de aplicacion (`core/services`)**: fachadas `SimService` y `FsService` que traducen peticiones externas a acciones de dominio.
- **Adaptadores (`adapters/`)**: CLI principal (`adapters/cli/main.py`) y documentacion de uso (`adapters/cli/CLI_README.md`, `FLUJO_EJECUCION_CLI.md`).
- **Datos (`data/examples`)**: escenarios CSV/JSON listos para alimentar el simulador.
- **Demos y utilidades**: `demo_cli.py`, `enhanced_demo.py`, `test_filesystem.py` para recorridos end-to-end.

## Detalle tecnico: simulador de planificacion (`core/scheduler`)

- **Algoritmos** (`core/scheduler/algorithms`):
  - `FCFSAlgorithm`: no expropiativo, respeta orden de llegada.
  - `SJFAlgorithm`: no expropiativo, elige menor rafaga restante con estabilidad en empates.
  - `RoundRobinAlgorithm`: expropiativo, quantum configurable; `time_slice` del simulador puede sobrescribir el valor.
  - `SchedulingDecision` define la interfaz comun (`next_process`, `preempt_current`, `timeslice`).
- **Ciclo de simulacion** (`core/scheduler/simulator.py`):
  - `SimulationConfig` agrupa algoritmo, `time_slice`, `max_time` y parametros de I/O (media/desviacion de intervalo y duracion, max eventos, habilitado).
  - En cada tick: se encolan llegadas, se avanza I/O de bloqueados, se reingresan procesos desbloqueados, el algoritmo decide el siguiente PCB, se consume CPU, se registran `context_switches` y `busy_time`, y se calculan tiempos de finalizacion/espera/retorno.
  - Si `max_time` se supera, la simulacion corta sin completar procesos restantes.
- **Modelo de procesos** (`core/scheduler/pcb.py`):
  - PCB contiene tiempos de llegada/rafaga, prioridad opcional, y metricas derivadas (`response_time`, `waiting_time`, `turnaround_time`).
  - Genera agendas de I/O pseudoaleatorias acotadas a la rafaga total; `io_request_due` y `tick_io` mueven el proceso entre `READY` y `BLOCKED`.
- **Colas y estados** (`core/scheduler/queues.py`, `core/scheduler/states.py`):
  - Colas `ReadyQueue` y `BlockedQueue` sobre `deque`; estados finitos `NEW`, `READY`, `RUNNING`, `BLOCKED`, `TERMINATED`.
- **Metricas** (`core/scheduler/metrics.py`):
  - `SimulationMetrics.from_pcbs` deriva metricas por proceso y agrega throughput, utilizacion de CPU y cambios de contexto.
- **Pruebas unitarias** (`core/scheduler/tests/test_scheduler.py`):
  - Cobertura de orden FCFS, desempate estable SJF, respeto de quantum y `time_slice` en RR, flujo determinista de I/O bloqueado/desbloqueado, corte por `max_time` y procesos de rafaga cero.

## Detalle tecnico: sistema de archivos virtual (`core/fs`)

- **Modelos** (`core/fs/models.py`):
  - `Directory` y `File` heredan de `FileSystemEntity`, mantienen propietario, permisos y construccion de rutas absolutas.
- **Permisos** (`core/fs/permissions.py`):
  - `PermissionSet` con banderas rwx solo para el propietario; todas las operaciones validan lectura/escritura/ejecucion respecto al usuario activo.
- **Operaciones** (`core/fs/ops.py`):
  - `ls`, `cd`, `pwd`, `mkdir`, `touch`, `cat`, `write`, `rm`, `tree`, `resolve`.
  - Soporte de rutas absolutas y relativas con `.` y `..`; validacion estricta de tipos y permisos.
  - Particularidades: `mkdir`, `touch` y `write` requieren que el directorio padre exista; `rm` acepta `recursive` solo via argumento nombrado (la shell actual no parsea `-r`); no hay persistencia entre sesiones ni multipropietario.
- **Renderizado de arbol** (`core/fs/tree_renderer.py`):
  - `render_tree` recorre DFS priorizando directorios y emite conectores estilo `tree` para visualizacion jerarquica.

## Servicios y adaptadores

- **SimService** (`core/services/sim_service.py`): traduce `SimulationRequest` en PCBs, instancia el algoritmo solicitado (`fcfs`, `rr`, `sjf`), arma el `SchedulerSimulator` y retorna `SimulationMetrics`.
- **FsService** (`core/services/fs_service.py`): mapea comandos de texto a metodos de `FileSystemOps` y normaliza las salidas para la CLI.
- **CLI** (`adapters/cli/main.py`):
  - Subcomando `sim`: `--algo` (`fcfs|rr|sjf`), `--input` (CSV/JSON `pid,arrival,burst[,priority]`), `--quantum` obligatorio para `rr`.
  - Subcomando `fs`: abre shell interactiva con prompt `fs:<ruta>` y comandos `ls`, `cd`, `pwd`, `mkdir`, `touch`, `cat`, `write`, `rm`, `tree`, `help`, `exit`. No existe parser de flags; los argumentos se pasan literales a `FileSystemOps`.
  - `format_metrics` imprime tabla por proceso y metricas agregadas (throughput, utilizacion de CPU, promedios de tiempos y cambios de contexto).
  - Documentacion complementaria en `adapters/cli/CLI_README.md` y `FLUJO_EJECUCION_CLI.md` (instrucciones paso a paso y sesiones ejemplo).

## Datos, demos y pruebas de soporte

- **Escenarios de entrada** (`data/examples`): `scenario1.csv`, `scenario3.csv` (tablas pid/llegada/rafaga/prioridad) y `scenario2.json` (lista de jobs) para validar algoritmos.
- **Demos**:
  - `demo_cli.py`: ejecuta simulaciones de muestra y muestra instrucciones para el shell del sistema de archivos.
  - `enhanced_demo.py`: imprime comandos listos para probar algoritmos y CLI; menciona una GUI PyWebview (no incluida en este repo).
- **Prueba rapida del FS**: `test_filesystem.py` recorre operaciones basicas a traves de `FsService`.

## Instalacion y ejecucion recomendada

```bash
python -m pip install -r requirements.txt

# Simulador
python -m adapters.cli.main sim --algo fcfs --input data/examples/scenario1.csv
python -m adapters.cli.main sim --algo rr --quantum 2 --input data/examples/scenario2.json

# Shell del sistema de archivos
python -m adapters.cli.main fs --user alice
```

Para validar el simulador, ejecutar `python -m pytest core/scheduler/tests/test_scheduler.py`.

## Limitaciones y consideraciones

- Los algoritmos se ejecutan en un modelo discreto simplificado; no hay planificacion multinucleo ni prioridades dinamicas.
- La I/O se modela con agendas discretas y pseudoaleatorias; no hay dispositivos ni latencias reales.
- El sistema de archivos es volátil (en memoria), monousuario y sin persistencia ni cuotas.
- El comando `rm` en la shell no acepta banderas; el borrado recursivo solo se expone por codigo (`recursive=True`).
- La GUI mencionada en los demos no esta presente en el repositorio.

## Autoria y roles

- Desarrollo del simulador de planificacion de CPU: Kevin Esguerra Cardona
- Desarrollo del sistema de archivos: Maicol
- Desarrollo de la CLI: Isabella
- Desarrollo de la GUI (interfaz Django; no incluida en este repositorio): Diego

## Referencia y contexto academico

- Repositorio GitHub: https://github.com/porgetit/proyecto-final-so/
- Proyecto desarrollado como trabajo final para la materia de Sistemas Operativos del programa de Ingenieria en Sistemas y Computacion de la Universidad Tecnologica de Pereira, bajo la direccion del ingeniero Juan Garcia.

## Disclaimer sobre uso de IA

Este informe y parte del soporte documental fueron preparados con asistencia de agentes de IA. Verifique y valide los detalles tecnicos antes de utilizarlos en entornos de produccion o evaluacion academica.
