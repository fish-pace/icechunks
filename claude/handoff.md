# Handoff — icechunks

Rolling state for this repo. Orientation only: the open threads below are a record of
what is unfinished, not a task list.

## Where things stand (2026-09-17)

Three datasets now live here. **GOBAI-O2 v2.3 monthly** (`gobai-o2-monthly/`) arrived on
2026-09-17 from `nmfs-opensci/gobai-rfrom-icechunks`, where it sat beside an unrelated
product. Its store — `fish-pace/gobai-o2/monthly`, materialized, not virtual — was built
2026-08-06 and is **done and static**: v2.3 is a finished archive version, so there is no
update pipeline to write. What it lacked was any way for a reader to know what it was or
how it was made; it now has a README, a notebook that runs end to end without credentials
(`RUN_WRITE=False`), and its own `requirements.txt`, all mirrored to the `gobai-o2/` root.

The CoastWatch OHC archive is **built and live** at `ocean-icechunks/noaa-ohc/{na,np,sp}`
on Source Cooperative — three repos (one per region grid), three groups each, covering
2020-04-30 → 2026-08-26. Anonymous read works. Docs, `requirements.txt` and
`icechunk_utils.py` are mirrored at `noaa-ohc/` and verified byte-identical to `main`.

**OA indicators** (`oa-indicators/`) is the newest, built 2026-09-17 in PR #24 — a **virtual**
store at `ocean-icechunks/oa-indicators/climatology`, snapshot `3VZQ6VDVY2644RZ9M0Z0`. NCEI
accession 0270962 ships one NetCDF per indicator; twelve of them are merged into one flat group
of 72 variables on `(depth 14, lat 76, lon 141)`. The whole store is **84 objects and 35 kB**
referencing 82 MB that stays at NCEI. No time dimension — it is a climatology. Docs mirrored to
the `oa-indicators/` root, gridlook viewer at `oa-indicators/viewer/`, and that viewer **does**
draw in an ordinary browser, unlike CoastWatch's. Accession 0270962 is finished, so there is no
update pipeline to write.

**Before running anything:** the JupyterLab kernel env is Python 3.11 and `icechunk` 2.x
is `requires_python = ">=3.12"`, so it cannot be installed there. A 3.12 venv does work —
recipe and its two traps are in [notes/environment.md](notes/environment.md).

## Working principles

- **The notebook outputs *are* the build log.** No separate log exists. Commit executed
  production notebooks; an uncommitted or stripped run erases the record of that build.
- **Verify the destination, not just the notebook.** "Committed" means the write path
  returned, not that the public read path works — see
  [notes/verifying-published-repos.md](notes/verifying-published-repos.md).
- **Mirror only from merged `main`.** Uploading from a branch is how the published copies
  drift. Re-sync after every merge that touches a mirrored file, then check by checksum.
- **This image ships more than we declare.** Four dependencies were missing from
  `requirements.txt` and invisible here because the image happens to have them. Anything
  that must work for a stranger gets tested in a clean venv, not in the kernel env.
- **Nothing copies array bytes.** Every pipeline is virtual references into files that stay
  at the source, which is why a full three-region rebuild is hours, not days.

## Recently shipped (2026-09-17, PRs #12–#19, #23–#25)

A full repo audit and its fixes. Recorded the 2026-08-26 rebuild that had sat uncommitted;
completed the docs mirror; added `requirements.txt`; trimmed CLAUDE.md to this repo and
pointed it at the shared `virtual-icechunk` skill; rewrote the root README; hardened
`ocean-heat-test-sc.ipynb` (scratch prefix, guarded clear cell, cells in running order) and
**verified it by running it**; made `icechunk_utils` portable and honest (`min_minutes_left`
enforced, `Repository.exists()` instead of a swallowed exception, discovered paths); settled
reuse as Apache-2.0 with no attribution asked and data citation deferred to NOAA.

## GOBAI-O2 monthly — what the cleanup found

Worth knowing before touching that store or writing a similar one:

- **The validation was vacuous.** The reopen cell rebound `ds` from the source to the
  published dataset, so every assertion after it compared the store with itself. Renamed
  to `published`. Look for this shape in any notebook that validates in place.
