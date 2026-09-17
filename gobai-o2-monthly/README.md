# GOBAI-O2 v2.3 (monthly) — Icechunk

**[🌐 View data in browser](https://data.source.coop/fish-pace/gobai-o2/viewer/index.html#icechunk+https://data.source.coop/fish-pace/gobai-o2/monthly::varname=oxy)** · **[💻 Data access (code)](#how-to-open-it)** · **[📦 Data access (NCEI)](https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.nodc:0259304)**

An [Icechunk](https://icechunk.io) store of the complete **GOBAI-O2 v2.3** monthly
dataset: global gridded ocean-interior dissolved oxygen, its uncertainty, temperature and
salinity, **2004-01 through 2024-12**, on a 1° × 1° × 58-level pressure grid.

```
https://data.source.coop/fish-pace/gobai-o2/monthly
```

Unlike the other stores in this repository, this one is **materialized**: it holds real
Zarr v3 chunks, not byte-range references. Nothing is fetched from NCEI at read time and
the store is self-contained. The source is a single 12 GB contiguous, uncompressed NetCDF
file, which offers no chunk boundaries worth referencing; rechunked and Zstd-compressed it
is 5.59 GB in 12,858 objects.

The dataset is complete and static — GOBAI-O2 v2.3 is a finished archive version, not a
growing feed — so this store needs no update pipeline. A later GOBAI-O2 version would be a
new store.

## View it in a browser

No install, no account, no download — the viewer streams chunks straight from the store:

| Field | Viewer |
|---|---|
| Dissolved oxygen | [Open `oxy` in the viewer](https://data.source.coop/fish-pace/gobai-o2/viewer/index.html#icechunk+https://data.source.coop/fish-pace/gobai-o2/monthly::varname=oxy) |
| Total uncertainty | [Open `uncer` in the viewer](https://data.source.coop/fish-pace/gobai-o2/viewer/index.html#icechunk+https://data.source.coop/fish-pace/gobai-o2/monthly::varname=uncer) |
| Temperature | [Open `temp` in the viewer](https://data.source.coop/fish-pace/gobai-o2/viewer/index.html#icechunk+https://data.source.coop/fish-pace/gobai-o2/monthly::varname=temp) |
| Salinity | [Open `sal` in the viewer](https://data.source.coop/fish-pace/gobai-o2/viewer/index.html#icechunk+https://data.source.coop/fish-pace/gobai-o2/monthly::varname=sal) |

The viewer is [gridlook](https://github.com/eeholmes/gridlook), a WebGL globe for
cloud-hosted Zarr and Icechunk stores, published alongside the data at
[`gobai-o2/viewer/`](https://data.source.coop/fish-pace/gobai-o2/viewer/index.html). The store to open is in the URL *fragment* after `#`, so any
store can be swapped into the same link — nothing about the viewer is specific to this
dataset. Give it a moment on first load: it fetches the store's metadata before drawing.

It is a browser rendering a multi-gigabyte store over the network, so treat it as a look,
not an analysis. For anything quantitative use the code path below.

## How to open it

Needs `icechunk >= 2.1` and `xarray`. No credentials, no account, and — because the chunks
are materialized — no virtual-chunk authorization step.

```python
import icechunk
import xarray as xr

url = "https://data.source.coop/fish-pace/gobai-o2/monthly"
repo = icechunk.Repository.open(icechunk.http_storage(url))
store = repo.readonly_session("main").store

# chunks={} gives lazy, dask-backed arrays. The full dataset is 12 GB uncompressed,
# so do not load it whole.
ds = xr.open_zarr(store, consolidated=False, chunks={})

print(ds)
print(ds.oxy.isel(time=0, pres=0).mean().compute())      # surface map, Jan 2004
print(ds.oxy.sel(lat=0, lon=180, method="nearest").isel(pres=0))  # equatorial time series
```

The snapshot that built the store is also tagged, so `readonly_session(tag="v2.3")` pins
you to it regardless of later commits.

**Longitudes run 20.5 → 379.5**, not 0 → 360 or −180 → 180: the grid starts at 20.5°E and
continues past the dateline into a second lap. This comes from the source file and is kept
as is. Selecting the Pacific near 200 is therefore `sel(lon=200)`, and a plot of a full
map is centred on the Atlantic. To get a conventional axis:

```python
ds = ds.assign_coords(lon=(ds.lon - 360) % 360).sortby("lon")   # 0 → 360
```

Land and below-bottom cells are `NaN` (about 39 % of the surface layer). There is no
`_FillValue` or `missing_value` to unmask — the source declares none, and float NaN
survives the round trip.

## About the data

GOBAI-O2 (Gridded Ocean Biogeochemistry from Artificial Intelligence — Oxygen) reconstructs
ocean interior dissolved oxygen by training machine-learning models on shipboard bottle and
profiling-float oxygen observations, then applying them to temperature and salinity fields
from the Roemmich and Gilson (2009) Argo climatology. The method is described in
[Sharp et al. (2023)](https://doi.org/10.5194/essd-15-4481-2023).

- **Grid:** 1° latitude × 1° longitude, 58 pressure levels from 2.5 to 1975 dbar
- **Extent:** lat −64.5 → 79.5, lon 20.5 → 379.5, monthly mid-month time stamps
  (2004-01-15 → 2024-12-15, 252 steps)
- **Conventions:** CF-1.12, ACDD-1.3 (added here; see "How this was built")
- **Product page:** <https://www.pmel.noaa.gov/gobai/>
- **Archive:** NCEI accession
  [0259304](https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.nodc:0259304),
  DOI [10.25921/z72m-yz67](https://doi.org/10.25921/z72m-yz67)

### Variables

| Variable | Long name | Units | CF `standard_name` |
|---|---|---|---|
| `oxy` | dissolved molecular oxygen concentration | µmol kg⁻¹ | `moles_of_oxygen_per_unit_mass_in_sea_water` |
| `uncer` | total uncertainty in `oxy` | µmol kg⁻¹ | — (no exact CF name; linked to `oxy` as `ancillary_variables`) |
| `temp` | sea water temperature | °C | `sea_water_temperature` |
| `sal` | sea water practical salinity | 1 | `sea_water_practical_salinity` |

All four are `float32` on `(time, pres, lat, lon)`. `temp` and `sal` are the Roemmich and
Gilson (2009) fields the oxygen reconstruction was driven with, carried along for
convenience — they are not an independent product.

### Chunking

Chunks are `(time: 14, pres: 2, lat: 73, lon: 120)` — 0.98 MB of float32 each, Zstd
compressed. That is a deliberate compromise between the two access patterns, neither of
which it favours: a global map at one time and pressure touches 6 chunks, a 252-month time
series at one point and depth touches 18, and a full-depth profile at one time touches 29.
Measured anonymously over the public endpoint, those three reads take about 0.4 s, 0.8 s
and 1.3 s.

## How this was built

The viewer is published by `publish_viewer.py` in the
[GitHub repository](https://github.com/fish-pace/icechunks)
(`python publish_viewer.py --product gobai-o2 --build ~/gridlook`); it is a plain static
build of gridlook, and holds no data of its own.

The notebook that built it sits next to this README:
**`gobai-o2-monthly-icechunk-sc.ipynb`** (also in the GitHub repository
<https://github.com/fish-pace/icechunks>, directory `gobai-o2-monthly/`). It downloads or
streams the NCEI file, adds CF and ACDD metadata, rechunks, writes with
`Dataset.to_zarr`, and validates the published store against the source.

It runs end to end **without credentials and without writing anything**: `RUN_WRITE`
defaults to `False`, so it opens the source, builds the same metadata and encoding, skips
the write, and validates. Set `RUN_WRITE = True` (with Source Cooperative write
credentials) to rebuild. `requirements.txt` beside it lists the package floors; Python 3.12
or newer is required, because `icechunk` 2.x is published `requires_python = ">=3.12"`.

The source file is one 12 GB NetCDF at

```
https://www.ncei.noaa.gov/data/oceans/archive/arc0207/0259304/5.5/data/0-data/GOBAI-O2-v2.3.nc
```

(accession 0259304, archive version 5.5, 12,207,313,813 bytes). NCEI's landing-page
download button currently redirects in a loop, but that archive path serves the file
directly and honours HTTP range requests, so the notebook can read it without downloading
it — `engine="netcdf4"` plus a `#mode=bytes` URL suffix. Downloading it first is still much
faster for a full rebuild, because the source is contiguous and uncompressed and the write
reads it in a strided pattern.

### What was changed from the source

**Metadata only. No data value was altered.** The source file carries per-variable
descriptions but no global attributes at all, and free-text units (`"micromoles per
kilogram"`, `"degrees Celcius"`, `"N/A"` for salinity). The build added `Conventions`,
`title`, `summary`, `source`, `history`, creator and citation fields, the DOI, the license
and `product_version`; CF `standard_name`, `units` and axis attributes on the coordinates;
CF standard names and udunits-style units on the variables; and `ancillary_variables`
linking `uncer` to `oxy`.

### Provenance

| When | What |
|---|---|
| 2026-08-06 | Built and committed, snapshot `8DKFSNN3G386BXJS8X6G`, tagged `v2.3` (icechunk 2.1.2) |
| 2026-09-17 | Metadata-only commit `3A41NX29VSPEXA94ES9G`: corrected `license` from CC BY 4.0 to CC0 1.0, which is what NCEI distributes with the source. No chunk was rewritten |

Both are in the repository's `ancestry()`, and every code block on this page was executed
against the live store before it was published.

## Reuse and citation

**Code.** The notebook and helpers are released under
[Apache-2.0](https://github.com/fish-pace/icechunks/blob/main/LICENSE) and are free to use,
copy, adapt and redistribute, commercially or not — no attribution required.

**Data.** The data is not ours. GOBAI-O2 is released by its authors under
[CC0 1.0](https://www.ncei.noaa.gov/data/oceans/archive/arc0207/0259304/5.5/data/0-data/GOBAI-O2-v2.3-license.txt),
which waives all copyright and imposes no legal obligation to cite. Scholarly practice
still asks that you do:

> Sharp, J. D., Fassbender, A. J., Carter, B. R., Johnson, G. C., Schultz, C., & Dunne,
> J. P. (2022). GOBAI-O2: A Global Gridded Monthly Dataset of Ocean Interior Dissolved
> Oxygen Concentrations Based on Shipboard and Autonomous Observations (NCEI Accession
> 0259304). NOAA National Centers for Environmental Information.
> <https://doi.org/10.25921/z72m-yz67>

and cite the method paper:

> Sharp, J. D., Fassbender, A. J., Carter, B. R., Johnson, G. C., Schultz, C., & Dunne,
> J. P. (2023). GOBAI-O2: temporally and spatially resolved fields of ocean interior
> dissolved oxygen over nearly 2 decades. *Earth System Science Data*, 15, 4481–4518.
> <https://doi.org/10.5194/essd-15-4481-2023>

## Credits

- **Data:** Jonathan D. Sharp, Andrea J. Fassbender, Brendan R. Carter, Gregory C. Johnson,
  Cristina Schultz and John P. Dunne — NOAA Pacific Marine Environmental Laboratory,
  CICOES/University of Washington, and NOAA GFDL. Archived by NOAA NCEI.
- **Temperature and salinity fields:** Roemmich, D., & Gilson, J. (2009), the Scripps
  Argo climatology, <https://sio-argo.ucsd.edu/RG_Climatology.html>.
- **Icechunk packaging:** built with [Icechunk](https://icechunk.io) and
  [Xarray](https://xarray.dev), hosted on
  [Source Cooperative](https://source.coop/fish-pace/gobai-o2).
