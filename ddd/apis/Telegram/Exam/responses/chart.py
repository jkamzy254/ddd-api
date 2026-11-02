import matplotlib
matplotlib.use("Agg")  # headless backend, no browser/display needed
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

PASS_CMAP = LinearSegmentedColormap.from_list("pass", ["#A8E6CF", "#05668D"])
FAIL_CMAP = LinearSegmentedColormap.from_list("fail", ["#FFCCCC", "#FF6666", "#990000"])


def render_pass_rate_chart(df, exam_name, chart_path):
    depts = df["Dept"].astype(str).tolist()
    passed = df["Passed"].astype(float).tolist()
    failed = df["Failed"].astype(float).tolist()
    pass_rate = df["PassRate"].astype(float).tolist()
    x = range(len(depts))

    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    try:
        # Stacked bars, coloured by pass rate (same gradients as the old Plotly chart)
        pass_bars = ax.bar(x, passed, color=[PASS_CMAP(r / 100) for r in pass_rate], label="Passed")
        fail_bars = ax.bar(x, failed, bottom=passed, color=[FAIL_CMAP((100 - r) / 100) for r in pass_rate], label="Failed")
        ax.bar_label(pass_bars, labels=[f"{int(v)}" if v else "" for v in passed], label_type="center", color="white", fontsize=10)
        ax.bar_label(fail_bars, labels=[f"{int(v)}" if v else "" for v in failed], label_type="center", color="white", fontsize=10)

        ax.set_xticks(list(x))
        ax.set_xticklabels(depts)
        ax.set_xlabel("Department")
        ax.set_ylabel("Number of Students")
        ax.spines["top"].set_visible(False)

        # Pass rate line on secondary axis
        ax2 = ax.twinx()
        ax2.plot(list(x), pass_rate, color="#0DCDFD", linewidth=1, marker="o", markersize=6, label="Pass Rate (%)")
        for i, r in enumerate(pass_rate):
            ax2.annotate(f"{r:.1f}%", (i, r), textcoords="offset points", xytext=(0, 8),
                         ha="center", color="#1A8DAA", fontsize=10, fontweight="bold",
                         bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.8))
        ax2.set_ylim(0, 105)
        ax2.set_ylabel("Pass Rate (%)")
        ax2.spines["top"].set_visible(False)

        handles1, labels1 = ax.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(handles1 + handles2, labels1 + labels2, loc="upper left")

        ax.set_title(f"{exam_name} Exam Results by Department")
        fig.tight_layout()
        fig.savefig(chart_path)
    finally:
        plt.close(fig)

    return chart_path
