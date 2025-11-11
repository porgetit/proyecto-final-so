"""Bootstrap for the PyWebview-powered GUI."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Iterable

import webview

from core.fs.models import Directory, User
from core.fs.permissions import PermissionSet
from core.services import FsService, SimService
from core.services.sim_service import JobSpec, SimulationRequest


def launch_app() -> None:
    """Create the PyWebview window and start the GUI loop."""
    bridge = AppBridge()
    html_path = Path(__file__).resolve().parent / "web" / "index.html"
    if not html_path.exists():
        raise FileNotFoundError(f"UI file not found: {html_path}")
    window = webview.create_window(
        "Process Planner + Virtual FS",
        url=html_path.as_uri(),
        js_api=bridge,
    )
    webview.start(gui="edgechromium", debug=False)


class AppBridge:
    """
    API exposed to the WebView frontend.

    Methods defined here are callable from JavaScript via `window.pywebview.api`.
    """

    def __init__(self) -> None:
        self.sim_service = SimService()
        self.fs_service = self._bootstrap_fs_service(username="webuser")

    def run_simulation(self, payload: dict) -> dict:
        """Invoke the scheduler service using the payload provided by the UI."""
        try:
            request = self._payload_to_request(payload)
            metrics = self.sim_service.run(request)
            return {"ok": True, "metrics": asdict(metrics)}
        except Exception as exc:  # pragma: no cover - UI error path
            return {"ok": False, "error": str(exc)}

    def execute_fs(self, command: str, args: Iterable[str] | None = None) -> dict:
        """Proxy filesystem commands to the FsService."""
        args = list(args or [])
        try:
            output = self.fs_service.execute(command, args)
            return {"ok": True, "output": output}
        except Exception as exc:  # pragma: no cover - UI error path
            return {"ok": False, "error": str(exc)}

    def _payload_to_request(self, payload: dict) -> SimulationRequest:
        """Convert the payload dictionary into a SimulationRequest."""
        jobs_data = payload.get("jobs") or []
        jobs = [
            JobSpec(
                pid=int(job.get("pid", idx + 1)),
                arrival=int(job.get("arrival", 0)),
                burst=int(job.get("burst", 1)),
                priority=int(job["priority"]) if job.get("priority") is not None else None,
                metadata={"source": "webview"},
            )
            for idx, job in enumerate(jobs_data)
        ]
        return SimulationRequest(
            jobs=jobs,
            algorithm=str(payload.get("algorithm", "fcfs")),
            quantum=payload.get("quantum"),
            options=payload.get("options", {}),
        )

    def _bootstrap_fs_service(self, *, username: str) -> FsService:
        """Create a filesystem service rooted at / for the given user."""
        user = User(username=username)
        root = Directory(
            name="",
            owner=user,
            permissions=PermissionSet.from_string("rwx"),
        )
        return FsService(root=root, user=user)


if __name__ == "__main__":
    launch_app()
