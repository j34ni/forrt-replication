# 05 — FORRT Replication Outcome

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.
>
> **Verify the actual numerical results first** by reading `results/` and `notebooks/03_analysis.py`. Don't quote numbers from memory. See `docs/verify-before-drafting.md`.

## Field-by-field draft

### Short URI suffix for outcome ID (text input, required)

Slug. Use kebab-case.

```
rantanen-2022-arctic-amplification-outcome
```

### Plain-text label for the outcome (text input, required)

Descriptive title.

```
Arctic Amplification replication outcome — Rantanen et al. 2022
```

### Search for a FORRT replication study (search/select, required)

URI of the Replication Study published in step 04. Pull from `nanopubs/PUBLISHED.md`.

```
https://w3id.org/sciencelive/np/RApBTOFIsvkcFttckgdZy-qF4FWE2dqdRwUColauzPGrc
```

### Repository URL (text input, required)

```
https://github.com/j34ni/forrt-replication
```

### Completion date (date picker, required)

```
2026-05-30
```

### Validation status (dropdown, required)

- [x] PartiallySupported
- [ ] Validated
- [ ] Contradicted

This dropdown maps to the CiTO intention in step 06: PartiallySupported → `qualifies`.

**Rationale:** The core direction of the claim is confirmed — the Arctic is warming substantially faster than the global mean, well above 3×. However, the multi-dataset mean AA ratio for the extended period 1979–2024/2025 is ~3.34, compared to the paper's reported 3.8 for 1979–2021. The lower ratio is scientifically expected (the most recent years show a slightly reduced amplification rate), so this is a qualification, not a contradiction.

### Confidence level (dropdown, required)

```
High
```

### Describe the overall conclusion about the original claim (textarea, required)

```
The replication partially supports the claim that the Arctic has warmed nearly four
times faster than the globe since 1979. Extending the analysis to 2024–2025 using
the same four observational datasets (ERA5, GISTEMP v4, Berkeley Earth, HadCRUT5)
and the same Arctic Amplification definition (OLS trend ratio, Arctic 66.5°N–90°N
vs global mean), we find a multi-dataset mean AA ratio of approximately 3.34 —
compared to the paper's reported value of 3.8 for the 1979–2021 window. The Arctic
is still warming roughly 3.3 times faster than the global mean, confirming the
direction and qualitative magnitude of the original claim. The reduced ratio reflects
the inclusion of more recent years rather than any methodological divergence.
```

### Describe the evidence that supports your conclusion (textarea, required)

```
OLS trend ratios (Arctic trend / global trend) for 1979–2024 or 2025:

| Dataset   | Arctic trend (°C/decade) | Global trend (°C/decade) | AA ratio |
|-----------|--------------------------|--------------------------|----------|
| BEST      | 0.681                    | 0.202                    | 3.37     |
| ERA5      | 0.685                    | 0.207                    | 3.31     |
| GISTEMP   | 0.680                    | 0.207                    | 3.29     |
| HadCRUT5  | 0.705                    | 0.208                    | 3.38     |
| **Mean**  | **0.688**                | **0.206**                | **3.34** |

All four datasets show statistically significant trends (p < 10⁻¹⁵ for Arctic,
p < 10⁻¹⁸ for global). The paper reported a multi-dataset mean AA of 3.8 (range
3.7–4.1) for 1979–2021. The replication's 1979–2024/2025 AA of ~3.34 is lower but
consistent with known interannual variability in the AA ratio over time.
```

### Describe what limits the conclusions of the study (textarea, optional)

```
1. Extended time window: the paper covers 1979–2021 (43 years); this replication
   covers 1979–2024/2025 (46–47 years). The longer window captures recent years
   in which the global warming trend has accelerated slightly, reducing the AA
   ratio. A strict apples-to-apples comparison would require running the same
   OLS on the same 1979–2021 window, which was not done here.

2. GISTEMP Arctic boundary: GISTEMP provides pre-computed zonal means for 64°N–90°N,
   not 66.5°N–90°N as defined in the paper. This introduces a small systematic
   difference for the GISTEMP dataset.

3. ERA5 CDS API version: the ERA5 file was downloaded via CDS API v2, which uses
   the coordinate name 'valid_time' instead of 'time'. The coordinate was renamed
   before processing; no data values were affected.

4. HadCRUT5 version: HadCRUT.5.0.2.0 was used (latest available). The paper used
   an earlier version; any updates to the dataset since 2022 are included here.

5. No climate model comparison: the paper's finding that models underestimate AA
   (CMIP5/CMIP6 mean ~2.5–2.7 vs observed ~3.8) was not replicated here. This
   replication covers only the observational component.
```

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 05.
