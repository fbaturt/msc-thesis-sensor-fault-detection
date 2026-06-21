"""
plot_results.py
---------------
Results visualisation for Monte Carlo simulation campaign.

Loads summary_grouped.csv (produced by analyze_results.py) and
summary_runs.csv (produced by main_run_batch.m) and generates four
publication-quality figures:

  Figure A  --  Mean detection delay: bias faults, both detectors
  Figure B  --  Missed detection rate: freeze faults, both detectors
  Figure C  --  Mean false alarm events per run: all scenarios
  Figure D  --  Detection delay distribution: freeze faults,
                rate-of-change detector only (box plots)

Usage
-----
    python plot_results.py

Working directory must be the project root (same folder that contains
the output/ directory).

Inputs
------
    output/summaries/summary_grouped.csv
    output/summaries/summary_runs.csv

Outputs
-------
    output/figures/py_fig_A_bias_delay.png
    output/figures/py_fig_B_freeze_miss.png
    output/figures/py_fig_C_false_alarms.png
    output/figures/py_fig_D_freeze_delay_dist.png

Dependencies
------------
    pandas     >= 1.3
    numpy      >= 1.21
    matplotlib >= 3.4
"""

import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ── Paths ──────────────────────────────────────────────────────────────────
_SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
_SUMM_DIR    = os.path.join(_SCRIPT_DIR, "..", "matlab", "output", "summaries")
_FIG_DIR_BASE = os.path.join(_SCRIPT_DIR, "..", "matlab", "output", "figures")
GROUPED_PATH = os.path.join(_SUMM_DIR, "summary_grouped.csv")
RUNS_PATH    = os.path.join(_SUMM_DIR, "summary_runs.csv")
FIG_DIR      = _FIG_DIR_BASE

# ── Ordering ───────────────────────────────────────────────────────────────
NOISE_ORDER       = ["low", "med", "high"]
NOISE_LABEL       = ["Low\n(sigma=0.5 kt)", "Medium\n(sigma=1.0 kt)", "High\n(sigma=2.0 kt)"]
NOISE_LABEL_SHORT = ["Low", "Med", "High"]
PHASE_ORDER       = ["climb", "descent"]
PHASE_LABEL       = {"climb": "Climb", "descent": "Descent"}

# ── Colours ────────────────────────────────────────────────────────────────
COLOR_T = "#2E86C1"
COLOR_R = "#E67E22"

# ── Dimensions ────────────────────────────────────────────────────────────
DPI        = 300
FIG_W      = 9.0
FIG_H      = 5.0
FIG_W_WIDE = 10.0
FIG_H_TALL = 7.0

# ── Global style ───────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":       "DejaVu Serif",
    "font.size":         12,
    "axes.titlesize":    12,
    "axes.labelsize":    12,
    "xtick.labelsize":   10,
    "ytick.labelsize":   10,
    "legend.fontsize":   10,
    "figure.dpi":        DPI,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         True,
    "grid.alpha":        0.35,
    "grid.linestyle":    "--",
    "grid.linewidth":    0.6,
})


# ══════════════════════════════════════════════════════════════════════════
# Utilities
# ══════════════════════════════════════════════════════════════════════════

def load_data():
    for path in (GROUPED_PATH, RUNS_PATH):
        if not os.path.exists(path):
            print(f"\nERROR: File not found: {path}")
            if "grouped" in path:
                print("Run analyze_results.py first.")
            else:
                print("Run main_run_batch.m in MATLAB first.")
            sys.exit(1)

    grouped = pd.read_csv(GROUPED_PATH)
    runs    = pd.read_csv(RUNS_PATH)

    for col in ["fault_type", "noise", "phase_focus",
                "T_delay_mean", "T_miss_rate", "T_FA_mean",
                "R_delay_mean", "R_miss_rate", "R_FA_mean"]:
        if col not in grouped.columns:
            print(f"ERROR: Missing column '{col}' in {GROUPED_PATH}")
            sys.exit(1)

    print(f"  Loaded grouped : {len(grouped)} rows")
    print(f"  Loaded runs    : {len(runs)} rows")
    return grouped, runs


def safe_val(sub, noise_key, col):
    if noise_key in sub.index:
        v = sub.loc[noise_key, col]
        return float(v) if not pd.isna(v) else 0.0
    return 0.0


# ══════════════════════════════════════════════════════════════════════════
# Figure A
# ══════════════════════════════════════════════════════════════════════════

