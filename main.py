import math
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon

from config import load_config
from mouse_listener import MouseListener
from ui.overlay import RadialOverlay
from ui.settings import ConfigEditorWindow


def _make_tray_icon() -> QIcon:
    px = QPixmap(64, 64)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor("#5b8dd9"))
    p.setPen(Qt.NoPen)
    p.drawEllipse(2, 2, 60, 60)
    p.setBrush(QColor("white"))
    for i in range(8):
        angle = math.radians(i * 45 - 90)
        cx = 32 + int(22 * math.cos(angle))
        cy = 32 + int(22 * math.sin(angle))
        p.drawEllipse(cx - 5, cy - 5, 10, 10)
    p.end()
    return QIcon(px)


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config = load_config()
    overlay = RadialOverlay(config)

    listener = MouseListener()
    listener.thumb_down.connect(overlay.show_at_cursor)
    listener.thumb_up.connect(overlay.on_thumb_up)
    listener.start()
    app.aboutToQuit.connect(listener.stop)

    settings_window: ConfigEditorWindow | None = None

    def open_settings():
        nonlocal settings_window
        if settings_window is None:
            settings_window = ConfigEditorWindow()
            settings_window.config_saved.connect(overlay.reload)
        settings_window.show()
        settings_window.raise_()
        settings_window.activateWindow()

    def show_about():
        QMessageBox.about(
            None,
            "About Haptic Overlay",
            "<b>Haptic Overlay</b><br><br>"
            "A radial menu overlay triggered by haptic device input.<br><br>"
            "Click a button in the radial menu to trigger its action.",
        )

    tray = QSystemTrayIcon(_make_tray_icon(), app)
    tray.setToolTip("Haptic Overlay")

    tray_menu = QMenu()
    tray_menu.addAction("Settings", open_settings)
    tray_menu.addAction("About", show_about)
    tray_menu.addSeparator()
    tray_menu.addAction("Exit", app.quit)

    tray.setContextMenu(tray_menu)
    tray.activated.connect(
        lambda reason: open_settings()
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick
        else None
    )
    tray.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()