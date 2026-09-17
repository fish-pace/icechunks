# The gridlook viewers

One `publish_viewer.py` builds gridlook once and publishes a copy beside each store. The
store lives in the URL *fragment*, which the host never sees, so a single build serves any
store. `PRODUCTS` is the only place a viewer is configured.

| Viewer | Prefix | Renders? |
|---|---|---|
| GOBAI-O2 | `fish-pace/gobai-o2/viewer/` | yes — Eli confirmed in a browser |
| OA indicators | `ocean-icechunks/oa-indicators/viewer/` | yes, transport verified; rendering unconfirmed |
| CoastWatch OHC | `ocean-icechunks/noaa-ohc/viewer/` | metadata only — see CORS below |

## CORS is the thing that decides whether a virtual store draws

A **materialized** store needs CORS on one host. A **virtual** store needs it on two,
because metadata comes from the repository and data from wherever the referenced bytes
live. That single difference explains every viewer above:

- `data.source.coop` — `access-control-allow-origin: *`, `Range` honoured, on GET and
  preflight. Never the problem.
- `www.ncei.noaa.gov` — sends `Access-Control-Allow-Origin: *` on ranged GETs. So the OA
  viewer draws. A plain `Range: bytes=a-b` is CORS-safelisted, so no preflight is involved.
- `coastwatch.noaa.gov` — serves ranged GETs (206, `Accept-Ranges: bytes`) and sends **no**
  `Access-Control-Allow-Origin`, on the GET or the preflight. The OHC viewer therefore loads
  metadata and coordinates, which are real chunks in the repo, and the browser blocks every
  science array.

Enforcement is in the browser, not the page, so nothing published can waive it — a CORS
extension is a local override that cannot be shipped. The OHC viewer is published anyway at
Eli's call: it renders for anyone running such an extension, and is in place for the day
CoastWatch sends the header (one Apache directive, no rebuild — the manifests do not change).
The alternative, proxying the source and rebuilding every store against the proxy prefix,
means re-serving NOAA bytes through infrastructure we would have to run.

## Link the repository root, not a group

`…/noaa-ohc/na/` is the whole link. gridlook's `splitIcechunkStoreAndGroup` walks a URL back
segment by segment until one opens as a repository root, then offers the groups
(`daily`/`14day_v1`/`14day`) and their variables as dropdowns. Naming a group or a `varname`
only freezes a choice the viewer already presents — which is why OHC has three links and not
thirty-six.

CLAUDE.md used to claim the opposite, that groups meant a link needed more than a store URL.
That was wrong and is corrected; do not re-derive it.

`variables` in `PRODUCTS` is therefore optional. `gobai-o2` sets it because its README offers
a link per variable; `noaa-ohc` does not.

## The catalog is `catalog-extended.json`, and it goes in the build output

`HashGlobeView.vue` sets `DEFAULT_CATALOG = "static/catalog-extended.json"`.
`static/catalog.json` is **never read** unless a link passes `::catalog=<url>` — editing it
changes nothing on screen.

gridlook ships 70 unrelated demo datasets in the extended file, so `write_catalog` in
`publish_viewer.py` writes a product-specific replacement **into the dist** at publish time,
driven by the `catalog` key in `PRODUCTS`. Never into the gridlook checkout: that would bake
one product's catalog into every other product's viewer and stamp the build
`gridlook_dirty`, leaving the published copy matching no commit. A catalog entry's `url`
becomes the location hash verbatim, so it carries the camera with it.

## Camera state

`px`, `py`, `alt`, `lat`, `lon` and `dimIndices_<dim>` ride in the same fragment — see
`STORE_PARAM_MAPPING` in gridlook's `paramStore.ts`. Stores covering different parts of the
globe need different centres; `_OHC_BASINS` holds the three CoastWatch ones.

Dragging the globe rewrites the address bar, so **a good opening view is obtained by
positioning and copying, not by computing one.** `alt` especially: `95910936` frames a basin
100° wide in longitude, and nothing here can check what a wider one needs.

## Other gridlook facts worth keeping

- **No time dimension is required**, but every time path is gated on a dim literally named
  `time`. Spatial dims must be the trailing two, and `dimension_names` must be in the Zarr
  metadata. It ranks the coordinate name `lat` above `latitude`, which is why the OA store
  uses the short spelling.
- **Build with `vite build --sourcemap false` and a capped heap.** `npm run build` adds
  `vue-tsc` and source maps and gets OOM-killed on a small machine.
- **README nav rows are plain markdown links, not centered HTML.** GitHub allows
  `<p align="center">`, but Source Cooperative renders the README through its own pipeline
  and serves the raw file as plain text, so HTML is a gamble in two places out of three.
- Source Cooperative's static-hosting behaviour — content types never inferred, no directory
  index, the edge 403ing `Python-urllib` — is in CLAUDE.md under "The browser viewer".
