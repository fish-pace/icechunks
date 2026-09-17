# The home quota, and why it keeps breaking builds

`/home/jovyan` has a **20 GiB hard quota**, set in 2i2c's cluster config at
`config/clusters/nmfs-openscapes/prod.values.yaml`:

```yaml
jupyterhub-home-nfs:
  quotaEnforcer:
    config:
      QuotaManager:
        hard_quota: 20   # in GiB
```

It excludes `allusers/`, `shared/`, `shared-public/` and `shared-readwrite/`, which sit under
the same mount but are separate NFS exports (`/prod/_shared-public` vs `/prod/eeholmes`).

## Three readings that mislead

Writes fail with `No space left on device` — a zero-byte `touch` included — while:

- `df` reports the whole export (512 G, 404 G used, ~110 G free) across every user. It says
  nothing about this budget.
- `df -i` shows 3 % inode use, and `~` holds ~242,000 files against 227 M free inodes. It is
  not a file-count limit.
- Total bytes used looks comfortable against any half-remembered ceiling. On 2026-09-17 that
  ceiling was recalled as 50 GB; it is 20 GiB, and three wrong explanations were published
  before the config settled it.

`nfs.dirsizeReporter` is disabled in that config, which is why nothing inside the container
can read usage.

## The only reliable reading

Write until it stops:

```bash
dd if=/dev/zero of=~/.quota-probe bs=1M count=10240 status=none; ls -l ~/.quota-probe; rm -f ~/.quota-probe
```

It fails at exactly the remaining bytes. Clean up after.

## What actually consumes it

Measured 2026-09-17: 17.77 GiB used, 1.89 GiB free — then `_temp_data` was moved out, leaving
~11 GiB used and 8.57 GiB free.

- `fish-pace-datasets/datasets/chla_z/notebooks/_temp_data` was **6.85 GB** of Argo BGC
  monthlies, ignored by git (`_temp_data/` in `.gitignore`) so **on no remote**. Copied to
  `shared-public/` at the same relative path, verified byte-identical with
  `rsync -ain --checksum`, then replaced with a symlink. A re-clone of that repo gets neither
  the data nor the link.
- `~/.cache/pip` refills on every venv build — install with `--no-cache-dir`.
- `~/.cache/claude/staging` holds Claude Code auto-update binaries, ~232 MB each, and the
  updater leaves them behind. Safe to clear; the live binary is a symlink into
  `~/.local/share/claude/versions/`.
- Only ~0.4 GB of the git repos under `~` are clean and pushed. Most carry uncommitted work,
  and `mindthegap` has three branches with no upstream at all. Deleting repos is a poor lever.

## Two consequences

- **A failed write truncates.** `pathlib.write_text` opens with mode `w`, so hitting the
  quota mid-write left `publish_viewer.py` at zero bytes. Write to a temp file and
  `os.replace`. An empty file still passes `ast.parse`, so a syntax check proves nothing.
- **Build in the scratchpad, not `~`.** `/` has tens of GB free.
