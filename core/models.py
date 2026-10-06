import importlib
from pathlib import Path

import domains


def load_models() -> list[str]:
    root = Path(domains.__path__[0])
    loaded = []

    for domain in sorted(p.name for p in root.iterdir() if p.is_dir()):
        target = root / domain / "models"
        if not (target.is_dir() or target.with_suffix(".py").is_file()):
            continue
        module = f"domains.{domain}.models"
        importlib.import_module(module)
        loaded.append(module)

    return loaded