def fig_A_bias_delay(grouped):
    bias  = grouped[grouped["fault_type"] == "bias"].copy()
    x     = np.arange(len(NOISE_ORDER))
    width = 0.30

    fig, axes = plt.subplots(1, 2, figsize=(FIG_W, FIG_H), sharey=True)
    fig.suptitle("Figure A — Mean Detection Delay: Constant Bias Faults",
                 fontsize=13, fontweight="bold")

    for ax, phase in zip(axes, PHASE_ORDER):
        sub    = bias[bias["phase_focus"] == phase].set_index("noise")
        t_vals = [safe_val(sub, n, "T_delay_mean") for n in NOISE_ORDER]
        r_vals = [safe_val(sub, n, "R_delay_mean") for n in NOISE_ORDER]

        bt = ax.bar(x - width/2, t_vals, width, label="Threshold",
                    color=COLOR_T, alpha=0.85, edgecolor="white", linewidth=0.6)
        br = ax.bar(x + width/2, r_vals, width, label="Rate-of-Change",
                    color=COLOR_R, alpha=0.85, edgecolor="white", linewidth=0.6)

        for bars in (bt, br):
            for bar in bars:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, h + 0.002,
                        f"{h:.2f}", ha="center", va="bottom", fontsize=8)

        ax.set_title(f"{PHASE_LABEL[phase]} Phase", fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(NOISE_LABEL)
        ax.set_xlabel("Noise Level")
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.2f"))
        ax.legend(loc="upper left")

    axes[0].set_ylabel("Mean Detection Delay (s)")
    fig.tight_layout()
    path = os.path.join(FIG_DIR, "py_fig_A_bias_delay.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════════════
# Figure B
# ══════════════════════════════════════════════════════════════════════════

def fig_B_freeze_miss(grouped):
    freeze = grouped[grouped["fault_type"] == "freeze"].copy()
    x      = np.arange(len(NOISE_ORDER))
    width  = 0.30

    fig, axes = plt.subplots(1, 2, figsize=(FIG_W, FIG_H), sharey=True)
    fig.suptitle("Figure B — Missed Detection Rate: Frozen Signal Faults",
                 fontsize=13, fontweight="bold")

    for ax, phase in zip(axes, PHASE_ORDER):
        sub    = freeze[freeze["phase_focus"] == phase].set_index("noise")
        t_vals = [safe_val(sub, n, "T_miss_rate") for n in NOISE_ORDER]
        r_vals = [safe_val(sub, n, "R_miss_rate") for n in NOISE_ORDER]

        bt = ax.bar(x - width/2, t_vals, width, label="Threshold",
                    color=COLOR_T, alpha=0.85, edgecolor="white", linewidth=0.6)
        br = ax.bar(x + width/2, r_vals, width, label="Rate-of-Change",
                    color=COLOR_R, alpha=0.85, edgecolor="white", linewidth=0.6)

        for bars in (bt, br):
            for bar in bars:
                h = bar.get_height()
                if h >= 0.01:
                    ax.text(bar.get_x() + bar.get_width()/2, h + 0.02,
                            f"{h:.0%}", ha="center", va="bottom", fontsize=8)

        ax.axhline(1.0, color="red", linewidth=0.9, linestyle=":", alpha=0.65)
        ax.set_title(f"{PHASE_LABEL[phase]} Phase", fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(NOISE_LABEL)
        ax.set_xlabel("Noise Level")
        ax.set_ylim(0, 1.20)
        ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1))
        ax.legend(loc="upper right")

    axes[0].set_ylabel("Missed Detection Rate")
    fig.tight_layout()
    path = os.path.join(FIG_DIR, "py_fig_B_freeze_miss.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════════════
# Figure C
# ══════════════════════════════════════════════════════════════════════════

def fig_C_false_alarms(grouped):
    panels = [
        ("bias",   "climb",   "Bias Faults - Climb Phase"),
        ("bias",   "descent", "Bias Faults - Descent Phase"),
        ("freeze", "climb",   "Freeze Faults - Climb Phase"),
        ("freeze", "descent", "Freeze Faults - Descent Phase"),
    ]
    x     = np.arange(len(NOISE_ORDER))
    width = 0.30

    fig, axes = plt.subplots(2, 2, figsize=(FIG_W_WIDE, FIG_H_TALL))
    fig.suptitle("Figure C — Mean False Alarm Events per Run",
                 fontsize=13, fontweight="bold")

    for (ft, pf, title), ax in zip(panels, axes.flat):
        sub    = grouped[(grouped["fault_type"] == ft) &
                         (grouped["phase_focus"] == pf)].set_index("noise")
        t_vals = [safe_val(sub, n, "T_FA_mean") for n in NOISE_ORDER]
        r_vals = [safe_val(sub, n, "R_FA_mean") for n in NOISE_ORDER]

        bt = ax.bar(x - width/2, t_vals, width, label="Threshold",
                    color=COLOR_T, alpha=0.85, edgecolor="white", linewidth=0.6)
        br = ax.bar(x + width/2, r_vals, width, label="Rate-of-Change",
                    color=COLOR_R, alpha=0.85, edgecolor="white", linewidth=0.6)

        for bars in (bt, br):
            for bar in bars:
                h = bar.get_height()
                if h >= 1.0:
                    ax.text(bar.get_x() + bar.get_width()/2, h * 1.03,
                            f"{h:.0f}", ha="center", va="bottom", fontsize=7)

        ax.set_title(title, fontweight="bold", fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(NOISE_LABEL_SHORT)
        ax.set_xlabel("Noise Level")
        ax.set_ylabel("Mean False Alarms / Run")
        ax.legend(fontsize=8)

    fig.tight_layout()
    path = os.path.join(FIG_DIR, "py_fig_C_false_alarms.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════════════
# Figure D
# ══════════════════════════════════════════════════════════════════════════

def fig_D_freeze_delay_dist(runs):
    detected = runs[(runs["fault_type"] == "freeze") &
                    (runs["R_missed"] == 0)].copy()

    if len(detected) == 0:
        print("  WARNING: No detected freeze faults in runs data. Skipping Figure D.")
        return

    fig, axes = plt.subplots(1, 2, figsize=(FIG_W, FIG_H), sharey=True)
    fig.suptitle(
        "Figure D — Detection Delay Distribution: Freeze Faults (Rate-of-Change Detector)",
        fontsize=12, fontweight="bold"
    )

    for ax, phase in zip(axes, PHASE_ORDER):
        sub  = detected[detected["phase_focus"] == phase]
        data = [sub[sub["noise"] == n]["R_delay_s"].dropna().values
                for n in NOISE_ORDER]

        valid_data   = [d for d in data if len(d) > 0]
        valid_labels = [NOISE_LABEL[i] for i, d in enumerate(data) if len(d) > 0]
        valid_counts = [len(d)          for d in data if len(d) > 0]

        if not valid_data:
            ax.text(0.5, 0.5, "No detections", transform=ax.transAxes,
                    ha="center", va="center", fontsize=11, color="grey")
            ax.set_title(f"{PHASE_LABEL[phase]} Phase", fontweight="bold")
            continue

        bp = ax.boxplot(
            valid_data, labels=valid_labels, patch_artist=True,
            medianprops=dict(color="black", linewidth=1.8),
            whiskerprops=dict(linewidth=1.2),
            capprops=dict(linewidth=1.2),
            flierprops=dict(marker="o", markersize=3,
                            markerfacecolor=COLOR_R, alpha=0.5)
        )
        for patch in bp["boxes"]:
            patch.set_facecolor(COLOR_R)
            patch.set_alpha(0.55)

        y_bot = ax.get_ylim()[0]
        for xi, n in enumerate(valid_counts, start=1):
            ax.text(xi, y_bot, f"n={n}", ha="center", va="bottom",
                    fontsize=8, color="dimgrey")

        ax.set_title(f"{PHASE_LABEL[phase]} Phase", fontweight="bold")
        ax.set_xlabel("Noise Level")

    axes[0].set_ylabel("Detection Delay (s)")
    fig.tight_layout()
    path = os.path.join(FIG_DIR, "py_fig_D_freeze_delay_dist.png")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


# ══════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════

def main():
    print("\n" + "="*60)
    print("  plot_results.py")
    print("="*60)

    os.makedirs(FIG_DIR, exist_ok=True)

    print("\nLoading data...")
    grouped, runs = load_data()

    print("\nGenerating Figure A...")
    fig_A_bias_delay(grouped)

    print("Generating Figure B...")
    fig_B_freeze_miss(grouped)

    print("Generating Figure C...")
    fig_C_false_alarms(grouped)

    print("Generating Figure D...")
    fig_D_freeze_delay_dist(runs)

    print("\n" + "="*60)
    print(f"  Done. Figures saved to: {FIG_DIR}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
