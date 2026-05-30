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
# # 02 — Data cleaning: area-weighted annual means
#
# Reads each raw dataset from `data/raw/` and produces a single tidy
# intermediate file `data/processed/annual_means.nc` with dimensions
# `(dataset, region, year)` and variable `temp_anomaly`.
#
# ## Method (Rantanen et al. 2022, §2 / Supplementary Methods)
#
# For each dataset:
# 1. **Area-weighted mean** over the region (Arctic: 66.5°N–90°N; Global:
#    90°S–90°N) using cosine-of-latitude weights.
# 2. **Annual mean** from monthly values (calendar-year average).
# 3. **Anomaly** relative to a 1979–2021 baseline (the paper's full window).
#    Using a common baseline ensures all four datasets can be plotted on the
#    same scale for comparison.
#
# ## Deviations from paper
# - The paper uses a 1979–2021 window; this replication extends to 2024 (or as
#   far as each dataset goes). The baseline is still 1979–2021 for comparability.
# - GISTEMP provides pre-computed zonal means (64N–90N), so no spatial
#   aggregation is needed for that dataset; the 64°N threshold vs 66.5°N is
#   noted explicitly.
# - ERA5 is processed only when `data/raw/era5_t2m_monthly.nc` is present.
#   If it is absent the pipeline proceeds with the three other datasets.
#
# ## Output
# `data/processed/annual_means.nc` — NetCDF with:
# - `dataset`: string coordinate (era5, gistemp, best, hadcrut5)
# - `region`: string coordinate (arctic, global)
# - `year`: integer coordinate
# - `temp_anomaly`: float32, degrees Celsius anomaly

# %%
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

RAW_DIR = Path("../data/raw")
PROC_DIR = Path("../data/processed")
PROC_DIR.mkdir(parents=True, exist_ok=True)

# Baseline period for anomaly computation (matches paper's full analysis window)
BASELINE_START = 1979
BASELINE_END = 2021

# Arctic definition (paper uses 66.5°N per the Arctic Circle convention)
ARCTIC_LAT_MIN = 66.5
ARCTIC_LAT_MAX = 90.0


# %%
# ---------------------------------------------------------------------------
# Shared utility: area-weighted zonal mean using cosine(lat) weights
# ---------------------------------------------------------------------------
def area_weighted_mean(
    da: xr.DataArray,
    lat_min: float,
    lat_max: float,
    lat_dim: str = "latitude",
) -> xr.DataArray:
    """
    Compute cosine-latitude-weighted mean over [lat_min, lat_max].

    Parameters
    ----------
    da : DataArray with a latitude dimension named `lat_dim`.
    lat_min, lat_max : bounding box in degrees N.
    lat_dim : name of the latitude coordinate.

    Returns
    -------
    DataArray with the latitude dimension collapsed.
    """
    da_region = da.sel({lat_dim: slice(lat_min, lat_max)})
    weights = np.cos(np.deg2rad(da_region[lat_dim]))
    weights = weights / weights.sum()
    result = (da_region * weights).sum(dim=lat_dim)
    # Also average over longitude for gridded datasets (ERA5, BEST, HadCRUT5)
    lon_dim = next((d for d in result.dims if d in ("longitude", "lon")), None)
    if lon_dim is not None:
        result = result.mean(dim=lon_dim)
    return result


def anomaly_relative_to_baseline(
    da: xr.DataArray,
    baseline_start: int,
    baseline_end: int,
    year_dim: str = "year",
) -> xr.DataArray:
    """Subtract the mean over [baseline_start, baseline_end] from da."""
    baseline = da.sel(
        {year_dim: slice(baseline_start, baseline_end)}
    ).mean(dim=year_dim)
    return da - baseline


# %%
# ---------------------------------------------------------------------------
# Collector: list of (dataset_name, region_name, years_array, anomaly_array)
# ---------------------------------------------------------------------------
records: list[dict] = []  # will be concatenated into xr.Dataset at the end


# %%
# ---------------------------------------------------------------------------
# 1. ERA5 — monthly gridded 2 m temperature (1979–2024)
# ---------------------------------------------------------------------------
# ERA5 is on a regular 1°×1° lat/lon grid.  The CDS download delivers
# temperature in Kelvin; we convert to Celsius before computing anomalies
# (though the anomaly difference cancels the offset).
#
# The file may be absent if CDS credentials were unavailable during download.

era5_path = RAW_DIR / "era5_t2m_monthly.nc"

