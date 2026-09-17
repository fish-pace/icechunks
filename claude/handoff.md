# Handoff — icechunks

Rolling state for this repo. Orientation only: the open threads below are a record of
what is unfinished, not a task list.

## Where things stand (2026-09-17)

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

## Open threads

- **Auto-update pipeline — undesigned, and the only substantial work left.** `write_group`
  skips groups that already exist but nothing appends *new time steps* to an existing group.
  Until that path and a trigger exist, the stores stay frozen at the last manual run and
  drift behind CoastWatch — three weeks and counting as of this writing.
- **Cosmetic:** the production notebook's kernel metadata records Python 3.11.14 (from being
  opened, not run); the test notebooks say 3.12.12, which is the truthful one.
- `ocean-icechunks/test-repo/noaa-ohc` holds 84 objects from verification runs. Deliberately
  left in place as a worked example.
