import json
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def data_dir() -> Path:
    return PROJECT_ROOT / "data"


@pytest.fixture
def load_seed(data_dir):
    def _load_seed(filename: str):
        with (data_dir / filename).open() as seed_file:
            return json.load(seed_file)

    return _load_seed

    return _load_seed
