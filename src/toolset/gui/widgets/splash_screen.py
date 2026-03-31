"""Splash screen for Holocron Toolset startup."""
from __future__ import annotations

from qtpy.QtCore import Qt, QTimer
from qtpy.QtGui import QColor, QFont, QLinearGradient, QPainter, QPixmap
from qtpy.QtWidgets import QProgressBar, QSplashScreen, QVBoxLayout, QLabel, QWidget


class ToolsetSplashScreen(QSplashScreen):
    """Dark splash screen with the Holocron icon and a green loading bar."""

    def __init__(self):
        # Create the splash pixmap
        pixmap = QPixmap(480, 360)
        pixmap.fill(QColor("#0a0a0a"))
        super().__init__(pixmap, Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)

        # Central widget overlay
        self._setupUi()
        self._progress = 0

    def _setupUi(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Spacer to push icon to center area
        layout.addStretch(2)

        # Icon
        iconLabel = QLabel(self)
        iconLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        iconPixmap = QPixmap(":/images/icons/sith.png")
        if not iconPixmap.isNull():
            iconPixmap = iconPixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        iconLabel.setPixmap(iconPixmap)
        iconLabel.setStyleSheet("background: transparent;")
        layout.addWidget(iconLabel)

        layout.addStretch(1)

        # Status message
        self._statusLabel = QLabel("Initializing...", self)
        self._statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._statusLabel.setStyleSheet(
            "color: #aaaaaa; font-size: 10pt; background: transparent; padding: 4px;"
        )
        layout.addWidget(self._statusLabel)

        # Progress bar
        self._progressBar = QProgressBar(self)
        self._progressBar.setRange(0, 100)
        self._progressBar.setValue(0)
        self._progressBar.setTextVisible(False)
        self._progressBar.setFixedHeight(6)
        self._progressBar.setStyleSheet(
            "QProgressBar {"
            "  background-color: #1a1a1a;"
            "  border: none;"
            "  border-radius: 3px;"
            "}"
            "QProgressBar::chunk {"
            "  background-color: #00c853;"
            "  border-radius: 3px;"
            "}"
        )
        layout.addWidget(self._progressBar)

        # Bottom bar with app name
        bottomBar = QWidget(self)
        bottomBar.setFixedHeight(36)
        bottomBar.setStyleSheet("background-color: #1a1a1a;")
        bottomLayout = QVBoxLayout(bottomBar)
        bottomLayout.setContentsMargins(12, 0, 12, 0)
        nameLabel = QLabel("Holocron Toolset", bottomBar)
        nameLabel.setStyleSheet(
            "color: #cccccc; font-size: 11pt; font-weight: bold; background: transparent;"
        )
        nameLabel.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        bottomLayout.addWidget(nameLabel)
        layout.addWidget(bottomBar)

    def setProgress(self, value: int, message: str = ""):
        """Update the progress bar and status message."""
        self._progress = value
        self._progressBar.setValue(value)
        if message:
            self._statusLabel.setText(message)
        self.repaint()

    def drawContents(self, painter: QPainter):
        """Override to prevent default splash message drawing."""
        pass
