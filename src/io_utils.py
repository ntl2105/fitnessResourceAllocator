import json
import shutil
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> Any:
    with Path(path).open(encoding="utf-8") as file:
        return json.load(file)


def save_json(path: str | Path, payload: Any) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, sort_keys=True)
        file.write("\n")


def copy_inputs(input_paths: list[Path], destination_dir: Path) -> list[Path]:
    destination_dir.mkdir(parents=True, exist_ok=True)
    copied_paths = []
    for input_path in input_paths:
        destination_path = destination_dir / input_path.name
        shutil.copy2(input_path, destination_path)
        copied_paths.append(destination_path)
    return copied_paths
