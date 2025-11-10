"""Shortest Job First scheduling algorithm (non-preemptive)."""

from __future__ import annotations

from typing import Iterable

from ..pcb import PCB
from ..queues import ReadyQueue
from .base import SchedulingAlgorithm, SchedulingDecision


class SJFAlgorithm(SchedulingAlgorithm):
    """Simple non-preemptive SJF placeholder."""

    name = "sjf"

    def reset(self) -> None:
        """Reset algorithm state between runs."""
        # SJF uses no additional state yet.

    def prime(self, ready_queue: ReadyQueue, jobs: Iterable[PCB]) -> None:
        """Load all available jobs before the simulation starts."""
        ready_queue.extend(sorted(jobs, key=lambda pcb: pcb.burst_time))

    def next_tick(
        self,
        *,
        current_time: int,  # noqa: ARG002 - reserved for stats
        running: PCB | None,
        ready_queue: ReadyQueue,
    ) -> SchedulingDecision:
        """Pick the job with the shortest remaining burst."""
        # TODO: Implement SJF selection and completion handling.
        raise NotImplementedError("SJF decision logic not implemented yet.")
