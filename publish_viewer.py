#!/usr/bin/env python3
"""Build the gridlook browser viewer and publish it into a Source Cooperative repo.

gridlook (https://github.com/eeholmes/gridlook, a fork of
https://github.com/d70-t/gridlook) is a WebGL viewer for cloud-hosted Zarr and
Icechunk stores. Its production build is a folder of plain static files with
relative paths, so it runs from any prefix that serves files over HTTPS -- no
server, no redirects. The store to open goes in the URL *fragment* (after
``#``), which the host never sees::

    https://data.source.coop/fish-pace/gobai-o2/viewer/index.html#icechunk+https://data.source.coop/fish-pace/gobai-o2/monthly::varname=oxy

Two things have to be true of the host, and both are true of Source
Cooperative (checked 2026-09-17):

* **CORS is open.** ``access-control-allow-origin: *`` with ``Range`` allowed
  and all headers exposed, on both GET and the OPTIONS preflight, so the viewer
  can read a store in another repo or another bucket.
* **Content types are served as uploaded.** They are *not* inferred, so this
  script sets them explicitly -- a browser refuses an ES module served as
  ``binary/octet-stream``, which is what an upload without ``ContentType`` gets.

There is no directory index: ``.../viewer/`` returns 400, so links must name
``index.html``. And the edge rejects the default ``Python-urllib`` User-Agent
with 403 -- any check from Python has to send its own (``curl`` is unaffected).

Usage
-----
1. Get gridlook and its dependencies::

       git clone https://github.com/eeholmes/gridlook ~/gridlook
       cd ~/gridlook && npm ci

   ``package.json`` asks for Node >= 24.16; the 2026-09-17 build ran on Node
   20.19.6 without trouble.

2. Build and upload. ``--build`` runs the Vite build for you; without it the
   script uploads an existing ``--dist`` folder::

       python publish_viewer.py --product gobai-o2 --build ~/gridlook --dry-run
       python publish_viewer.py --product gobai-o2 --build ~/gridlook

   ``--product`` picks the repo and store (see ``PRODUCTS``); it is required, so
   nothing is uploaded anywhere by default. One build serves every product --
   the store lives in the link, not the build -- so build once and pass
   ``--dist`` for the next one.

3. Open the viewer URL the script prints. ``--prune`` also deletes objects under
   the viewer prefix that the new build no longer contains; every build has new
   content-hashed asset names, so old ones pile up otherwise. Pruning never
   touches anything outside the viewer prefix.

Why not ``npm run build``: that runs ``vue-tsc`` and writes source maps, and on
a small machine it is OOM-killed. ``vite build --sourcemap false`` with a capped
Node heap builds in seconds and halves the upload (~23 MB). Type checking
belongs to gridlook's CI, not to publishing.

Credentials: the same short-lived Source Cooperative token as everything else
here, through ``icechunk_utils.get_source_credentials`` (which shells out to the
``source-coop`` CLI). Log in first::

    source-coop login --duration 1d --port 8400
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from icechunk_utils import get_source_credentials

PUBLIC = "https://data.source.coop"

# One entry per store that gets a viewer. `variables` are the data variables
# offered as links; the viewer opens one at a time.
#
# The CoastWatch OHC stores are not here: their data lives in groups
# (`daily`, `14day_v1`, `14day`) rather than at the root, so a link needs more
# than a store URL and a variable name.
PRODUCTS = {
    "gobai-o2": {
        "bucket": "fish-pace",
        "viewer_prefix": "gobai-o2/viewer",
        "store_url": f"{PUBLIC}/fish-pace/gobai-o2/monthly",
        "variables": ("oxy", "uncer", "temp", "sal"),
    },
}
DEFAULT_DIST = Path("/tmp/gridlook-dist")

# Browsers refuse ES modules served with the wrong type, and refuse to
# stream-compile wasm unless it is application/wasm. Do not rely on the
# platform's mimetypes table for these.
CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript",
    ".mjs": "text/javascript",
    ".css": "text/css",
    ".json": "application/json",
    ".geojson": "application/geo+json",
    ".wasm": "application/wasm",
    ".woff2": "font/woff2",
    ".woff": "font/woff",
    ".ttf": "font/ttf",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".ico": "image/x-icon",
    ".txt": "text/plain; charset=utf-8",
}


def viewer_urls(product: dict, prefix: str) -> dict[str, str]:
    base = f"{PUBLIC}/{product['bucket']}/{prefix}/index.html"
    store = f"icechunk+{product['store_url']}"
    return {var: f"{base}#{store}::varname={var}" for var in product["variables"]}


def build(gridlook: Path, dist: Path) -> None:
    gridlook = gridlook.expanduser().resolve()
    if not (gridlook / "package.json").exists():
        sys.exit(f"{gridlook} is not a gridlook checkout (no package.json)")
    if not (gridlook / "node_modules").exists():
        subprocess.run(["npm", "ci"], cwd=gridlook, check=True)
    env = dict(os.environ, NODE_OPTIONS="--max-old-space-size=1500")
    cmd = ["npx", "vite", "build", "--outDir", str(dist), "--emptyOutDir",
           "--sourcemap", "false"]
    print("$", " ".join(cmd), f"  (in {gridlook})")
    subprocess.run(cmd, cwd=gridlook, env=env, check=True)
    write_build_info(gridlook, dist)


def write_build_info(gridlook: Path, dist: Path) -> None:
    """Record which gridlook commit is live, so the published copy is traceable."""
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=gridlook, capture_output=True,
                              text=True).stdout.strip()
    info = {
        "gridlook_remote": git("remote", "get-url", "origin"),
        "gridlook_commit": git("rev-parse", "HEAD"),
        "gridlook_dirty": bool(git("status", "--porcelain", "--untracked-files=no")),
        "built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (dist / "build-info.json").write_text(json.dumps(info, indent=2) + "\n")


def plan(dist: Path) -> list[tuple[Path, str, str, str]]:
    """(local file, relative key, content type, cache control) for every file."""
    if not (dist / "index.html").exists():
        sys.exit(f"{dist} has no index.html -- build first (--build)")
    rows = []
    for path in sorted(p for p in dist.rglob("*") if p.is_file()):
        rel = path.relative_to(dist).as_posix()
        ctype = (CONTENT_TYPES.get(path.suffix.lower())
                 or mimetypes.guess_type(path.name)[0]
                 or "application/octet-stream")
        if rel == "index.html":
            cache = "no-cache"
        elif rel.startswith("assets/"):
            cache = "public, max-age=31536000, immutable"
        else:
            cache = "public, max-age=300"
        rows.append((path, rel, ctype, cache))
    return rows


def s3_client():
    import boto3

    creds, expiration = get_source_credentials()
    print(f"  Source Cooperative token valid until {expiration.isoformat()}")
    return boto3.client(
        "s3",
        endpoint_url=creds["endpoint_url"],
        region_name=creds["region_name"],
        aws_access_key_id=creds["aws_access_key_id"],
        aws_secret_access_key=creds["aws_secret_access_key"],
        aws_session_token=creds.get("aws_session_token"),
    )


def upload(rows, bucket: str, prefix: str, prune: bool) -> None:
    s3 = s3_client()
    # Assets first, index.html last: a visitor never gets a page whose assets
    # are not up yet.
    for path, rel, ctype, cache in sorted(rows, key=lambda r: r[1] == "index.html"):
        s3.upload_file(
            Filename=str(path), Bucket=bucket, Key=f"{prefix}/{rel}",
            ExtraArgs={"ContentType": ctype, "CacheControl": cache},
        )
        print(f"  put {rel}")
    if prune:
        keep = {f"{prefix}/{rel}" for _, rel, _, _ in rows}
        pages = s3.get_paginator("list_objects_v2").paginate(
            Bucket=bucket, Prefix=f"{prefix}/")
        for page in pages:
            for obj in page.get("Contents", []):
                if obj["Key"] not in keep:
                    s3.delete_object(Bucket=bucket, Key=obj["Key"])
                    print(f"  removed stale {obj['Key'][len(prefix) + 1:]}")


def verify(bucket: str, prefix: str) -> None:
    """Anonymous check that the page is public and served with the right type."""
    url = f"{PUBLIC}/{bucket}/{prefix}/index.html?cb={os.getpid()}"
    # Source Cooperative's edge 403s the default Python-urllib User-Agent.
    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": "gridlook-publisher"})
    with urllib.request.urlopen(req) as r:
        print(f"  {r.status} {r.headers['Content-Type']}  "
              f"cache-control: {r.headers.get('Cache-Control', '(not echoed)')}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--product", required=True, choices=sorted(PRODUCTS),
                    help="which repo and store to publish the viewer for")
    ap.add_argument("--build", type=Path, metavar="GRIDLOOK_DIR",
                    help="gridlook checkout to build before uploading")
    ap.add_argument("--dist", type=Path, default=DEFAULT_DIST,
                    help=f"build output folder (default {DEFAULT_DIST})")
    ap.add_argument("--prefix", default=None,
                    help="prefix for the viewer (default: the product's viewer_prefix)")
    ap.add_argument("--dry-run", action="store_true",
                    help="list what would be uploaded; upload nothing")
    ap.add_argument("--prune", action="store_true",
                    help="delete objects under the prefix that this build lacks")
    args = ap.parse_args()
    product = PRODUCTS[args.product]
    prefix = (args.prefix or product["viewer_prefix"]).strip("/")
    bucket = product["bucket"]

    if args.build:
        build(args.build, args.dist)
    rows = plan(args.dist)
    size = sum(p.stat().st_size for p, *_ in rows)
    print(f"{len(rows)} files, {size / 2**20:.1f} MB -> s3://{bucket}/{prefix}/")

    if args.dry_run:
        for _, rel, ctype, cache in rows:
            print(f"  {rel:55s} {ctype:28s} {cache}")
    else:
        upload(rows, bucket, prefix, args.prune)
        verify(bucket, prefix)

    print("\nViewer links:")
    for var, url in viewer_urls(product, prefix).items():
        print(f"  {var}: {url}")


if __name__ == "__main__":
    main()
