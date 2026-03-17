"""Bridge Python logging to Qt: thread-safe handler and level-to-color mapping for UI log panes."""

from __future__ import annotations

import logging

from qtpy.QtCore import QObject, Signal  # pyright: ignore[reportPrivateImportUsage]

# Log level to CSS/text color name for use in rich text (theme-friendly)
LEVEL_COLORS: dict[int, str] = {
    logging.DEBUG: "#6b9080",      # muted cyan/teal
    logging.INFO: "inherit",       # default text
    logging.WARNING: "#b0892a",    # amber
    logging.ERROR: "#c53030",     # red
    logging.CRITICAL: "#9b2c2c",  # strong red
}


class LogRecordEmitter(QObject):
    """Emits log record data so UI can append on the main thread (QueuedConnection)."""

    record_emitted = Signal(int, str, str)  # levelno, formatted_message, logger_name


class QtLogHandler(logging.Handler):
    """Logging handler that forwards records to a Qt signal for UI display."""

    def __init__(self, emitter: LogRecordEmitter) -> None:
        super().__init__()
        self._emitter = emitter

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self._emitter.record_emitted.emit(record.levelno, msg, record.name)
        except Exception:  # noqa: BLE001
            self.handleError(record)
