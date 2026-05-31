# forrt-replication

> **The Arctic has warmed nearly four times faster than the globe since 1979** — replication study.
>
> Reference paper: [10.1038/s43247-022-00498-3](https://doi.org/10.1038/s43247-022-00498-3)

This repository is a self-contained replication of the headline claim from the reference paper above. It produces:

- A reproducible computational pipeline (Snakefile + notebooks).
- A FORRT-tagged nanopublication chain on the [Science Live platform](https://platform.sciencelive4all.org), documenting the claim, the replication design, and the outcome with full provenance.
- A Zenodo-archived release (source + container image) with a citable DOI.

## Quick start

```bash
git clone https://github.com/j34ni/forrt-replication.git
cd forrt-replication
pixi install
pixi run snakemake --cores 1
```

Or with Docker:

```bash
docker run --rm ghcr.io/j34ni/forrt-replication:latest
```

## Structure

- `paper/` — the source paper PDF (drop yours in there).
- `notebooks/` — jupytext `.py` notebooks that drive the pipeline.
- `data/` — downloaded by `notebooks/01_data_download.py`, never committed.
- `nanopubs/` — drafts of the FORRT chain field-by-field, plus the published-URI registry.
- `docs/` — operating manuals (FORRT form fields, chain decision tree, claim-type vocabulary).
- `figures/` — curated figures used in the Jupyter Book.

## Nanopublication chain

The full chain is registered in [`nanopubs/PUBLISHED.md`](nanopubs/PUBLISHED.md). Each step is browsable via the Science Live viewer:

| Step | Template | URI |
|---|---|---|
| 01 | Quote-with-comment | [RACDO0UW…](https://platform.sciencelive4all.org/np/?uri=https://w3id.org/sciencelive/np/RACDO0UWMNmksxCsB-cXrci0udSs3d_1qEVP9l7zVJmfE) |
| 02 | AIDA Sentence | [RAQgvBqS…](https://platform.sciencelive4all.org/np/?uri=https://w3id.org/sciencelive/np/RAQgvBqSP9q14kmTtzwDXtpoUZCKosM-GvICbQyH1Q7iw) |
| 03 | FORRT Claim | [RA7QUD7D…](https://platform.sciencelive4all.org/np/?uri=https://w3id.org/sciencelive/np/RA7QUD7DRYY2CJOHXFkgBVKQ9Oq8tkykONjLFZe7LNGVs) |
| 04 | FORRT Replication Study | [RApBTOFI…](https://platform.sciencelive4all.org/np/?uri=https://w3id.org/sciencelive/np/RApBTOFIsvkcFttckgdZy-qF4FWE2dqdRwUColauzPGrc) |
| 05 | FORRT Replication Outcome | [RAZYUn5K…](https://platform.sciencelive4all.org/np/?uri=https://w3id.org/sciencelive/np/RAZYUn5KQru5hr0vo3dwhK0-tQlOMlta4uv-xnGvH597c) |
| 06 | CiTO Citation | [RA2WH2Tp…](https://platform.sciencelive4all.org/np/?uri=https://w3id.org/np/RA2WH2Tp-G9dVIxzhfHCnAm1RgRjYrnKRkDN_DVz5ktXw) |

## Citation

If you use this work, please cite both:

- This software: [`CITATION.cff`](CITATION.cff) → DOI [{{ZENODO_DOI}}]({{ZENODO_DOI}}).
- The original paper: [10.1038/s43247-022-00498-3](https://doi.org/10.1038/s43247-022-00498-3).
