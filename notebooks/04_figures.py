# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 04 — Figures
#
# Produces the two main figures for the Arctic Amplification replication:
#
# 1. **`figures/main_result.png`** — Time series of Arctic (top) and global
#    (bottom) annual temperature anomalies for all available datasets.
# 2. **`figures/aa_comparison.png`** — Bar chart comparing each dataset's AA
#    ratio against the paper's reported range (3.7–4.1).
#
# Style: `seaborn-v0_8-whitegrid`, dpi=150.
# Rule: always `plt.show()` after `fig.savefig()` — required for MyST inline display.

# %%
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats

PROC_DIR = Path("../data/processed")
RESULTS_DIR = Path("../results")
FIGURES_DIR = Path("../figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Style from USER_PREFERENCES.md
plt.style.use("seaborn-v0_8-whitegrid")
DPI = 150

# %%
# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
ds = xr.open_dataset(PROC_DIR / "annual_means.nc")
df_aa = pd.read_csv(RESULTS_DIR / "aa_ratio.csv")

datasets_present = ds["dataset"].values.tolist()
print(f"Datasets: {datasets_present}")

# Colour palette — consistent across both figures
PALETTE = {
    "era5": "#E63946",      # red
    "gistemp": "#457B9D",   # blue
    "best": "#2A9D8F",      # teal
    "hadcrut5": "#E9C46A",  # amber
}
LABELS = {
    "era5": "ERA5",
    "gistemp": "GISTEMP v4",
    "best": "Berkeley Earth",
    "hadcrut5": "HadCRUT5",
}


# %%
# ---------------------------------------------------------------------------
# Figure 1: Time series — Arctic (top) and global (bottom)
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

ax_arctic, ax_global = axes

for dataset in datasets_present:
    color = PALETTE.get(dataset, "gray")
    label = LABELS.get(dataset, dataset.upper())

    years = ds["year"].values.astype(int)

    arctic_vals = ds["temp_anomaly"].sel(dataset=dataset, region="arctic").values
    global_vals = ds["temp_anomaly"].sel(dataset=dataset, region="global").values

    # Drop NaN
    mask_a = ~np.isnan(arctic_vals)
    mask_g = ~np.isnan(global_vals)

    ax_arctic.plot(years[mask_a], arctic_vals[mask_a], color=color, lw=1.5,
                   label=label, alpha=0.9)
    ax_global.plot(years[mask_g], global_vals[mask_g], color=color, lw=1.5,
                   label=label, alpha=0.9)

    # OLS trend line (Arctic)
    if mask_a.sum() > 2:
        x_a = years[mask_a].astype(float)
        slope_a, intercept_a, *_ = stats.linregress(x_a, arctic_vals[mask_a])
        ax_arctic.plot(years[mask_a], intercept_a + slope_a * x_a,
                       color=color, lw=0.8, ls="--", alpha=0.6)

    # OLS trend line (global)
    if mask_g.sum() > 2:
        x_g = years[mask_g].astype(float)
        slope_g, intercept_g, *_ = stats.linregress(x_g, global_vals[mask_g])
        ax_global.plot(years[mask_g], intercept_g + slope_g * x_g,
                       color=color, lw=0.8, ls="--", alpha=0.6)

ax_arctic.axhline(0, color="black", lw=0.5, ls=":")
ax_global.axhline(0, color="black", lw=0.5, ls=":")

ax_arctic.set_title(
    "Arctic (66.5°N–90°N) annual temperature anomaly\n"
    "(baseline 1979–2021; dashed = OLS trend)",
    fontsize=11,
)
ax_global.set_title(
    "Global annual temperature anomaly\n"
    "(baseline 1979–2021; dashed = OLS trend)",
    fontsize=11,
)
ax_arctic.set_ylabel("Temperature anomaly (°C)")
ax_global.set_ylabel("Temperature anomaly (°C)")
ax_global.set_xlabel("Year")

ax_arctic.legend(loc="upper left", fontsize=9, framealpha=0.8)

fig.suptitle(
    "Arctic Amplification replication — Rantanen et al. 2022\n"
    "(extended to latest available year)",
    fontsize=12,
    y=1.01,
)
fig.tight_layout()
fig.savefig(FIGURES_DIR / "main_result.png", dpi=DPI, bbox_inches="tight")
plt.show()  # required for MyST inline display
print(f"Saved {FIGURES_DIR / 'main_result.png'}")


# %%
# ---------------------------------------------------------------------------
# Figure 2: Bar chart — AA ratio per dataset vs paper values
# ---------------------------------------------------------------------------
# Paper reports: ERA5=3.9, GISTEMP=4.1, BEST=3.7, HadCRUT5=3.7 (1979–2021)
PAPER_AA = {
    "era5": 3.9,
    "gistemp": 4.1,
    "best": 3.7,
    "hadcrut5": 3.7,
}

fig2, ax2 = plt.subplots(figsize=(8, 5))

n_ds = len(df_aa)
x = np.arange(n_ds)
width = 0.35

our_vals = df_aa["aa_ratio"].values
our_labels = df_aa["dataset"].values
paper_vals = np.array([PAPER_AA.get(d, np.nan) for d in our_labels])

colors_our = [PALETTE.get(d, "gray") for d in our_labels]
colors_paper = ["#cccccc"] * n_ds  # grey for paper reference

bars_paper = ax2.bar(
    x - width / 2, paper_vals, width,
    color=colors_paper, edgecolor="black", lw=0.8,
    label="Rantanen et al. 2022 (1979–2021)",
    zorder=2,
)
bars_ours = ax2.bar(
    x + width / 2, our_vals, width,
    color=colors_our, edgecolor="black", lw=0.8,
    label="This replication (1979–latest)",
    zorder=2,
)

# Value labels on bars
for bar, val in zip(bars_paper, paper_vals):
    if not np.isnan(val):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                 f"{val:.1f}", ha="center", va="bottom", fontsize=9)
