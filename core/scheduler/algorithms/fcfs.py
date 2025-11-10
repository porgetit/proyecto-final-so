"""First-Come First-Served scheduling algorithm."""

from __future__ import annotations

from typing import Iterable

from ..pcb import PCB
from ..queues import ReadyQueue
from .base import SchedulingAlgorithm, SchedulingDecision


class FCFSAlgorithm(SchedulingAlgorithm):
    """Non-preemptive FCFS implementation."""

    name = "fcfs"

    def reset(self) -> None:
        """No internal state yet, but method provided for symmetry."""

    def prime(self, ready_queue: ReadyQueue, jobs: Iterable[PCB]) -> None:
        """Load jobs in arrival order."""
        ready_queue.extend(sorted(jobs, key=lambda pcb: pcb.arrival_time))

    def next_tick(
        self,
        *,
        current_time: int,  # noqa: ARG002 - kept for future logic
        running: PCB | None,
        ready_queue: ReadyQueue,
    ) -> SchedulingDecision:
        """FCFS always selects the head of the ready queue."""
        # TODO: Implement FCFS logic (handle idle CPU, completion, metrics, etc.).
        raise NotImplementedError("FCFS decision logic not implemented yet.")
