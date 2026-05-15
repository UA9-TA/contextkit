import json
from pathlib import Path
from typing import Any


class Config:
    def __init__(self, config_file: str = None):
        if not config_file:
            self.config_file = Path.home() / ".contextkit.json"
        else:
            self.config_file = Path(config_file)

        self.settings = {
            "max_tokens": 30000,
            "format": "markdown",
            "semantic": False
        }
        self.load()

    def load(self) -> None:
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    self.settings.update(data)
            except Exception:
                pass

    def save(self) -> None:
        with open(self.config_file, "w") as f:
            json.dump(self.settings, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.settings[key] = value
        self.save()
