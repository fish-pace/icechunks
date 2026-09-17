# Handoff — icechunks

Rolling state for this repo. Orientation only: the open threads below are a record of
what is unfinished, not a task list.

## Where things stand (2026-09-17)

Two datasets now live here. **GOBAI-O2 v2.3 monthly** (`gobai-o2-monthly/`) arrived on
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

## Recently shipped (2026-09-17, PRs #12–#19)

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

## Open threads

- **Auto-update pipeline — undesigned, and the only substantial work left.** `write_group`
  skips groups that already exist but nothing appends *new time steps* to an existing group.
  Until that path and a trigger exist, the stores stay frozen at the last manual run and
  drift behind CoastWatch — three weeks and counting as of this writing.
- **Cosmetic:** the production notebook's kernel metadata records Python 3.11.14 (from being
  opened, not run); the test notebooks say 3.12.12, which is the truthful one.
- `ocean-icechunks/test-repo/noaa-ohc` holds 84 objects from verification runs. Deliberately
  left in place as a worked example.
