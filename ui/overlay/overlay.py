from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QWidget

from actions import ActionResolver
from models import ConfigModel
from ui.overlay.radial_menu import RadialMenu


class RadialOverlay(QWidget):
    def __init__(self, config: ConfigModel):
        super().__init__()

        self.config = config

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.menu = RadialMenu(config, self)
        self.resize(self.menu.size())

        self._press_pos = None
        self.menu.button_clicked.connect(self._on_button_clicked)

        self.hide()

    def reload(self, config: ConfigModel):
        self.hide()
        self.config = config
        old_menu = self.menu
        self.menu = RadialMenu(config, self)
        self.menu.button_clicked.connect(self._on_button_clicked)
        self.resize(self.menu.size())
        old_menu.button_clicked.disconnect()
        old_menu.setParent(None)
        old_menu.deleteLater()

    def _on_button_clicked(self, idx: int):
        ActionResolver.resolve(self.config.buttons[idx].action).execute()
        self.hide()

    def show_at_cursor(self):
        if self.isVisible():
            self._press_pos = None
            self.hide()
            return

        cursor_pos = QCursor.pos()
        self._press_pos = cursor_pos

        self.move(
            cursor_pos.x() - self.width() // 2,
            cursor_pos.y() - self.height() // 2,
        )

        self.menu.reset()
        self.show()
        self.raise_()
        self.activateWindow()

    def on_thumb_up(self):
        if not self.isVisible():
            return

        cursor_pos = QCursor.pos()

        if self._press_pos is not None:
            dx = cursor_pos.x() - self._press_pos.x()
            dy = cursor_pos.y() - self._press_pos.y()
            moved = (dx * dx + dy * dy) ** 0.5
            if moved < self.config.drag_threshold:
                return

        if not self.menu.drag_select(cursor_pos):
            self.hide()

    def changeEvent(self, event):
        if event.type() == QEvent.Type.ActivationChange and not self.isActiveWindow():
            self.hide()

    def mousePressEvent(self, event):
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()