if era5_path.exists() and era5_path.stat().st_size > 0:
    print("[ERA5] Loading...")
    _era5_dims = xr.open_dataset(era5_path).dims
    _chunks = {"valid_time": 12} if "valid_time" in _era5_dims else {"time": 12}
    ds_era5 = xr.open_dataset(era5_path, chunks=_chunks)

    # Normalise coordinate names — CDS API v2 uses 'valid_time'; older uses 'time'
    rename_map = {}
    if "valid_time" in ds_era5.dims and "time" not in ds_era5.dims:
        rename_map["valid_time"] = "time"
    if "lat" in ds_era5.dims:
        rename_map["lat"] = "latitude"
    if "lon" in ds_era5.dims:
        rename_map["lon"] = "longitude"
    if rename_map:
        ds_era5 = ds_era5.rename(rename_map)

    # Temperature variable name: 't2m' in CDS downloads
    t2m = ds_era5["t2m"]  # shape: (time, latitude, longitude)

    # Sort latitude ascending so slice(66.5, 90) works
    if t2m["latitude"].values[0] > t2m["latitude"].values[-1]:
        t2m = t2m.isel(latitude=slice(None, None, -1))

    # Monthly → annual mean (calendar year)
    t2m_annual = t2m.resample(time="YE").mean(dim="time")
    t2m_annual["year"] = t2m_annual["time"].dt.year
    t2m_annual = t2m_annual.swap_dims({"time": "year"}).drop_vars("time")

    for region_name, lat_min, lat_max in [
        ("arctic", ARCTIC_LAT_MIN, ARCTIC_LAT_MAX),
        ("global", -90.0, 90.0),
    ]:
        series = area_weighted_mean(t2m_annual, lat_min, lat_max)
        anom = anomaly_relative_to_baseline(series, BASELINE_START, BASELINE_END)
        records.append(
            {
                "dataset": "era5",
                "region": region_name,
                "year": anom["year"].values,
                "temp_anomaly": anom.values.astype(np.float32),
            }
        )
    print(f"[ERA5] processed years {records[-1]['year'][0]}–{records[-1]['year'][-1]}")
else:
    print("[ERA5] File not found — skipping (run 01_data_download.py with CDS credentials)")


# %%
# ---------------------------------------------------------------------------
# 2. GISTEMP v4 zonal means (CSV)
# ---------------------------------------------------------------------------
# The NASA GISS zonal CSV has rows = years and columns = latitude bands.
# Relevant columns:
#   "64N-90N"  — closest pre-computed Arctic band (paper uses 66.5°N)
#   "NHem"     — Northern Hemisphere mean (used for reference only)
#   "Glob"     — global mean
#
# NOTE: GISTEMP's zonal bands are fixed at 64°N–90°N, not 66.5°N–90°N.
# This is a known difference from the paper's definition (66.5°N).  The
# 64°N band is the best available approximation from GISTEMP's pre-computed
# output. This deviation is explicitly noted here and in 03_analysis.py.

gistemp_path = RAW_DIR / "gistemp_v4_zonal.csv"

if gistemp_path.exists() and gistemp_path.stat().st_size > 0:
    print("[GISTEMP] Loading...")
    # The CSV has a header row describing units and then the data rows.
    # Year column is "Year"; temperature anomaly unit is °C (×100 in some
    # versions — check actual file).
    df_giss = pd.read_csv(gistemp_path, comment="*", skipinitialspace=True)

    # Normalise column names (strip whitespace)
    df_giss.columns = [c.strip() for c in df_giss.columns]

    # Identify year column (always first or named 'Year')
    year_col = "Year" if "Year" in df_giss.columns else df_giss.columns[0]
    df_giss = df_giss.rename(columns={year_col: "year"})
    df_giss = df_giss[df_giss["year"].astype(str).str.match(r"^\d{4}$")].copy()
    df_giss["year"] = df_giss["year"].astype(int)

    # Select 1979 onward
    df_giss = df_giss[df_giss["year"] >= 1979].reset_index(drop=True)

    # Identify Arctic and Global columns
    # Typical column names: "64N-90N", "Glob"
    arctic_col = next(
        (c for c in df_giss.columns if "64N" in c or "64n" in c.lower()), None
    )
    global_col = next(
        (c for c in df_giss.columns if c.strip().lower() in {"glob", "global"}), None
    )

    if arctic_col is None or global_col is None:
        print(f"  [WARN] Could not identify GISTEMP columns. Available: {list(df_giss.columns)}")
    else:
        for region_name, col in [("arctic", arctic_col), ("global", global_col)]:
            series_vals = pd.to_numeric(df_giss[col], errors="coerce").values.astype(np.float32)
            years = df_giss["year"].values

            # GISTEMP anomalies are already relative to 1951–1980; re-centre to
            # 1979–2021 baseline for consistency with other datasets.
            da = xr.DataArray(series_vals, coords={"year": years}, dims=["year"])
            # Drop years where value is NaN (end of record or missing)
            da = da.dropna(dim="year")
            anom = anomaly_relative_to_baseline(da, BASELINE_START, BASELINE_END)
            records.append(
                {
                    "dataset": "gistemp",
                    "region": region_name,
                    "year": anom["year"].values,
                    "temp_anomaly": anom.values.astype(np.float32),
                }
            )
        print(f"[GISTEMP] Arctic col: '{arctic_col}', Global col: '{global_col}'")
        print(f"[GISTEMP] processed years {records[-1]['year'][0]}–{records[-1]['year'][-1]}")
