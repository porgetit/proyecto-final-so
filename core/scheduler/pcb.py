"""Process Control Block definition used by the scheduler."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .states import ProcessState


@dataclass(slots=True)
class PCB:
    """Minimal PCB structure shared by every scheduling algorithm."""

    pid: int
    arrival_time: int
    burst_time: int
    priority: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    remaining_time: int = field(init=False)
    state: ProcessState = field(default=ProcessState.NEW, init=False)
    start_time: int | None = field(default=None, init=False)
    finish_time: int | None = field(default=None, init=False)
    response_time: int | None = field(default=None, init=False)
    waiting_time: int | None = field(default=None, init=False)
    turnaround_time: int | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.remaining_time = self.burst_time

    def set_state(self, state: ProcessState) -> None:
        """Update PCB state; algorithms may hook extra bookkeeping before or after."""
        self.state = state

    def consume(self, time_slice: int) -> None:
        """
        Reduce remaining burst time after execution.

        This function does not validate the time slice, so callers must avoid
        passing values larger than the remaining time.
        """
        self.remaining_time = max(0, self.remaining_time - time_slice)
