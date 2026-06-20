import inspect

from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QLineEdit,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from actions import ActionFactory


def _registry_types() -> list[tuple[str | None, str, list[str]]]:
    entries = []
    for type_key, action_class in ActionFactory._registry.items():
        sig = inspect.signature(action_class.__init__)
        fields = [n for n in sig.parameters if n != "self"]
        label = type_key.replace("_", " ").title()
        entries.append((type_key, label, fields))
    entries.append((None, "String (legacy)", ["value"]))
    return entries


class ActionEditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._types = _registry_types()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel("Type"))
        self.type_combo = QComboBox()
        for _, label, _ in self._types:
            self.type_combo.addItem(label)
        layout.addWidget(self.type_combo)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        for _, _, fields in self._types:
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setContentsMargins(0, 0, 0, 0)
            for field in fields:
                page_layout.addWidget(QLabel(field.replace("_", " ").capitalize()))
                page_layout.addWidget(QLineEdit())
            page_layout.addStretch()
            self.stack.addWidget(page)

        self.type_combo.currentIndexChanged.connect(self.stack.setCurrentIndex)

    def _inputs_for(self, page_index: int) -> list[QLineEdit]:
        return self.stack.widget(page_index).findChildren(QLineEdit)

    def _index_for_key(self, type_key: str | None) -> int:
        for i, (key, _, _) in enumerate(self._types):
            if key == type_key:
                return i
        return len(self._types) - 1

    def set_action(self, action: dict | str):
        if isinstance(action, str):
            idx = self._index_for_key(None)
            self.type_combo.setCurrentIndex(idx)
            inputs = self._inputs_for(idx)
            if inputs:
                inputs[0].setText(action)
            return

        idx = self._index_for_key(action.get("type"))
        self.type_combo.setCurrentIndex(idx)
        _, _, fields = self._types[idx]
        for field, inp in zip(fields, self._inputs_for(idx)):
            inp.setText(str(action.get(field, "")))

    def get_action(self) -> dict | str:
        idx = self.type_combo.currentIndex()
        type_key, _, fields = self._types[idx]
        inputs = self._inputs_for(idx)

        if type_key is None:
            return inputs[0].text() if inputs else ""

        return {"type": type_key, **{f: inp.text() for f, inp in zip(fields, inputs)}}