else:
    print("[GISTEMP] File not found — skipping")


# %%
# ---------------------------------------------------------------------------
# 3. Berkeley Earth (BEST) land+ocean gridded NetCDF
# ---------------------------------------------------------------------------
# The BEST 1°×1° gridded file contains:
#   "temperature"      — monthly temperature anomaly (°C, rel. 1951–1980)
#   "climatology"      — mean seasonal cycle (for adding back if needed)
#   "latitude", "longitude", "time"
#
# We use the anomaly field directly and re-centre to the 1979–2021 baseline.

best_path = RAW_DIR / "best_land_ocean.nc"

if best_path.exists() and best_path.stat().st_size > 0:
    print("[BEST] Loading...")
    ds_best = xr.open_dataset(best_path, chunks={"time": 12})

    # Berkeley Earth uses "latitude"/"longitude" and "time" (as float years or
    # datetime). Identify the temperature anomaly variable.
    temp_var = "temperature" if "temperature" in ds_best else list(ds_best.data_vars)[0]
    t_best = ds_best[temp_var]

    # Sort latitude ascending
    if "latitude" in t_best.dims:
        if t_best["latitude"].values[0] > t_best["latitude"].values[-1]:
            t_best = t_best.isel(latitude=slice(None, None, -1))
        lat_dim = "latitude"
    elif "lat" in t_best.dims:
        t_best = t_best.rename({"lat": "latitude", "lon": "longitude"})
        if t_best["latitude"].values[0] > t_best["latitude"].values[-1]:
            t_best = t_best.isel(latitude=slice(None, None, -1))
        lat_dim = "latitude"
    else:
        raise ValueError(f"Cannot find latitude dim in BEST. Dims: {t_best.dims}")

    # Time → annual mean.  BEST time can be float (decimal years) or datetime.
    time_vals = ds_best["time"].values
    if np.issubdtype(time_vals.dtype, np.floating):
        # Decimal year — extract integer year and average
        years_monthly = time_vals.astype(int)
        t_best_arr = t_best.values  # (time, lat, lon)
        # Group by integer year
        unique_years = np.unique(years_monthly)
        annual_vals = np.stack(
            [t_best_arr[years_monthly == yr].mean(axis=0) for yr in unique_years],
            axis=0,
        )
        t_best_annual = xr.DataArray(
            annual_vals,
            coords={
                "year": unique_years,
                "latitude": t_best["latitude"].values,
                "longitude": t_best["longitude"].values,
            },
            dims=["year", "latitude", "longitude"],
        )
    else:
        # datetime64 — use resample
        t_best_annual = t_best.resample(time="YE").mean(dim="time")
        t_best_annual["year"] = t_best_annual["time"].dt.year
        t_best_annual = t_best_annual.swap_dims({"time": "year"}).drop_vars("time")

    # Filter to 1979 onward
    t_best_annual = t_best_annual.sel(year=t_best_annual["year"] >= 1979)

    for region_name, lat_min, lat_max in [
        ("arctic", ARCTIC_LAT_MIN, ARCTIC_LAT_MAX),
        ("global", -90.0, 90.0),
    ]:
        series = area_weighted_mean(t_best_annual, lat_min, lat_max, lat_dim="latitude")
        anom = anomaly_relative_to_baseline(series, BASELINE_START, BASELINE_END)
        records.append(
            {
                "dataset": "best",
                "region": region_name,
                "year": anom["year"].values,
                "temp_anomaly": anom.values.astype(np.float32),
            }
        )
    print(f"[BEST] processed years {records[-1]['year'][0]}–{records[-1]['year'][-1]}")
else:
    print("[BEST] File not found — skipping")


# %%
# ---------------------------------------------------------------------------
# 4. HadCRUT5 ensemble median gridded NetCDF
# ---------------------------------------------------------------------------
# The Met Office ensemble mean product (HadCRUT.5.x.x.x.analysis.anomalies.
# ensemble_mean.nc) contains:
#   "tas_mean"  — surface air temperature anomaly (°C, rel. 1961–1990)
#   "latitude", "longitude", "time" (monthly, datetime)
#
# Grid: 5°×5° regular lat/lon.  We area-weight as for other datasets.

hadcrut5_path = RAW_DIR / "hadcrut5_median.nc"

