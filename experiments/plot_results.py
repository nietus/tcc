from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS_DIR = ROOT / "results" / "drone_routing_review"
DEFAULT_FIGURES_DIR = ROOT / "figures" / "drone_routing_review"

ALGORITHM_ORDER = [
    "edd", "sweep", "nearest", "grasp", "alns",
    "mp_eavns", "mp_eavns_norepair", "mp_eavns_noshake", "mp_eavns_nowarm",
]
ALGORITHM_LABELS = {
    "edd": "EDD",
    "sweep": "Sweep",
    "nearest": "Nearest",
    "grasp": "GRASP",
    "alns": "ALNS",
    "mp_eavns": "MP-EAVNS",
    "mp_eavns_norepair": "MP-EAVNS\n(s/ 2-opt aux.)",
    "mp_eavns_noshake":  "MP-EAVNS\n(s/ perturb.)",
    "mp_eavns_nowarm":   "MP-EAVNS\n(s/ herança)",
}
POLICY_ORDER = ["depot", "phased", "all"]
POLICY_LABELS = {
    "depot": "Depósito",
    "phased": "Faseada",
    "all": "Completa",
}

# Cohesive sequential palette: light → dark within each family.
# Algorithms use cool blues/teals; the strongest algorithm (MP-EAVNS) gets
# the deepest hue. Policies use a parallel green family.
PALETTE = {
    "edd": "#cbd5e1",
    "sweep": "#94a3b8",
    "nearest": "#64748b",
    "grasp": "#0e7490",
    "alns": "#b45309",
    "mp_eavns": "#0c4a6e",
    "mp_eavns_norepair": "#1f6f8b",
    "mp_eavns_noshake":  "#1f6f8b",
    "mp_eavns_nowarm":   "#1f6f8b",
    "depot": "#bbf7d0",
    "phased": "#34d399",
    "all": "#047857",
}

# Secondary accent for dual-axis or callouts.
ACCENT = "#b45309"
NEUTRAL_TEXT = "#111827"
GRID_COLOR = "#e5e7eb"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_float(row: dict[str, str], key: str) -> float:
    return float(row[key])


def article_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Serif",
            "font.size": 8.5,
            "axes.labelsize": 8.5,
            "axes.titlesize": 11,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "figure.dpi": 140,
            "savefig.dpi": 220,
            "savefig.bbox": "tight",
            "axes.edgecolor": NEUTRAL_TEXT,
            "axes.linewidth": 0.7,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": GRID_COLOR,
            "grid.linestyle": ":",
            "grid.linewidth": 0.7,
            "xtick.color": NEUTRAL_TEXT,
            "ytick.color": NEUTRAL_TEXT,
            "axes.labelcolor": NEUTRAL_TEXT,
        }
    )


def br_number(value: float, decimals: int = 1) -> str:
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def objective_formatter(value: float, _: int = 0) -> str:
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M".replace(".", ",")
    if abs(value) >= 1_000:
        return f"{value / 1_000:.0f}k"
    return br_number(value, 0)


def _styled_bar(
    ax,
    labels: list[str],
    values: list[float],
    colors: list[str],
    ylabel: str,
    formatter,
    annotate_decimals: int | None = None,
) -> None:
    bars = ax.bar(labels, values, color=colors, edgecolor=NEUTRAL_TEXT, linewidth=0.5)
    ax.set_ylabel(ylabel)
    ax.yaxis.set_major_formatter(FuncFormatter(formatter))
    ax.grid(axis="x", visible=False)
    ymax = max(values) if values else 1.0
    ax.set_ylim(top=ymax * 1.15)
    for bar, value in zip(bars, values):
        if annotate_decimals is None:
            label = objective_formatter(value)
        else:
            label = br_number(value, annotate_decimals)
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + ymax * 0.02,
            label,
            ha="center",
            va="bottom",
            fontsize=8.5,
            color=NEUTRAL_TEXT,
        )


def _styled_hbar(
    ax,
    labels: list[str],
    values: list[float],
    colors: list[str],
    xlabel: str,
    formatter,
    annotate_decimals: int | None = None,
    invert: bool = True,
) -> None:
    positions = list(range(len(labels)))
    bars = ax.barh(positions, values, color=colors, edgecolor=NEUTRAL_TEXT, linewidth=0.5)
    ax.set_yticks(positions, labels)
    if invert:
        ax.invert_yaxis()
    ax.set_xlabel(xlabel)
    ax.xaxis.set_major_formatter(FuncFormatter(formatter))
    ax.grid(axis="y", visible=False)
    xmax = max(values) if values else 1.0
    ax.set_xlim(right=xmax * 1.18)
    for bar, value in zip(bars, values):
        if annotate_decimals is None:
            label = objective_formatter(value)
        else:
            label = br_number(value, annotate_decimals)
        ax.text(
            value + xmax * 0.015,
            bar.get_y() + bar.get_height() / 2,
            label,
            ha="left",
            va="center",
            fontsize=8.5,
            color=NEUTRAL_TEXT,
        )


