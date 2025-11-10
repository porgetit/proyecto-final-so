"""Metrics models produced by the scheduler simulator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List


@dataclass(slots=True)
class ProcessMetrics:
    """Holds the canonical metrics for a single process."""

    pid: int
    waiting_time: float | None = None
    turnaround_time: float | None = None
    response_time: float | None = None


@dataclass(slots=True)
class SimulationMetrics:
    """Aggregated metrics from a scheduler run."""

    processes: List[ProcessMetrics] = field(default_factory=list)
    throughput: float | None = None
    cpu_utilization: float | None = None
    context_switches: int = 0

    def add_process_metrics(self, metrics: ProcessMetrics) -> None:
        """Collect metrics for a single process."""
        self.processes.append(metrics)

    @classmethod
    def from_pcbs(cls, pcbs: Iterable["PCB"]) -> "SimulationMetrics":
        """
        Convenience constructor to build metrics from the final PCB state.

        # TODO: Derive every metric once the simulator logic is available.
        """
        # Local import to avoid circular dependency during skeleton stage.
        from .pcb import PCB  # pylint: disable=cyclic-import

        _ = PCB  # appease linters until implementation arrives
        return cls()
