import argparse
from datetime import datetime
from pathlib import Path

from run import run_config


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs", default="configs", help="Configs directory")
    args = parser.parse_args()

    cfg_dir = Path(args.configs)
    if not cfg_dir.exists():
        raise SystemExit(f"Config directory not found: {cfg_dir}")

    stamp = _timestamp()
    out_root = Path("runs") / stamp

    configs = sorted(cfg_dir.glob("*.json"))
    if not configs:
        raise SystemExit(f"No config files found in {cfg_dir}")

    for cfg_path in configs:
        out_dir = out_root / cfg_path.stem
        run_root = run_config(cfg_path, out_dir)
        print(f"Wrote outputs to {run_root}")


if __name__ == "__main__":
    main()