def metric_bar(
    rows: list[dict[str, str]],
    key_field: str,
    order: list[str],
    labels: dict[str, str],
    metric: str,
    ylabel: str,
    output: Path,
) -> None:
    ordered = [next(row for row in rows if row[key_field] == key) for key in order]
    values = [as_float(row, metric) for row in ordered]
    colors = [PALETTE[key] for key in order]
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    formatter = objective_formatter if "objective" in metric else (lambda x, p=0: br_number(x, 2))
    annotate_decimals = None if "objective" in metric else 2
    _styled_bar(ax, [labels[key] for key in order], values, colors, ylabel, formatter, annotate_decimals)
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def algorithm_summary_panel(results: list[dict[str, str]], output: Path) -> None:
    algorithms = ["grasp", "alns", "mp_eavns"]
    viability_policies = ["depot", "phased", "all"]
    distance_policies = ["phased", "all"]
    labels = [ALGORITHM_LABELS[key] for key in algorithms]
    positions = list(range(len(algorithms)))

    def rows_for(algorithm: str, policy: str) -> list[dict[str, str]]:
        return [
            row for row in results
            if row["algorithm"] == algorithm and row["station_policy"] == policy
        ]

    fig, (ax_viab, ax_dist) = plt.subplots(1, 2, figsize=(6.7, 2.65), sharey=True)

    bar_h = 0.22
    offsets = [-bar_h, 0, bar_h]
    for offset, policy in zip(offsets, viability_policies):
        values = []
        for algorithm in algorithms:
            rows = rows_for(algorithm, policy)
            values.append(100.0 * sum(as_float(row, "infeasible_legs") == 0.0 for row in rows) / len(rows))
        bars = ax_viab.barh(
            [pos + offset for pos in positions],
            values,
            height=bar_h,
            color=PALETTE[policy],
            edgecolor=NEUTRAL_TEXT,
            linewidth=0.45,
            label=POLICY_LABELS[policy],
        )
        for bar, value in zip(bars, values):
            ax_viab.text(
                value + 1.4,
                bar.get_y() + bar.get_height() / 2,
                br_number(value, 1),
                ha="left",
                va="center",
                fontsize=7.4,
                color=NEUTRAL_TEXT,
            )

    bar_h2 = 0.28
    offsets2 = [-bar_h2 / 2, bar_h2 / 2]
    distance_max = 1.0
    for offset, policy in zip(offsets2, distance_policies):
        values = []
        for algorithm in algorithms:
            viable = [
                row for row in rows_for(algorithm, policy)
                if as_float(row, "infeasible_legs") == 0.0
            ]
            values.append(mean(as_float(row, "distance") for row in viable))
        distance_max = max(distance_max, max(values))
        bars = ax_dist.barh(
            [pos + offset for pos in positions],
            values,
            height=bar_h2,
            color=PALETTE[policy],
            edgecolor=NEUTRAL_TEXT,
            linewidth=0.45,
        )
        xmax = max(values)
        for bar, value in zip(bars, values):
            ax_dist.text(
                value + xmax * 0.015,
                bar.get_y() + bar.get_height() / 2,
                br_number(value, 0),
                ha="left",
                va="center",
                fontsize=7.4,
                color=NEUTRAL_TEXT,
            )

    ax_viab.set_yticks(positions, labels)
    ax_viab.invert_yaxis()
    ax_viab.set_xlim(0, 108)
    ax_dist.set_xlim(0, distance_max * 1.18)
    ax_viab.set_xlabel("Soluções viáveis (%)")
    ax_dist.set_xlabel("Distância viável média")
    ax_viab.set_title("(a) Viabilidade")
    ax_dist.set_title("(b) Qualidade da rota")
    ax_viab.xaxis.set_major_formatter(FuncFormatter(lambda x, p=0: br_number(x, 0)))
    ax_dist.xaxis.set_major_formatter(FuncFormatter(lambda x, p=0: br_number(x, 0)))
    ax_viab.legend(frameon=False, ncol=3, loc="lower right", handletextpad=0.35, columnspacing=0.8)
    ax_dist.tick_params(axis="y", left=False, labelleft=False)
    fig.subplots_adjust(wspace=0.16)
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def policy_summary_panel(summary: list[dict[str, str]], output: Path) -> None:
    ordered = [next(row for row in summary if row["station_policy"] == key) for key in POLICY_ORDER]
    objectives = [as_float(row, "objective_mean") for row in ordered]
    infeasibles = [as_float(row, "infeasible_legs_mean") for row in ordered]
    colors = [PALETTE[key] for key in POLICY_ORDER]
    labels = [POLICY_LABELS[key] for key in POLICY_ORDER]

    fig, (ax_obj, ax_inf) = plt.subplots(1, 2, figsize=(7.4, 3.4))
    _styled_bar(ax_obj, labels, objectives, colors, "Objetivo", objective_formatter)
    _styled_bar(
        ax_inf,
        labels,
        infeasibles,
        colors,
        "Trechos inviáveis",
        lambda x, p=0: br_number(x, 2),
        annotate_decimals=2,
    )
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def boxplot_objective_by_algorithm(rows: list[dict[str, str]], output: Path) -> None:
    data = [
        [as_float(row, "objective") for row in rows if row["algorithm"] == algorithm]
        for algorithm in ALGORITHM_ORDER
    ]
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    box = ax.boxplot(
        data,
        tick_labels=[ALGORITHM_LABELS[a] for a in ALGORITHM_ORDER],
        showfliers=False,
        patch_artist=True,
        medianprops={"color": NEUTRAL_TEXT, "linewidth": 1.2},
        boxprops={"edgecolor": NEUTRAL_TEXT, "linewidth": 0.6},
        whiskerprops={"color": NEUTRAL_TEXT, "linewidth": 0.6},
        capprops={"color": NEUTRAL_TEXT, "linewidth": 0.6},
    )
    for patch, algorithm in zip(box["boxes"], ALGORITHM_ORDER):
        patch.set_facecolor(PALETTE[algorithm])
        patch.set_alpha(0.85)
    ax.set_ylabel("Objetivo (log)")
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(objective_formatter))
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def heatmap_algorithm_policy(rows: list[dict[str, str]], output: Path) -> None:
    matrix: list[list[float]] = []
    for algorithm in ALGORITHM_ORDER:
        matrix.append(
            [
                as_float(
                    next(
                        row
                        for row in rows
                        if row["algorithm"] == algorithm and row["station_policy"] == policy
                    ),
                    "objective_mean",
                )
                for policy in POLICY_ORDER
            ]
        )

    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    image = ax.imshow(matrix, cmap="YlGnBu_r", aspect="auto")
    flat_values = [value for row in matrix for value in row]
    min_value = min(flat_values)
    max_value = max(flat_values)
    ax.set_xticks(range(len(POLICY_ORDER)), [POLICY_LABELS[p] for p in POLICY_ORDER])
    ax.set_yticks(range(len(ALGORITHM_ORDER)), [ALGORITHM_LABELS[a] for a in ALGORITHM_ORDER])
    ax.set_xlabel("Política de estações")
    ax.set_ylabel("Algoritmo")
    ax.grid(False)
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            normalized = (value - min_value) / (max_value - min_value + 1e-9)
            color = "white" if normalized < 0.45 else NEUTRAL_TEXT
            ax.text(
                j,
                i,
                objective_formatter(value),
                ha="center",
                va="center",
                fontsize=9,
                color=color,
            )
    cbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.set_ylabel("Objetivo", rotation=270, labelpad=14)
    cbar.ax.yaxis.set_major_formatter(FuncFormatter(objective_formatter))
    cbar.outline.set_visible(False)
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def period_lines(
    rows: list[dict[str, str]],
    group_field: str,
    order: list[str],
    labels: dict[str, str],
    output: Path,
) -> None:
    grouped: dict[tuple[str, int], list[float]] = defaultdict(list)
    periods = sorted({int(row["period"]) for row in rows})
    for row in rows:
        grouped[(row[group_field], int(row["period"]))].append(as_float(row, "infeasible_legs"))

    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    for key in order:
        values = [mean(grouped[(key, period)]) for period in periods]
        ax.plot(
            periods,
            values,
            marker="o",
            linewidth=1.8,
            markersize=4.5,
            label=labels[key],
            color=PALETTE[key],
        )
    ax.set_xlabel("Período")
    ax.set_ylabel("Trechos inviáveis")
    ax.set_xticks(periods)
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, ncol=len(order), loc="upper right")
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def runtime_tradeoff(summary: list[dict[str, str]], output: Path) -> None:
    fig, ax = plt.subplots(figsize=(5.2, 2.85))
    main_algorithms = {"edd", "sweep", "nearest", "grasp", "alns", "mp_eavns"}
    for row in summary:
        algorithm = row["algorithm"]
        if algorithm not in main_algorithms:
            continue
        ax.scatter(
            as_float(row, "runtime_seconds_mean"),
            as_float(row, "objective_mean"),
            s=56,
            color=PALETTE[algorithm],
            edgecolor=NEUTRAL_TEXT,
            linewidth=0.5,
            zorder=3,
            label=ALGORITHM_LABELS[algorithm],
        )
    ax.set_xlabel("Tempo por solução (s, log)")
    ax.set_ylabel("Objetivo")
    ax.set_title("Custo computacional e objetivo")
    ax.set_xscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(objective_formatter))
    ax.legend(frameon=False, ncol=2, loc="upper right", handletextpad=0.35, columnspacing=0.9)
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def range_sensitivity(results_dirs: list[Path], output: Path, algorithm: str = "mp_eavns", policy: str = "phased") -> None:
    available: list[tuple[int, list[dict[str, str]]]] = []
    for directory in results_dirs:
        if not directory.exists():
            continue
        match = None
        for token in directory.name.split("_"):
            if token.startswith("r") and token[1:].isdigit():
                match = int(token[1:])
        if match is None and directory.name.endswith("full_small"):
            match = 80
        if match is None and (directory.name.endswith("_all") or directory.name.endswith("_review")):
            match = 80
        if match is not None:
            # prefer algorithm × policy file when it exists; otherwise fall back to aggregate summary
            ap_path = directory / "algorithm_station_summary.csv"
            if ap_path.exists():
                rows = read_csv(ap_path)
                rows = [r for r in rows if r["algorithm"] == algorithm and r["station_policy"] == policy]
            else:
                rows = read_csv(directory / "summary.csv")
                rows = [r for r in rows if r["algorithm"] == algorithm]
            if rows:
                available.append((match, rows))
    if not available:
        return

    available.sort(key=lambda item: item[0])
    ranges = [item[0] for item in available]
    objective = [as_float(item[1][0], "objective_mean") for item in available]
    infeasible = [as_float(item[1][0], "infeasible_legs_mean") for item in available]

    fig, (ax_obj, ax_inf) = plt.subplots(1, 2, figsize=(7.6, 3.4), sharex=True)
    ax_obj.plot(
        ranges,
        objective,
        color=PALETTE["mp_eavns"],
        marker="o",
        markersize=6,
        linewidth=1.9,
    )
    ax_inf.plot(
        ranges,
        infeasible,
        color=ACCENT,
        marker="s",
        markersize=6,
        linewidth=1.9,
    )
    for x, y in zip(ranges, objective):
        ax_obj.annotate(
            objective_formatter(y),
            (x, y),
            xytext=(0, 7),
            textcoords="offset points",
            ha="center",
            fontsize=8.5,
            color=NEUTRAL_TEXT,
        )
    for x, y in zip(ranges, infeasible):
        ax_inf.annotate(
            br_number(y, 2),
            (x, y),
            xytext=(0, 7),
            textcoords="offset points",
            ha="center",
            fontsize=8.5,
            color=NEUTRAL_TEXT,
        )
    ax_obj.set_ylabel("Objetivo")
    ax_inf.set_ylabel("Trechos inviáveis")
    ax_obj.set_xlabel("Autonomia")
    ax_inf.set_xlabel("Autonomia")
    ax_obj.yaxis.set_major_formatter(FuncFormatter(objective_formatter))
    ax_inf.yaxis.set_major_formatter(FuncFormatter(lambda x, p=0: br_number(x, 2)))
    ax_obj.set_xticks(ranges)
    ax_obj.set_ylim(bottom=0)
    ax_inf.set_ylim(bottom=0)
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate article-style plots for drone routing experiments.")
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--figures-dir", type=Path, default=DEFAULT_FIGURES_DIR)
    args = parser.parse_args()

    article_style()
    args.figures_dir.mkdir(parents=True, exist_ok=True)

    summary = read_csv(args.results_dir / "summary.csv")
    results = read_csv(args.results_dir / "results.csv")
    # Figures used by the current article.
    algorithm_summary_panel(results, args.figures_dir / "algorithm_summary.pdf")
    runtime_tradeoff(summary, args.figures_dir / "runtime_tradeoff.pdf")
    print(f"Plots written to {args.figures_dir}")


if __name__ == "__main__":
    main()
