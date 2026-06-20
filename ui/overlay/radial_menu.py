import math

from PySide6.QtCore import QEvent, Signal
from PySide6.QtWidgets import QWidget

from models import ConfigModel
from ui.overlay.button import RadialMenuButton


class RadialMenu(QWidget):
    button_clicked = Signal(int)

    def __init__(self, config: ConfigModel, parent=None):
        super().__init__(parent)
        self.config = config

        size = (config.radius + config.button_size) * 2
        self.setFixedSize(size, size)
        self.setMouseTracking(True)

        self._hovered_btn: RadialMenuButton | None = None
        self.buttons: list[RadialMenuButton] = []

        for i, button in enumerate(config.buttons):
            btn = RadialMenuButton(button, self, size=config.button_size)
            btn.setStyleSheet(config.button_style)
            btn.clicked.connect(lambda checked=False, idx=i: self.button_clicked.emit(idx))
            angle = (2 * math.pi * i / config.buttons_amount) - math.pi / 2
            btn.set_shifts(angle, config.radius)
            self.buttons.append(btn)

        self._position_buttons()

    def _position_buttons(self):
        center = self.rect().center()
        for btn in self.buttons:
            btn.move(center.x() + btn.x_shift, center.y() + btn.y_shift)
            btn.resize(self.config.button_size, self.config.button_size)

    def _sector_at(self, cursor_pos) -> int | None:
        center = self.mapToGlobal(self.rect().center())
        dx = cursor_pos.x() - center.x()
        dy = cursor_pos.y() - center.y()
        dist = (dx * dx + dy * dy) ** 0.5

        if dist < self.config.dead_zone:
            return None

        angle = (math.degrees(math.atan2(dy, dx)) + 90) % 360
        n = self.config.buttons_amount
        if n == 0:
            return None
        sector_size = 360 / n
        return int((angle + sector_size / 2) / sector_size) % n

    def hover_at(self, cursor_pos):
        idx = self._sector_at(cursor_pos)
        hit = self.buttons[idx] if idx is not None else None

        if hit is not self._hovered_btn:
            if self._hovered_btn is not None:
                self._hovered_btn.animate(1.0)
            if hit is not None:
                hit.animate(1.18)
            self._hovered_btn = hit

    def drag_select(self, cursor_pos) -> bool:
        idx = self._sector_at(cursor_pos)
        if idx is not None:
            self.button_clicked.emit(idx)
            return True
        return False

    def reset(self):
        self._hovered_btn = None
        self._position_buttons()

    def mouseMoveEvent(self, event):
        self.hover_at(event.globalPosition().toPoint())

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseMove:
            self.hover_at(event.globalPosition().toPoint())
        return False