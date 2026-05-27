from pathlib import Path
import json
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.generation.availability_patterns import expand_availability_patterns  # noqa: E402


def main() -> int:
    source_path = PROJECT_ROOT / "data" / "availability_patterns.json"
    output_path = PROJECT_ROOT / "data" / "availability.json"
    patterns = json.loads(source_path.read_text())
    expanded = expand_availability_patterns(patterns)
    output_path.write_text(json.dumps(expanded, indent=2) + "\n")
    print(
        "Expanded "
        f"{len(patterns.get('patterns', []))} availability patterns into "
        f"{len(expanded['availability_blocks'])} availability blocks."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
