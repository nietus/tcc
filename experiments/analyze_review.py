"""Post-run analysis for the reviewer-driven sweep.

Computes:
  - per-algorithm policy means (objective + infeasibility)
  - viable-only metrics (distance, tardiness, recharges)
  - viability rate per algorithm
"""
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results" / "drone_routing_review"


def load(name: str) -> list[dict[str, str]]:
    with (RES / name).open(newline="", encoding="utf-8") as h:
        return list(csv.DictReader(h))


def to_f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def main() -> None:
    rows = load("results.csv")
    print(f"Total runs: {len(rows)}")
    algos = sorted({r["algorithm"] for r in rows})
    policies = ["depot", "phased", "all"]
    print(f"Algorithms: {algos}")

    print("\n--- Mean infeasibility per algorithm × policy ---")
    print(f"{'algo':<22}" + "".join(f"{p:>10}" for p in policies))
    for algo in algos:
        cells = []
        for pol in policies:
            sub = [to_f(r, "infeasible_legs") for r in rows if r["algorithm"] == algo and r["station_policy"] == pol]
            cells.append(mean(sub) if sub else float("nan"))
        print(f"{algo:<22}" + "".join(f"{c:>10.3f}" for c in cells))

    print("\n--- Mean objective per algorithm × policy ---")
    print(f"{'algo':<22}" + "".join(f"{p:>14}" for p in policies))
    for algo in algos:
        cells = []
        for pol in policies:
            sub = [to_f(r, "objective") for r in rows if r["algorithm"] == algo and r["station_policy"] == pol]
            cells.append(mean(sub) if sub else float("nan"))
        print(f"{algo:<22}" + "".join(f"{c:>14.0f}" for c in cells))

    print("\n--- Viability rate (% of runs with infeasible_legs == 0) per algorithm × policy ---")
    print(f"{'algo':<22}" + "".join(f"{p:>10}" for p in policies))
    for algo in algos:
        cells = []
        for pol in policies:
            sub = [to_f(r, "infeasible_legs") for r in rows if r["algorithm"] == algo and r["station_policy"] == pol]
            if not sub:
                cells.append(float("nan"))
            else:
                v = sum(1 for x in sub if x == 0.0) / len(sub) * 100
                cells.append(v)
        print(f"{algo:<22}" + "".join(f"{c:>10.1f}" for c in cells))

    print("\n--- Viable-only mean distance per algorithm × policy ---")
    print(f"{'algo':<22}" + "".join(f"{p:>10}" for p in policies))
    for algo in algos:
        cells = []
        for pol in policies:
            sub = [to_f(r, "distance") for r in rows if r["algorithm"] == algo and r["station_policy"] == pol and to_f(r, "infeasible_legs") == 0.0]
            cells.append(mean(sub) if sub else float("nan"))
        if any(c != c for c in cells):  # if any NaN
            pass
        print(f"{algo:<22}" + "".join(f"{c:>10.1f}" if c == c else f"{'--':>10}" for c in cells))

    print("\n--- Viable-only mean tardiness per algorithm × policy ---")
    print(f"{'algo':<22}" + "".join(f"{p:>12}" for p in policies))
    for algo in algos:
        cells = []
        for pol in policies:
            sub = [to_f(r, "tardiness") for r in rows if r["algorithm"] == algo and r["station_policy"] == pol and to_f(r, "infeasible_legs") == 0.0]
            cells.append(mean(sub) if sub else float("nan"))
        print(f"{algo:<22}" + "".join(f"{c:>12.1f}" if c == c else f"{'--':>12}" for c in cells))

    # Headline percentages for the article
    print("\n--- Headline relative numbers (B=80) ---")
    def algo_obj(a: str) -> float:
        sub = [to_f(r, "objective") for r in rows if r["algorithm"] == a]
        return mean(sub)
    if all(a in algos for a in ("mp_eavns", "grasp")):
        m = algo_obj("mp_eavns"); g = algo_obj("grasp")
        print(f"MP-EAVNS vs GRASP: {(1-m/g)*100:.1f}%")
    if all(a in algos for a in ("mp_eavns", "alns")):
        m = algo_obj("mp_eavns"); a = algo_obj("alns")
        print(f"MP-EAVNS vs ALNS: {(1-m/a)*100:.1f}%")
        print(f"ALNS vs GRASP: {(1-a/algo_obj('grasp'))*100:.1f}%")
    # Best vs worst constructive
    constr = ["edd", "sweep", "nearest"]
    avail = [a for a in constr if a in algos]
    if avail:
        worst = max(algo_obj(a) for a in avail)
        m = algo_obj("mp_eavns")
        print(f"MP-EAVNS vs worst constructive: {(1-m/worst)*100:.1f}%")
        best = min(algo_obj(a) for a in avail)
        print(f"MP-EAVNS vs best constructive: {(1-m/best)*100:.1f}%")

    # Viable-only headline: MP-EAVNS vs GRASP on distance
    def viable_dist(a: str) -> float | None:
        sub = [to_f(r, "distance") for r in rows if r["algorithm"] == a and to_f(r, "infeasible_legs") == 0.0]
        return mean(sub) if sub else None
    md = viable_dist("mp_eavns"); gd = viable_dist("grasp")
    if md is not None and gd is not None:
        print(f"\nViable-only: MP-EAVNS distance {md:.1f} vs GRASP {gd:.1f} -> reduction {(1-md/gd)*100:.1f}%")

    # Policy means for MP-EAVNS
    print("\n--- Policy means for MP-EAVNS (B=80) ---")
    for pol in policies:
        sub_obj = [to_f(r, "objective") for r in rows if r["algorithm"] == "mp_eavns" and r["station_policy"] == pol]
        sub_inf = [to_f(r, "infeasible_legs") for r in rows if r["algorithm"] == "mp_eavns" and r["station_policy"] == pol]
        sub_dist = [to_f(r, "distance") for r in rows if r["algorithm"] == "mp_eavns" and r["station_policy"] == pol]
        sub_tard = [to_f(r, "tardiness") for r in rows if r["algorithm"] == "mp_eavns" and r["station_policy"] == pol]
        if sub_obj:
            print(f"  {pol}: obj={mean(sub_obj):.0f}, inf={mean(sub_inf):.3f}, dist={mean(sub_dist):.1f}, tard={mean(sub_tard):.1f}, n={len(sub_obj)}")


if __name__ == "__main__":
    main()
