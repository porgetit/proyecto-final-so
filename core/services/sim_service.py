"""Service layer for running CPU scheduling simulations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Type

from ..scheduler.algorithms import FCFSAlgorithm, RoundRobinAlgorithm, SJFAlgorithm, SchedulingAlgorithm
from ..scheduler.metrics import SimulationMetrics
from ..scheduler.pcb import PCB
from ..scheduler.simulator import SchedulerSimulator, SimulationConfig


@dataclass(slots=True)
class JobSpec:
    """Declarative job description typically produced by parsers or adapters."""

    pid: int
    arrival: int
    burst: int
    priority: int | None = None
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class SimulationRequest:
    """Payload accepted by :class:`SimService.run`."""

    jobs: Iterable[JobSpec]
    algorithm: str
    quantum: int | None = None
    options: Dict[str, object] = field(default_factory=dict)


class SimService:
    """Facade that hides simulator wiring from adapters."""

    def __init__(self, simulator_cls: Type[SchedulerSimulator] = SchedulerSimulator) -> None:
        self.simulator_cls = simulator_cls

    def run(self, request: SimulationRequest) -> SimulationMetrics:
        """
        Execute the simulation for the given request payload.

        # TODO: Flesh out conversion from JobSpec -> PCB, select algorithm, and run simulator.
        """
        algorithm = self._build_algorithm(request)
        sim = self.simulator_cls(SimulationConfig(algorithm=algorithm))
        pcbs: list[PCB] = [self._job_to_pcb(job) for job in request.jobs]
        sim.load_jobs(pcbs)
        # Actual simulator loop not implemented yet, so we return an empty metrics container.
        return SimulationMetrics()

    def _job_to_pcb(self, job: JobSpec) -> PCB:
        """Convert a JobSpec into a PCB instance."""
        pcb = PCB(
            pid=job.pid,
            arrival_time=job.arrival,
            burst_time=job.burst,
            priority=job.priority,
            metadata=job.metadata,
        )
        return pcb

    def _build_algorithm(self, request: SimulationRequest) -> SchedulingAlgorithm:
        """Instantiate the algorithm requested by the caller."""
        algo = request.algorithm.lower()
        if algo == "fcfs":
            return FCFSAlgorithm()
        if algo == "rr":
            if request.quantum is None:
                raise ValueError("Round Robin requires a quantum value.")
            return RoundRobinAlgorithm(request.quantum)
        if algo == "sjf":
            return SJFAlgorithm()
        raise ValueError(f"Unsupported algorithm '{request.algorithm}'.")
