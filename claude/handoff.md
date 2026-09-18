# Handoff — icechunks

Rolling state for this repo. Orientation only: the open threads below are a record of what
is unfinished, not a task list.

## Where things stand (2026-09-17)

Three datasets, all built, published and documented on Source Cooperative. Each has a
README, its own `requirements.txt`, and its notebooks mirrored to its store root, plus a
gridlook viewer.

| Dataset | Store | Kind | Viewer |
|---|---|---|---|
| CoastWatch OHC | `ocean-icechunks/noaa-ohc/{na,np,sp}` | virtual | published, but CORS-blocked at the source |
| GOBAI-O2 v2.3 monthly | `fish-pace/gobai-o2/monthly` | materialized | renders — confirmed by Eli |
| OA indicators | `ocean-icechunks/oa-indicators/climatology` | virtual | renders — confirmed by Eli, 2026-09-18 |

- **CoastWatch OHC** — three repos, one per region grid, three groups each (`daily`,
  `14day_v1`, `14day`), covering 2020-04-30 → 2026-08-26. The only **growing** source here,
  and so the only one needing an update pipeline; see Open threads.
- **GOBAI-O2 v2.3** — arrived 2026-09-17 from `nmfs-opensci/gobai-rfrom-icechunks`. Finished
  archive version, static. [notes/gobai-o2-monthly.md](notes/gobai-o2-monthly.md)
- **OA indicators** — NCEI accession 0270962, built in PR #24. Twelve NetCDFs merged into one
  flat group of 72 variables; 84 objects and 35 kB referencing 82 MB left at NCEI. Finished
  accession, static. [notes/oa-indicators.md](notes/oa-indicators.md)

**Before running anything:** the kernel env is Python 3.11 and `icechunk` 2.x requires
>= 3.12, so it cannot be installed there. A 3.12 venv works — recipe and traps in
[notes/environment.md](notes/environment.md). Build venvs in the scratchpad and install with
`--no-cache-dir`: `~` has a 20 GiB quota and little headroom
([notes/home-quota.md](notes/home-quota.md)).

## Working principles

- **The notebook outputs *are* the build log.** No separate log exists. Commit executed
  production notebooks; an uncommitted or stripped run erases the record of that build.
- **Verify the destination, not just the notebook.** "Committed" means the write path
  returned, not that the public read path works —
  [notes/verifying-published-repos.md](notes/verifying-published-repos.md).
- **Verify transport here, rendering with Eli.** There is no browser on the hub. Check status
  codes, content types and CORS, then ask.
- **Mirror only from merged `main`**, then check by checksum. Uploading from a branch is how
  the published copies drift.
- **This image ships more than we declare.** Anything that must work for a stranger gets
  tested in a clean venv, not in the kernel env.
- **Nothing copies array bytes.** Every pipeline but GOBAI-O2 is virtual references into
  files that stay at the source.
- **Use `git worktree` for anything substantial.** Concurrent sessions share this checkout.

## Recently shipped (2026-09-17, PRs #12–#19, #23–#26)

A full repo audit and its fixes; GOBAI-O2 moved in and made reproducible; the OA-indicators
store built; viewers published for all three products; CoastWatch brought up to the same
standard (README, per-product `requirements.txt`, notebooks verified by running them in a
clean venv). Two notebook bugs were found that way — a vacuous validation in the GOBAI
notebook, and `ocean-heat-test-sc.ipynb` failing on any re-run until the first write was
given `mode="w"`.

## Open threads

- **Auto-update pipeline for CoastWatch — undesigned, and the only substantial work left.**
  `write_group` skips groups that already exist, but nothing appends *new time steps* to an
  existing group. Until that path and a trigger exist the stores stay frozen at the last
  manual run and drift behind the archive.
- **`np` and `sp` viewer links share `na`'s `alt`** and may open too tight. Needs two numbers
  from a browser: drag each globe, copy the URL, update `_OHC_BASINS` in `publish_viewer.py`.
- **The OHC viewer's behaviour under a CORS-disabling extension is unconfirmed.** The OA
  viewer renders (Eli, 2026-09-18); the OHC one is blocked at `coastwatch.noaa.gov` by design
  and shows coordinates only, so the open question is narrower than it was — whether it draws
  for someone overriding CORS locally. [notes/viewers.md](notes/viewers.md)
- **The docs mirror has no committed tooling.** The only committed path is the last cell of
  `ocean-heat-production-sc.ipynb`, which means a 2.5-hour rebuild first, so 2026-09-17's
  mirrors used a throwaway scratchpad script. Worth a committed `mirror_docs.py` beside
  `publish_viewer.py`. That cell also passes **no `ContentType`**, and Source Cooperative
  serves types as uploaded — a full rebuild could downgrade all five files to
  `binary/octet-stream`.
- **Cosmetic:** the production notebook's kernel metadata records Python 3.11.14 (from being
  opened, not run); the test notebooks say 3.12.12, which is the truthful one.
- `ocean-icechunks/test-repo/{noaa-ohc,oa-indicators}` hold objects from verification runs,
  deliberately left as worked examples.

## Notes

- [environment.md](notes/environment.md) — the 3.12 venv recipe and its traps
- [home-quota.md](notes/home-quota.md) — the 20 GiB quota, how to measure it, what fills it
- [verifying-published-repos.md](notes/verifying-published-repos.md) — checking a store over HTTPS
- [viewers.md](notes/viewers.md) — gridlook, CORS on two hosts, catalogs, camera state
- [gobai-o2-monthly.md](notes/gobai-o2-monthly.md) — what that cleanup found
- [oa-indicators.md](notes/oa-indicators.md) — what that build found
- [ohc-rebuild-2026-08-26.md](notes/ohc-rebuild-2026-08-26.md) — the CoastWatch rebuild record
