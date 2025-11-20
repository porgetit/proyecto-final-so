# Simulador de Planificación de CPU

Módulo de simulación discreta para estudiar algoritmos clásicos de planificación de CPU (FCFS, SJF y Round Robin), con soporte para bloqueos de I/O aleatorios y cálculo de métricas de rendimiento.
Los tests automatizados verifican el comportamiento de colas, algoritmos y métricas para asegurar coherencia con la implementación.

---

## Contenido del módulo

* **`scheduler.simulator.SchedulerSimulator`**
  Orquestador principal. Ejecuta el ciclo de reloj, gestiona las colas *ready* y *blocked*, aplica las decisiones del algoritmo y calcula métricas agregadas.

* **`scheduler.simulator.SimulationConfig`**
  Configuración central: algoritmo, `time_slice` opcional, límite de tiempo y parámetros de I/O.

* **`scheduler.pcb.PCB`**
  Estructura de Proceso (*Process Control Block*).
  Contiene:

  * métricas de ejecución (espera, retorno, respuesta),
  * agenda de I/O,
  * estados de ciclo de vida,
  * ráfaga restante (`remaining_burst`).

* **`scheduler.algorithms.*`**
  Implementaciones de:

  * FCFS
  * SJF (no expropiativo)
  * Round Robin (expropiativo)
    Cada algoritmo expone `prime()` y `next_tick()`.

* **`scheduler.metrics`**
  Obtiene métricas agregadas y por proceso a partir del estado final de los PCBs.

* **`scheduler.queues`**
  Colas *ready* y *blocked* basadas en `collections.deque`.

* **`tests/`**
  Pruebas automáticas con `pytest` para algoritmos, bloqueos de I/O y casos borde.

---

## Flujo de simulación

En cada *tick* del reloj:

1. Se encolan procesos cuya llegada está programada para ese tiempo.
2. Se avanza el I/O de los procesos bloqueados mediante `tick_io`.
3. Los procesos que terminan I/O se reenfilan en *ready*.
4. El algoritmo de planificación toma una decisión mediante `next_tick`.
5. Se ejecuta un tick de CPU del proceso seleccionado.

Notas relevantes:

* `time_slice` puede sobreescribir el *quantum* del algoritmo (Round Robin) sin modificar su constructor.
* Al finalizar un PCB se registran:

  * `finish_time`
  * `turnaround_time`
  * `waiting_time`
  * `response_time`
* Una ráfaga inicial (`burst_time`) igual a 0 consume **1 tick** en este modelo para efectos de consistencia.

---

## Bloqueos de I/O y aleatoriedad

Cada PCB puede generar una **agenda de I/O** a partir de distribuciones normales:

* `io_interval_mean`, `io_interval_stddev`
* `io_duration_mean`, `io_duration_stddev`
* `io_max_events`

También se puede asignar manualmente una agenda para reproducibilidad.

El I/O puede desactivarse:

* globalmente: `io_enabled=False`
* por proceso: `metadata={"io_enabled": False}`

---

## Configuración y métricas

### Métricas agregadas

```math

\text{throughput} = \frac{\lvert \text{completed} \rvert}{\text{clock}}
```

```math
\text{cpu utilization} = \frac{\text{busy time}}{\text{clock}}

```

Además se registran:

* número de *context_switches*
* tiempo total simulado

### Métricas por proceso

`SimulationMetrics.from_pcbs` deriva:

* tiempo de espera
* tiempo de retorno
* tiempo de respuesta

evitando duplicar cálculos.

`max_time` permite detener la simulación si se supera el límite especificado.

---

## Algoritmos de planificación y macroalgoritmos

### Protocolo base

El archivo `algorithms/base.py` define:

* la interfaz `SchedulingAlgorithm`
* los métodos:

  * `reset()`
  * `prime(ready_queue, jobs)`
  * `next_tick(current_time, running, ready_queue)`
* la estructura `SchedulingDecision`

Esto permite añadir nuevos algoritmos sin modificar el bucle principal del simulador.

---

### FCFS — *First-Come, First-Served*

**Definición:** no expropiativo; los procesos se ejecutan en orden de llegada.

**Selección del proceso:**

```math
p^* = \arg\min_{p \in R_t} (a_p, i_p)
```

donde:

* $`a_{p}`$ = tiempo de llegada
* $`i_p`$ = índice de estabilidad (orden de entrada a la cola)

Una vez seleccionado, el proceso corre hasta finalizar o bloquearse por I/O.

---

### SJF — *Shortest Job First*

**Definición:** no expropiativo; selecciona el proceso con menor ráfaga restante.

**Selección del proceso:**

```math
p^* = \arg\min_{p \in R_t} (\text{rem}_p, i_p)
```

donde:

* $`\text{rem}_p`$ = ráfaga restante
* $`i_p`$ garantiza estabilidad en empates

El proceso se ejecuta hasta terminar o bloquearse.

---

### Round Robin (RR)

**Definición:** expropiativo; rota procesos con cuantum ($q$), sobreescribible vía `time_slice`.

Mantenimiento:

* `r`: proceso actual
* `d`: tiempo en que fue despachado

**Reglas:**

1. Si $r$ existe y $t - d < q$ → continúa.
2. Si expira el cuantum y hay procesos en *ready* → `r` se encola de nuevo y se toma el siguiente.
3. Si no hay proceso en ejecución → se toma el siguiente de *ready*.
4. I/O interrumpe y mueve a *BLOCKED*.

---

## Uso básico

```python
from scheduler.simulator import SchedulerSimulator, SimulationConfig
from scheduler.algorithms.rr import RoundRobinAlgorithm
from scheduler.pcb import PCB

config = SimulationConfig(
    algorithm=RoundRobinAlgorithm(quantum=4),
    time_slice=2,              # sobrescribe el cuantum del algoritmo
    io_enabled=True,
    io_interval_mean=5.0,
    io_interval_stddev=1.5,
    io_duration_mean=3.0,
    io_duration_stddev=1.0,
)

sim = SchedulerSimulator(config)
sim.load_jobs([PCB(1, 0, 8), PCB(2, 2, 4)])

metrics = sim.run()
```

---

## Pruebas automatizadas

Ejecutar:

```bash
python -m pytest -q
```

Cobertura (`tests/test_scheduler.py`):

* FCFS respeta el orden de llegada.
* SJF selecciona la ráfaga más corta y mantiene estabilidad en empates.
* Round Robin respeta el *time_slice* y rota según el cuantum esperado.
* Flujo completo de bloqueo/desbloqueo de I/O con agenda determinista.
* Casos borde:

  * empates en SJF
  * corte por `max_time`
  * ráfagas cero
