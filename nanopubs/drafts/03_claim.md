# 03 — FORRT Claim

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.

**Form heading:** *"FORRT Claim — Declare an original claim according to FORRT, linking it to an AIDA sentence with a specific FORRT type."*

## Field-by-field draft

### Short URI suffix as claim ID (text input, required)

Slug becomes part of the nanopub URI. Use kebab-case.

```
rantanen-2022-arctic-amplification-claim
```

### Label of the claim (text input, required)

A descriptive title (not a sentence). Used for searches/discovery.

```
Arctic Amplification ratio — Rantanen et al. 2022
```

### Search for an AIDA sentence (search/select, required)

URI of the AIDA published in step 02. Pull from `nanopubs/PUBLISHED.md`.

> _If the AIDA was published via Nanodash (`w3id.org/np/...` namespace), the platform's search may not find it — paste the URI manually._

```
https://w3id.org/sciencelive/np/RAQgvBqSP9q14kmTtzwDXtpoUZCKosM-GvICbQyH1Q7iw
```

### Type of FORRT claim (dropdown, required)

Pick one. See `docs/claim-type-vocabulary.md` for the seven options and how to choose.

- [ ] computational performance
- [ ] scalability
- [ ] data quality
- [ ] data governance
- [x] **descriptive pattern**
- [ ] model performance
- [ ] statistical significance

**Rationale:** The claim asserts an observed empirical relationship — the ratio of Arctic warming rate to global warming rate — derived from observational datasets. The significance tests are the evidence supporting the pattern, not the claim itself.

### Source URI (text input, optional)

Full URL form: `https://doi.org/...` (NOT bare DOI).

```
https://doi.org/10.1038/s43247-022-00498-3
```

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 03.
