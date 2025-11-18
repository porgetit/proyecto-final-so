import random
import sys
from pathlib import Path

import pytest

# Ensure the scheduler package is importable when tests run from repository root.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from scheduler.algorithms.fcfs import FCFSAlgorithm
from scheduler.algorithms.rr import RoundRobinAlgorithm
from scheduler.algorithms.sjf import SJFAlgorithm
from scheduler.pcb import PCB
from scheduler.simulator import SchedulerSimulator, SimulationConfig


def test_fcfs_runs_in_arrival_order_without_io():
    config = SimulationConfig(algorithm=FCFSAlgorithm(), io_enabled=False)
    sim = SchedulerSimulator(config)
    jobs = [PCB(1, 0, 3), PCB(2, 1, 2), PCB(3, 2, 1)]
    sim.load_jobs(jobs)

    metrics = sim.run()
    results = {m.pid: m for m in metrics.processes}

    assert sim.completed[0].pid == 1
    assert sim.completed[1].pid == 2
    assert sim.completed[2].pid == 3
    # Waiting times derived from classic FCFS timeline.
    assert results[1].waiting_time == 0
    assert results[2].waiting_time == 2
    assert results[3].waiting_time == 3
    assert metrics.context_switches == 3


def test_sjf_picks_shortest_job_first():
    config = SimulationConfig(algorithm=SJFAlgorithm(), io_enabled=False)
    sim = SchedulerSimulator(config)
    jobs = [PCB(1, 0, 5), PCB(2, 0, 2)]
    sim.load_jobs(jobs)

    metrics = sim.run()
    results = {m.pid: m for m in metrics.processes}

    # Job 2 should start immediately; job 1 waits for it to finish.
    assert results[2].waiting_time == 0
    assert results[1].waiting_time == 2
    assert sim.completed[0].pid == 2
    assert sim.completed[1].pid == 1


def test_round_robin_time_slice_override():
    rr = RoundRobinAlgorithm(quantum=5)
    config = SimulationConfig(algorithm=rr, time_slice=2, io_enabled=False)
    sim = SchedulerSimulator(config)
    jobs = [PCB(1, 0, 4), PCB(2, 0, 4)]
    sim.load_jobs(jobs)

    metrics = sim.run()
    results = {m.pid: m for m in metrics.processes}

    # The time slice should override algorithm quantum.
    assert rr.quantum == 2
    # Expected RR behaviour with 2-tick quanta.
    assert results[1].waiting_time == 2
    assert results[2].waiting_time == 4
    assert metrics.context_switches == 4


def test_io_blocking_moves_processes_between_queues():
    random.seed(42)
    config = SimulationConfig(algorithm=FCFSAlgorithm(), io_enabled=False)
    sim = SchedulerSimulator(config)
    job1 = PCB(1, 0, 5, metadata={"io_enabled": False})
    job2 = PCB(2, 1, 2, metadata={"io_enabled": False})
    sim.load_jobs([job1, job2])
    # Manually attach a deterministic I/O schedule for job1.
    job1.io_schedule = [(2, 2)]
    job1._next_io_index = 0  # noqa: SLF001

    metrics = sim.run()
    results = {m.pid: m for m in metrics.processes}

    # Job1 blocks once and resumes after job2 finishes.
    assert results[1].waiting_time == 2
    assert results[1].turnaround_time == 7
    assert len(sim.blocked_queue) == 0
    assert len(sim.ready_queue) == 0
    assert len(sim.completed) == 2


def test_sjf_tie_uses_queue_order_when_bursts_equal():
    config = SimulationConfig(algorithm=SJFAlgorithm(), io_enabled=False)
    sim = SchedulerSimulator(config)
    jobs = [PCB(1, 0, 3), PCB(2, 0, 3)]
    sim.load_jobs(jobs)

    metrics = sim.run()
    results = {m.pid: m for m in metrics.processes}

    # Arrival order preserved on ties; job1 runs first.
    assert sim.completed[0].pid == 1
    assert sim.completed[1].pid == 2
    assert results[1].waiting_time == 0
    assert results[2].waiting_time == 3
    assert metrics.context_switches == 2


def test_max_time_stops_simulation_early():
    config = SimulationConfig(algorithm=FCFSAlgorithm(), max_time=2, io_enabled=False)
    sim = SchedulerSimulator(config)
    sim.load_jobs([PCB(1, 0, 10), PCB(2, 1, 10)])

    metrics = sim.run()

    # No process should complete within 2 ticks of runtime.
    assert len(sim.completed) == 0
    assert metrics.throughput == 0
    assert metrics.cpu_utilization == pytest.approx(1.0)


def test_zero_burst_process_completes_without_error():
    config = SimulationConfig(algorithm=FCFSAlgorithm(), io_enabled=False)
    sim = SchedulerSimulator(config)
    sim.load_jobs([PCB(1, 0, 0)])

    metrics = sim.run()
    results = {m.pid: m for m in metrics.processes}

    # Zero-burst job completes in a single tick in current model.
    assert len(sim.completed) == 1
    assert sim.completed[0].finish_time == 1
    assert results[1].turnaround_time == 1
    assert metrics.cpu_utilization == 1.0
