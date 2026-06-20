from evdev import InputDevice, ecodes, list_devices
from PySide6.QtCore import QThread, Signal

THUMB_BUTTON = ecodes.BTN_BACK


def find_device() -> InputDevice:
    for path in list_devices():
        try:
            device = InputDevice(path)
            caps = device.capabilities()
            has_thumb_button = THUMB_BUTTON in caps.get(ecodes.EV_KEY, [])
            has_pointer = ecodes.EV_REL in caps
            if has_thumb_button and has_pointer:
                return device
        except (PermissionError, OSError):
            continue
    raise RuntimeError(
        "No pointing device with BTN_BACK found. "
        "Check that your device is connected and you have read permission on /dev/input/."
    )


class MouseListener(QThread):
    thumb_down = Signal()
    thumb_up = Signal()

    def __init__(self, device_path: str | None = None):
        super().__init__()
        self._device = InputDevice(device_path) if device_path else find_device()

    def stop(self):
        self._device.close()
        self.wait()

    def run(self):
        print(f"Listening on {self._device.path}: {self._device.name}")

        try:
            for event in self._device.read_loop():
                if event.type == ecodes.EV_KEY and event.code == THUMB_BUTTON:
                    if event.value == 1:
                        self.thumb_down.emit()
                    elif event.value == 0:
                        self.thumb_up.emit()
        except OSError:
            pass
