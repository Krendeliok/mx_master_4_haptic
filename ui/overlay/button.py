import math

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect
from PySide6.QtWidgets import QPushButton

from models import ButtonConfigModel


class RadialMenuButton(QPushButton):
    x_shift: int
    y_shift: int

    def __init__(
        self,
        button: ButtonConfigModel,
        /,
        parent=None,
        *,
        size: int,
        **kwargs,
    ):
        super().__init__(button.label, parent, **kwargs)
        self.size = size
        self._parent = parent

        self.resize(size, size)
        self.setMouseTracking(True)
        self.installEventFilter(parent)
        self._animation: QPropertyAnimation | None = None

    def set_shifts(self, angle, radius):
        self.x_shift = round(math.cos(angle) * radius - self.size / 2)
        self.y_shift = round(math.sin(angle) * radius - self.size / 2)

    def animate(self, scale):
        if self._animation is not None:
            self._animation.stop()
            self._animation.deleteLater()

        new_size = round(self.size * scale)
        center = self.geometry().center()
        new_x = center.x() - new_size // 2
        new_y = center.y() - new_size // 2

        self._animation = QPropertyAnimation(self, b"geometry", self._parent)
        self._animation.setDuration(120)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        self._animation.setStartValue(self.geometry())
        self._animation.setEndValue(QRect(new_x, new_y, new_size, new_size))
        self._animation.finished.connect(lambda: setattr(self, "_animation", None))
        self._animation.start()