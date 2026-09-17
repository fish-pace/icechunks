# The env the notebooks need, and the env they have

## icechunk 2.x is Python >= 3.12 only

Every icechunk 2.x release on PyPI — 2.0.0 through 2.2.1 — is published with
`requires_python = ">=3.12"`. There are no 3.11 wheels and no sdist fallback that
builds on 3.11.

The JupyterLab image (`/srv/conda/envs/notebook`) is currently **Python 3.11.14**,
and `icechunk` is not installed in it. The production run of 2026-08-26 was on
Python 3.12 — its stored warnings carry
`/srv/conda/envs/notebook/lib/python3.12/site-packages/...` paths, while the same
env today is `.../python3.11/...`. So the image moved *backwards* a minor version
at some point between the build and 2026-09-17.

Consequence: **`pip install "icechunk>=2.1"` in the current image resolves to
nothing** — pip reports no matching distribution, because the only versions it can
see for 3.11 are the 1.1.x line. The install line in CLAUDE.md is correct about
what is needed and silently wrong about whether it will work here.

Options when this next matters, in the order worth trying:

1. Check whether the image has been bumped back to 3.12 — this is a managed image
   and the interpreter is not ours to choose. `python -V` settles it.
2. Build in a 3.12 env of our own (venv/conda) rather than the kernel env.
3. Pin to `icechunk>=1.1,<2` — **not** advisable. The notebooks use 2.x APIs, and
   the published repos were written by 2.x.

Do not "fix" this by relaxing the bound in `requirements.txt` to whatever installs.

## Two dependencies the docs never mention

`NetCDF3Parser` (the `daily` and `14day_v1` groups) reaches
`kerchunk.netCDF3.NetCDF3ToZarr`, which subclasses `scipy.io._netcdf.netcdf_file`.
So the NetCDF-3 path needs **kerchunk and scipy**, neither of which appears in the
notebook imports or in CLAUDE.md's pip line. It has never been noticed because the
JupyterLab image ships both. On a bare env, the two NetCDF-3 groups fail with
kerchunk's "pip/conda install scipy" hint while the HDF5 group works fine — which
looks like a data problem and is not one.

`requirements.txt` lists them with this reasoning inline.

## Verifying a published repo without icechunk

Since the kernel env currently cannot import icechunk at all, repo-existence checks
go over plain HTTPS — see [verifying-published-repos.md](verifying-published-repos.md).
