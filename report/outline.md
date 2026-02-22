# Report Outline (Q6)

1. Title + abstract (2-4 sentences)
2. Introduction
3. Literature survey
4. Problem setup and model contract
5. Baselines
6. Proposed approach
7. Experimental design
8. Results
9. Discussion
10. Limitations
11. AI transparency note
12. Conclusion

## Section notes
Introduction
- State the trend from DCTCP to AI-augmented tuning.
- Summarize what you contribute (a distinct controller and a small numerical study).

Literature survey
- DCTCP: limitation it fixed vs traditional TCP and how it uses ECN.
- Remy: key idea of automated controller synthesis for a target network model.

Problem setup and model contract
- Discrete-time fluid model, dt, single bottleneck, ECN threshold, queue.
- Assumptions and why they are acceptable for a concept study.

Baselines
- Reno AIMD update rule.
- Simplified DCTCP alpha update and cwnd reduction.

Proposed approach
- Risk-aware adaptive ECN controller.
- Safety guardrails (no increase above target queue, capped increase).

Experimental design
- 3 scenarios: steady, incast, heterogeneous RTT.
- 3 metrics: queue proxy (avg/p99), throughput, fairness.
- 3 plots: queue vs time, per-flow throughput, fairness bar chart.

Results
- Insert figures and refer to metrics.csv per scenario.

Discussion
- Technical challenge: stability under long RTT and incast.
- Risk: fairness/deployability tradeoffs.
- Tie results to both.

Limitations
- Fluid model, simplified DCTCP, Remy conceptual description.

AI transparency note
- What AI helped with, what you verified manually, what you rejected.

Conclusion
- Short summary + next steps.
