<div align="center">

# Aircraft Air Data Sensor Fault Detection
### MSc Thesis — Riga Technical University, 2026

**Evaluation of Classical Fault Detection Methods for Aircraft Air Data Sensors Using Simulated Flight Data**

 Furkan Batur Tavli · MSc Mechanical Engineering (Aviation Transport) · 231AMM063

[![MATLAB](https://img.shields.io/badge/MATLAB-R2023+-0076A8?style=flat-square&logo=mathworks&logoColor=white)](https://www.mathworks.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](./Tavli_Furkan_Batur_Diploma_Confidental.pdf)
[![Thesis](https://img.shields.io/badge/Thesis-PDF-red?style=flat-square)](./Furkan_Batur_Tavli_Master_Thesis_231AMM063.pdf)

</div>

---

## 🎯 Overview

Aircraft air data sensors — pitot tubes, static ports, and angle-of-attack vanes — are safety-critical components that feed airspeed, altitude, and attitude data to flight control and avionics systems. Sensor faults have been contributing factors in major aviation accidents including Air France 447 (2009).

This thesis evaluates two **classical fault detection algorithms** — a threshold-based detector and a rate-of-change detector — against two fault types (bias and freeze) injected into simulated Indicated Airspeed (IAS) signals across realistic flight phases.

**600 Monte Carlo simulation runs** across 12 scenarios provide statistically robust performance metrics covering detection delay, missed detection rate, and false alarm rate under low, medium, and high noise conditions.

---

## ✈️ Background & Motivation

Air data sensor faults fall into several categories. This thesis focuses on two of the most operationally significant:

<div align="center">

| Fault Type | Description | Real-world analogue |
|---|---|---|
| **Bias** | Signal permanently offset by a fixed magnitude (+10 kt) after fault onset | Blocked pitot tube, calibration drift |
| **Freeze** | Signal locks at the value recorded at fault onset | Ice blockage, stuck sensor |

</div>

The research question: *How well do simple, computationally inexpensive classical methods perform compared to each other under realistic noise conditions and across climb vs. descent phases?*

This is directly relevant to **CAMO trend monitoring**, **airworthiness engineering**, and the design of lightweight fault detection logic for embedded avionics.

---

## 🏗️ Repository Structure

```
msc-thesis-sensor-fault-detection/
│
├── matlab/                         # Simulation engine (MATLAB)
│   ├── main_run_batch.m            # Monte Carlo batch runner (600 runs)
│   ├── main_run_single.m           # Single-run mode for visualisation
│   ├── config_default.m            # Central configuration (all parameters)
│   │
│   ├── sim/                        # Signal simulation
│   │   ├── generate_profile.m      # Piecewise IAS flight profile (climb/cruise/descent)
│   │   ├── add_noise.m             # Gaussian noise injection
│   │   ├── inject_bias.m           # Bias fault injection
│   │   └── inject_freeze.m         # Freeze fault injection
│   │
│   ├── detect/                     # Detection algorithms
│   │   ├── detect_threshold.m      # Threshold detector (absolute bounds + jump limit)
│   │   └── detect_rate.m           # Rate-of-change detector (phase-aware freeze logic)
│   │
│   ├── eval/
│   │   └── compute_metrics.m       # Detection delay, miss rate, false alarm count
│   │
│   └── utils/
│       ├── set_seed.m
│       ├── make_run_id.m
│       ├── save_run_csv.m
│       └── make_fig_*.m            # Figure generation scripts
│
├── python/                         # Post-processing & visualisation (Python)
│   ├── analyze_results.py          # Statistical aggregation → thesis tables
│   └── plot_results.py             # Publication-quality figures
│
├── results/                        # Pre-generated outputs
│   ├── summary_runs.csv            # Raw results: 600 individual runs
│   ├── summary_grouped.csv         # Aggregated metrics per scenario
│   ├── table_3_1_bias.csv          # Thesis Table 3.1 — Bias fault results
│   ├── table_3_2_freeze.csv        # Thesis Table 3.2 — Freeze fault results
│   └── table_3_3_fa.csv            # Thesis Table 3.3 — False alarm analysis
│
├── figures/                        # Result plots
│   ├── fig3_2_profile_med_seed_1.png
│   ├── fig3_3_bias_med_seed_1_phase_climb.png
│   ├── fig3_4_freeze_med_seed_1_phase_climb.png
│   ├── py_fig_A_bias_delay.png
│   ├── py_fig_B_freeze_miss.png
│   ├── py_fig_C_false_alarms.png
│   └── py_fig_D_freeze_delay_dist.png
│
├── Furkan_Batur_Tavli_Master_Thesis_231AMM063.pdf
├── Tavli_Furkan_Batur_Diploma_Confidental.pdf
└── README.md
```

---

## ⚙️ Simulation Design

### Flight Profile
A 600-second piecewise Indicated Airspeed (IAS) profile simulates a generic short-haul flight:

<div align="center">

| Phase | Time window | IAS range |
|---|---|---|
| Climb | 0 – 200 s | 140 → 250 kt |
| Cruise | 200 – 450 s | 250 kt ± 1 kt (sine variation) |
| Descent | 450 – 600 s | 250 → 160 kt |

</div>

Gaussian noise is applied at three levels: **low** (σ = 0.5 kt), **medium** (σ = 1.0 kt), **high** (σ = 2.0 kt).

### Fault Injection
Faults are injected randomly within 30–60% of the focused phase (climb or descent), ensuring the detector has time to respond within the phase window.

- **Bias:** +10 kt constant offset added after fault onset
- **Freeze:** signal held at the value recorded at fault onset

### Detection Algorithms

**Threshold Detector (`detect_threshold.m`)**
- Flags samples outside absolute bounds [60, 400] kt
- Flags instantaneous jumps exceeding 40 kt/s

**Rate-of-Change Detector (`detect_rate.m`)**
- Flags excessive rate-of-change > 40 kt/s
- Phase-aware freeze detection: flags signals with near-zero rate (< 0.2 kt/s) sustained for ≥ 5 seconds during climb or descent (suppressed in cruise to avoid false alarms)

### Monte Carlo Campaign
- **12 scenarios:** 2 fault types × 3 noise levels × 2 phases
- **50 runs per scenario** with deterministic seeds for reproducibility
- **600 total runs**

---

## 📊 Key Results

### Bias Fault Detection

Both detectors perform strongly on bias faults. The +10 kt offset is large enough to trigger detection almost immediately across all noise levels.

<div align="center">

| Noise | Phase | T Delay (s) | T Miss Rate | R Delay (s) | R Miss Rate |
|---|---|---|---|---|---|
| Low | Climb | 0.00 | 0.00 | 0.00 | 0.00 |
| Low | Descent | 0.00 | 0.00 | 0.00 | 0.00 |
| Medium | Climb | 0.00 | 0.00 | 0.00 | 0.00 |
| Medium | Descent | 0.00 | 0.00 | 0.00 | 0.00 |
| High | Climb | 0.00 | 0.00 | 0.00 | 0.00 |
| High | Descent | 0.03 | 0.00 | 0.03 | 0.00 |

T = Threshold Detector · R = Rate-of-Change Detector

</div>

**Finding:** Both methods detect bias faults with near-zero delay and zero missed detections across all noise levels. High noise introduces a marginal 0.03 s delay, but reliability remains perfect.

---

### Freeze Fault Detection

This is where the detectors diverge significantly.

<div align="center">

| Noise | Phase | T Delay (s) | T Miss Rate | R Delay (s) | R Miss Rate |
|---|---|---|---|---|---|
| Low | Climb | — | **1.00** | 5.00 | 0.00 |
| Low | Descent | — | **1.00** | 4.99 | 0.00 |
| Medium | Climb | — | **1.00** | 5.00 | 0.00 |
| Medium | Descent | — | **1.00** | 5.00 | 0.00 |
| High | Climb | 0.00 | 0.78 | 3.90 | 0.00 |
| High | Descent | 0.00 | 0.86 | 4.30 | 0.00 |

</div>

**Finding:** The threshold detector **completely fails** to detect freeze faults at low and medium noise (100% miss rate) — a frozen signal within normal bounds is invisible to absolute-limit checks. The rate-of-change detector detects all freeze faults with a consistent ~5 s delay (by design: the hold window). Under high noise, the threshold detector paradoxically recovers, as noise-induced jumps around the frozen value trigger the jump limit.

---

### False Alarm Analysis

<div align="center">

| Fault | Noise | Phase | T FA Mean | R FA Mean |
|---|---|---|---|---|
| Bias | Low | Climb | 0.00 | 0.00 |
| Bias | Medium | Climb | 3.64 | 3.64 |
| Bias | High | Climb | 95.42 | 95.42 |
| Freeze | High | Descent | 573.06 | 573.06 |

</div>

**Finding:** False alarm rates remain at zero under low noise for both detectors. Under high noise, false alarms increase substantially — predominantly in the descent phase where rate-of-change variability is highest. Both detectors share the same false alarm profile since both use rate-based logic for the jump/rate check.

---

## 🔍 Conclusions

1. **For bias faults:** Both detectors are equally effective. Either can be deployed without concern for noise level within the tested range.

2. **For freeze faults:** The rate-of-change detector is categorically superior. Threshold-based detection is blind to freeze faults when the frozen value falls within normal operating bounds — a fundamental design limitation with direct safety implications.

3. **Noise-reliability tradeoff:** High noise degrades both detectors through increased false alarms. Adaptive thresholds or noise-aware hold windows would be the logical next step.

4. **Phase sensitivity:** Descent scenarios consistently produce higher false alarm counts than climb, due to the steeper and more variable rate-of-change profile during descent.

> **Practical implication:** A combined detector using threshold limits for bias and rate-of-change logic for freeze would outperform either method alone — a straightforward enhancement for embedded CAMO monitoring systems.

---

## 🚀 How to Run

### Requirements
- MATLAB R2023+ (no additional toolboxes required)
- Python 3.9+ with `pandas` and `numpy`

### Step 1 — Run Simulations (MATLAB)
```matlab
% Run the full 600-run Monte Carlo campaign
main_run_batch

% Or run and visualise a single scenario
main_run_single
```
Output CSVs are saved to `matlab/output/summaries/`.

### Step 2 — Post-process Results (Python)
```bash
pip install pandas numpy
python python/analyze_results.py
```
Generates grouped summary and thesis tables.

### Step 3 — Generate Figures (Python)
```bash
python python/plot_results.py
```
Saves publication-quality figures to `figures/`.

---

<div align="center">

## 📄 Documents

| Document | Description |
|---|---|
| [`Master_Thesis.pdf`](./Furkan_Batur_Tavli_Master_Thesis_231AMM063.pdf) | Full thesis — methodology, literature review, results, conclusions |
| [`Diploma.pdf`](./Tavli_Furkan_Batur_Diploma_Confidental.pdf) | MSc degree certificate — Riga Technical University, 2026 |

---

## 👤 Author

**Furkan Batur Tavli**
MSc Mechanical Engineering (Aviation Transport) · Riga Technical University

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/furkan-batur-tavli/)
[![GitHub](https://img.shields.io/badge/Portfolio-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/fbaturt/Data-Analytics-Portfolio)
[![Email](https://img.shields.io/badge/Email-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:furkanbaturtavli@gmail.com)

---

*This repository contains the complete simulation codebase, result datasets, and analysis scripts produced for the MSc thesis at Riga Technical University (2026).*

</div>
