# icechunks — virtual Icechunk stores for NOAA satellite data

Jupyter notebooks that build **[Icechunk](https://icechunk.io) repositories of virtual
references**: the source NetCDF/HDF5 files stay where they are, and Icechunk stores only
Zarr metadata plus byte-range pointers back to the originals. Nothing copies the science
arrays, so a store of a multi-terabyte archive is megabytes of metadata and reads stream
straight from the data provider.

The pattern is **source NetCDF → [VirtualiZarr](https://virtualizarr.readthedocs.io)
→ Icechunk**. This repository applies it to one dataset: the NOAA CoastWatch **Ocean Heat
Content (OHC)** archive, 2020 to present, for three regions.

## The published stores

Public, anonymously readable, no account needed:

| Region | Icechunk repository |
|---|---|
| North Atlantic | `https://data.source.coop/ocean-icechunks/noaa-ohc/na` |
| North Pacific | `https://data.source.coop/ocean-icechunks/noaa-ohc/np` |
| South Pacific | `https://data.source.coop/ocean-icechunks/noaa-ohc/sp` |

Each region is a separate repository — the three use different lat/lon grids and cannot
share a virtual array. Each holds three groups (`daily`, `14day_v1`, `14day`) covering
different generations and encodings of the product.

Full documentation of the data, the groups, and how to read them is in
**[`coastwatch-heat-content/README.md`](coastwatch-heat-content/README.md)**, which is also
published alongside the stores.

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

## Repository layout

```text
coastwatch-heat-content/
  README.md                        data documentation, mirrored to the stores
  ocean-heat-test-local.ipynb      minimal proof of concept, writes locally, no credentials
  ocean-heat-test-sc.ipynb         minimal proof of concept, writes to Source Cooperative
  ocean-heat-production-sc.ipynb   the full pipeline that built all three region stores
icechunk_utils.py                  Source Cooperative credential and repo helpers
requirements.txt                   dependency floors
claude/                            working notes for AI coding agents
```

## Installing

```bash
pip install -r requirements.txt
```

**Python 3.12 or newer is required** — every `icechunk` 2.x release is published
`requires_python = ">=3.12"`. Use pip, not conda; the environment will not solve.

Reading the published stores needs only `icechunk` and `xarray`. Re-running the write
notebooks additionally needs Source Cooperative write credentials, so for most readers
they are read-along references rather than something to execute.

## Related

- **[`virtual-icechunk` skill](https://github.com/nmfs-opensci/agent-skills)** — shared
  guidance for building, validating and auditing virtual Icechunk stores.
- Sibling repositories apply the same pattern to NOAA CEFI, PACE, GOBAI-O2/RFROM and
  Copernicus GlobColour data.

## Reuse and citation

**Code.** Released under [Apache License 2.0](LICENSE). Use it, copy it, adapt it, and
redistribute it, commercially or not — you do not need to credit us, cite us, or ask
permission. (Apache-2.0 asks that you keep the license and copyright notice with copies you
redistribute; we ask for nothing beyond that.)

**Data.** None of the data is ours. These stores contain no science arrays at all — only
references to files hosted by NOAA CoastWatch. The Satellite Ocean Heat Content Suite is
produced by USDOC/NOAA/NESDIS/OSPO with the University of Miami / Rosenstiel School. For
data use and citation, follow the source: the
[product page](http://www.ospo.noaa.gov/Products/ocean/ocean_heat.html), and the
[Credits](coastwatch-heat-content/README.md#credits) section of the data documentation.
