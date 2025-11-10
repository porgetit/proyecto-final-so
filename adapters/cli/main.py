"""Command line interface for the scheduler + filesystem MVP."""

from __future__ import annotations

import argparse
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

    # TODO: Implement CSV/JSON parsing according to the README scenarios.
    """
    if not path.exists():
        raise FileNotFoundError(f"Scenario file '{path}' does not exist.")
    return []


def format_metrics(metrics: SimulationMetrics) -> str:
    """
    Render simulation metrics for terminal output.

    # TODO: Replace placeholder string once metrics aggregation is implemented.
    """
    _ = metrics
    return "Simulation metrics are not available yet (MVP scaffold)."


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
    """Minimal REPL loop that proxies commands to FsService."""
    print("Entering virtual filesystem shell. Type 'exit' to leave.")
    while True:
        try:
            raw = input("fs> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not raw:
            continue
        if raw in {"exit", "quit"}:
            break
        command, *arguments = raw.split()
        try:
            output = service.execute(command, arguments)
            if output:
                print(output)
        except Exception as exc:  # pragma: no cover - placeholder error path
            print(f"Error: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
