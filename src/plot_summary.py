import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def _load_metrics(run_root: Path) -> pd.DataFrame:
    rows = []
    for metrics_path in sorted(run_root.glob("*/metrics.csv")):
        scenario = metrics_path.parent.name
        df = pd.read_csv(metrics_path)
        df["scenario"] = scenario
        rows.append(df)
    if not rows:
        raise SystemExit(f"No metrics.csv found under {run_root}")
    return pd.concat(rows, ignore_index=True)


def _plot_metric(df: pd.DataFrame, metric: str, out_path: Path) -> None:
    pivot = df.pivot(index="scenario", columns="algorithm", values=metric)
    order = [s for s in ["steady", "incast", "hetero_rtt"] if s in pivot.index]
    if order:
        pivot = pivot.reindex(order)

    ax = pivot.plot(kind="bar", figsize=(8, 4))
    ax.set_xlabel("Scenario")

    label = metric.replace("_", " ").title()
    if metric in {"avg_queue", "p99_queue"}:
        label = f"{label} (packets)"
    ax.set_ylabel(label)

    title = "P99 Queue (Tail Latency Proxy) by Scenario" if metric == "p99_queue" else f"{label} by Scenario"
    ax.set_title(title)

    ax.legend(title="Algorithm", bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)
    ax.tick_params(axis="x", labelrotation=0)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True, help="Run root (e.g., runs/20260220-205208)")
    parser.add_argument("--all", action="store_true", help="Generate all summary plots")
    parser.add_argument("--metric", default="p99_queue",
                        choices=["avg_queue", "p99_queue", "total_throughput", "fairness"],
                        help="Metric to plot")
    args = parser.parse_args()

    run_root = Path(args.run)
    df = _load_metrics(run_root)
    metrics = ["avg_queue", "p99_queue", "total_throughput", "fairness"]
    if args.all:
        for metric in metrics:
            out_path = run_root / f"summary_{metric}.png"
            _plot_metric(df, metric, out_path)
            print(f"Wrote {out_path}")
        return

    out_path = run_root / f"summary_{args.metric}.png"
    _plot_metric(df, args.metric, out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
