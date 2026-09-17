# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Jupyter notebooks that publish NOAA ocean datasets as Icechunk repositories on Source Cooperative. Two datasets, built two different ways:

- `coastwatch-heat-content/` — **virtual**: the pattern **source NetCDF files → VirtualiZarr (virtual references) → Icechunk repository**, applied to the NOAA CoastWatch Ocean Heat Content archive. The large science arrays are never copied; Icechunk stores metadata and byte-range references back to the originals.
- `gobai-o2-monthly/` — **materialized**: GOBAI-O2 v2.3 monthly from NCEI, written as real Zarr v3 chunks with `Dataset.to_zarr`. Virtualizing would buy nothing there — the source is a single 12 GB contiguous, uncompressed NetCDF with no chunk boundaries to reference. Keep the two straight: the virtual gotchas below (virtual chunk containers, `url_prefix`, `authorize_virtual_chunk_access`) do not apply to it at all.

Sibling repos apply the virtual pattern to other datasets — see "Skills and related repos" below.

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

**GOBAI-O2 v2.3 monthly: done and static.** Materialized store at `fish-pace/gobai-o2/monthly`
(`https://data.source.coop/fish-pace/gobai-o2/monthly`), built 2026-08-06 — snapshot
`8DKFSNN3G386BXJS8X6G`, tag `v2.3`, 12,858 objects, 5.59 GB, chunks `(14, 2, 73, 120)`. Snapshot
`3A41NX29VSPEXA94ES9G` (2026-09-17) is a metadata-only fix of the `license` attribute to CC0 1.0.
GOBAI-O2 v2.3 is a finished archive version, not a growing feed, so there is **no update pipeline to
write** — a later GOBAI version would be a new store. The notebook, README and `requirements.txt` are
mirrored at the `gobai-o2/` root. The notebook arrived here on 2026-09-17 from
`nmfs-opensci/gobai-rfrom-icechunks`, where it did not belong; its first commit in this repo is the
unmodified original, so the 2026-08-06 build outputs are in the history.

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

Each pipeline declares its own floors — lower bounds, no lock file, reasoning inline. Both are
mirrored to their destination roots, so a reader who finds the stores on Source Cooperative gets the
pins with them.

```
pip install -r requirements.txt                    # CoastWatch (virtual)
pip install -r gobai-o2-monthly/requirements.txt   # GOBAI-O2 monthly (materialized)
```

They are deliberately separate: the GOBAI-O2 notebook uses no virtualizarr, kerchunk, obstore or
scipy, and adds netCDF4 (the only engine that reads the `#mode=bytes` URL form).

Do not use conda; the env will not solve. Two constraints that bite:

