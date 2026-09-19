# NOAA OISST v2.1 sea surface temperature — Icechunk

**[🌐 View data in browser](https://data.source.coop/ocean-icechunks/noaa-oisst/viewer/index.html#icechunk+https://data.source.coop/ocean-icechunks/noaa-oisst/oisst.icechunk/daily::varname=sst::dimIndices_time=15828::dimIndices_zlev=0)** · **[💻 Data access (code)](#how-to-open-it)** · **[📦 Data access (NCEI)](https://www.ncei.noaa.gov/products/optimum-interpolation-sst)** · **[📦 Data access (AWS Open Data)](https://registry.opendata.aws/noaa-cdr-oceanic/)** · **[📄 DOI 10.25921/RE9P-PT57](https://doi.org/10.25921/RE9P-PT57)**

An [Icechunk](https://icechunk.io) store of **NOAA's 1/4° Daily Optimum Interpolation Sea
Surface Temperature (OISST) v2.1** Climate Data Record — SST, SST anomaly, analysis error
and sea-ice concentration on a global 0.25° grid, **every day from 1981-09-01 to a day or two
ago**, kept up to date by an automated run about once a day.

| Icechunk repository | Group | What it holds |
|---|---|---|
| `https://data.source.coop/ocean-icechunks/noaa-oisst/oisst.icechunk` | `daily` | every day since 1981-09-01; **virtual** references to NOAA's files |
| | `monthly` | min, max, mean and standard deviation of each variable for every complete month; **real data**, chunked for time series |

The store is built and maintained by [NERACOOS](https://neracoos.org) /
[GMRI](https://gmri.org), and was started at
[OceanHackWeek 2026](https://oceanhackweek.org); see
[How this was built](#how-this-was-built). This page was written separately, by inspecting the
published store, and says where it is reporting the maintainers' description rather than
something checked.

The `daily` group is **virtual**: it copies no science data. Icechunk holds Zarr metadata
and byte-range references back to NOAA's original NetCDF files in the
[NOAA Oceanic Climate Data Records bucket](https://registry.opendata.aws/noaa-cdr-oceanic/)
on AWS (`s3://noaa-cdr-sea-surface-temp-optimum-interpolation-pds`, us-east-1), and every
read of a daily value goes to that bucket. That costs one extra step when opening — see
[How to open it](#how-to-open-it). The `monthly` group is ordinary Zarr data held in the
store itself.

## View it in a browser

No install, no account, no download — and **no CORS workaround**: both hosts a browser has to
talk to, Source Cooperative and NOAA's bucket, send `Access-Control-Allow-Origin: *`
(checked 2026-09-19).

| Group | Viewer |
|---|---|
| `daily` | [SST](https://data.source.coop/ocean-icechunks/noaa-oisst/viewer/index.html#icechunk+https://data.source.coop/ocean-icechunks/noaa-oisst/oisst.icechunk/daily::varname=sst::dimIndices_time=15828::dimIndices_zlev=0) · [SST anomaly](https://data.source.coop/ocean-icechunks/noaa-oisst/viewer/index.html#icechunk+https://data.source.coop/ocean-icechunks/noaa-oisst/oisst.icechunk/daily::varname=anom::dimIndices_time=15828::dimIndices_zlev=0) · [sea ice](https://data.source.coop/ocean-icechunks/noaa-oisst/viewer/index.html#icechunk+https://data.source.coop/ocean-icechunks/noaa-oisst/oisst.icechunk/daily::varname=ice::dimIndices_time=15828::dimIndices_zlev=0) · [analysis error](https://data.source.coop/ocean-icechunks/noaa-oisst/viewer/index.html#icechunk+https://data.source.coop/ocean-icechunks/noaa-oisst/oisst.icechunk/daily::varname=err::dimIndices_time=15828::dimIndices_zlev=0) |
| `monthly` | [mean SST](https://data.source.coop/ocean-icechunks/noaa-oisst/viewer/index.html#icechunk+https://data.source.coop/ocean-icechunks/noaa-oisst/oisst.icechunk/monthly::varname=sst_mean::dimIndices_time=520::dimIndices_zlev=0) · [max SST](https://data.source.coop/ocean-icechunks/noaa-oisst/viewer/index.html#icechunk+https://data.source.coop/ocean-icechunks/noaa-oisst/oisst.icechunk/monthly::varname=sst_max::dimIndices_time=520::dimIndices_zlev=0) · [mean SST anomaly](https://data.source.coop/ocean-icechunks/noaa-oisst/viewer/index.html#icechunk+https://data.source.coop/ocean-icechunks/noaa-oisst/oisst.icechunk/monthly::varname=anom_mean::dimIndices_time=520::dimIndices_zlev=0) |

The links open at 1 January 2025 (daily) and January 2025 (monthly) — a link cannot say "the
latest day" — and the time slider, the other variables and both groups are controls in the
viewer. Everything after `#` is a URL *fragment*, which the host never sees, so one viewer
build serves any store. Drag the globe and the address bar updates — copy it to share the
exact view you are looking at.

The viewer is [gridlook](https://github.com/eeholmes/gridlook), a WebGL globe for
cloud-hosted Zarr and Icechunk stores, published alongside the data at
[`noaa-oisst/viewer/`](https://data.source.coop/ocean-icechunks/noaa-oisst/viewer/index.html).
Give it a moment on first load: the `daily` group's metadata takes several seconds to read
(see [What to expect from reads](#what-to-expect-from-reads)). It is a browser reading a
remote archive, so treat it as a look, not an analysis.

## How to open it

No credentials and no account: both the store and NOAA's bucket are read anonymously.

```
pip install "icechunk>=2.0" xarray zarr "dask[array]"      # Python >= 3.12
```

> **icechunk 1.x will not work.** `icechunk.http_storage` does not exist in icechunk 1.x
> (it arrived in 2.0). Every icechunk 2.x release needs **Python 3.12 or newer**, so on an
> older Python `pip install icechunk` quietly installs 1.1.x, and the code below fails with
> `AttributeError: module 'icechunk' has no attribute 'http_storage'`. Check what you have:
> `python -c "import icechunk; print(icechunk.__version__)"`.

```python
import icechunk
import xarray as xr

url = "https://data.source.coop/ocean-icechunks/noaa-oisst/oisst.icechunk"
repo = icechunk.Repository.open(icechunk.http_storage(url))

# The daily arrays live in NOAA's S3 bucket, outside the store, so the virtual chunk
# container has to be authorized — anonymously. The container is in the store's saved
# config, so you do not need to know the bucket's name. The references are s3:// URLs,
# which is why this takes S3 anonymous credentials rather than HttpAccess.
auth = icechunk.containers_credentials(
    {prefix: icechunk.s3_anonymous_credentials() for prefix in repo.config.virtual_chunk_containers}
)
store = repo.reopen(authorize_virtual_chunk_access=auth).readonly_session("main").store

daily = xr.open_zarr(store, group="daily", consolidated=False, chunks={})
monthly = xr.open_zarr(store, group="monthly", consolidated=False, chunks={})

sst = daily.sst.sel(time="2024-07-04").squeeze().load()          # one global field
series = monthly.sst_mean.sel(lat=43.5, lon=290.5, method="nearest").squeeze().load()  # 45 years at a point
```

`chunks={}` gives lazy, dask-backed arrays. `monthly` needs no authorization of its own — it
is real data — but opening both from one authorized store is simplest.

Three things that trip people up:

- **Times are at 12:00 UTC**, the centre of each day. Select with a date string,
  `sel(time="2024-07-04")` or a `slice`; an exact midnight timestamp is not on the axis.
  `monthly` is stamped at the first of each month.
- **Longitude runs 0 to 360** (0.125 … 359.875), so 69.5°W is `lon=290.5`.
- Every variable has a length-1 `zlev` dimension (0 m). `.squeeze()` drops it.

### Which group to use

`daily` stores each day as one whole global field, which is what NOAA's files contain and
what a virtual store must keep. It is the right group for maps, single days and short
windows. A long time series at a point would read one whole field per day — 16,000 of them —
so for that use `monthly`, which is chunked `(24 months, 1, 90, 90)`: the maintainers report
that 44 years at a point costs about 9 MB and 23 requests.

### Preliminary and final data

NOAA publishes a *preliminary* file within a day or two of observation and replaces it with
the *final* file about two weeks later. Both are in `daily`: the maintainers' description is
that a final file replaces the preliminary one in place as soon as it exists, so each date
always carries the best available data. A boolean `preliminary` coordinate marks which is
which; on 2026-09-19 the most recent 14 days were flagged.

```python
final_only = daily.isel(time=~daily.preliminary.values)
```

`monthly` is computed from final data only, so it ends at the last complete final month.
Because NOAA deletes a preliminary file when the final one appears, a read of a
still-preliminary day can fail for the day or so before the store's next update; re-read, or
use final data only.

### What to expect from reads

Measured on 2026-09-19 from a JupyterHub in AWS us-west-2 (the NOAA bucket is in us-east-1),
with `zarr.config.set({"async.concurrency": 64})`. Observations, not benchmarks.

| read | time |
|---|---|
| open `daily` | 7 s |
| open `monthly` | 0.9 s |
| one day, global (`daily`) | 1.0 s |
| 31 days at a point (`daily`) | 0.8 s |
| 540 months at a point (`monthly`) | 1.4 s |
| one month, global (`monthly`, 64 chunks) | 1.0 s |

Opening `daily` is slow because its `time` coordinate is stored as 16,452 one-value chunks,
one per appended day, and all of them are read on open. It is a fixed cost per open, not per
read.

## About the data

[OISST v2.1](https://www.ncei.noaa.gov/products/optimum-interpolation-sst) ("Reynolds SST")
is a NOAA Climate Data Record from the National Centers for Environmental Information. SST
observations from satellite (AVHRR) and in situ platforms (ships, buoys, Argo floats) are
interpolated and extrapolated to a complete, smoothed global field every day; at the
marginal ice zone, sea-ice concentrations are used to generate proxy SSTs. This is the
**AVHRR-only** product. The grid is 0.25° × 0.25°, 720 × 1440, global.

### Variables

`daily` — stored as NOAA's `int16` with `scale_factor = 0.01` and `_FillValue = -999` over
land; xarray decodes them to floating point with NaN:

| variable | long name | units |
|---|---|---|
| `sst` | Daily sea surface temperature | Celsius |
| `anom` | Daily sea surface temperature anomalies (against a 1971–2000 climatology) | Celsius |
| `err` | Estimated error standard deviation of analysed_sst | Celsius |
| `ice` | Sea ice concentration — **a fraction, 0 to 1**, despite NOAA's `units` attribute | % |
| `preliminary` (coordinate) | whether that day is still NOAA's preliminary file | boolean |

`monthly` — sixteen variables, `<var>_min`, `<var>_max`, `<var>_mean` and `<var>_std` for
each of `sst`, `anom`, `err` and `ice`, as `int16` with `scale_factor = 0.01` for `sst_*` and
`anom_*` and `0.001` for `err_*` and `ice_*`. xarray decodes all of them correctly. **Read
the names, not the attributes:** each monthly variable still carries its daily source's
`long_name` — `sst_std` says "Daily sea surface temperature" — and the `monthly` group has
no global attributes. The `valid_min`/`valid_max` attributes of `err_*` and `ice_*` were not
rescaled with the data, so a tool that honours them (xarray does not) would mask monthly ice
concentrations above 0.1; ignore them. Reported to the maintainers as
[noaa_oisst#2](https://github.com/ocean-icechunks/noaa_oisst/issues/2), along with the slow
open of `daily`. The `daily` group carries NOAA's full CF-1.6 / ACDD-1.3 global
attributes, taken from the most recent file.

## How this was built

Not in this repository. The store is built and updated by NERACOOS / GMRI; the project is
**<https://github.com/ocean-icechunks/noaa_oisst>** (formerly
`oceanhackweek/ohw26_oisst_icechunk`), whose README describes the design. As of 2026-09-19
that repository holds the README only — the pipeline code is not published there yet — so
what follows is the maintainers' description plus what the store itself shows.

- `daily`: each NOAA NetCDF file's chunk references are parsed with
  [VirtualiZarr](https://virtualizarr.readthedocs.io) and committed. The references are
  `s3://` URLs into NOAA's bucket; the chunks are NOAA's own — one per day and variable,
  zlib-compressed with shuffle.
- `monthly`: statistics computed from final daily data and written as Zarr, blosc-compressed.
- A scheduled run ingests whatever is new: new preliminary days, final files replacing the
  preliminary days they supersede, and a monthly rollup once every day of a month is final.

The store's history is its log — 1,089 commits on 2026-09-19, from "Repository initialized"
on 2026-08-28 through the month-by-month backfill to entries like *"Final files replace
preliminary for 2026-09-01, 2026-09-02"*:

```python
for snapshot in repo.ancestry(branch="main"):
    print(snapshot.written_at, snapshot.message)
```

This README and the viewer are maintained in
<https://github.com/ocean-icechunks/icechunks> (`noaa-oisst/README.md`, and the `noaa-oisst`
entry in `publish_viewer.py`).

### What was changed from the source

Nothing in NOAA's arrays or their attributes, as far as inspection shows. The store adds the
`preliminary` coordinate and the `monthly` group.

### Provenance

| When | What |
|---|---|
| 2026-08-28 | Repository initialized; `daily` backfilled from 1981-09-01 |
| 2026-09-19 | State when this page was written: `daily` has 16,452 days through 2026-09-16, the last 14 preliminary; `monthly` has 540 months, 1981-09 through 2026-08; head snapshot `1H5D09GQTBHSNHGT67TG`. The store has moved on since — it updates about daily |
| 2026-09-19 | gridlook viewer published at `noaa-oisst/viewer/` |

Every code block on this page was executed against the live store before it was published.
**Not verified:** the monthly statistics against an independent calculation; the
maintainers' figures for the cost of a point time series; how the update run is scheduled.
The viewer's transport was checked here; that it draws was reported by Eli Holmes.

## Reuse and citation

**This page and the viewer configuration** are released under
[Apache-2.0](https://github.com/ocean-icechunks/icechunks/blob/main/LICENSE) and are free to
use, copy, adapt and redistribute, commercially or not — no attribution required. For the
store and its pipeline, see the [maintainers' repository](https://github.com/ocean-icechunks/noaa_oisst).

**Data.** The data is NOAA's, and the `daily` group contains none of it — only references to
NOAA's files. NOAA data disseminated through its open-data program are open to the public
and can be used as desired; NOAA requests attribution, and it is not permissible to state or
imply endorsement by or affiliation with NOAA. The `monthly` statistics are derived from
NOAA's data and are not an original, unaltered NOAA product. Cite the Climate Data Record,
not this repackaging:

> Huang, Boyin; Liu, Chunying; Banzon, Viva F.; Freeman, Eric; Graham, Garrett; Hankins,
> William; Smith, Thomas M.; Zhang, Huai-Min (2020). NOAA 0.25-degree Daily Optimum
> Interpolation Sea Surface Temperature (OISST), Version 2.1. NOAA National Centers for
> Environmental Information. <https://doi.org/10.25921/RE9P-PT57>

> Huang, B., C. Liu, V. Banzon, E. Freeman, G. Graham, B. Hankins, T. Smith, and H.-M. Zhang
> (2021). Improvements of the Daily Optimum Interpolation Sea Surface Temperature (DOISST)
> Version 2.1. *Journal of Climate*, 34(8), 2923–2939.
> <https://doi.org/10.1175/JCLI-D-20-0166.1>

Earlier descriptions of the method: Reynolds et al. (2007),
<https://doi.org/10.1175/2007JCLI1824.1>, and Banzon et al. (2016),
<https://doi.org/10.5194/essd-8-165-2016>.

## Credits

- **Data:** NOAA National Centers for Environmental Information, OISST v2.1 Climate Data
  Record; hosted on AWS through the NOAA Open Data Dissemination program.
- **Icechunk store and update pipeline:** [NERACOOS](https://neracoos.org) /
  [GMRI](https://gmri.org) (Alex Kerney), started at
  [OceanHackWeek 2026](https://oceanhackweek.org); built with
  [VirtualiZarr](https://virtualizarr.readthedocs.io), [Icechunk](https://icechunk.io) and
  [Xarray](https://xarray.dev), hosted on
  [Source Cooperative](https://source.coop/ocean-icechunks/noaa-oisst).
- **This page and the viewer:** Eli Holmes, NOAA Fisheries.
