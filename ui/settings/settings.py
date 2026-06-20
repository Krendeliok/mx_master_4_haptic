import json

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from config import CONFIG_FILE, CONFIG_DIR
from models import ConfigModel, ButtonConfigModel
from ui.overlay.radial_menu import RadialMenu
from ui.settings.actions_editor import ActionEditorWidget


class ConfigEditorWindow(QMainWindow):
    config_saved = Signal(ConfigModel)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Haptic Overlay — Settings")
        self.setMinimumSize(720, 520)

        self._buttons_data: list[ButtonConfigModel] = []
        self._selected_idx: int | None = None
        self.preview_menu: RadialMenu | None = None

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setSpacing(8)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_general_tab(), "General")
        self.tabs.addTab(self._build_buttons_tab(), "Buttons")
        root_layout.addWidget(self.tabs)
        root_layout.addLayout(self._build_footer())

        self.setCentralWidget(root)
        self._load()

    # ------------------------------------------------------------------ tabs

    def _build_general_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self._build_general_group())
        layout.addWidget(self._build_style_group())
        return tab

    def _build_buttons_tab(self) -> QWidget:
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        content_row = QHBoxLayout()

        # Left: radial menu preview
        self.menu_container = QWidget()
        self.menu_container.setMinimumSize(380, 380)
        self.menu_container_layout = QVBoxLayout(self.menu_container)
        self.menu_container_layout.setAlignment(Qt.AlignCenter)
        content_row.addWidget(self.menu_container, stretch=1)

        # Right: sidebar (hidden until a button is selected)
        self.sidebar = self._build_sidebar()
        self.sidebar.setFixedWidth(270)
        self.sidebar.setVisible(False)
        content_row.addWidget(self.sidebar)

        tab_layout.addLayout(content_row)

        toolbar = QHBoxLayout()
        add_btn = QPushButton("Add button")
        add_btn.clicked.connect(self._add_button)
        self.remove_btn = QPushButton("Remove button")
        self.remove_btn.clicked.connect(self._remove_button)
        toolbar.addWidget(add_btn)
        toolbar.addWidget(self.remove_btn)
        toolbar.addStretch()
        tab_layout.addLayout(toolbar)

        return tab

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        layout = QVBoxLayout(sidebar)
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(QLabel("Label"))
        self.sidebar_label = QLineEdit()
        layout.addWidget(self.sidebar_label)

        action_group = QGroupBox("Action")
        action_layout = QVBoxLayout(action_group)
        self.action_editor = ActionEditorWidget()
        action_layout.addWidget(self.action_editor)
        layout.addWidget(action_group)

        return sidebar

    # ------------------------------------------------------------------ general / style groups

    def _build_general_group(self) -> QGroupBox:
        box = QGroupBox("General")
        form = QFormLayout(box)

        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(40, 600)
        form.addRow("Radius:", self.radius_spin)

        self.button_size_spin = QSpinBox()
        self.button_size_spin.setRange(24, 300)
        form.addRow("Button size:", self.button_size_spin)

        self.drag_threshold_spin = QSpinBox()
        self.drag_threshold_spin.setRange(0, 100)
        form.addRow("Drag threshold:", self.drag_threshold_spin)

        self.dead_zone_spin = QSpinBox()
        self.dead_zone_spin.setRange(0, 200)
        form.addRow("Dead zone:", self.dead_zone_spin)

        return box

    def _build_style_group(self) -> QGroupBox:
        box = QGroupBox("Button style (CSS)")
        layout = QVBoxLayout(box)
        self.style_edit = QTextEdit()
        self.style_edit.setFixedHeight(120)
        layout.addWidget(self.style_edit)
        return box

    def _build_footer(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self._load)
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save)
        row.addWidget(cancel_btn)
        row.addWidget(save_btn)
        return row

    # ------------------------------------------------------------------ load / save

    def _load(self):
        try:
            with open(CONFIG_FILE) as f:
                data = ConfigModel.model_validate_json(f.read())
        except Exception as e:
            QMessageBox.critical(self, "Load error", str(e))
            return

        self.radius_spin.setValue(data.radius)
        self.button_size_spin.setValue(data.button_size)
        self.drag_threshold_spin.setValue(data.drag_threshold)
        self.dead_zone_spin.setValue(data.dead_zone)
        self.style_edit.setPlainText(data.button_style)

        self._buttons_data = data.buttons
        self._selected_idx = None
        self.sidebar.setVisible(False)
        self._rebuild_preview()

    def _save(self):
        self._flush_sidebar()
        data = {
            "radius": self.radius_spin.value(),
            "button_size": self.button_size_spin.value(),
            "drag_threshold": self.drag_threshold_spin.value(),
            "dead_zone": self.dead_zone_spin.value(),
            "button_style": self.style_edit.toPlainText(),
            "buttons": [b.model_dump() for b in self._buttons_data],
        }
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f, indent="\t")
        except Exception as e:
            QMessageBox.critical(self, "Save error", str(e))
            return

        self._rebuild_preview()
        config = self._build_preview_config()
        if config:
            self.config_saved.emit(config)
        QMessageBox.information(self, "Saved", "Config saved.")

    # ------------------------------------------------------------------ preview

    def _build_preview_config(self) -> ConfigModel | None:
        try:
            return ConfigModel(
                radius=self.radius_spin.value(),
                button_size=self.button_size_spin.value(),
                drag_threshold=self.drag_threshold_spin.value(),
                dead_zone=self.dead_zone_spin.value(),
                button_style=self.style_edit.toPlainText(),
                buttons=self._buttons_data,
            )
        except Exception:
            return None

    def _rebuild_preview(self):
        if self.preview_menu is not None:
            self.preview_menu.button_clicked.disconnect()
            self.preview_menu.setParent(None)
            self.preview_menu.deleteLater()
            self.preview_menu = None

        config = self._build_preview_config()
        if not config or not config.buttons:
            return

        menu = RadialMenu(config)
        menu.button_clicked.connect(self._on_button_selected)
        self.menu_container_layout.addWidget(menu)
        self.menu_container_layout.setAlignment(menu, Qt.AlignCenter)
        self.preview_menu = menu

    # ------------------------------------------------------------------ sidebar

    def _on_button_selected(self, idx: int):
        self._flush_sidebar()
        self._selected_idx = idx
        btn = self._buttons_data[idx]

        self.sidebar_label.blockSignals(True)
        self.sidebar_label.setText(btn.label)
        self.sidebar_label.blockSignals(False)

        self.action_editor.set_action(btn.action)
        self.sidebar.setVisible(True)

    def _flush_sidebar(self):
        if self._selected_idx is None or not self.sidebar.isVisible():
            return
        self._buttons_data[self._selected_idx] = ButtonConfigModel(
            label=self.sidebar_label.text(),
            action=self.action_editor.get_action(),
        )

    # ------------------------------------------------------------------ add / remove

    def _add_button(self):
        self._flush_sidebar()
        self._buttons_data.append(ButtonConfigModel(label="New", action=""))
        self._rebuild_preview()
        self._on_button_selected(len(self._buttons_data) - 1)

    def _remove_button(self):
        if self._selected_idx is None:
            return
        self._buttons_data.pop(self._selected_idx)
        self._selected_idx = None
        self.sidebar.setVisible(False)
        self._rebuild_preview()
