from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
from typing import Any, Dict

CONFIG_DIR = Path.home() / ".mpro400_analyzer"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _apply_defaults(payload: Dict[str, Any]) -> Dict[str, Any]:
    defaults = {
        "show_onboarding": True,
        "last_dir": str(Path.home()),
    }
    merged = defaults.copy()
    merged.update(payload)
    return merged


@dataclass
class AppConfig:
    """Container for persisted UI preferences."""

    show_onboarding: bool = True
    last_dir: str = str(Path.home())

    @classmethod
    def load(cls, path: Path = CONFIG_FILE) -> "AppConfig":
        if not path.exists():
            return cls()
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return cls()
        return cls(**_apply_defaults(payload))

    def save(self, path: Path = CONFIG_FILE) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = asdict(self)
        try:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except OSError:
            # Saving failures are non-fatal; the app continues with runtime state.
            pass

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)
