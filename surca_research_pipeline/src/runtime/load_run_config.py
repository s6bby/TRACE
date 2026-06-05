import json
import sys
from pathlib import Path


def resolve_path(repo_root: Path, value: str) -> str:
    path = Path(value)
    if path.is_absolute():
        return str(path)
    return str((repo_root / path).resolve())


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: load_run_config.py <config_path>", file=sys.stderr)
        return 1

    config_path = Path(sys.argv[1]).resolve()
    repo_root = config_path.parents[3]
    data = json.loads(config_path.read_text(encoding="utf-8"))

    path_keys = {"python", "requirements", "base_dir", "demo_dir", "npm_cmd"}

    for key, value in data.items():
        env_key = key.upper()
        if key in path_keys:
            print(f"{env_key}={resolve_path(repo_root, str(value))}")
        else:
            print(f"{env_key}={value}")

    python_path = Path(resolve_path(repo_root, str(data["python"])))
    print(f"VENV_DIR={python_path.parent.parent}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
