# 02 — AIDA Sentence

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.

**Form heading:** *"AIDA Sentence — Make structured scientific claims following the AIDA model"*

## Field-by-field draft

### AIDA sentence (textarea, required)

Atomic, Independent, Declarative, Absolute. One empirical finding. Must end with a full stop.

> _If your draft AIDA contains "and" linking two distinct findings, split into two AIDA nanopubs._

```
The mean Arctic Amplification ratio (Arctic OLS warming trend / global OLS warming trend, 1979–2021) was 3.8 across four observational datasets (ERA5, GISTEMP v4, Berkeley Earth, HadCRUT5), indicating that the Arctic warmed approximately four times faster than the global mean.
```

### Select related topics/tags (dropdown, optional)

Predefined topic vocabulary — list the labels you intend to pick from the dropdown.

```
climate change
temperature
climatology
```

> Note: the dropdown is Wikidata-linked; only terms tied to existing publications are available. "Arctic amplification", "temperature trend", "polar warming", and "observational climatology" had no matching entries. The three above were the closest available matches.

### Relates to this nanopublication (text input, required)

URI of the nanopub the AIDA derives from.

- For paper-rooted chains: the Quote-with-comment URI (from step 01).
- For question-rooted chains: the PICO or PCC URI (from step 01).

Pull the URI from `nanopubs/PUBLISHED.md`.

```
https://w3id.org/sciencelive/np/RACDO0UWMNmksxCsB-cXrci0udSs3d_1qEVP9l7zVJmfE
```

### Supported by datasets (repeatable group, optional)

DOIs/URLs of datasets that ground the AIDA claim.

- DOI 1: `https://doi.org/10.24381/cds.f17050d7` (ERA5 monthly averaged data on single levels — Copernicus CDS)
- DOI 2: `https://doi.org/10.7289/V5N58JJ9` (GISTEMP v4 — NASA GISS)
- DOI 3: `https://doi.org/10.5194/essd-12-3469-2020` (Berkeley Earth Land+Ocean, Rohde & Hausfather 2020)
- DOI 4: `https://doi.org/10.1029/2019GL085237` (HadCRUT5 — Morice et al. 2021)

### Supported by other publications (repeatable group, optional)

DOIs/URLs of publications that support the AIDA claim — e.g. peer-reviewed methods papers, or the original paper if not already cited via the Quote.

- DOI 1: `https://doi.org/10.1038/s43247-022-00498-3` (Rantanen et al. 2022)

> **Known platform bug (2026-04-26):** if both *Supported by datasets* AND *Supported by other publications* are populated and publishing fails, fall back to publishing this AIDA via Nanodash. The URI namespace becomes `https://w3id.org/np/...` (still valid and citable).

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 02.
