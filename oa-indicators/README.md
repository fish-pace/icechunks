# Ocean acidification indicators, North American margins — Icechunk

**[🌐 View data in browser](https://data.source.coop/ocean-icechunks/oa-indicators/viewer/index.html#icechunk+https://data.source.coop/ocean-icechunks/oa-indicators/climatology::varname=OmegaA_an::px=0::py=0::alt=95910936::lat=48::lon=-110::dimIndices_depth=0)** · **[💻 Data access (code)](#how-to-open-it)** · **[📦 Data access (NCEI)](https://www.ncei.noaa.gov/data/oceans/ncei/ocads/metadata/0270962.html)** · **[📄 DOI 10.25921/g8pb-zy76](https://doi.org/10.25921/g8pb-zy76)**

An [Icechunk](https://icechunk.io) store of the **NCEI coastal climatology of ocean
acidification indicators on the North American ocean margins** — twelve indicators at 14
standard depth levels from the surface to 500 m, on a 1° × 1° grid, gridded from
observations collected 2003-12-06 to 2018-11-22 and adjusted to the year 2010.

```
https://data.source.coop/ocean-icechunks/oa-indicators/climatology
```

This store is **virtual**: it holds Zarr metadata and byte-range references, and no array
data at all. The whole store is **84 objects and 35 kB**, pointing at **82 MB** of NetCDF
that stays at NCEI. Every data read goes back to `www.ncei.noaa.gov`, so the store is only
as available as NCEI is.

What it adds over the source archive is that the twelve files become **one dataset**. NCEI
ships one NetCDF per indicator with no usable coordinates; here they are merged into 72
variables on a shared, CF-compliant `(depth, lat, lon)` grid you can `sel()` into.

The source accession is a finished, static product, so this store needs no update pipeline.

## View it in a browser

No install, no account, no download — the viewer streams chunks straight from the store,
and the science arrays straight from NCEI:

| Field | Viewer |
|---|---|
| Aragonite saturation state | [Open `OmegaA_an` in the viewer](https://data.source.coop/ocean-icechunks/oa-indicators/viewer/index.html#icechunk+https://data.source.coop/ocean-icechunks/oa-indicators/climatology::varname=OmegaA_an::px=0::py=0::alt=95910936::lat=48::lon=-110::dimIndices_depth=0) |
| pH (total scale) | [Open `pHT_an` in the viewer](https://data.source.coop/ocean-icechunks/oa-indicators/viewer/index.html#icechunk+https://data.source.coop/ocean-icechunks/oa-indicators/climatology::varname=pHT_an::px=0::py=0::alt=95910936::lat=48::lon=-110::dimIndices_depth=0) |
| Dissolved inorganic carbon | [Open `DIC_an` in the viewer](https://data.source.coop/ocean-icechunks/oa-indicators/viewer/index.html#icechunk+https://data.source.coop/ocean-icechunks/oa-indicators/climatology::varname=DIC_an::px=0::py=0::alt=95910936::lat=48::lon=-110::dimIndices_depth=0) |
| Total alkalinity | [Open `TA_an` in the viewer](https://data.source.coop/ocean-icechunks/oa-indicators/viewer/index.html#icechunk+https://data.source.coop/ocean-icechunks/oa-indicators/climatology::varname=TA_an::px=0::py=0::alt=95910936::lat=48::lon=-110::dimIndices_depth=0) |
| Fugacity of CO₂ | [Open `fCO2_an` in the viewer](https://data.source.coop/ocean-icechunks/oa-indicators/viewer/index.html#icechunk+https://data.source.coop/ocean-icechunks/oa-indicators/climatology::varname=fCO2_an::px=0::py=0::alt=95910936::lat=48::lon=-110::dimIndices_depth=0) |
| Revelle factor | [Open `RF_an` in the viewer](https://data.source.coop/ocean-icechunks/oa-indicators/viewer/index.html#icechunk+https://data.source.coop/ocean-icechunks/oa-indicators/climatology::varname=RF_an::px=0::py=0::alt=95910936::lat=48::lon=-110::dimIndices_depth=0) |

Those are the `_an` (objectively analysed mean) fields; the viewer's own dropdown reaches
all 72 variables, and the **Depth** slider moves through the 14 levels.

The links carry an opening view — centred on the middle of the grid, at the surface — and
the viewer's dataset picker offers this store rather than gridlook's 70 demo datasets,
because the published copy ships its own `static/catalog-extended.json`.

The viewer is [gridlook](https://github.com/eeholmes/gridlook), a WebGL globe for
cloud-hosted Zarr and Icechunk stores, published alongside the data at
[`oa-indicators/viewer/`](https://data.source.coop/ocean-icechunks/oa-indicators/viewer/index.html). The store to open is in the URL *fragment* after `#`, so
any store can be swapped into the same link — nothing about the viewer is specific to this
dataset.

**Unlike the CoastWatch stores in this repository, this one draws in an ordinary browser.**
A virtual store needs CORS on two hosts, because metadata and data come from different
places. Source Cooperative is wide open, and `www.ncei.noaa.gov` also sends
`Access-Control-Allow-Origin: *` on ranged GETs — where `coastwatch.noaa.gov` sends no CORS
headers at all and is therefore blocked. A `Range: bytes=a-b` header is CORS-safelisted, so
no preflight is involved.

## How to open it

Needs `icechunk >= 2.2` and `xarray`. No credentials and no account.

> **icechunk 1.x will not work.** `icechunk.http_storage` does not exist in icechunk 1.x
> (it arrived in 2.0), and `icechunk.credentials.HttpAccess` arrived in 2.1. Every icechunk
> 2.x release needs **Python 3.12 or newer**, so on an older Python `pip install icechunk`
> quietly installs 1.1.x, and the code below fails with
> `AttributeError: module 'icechunk' has no attribute 'http_storage'`. Check what you have:
> `python -c "import icechunk; print(icechunk.__version__)"`.

```python
import icechunk
import xarray as xr

url = "https://data.source.coop/ocean-icechunks/oa-indicators/climatology"
repo = icechunk.Repository.open(icechunk.http_storage(url))

# The arrays live at NCEI, outside the store, so authorize the virtual chunk
# container at open time. This is the one non-standard step for a virtual store;
# the container is in the saved config, so you do not need to know the URL.
auth = {p: icechunk.credentials.HttpAccess for p in repo.config.virtual_chunk_containers or []}
store = repo.reopen(authorize_virtual_chunk_access=auth).readonly_session("main").store

ds = xr.open_zarr(store, consolidated=False, chunks=None)
print(ds)
```

Measured anonymously over the public endpoint: opening the store and reading its metadata
takes about 1.5 s, and any single field about 1 s.

```python
ds.OmegaA_an.sel(depth=0)                                  # surface aragonite saturation
ds.pHT_an.sel(lat=44.5, lon=-124.5, method="nearest")      # pH profile, Oregon shelf
ds[["OmegaA_an", "OmegaA_SE", "OmegaA_dd"]].sel(depth=100) # value, error, sample count
```

**Use `chunks=None`, not `chunks={}`, unless you want dask.** Each variable is a *single*
chunk covering the whole array, because the source arrays are contiguous and uncompressed.
There is nothing to parallelise within a variable, and any read of any part of a variable
fetches all 1.2 MB of it.

Land and unsampled cells are `NaN`. The source uses NaN directly and declares no
`_FillValue` or `missing_value`, so nothing has to be unmasked.

## About the data

These are World Ocean Atlas–style objective analyses of carbonate-system observations from
[CODAP-NA](https://doi.org/10.5194/essd-13-2777-2021) (Version 2021) and
[GLODAPv2.2021](https://doi.org/10.5194/essd-13-5565-2021), adjusted to the year 2010 with
ESPER ([Carter et al. 2021](https://doi.org/10.1002/lom3.10461)) before gridding.

- **Grid:** 1° latitude × 1° longitude, 14 depth levels — 0, 10, 20, 30, 50, 75, 100, 125,
  150, 200, 250, 300, 400, 500 m
- **Extent:** lat 10.5 → 85.5 °N, lon −179.5 → −39.5 °E. Coverage is coastal, not global:
  about 63 % of the surface grid has data
- **No time dimension.** It is a climatology; the contributing observations span
  2003-12-06 to 2018-11-22
- **Conventions:** CF-1.12, ACDD-1.3 (added here — see "What was changed from the source")
- **Archive:** NCEI accession
  [0270962](https://www.ncei.noaa.gov/data/oceans/ncei/ocads/metadata/0270962.html),
  DOI [10.25921/g8pb-zy76](https://doi.org/10.25921/g8pb-zy76)

### Variables

Twelve indicators × six fields = **72 variables**, all `float64` on `(depth, lat, lon)`.

| Prefix | Indicator | Units | CF `standard_name` |
|---|---|---|---|
| `OmegaA` | aragonite saturation state | 1 | — |
| `OmegaC` | calcite saturation state | 1 | — |
| `CO3` | carbonate ion content | µmol kg⁻¹ | — |
| `DIC` | total dissolved inorganic carbon content | µmol kg⁻¹ | `moles_of_dissolved_inorganic_carbon_per_unit_mass_in_sea_water` |
| `TA` | total alkalinity content | µmol kg⁻¹ | `sea_water_alkalinity_per_unit_mass_expressed_as_mole_equivalent` |
| `pHT` | pH on the total scale | 1 | `sea_water_ph_reported_on_total_scale` |
| `fCO2` | fugacity of carbon dioxide | µatm | `fugacity_of_carbon_dioxide_in_sea_water` |
| `Hfree` | free hydrogen ion content | nmol kg⁻¹ | — |
| `Htotal` | total hydrogen ion content | nmol kg⁻¹ | — |
| `RF` | Revelle factor | 1 | — |
| `T` | water temperature (ITS-90) | °C | `sea_water_temperature` |
| `S` | salinity (PSS-78) | 1 | `sea_water_practical_salinity` |

A dash means the [CF standard name table](https://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html)
has no entry for that quantity — it was checked, and none was invented.

Each prefix carries six fields:

| Suffix | Field |
|---|---|
| `_an` | objectively analysed mean — **the field NCEI recommends using** |
| `_mn` | statistical mean of the observations in each grid square |
| `_sd` | standard deviation about that mean |
| `_SE` | standard error of the analysed field |
| `_dd` | number of observations (`number_of_observations`) |
| `_gp` | number of grid squares within the radius of influence |

So `OmegaA_an` is the analysed aragonite saturation state, and `OmegaA_dd` the number of
observations behind it — useful for deciding where the analysis is actually constrained.

## How this was built

The notebook that built it sits next to this README:
**`oa-indicators-icechunk-sc.ipynb`** (also in the GitHub repository
<https://github.com/ocean-icechunks/icechunks>, directory `oa-indicators/`). It opens each of
the twelve source files with [VirtualiZarr](https://virtualizarr.readthedocs.io), merges
them, rewrites the metadata, writes the store, and then validates the *published* store
from the anonymous read path — including reading **all 72 arrays back and comparing them
element by element against the source files at NCEI**.

It runs end to end **without credentials and without writing anything**: `RUN_WRITE`
defaults to `False`, so it builds the virtual dataset and the metadata, skips the write,
and validates the live store. The committed outputs are from exactly that run.
`requirements.txt` beside it lists the package floors; Python 3.12 or newer is required,
because `icechunk` 2.x is published `requires_python = ">=3.12"`.

The source is twelve NetCDF-4 files, one per indicator, at

```
https://www.ncei.noaa.gov/data/oceans/ncei/ocads/data/0270962/
```

NCEI serves them over HTTPS with `Accept-Ranges: bytes`, which is what makes virtualizing
possible, and — unlike NOAA CoastWatch — with `Access-Control-Allow-Origin: *`.

### What was changed from the source

**Metadata only. No data value was altered** — which is the only kind of change a virtual
store can make, since the bytes stay in NCEI's files.

- **The coordinates were unusable as delivered.** The files carry phony HDF5 dimension
  scales `dep`, `lat` and `lon` — arrays of zeros marked *"This is a netCDF dimension but
  not a netCDF variable"* — while the real values sit in three separate variables `depth`,
  `latitude` and `longitude`. xarray hides the phony scales and reports `Dimensions
  without coordinates`, so `sel(lat=...)` did not work on the source at all. The real
  variables are promoted to index coordinates named `depth`, `lat` and `lon`.
- **`units` was not UDUNITS.** Every dimensionless field said `"N/A"`, and temperature said
  `"degrees Celsius"` — with a space, which UDUNITS will not parse. They are now `"1"` and
  `"degree_Celsius"`.
- **`standard_name` held free text**, not CF standard names — `"Aragonite saturation
  state"`, `"Number_of_observations for pH on Total Scale"`. That text moved to `long_name`
  (and the source's own wrapped `long_name` was kept verbatim as `comment`), and a real
  `standard_name` was supplied only where the CF table has one.
- **There were no global attributes** beyond a per-file title, abstract and citation. The
  store has a full CF/ACDD set: `Conventions`, `title`, `summary`, `keywords`, `source`,
  `history`, creator and publisher fields, the DOI, the citation, the geospatial bounds and
  the observation time coverage.
- Coordinates gained `standard_name`, `units`, `axis` and — for depth — `positive: down`.
- Each variable gained a `source` attribute naming the NetCDF file it references.

The viewer is published by `publish_viewer.py` in the same repository
(`python publish_viewer.py --product oa-indicators --build ~/gridlook`); it is a plain
static build of gridlook and holds no data of its own.

### Provenance

| When | What |
|---|---|
| 2026-09-17 | Built and committed, snapshot `3VZQ6VDVY2644RZ9M0Z0` (icechunk 2.2.2, virtualizarr 2.7.3) |
| 2026-09-17 | gridlook viewer published at `oa-indicators/viewer/`, with its own dataset catalog and an opening view |

Every code block on this page was executed against the live store before it was published.

## Reuse and citation

**Code.** The notebook and helpers are released under
[Apache-2.0](https://github.com/ocean-icechunks/icechunks/blob/main/LICENSE) and are free to use,
copy, adapt and redistribute, commercially or not — no attribution required.

**Data.** The data is not ours, and this store contains none of it — only references to
NCEI's files. NCEI states no use restrictions for accession 0270962. Please cite it:

> Jiang, Li-Qing; Boyer, Tim P.; Paver, Christopher R.; Reagan, James R.; Alin, Simone R.;
> Barbero, Leticia; Carter, Brendan R.; Feely, Richard A.; Wanninkhof, Rik (2022).
> Climatological distribution of ocean acidification indicators from surface to 500 meters
> water depth on the North American ocean margins from 2003-12-06 to 2018-11-22 (NCEI
> Accession 0270962). NOAA National Centers for Environmental Information. Dataset.
> <https://doi.org/10.25921/g8pb-zy76>

and, for the observations the analysis is built on:

> Jiang, L.-Q., Feely, R. A., Wanninkhof, R., Greeley, D., Barbero, L., Alin, S., et al.
> (2021). Coastal Ocean Data Analysis Product in North America (CODAP-NA) — an internally
> consistent data product for discrete inorganic carbon, oxygen, and nutrients on the North
> American ocean margins. *Earth System Science Data*, 13(6), 2777–2799.
> <https://doi.org/10.5194/essd-13-2777-2021>

## Credits

- **Data:** Li-Qing Jiang, Tim P. Boyer, Christopher R. Paver, Hyelim Yoo, James R. Reagan,
  Simone R. Alin, Leticia Barbero, Brendan R. Carter, Richard A. Feely and Rik Wanninkhof —
  CISESS/University of Maryland, NOAA NCEI, NOAA PMEL, NOAA AOML, CIMAS and CICOES.
  Funded by the NOAA Ocean Acidification Program and archived by NOAA NCEI.
- **Icechunk packaging:** built with [Icechunk](https://icechunk.io),
  [VirtualiZarr](https://virtualizarr.readthedocs.io) and [Xarray](https://xarray.dev),
  hosted on [Source Cooperative](https://source.coop/ocean-icechunks/oa-indicators).
