"""Command line interface for the scheduler + filesystem MVP."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Callable, Sequence

from core.fs.models import Directory, User
from core.fs.permissions import PermissionSet
from core.scheduler.metrics import SimulationMetrics
from core.services import FsService, SimService
from core.services.sim_service import JobSpec, SimulationRequest


def build_parser() -> argparse.ArgumentParser:
    """Create the top-level CLI parser with its subcommands."""
    parser = argparse.ArgumentParser(
        description="CPU scheduler simulator and virtual filesystem shell."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sim_parser = subparsers.add_parser("sim", help="Run a scheduling simulation.")
    sim_parser.add_argument(
        "--algo",
        choices=["fcfs", "rr", "sjf"],
        required=True,
        help="Scheduling algorithm to use.",
    )
    sim_parser.add_argument(
        "--quantum",
        type=int,
        default=None,
        help="Quantum for Round Robin (ignored otherwise).",
    )
    sim_parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to the scenario file (CSV/JSON).",
    )
    sim_parser.set_defaults(handler=handle_sim_command)

    fs_parser = subparsers.add_parser(
        "fs",
        help="Start an interactive shell for the virtual filesystem.",
    )
    fs_parser.add_argument(
        "--user",
        type=str,
        default="user",
        help="Username for the filesystem session.",
    )
    fs_parser.set_defaults(handler=handle_fs_command)

    return parser


def _load_jobs_from_csv(path: Path) -> list[JobSpec]:
    """Parse jobs from CSV format: pid,arrival_time,burst_time[,priority]"""
    jobs = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for line_num, row in enumerate(reader, 1):
            # Skip empty lines and comments
            if not row or (row[0] and row[0].strip().startswith('#')):
                continue
                
            try:
                if len(row) < 3:
                    print(f"Warning: Line {line_num} has insufficient columns, skipping")
                    continue
                
                pid = int(row[0].strip())
                arrival = int(row[1].strip())
                burst = int(row[2].strip())
                priority = int(row[3].strip()) if len(row) > 3 and row[3].strip() else None
                
                jobs.append(JobSpec(
                    pid=pid,
                    arrival=arrival,
                    burst=burst,
                    priority=priority
                ))
            except ValueError as e:
                print(f"Warning: Line {line_num} has invalid data ({e}), skipping")
                continue
    
    return jobs


def _load_jobs_from_json(path: Path) -> list[JobSpec]:
    """Parse jobs from JSON format: [{"pid": int, "arrival": int, "burst": int, "priority": int?}]"""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        raise ValueError("JSON file must contain an array of job objects")
    
    jobs = []
    for i, job_data in enumerate(data):
        if not isinstance(job_data, dict):
            print(f"Warning: Item {i} is not an object, skipping")
            continue
            
        try:
            jobs.append(JobSpec(
                pid=int(job_data.get('pid', i + 1)),
                arrival=int(job_data.get('arrival', 0)),
                burst=int(job_data.get('burst', 1)),
                priority=int(job_data['priority']) if job_data.get('priority') is not None else None
            ))
        except (ValueError, KeyError) as e:
            print(f"Warning: Item {i} has invalid data ({e}), skipping")
            continue
    
    return jobs


def _print_fs_help() -> None:
    """Print help for filesystem commands."""
    help_text = """
FILESYSTEM COMMANDS:
    ls [path]           - List directory contents
    cd <path>           - Change current directory
    pwd                 - Show current directory
    mkdir <path>        - Create directory
    touch <path>        - Create empty file or update timestamps
    cat <path>          - Display file contents
    write <path> <text> - Write text to file
    rm <path>           - Remove file or directory
    tree                - Show directory tree structure
    help                - Show this help message
    exit                - Exit filesystem shell

EXAMPLES:
    mkdir docs
    cd docs
    touch readme.txt
    write readme.txt "Hello World"
    cat readme.txt
    cd ..
    rm docs/readme.txt
"""
    print(help_text)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point invoked by `python -m adapters.cli.main`."""
    parser = build_parser()
    args = parser.parse_args(argv)
    handler: Callable[[argparse.Namespace], int] | None = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 1
    return handler(args)


def handle_sim_command(args: argparse.Namespace) -> int:
    """Dispatch the sim subcommand to the scheduler service."""
    sim_service = SimService()
    jobs = load_jobs_from_path(Path(args.input))
    request = SimulationRequest(
        jobs=jobs,
        algorithm=args.algo,
        quantum=args.quantum,
    )
    metrics = sim_service.run(request)
    print(format_metrics(metrics))
    return 0


def handle_fs_command(args: argparse.Namespace) -> int:
    """Launch a minimal REPL that uses FsService for each command."""
    service = bootstrap_fs_service(username=args.user)
    filesystem_shell(service)
    return 0


