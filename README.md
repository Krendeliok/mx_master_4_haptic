# Haptic Overlay

A Linux radial menu overlay triggered by the mouse thumb button (back button). Hold the thumb button, move the cursor toward a segment, and release to execute the bound action — all without lifting your hand off the mouse.

![radial menu concept: buttons arranged in a circle around the cursor](https://placeholder)

## Features

- Radial menu appears at the cursor position when the thumb button is held
- Drag-to-select: release over a segment to trigger it; release in the center dead zone to cancel
- Configurable number of buttons, radius, size, and CSS styling
- Actions per button: run a shell command, open a URL, or add your own action type
- System tray icon with quick access to Settings and Exit
- Settings window with live radial preview
- Hot-reload: config changes apply immediately, no restart needed
- Auto-detects your mouse — no hardcoded device paths

## Requirements

- Linux (uses `/dev/input` via `evdev`)
- Python 3.14+
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- A mouse with a thumb/back button (`BTN_BACK`)
- Membership in the `input` group (see below)

## Installation

```bash
git clone <repo-url>
cd haptic_overlay
./install.sh
```

The script:
1. Builds and installs the package with `uv tool install`
2. Creates `~/.config/autostart/haptic-overlay.desktop` so the overlay starts on login

### Input group permission

The overlay reads raw input events. Without the right permissions it cannot see your mouse buttons:

```bash
sudo usermod -aG input $USER
```

Log out and back in once for the change to take effect. The install script will warn you if this is needed.

## Running

```bash
haptic-overlay           # start the overlay (system tray)
haptic-overlay-settings  # open settings directly
```

The overlay runs silently in the system tray. Right-click the tray icon to open Settings or Exit.

## Uninstalling

```bash
./uninstall.sh
```

Removes the installed commands and the autostart entry. Your config at `~/.config/haptic-overlay/` is preserved — delete it manually for a full clean slate.

## Configuration

Config is stored at `~/.config/haptic-overlay/config.json` and created with defaults on first run. You can edit it via the Settings window or directly in a text editor.

```jsonc
{
    "radius": 120,          // distance from center to button midpoint (px)
    "button_size": 72,      // button width and height (px)
    "drag_threshold": 8,    // min cursor movement (px) to count as a drag
    "dead_zone": 24,        // center radius (px) where release is a cancel
    "button_style": "...",  // Qt CSS applied to every button
    "buttons": [
        {
            "label": "Terminal",
            "action": { "type": "shell_command", "command": "kitty" }
        },
        {
            "label": "Browser",
            "action": { "type": "open_url", "url": "https://example.com" }
        },
        {
            "label": "Files",
            "action": { "type": "shell_command", "command": "nautilus" }
        }
    ]
}
```

### Action types

| Type | Required fields | Description |
|---|---|---|
| `shell_command` | `command` | Runs a shell command (fire-and-forget, no terminal window) |
| `open_url` | `url` | Opens a URL in the default browser |

## Adding a custom action

1. Create a file in `actions/handlers/`, for example `actions/handlers/notify.py`:

```python
from actions.handlers.base import Action
from actions.factory import ActionFactory

@ActionFactory.register("notify")
class NotifyAction(Action):
    def __init__(self, message: str):
        self.message = message

    def execute(self) -> None:
        import subprocess
        subprocess.Popen(["notify-send", self.message],
                         start_new_session=True,
                         stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
```

2. Import it in `actions/handlers/__init__.py` so it is registered.

3. Use it in your config:

```json
{ "type": "notify", "message": "Hello!" }
```

The Settings window will automatically show the `message` field for this action type.

## Project layout

```
haptic_overlay/
├── main.py                  # entry point, system tray app
├── settings.py              # settings entry point
├── config.py                # load / write config (XDG path)
├── models.py                # Pydantic config models
├── actions/
│   ├── factory.py           # decorator-based action registry
│   ├── resolver.py          # resolves button config → Action instance
│   └── handlers/
│       ├── base.py          # Action ABC
│       ├── shell_command.py
│       └── open_url.py
├── mouse_listener/
│   └── mouse_listener.py    # evdev QThread, auto-detects device
└── ui/
    ├── overlay/
    │   ├── overlay.py       # top-level transparent QWidget
    │   ├── radial_menu.py   # button layout, hover, drag-select
    │   └── button.py        # individual animated button
    └── settings/
        ├── settings.py      # two-tab settings window
        └── actions_editor.py # dynamic action fields from registry
```