"""Round Robin scheduling algorithm with configurable quantum."""

from __future__ import annotations

from typing import Iterable

from ..pcb import PCB
from ..queues import ReadyQueue
from .base import SchedulingAlgorithm, SchedulingDecision


class RoundRobinAlgorithm(SchedulingAlgorithm):
    """RR algorithm placeholder."""

    name = "rr"

    def __init__(self, quantum: int) -> None:
        self.quantum = quantum

    def reset(self) -> None:
        """Reset algorithm state between runs."""
        # RR currently keeps no additional state.

    def prime(self, ready_queue: ReadyQueue, jobs: Iterable[PCB]) -> None:
        """Initial load simply enqueues the jobs."""
        ready_queue.extend(sorted(jobs, key=lambda pcb: pcb.arrival_time))

    def next_tick(
        self,
        *,
        current_time: int,  # noqa: ARG002 - reserved for the future
        running: PCB | None,
        ready_queue: ReadyQueue,
    ) -> SchedulingDecision:
        """RR rotates processes after consuming the quantum."""
        # TODO: Implement RR decision and rotation logic.
        raise NotImplementedError("Round Robin decision logic not implemented yet.")
