# Simulador de Planificación de CPU

Este módulo implementa un simulador discreto de planificación de CPU con algoritmos clásicos (FCFS, SJF, Round Robin) y soporte de bloqueos I/O aleatorios. Está pensado para integrarse como componente de núcleo en proyectos educativos o de visualización de sistemas operativos.

## Qué hay en el módulo
- `scheduler.simulator.SchedulerSimulator`: Orquestador principal; ejecuta el bucle de reloj, gestiona colas ready/bloqueadas, aplica decisiones del algoritmo y calcula métricas agregadas.
- `scheduler.simulator.SimulationConfig`: Configuración compartida (algoritmo, `time_slice` opcional, límites de tiempo y parámetros de I/O).
- `scheduler.pcb.PCB`: Estructura de proceso con métricas (espera, retorno, respuesta), planificación de I/O y estados de ciclo de vida.
- `scheduler.algorithms.*`: Implementaciones de FCFS, SJF (no expropiativo) y Round Robin (expropiativo) que exponen `prime`/`next_tick`.
- `scheduler.metrics`: Crea métricas de procesos y simulaciones a partir del estado final de los PCBs.
- `scheduler.queues`: Colas ready/bloqueadas simples basadas en `deque`.
- `tests/`: Pruebas automatizadas con pytest que cubren algoritmos, bloqueos I/O y casos borde.

## Énfasis y características
- **Simulación discreta**: Cada tick encola llegadas, avanza I/O bloqueado y pide al algoritmo la siguiente decisión.
- **Bloqueos I/O aleatorios**: Cada PCB puede generar una agenda de I/O mediante distribuciones normales controlables (`io_interval_*`, `io_duration_*`, `io_max_events`); al dispararse, el proceso pasa a la cola bloqueada y regresa cuando termina el I/O.
- **Cuantum configurable**: `SimulationConfig.time_slice` invalida dinámicamente el `quantum` de algoritmos que lo soporten (p. ej., Round Robin) sin cambiar su constructor.
- **Métricas consistentes**: Throughput y utilización se calculan en el bucle principal con base en ticks simulados y tiempo ocupado; se evita el cálculo duplicado en `SimulationMetrics.from_pcbs`.

## Pruebas automatizadas
Ejecuta la suite:
```bash
python -m pytest -q
```
Cobertura incluida (`tests/test_scheduler.py`):
- FCFS respeta orden de llegada y calcula esperas clásicas.
- SJF elige el trabajo más corto y mantiene orden de llegada en empates.
- Round Robin respeta la anulación de `time_slice` y rota según el cuantum esperado.
- Flujo bloqueado/desbloqueado de I/O con agenda determinista.
- Casos borde: empates de SJF, corte por `max_time`, ráfaga cero.

## Integración como módulo central
1. **Instalación local**: Añade `core/scheduler` al `PYTHONPATH` o empaqueta el módulo (p. ej., con `pip install -e .` si se crea un `setup.py/pyproject`).
2. **Uso básico**:
   ```python
   from scheduler.simulator import SchedulerSimulator, SimulationConfig
   from scheduler.algorithms.rr import RoundRobinAlgorithm
   from scheduler.pcb import PCB

   config = SimulationConfig(
       algorithm=RoundRobinAlgorithm(quantum=4),
       time_slice=2,              # opcional: sobrescribe el cuantum
       io_enabled=True,           # activa bloqueos I/O aleatorios
       io_interval_mean=5.0,
       io_interval_stddev=1.5,
       io_duration_mean=3.0,
       io_duration_stddev=1.0,
   )
   sim = SchedulerSimulator(config)
   sim.load_jobs([PCB(1, 0, 8), PCB(2, 2, 4)])
   metrics = sim.run()
   ```
3. **En un proyecto mayor**: Expone este simulador detrás de un servicio (API REST/CLI) o como backend de visualización. La interfaz mínima es `load_jobs` + `run`; puedes enriquecer `SimulationConfig` con seeds para reproducibilidad, o conectar eventos de estado a tu capa de presentación.

## Notas
- Los bloqueos I/O se desactivan por proceso con `metadata={"io_enabled": False}`.
- Si necesitas control total de la aleatoriedad, genera y asigna agendas de I/O manualmente en cada PCB antes de `run`.