- **Never sample a contiguous, uncompressed source through dask chunks.** 81 scattered
  points read at `chunks=(14, 2, 73, 120)` took 11m41s; `chunks=None` for the sample took
  the whole notebook to 57 s. The source has no chunks, so every dask chunk is thousands
  of strided range requests.
- **NCEI's download button is broken, the data is not.** `/archive/accession/download/…`
  302-loops; the archive filesystem path under `/data/oceans/archive/arc0207/0259304/5.5/`
  serves the 12 GB file directly and honours range requests, so `engine="netcdf4"` with a
  `#mode=bytes` suffix streams it.
- **A metadata-only fix to a published store is cheap.** The `license` attribute said
  CC BY 4.0; GOBAI-O2 is CC0 1.0. `zarr.open_group(session.store, mode="r+").attrs.put(...)`
  plus a commit rewrote no chunks — snapshot `3A41NX29VSPEXA94ES9G`.
- An aborted `Repository.create` had left an empty repo at the `gobai-o2/` **root** prefix
  (repo + one snapshot + one transaction, no refs). Deleted. Watch for this whenever a
  prefix is corrected after a first create.

## The GOBAI-O2 viewer (2026-09-17) — live and confirmed

gridlook is published at `fish-pace/gobai-o2/viewer/` (101 files, 22.5 MB) by the new
`publish_viewer.py`, and linked from the README's top nav row and its own section.
**Eli opened it in a browser and it renders**, so the whole path — build, upload, content
types, CORS, icechunk-js reading a materialized store — is proven end to end.
Four links, one per variable: `https://data.source.coop/fish-pace/gobai-o2/viewer/index.html#icechunk+https://data.source.coop/fish-pace/gobai-o2/monthly::varname=oxy` and the same for `uncer`,
`temp`, `sal`.

Verified from here: all 101 objects serve 200 with correct content types (including
`application/wasm`), and the cross-origin fetches the viewer makes against the store —
`repo`, `snapshots/…`, `manifests/…`, ranged — return 206 with
`access-control-allow-origin: *`. There is no browser on the hub, so the rendering itself
was confirmed by Eli, not here. That division is the norm: check the transport, then ask.

The README's top nav row is **plain markdown links, not centered HTML** — GitHub allows
`<p align="center">`, but the Source Cooperative repo page renders the README through its
own pipeline and the raw file is served as plain text, so HTML would be a gamble in two
places out of three.

Source Cooperative's static-hosting behaviour is in CLAUDE.md under "The browser viewer";
the two that cost time were content types never being inferred, and the edge 403ing the
default `Python-urllib` User-Agent, which reads exactly like a permissions failure.

## OA indicators — what the build found

Details are in CLAUDE.md under "Key gotchas (OA indicators…)"; the ones that cost time:

- **`xr.merge` applies `combine_attrs` to *variable* attributes, not just the dataset's.** So
  `combine_attrs="drop"` silently empties every variable's attrs. It looked like virtualizarr
  losing metadata and was not. Use `"drop_conflicts"` and clear the per-file globals by hand.
- **The source coordinates were unusable, not merely untidy.** Phony all-zero HDF5 dimension
  scales `dep`/`lat`/`lon`, with the real values in separate variables. xarray reports
  `Dimensions without coordinates`, so `sel(lat=...)` did not work on the source at all.
  `swap_dims` fixes it as metadata, which is all a virtual store can do.
- **CF compliance here was substantive.** `units` was `"N/A"` on every dimensionless field and
  `"degrees Celsius"` on temperature; `standard_name` held free text. Real CF standard names
  exist for only six of the twelve indicators — checked against the table, and **none invented**
  for saturation states, the Revelle factor, hydrogen ion content or carbonate per unit mass.
- **`vz.to_icechunk` defaults to `mode="w-"`**, so re-running a write raises `ContainsGroupError`
  rather than being a no-op. The notebook now skips a populated store unless `OVERWRITE` is set.
