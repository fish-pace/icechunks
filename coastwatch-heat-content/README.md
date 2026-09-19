# NOAA CoastWatch Ocean Heat Content — Icechunk

**[🌐 View data in browser](#view-it-in-a-browser)** · **[💻 Data access (code)](#how-to-open-it)** · **[📦 Data access (CoastWatch)](https://coastwatch.noaa.gov/pub/socd2/coastwatch/ocean_heat/)**

[Icechunk](https://icechunk.io) stores of the full **NOAA CoastWatch Ocean Heat Content
(OHC) Product Suite** archive — upper-ocean heat content, SST, sea surface height anomaly
and isotherm depths at 0.25°, daily, **2020-04-30 through 2026-08-26** — for three regions:

| Region | Icechunk repository | Grid |
|---|---|---|
| **North Atlantic** (`na`) | `https://data.source.coop/ocean-icechunks/noaa-ohc/na` | 241 × 401 |
| **North Pacific** (`np`) | `https://data.source.coop/ocean-icechunks/noaa-ohc/np` | 241 × 721 |
| **South Pacific** (`sp`) | `https://data.source.coop/ocean-icechunks/noaa-ohc/sp` | 241 × 641 |

Each region is a **separate repository** because the three use different lat/lon grids and
cannot share a virtual Zarr array. Each holds the same three groups — see
[Groups inside each repository](#groups-inside-each-repository).

These stores are **virtual**: they copy no science data at all. Icechunk holds Zarr
metadata and byte-range references back to the original NetCDF/HDF5 files hosted at NOAA
CoastWatch, so a store of a multi-terabyte archive is megabytes of metadata and reads are
streamed from `coastwatch.noaa.gov` over HTTP range requests. That costs one extra step
when opening — see [How to open it](#how-to-open-it) — and it is why the browser viewer
needs the workaround described below.

The stores are built by a manual run, not a live feed. Until an automatic append is in
place, the last time step lags the CoastWatch archive by however long has passed since the
build recorded in [Provenance](#provenance).

## View it in a browser

> ### ⚠️ Read this first: the data will not draw unless you disable CORS
>
> The viewer loads, lists the variables and draws the map graticule, and then stops —
> because the science arrays are not in the store. They are at `coastwatch.noaa.gov`,
> which serves byte ranges happily to a script but sends no
> `Access-Control-Allow-Origin` header, so **your browser** refuses to hand those bytes
> to the page. This is a rule browsers enforce on the page's behalf; nothing the viewer
> or this repository can contain will waive it.
>
> To look at the data anyway, install a CORS-disabling browser extension (search your
> browser's extension store for "CORS unblock" or "Allow CORS"), enable it, and reload
> the viewer. Such an extension switches off a real security protection for the sites you
> enable it on, so turn it back off when you are done — or use a separate browser profile
> for it.
>
> The code path below has no such problem: this affects browsers only.

With that in place, the viewer streams chunks straight from the store — no install, no
account, no download:

| Region | Viewer |
|---|---|
| North Atlantic (`na`) | [Open `na` in the viewer](https://data.source.coop/ocean-icechunks/noaa-ohc/viewer/index.html#icechunk+https://data.source.coop/ocean-icechunks/noaa-ohc/na/::px=0::py=0::alt=95910936::lat=25.0562::lon=-47.2424::dimIndices_time=0) |
| North Pacific (`np`) | [Open `np` in the viewer](https://data.source.coop/ocean-icechunks/noaa-ohc/viewer/index.html#icechunk+https://data.source.coop/ocean-icechunks/noaa-ohc/np/::px=0::py=0::alt=95910936::lat=30.0::lon=-170.0::dimIndices_time=0) |
| South Pacific (`sp`) | [Open `sp` in the viewer](https://data.source.coop/ocean-icechunks/noaa-ohc/viewer/index.html#icechunk+https://data.source.coop/ocean-icechunks/noaa-ohc/sp/::px=0::py=0::alt=95910936::lat=-30.0::lon=-150.0::dimIndices_time=0) |

Each link opens that region's repository centred on its own basin, at the first time step.
There is deliberately no link per group or per variable: the three groups (`daily`,
`14day_v1`, `14day`) and the variables within each are dropdowns in the viewer, and its
dataset picker lists all three regions — so you can move anywhere in the archive without
coming back here.

Everything after `#` is a URL *fragment*, which the host never sees, so one viewer build
serves any store: the repository is the part before the first `::`, and `lat`, `lon` and
`alt` are the camera. Drag the globe and the address bar updates — copy it to share the
exact view you are looking at.

The viewer is [gridlook](https://github.com/eeholmes/gridlook), a WebGL globe for
cloud-hosted Zarr and Icechunk stores, published alongside the data at
[`noaa-ohc/viewer/`](https://data.source.coop/ocean-icechunks/noaa-ohc/viewer/index.html).
Give it a moment on first load: it fetches the store's metadata before drawing. It is a
browser reading a remote archive, so treat it as a look, not an analysis.

## How to open it

Requires `icechunk >= 2.1` and `xarray`. The science arrays live at CoastWatch, outside
these stores, so you must authorize the virtual chunk container at open time — this is the
one non-standard step, and the price of not copying the data.

> **icechunk 1.x will not work.** `icechunk.http_storage` does not exist in icechunk 1.x
> (it arrived in 2.0), and `icechunk.credentials.HttpAccess` arrived in 2.1. Every icechunk
> 2.x release needs **Python 3.12 or newer**, so on an older Python `pip install icechunk`
> quietly installs 1.1.x, and the code below fails with
> `AttributeError: module 'icechunk' has no attribute 'http_storage'`. Check what you have:
> `python -c "import icechunk; print(icechunk.__version__)"`.

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

print(ds_14day)
```

CoastWatch blocks the default `python-requests` User-Agent, but Icechunk sends its own
(`icechunk-rust-x.y.z`), so no custom headers are needed for reads.

If a read raises `StorageError: error fetching virtual reference ... connection closed
before message completed`, retry it. CoastWatch's HTTPS endpoint is slow and occasionally
drops connections; the reference is fine, and the same read succeeds on a retry.

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

Use `chunks={}` (dask-backed) as shown — with `chunks=None` the arrays are plain NumPy and
this concatenation eagerly materializes several GB into memory.

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

Each region covers a different domain — the North Atlantic grid is 0°–60°N, 100°W–0°, at
241 × 401. Open a repo and inspect its `latitude`/`longitude` coordinates for the exact
extent of the others.

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

Coordinates are `time`, `latitude` (`degrees_north`) and `longitude` (`degrees_east`).

Missing data is `-999` in the source files. A CF `missing_value` attribute has been added
where the source omitted it, so xarray masks `-999` to `NaN` automatically on read — no
manual masking needed.

## Groups inside each repository

Every region repo has the same three groups. They exist because the archive is not
homogeneous, and a single virtual Zarr array cannot span files that differ in variable set
or byte-level encoding:

| Group | Source directory | Period | Format |
|---|---|---|---|
| `daily` | `{region}/2020`–`{region}/2024` | 2020-04-30 → 2024-01-18 | NetCDF-3 Classic, big-endian |
| `14day_v1` | `{region}14/2024` → `{region}14/2025` day 084 | 2024-01-15 → 2025-03-25 | NetCDF-3 Classic, big-endian |
| `14day` | `{region}14/2025` day 085 → present | 2025-03-27 → 2026-08-26 | HDF5, little-endian |

1. **`daily` vs. `14day*`** — two generations of the product (source dirs `{region}` and
   `{region}14`) with **different variable sets**. The `14day*` files add the SST
   `quality_flag` variable, and `14day_v1` additionally carries a scalar
   `quality_information` summary. Keeping them separate preserves each generation's
   variables without forcing empty columns.
2. **`14day_v1` vs. `14day`** — partway through 2025 the source files switched from
   **NetCDF-3 (big-endian)** to **HDF5 (little-endian)**. Because Icechunk stores a single
   codec pipeline per array and references the original bytes, big-endian and
   little-endian chunks cannot live in one virtual array. The split is at day-of-year
   084/085 of 2025, verified identical for all three regions.

Time steps per group, as built:

| Region | `daily` | `14day_v1` | `14day` | Corrupt source files dropped |
|---|---|---|---|---|
| `na` | 1357 | 430 | 507 | 6 (`14day`) |
| `np` | 1356 | 390 | 513 | 1 (`daily`), 21 (`14day_v1`) |
| `sp` | 1349 | 411 | 513 | none |

> **Note on the overlap and gaps.** `daily` and `14day_v1` overlap by a few days around
> January 2024 (both cover 2024-01-15…2024-01-18). A handful of source files with corrupt
> (all-zero) coordinates and data were dropped during construction — they are bad in the
> source archive, not mishandled here — so a group may begin one day after its nominal
> boundary, and the counts differ between regions.

For a continuous single time series, open the groups separately and concatenate the shared
variables at read time, as shown above.

## How this was built

The notebooks that built these stores live in the GitHub repository
**<https://github.com/ocean-icechunks/icechunks>** (directory `coastwatch-heat-content/`). Two of
them sit alongside this README on Source Cooperative:

| Notebook | What it shows | Here? |
|---|---|---|
| `ocean-heat-test-local.ipynb` | Minimal proof of concept: CoastWatch NetCDF → VirtualiZarr → a **local** Icechunk store. Runs with no credentials; the committed copy carries its outputs. | yes |
| `ocean-heat-production-sc.ipynb` | The full parametrized pipeline that built all three region repos. Its committed outputs are the build log. | yes |
| `ocean-heat-test-sc.ipynb` | The same proof of concept, writing to Icechunk on Source Cooperative. | GitHub only |

`ocean-heat-test-sc.ipynb` is deliberately not published here: it needs Source Cooperative
write credentials, so it is no use to a reader who has just found the stores, and
`ocean-heat-test-local.ipynb` shows the same steps with none. It writes only to a scratch
repository and refuses to touch the published prefix.

**Start with `ocean-heat-test-local.ipynb`.** It is short, needs no account, and its
committed outputs show the whole pattern working: a ranged GET against CoastWatch, three
daily files virtualized and appended along `time` in about one second each, then the store
reopened and one `ohc` field read back through its virtual references.

The write notebooks import shared helpers from `icechunk_utils.py` (included here), and
`requirements.txt` (also included) lists the package floors. **Python 3.12 or newer is
required** — every `icechunk` 2.x release is published `requires_python = ">=3.12"`.

```bash
pip install -r requirements.txt
```

The browser viewer is published separately by `publish_viewer.py` in the GitHub
repository (`python publish_viewer.py --product noaa-ohc --build ~/gridlook`). It is a
plain static build of gridlook and holds no data of its own.

### Provenance

| When | What |
|---|---|
| 2026-08-26 | All three regions built at this location and committed — `na` head `PD810W3C6EZ7V5Y5094G`, `np` head `F29D3QM6P7G56RH3ZMYG`, `sp` head `MCV4SVX7J65PRQ15DY2G`. Four snapshots each: one per group, on top of the repository's first commit |
| 2026-09-17 | gridlook viewer published at `noaa-ohc/viewer/` (102 files, 22.5 MB) |

An earlier build of the same archive lived under `fish-pace/coastwatch/ocean-heat/`; these
repositories replaced it and it is no longer maintained. Every code block on this page was
executed against the live stores before it was published.

## Reuse and citation

**Code.** The notebooks and helpers are released under
[Apache-2.0](https://github.com/ocean-icechunks/icechunks/blob/main/LICENSE) and are free to use,
copy, adapt and redistribute, commercially or not — no attribution required.

**Data.** The data is not ours, and these stores contain none of it — only references to
files hosted by NOAA CoastWatch. For data use and citation, follow the source product
credited below.

## Credits

- **Data:** USDOC/NOAA/NESDIS/OSPO; University of Miami / Rosenstiel School of Marine and
  Atmospheric Science (contact: Lynn K. Shay). Product page:
  <http://www.ospo.noaa.gov/Products/ocean/ocean_heat.html>
- **Icechunk packaging:** built with [VirtualiZarr](https://virtualizarr.readthedocs.io),
  [Icechunk](https://icechunk.io) and [Xarray](https://xarray.dev), hosted on
  [Source Cooperative](https://source.coop/ocean-icechunks/noaa-ohc); the original file
  bytes remain at NOAA CoastWatch.
