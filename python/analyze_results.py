"""
analyze_results.py
------------------
Statistical post-processing of Monte Carlo simulation results.
 
Loads summary_runs.csv produced by main_run_batch.m, computes grouped
performance metrics, and exports:
  - summary_grouped.csv   : mean metrics per scenario
  - table_3_1_bias.csv    : Chapter 3, Table 3.1 (bias fault results)
  - table_3_2_freeze.csv  : Chapter 3, Table 3.2 (freeze fault results)
  - table_3_3_fa.csv      : Chapter 3, Table 3.3 (false alarm analysis)
 
Usage:
    python analyze_results.py
 
Input:
    output/summaries/summary_runs.csv
 
Outputs:
    output/summaries/summary_grouped.csv
    output/summaries/table_3_1_bias.csv
    output/summaries/table_3_2_freeze.csv
    output/summaries/table_3_3_fa.csv
 
Dependencies:
    pandas >= 1.3
    numpy  >= 1.21
"""
 
import os
import numpy as np
import pandas as pd
 
# ── Paths ──────────────────────────────────────────────────────────────────
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SUMM_DIR   = os.path.join(_SCRIPT_DIR, "..", "matlab", "output", "summaries")
INPUT_PATH  = os.path.join(_SUMM_DIR, "summary_runs.csv")
OUTPUT_DIR  = _SUMM_DIR
 
