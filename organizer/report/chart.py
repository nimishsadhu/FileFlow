import base64
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from ..config import CATEGORY_COLORS


def generate_chart(category_counts):
    labels = list(category_counts.keys())
    sizes  = list(category_counts.values())
    colors = [CATEGORY_COLORS.get(l, "#94a3b8") for l in labels]

    fig, ax = plt.subplots(figsize=(7, 7), facecolor="none")
    ax.set_facecolor("none")

    _, _, autotexts = ax.pie(
        sizes,
        labels=None,
        autopct=lambda p: f"{p:.1f}%" if p > 4 else "",
        colors=colors,
        startangle=140,
        pctdistance=0.72,
        wedgeprops={"linewidth": 3, "edgecolor": "#0f1117", "width": 0.65},
    )

    for at in autotexts:
        at.set_fontsize(11)
        at.set_fontweight("bold")
        at.set_color("white")

    total = sum(sizes)
    ax.text(0, 0.08, str(total), ha="center", va="center",
            fontsize=38, fontweight="bold", color="white", fontfamily="monospace")
    ax.text(0, -0.2, "F I L E S", ha="center", va="center",
            fontsize=10, color="#94a3b8", fontfamily="monospace", fontweight="bold")

    patches = [
        mpatches.Patch(color=colors[i], label=f"{labels[i]}  ({sizes[i]})")
        for i in range(len(labels))
    ]
    legend = ax.legend(
        handles=patches,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=min(len(labels), 4),
        frameon=False,
        fontsize=10,
        labelcolor="white",
    )
    for t in legend.get_texts():
        t.set_fontfamily("monospace")

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor="none", transparent=True)
    plt.close()
    buf.seek(0)

    return base64.b64encode(buf.read()).decode("utf-8")
