# Handoff — icechunks

Rolling state for this repo. Orientation only: open threads below are a record of
what is unfinished, not a task list.

## Where things stand (2026-09-17)

The CoastWatch OHC archive is **built and live** at
`ocean-icechunks/noaa-ohc/{na,np,sp}` on Source Cooperative — three separate repos
(one per region grid), three groups each (`daily`, `14day_v1`, `14day`), covering
2020-04-30 → 2026-08-26. Anonymous read works.

The build ran on 2026-08-26 and succeeded, but the executed notebook sat
uncommitted for three weeks, so `main` still called the rebuild "in progress".
PR #12 fixes that. See [notes/ohc-rebuild-2026-08-26.md](notes/ohc-rebuild-2026-08-26.md)
for what the run actually did — snapshot IDs, timings, and the corrupt-file drops.

**Before running anything:** the JupyterLab image is Python 3.11.14 and `icechunk` is
not installed in it. icechunk 2.x is published `requires_python = ">=3.12"`, so it
cannot be installed there at all — the notebooks are currently unrunnable in the
kernel env. See [notes/environment.md](notes/environment.md).

## Working principles for this repo

- **The notebook outputs *are* the build log.** There is no separate log file. If a
  production run is left uncommitted or stripped of outputs, the record of that
  build is gone. Commit executed production notebooks.
- **Verify the destination, not just the notebook.** A run that prints "committed"
  is evidence the write path returned, not that the public read path works. Check
  the published prefix independently — see
  [notes/verifying-published-repos.md](notes/verifying-published-repos.md).
- **Nothing in this repo copies array bytes.** Every pipeline is virtual references
  into files that stay at the source. A "rebuild" is metadata only, which is why a
  full three-region rebuild is hours, not days.
- Docs/notebooks are mirrored to the destination root for reproducibility, so the
  git copy and the published copy can drift. They currently have.

## Recently shipped

- **Docs mirror completed 2026-09-17.** All six files are at `noaa-ohc/` and
  anonymous-readable: `README.md`, `requirements.txt`, `icechunk_utils.py` and the
  three notebooks. Three of them had 404ed since the first build while the README
  claimed they were "included here". `requirements.txt` is new — see
  [notes/environment.md](notes/environment.md) for the two dependency findings behind
  it, one of which blocks re-running the notebooks in the current image.
- **PR #13** (open, stacked on #12) — `requirements.txt`, the widened mirror list, and
  the CLAUDE.md updates that mark the mirror done.
- **PR #12** (open, not merged) — commits the executed production notebook and
  rewrites CLAUDE.md's status section: rebuild done, coverage table, corrupt-file
  drops. Merge this before #13; both touch the production notebook.
- **PR #8** — re-pointed the destination from `fish-pace/coastwatch/ocean-heat` to
  `ocean-icechunks/noaa-ohc` across notebooks, README, CLAUDE.md, `icechunk_utils.py`.
- **PRs #3–#6** — the original build under `fish-pace/coastwatch/ocean-heat`, plus
  docs and the GitHub link.

## Open threads

- **Auto-update pipeline — undesigned.** `write_group` skips groups that already
  exist, but nothing appends *new time steps* to an existing group. Until that path
  exists the repos are frozen at the last manual run and drift behind CoastWatch.
- **Repo hygiene**: `README.md` at the repo root is three lines and has no reuse
  statement, though the repo is Apache-2.0. Untracked `.claude/settings.local.json`
  is neither committed nor gitignored.
