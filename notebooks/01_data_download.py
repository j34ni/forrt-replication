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
# # 01 — Data download
#
# Downloads all observational temperature datasets used in the Arctic
# Amplification replication (Rantanen et al. 2022, DOI: 10.1038/s43247-022-00498-3).
#
# ## Datasets
#
# | Dataset | Source | File |
# |---------|--------|------|
# | ERA5 monthly 2 m temperature | Copernicus CDS via `cdsapi` | `era5_t2m_monthly.nc` |
# | GISTEMP v4 zonal means | NASA GISS public CSV | `gistemp_v4_zonal.csv` |
# | Berkeley Earth (BEST) land+ocean | Berkeley Earth public NetCDF | `best_land_ocean.nc` |
# | HadCRUT5 ensemble median | Met Office public NetCDF | `hadcrut5_median.nc` |
#
# ## ERA5 credentials
#
# ERA5 download requires a Copernicus CDS account and a `~/.cdsapirc` file:
#
# ```
# url: https://cds.climate.copernicus.eu/api
# key: <YOUR_PERSONAL_ACCESS_TOKEN>
# ```
#
# Get a token at: https://cds.climate.copernicus.eu/profile
# The ERA5 dataset used is: `reanalysis-era5-single-levels-monthly-means`
#
# In CI, set the GitHub Actions secret `CDSAPI_KEY` and write `~/.cdsapirc`
# using the workflow step documented in DOMAIN.md § Copernicus credentials.
#
# **All downloads are idempotent:** if the target file exists and is non-empty,
# it is skipped. Delete the file to force a fresh download.

# %%
import hashlib
import json
import os
from pathlib import Path

import requests

RAW_DIR = Path("../data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# %%
# ---------------------------------------------------------------------------
# Source registry — FAIR4RS: every input must be traceable and citable.
# ---------------------------------------------------------------------------
SOURCES = [
    {
        "name": "ERA5 monthly mean 2m temperature",
        "provider": "Copernicus Climate Data Store",
        "dataset_id": "reanalysis-era5-single-levels-monthly-means",
        "doi": "10.24381/cds.f17050d7",
        "url": "https://cds.climate.copernicus.eu/",
        "license": "Copernicus License (free for research)",
        "accessed_on": "2026-05-30",
        "local_file": "era5_t2m_monthly.nc",
        "sha256": None,
    },
    {
        "name": "GISTEMP v4 zonal temperature means",
        "provider": "NASA Goddard Institute for Space Studies",
        "doi": "10.1029/2019JD032050",
        "url": (
            "https://data.giss.nasa.gov/gistemp/tabledata_v4/"
            "ZonAnn.Ts+dSST.csv"
        ),
        "license": "Public domain (US Government work)",
        "accessed_on": "2026-05-30",
        "local_file": "gistemp_v4_zonal.csv",
        "sha256": None,
    },
    {
        "name": "Berkeley Earth (BEST) land+ocean temperature",
        "provider": "Berkeley Earth",
        "doi": "10.1175/JCLI-D-18-0094.1",
        "url": (
            "https://berkeley-earth-temperature.s3.amazonaws.com/"
            "Global/Gridded/Land_and_Ocean_LatLong1.nc"
        ),
        "license": "CC-BY 4.0",
        "accessed_on": "2026-05-30",
        "local_file": "best_land_ocean.nc",
        "sha256": None,
    },
    {
        "name": "HadCRUT5 ensemble median (analysis)",
        "provider": "Met Office Hadley Centre / CRU",
        "doi": "10.1029/2019JD032361",
        "url": (
            "https://crudata.uea.ac.uk/cru/data/temperature/"
            "HadCRUT.5.0.2.0.analysis.anomalies.ensemble_mean.nc"
        ),
        "license": "Open Government Licence v3",
        "accessed_on": "2026-05-30",
        "local_file": "hadcrut5_median.nc",
        "sha256": None,
    },
]


# %%
# ---------------------------------------------------------------------------
# Generic HTTP download (GISTEMP, BEST, HadCRUT5)
# ---------------------------------------------------------------------------
def download_http(url: str, dest: Path, label: str) -> Path:
    """Stream-download a URL to dest, skipping if dest already exists."""
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  [skip] {label} already at {dest}")
        return dest
    print(f"  [fetch] {label}")
    headers = {"User-Agent": "forrt-replication/0.1 (research; jiaquinta@vitenhub.no)"}
    with requests.get(url, stream=True, timeout=600, headers=headers) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=65536):
                fh.write(chunk)
    print(f"  [done]  {dest} ({dest.stat().st_size / 1e6:.1f} MB)")
    return dest


