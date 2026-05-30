# Snakefile — orchestrates the Arctic Amplification replication pipeline.
#
# Rantanen et al. 2022 (DOI: 10.1038/s43247-022-00498-3)
# Replication: same AA definition + same observational datasets,
# extended to the most recently available year.
#
# Usage:
#   snakemake --cores 1          # run everything
#   snakemake --cores 1 -n       # dry run
#   snakemake --cores 1 --forceall  # re-run even if outputs exist

NOTEBOOKS = "notebooks"
DATA = "data"
RESULTS = "results"
FIGURES = "figures"


rule all:
    input:
        f"{FIGURES}/main_result.png",
        f"{FIGURES}/aa_comparison.png",
        f"{RESULTS}/aa_ratio.csv",
        f"{RESULTS}/aa_sensitivity.csv",


# ---------- 01: Data download ----------
# Downloads ERA5 (requires ~/.cdsapirc), GISTEMP, BEST, and HadCRUT5.
# ERA5 download is skipped gracefully when CDS credentials are absent.
rule data_download:
    output:
        # ERA5 and HadCRUT5 are downloaded best-effort inside the notebook;
        # only GISTEMP, BEST, and sources.json are guaranteed outputs.
        f"{DATA}/raw/sources.json",
        f"{DATA}/raw/gistemp_v4_zonal.csv",
        f"{DATA}/raw/best_land_ocean.nc",
    log:
        f"{RESULTS}/logs/01_data_download.log",
    shell:
        "mkdir -p {RESULTS}/logs && "
        "cd {NOTEBOOKS} && "
        "jupytext --to notebook --execute 01_data_download.py "
        "2>&1 | tee ../{log}"


# ---------- 02: Data clean ----------
# Area-weighted annual means → data/processed/annual_means.nc
rule data_clean:
    input:
        f"{DATA}/raw/sources.json",
        f"{DATA}/raw/gistemp_v4_zonal.csv",
        f"{DATA}/raw/best_land_ocean.nc",
    output:
        f"{DATA}/processed/annual_means.nc",
    log:
        f"{RESULTS}/logs/02_data_clean.log",
    shell:
        "mkdir -p {RESULTS}/logs && "
        "cd {NOTEBOOKS} && "
        "jupytext --to notebook --execute 02_data_clean.py "
        "2>&1 | tee ../{log}"


# ---------- 03: Analysis ----------
# OLS trends and AA ratios → results/aa_ratio.csv + aa_sensitivity.csv
rule analysis:
    input:
        f"{DATA}/processed/annual_means.nc",
    output:
        f"{RESULTS}/aa_ratio.csv",
        f"{RESULTS}/aa_sensitivity.csv",
    log:
        f"{RESULTS}/logs/03_analysis.log",
    shell:
        "mkdir -p {RESULTS}/logs && "
        "cd {NOTEBOOKS} && "
        "jupytext --to notebook --execute 03_analysis.py "
        "2>&1 | tee ../{log}"


# ---------- 04: Figures ----------
# Time series + AA bar chart → figures/main_result.png + aa_comparison.png
rule figures:
    input:
        f"{DATA}/processed/annual_means.nc",
        f"{RESULTS}/aa_ratio.csv",
        f"{RESULTS}/aa_sensitivity.csv",
    output:
        f"{FIGURES}/main_result.png",
        f"{FIGURES}/aa_comparison.png",
    log:
        f"{RESULTS}/logs/04_figures.log",
    shell:
        "mkdir -p {RESULTS}/logs {FIGURES} && "
        "cd {NOTEBOOKS} && "
        "jupytext --to notebook --execute 04_figures.py "
        "2>&1 | tee ../{log}"