if hadcrut5_path.exists() and hadcrut5_path.stat().st_size > 0:
    print("[HadCRUT5] Loading...")
    ds_hc5 = xr.open_dataset(hadcrut5_path, chunks={"time": 12})

    # Identify temperature variable (usually "tas_mean" or "temperature_anomaly")
    temp_var_hc5 = next(
        (v for v in ds_hc5.data_vars if "tas" in v.lower() or "temp" in v.lower()),
        list(ds_hc5.data_vars)[0],
    )
    t_hc5 = ds_hc5[temp_var_hc5]

    # Normalise dim names
    if "lat" in t_hc5.dims and "latitude" not in t_hc5.dims:
        t_hc5 = t_hc5.rename({"lat": "latitude", "lon": "longitude"})

    # Sort latitude ascending
    if t_hc5["latitude"].values[0] > t_hc5["latitude"].values[-1]:
        t_hc5 = t_hc5.isel(latitude=slice(None, None, -1))

    # Monthly → annual mean
    t_hc5_annual = t_hc5.resample(time="YE").mean(dim="time")
    t_hc5_annual["year"] = t_hc5_annual["time"].dt.year
    t_hc5_annual = t_hc5_annual.swap_dims({"time": "year"}).drop_vars("time")

    # Filter to 1979 onward
    t_hc5_annual = t_hc5_annual.sel(year=t_hc5_annual["year"] >= 1979)

    for region_name, lat_min, lat_max in [
        ("arctic", ARCTIC_LAT_MIN, ARCTIC_LAT_MAX),
        ("global", -90.0, 90.0),
    ]:
        series = area_weighted_mean(t_hc5_annual, lat_min, lat_max, lat_dim="latitude")
        anom = anomaly_relative_to_baseline(series, BASELINE_START, BASELINE_END)
        records.append(
            {
                "dataset": "hadcrut5",
                "region": region_name,
                "year": anom["year"].values,
                "temp_anomaly": anom.values.astype(np.float32),
            }
        )
    print(f"[HadCRUT5] processed years {records[-1]['year'][0]}–{records[-1]['year'][-1]}")
else:
    print("[HadCRUT5] File not found — skipping")


# %%
# ---------------------------------------------------------------------------
# Assemble into a single xr.Dataset and save as NetCDF
# ---------------------------------------------------------------------------
# Output structure:
#   Dimensions: dataset × region × year
#   Variable:   temp_anomaly (float32)

if not records:
    raise RuntimeError(
        "No datasets were successfully processed. "
        "Check that at least one raw file is present in data/raw/."
    )

# Determine the union of years across all records
all_years = sorted(
    set(int(y) for rec in records for y in rec["year"])
)

datasets_present = sorted(set(r["dataset"] for r in records))
regions_present = sorted(set(r["region"] for r in records))

# Build a padded array: (n_datasets, n_regions, n_years) filled with NaN
n_d, n_r, n_y = len(datasets_present), len(regions_present), len(all_years)
data_arr = np.full((n_d, n_r, n_y), np.nan, dtype=np.float32)

d_idx = {d: i for i, d in enumerate(datasets_present)}
r_idx = {r: i for i, r in enumerate(regions_present)}
y_idx = {y: i for i, y in enumerate(all_years)}

for rec in records:
    di = d_idx[rec["dataset"]]
    ri = r_idx[rec["region"]]
    for yr, val in zip(rec["year"], rec["temp_anomaly"]):
        yi = y_idx[int(yr)]
        data_arr[di, ri, yi] = val

ds_out = xr.Dataset(
    {
        "temp_anomaly": xr.DataArray(
            data_arr,
            dims=["dataset", "region", "year"],
            coords={
                "dataset": datasets_present,
                "region": regions_present,
                "year": all_years,
            },
            attrs={
                "units": "degC",
                "long_name": "Surface air temperature anomaly",
                "baseline": f"{BASELINE_START}–{BASELINE_END}",
                "note": (
                    "GISTEMP Arctic region is 64N–90N (pre-computed zonal band); "
                    "all other datasets use 66.5N–90N area-weighted mean."
                ),
            },
        )
    },
    attrs={
        "title": "Arctic Amplification replication — annual temperature anomalies",
        "source": "Rantanen et al. 2022 replication (forrt-replication)",
        "created": pd.Timestamp.now().isoformat(),
        "datasets": ", ".join(datasets_present),
        "arctic_definition": "66.5N–90N (GISTEMP: 64N–90N)",
        "baseline_period": f"{BASELINE_START}–{BASELINE_END}",
    },
)

out_path = PROC_DIR / "annual_means.nc"
ds_out.to_netcdf(out_path)
print(f"\nWrote {out_path}")
print(ds_out)
print(f"\nDatasets present: {datasets_present}")
print(f"Regions:          {regions_present}")
print(f"Years:            {all_years[0]}–{all_years[-1]} ({len(all_years)} values)")
