"""
plot_results.py
Reads data/results.csv (produced by the C++ program) and draws a
log-log error plot for each test function: log(error) vs log(h),
one line per method (forward / backward / central).
"""

import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/results.csv")

functions = df["function"].unique()

fig, axes = plt.subplots(1, 3, figsize=(16, 5))

for ax, func_name in zip(axes, functions):
    subset = df[df["function"] == func_name].sort_values("h")

    ax.loglog(subset["h"], subset["error_forward"], marker="o", label="Forward")
    ax.loglog(subset["h"], subset["error_backward"], marker="s", label="Backward")
    ax.loglog(subset["h"], subset["error_central"], marker="^", label="Central")

    ax.set_title(func_name)
    ax.set_xlabel("log(h)")
    ax.set_ylabel("log(error)")
    ax.grid(True, which="both", linestyle="--", alpha=0.5)
    ax.legend()
    ax.invert_xaxis()  # so h decreases left -> right, matches the h column order

fig.suptitle("Log-Log Error Plot: Forward vs Backward vs Central Difference (at x = 1)")
fig.tight_layout()
fig.savefig("plots/log_log_error_plot.png", dpi=150)
print("Saved plots/log_log_error_plot.png")
