import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

SRC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC_DIR))

from metrics import jain_fairness
from sim import simulate


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def _plot_queue(times, queues, out_path):
    plt.figure(figsize=(8, 4))
    for algo, q in queues.items():
        plt.plot(times, q, label=algo)
    plt.xlabel("Time (s)")
    plt.ylabel("Queue (packets)")
    plt.title("Queue vs Time")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def _plot_throughput(throughputs, out_path):
    df = pd.DataFrame(throughputs)
    df = df.set_index("flow")
    ax = df.plot(kind="bar", figsize=(8, 4))
    ax.set_xlabel("Flow")
    ax.set_ylabel("Avg throughput (packets/s)")
    ax.set_title("Per-flow Throughput")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def _plot_fairness(metrics, out_path):
    df = pd.DataFrame(metrics)
    plt.figure(figsize=(6, 4))
    plt.bar(df["algorithm"], df["fairness"])
    plt.ylabel("Jain's fairness index")
    plt.title("Fairness by Algorithm")
    plt.ylim(0, 1.05)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def run_config(cfg_path: Path, out_dir: Optional[Path] = None) -> Path:
    cfg = json.loads(cfg_path.read_text())

    run_root = out_dir if out_dir else Path("runs") / _timestamp() / cfg_path.stem
    run_root.mkdir(parents=True, exist_ok=True)

    queues = {}
    metrics = []
    throughput = {}
    times = None

    for algo in cfg["algorithms"]:
        result = simulate(cfg, algo)
        queues[algo] = result.queue
        if times is None:
            times = result.times

        avg_q = float(result.queue.mean())
        p99_q = float(pd.Series(result.queue).quantile(0.99))
        total_throughput = float(sum(result.per_flow_rate.values()))
        fairness = float(jain_fairness(list(result.per_flow_rate.values())))

        metrics.append({
            "algorithm": algo,
            "avg_queue": avg_q,
            "p99_queue": p99_q,
            "total_throughput": total_throughput,
            "fairness": fairness,
        })

        for flow_id, rate in result.per_flow_rate.items():
            throughput.setdefault(flow_id, {})[algo] = rate

    throughput_df = pd.DataFrame.from_dict(throughput, orient="index")
    if not throughput_df.empty:
        throughput_df.index.name = "flow"
        throughput_df = throughput_df.reset_index()

    pd.DataFrame(metrics).to_csv(run_root / "metrics.csv", index=False)
    if not throughput_df.empty:
        throughput_df.to_csv(run_root / "throughput.csv", index=False)

    if times is not None:
        _plot_queue(times, queues, run_root / "queue.png")
    if not throughput_df.empty:
        _plot_throughput(throughput_df, run_root / "throughput.png")
    _plot_fairness(metrics, run_root / "fairness.png")

    return run_root


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to config JSON")
    parser.add_argument("--out", default=None, help="Output directory")
    args = parser.parse_args()

    cfg_path = Path(args.config)
    out_dir = Path(args.out) if args.out else None
    run_root = run_config(cfg_path, out_dir)
    print(f"Wrote outputs to {run_root}")


if __name__ == "__main__":
    main()
