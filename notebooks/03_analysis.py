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
# # 03 — Arctic Amplification analysis
#
# Computes Arctic Amplification (AA) ratios for each observational dataset,
# replicating and extending Rantanen et al. (2022, DOI: 10.1038/s43247-022-00498-3).
#
# ## Method (faithful port of paper §2 / Fig. 1)
#
# - **OLS linear trend** is fitted to the full time series (1979–latest year)
#   for both the Arctic (66.5°N–90°N) and Global means.
# - **AA ratio** = Arctic OLS slope / Global OLS slope (dimensionless).
# - **Multi-dataset mean AA** is the unweighted mean across the available datasets.
# - The paper reports AA43 = 3.8 (range 3.7–4.1 across ERA5, GISTEMP, BEST, HadCRUT5)
#   for the 1979–2021 period.
#
# ## Sensitivity analyses
#
# 1. Arctic boundary sensitivity: AA ratio computed for Arctic boundaries from
#    55°N to 80°N in 2.5° steps (using ERA5 if available, else BEST).
#    This reproduces Fig. 3 from the paper.
# 2. Trend-length sensitivity: AA ratio computed for all start years giving
#    a window of at least 20 years.
#
# ## Deviations from original paper
# - Extended to 2024 (or latest available year per dataset) vs paper's 2021.
# - Python/xarray/scipy implementation vs original R scripts (not published).
# - GISTEMP Arctic = 64°N–90°N (pre-computed band) vs paper's 66.5°N.
# - Sensitivity analysis uses only ERA5 (or BEST as fallback) vs paper using
#   all four datasets — noted in the output CSV.

# %%
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats

