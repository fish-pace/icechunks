# GOBAI-O2 monthly — what the cleanup found

The store (`fish-pace/gobai-o2/monthly`, materialized) was built 2026-08-06 and is static:
v2.3 is a finished archive version, so there is no update pipeline to write. A later GOBAI
version would be a new store. What follows is worth knowing before touching it or writing a
similar one.

- **The validation was vacuous.** The reopen cell rebound `ds` from the source to the
  published dataset, so every assertion after it compared the store with itself. Renamed to
  `published`. Look for this shape in any notebook that validates in place.
- **Never sample a contiguous, uncompressed source through dask chunks.** 81 scattered
  points read at `chunks=(14, 2, 73, 120)` took 11m41s; `chunks=None` for the sample took
  the whole notebook to 57 s. The source has no chunks, so every dask chunk is thousands of
  strided range requests.
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
