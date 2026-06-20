import sys

from PySide6.QtWidgets import QApplication

from ui.settings import ConfigEditorWindow


def main():
    app = QApplication(sys.argv)
    window = ConfigEditorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
