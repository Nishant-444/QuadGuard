# Note for Future Nishant -- Chart plotting module using matplotlib.
# Generates comparative bar charts visualizing coverage outage minutes between Guard ON and Guard OFF.

import os
import matplotlib.pyplot as plt


def plot_guard_comparison(
    outage_with_guard: int, outage_without_guard: int, out_path: str
) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

    categories = ["Guard ON\n(QuadGuard)", "Guard OFF\n(Greedy / Standard)"]
    values = [outage_with_guard, outage_without_guard]
    colors = ["#2E7D32", "#C62828"]  # green for guard ON, red for guard OFF

    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
    bars = ax.bar(
        categories, values, color=colors, width=0.5, edgecolor="black", linewidth=1.2
    )

    ax.set_ylabel(
        "Coverage Outage Minutes (0–120 min sim)", fontsize=11, fontweight="bold"
    )
    ax.set_title(
        "Emergency Fleet Coverage Preservation Comparison",
        fontsize=12,
        fontweight="bold",
        pad=15,
    )
    ax.set_ylim(0, max(values) * 1.2 if max(values) > 0 else 10)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for bar, val in zip(bars, values):
        yval = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval + (max(values) * 0.02),
            f"{val} min",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