NOISE_ORDER = ["low", "med", "high"]
NOISE_LABEL = {"low": "Low", "med": "Medium", "high": "High"}
PHASE_ORDER = ["climb", "descent"]
PHASE_LABEL = {"climb": "Climb", "descent": "Descent"}
 
 
def load_data(path):
    """Load and validate the simulation run summary CSV."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Input file not found: {path}\n"
            "Run main_run_batch.m in MATLAB first to generate simulation results."
        )
    df = pd.read_csv(path)
    required = [
        "fault_type", "noise", "phase_focus",
        "T_delay_s", "T_missed", "T_false_alarms",
        "R_delay_s", "R_missed", "R_false_alarms"
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in input CSV: {missing}")
    print(f"Loaded {len(df)} simulation runs from: {path}")
    return df
 
 
def compute_grouped_metrics(df):
    """
    Compute mean detection delay, missed detection rate, and mean false
    alarm count per scenario group (fault_type x noise x phase_focus).
 
    Detection delay is averaged only over non-missed runs (missed == 0),
    consistent with the thesis methodology Section 2.7.1.
    """
    rows = []
    groups = df.groupby(["fault_type", "noise", "phase_focus"])
 
    for (ft, nn, pf), grp in groups:
        n = len(grp)
 
        # Threshold detector metrics
        T_detected = grp[grp["T_missed"] == 0]
        T_delay_mean = T_detected["T_delay_s"].mean() if len(T_detected) > 0 else np.nan
        T_miss_rate  = grp["T_missed"].mean()
        T_FA_mean    = grp["T_false_alarms"].mean()
 
        # Rate-of-change detector metrics
        R_detected = grp[grp["R_missed"] == 0]
        R_delay_mean = R_detected["R_delay_s"].mean() if len(R_detected) > 0 else np.nan
        R_miss_rate  = grp["R_missed"].mean()
        R_FA_mean    = grp["R_false_alarms"].mean()
 
        rows.append({
            "fault_type":    ft,
            "noise":         nn,
            "phase_focus":   pf,
            "T_delay_mean":  round(T_delay_mean, 4) if not np.isnan(T_delay_mean) else np.nan,
            "T_miss_rate":   round(T_miss_rate, 4),
            "T_FA_mean":     round(T_FA_mean, 4),
            "R_delay_mean":  round(R_delay_mean, 4) if not np.isnan(R_delay_mean) else np.nan,
            "R_miss_rate":   round(R_miss_rate, 4),
            "R_FA_mean":     round(R_FA_mean, 4),
            "n":             n
        })
 
    grouped = pd.DataFrame(rows)
 
    # Sort by fault_type, noise level order, phase
    grouped["noise_order"] = grouped["noise"].map(
        {k: i for i, k in enumerate(NOISE_ORDER)}
    )
    grouped = grouped.sort_values(
        ["fault_type", "noise_order", "phase_focus"]
    ).drop(columns=["noise_order"]).reset_index(drop=True)
 
    return grouped
 
 
def format_delay(val):
    """Format detection delay for thesis tables. NaN -> em dash."""
    if pd.isna(val):
        return "—"
    return f"{val:.2f}"
 
 
def build_table_3_1_bias(grouped):
    """
    Build Table 3.1: Mean Detection Metrics for Bias Faults.
    Columns: Noise | Phase | T Delay (s) | T Miss Rate | R Delay (s) | R Miss Rate
    """
    bias = grouped[grouped["fault_type"] == "bias"].copy()
    rows = []
    for _, row in bias.iterrows():
        rows.append({
            "Noise":         NOISE_LABEL.get(row["noise"], row["noise"]),
            "Phase":         PHASE_LABEL.get(row["phase_focus"], row["phase_focus"]),
            "T Delay (s)":   format_delay(row["T_delay_mean"]),
            "T Miss Rate":   f"{row['T_miss_rate']:.2f}",
            "R Delay (s)":   format_delay(row["R_delay_mean"]),
            "R Miss Rate":   f"{row['R_miss_rate']:.2f}",
        })
    return pd.DataFrame(rows)
 
 
def build_table_3_2_freeze(grouped):
    """
    Build Table 3.2: Mean Detection Metrics for Freeze Faults.
    Columns: Noise | Phase | T Delay (s) | T Miss Rate | R Delay (s) | R Miss Rate
    """
    freeze = grouped[grouped["fault_type"] == "freeze"].copy()
    rows = []
    for _, row in freeze.iterrows():
        rows.append({
            "Noise":         NOISE_LABEL.get(row["noise"], row["noise"]),
            "Phase":         PHASE_LABEL.get(row["phase_focus"], row["phase_focus"]),
            "T Delay (s)":   format_delay(row["T_delay_mean"]),
            "T Miss Rate":   f"{row['T_miss_rate']:.2f}",
            "R Delay (s)":   format_delay(row["R_delay_mean"]),
            "R Miss Rate":   f"{row['R_miss_rate']:.2f}",
        })
    return pd.DataFrame(rows)
 
 
def build_table_3_3_false_alarms(grouped):
    """
    Build Table 3.3: Mean False Alarm Events per Run.
    Columns: Fault | Noise | Phase | T FA Mean | R FA Mean
    """
    rows = []
    for _, row in grouped.iterrows():
        rows.append({
            "Fault":     row["fault_type"].capitalize(),
            "Noise":     NOISE_LABEL.get(row["noise"], row["noise"]),
            "Phase":     PHASE_LABEL.get(row["phase_focus"], row["phase_focus"]),
            "T FA Mean": f"{row['T_FA_mean']:.2f}",
            "R FA Mean": f"{row['R_FA_mean']:.2f}",
        })
    return pd.DataFrame(rows)
 
 
def print_table(title, df):
    """Print a formatted table to console."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)
    print(df.to_string(index=False))
 
 
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
 
    # Load data
    df = load_data(INPUT_PATH)
 
    # Compute grouped metrics
    print("\nComputing grouped scenario metrics...")
    grouped = compute_grouped_metrics(df)
 
    # Save grouped summary
    grouped_path = os.path.join(OUTPUT_DIR, "summary_grouped.csv")
    grouped.to_csv(grouped_path, index=False)
    print(f"Saved: {grouped_path}")
 
    # Build and save thesis tables
    t31 = build_table_3_1_bias(grouped)
    t32 = build_table_3_2_freeze(grouped)
    t33 = build_table_3_3_false_alarms(grouped)
 
    t31.to_csv(os.path.join(OUTPUT_DIR, "table_3_1_bias.csv"), index=False)
    t32.to_csv(os.path.join(OUTPUT_DIR, "table_3_2_freeze.csv"), index=False)
    t33.to_csv(os.path.join(OUTPUT_DIR, "table_3_3_fa.csv"), index=False)
    print("Saved: table_3_1_bias.csv, table_3_2_freeze.csv, table_3_3_fa.csv")
 
    # Print tables to console for verification
    print_table("Table 3.1 — Bias Fault Detection Metrics", t31)
    print_table("Table 3.2 — Freeze Fault Detection Metrics", t32)
    print_table("Table 3.3 — False Alarm Analysis", t33)
 
    # Summary statistics
    print(f"\n{'='*70}")
    print("  CAMPAIGN SUMMARY")
    print('='*70)
    print(f"  Total simulation runs  : {len(df)}")
    print(f"  Fault types            : {sorted(df['fault_type'].unique())}")
    print(f"  Noise levels           : {NOISE_ORDER}")
    print(f"  Flight phases          : {sorted(df['phase_focus'].unique())}")
    print(f"  Runs per scenario      : {df.groupby(['fault_type','noise','phase_focus']).size().iloc[0]}")
    print(f"  Scenarios total        : {len(grouped)}")
    print(f"\nPost-processing complete.")
 
 
if __name__ == "__main__":
    main()
 
