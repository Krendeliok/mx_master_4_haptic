import json
from pathlib import Path

from models import ConfigModel

CONFIG_DIR = Path.home() / ".config" / "haptic-overlay"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> ConfigModel:
    if not CONFIG_FILE.exists():
        config = ConfigModel()
        _write_config(config)
        return config

    try:
        config = ConfigModel.model_validate_json(CONFIG_FILE.read_text(), extra="ignore")
    except Exception as e:
        raise Exception(f"Error parsing {CONFIG_FILE}: {e}")

    return config


def _write_config(config: ConfigModel) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = config.model_dump(exclude={"buttons_amount"})
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent="\t")