- **Python >= 3.12 is required.** Every `icechunk` 2.x release is published
  `requires_python = ">=3.12"`. The JupyterLab image is currently Python 3.11.14, where
  `pip install "icechunk>=2.1"` finds no matching distribution at all (pip sees only the 1.1.x
  line). A 3.12 venv built from `/srv/conda/bin/python3.12` does work and has been used to run
  the notebooks — recipe and traps in `claude/notes/environment.md`.
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
  source-coop login --duration 1d --port 8400
  ```
  The CLI lives at `~/.cargo/bin/source-coop` on this hub and is not on `$PATH` by default;
  `icechunk_utils` finds it via `$SOURCE_COOP_CLI`, then `$PATH`, then `~/.cargo/bin`. The
  login flow is served on the given port — reach it through the hub proxy at
  `<hub-url>/user/<username>/proxy/8400/`.
  A full rebuild takes about 2.5 hours, so ask for a duration well beyond that.
  `open_source_icechunk_repo` enforces `min_minutes_left` (default 15) and stops cleanly
  rather than starting a write that cannot finish; `wait_for_fresh_repo` additionally
  prompts for a refresh, but needs an interactive session.
- Public Icechunk repos on Source Coop can be read anonymously via `icechunk.http_storage(url)`.
- NOAA S3 sources use `skip_signature=True` / `anonymous=True`.
- CoastWatch HTTPS requires a browser-like User-Agent header; the default `python-requests` UA returns 403.

## Notebook inventory (`gobai-o2-monthly/`)

One notebook, `gobai-o2-monthly-icechunk-sc.ipynb`, mirrored to the `gobai-o2/` root along with its
README and `requirements.txt`. It is guarded by two flags, both `False` in the committed copy:
`RUN_WRITE` (open credentials and rebuild the store) and `RUN_MIRROR` (upload the docs). With both
off it runs end to end with no credentials and writes nothing — opens the source, builds the
metadata and encoding, skips the write, then validates the published store against the source. The
committed outputs are from exactly that run (2026-09-17, 57 s, clean Python 3.12 venv).

## Notebook inventory (`coastwatch-heat-content/`)

All three notebooks read the same source — NOAA CoastWatch OHC over HTTPS.

| Notebook | Icechunk destination | Mirrored to Source Coop? |
|---|---|---|
| `ocean-heat-test-local.ipynb` | Local filesystem — minimal proof of concept, no credentials needed | yes |
| `ocean-heat-test-sc.ipynb` | Source Coop — minimal proof of concept | **no, git only** |
| `ocean-heat-production-sc.ipynb` | Source Coop (`ocean-icechunks/noaa-ohc/{na,np,sp}`) | yes |

`ocean-heat-test-sc.ipynb` stays in git only: it needs write credentials, so it is no use
to a reader who just found the stores, and `ocean-heat-test-local.ipynb` shows the same
steps with none. It writes to `ocean-icechunks/test-repo/noaa-ohc` (the scratch repo at
<https://source.coop/ocean-icechunks/test-repo>), never to the published prefix, and its
clear cell is guarded by both a `RUN_CLEAR` flag and a `PROTECTED` set that refuses any
prefix holding a published archive. It carries no saved outputs by design — it is a
template of the steps.

## Key gotchas (GOBAI-O2 / materialized)

- **NCEI's landing-page download button is broken** — `/archive/accession/download/0259304` 302-loops.
  The archive filesystem path works and honours range requests:
  `https://www.ncei.noaa.gov/data/oceans/archive/arc0207/0259304/5.5/data/0-data/GOBAI-O2-v2.3.nc`
  (12,207,313,813 bytes). Do not conclude NCEI is down from the button alone.
- **`engine="netcdf4"` plus a `#mode=bytes` URL suffix streams the source**, no download. h5netcdf
  cannot do this. Opening takes ~6 s, one `(lat, lon)` plane ~1 s.
- **Never sample a contiguous, uncompressed source through dask chunks.** Comparing 81 scattered
  points with the source opened at `chunks=(14, 2, 73, 120)` took **11m41s**, because each point
  drags in a whole chunk and a chunk is thousands of strided range requests. Re-opening the source
  with `chunks=None` for the sample made the same notebook run take **57 s**.
- **The `license` attribute was wrong in the first build** (CC BY 4.0). GOBAI-O2 ships CC0 1.0;
  NCEI distributes the text as `GOBAI-O2-v2.3-license.txt` beside the data. Fixed by opening a
  writable session, `zarr.open_group(...).attrs.put(...)` and committing — a metadata-only commit
  rewrites no chunks and takes seconds.
- **Longitudes run 20.5 → 379.5**, not 0–360. That is the source grid; it is kept as is.

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
| GOBAI-O2 v2.3 monthly (2004–2024), materialized | `https://data.source.coop/fish-pace/gobai-o2/monthly` |

Each CoastWatch OHC region is a **separate repo** (different lat/lon grids). Every region repo has three groups: `daily` (original `{region}` product, NetCDF-3), `14day_v1` (`{region}14` NetCDF-3 big-endian), `14day` (`{region}14` HDF5 little-endian). The `14day_v1`/`14day` split is at 2025 day 084/085; the `daily`/`14day` split is a variable-set/product-generation difference.

The `noaa-ohc/` **root** (alongside the `na/`/`np/`/`sp/` repo subfolders) also holds the human-facing docs, mirrored from git: `README.md`, `requirements.txt`, `icechunk_utils.py`, `ocean-heat-production-sc.ipynb` and `ocean-heat-test-local.ipynb` — five files, **not** `ocean-heat-test-sc.ipynb` (see the inventory above). These are reference/reproducibility copies; keep them in sync when the git versions change. The last cell of `ocean-heat-production-sc.ipynb` uploads the set; `requirements.txt` and `icechunk_utils.py` come from the repo root via `../`, flattened onto the destination root by `path.name`.
