# Q6 Workflow Summary (from user-provided plan)

- Scope: explain DCTCP vs TCP and Remy; propose distinct new approach; analyze one technical challenge + one risk numerically.
- Baselines: TCP Reno (AIMD) and simplified DCTCP.
- Proposal: risk-aware adaptive ECN controller with stability guardrails for long RTT.
- Model: discrete-time fluid model with cwnd, bottleneck capacity, single queue, ECN threshold.
- Experiments: 3 scenarios (steady, incast, hetero RTT), 3 metrics (queue/ECN, throughput, fairness), 3 plots.
- Reproducibility: configs in `configs/`, outputs in `runs/` only, one command to reproduce.
- Limitations: fluid model, simplified DCTCP, Remy discussed conceptually, speculative space-borne assumptions.
- AI transparency: document what AI helped with, what you verified, and what you rejected.
