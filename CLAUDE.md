# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Jupyter notebooks that demonstrate the pattern **source NetCDF files → VirtualiZarr (virtual references) → Icechunk repository**, applied to one dataset: the NOAA CoastWatch Ocean Heat Content archive, in `coastwatch-heat-content/`. The large science arrays are never copied; Icechunk stores metadata and byte-range references back to the originals. Sibling repos apply the same pattern to other datasets — see "Skills and related repos" below.

## Status & roadmap (last updated 2026-09-17)

**Done:** The CoastWatch OHC archive is built and verified as three separate Icechunk repos on
Source Cooperative at `ocean-icechunks/noaa-ohc/{na,np,sp}`, each with three groups (`daily`,
`14day_v1`, `14day`). It was first built under `fish-pace/coastwatch/ocean-heat/{na,np,sp}`
(PRs #3–#6); the destination re-point landed in PR #8, and the **rebuild at the new location
ran successfully on 2026-08-26** — write credentials re-pointed, `ocean-heat-production-sc.ipynb`
executed end to end, all nine groups committed, and the boundary / variable-set / codec-homogeneity
assertions passed. Anonymous read at `https://data.source.coop/ocean-icechunks/noaa-ohc/{na,np,sp}`
is live. The GitHub repo is `https://github.com/fish-pace/icechunks`.

Coverage as built (2020-04-30 → 2026-08-26), from the executed notebook's outputs:

| Region | `daily` | `14day_v1` | `14day` | Corrupt files dropped |
|---|---|---|---|---|
| na | 1357 | 430 | 507 | 6 (`14day`) |
| np | 1356 | 390 | 513 | 1 (`daily`), 21 (`14day_v1`) |
| sp | 1349 | 411 | 513 | none |

Corrupt source files are dropped by design (`open_region` counts them); the per-region counts
differ because the bad files are in the source archive, not in our handling of it.

**Docs mirror (done 2026-09-17):** all six files are now at `noaa-ohc/` — `README.md`,
`requirements.txt`, `icechunk_utils.py` and the three notebooks — anonymous-readable with correct
content types. Previously only `README.md` and the production notebook had ever been uploaded, so
the other three 404ed while the README claimed they were "included here". The mirror cell's
`files_to_upload` now lists all six, and the published production notebook is the executed copy
(~1.2 MB) rather than the stripped one.

**Next tasks (design open):**
1. **Auto-update pipeline** to append new CoastWatch files as they land. **Undesigned.**
   `write_group` is already idempotent/append-friendly (skips groups that exist), but it does not
   yet append *new time steps* to an existing group — that appending path, plus scheduling/triggering
   when new source files appear, still needs to be figured out. Until it exists the repos stay frozen
   at the last manual run, so they drift behind the source archive by however long since.

## Skills and related repos

- **`virtual-icechunk` skill** — <https://github.com/nmfs-opensci/agent-skills> (`skills/virtual-icechunk/`, checked out locally at `~/agent-skills`). The shared, agent-independent guidance for building, validating, documenting and auditing virtual Icechunk stores. Prefer it over re-deriving practice from this repo's notebooks, and feed genuinely new lessons back into it rather than only into this file.
- **Sibling repos using the same pattern**, each with its own notebooks and destinations — they are *not* in this repo:
  - `~/cefi-icechunks` — NOAA CEFI MOM6 (`https://data.source.coop/eeholmes/cefi/nepacific-icechunk`, groups `daily/regrid/main`, `daily/regrid/aux`; the yearly-file vs. full-period-file split is why it has two groups).
  - `~/pace-icechunks` — PACE ocean colour.
  - `~/gobai-rfrom-icechunks` — GOBAI-O2 / RFROM, the source of the `requirements.txt` style used here.
  - GlobColour/Copernicus CHL — `https://data.source.coop/fish-pace/globcolour/cmems_obs-oc_glo_bgc-plankton_my_l3-multi-4km_P1D`.

## Required packages

Install from `requirements.txt` at the repo root — lower bounds, no lock file, reasoning inline.
It is also mirrored to the destination root, so a reader who finds the repos on Source Cooperative
gets the pins with them.

```
pip install -r requirements.txt
```

Do not use conda; the env will not solve. Two constraints that bite:

- **Python >= 3.12 is required.** Every `icechunk` 2.x release is published
  `requires_python = ">=3.12"`. The JupyterLab image is currently Python 3.11.14, where
  `pip install "icechunk>=2.1"` finds no matching distribution at all (pip sees only the 1.1.x
  line). The 2026-08-26 production run was on 3.12. See `claude/notes/environment.md` before
  trying to work around it.
- **The NetCDF-3 groups need `kerchunk` and `scipy`**, which the notebooks' own inline pip lines
  omit — `NetCDF3Parser` calls `kerchunk.netCDF3.NetCDF3ToZarr`, which subclasses scipy's
  `netcdf_file`. They are satisfied in the image by luck, not by declaration.
  `requirements.txt` lists them.

## Running notebooks

Notebooks run in JupyterLab. Install with `pip install -r requirements.txt` (see above); each
notebook also carries a commented pip line of its own, kept so a notebook downloaded standalone
from Source Cooperative is self-describing — those lines predate `requirements.txt` and omit
`kerchunk`/`scipy`.

The **write** notebooks (`ocean-heat-production-sc.ipynb`, `ocean-heat-test-sc.ipynb`) import shared helpers from `icechunk_utils.py`. It lives at the repo root (the notebooks add `..` to `sys.path`); when a notebook is downloaded standalone from Source Cooperative, `icechunk_utils.py` sits **alongside** it (Jupyter puts the notebook's own directory on `sys.path`, so the co-located copy imports without changes). `ocean-heat-test-local.ipynb` needs no helpers and is fully self-contained.

## Core pattern (used in all notebooks)

1. Create an `ObjectStoreRegistry` pointing to the source data location (S3 or HTTPS).
2. Open each source file virtually with `open_virtual_dataset(..., loadable_variables=[coords], decode_times=True)`.
3. Configure an `icechunk.RepositoryConfig` with a `VirtualChunkContainer` whose `url_prefix` **must have a trailing `/`**.
4. Create or open the Icechunk repo with `icechunk.Repository.create/open(storage, config)`.
5. Write the first file with `vds.vz.to_icechunk(session.store)` and append later files with `append_dim="time"`.
6. Commit with `session.commit("message")` — nothing persists until this call.
7. Reopen for reading: `repo.readonly_session("main").store` → `xr.open_zarr(store, consolidated=False)`.

## Credentials

- **Source Cooperative write credentials come from the `source-coop` CLI, not from a file in this repo.** `icechunk_utils.get_source_credentials()` shells out to `source-coop creds` and then reads the CLI's own cache at `~/.cache/source-coop/credentials/_default.json`. Any `*creds*.json` sitting in the working tree is a leftover from an older workflow; it is gitignored and nothing reads it. These are short-TTL STS tokens — refresh with a browser login:
  ```bash
  /home/jovyan/.cargo/bin/source-coop login --duration 1d --port 8400
  ```
  A full rebuild takes about 2.5 hours, so ask for a duration well beyond that. Note that `open_source_icechunk_repo` stops cleanly only when the token is **already** expired — its `min_minutes_left` argument is currently accepted and ignored, so it will happily start a two-hour write on a token with ten minutes left. `wait_for_fresh_repo` does implement the check.
- Public Icechunk repos on Source Coop can be read anonymously via `icechunk.http_storage(url)`.
- NOAA S3 sources use `skip_signature=True` / `anonymous=True`.
- CoastWatch HTTPS requires a browser-like User-Agent header; the default `python-requests` UA returns 403.

## Notebook inventory (`coastwatch-heat-content/`)

All three notebooks read the same source — NOAA CoastWatch OHC over HTTPS.

| Notebook | Icechunk destination | Mirrored to Source Coop? |
|---|---|---|
| `ocean-heat-test-local.ipynb` | Local filesystem — minimal proof of concept, no credentials needed | yes |
| `ocean-heat-test-sc.ipynb` | Source Coop — minimal proof of concept | **no, git only** |
| `ocean-heat-production-sc.ipynb` | Source Coop (`ocean-icechunks/noaa-ohc/{na,np,sp}`) | yes |

`ocean-heat-test-sc.ipynb` is not published: it needs Source Cooperative **write**
credentials, so it is no use to a reader who just found the stores, and
`ocean-heat-test-local.ipynb` demonstrates the same pattern with none.

It writes to `ocean-icechunks/test-repo/noaa-ohc` — inside the scratch Source Cooperative
repository <https://source.coop/ocean-icechunks/test-repo> — never to the published
`ocean-icechunks/noaa-ohc`. Its
clear cell is guarded twice — a `RUN_CLEAR` flag (a variable, not a `%%script false` magic
that one stray keystroke removes) and a `PROTECTED` set that refuses any prefix holding a
published archive. It carries no saved outputs: it is a template of the steps, and stale
outputs from a half-ordered run were what made the earlier copy misleading.

## Key gotchas

- **`url_prefix` must end with `/`** in `VirtualChunkContainer` — missing the slash silently fails to match virtual chunks.
- **`authorize_virtual_chunk_access`** must be passed at `Repository.open/create` time for virtual chunks outside the Icechunk repo to be readable.
- **Anonymous read URL must include the bucket.** `icechunk.http_storage(url)` needs the full path `https://data.source.coop/{BUCKET}/{prefix}` (e.g. `ocean-icechunks/noaa-ohc/na`), not just the prefix. A wrong/short URL raises `RepositoryNotFoundError: the repository doesn't exist` **deterministically** — it is not a flaky gateway. When an open 404s, verify the full `{bucket}/{prefix}` URL by hand before adding retries. (The S3 write path via `open_source_icechunk_repo` takes `bucket=` separately, so `region_prefix()` intentionally omits it.)
- **`save_config()` is required for anonymous readers.** `Repository.open(storage, config=...)` uses the config only for the current session. To persist the `VirtualChunkContainer` so anonymous reopeners pick it up, call `repo.save_config()` after open/create.
- **Scalar vs. slice indexing on virtual arrays**: prefer `isel(time=slice(0,1), z_l=slice(0,1)).squeeze(drop=True)` over `isel(time=0, z_l=0)` to avoid loading unexpectedly large chunks.
- **Transient CoastWatch read failures are not corruption.** A virtual-chunk read can fail with `StorageError: error fetching virtual reference ... connection closed before message completed`; the same read succeeds on retry with nothing changed (verified 5/5 after one such failure). CoastWatch HTTPS is slow and drops connections. `scrape_nc_urls` retries with backoff on the write side; chunk reads have no retry, so a reader just sees the drop.
- **Writable sessions are single-use**: after `session.commit()`, call `repo.writable_session("main")` again before writing more data.
- **Variables with different file layouts cannot be merged virtually** — they need separate groups. Here that is why `daily`/`14day_v1`/`14day` are three groups rather than one array.
- **Coordinate repair before writing.** Some CoastWatch files carry all-zero lat/lon grids. `build_grid_template` probes the first files for a valid grid and `make_repair` substitutes it as a `preprocess` hook on `open_virtual_mfdataset`; files that still fail to open are dropped and counted. The same hook strips NaN attributes, which Zarr metadata (JSON) cannot represent.

## Manifest splitting (large repos)

For repos with 1000s of time steps, configure manifest splitting to avoid giant manifests at commit time:

```python
config.manifest = icechunk.ManifestConfig(
    splitting=icechunk.ManifestSplittingConfig.from_dict({
        icechunk.ManifestSplitCondition.AnyArray(): {
            icechunk.ManifestSplitDimCondition.DimensionName("time"): 100
        }
    })
)
config.manifest.max_concurrent_manifest_fetches_during_commit = 16
```

## Public Icechunk repos

| Dataset | URL |
|---|---|
| CoastWatch OHC — North Atlantic (2020–present) | `https://data.source.coop/ocean-icechunks/noaa-ohc/na` |
| CoastWatch OHC — North Pacific (2020–present) | `https://data.source.coop/ocean-icechunks/noaa-ohc/np` |
| CoastWatch OHC — South Pacific (2020–present) | `https://data.source.coop/ocean-icechunks/noaa-ohc/sp` |

Each CoastWatch OHC region is a **separate repo** (different lat/lon grids). Every region repo has three groups: `daily` (original `{region}` product, NetCDF-3), `14day_v1` (`{region}14` NetCDF-3 big-endian), `14day` (`{region}14` HDF5 little-endian). The `14day_v1`/`14day` split is at 2025 day 084/085; the `daily`/`14day` split is a variable-set/product-generation difference.

The `noaa-ohc/` **root** (alongside the `na/`/`np/`/`sp/` repo subfolders) also holds the human-facing docs, mirrored from git: `README.md`, `requirements.txt`, `icechunk_utils.py`, `ocean-heat-production-sc.ipynb` and `ocean-heat-test-local.ipynb` — five files, **not** `ocean-heat-test-sc.ipynb` (see the inventory above). These are reference/reproducibility copies; keep them in sync when the git versions change. The last cell of `ocean-heat-production-sc.ipynb` uploads the set; `requirements.txt` and `icechunk_utils.py` come from the repo root via `../`, flattened onto the destination root by `path.name`.
