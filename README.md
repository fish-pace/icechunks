# icechunks — Icechunk stores of NOAA ocean data

Jupyter notebooks that publish NOAA ocean datasets as
**[Icechunk](https://icechunk.io) repositories** on
[Source Cooperative](https://source.coop), anonymously readable with `xarray`.

Two datasets, built two different ways:

- **NOAA CoastWatch Ocean Heat Content**, in `coastwatch-heat-content/` — **virtual
  references**. The source NetCDF/HDF5 files stay at CoastWatch and Icechunk stores only
  Zarr metadata plus byte-range pointers back to them, via
  [VirtualiZarr](https://virtualizarr.readthedocs.io). Nothing copies the science arrays,
  so a store of a multi-terabyte archive is megabytes of metadata.
- **GOBAI-O2 v2.3 monthly**, in `gobai-o2-monthly/` — **materialized**. Real Zarr v3
  chunks written with `Dataset.to_zarr`, self-contained and independent of the source.
  Its source is one 12 GB contiguous, uncompressed NetCDF at NCEI with no chunk
  boundaries worth referencing, which is exactly the case where virtualizing buys nothing.

## The published stores

Public, anonymously readable, no account needed:

| Dataset | Icechunk repository | Kind |
|---|---|---|
| CoastWatch OHC — North Atlantic | `https://data.source.coop/ocean-icechunks/noaa-ohc/na` | virtual |
| CoastWatch OHC — North Pacific | `https://data.source.coop/ocean-icechunks/noaa-ohc/np` | virtual |
| CoastWatch OHC — South Pacific | `https://data.source.coop/ocean-icechunks/noaa-ohc/sp` | virtual |
| GOBAI-O2 v2.3 monthly, 2004–2024 | `https://data.source.coop/fish-pace/gobai-o2/monthly` | materialized |

GOBAI-O2 also has a **browser viewer** — no install, no account:
[open `oxy` on the globe](https://data.source.coop/fish-pace/gobai-o2/viewer/index.html#icechunk+https://data.source.coop/fish-pace/gobai-o2/monthly::varname=oxy). It is
[gridlook](https://github.com/eeholmes/gridlook), published beside the data by
`publish_viewer.py`; the store to open lives in the URL fragment, so one build serves any
store.

Each CoastWatch region is a separate repository — the three use different lat/lon grids
and cannot share a virtual array. Each holds three groups (`daily`, `14day_v1`, `14day`)
covering different generations and encodings of the product.

Full documentation of each dataset, and how to read it, is in the product README —
**[`coastwatch-heat-content/README.md`](coastwatch-heat-content/README.md)** and
**[`gobai-o2-monthly/README.md`](gobai-o2-monthly/README.md)** — each of which is also
published alongside its store.

## Quick start

```python
import icechunk
import xarray as xr

url = "https://data.source.coop/ocean-icechunks/noaa-ohc/na"
repo = icechunk.Repository.open(icechunk.http_storage(url))

# The arrays live at CoastWatch, outside the store, so authorize the virtual
# chunk container at open time — this is the one non-standard step.
auth = {p: icechunk.credentials.HttpAccess for p in repo.config.virtual_chunk_containers or []}
store = repo.reopen(authorize_virtual_chunk_access=auth).readonly_session("main").store

ds = xr.open_zarr(store, group="14day", consolidated=False, chunks={})
print(ds)
```

A materialized store needs no such authorization — the chunks are inside it:

```python
url = "https://data.source.coop/fish-pace/gobai-o2/monthly"
repo = icechunk.Repository.open(icechunk.http_storage(url))
ds = xr.open_zarr(repo.readonly_session("main").store, consolidated=False, chunks={})
print(ds)
```

## Repository layout

```text
coastwatch-heat-content/
  README.md                        data documentation, mirrored to the stores
  ocean-heat-test-local.ipynb      minimal proof of concept, writes locally, no credentials
  ocean-heat-test-sc.ipynb         minimal proof of concept, writes to Source Cooperative
  ocean-heat-production-sc.ipynb   the full pipeline that built all three region stores
gobai-o2-monthly/
  README.md                        data documentation, mirrored to the store
  gobai-o2-monthly-icechunk-sc.ipynb   the pipeline that built the GOBAI-O2 store
  requirements.txt                 dependency floors for that notebook
icechunk_utils.py                  Source Cooperative credential and repo helpers
publish_viewer.py                  builds gridlook and publishes it beside a store
requirements.txt                   dependency floors for the CoastWatch notebooks
claude/                            working notes for AI coding agents
```

## Installing

Each pipeline declares its own floors, because they need different things — the
CoastWatch notebooks pull in VirtualiZarr, kerchunk and obstore, and the GOBAI-O2
notebook needs none of them:

```bash
pip install -r requirements.txt                    # CoastWatch (virtual)
pip install -r gobai-o2-monthly/requirements.txt   # GOBAI-O2 monthly (materialized)
```

**Python 3.12 or newer is required** — every `icechunk` 2.x release is published
`requires_python = ">=3.12"`. Use pip, not conda; the environment will not solve.

Reading the published stores needs only `icechunk` and `xarray`. Re-running the CoastWatch
write notebooks additionally needs Source Cooperative write credentials, so for most
readers they are read-along references. `gobai-o2-monthly-icechunk-sc.ipynb` is the
exception: it runs end to end with no credentials and writes nothing unless you set
`RUN_WRITE = True`.

## Related

- **[`virtual-icechunk` skill](https://github.com/nmfs-opensci/agent-skills)** — shared
  guidance for building, validating and auditing virtual Icechunk stores.
- Sibling repositories apply the same pattern to NOAA CEFI, PACE, RFROM / GOBAI HR and
  Copernicus GlobColour data. In particular
  [`nmfs-opensci/gobai-rfrom-icechunks`](https://github.com/nmfs-opensci/gobai-rfrom-icechunks)
  publishes RFROM and **GOBAI HR** — a different, weekly, higher-resolution GOBAI product
  on NOAA NODD, not to be confused with the GOBAI-O2 v2.3 monthly store here.

## Reuse and citation

**Code.** Released under [Apache License 2.0](LICENSE). Use it, copy it, adapt it, and
redistribute it, commercially or not — you do not need to credit us, cite us, or ask
permission. (Apache-2.0 asks that you keep the license and copyright notice with copies you
redistribute; we ask for nothing beyond that.)

**Data.** None of the data is ours, and each dataset carries its own terms — follow the
source, not this repository:

- **CoastWatch OHC** — the stores contain no science arrays at all, only references to
  files hosted by NOAA CoastWatch. The Satellite Ocean Heat Content Suite is produced by
  USDOC/NOAA/NESDIS/OSPO with the University of Miami / Rosenstiel School. See the
  [product page](http://www.ospo.noaa.gov/Products/ocean/ocean_heat.html) and the
  [Credits](coastwatch-heat-content/README.md#credits) section of its documentation.
- **GOBAI-O2 v2.3** — released by its authors under CC0 1.0, so no legal obligation to
  cite; scholarly practice still asks that you do. Citations are in
  [`gobai-o2-monthly/README.md`](gobai-o2-monthly/README.md#reuse-and-citation).
