# NOAA CoastWatch Ocean Heat Content — Icechunk

[Icechunk](https://icechunk.io) stores of the full **NOAA CoastWatch Ocean Heat Content
(OHC) Product Suite** archive, spanning **2020 to present**, for three regions:

| Region | Icechunk repository |
|---|---|
| **North Atlantic** (`na`) | `https://data.source.coop/ocean-icechunks/noaa-ohc/na` |
| **North Pacific** (`np`)  | `https://data.source.coop/ocean-icechunks/noaa-ohc/np` |
| **South Pacific** (`sp`)  | `https://data.source.coop/ocean-icechunks/noaa-ohc/sp` |

Each region is a **separate repository** because the three regions use different lat/lon
grids and cannot share a virtual Zarr array.

These repositories do **not** copy the science data. Icechunk stores only metadata and
byte-range references back to the original NetCDF/HDF5 files hosted at NOAA CoastWatch;
reads are streamed directly from `coastwatch.noaa.gov` over HTTP range requests
("virtual chunks"). See [How to open it](#how-to-open-it) for the one extra step this
requires.

## How these were built

The notebooks that built these stores live in the GitHub repository
**<https://github.com/fish-pace/icechunks>** (directory `coastwatch-heat-content/`), and a
copy of each sits alongside this README on Source Cooperative:

| Notebook | What it shows |
|---|---|
| `ocean-heat-test-local.ipynb` | Minimal proof of concept: CoastWatch NetCDF → VirtualiZarr → a **local** Icechunk store. |
| `ocean-heat-test-sc.ipynb`    | Minimal proof of concept writing to Icechunk on **Source Cooperative**. |
| `ocean-heat-production-sc.ipynb` | The full parametrized pipeline that built all three region repos (`na`/`np`/`sp`). |

They are provided to document how the archive was assembled and as a starting point for
anyone building something similar. The write notebooks import shared helpers from
`icechunk_utils.py` (included here); running them additionally requires Source Cooperative
write credentials, so for most readers they are read-along references.

## About the data

The Satellite Ocean Heat Content Suite (produced by USDOC/NOAA/NESDIS/OSPO with the
University of Miami/Rosenstiel School) blends altimeter sea-surface-height anomalies with
GeoPolar blended SST and the SMARTS climatology to estimate upper-ocean heat content and
related fields. It is widely used in hurricane-intensification analysis.

- **Resolution:** 0.25° (~25 km), daily
- **Projection:** geographic latitude/longitude (WGS84-style; see the `crs` variable)
- **Conventions:** CF-1.6
- **Source product:** <http://www.ospo.noaa.gov/Products/ocean/ocean_heat.html>
- **Source archive:** <https://coastwatch.noaa.gov/pub/socd2/coastwatch/ocean_heat/>

Each region covers a different domain (e.g. the North Atlantic grid is 0°–60°N,
100°W–0°, 241 × 401). Open a repo and inspect its `latitude`/`longitude` coordinates for
the exact extent.

### Variables

| Variable | Long name | Units |
|---|---|---|
| `ohc` | ocean heat content | kJ cm⁻² |
| `sst` | sea surface temperature | °C |
| `ssha` | sea surface height above mean sea level | cm |
| `sshaE` | error in objective analysis of SSHA | — |
| `iso20C` | depth of the 20 °C isotherm | m |
| `iso26C` | depth of the 26 °C isotherm | m |
| `omld` | ocean mixed layer thickness | m |
| `landmask` | land/sea binary mask | — |
| `quality_flag` | per-cell SST quality flag (0 = good, 1 = bad) | — (`14day*` groups only) |
| `crs` | grid-mapping container (`grid_mapping_name = latitude_longitude`) | — |
| `quality_information` | scalar retrieval-statistics summary | — (`14day_v1` only) |

Coordinates are `time`, `latitude` (`degrees_north`), and `longitude` (`degrees_east`).

Missing data is represented as `-999` in the source files. A CF `missing_value`
attribute has been added where the source omitted it, so xarray masks `-999` to `NaN`
automatically on read — no manual masking needed.

## Groups inside each repository

Every region repo has the same three groups. They exist because the archive is not
homogeneous, and a single virtual Zarr array cannot span files that differ in variable
set or byte-level encoding:

| Group | Source directory | Period | Format |
|---|---|---|---|
| `daily` | `{region}/2020`–`{region}/2024` | 2020 → 2024-01-18 | NetCDF-3 Classic, big-endian |
| `14day_v1` | `{region}14/2024` → `{region}14/2025` day 084 | 2024-01-15 → 2025-03-25 | NetCDF-3 Classic, big-endian |
| `14day` | `{region}14/2025` day 085 → present | 2025-03-27 → present | HDF5, little-endian |

1. **`daily` vs. `14day*`** — these are two generations of the product (source dirs
   `{region}` and `{region}14`) with **different variable sets**. The `14day*` files add
   the SST `quality_flag` variable (and `14day_v1` additionally carries a scalar
   `quality_information` summary). Keeping them separate preserves each generation's
   variables without forcing empty columns.
2. **`14day_v1` vs. `14day`** — partway through 2025 the source files switched from
   **NetCDF-3 (big-endian)** to **HDF5 (little-endian)**. Because Icechunk stores a single
   codec pipeline per array and references the original bytes, big-endian and
   little-endian chunks cannot live in one virtual array. The split is at day-of-year
   084/085 of 2025, verified identical for all three regions.

> **Note on the overlap and gaps.** The `daily` and `14day` products overlap by a few days
> around January 2024 (both cover 2024-01-15…2024-01-18). A handful of source files with
> corrupt (all-zero) coordinates and data were dropped during construction, so a group may
> begin one day after its nominal codec boundary.

For a continuous single time series, open the groups separately and concatenate the
shared variables at read time (see below).

## How to open it

Requires `icechunk >= 2.1` and `xarray`. The science arrays live at CoastWatch, outside
these Icechunk stores, so you must authorize the virtual chunk container at open time —
this is the one non-standard step.

```python
import icechunk
import xarray as xr

# Pick a region: na (North Atlantic), np (North Pacific), or sp (South Pacific).
region = "na"
url = f"https://data.source.coop/ocean-icechunks/noaa-ohc/{region}"
repo = icechunk.Repository.open(icechunk.http_storage(url))

# Authorize reading virtual chunks from coastwatch.noaa.gov (anonymous HTTP).
auth = {p: icechunk.credentials.HttpAccess for p in repo.config.virtual_chunk_containers or []}
store = repo.reopen(authorize_virtual_chunk_access=auth).readonly_session("main").store

# chunks={} gives lazy, dask-backed arrays (recommended for the full archive).
ds_daily    = xr.open_zarr(store, group="daily",    consolidated=False, chunks={})
ds_14day_v1 = xr.open_zarr(store, group="14day_v1", consolidated=False, chunks={})
ds_14day    = xr.open_zarr(store, group="14day",    consolidated=False, chunks={})

print(ds_daily)
```

CoastWatch blocks the default `python-requests` User-Agent, but Icechunk sends its own
(`icechunk-rust-x.y.z`), so no custom headers are needed for reads.

### One continuous time series across groups

```python
shared = sorted(
    set(ds_daily.data_vars) & set(ds_14day_v1.data_vars) & set(ds_14day.data_vars)
)
ds = xr.concat(
    [ds_daily[shared], ds_14day_v1[shared], ds_14day[shared]],
    dim="time",
    data_vars="minimal",
    coords="minimal",
    compat="override",
)
```

Use `chunks={}` (dask-backed) as shown — with `chunks=None` the arrays are plain NumPy
and this concatenation eagerly materializes several GB into memory.

## Credits

- **Data:** USDOC/NOAA/NESDIS/OSPO; University of Miami / Rosenstiel School of Marine and
  Atmospheric Science (contact: Lynn K. Shay). Product page:
  <http://www.ospo.noaa.gov/Products/ocean/ocean_heat.html>
- **Icechunk packaging:** built with [VirtualiZarr](https://virtualizarr.readthedocs.io)
  and [Icechunk](https://icechunk.io); the original file bytes remain at NOAA CoastWatch.
