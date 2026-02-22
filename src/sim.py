from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np


@dataclass
class FlowState:
    flow_id: str
    rtt: float
    start: float
    end: float
    cwnd: float
    alpha: float = 0.0
    marks: int = 0
    steps: int = 0
    next_update: float = 0.0


@dataclass
class SimResult:
    times: np.ndarray
    queue: np.ndarray
    delivered: Dict[str, float]
    per_flow_rate: Dict[str, float]


def _update_flow(flow: FlowState, algo: str, F: float, q: float, cfg: dict) -> None:
    min_cwnd = cfg.get("min_cwnd", 1.0)

    if algo == "reno":
        ai = cfg.get("reno", {}).get("ai", 1.0)
        md = cfg.get("reno", {}).get("md", 0.5)
        if F > 0:
            flow.cwnd = max(min_cwnd, flow.cwnd * md)
        else:
            flow.cwnd += ai
        return

    if algo == "dctcp":
        g = cfg.get("dctcp", {}).get("g", 0.0625)
        ai = cfg.get("dctcp", {}).get("ai", 1.0)
        flow.alpha = (1 - g) * flow.alpha + g * F
        if F > 0:
            flow.cwnd = max(min_cwnd, flow.cwnd * (1 - flow.alpha / 2))
        else:
            flow.cwnd += ai
        return

    if algo == "risk_ecn":
        ai = cfg.get("risk_ecn", {}).get("ai", 1.0)
        md = cfg.get("risk_ecn", {}).get("md", 0.3)
        max_inc = cfg.get("risk_ecn", {}).get("max_inc", 0.5)
        q_target = cfg.get("risk_ecn", {}).get("q_target", cfg.get("ecn_threshold", 0.0))

        if F > 0:
            flow.cwnd = max(min_cwnd, flow.cwnd * (1 - md * F))
            return

        if q <= q_target:
            scale = 1.0 if q_target <= 0 else max(0.0, 1.0 - (q / q_target))
            inc = min(max_inc, ai * scale)
            flow.cwnd += inc
        return

    raise ValueError(f"Unknown algorithm: {algo}")


def simulate(cfg: dict, algo: str) -> SimResult:
    dt = cfg["dt"]
    duration = cfg["duration"]
    C = cfg["link_capacity"]
    K = cfg.get("ecn_threshold", 0.0)
    B = cfg.get("queue_max", None)

    flows: List[FlowState] = []
    for f in cfg["flows"]:
        flow = FlowState(
            flow_id=f["id"],
            rtt=f["rtt"],
            start=f["start"],
            end=f["end"],
            cwnd=f.get("init_cwnd", cfg.get("init_cwnd", 10.0)),
        )
        flow.next_update = flow.start + flow.rtt
        flows.append(flow)

    times = np.arange(0.0, duration + dt, dt)
    queue = np.zeros_like(times)
    delivered = {f.flow_id: 0.0 for f in flows}
    per_flow_rate = {f.flow_id: 0.0 for f in flows}

    q = 0.0
    for i, t in enumerate(times):
        active = [f for f in flows if f.start <= t < f.end]

        rates = {}
        for f in active:
            rates[f.flow_id] = f.cwnd / f.rtt
        total_rate = sum(rates.values())

        q = max(0.0, q + (total_rate - C) * dt)
        if B is not None:
            q = min(q, B)
        queue[i] = q

        marked = 1.0 if q >= K else 0.0
        for f in active:
            f.steps += 1
            f.marks += marked

        if total_rate > 0:
            for f in active:
                share = rates[f.flow_id] / total_rate
                delivered[f.flow_id] += C * share * dt

        for f in active:
            if t >= f.next_update:
                F = f.marks / max(1, f.steps)
                _update_flow(f, algo, F, q, cfg)
                f.marks = 0
                f.steps = 0
                f.next_update = t + f.rtt

    active_durations = {f.flow_id: max(0.0, min(duration, f.end) - f.start) for f in flows}
    for fid, dur in active_durations.items():
        per_flow_rate[fid] = delivered[fid] / dur if dur > 0 else 0.0

    return SimResult(times=times, queue=queue, delivered=delivered, per_flow_rate=per_flow_rate)