def sha256_of(path: Path) -> str:
    """Return hex SHA-256 digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# %%
# ---------------------------------------------------------------------------
# 1. ERA5 monthly 2 m temperature — via cdsapi
# ---------------------------------------------------------------------------
# ERA5 is downloaded at 1-degree resolution, global, all months 1979–2024.
# The variable "2m_temperature" is the near-surface air temperature used in
# the paper.  We request monthly means (product_type: monthly_averaged_reanalysis).
#
# NOTE: this cell requires a valid ~/.cdsapirc. Without it, the download is
# skipped with a warning so that the rest of the pipeline can be tested with
# the other three datasets.

era5_dest = RAW_DIR / "era5_t2m_monthly.nc"

if era5_dest.exists() and era5_dest.stat().st_size > 0:
    print(f"[skip] ERA5 already at {era5_dest}")
else:
    try:
        import cdsapi  # noqa: PLC0415

        c = cdsapi.Client()
        print("[fetch] ERA5 monthly 2m temperature 1979–2024 (global, 1°)...")
        print("  This may take 5–30 minutes depending on CDS queue.")
        c.retrieve(
            "reanalysis-era5-single-levels-monthly-means",
            {
                "product_type": "monthly_averaged_reanalysis",
                "variable": "2m_temperature",
                "year": [str(y) for y in range(1979, 2025)],
                "month": [f"{m:02d}" for m in range(1, 13)],
                "time": "00:00",
                "area": [90, -180, -90, 180],  # N, W, S, E — global
                "grid": [1.0, 1.0],
                "format": "netcdf",
            },
            str(era5_dest),
        )
        print(f"[done] ERA5 at {era5_dest} ({era5_dest.stat().st_size / 1e6:.1f} MB)")
    except Exception as exc:
        print(f"[WARN] ERA5 download failed: {exc}")
        print("       Set up ~/.cdsapirc with a valid CDS API token to enable ERA5.")
        print("       The pipeline will proceed with GISTEMP, BEST, HadCRUT5 only.")

# %%
# ---------------------------------------------------------------------------
# 2. GISTEMP v4 zonal annual means (public CSV)
# ---------------------------------------------------------------------------
# NASA provides a pre-computed zonal means table: rows = years, columns = zones
# including 64N–90N (Arctic) and Global.  This is the simplest path for
# GISTEMP — no need to download and regrid the full gridded product.

gistemp_dest = RAW_DIR / "gistemp_v4_zonal.csv"
gistemp_src = next(s for s in SOURCES if "GISTEMP" in s["name"])
download_http(gistemp_src["url"], gistemp_dest, "GISTEMP v4 zonal CSV")

# %%
# ---------------------------------------------------------------------------
# 3. Berkeley Earth (BEST) land+ocean gridded NetCDF
# ---------------------------------------------------------------------------
# The 1°×1° monthly gridded product contains temperature anomalies
# (relative to 1951–1980 climatology). ~600 MB file.

best_dest = RAW_DIR / "best_land_ocean.nc"
best_src = next(s for s in SOURCES if "Berkeley" in s["name"])
download_http(best_src["url"], best_dest, "Berkeley Earth land+ocean NetCDF")

# %%
# ---------------------------------------------------------------------------
# 4. HadCRUT5 ensemble median (analysis product, monthly global)
# ---------------------------------------------------------------------------
# We download the global monthly summary series. HadCRUT5 also ships regional
# diagnostics, but the gridded file (used in 02_data_clean.py) contains the
# full spatial information needed for area-weighted Arctic means.
#
# The full gridded ensemble median is at:
# https://www.metoffice.gov.uk/hadobs/hadcrut5/data/current/analysis/
#   diagnostics/HadCRUT.5.0.2.0.analysis.anomalies.ensemble_mean.nc
# (~200 MB). We use that for spatial processing in notebook 02.

hadcrut5_gridded_url = (
    "https://crudata.uea.ac.uk/cru/data/temperature/"
    "HadCRUT.5.0.2.0.analysis.anomalies.ensemble_mean.nc"
)
hadcrut5_dest = RAW_DIR / "hadcrut5_median.nc"

if hadcrut5_dest.exists() and hadcrut5_dest.stat().st_size > 0:
    print(f"  [skip] HadCRUT5 already at {hadcrut5_dest}")
else:
    print("[fetch] HadCRUT5 ensemble mean gridded NetCDF (~200 MB)...")
    try:
        download_http(hadcrut5_gridded_url, hadcrut5_dest, "HadCRUT5 gridded ensemble mean")
    except Exception as exc:
        print(f"[WARN] HadCRUT5 download failed: {exc}")
        print("       Pipeline will proceed with GISTEMP, BEST, and ERA5 only.")

# %%
# ---------------------------------------------------------------------------
# Update SOURCES with SHA-256 digests and persist sources.json
# ---------------------------------------------------------------------------
file_map = {
    "ERA5 monthly mean 2m temperature": era5_dest,
    "GISTEMP v4 zonal temperature means": gistemp_dest,
    "Berkeley Earth (BEST) land+ocean temperature": best_dest,
    "HadCRUT5 ensemble median (analysis)": hadcrut5_dest,
}

for src in SOURCES:
    p = file_map.get(src["name"])
    if p and p.exists() and p.stat().st_size > 0:
        src["sha256"] = sha256_of(p)
    else:
        src["sha256"] = None

with open(RAW_DIR / "sources.json", "w") as fh:
    json.dump({"sources": SOURCES}, fh, indent=2)

print(f"\nLogged {len(SOURCES)} source(s) to {RAW_DIR / 'sources.json'}")
for src in SOURCES:
    status = "OK" if src["sha256"] else "MISSING"
    print(f"  [{status}] {src['name']}: {src['local_file']}")