def load_jobs_from_path(path: Path) -> list[JobSpec]:
    """
    Load job definitions from disk.
    
    Supports CSV format: pid,arrival_time,burst_time[,priority]
    Supports JSON format: [{"pid": int, "arrival": int, "burst": int, "priority": int?}]
    """
    if not path.exists():
        raise FileNotFoundError(f"Scenario file '{path}' does not exist.")
    
    jobs = []
    
    if path.suffix.lower() == '.csv':
        jobs = _load_jobs_from_csv(path)
    elif path.suffix.lower() == '.json':
        jobs = _load_jobs_from_json(path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}. Use .csv or .json")
    
    if not jobs:
        raise ValueError(f"No valid jobs found in {path}")
    
    return jobs


def format_metrics(metrics: SimulationMetrics) -> str:
    """
    Render simulation metrics for terminal output.
    """
    if not metrics.processes:
        return "No process metrics available (simulation may not have run properly)."
    
    output = []
    output.append("=" * 80)
    output.append("SIMULATION RESULTS")
    output.append("=" * 80)
    
    # Process metrics table
    output.append("\nPER-PROCESS METRICS:")
    output.append("-" * 60)
    output.append(f"{'PID':<5} {'Wait Time':<12} {'Turnaround':<12} {'Response':<10}")
    output.append("-" * 60)
    
    for proc in metrics.processes:
        wait = f"{proc.waiting_time:.1f}" if proc.waiting_time is not None else "N/A"
        turnaround = f"{proc.turnaround_time:.1f}" if proc.turnaround_time is not None else "N/A"
        response = f"{proc.response_time:.1f}" if proc.response_time is not None else "N/A"
        output.append(f"{proc.pid:<5} {wait:<12} {turnaround:<12} {response:<10}")
    
    # System metrics
    output.append("\nSYSTEM METRICS:")
    output.append("-" * 30)
    if metrics.throughput is not None:
        output.append(f"Throughput: {metrics.throughput:.2f} processes/unit")
    if metrics.cpu_utilization is not None:
        output.append(f"CPU Utilization: {metrics.cpu_utilization:.1f}%")
    output.append(f"Context Switches: {metrics.context_switches}")
    
    # Average calculations
    if metrics.processes:
        wait_times = [p.waiting_time for p in metrics.processes if p.waiting_time is not None]
        turnaround_times = [p.turnaround_time for p in metrics.processes if p.turnaround_time is not None]
        response_times = [p.response_time for p in metrics.processes if p.response_time is not None]
        
        if wait_times:
            avg_wait = sum(wait_times) / len(wait_times)
            output.append(f"Average Waiting Time: {avg_wait:.2f}")
        if turnaround_times:
            avg_turnaround = sum(turnaround_times) / len(turnaround_times)
            output.append(f"Average Turnaround Time: {avg_turnaround:.2f}")
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            output.append(f"Average Response Time: {avg_response:.2f}")
    
    output.append("=" * 80)
    return "\n".join(output)


def bootstrap_fs_service(*, username: str) -> FsService:
    """Create a fresh FsService with a root directory for the given user."""
    user = User(username=username)
    root = Directory(
        name="",
        owner=user,
        permissions=PermissionSet.from_string("rwx"),
    )
    return FsService(root=root, user=user)


def filesystem_shell(service: FsService) -> None:
    """Interactive REPL loop for the virtual filesystem."""
    print("=" * 60)
    print("Virtual Filesystem Shell")
    print("Available commands: ls, cd, pwd, mkdir, touch, cat, write, rm, tree, help, exit")
    print("Type 'help' for command usage or 'exit' to leave.")
    print("=" * 60)
    
    current_path = "/"
    
    while True:
        try:
            prompt = f"fs:{current_path}> "
            raw = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting filesystem shell...")
            break
        
        if not raw:
            continue
            
        if raw in {"exit", "quit"}:
            print("Goodbye!")
            break
            
        if raw == "help":
            _print_fs_help()
            continue
            
        if raw == "pwd":
            print(current_path)
            continue
            
        parts = raw.split()
        command = parts[0]
        arguments = parts[1:]
        
        try:
            if command == "cd":
                # Handle cd specially to update prompt
                result = service.execute(command, arguments)
                if result:  # cd should return the new path
                    current_path = result if result != "" else "/"
                    print(f"Changed to: {current_path}")
            else:
                output = service.execute(command, arguments)
                if output:
                    print(output)
                    
        except Exception as exc:
            print(f"Error: {exc}")
            if command not in ["ls", "cd", "pwd", "mkdir", "touch", "cat", "write", "rm", "tree"]:
                print(f"Unknown command '{command}'. Type 'help' for available commands.")


if __name__ == "__main__":
    raise SystemExit(main())
