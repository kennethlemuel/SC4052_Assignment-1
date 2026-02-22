def jain_fairness(values):
    values = [v for v in values if v is not None]
    if not values:
        return 0.0
    s = sum(values)
    if s == 0:
        return 0.0
    s2 = sum(v * v for v in values)
    n = len(values)
    return (s * s) / (n * s2)
