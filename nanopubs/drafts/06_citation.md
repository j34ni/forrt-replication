# 06 — CiTO Citation

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.

**Description:** *"Declare citations between papers or other works, using Citation Typing Ontology"*

## Field-by-field draft

### Identifier for the citing creative work (text input, required)

URI of the Outcome published in step 05. Pull from `nanopubs/PUBLISHED.md`.

```
https://w3id.org/sciencelive/np/RAZYUn5KQru5hr0vo3dwhK0-tQlOMlta4uv-xnGvH597c
```

### List citations (repeatable group, required ≥1)

#### Citation 1 — back to the original paper

##### Citation Type (dropdown)

Choose based on the Outcome's validation status:

- Validated → `confirms`
- PartiallySupported → `qualifies`
- Contradicted → `disputes`

For question-rooted chains where there is no original paper to confirm/dispute, use `usesMethodIn` or `citesAsAuthority` for the methodology paper(s).

> **Note:** `replicates` is NOT in the Science Live dropdown (despite existing in upstream CiTO). When citing a notebook/tutorial that was directly reused, use **`credits`** instead.

```
qualifies
```

**Rationale:** Outcome is PartiallySupported — the direction and qualitative magnitude of the claim are confirmed (Arctic warming substantially above 3×), but the extended-period AA ratio (~3.34) is lower than the paper's reported 3.8, qualifying rather than fully confirming the "nearly four times" framing.

##### DOI or other URL of the cited work (text input)

```
https://doi.org/10.1038/s43247-022-00498-3
```

#### Additional citations (optional)

If the Outcome cites methods papers, related replications, or upstream tools, add them here.

- _Type: `usesMethodIn` → URL: `https://doi.org/10.24381/cds.f17050d7` (ERA5)_

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 06.

This completes the six-step FORRT chain. Optional next layers:

- **Research Software** (`drafts/07_research_software.md`) — if the repo *produces* a reusable software artefact.
- **Research Synthesis** (`drafts/08_synthesis.md`) — if this chain is one of several testing facets of a shared property.