- **NCEI sends `Access-Control-Allow-Origin: *`** on ranged GETs where `coastwatch.noaa.gov`
  sends none. That, and nothing else, is why this viewer draws and the OHC one does not. A
  simple `Range: bytes=a-b` is CORS-safelisted, so no preflight is involved either.
- **gridlook needs no time dimension** — every time path is gated on a dim literally named
  `time`. It does need the spatial dims to be the trailing two, and `dimension_names` in the
  Zarr metadata. It also ranks coordinate name `lat` above `latitude`, which is why the store
  uses the short spelling.

**Still unconfirmed:** whether the OA viewer actually *renders*. Transport is verified from here
(content types, `application/wasm`, CORS on both hosts) but there is no browser on the hub. Ask
Eli — that division is the norm.

## Earlier next task, now done

**Issue #20 — OA indicators** (<https://github.com/fish-pace/icechunks/issues/20>), when
Eli says to start. Build a **virtual** Icechunk store, modelled on
`coastwatch-heat-content/`, from NCEI accession
[0270962](https://www.ncei.noaa.gov/data/oceans/ncei/ocads/metadata/0270962.html); data at
<https://www.ncei.noaa.gov/data/oceans/ncei/ocads/data/0270962/>, readable over HTTPS and
byte-subsettable. **One variable per NetCDF file, all to be merged into one store.** Then
a README, the reproducibility artifacts the other examples have, and a viewer. Destination
`https://source.coop/ocean-icechunks/oa-indicators`; the issue also says to test against
`~/test-repo/oa-indicators` (probably the `ocean-icechunks/test-repo` scratch repo — worth
confirming with Eli before writing anything to it).

Most of the parts exist. Reuse, do not reinvent:

- `coastwatch-heat-content/ocean-heat-production-sc.ipynb` for the virtual pattern, and
  `ocean-heat-test-local.ipynb` for a credential-free proof of concept first.
- `publish_viewer.py` for the viewer — add one `PRODUCTS` entry (bucket
  `ocean-icechunks`, its own viewer prefix, the store URL, the variable names). One
  gridlook build serves any store; nothing else should need changing. But note the
  CoastWatch caveat in CLAUDE.md: if the variables end up in **groups**, a link needs more
  than a store URL and a variable name, and that gap is still unsolved.
- The GOBAI-O2 set is the current template for "reproducibility artifacts": a README with
  a nav row and executed code blocks, a per-product `requirements.txt`, and a notebook
  that runs end to end with `RUN_WRITE`/`RUN_MIRROR` defaulting to `False`.
- `virtual-icechunk` skill first — this one is virtual, so it applies (it does not cover
  the materialized GOBAI-O2 work).

Merging one variable per file into a single store is the part with no precedent here:
CoastWatch splits into groups because of codec differences, which is the opposite problem.
Expect that to be where the design effort goes.

*Delivered in PR #24. Kept above as the record of what was asked for.*

## Open threads

- **Auto-update pipeline — undesigned, and the only substantial work left.** `write_group`
  skips groups that already exist but nothing appends *new time steps* to an existing group.
  Until that path and a trigger exist, the stores stay frozen at the last manual run and
  drift behind CoastWatch — three weeks and counting as of this writing.
- **Cosmetic:** the production notebook's kernel metadata records Python 3.11.14 (from being
  opened, not run); the test notebooks say 3.12.12, which is the truthful one.
- `ocean-icechunks/test-repo/noaa-ohc` holds 84 objects from verification runs. Deliberately
  left in place as a worked example. `test-repo/oa-indicators` is the same thing for PR #24.
- **The home quota is tight enough to break builds.** Writes to `~` started failing with
  "No space left on device" twice on 2026-09-17 while `df` still reported 109 G free on the
  export — it is a per-user block quota, not raw space. Clearing `~/.cache/pre-commit` (101 MB)
  was enough to unblock it, which shows how little headroom there is. `~/.cache/claude` is
  another 658 MB in four files if more is needed. The 404 G underneath has never been surveyed.
- **This repo now has concurrent sessions.** On 2026-09-17 two ran at once and the shared
  working tree had its branch switched mid-task. Use `git worktree add` for anything
  substantial; PRs #23, #24 and #25 all overlapped and #24 had to be rebased twice.
