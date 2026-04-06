"""Shared helpers for GIT instance property dialogs."""

from __future__ import annotations

from pykotor.common.misc import ResRef


def parse_resref_field(text: str) -> tuple[ResRef | None, str | None]:
    """Return (ResRef, None) on success, or (None, error_message)."""
    stripped: str = text.strip()
    if not stripped:
        return ResRef.from_blank(), None
    if not ResRef.is_valid(stripped):
        return (
            None,
            'Resref must be ASCII, at most 16 characters, and must not contain \\ / : * ? " < > |',
        )
    return ResRef(stripped), None
