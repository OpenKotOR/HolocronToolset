"""Prefer standalone app-process-lifecycle; fall back to in-tree utility.system.app_process."""

from __future__ import annotations

try:
    from app_process_lifecycle.shutdown import (
        gracefully_shutdown_threads,
        start_shutdown_process,
        terminate_child_processes,
        terminate_main_process,
    )
except ImportError:  # pragma: no cover - fallback while pykotor still vendors app_process
    from utility.system.app_process.shutdown import (
        gracefully_shutdown_threads,
        start_shutdown_process,
        terminate_child_processes,
        terminate_main_process,
    )

__all__ = [
    "gracefully_shutdown_threads",
    "start_shutdown_process",
    "terminate_child_processes",
    "terminate_main_process",
]