for bar, val in zip(bars_ours, our_vals):
    if not np.isnan(val):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                 f"{val:.1f}", ha="center", va="bottom", fontsize=9)

# Reference line at paper's multi-dataset mean AA = 3.8
ax2.axhline(3.8, color="#E63946", lw=1.2, ls="--", zorder=1,
            label="Paper multi-dataset mean (3.8)")

ax2.set_xticks(x)
ax2.set_xticklabels([LABELS.get(d, d.upper()) for d in our_labels], fontsize=10)
ax2.set_ylabel("Arctic Amplification ratio", fontsize=11)
ax2.set_ylim(0, max(5.5, np.nanmax([our_vals.max(), 4.5]) + 0.5))
ax2.set_title(
    "Arctic Amplification ratio: replication vs paper\n"
    "(AA = Arctic OLS slope / Global OLS slope, 1979–latest)",
    fontsize=11,
)
ax2.legend(fontsize=9, loc="upper right", framealpha=0.9)

fig2.tight_layout()
fig2.savefig(FIGURES_DIR / "aa_comparison.png", dpi=DPI, bbox_inches="tight")
plt.show()  # required for MyST inline display
print(f"Saved {FIGURES_DIR / 'aa_comparison.png'}")


# %%
# ---------------------------------------------------------------------------
# Figure 3 (optional): Boundary sensitivity — AA vs Arctic lat threshold
# ---------------------------------------------------------------------------
sens_path = RESULTS_DIR / "aa_sensitivity.csv"
if sens_path.exists():
    df_sens = pd.read_csv(sens_path)
    if not df_sens.empty and "arctic_lat_min" in df_sens.columns:
        fig3, ax3 = plt.subplots(figsize=(7, 4))

        for ds_name, grp in df_sens.groupby("dataset"):
            color = PALETTE.get(ds_name, "steelblue")
            label = LABELS.get(ds_name, ds_name.upper())
            ax3.plot(grp["arctic_lat_min"], grp["aa_ratio"],
                     "o-", color=color, lw=1.5, label=label)

        ax3.axvline(66.5, color="black", lw=1.0, ls="--",
                    label="Arctic Circle (66.5°N)")
        ax3.axhline(3.8, color="#E63946", lw=1.0, ls=":",
                    label="Paper mean AA = 3.8")

        ax3.set_xlabel("Arctic boundary (°N)", fontsize=11)
        ax3.set_ylabel("Arctic Amplification ratio", fontsize=11)
        ax3.set_title(
            "AA ratio sensitivity to Arctic boundary definition\n"
            "(global OLS slope as denominator)",
            fontsize=11,
        )
        ax3.legend(fontsize=9)
        fig3.tight_layout()
        fig3.savefig(FIGURES_DIR / "aa_sensitivity.png", dpi=DPI, bbox_inches="tight")
        plt.show()  # required for MyST inline display
        print(f"Saved {FIGURES_DIR / 'aa_sensitivity.png'}")
    else:
        print("[skip] aa_sensitivity.csv is empty — boundary sensitivity figure not produced")
else:
    print("[skip] aa_sensitivity.csv not found")
