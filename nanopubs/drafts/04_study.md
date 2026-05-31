# 04 — FORRT Replication Study

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.
>
> **Verify code first:** read the actual reproduction script in `notebooks/03_analysis.py` before writing the methodology field. See `docs/verify-before-drafting.md`.

## Field-by-field draft

### Short URI suffix for study ID (text input, required)

Slug. Use kebab-case.

```
rantanen-2022-arctic-amplification-study
```

### Label/name of replication study (text input, required)

Human-readable title.

```
Computational replication of Arctic Amplification — Rantanen et al. 2022
```

### Study type (dropdown, required)

- [x] **Reproduction/Replication Study** — both.

**Rationale:** The study uses the same four observational datasets as the paper (ERA5, GISTEMP v4, Berkeley Earth, HadCRUT5) and the same statistical method (OLS trend ratio), which makes it a reproduction study. It deviates on implementation language (Python/xarray vs R), time window (extended to 2024–2025 vs 2021), and the GISTEMP Arctic boundary (64°N vs 66.5°N), which introduces replication aspects.

### Search for a FORRT claim (search/select, required)

URI of the Claim published in step 03. Pull from `nanopubs/PUBLISHED.md`.

```
https://w3id.org/sciencelive/np/RA7QUD7DRYY2CJOHXFkgBVKQ9Oq8tkykONjLFZe7LNGVs
```

### Describe what part of the claim is reproduced/replicated (textarea, required)

The **scope** of the claim being tested. Which aspect, what's in/out of scope. NOT methodology. NOT results. See `docs/pico-study-outcome-levels.md`.

```
The observational component of the Arctic Amplification claim: whether the ratio of
the Arctic (66.5°N–90°N) linear warming trend to the global mean warming trend,
computed from the same four publicly available observational datasets, exceeds 3×
for the period starting in 1979. The model comparison component of the original
paper (showing that CMIP5/CMIP6 models underestimate the observed AA) is
explicitly out of scope.
```

### Describe how the claim is reproduced/replicated (textarea, required)

The **method** in plain prose. Read `notebooks/03_analysis.py` and any config files first. NOT exact numerical results.

```
Annual mean temperature anomalies for the Arctic region (66.5°N–90°N) and the
global mean are extracted from each of four observational datasets: ERA5 monthly
2-metre temperature (Copernicus CDS), GISTEMP v4 zonal means (NASA GISS),
Berkeley Earth Land+Ocean monthly gridded data, and HadCRUT5. An ordinary
least-squares (OLS) linear trend is fitted to the full available annual series
starting from 1979, separately for the Arctic and global means. The Arctic
Amplification ratio for each dataset is the Arctic OLS slope divided by the global
OLS slope (dimensionless). The headline result is the unweighted mean of the four
per-dataset AA ratios. All computations are implemented in Python using xarray,
numpy, and scipy.stats.linregress. The full pipeline (data download → cleaning →
analysis → figures) is automated via Snakemake and reproduced with pixi-managed
dependencies.
```

### Describe any deviations from original methodology (textarea, optional)

What's different from the original method. Verify against the actual code, don't guess.

```
1. Extended time window: the paper covers 1979–2021 (43 years); this replication
   extends to 1979–2024 or 2025 (46–47 years, depending on dataset availability).

2. Implementation language: the paper's analysis was performed in R (unpublished
   scripts); this replication uses Python 3 with xarray, numpy, and
   scipy.stats.linregress.

3. GISTEMP Arctic boundary: GISTEMP v4 provides pre-computed zonal means for the
   64°N–90°N band, not 66.5°N–90°N as defined in the paper. The pre-computed band
   is used directly, introducing a small systematic difference for this dataset.

4. ERA5 CDS API version: ERA5 data was downloaded via CDS API v2, which labels the
   time coordinate "valid_time" instead of "time". The coordinate is renamed before
   processing; no data values are affected.

5. HadCRUT5 version: HadCRUT5.0.2.0 (latest available at time of replication) was
   used. The paper used an earlier release; any dataset updates since 2022 are
   included in this replication.

6. Boundary sensitivity analysis (replicating paper Fig. 3a): uses ERA5 alone (or
   Berkeley Earth as fallback), not all four datasets as in the paper.

7. No climate model comparison: the paper's CMIP5/CMIP6 comparison is not
   reproduced.
```

### Search keywords (Wikidata) (multi-select, optional)

Provide labels (not QIDs) — the Wikidata search picks up labels.

- Label 1: Arctic amplification
- Label 2: climate change
- Label 3: temperature trend
- Label 4: polar warming

### Search discipline (Wikidata) (search, optional)

Provide labels.

- Discipline label: climatology

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 04.
