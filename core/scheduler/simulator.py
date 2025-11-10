"""High-level orchestration of the CPU scheduling simulation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

from .algorithms.base import SchedulingAlgorithm
from .metrics import SimulationMetrics
from .pcb import PCB
from .queues import BlockedQueue, ReadyQueue


@dataclass
class SimulationConfig:
    """Configuration knobs shared by every algorithm."""

    algorithm: SchedulingAlgorithm
    time_slice: int | None = None
    max_time: int | None = None


class SchedulerSimulator:
    """Coordinates queues, algorithm decisions and bookkeeping."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.ready_queue = ReadyQueue()
        self.blocked_queue = BlockedQueue()
        self.clock: int = 0
        self.completed: List[PCB] = []
        self._jobs: list[PCB] = []

    def load_jobs(self, jobs: Sequence[PCB] | Iterable[PCB]) -> None:
        """Reset internal state and register the PCBs to simulate."""
        self.clock = 0
        self.ready_queue = ReadyQueue()
        self.blocked_queue = BlockedQueue()
        self.completed = []
        self._jobs = list(jobs)
        self._jobs.sort(key=lambda pcb: pcb.arrival_time)

    def run(self) -> SimulationMetrics:
        """
        Execute the simulation using the configured algorithm.

        # TODO: Implement the discrete-event loop that feeds processes into the
        # ready queue, applies algorithm decisions, and records metrics.
        """
        return SimulationMetrics()