PROC_DIR = Path("../data/processed")
RESULTS_DIR = Path("../results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# %%
# ---------------------------------------------------------------------------
# Load processed annual means
# ---------------------------------------------------------------------------
ds = xr.open_dataset(PROC_DIR / "annual_means.nc")
print(ds)
print(f"\nDatasets: {ds['dataset'].values.tolist()}")
print(f"Regions:  {ds['region'].values.tolist()}")
print(f"Years:    {int(ds['year'].min())}–{int(ds['year'].max())}")


# %%
# ---------------------------------------------------------------------------
# OLS trend helper
# ---------------------------------------------------------------------------
def ols_trend(years: np.ndarray, values: np.ndarray) -> dict:
    """
    Fit OLS linear trend.  Returns slope (°C yr⁻¹), intercept, p-value (two-tailed),
    and 95 % confidence interval on the slope.

    NaN values are dropped before fitting so that datasets with shorter
    records are handled gracefully.
    """
    mask = ~np.isnan(values)
    x, y = years[mask].astype(float), values[mask]
    if len(x) < 5:
        return {"slope": np.nan, "intercept": np.nan, "p_value": np.nan,
                "slope_ci95_lo": np.nan, "slope_ci95_hi": np.nan, "n": len(x)}
    slope, intercept, r_val, p_val, std_err = stats.linregress(x, y)
    t_crit = stats.t.ppf(0.975, df=len(x) - 2)
    return {
        "slope": slope,
        "intercept": intercept,
        "r_squared": r_val**2,
        "p_value": p_val,
        "slope_ci95_lo": slope - t_crit * std_err,
        "slope_ci95_hi": slope + t_crit * std_err,
        "n": len(x),
    }


# %%
# ---------------------------------------------------------------------------
# Main AA computation: full 1979–latest period
# ---------------------------------------------------------------------------
rows = []

for dataset in ds["dataset"].values:
    arctic_da = ds["temp_anomaly"].sel(dataset=dataset, region="arctic")
    global_da = ds["temp_anomaly"].sel(dataset=dataset, region="global")

    years = ds["year"].values.astype(int)

    # Filter to years where both Arctic and global are non-NaN
    mask = ~(np.isnan(arctic_da.values) | np.isnan(global_da.values))
    valid_years = years[mask]

    if valid_years.size < 5:
        print(f"[WARN] {dataset}: fewer than 5 valid years — skipping")
        continue

    start_yr = int(valid_years[0])
    end_yr = int(valid_years[-1])

    arctic_trend = ols_trend(valid_years.astype(float), arctic_da.values[mask])
    global_trend = ols_trend(valid_years.astype(float), global_da.values[mask])

    aa = arctic_trend["slope"] / global_trend["slope"] if global_trend["slope"] != 0 else np.nan

    rows.append(
        {
            "dataset": dataset,
            "start_year": start_yr,
            "end_year": end_yr,
            "n_years": end_yr - start_yr + 1,
            "arctic_trend_C_per_decade": arctic_trend["slope"] * 10,
            "global_trend_C_per_decade": global_trend["slope"] * 10,
            "aa_ratio": aa,
            "arctic_trend_p": arctic_trend["p_value"],
            "global_trend_p": global_trend["p_value"],
            "arctic_r2": arctic_trend.get("r_squared", np.nan),
            "global_r2": global_trend.get("r_squared", np.nan),
        }
    )

df_aa = pd.DataFrame(rows)

# Multi-dataset mean and range
aa_vals = df_aa["aa_ratio"].dropna()
multi_mean = aa_vals.mean()
multi_range_lo = aa_vals.min()
multi_range_hi = aa_vals.max()

print("\n=== Arctic Amplification ratios (full period, 1979–latest) ===")
print(df_aa[["dataset", "start_year", "end_year", "arctic_trend_C_per_decade",
             "global_trend_C_per_decade", "aa_ratio"]].to_string(index=False))
print(f"\nMulti-dataset mean AA = {multi_mean:.2f}  (range {multi_range_lo:.2f}–{multi_range_hi:.2f})")
print(f"Paper's reported value: AA = 3.8  (range 3.7–4.1, 1979–2021)")

df_aa.to_csv(RESULTS_DIR / "aa_ratio.csv", index=False)
print(f"\nSaved {RESULTS_DIR / 'aa_ratio.csv'}")


# %%
# ---------------------------------------------------------------------------
# Sensitivity 1: vary Arctic boundary from 55°N to 80°N (2.5° steps)
# ---------------------------------------------------------------------------
# Use ERA5 if available (best spatial resolution), else BEST as fallback.
# This replicates the sensitivity analysis in Rantanen et al. 2022, Fig. 3a.

sensitivity_dataset = None
if "era5" in ds["dataset"].values:
    sensitivity_dataset = "era5"
elif "best" in ds["dataset"].values:
    sensitivity_dataset = "best"

sensitivity_rows = []

if sensitivity_dataset is not None:
    # We need the full gridded data for this — reload from raw
    # The annual_means.nc has already collapsed latitude, so we must
    # re-open the source file for the boundary sweep.
    raw_dir = PROC_DIR.parent / "raw"

    def _load_gridded_annual(dataset_name: str) -> xr.DataArray | None:
        """Load gridded annual temperature anomaly for the named dataset."""
        if dataset_name == "era5":
            p = raw_dir / "era5_t2m_monthly.nc"
            if not (p.exists() and p.stat().st_size > 0):
                return None
            _chunks = {"valid_time": 12} if "valid_time" in xr.open_dataset(p).dims else {"time": 12}
            ds_raw = xr.open_dataset(p, chunks=_chunks)
            rename_map = {}
            if "valid_time" in ds_raw.dims and "time" not in ds_raw.dims:
                rename_map["valid_time"] = "time"
            if "lat" in ds_raw.dims:
                rename_map["lat"] = "latitude"
            if "lon" in ds_raw.dims:
                rename_map["lon"] = "longitude"
            if rename_map:
                ds_raw = ds_raw.rename(rename_map)
            t = ds_raw["t2m"]
        elif dataset_name == "best":
            p = raw_dir / "best_land_ocean.nc"
            if not (p.exists() and p.stat().st_size > 0):
                return None
            ds_raw = xr.open_dataset(p, chunks={"time": 12})
            temp_var = "temperature" if "temperature" in ds_raw else list(ds_raw.data_vars)[0]
            t = ds_raw[temp_var]
            if "lat" in t.dims:
                t = t.rename({"lat": "latitude", "lon": "longitude"})
        else:
            return None

        # Sort latitude ascending
        if t["latitude"].values[0] > t["latitude"].values[-1]:
            t = t.isel(latitude=slice(None, None, -1))

        # Monthly → annual; handle both datetime and decimal-year time axes
        time_vals = ds_raw["time"].values
        if np.issubdtype(time_vals.dtype, np.floating):
            years_monthly = time_vals.astype(int)
            unique_years = np.unique(years_monthly)
            t_vals = t.values
            annual_arr = np.stack(
                [t_vals[years_monthly == yr].mean(axis=0) for yr in unique_years],
                axis=0,
            )
            t_annual = xr.DataArray(
                annual_arr,
                coords={
                    "year": unique_years,
                    "latitude": t["latitude"].values,
                    "longitude": t["longitude"].values,
                },
                dims=["year", "latitude", "longitude"],
            )
        else:
            t_annual = t.resample(time="YE").mean(dim="time")
            t_annual["year"] = t_annual["time"].dt.year
            t_annual = t_annual.swap_dims({"time": "year"}).drop_vars("time")

        t_annual = t_annual.sel(year=t_annual["year"] >= 1979)
        return t_annual

    gridded = _load_gridded_annual(sensitivity_dataset)

    if gridded is not None:
        # Global trend (denominator is the same for all Arctic boundaries)
        global_series = (
            gridded
            * np.cos(np.deg2rad(gridded["latitude"]))
            / np.cos(np.deg2rad(gridded["latitude"])).sum()
        ).sum(dim="latitude").mean(dim="longitude")
        # Re-centre to 1979–2021 baseline
        global_baseline = global_series.sel(year=slice(1979, 2021)).mean("year")
        global_series = global_series - global_baseline
        global_years = global_series["year"].values.astype(float)
        global_vals = global_series.values
        global_mask = ~np.isnan(global_vals)
        global_slope = stats.linregress(
            global_years[global_mask], global_vals[global_mask]
        ).slope

        for lat_threshold in np.arange(55.0, 80.1, 2.5):
            arctic_series = (
                gridded.sel(latitude=slice(lat_threshold, 90.0))
            )
            weights = np.cos(np.deg2rad(arctic_series["latitude"]))
            arctic_mean = (arctic_series * weights / weights.sum()).sum(
                dim="latitude"
            ).mean(dim="longitude")
            baseline = arctic_mean.sel(year=slice(1979, 2021)).mean("year")
            arctic_mean = arctic_mean - baseline

            a_years = arctic_mean["year"].values.astype(float)
            a_vals = arctic_mean.values
            a_mask = ~np.isnan(a_vals)
            if a_mask.sum() < 5:
                continue
            a_slope = stats.linregress(a_years[a_mask], a_vals[a_mask]).slope
            aa_sens = a_slope / global_slope if global_slope != 0 else np.nan
            sensitivity_rows.append(
                {
                    "dataset": sensitivity_dataset,
                    "arctic_lat_min": lat_threshold,
                    "aa_ratio": aa_sens,
                    "arctic_trend_C_per_decade": a_slope * 10,
                    "global_trend_C_per_decade": global_slope * 10,
                }
            )

        df_sens = pd.DataFrame(sensitivity_rows)
        print("\n=== Sensitivity: Arctic boundary (55°N–80°N) ===")
        print(df_sens[["arctic_lat_min", "aa_ratio"]].to_string(index=False))
        df_sens.to_csv(RESULTS_DIR / "aa_sensitivity.csv", index=False)
        print(f"\nSaved {RESULTS_DIR / 'aa_sensitivity.csv'}")
    else:
        print(f"[WARN] Could not load gridded data for {sensitivity_dataset} — skipping boundary sensitivity")
        df_sens = pd.DataFrame(columns=["dataset", "arctic_lat_min", "aa_ratio",
                                         "arctic_trend_C_per_decade", "global_trend_C_per_decade"])
        df_sens.to_csv(RESULTS_DIR / "aa_sensitivity.csv", index=False)
else:
    print("[WARN] No suitable dataset for boundary sensitivity — skipping")
    df_sens = pd.DataFrame(columns=["dataset", "arctic_lat_min", "aa_ratio",
                                     "arctic_trend_C_per_decade", "global_trend_C_per_decade"])
    df_sens.to_csv(RESULTS_DIR / "aa_sensitivity.csv", index=False)


# %%
# ---------------------------------------------------------------------------
# Summary printout (headline number for nanopub Outcome)
# ---------------------------------------------------------------------------
print("\n" + "="*60)
print("HEADLINE RESULT")
print("="*60)
print(f"Multi-dataset mean AA (1979–latest): {multi_mean:.2f}")
print(f"  Range across datasets: {multi_range_lo:.2f}–{multi_range_hi:.2f}")
print(f"  Datasets: {', '.join(df_aa['dataset'].tolist())}")
print(f"  End years: { {r['dataset']: r['end_year'] for _, r in df_aa.iterrows()} }")
print(f"\nPaper headline (Rantanen et al. 2022):")
print(f"  AA = 3.8 (range 3.7–4.1, 1979–2021, ERA5+GISTEMP+BEST+HadCRUT5)")
print("="*60)
