# Fusion build scripts

The station is the Autodesk Fusion design **Sporting El Soghra Station** (project *Eshera-Personal*, folder
*Alexandria Tram Station - Sporting El Soghra*). Unlike the tram models, **everything is scripted**: an empty
hybrid-intent design plus these scripts rebuilds the whole station from the user parameters.

## Structure
```
Sporting El Soghra Station (root)
├── Station Half:1          south half, at identity
│   ├── Pavilion             walls, windows, pilasters + consoles, cornice, platform-side piers, ribs, coffered
│   │                        eave, benches, doors, west canopy, hipped tile roof (roll tiles, hip/ridge caps)
│   ├── Platform             deck, grooved paving, tactile strip, copings, parapets, boundary wall
│   ├── Track                rails, fastenings, sleepers, ballast (one track)
│   ├── Embankment           fill, stone-pitched slope with rubble, pavement, kerb, carriageway strip
│   └── Stairs               double-return stair from the street to the platform
├── Station Half:2          the same component turned 180° about the vertical axis x = twin_cx between the tracks
│                           = the north pavilion, its platform, the other track and the north slope
└── Overhead Line            centre poles, cantilevers, contact wires
```
Each component holds one base feature with one solid body per material (body names = material classes, used by
`build_appearance.py`). A rebuild replaces the base feature, so the timeline does not grow.

Frame: X along the track (bearing ≈ 55°, + ENE, 0 = west end wall of the south pavilion), Y up from top of rail,
Z across (+ towards the south carriageway, 0 = street face of the south pavilion). API units are cm.

## Exec loader
The scripts are plain modules with a `run(context)` function, executed by a loader that passes `__file__` (the
scripts load their helpers from `lib/` and from each other by path, under unique module names, and never touch
`sys.path`). Run it from Fusion's *Scripts and Add-Ins* (as a one-off script), the Text Commands Python prompt or
any tool that executes Python inside Fusion (e.g. Fusion's MCP server):

```python
def run(_context: str):
    path = '<repo>/fusion/scripts/build_all.py'
    ns = {'__name__': 'fusion_script', '__file__': path}
    exec(compile(open(path).read(), path, 'exec'), ns)
    ns['run'](_context)
```

Every script activates the document **by name** (`Sporting El Soghra Station`) before touching anything.

## Build order
| # | Script | Builds |
|---|---|---|
| 1 | `build_params.py` | User parameters from `params.py` (missing ones; `run(ctx, force=True)` resets all) |
| 2 | `build_pavilion.py` | Component Pavilion (≈ 3 s) |
| 3 | `build_site.py` | Embankment, Track, Platform (≈ 25 s: rubble stones and tile joints) |
| 4 | `build_stairs.py` | Stairs |
| 5 | `build_twin.py` | Second occurrence of Station Half (north twin) |
| 6 | `build_ocs.py` | Overhead Line |
| 7 | `build_appearance.py` | Weathered appearances by body name |

`build_all.py` runs them in order (`run(ctx, steps=[...])` for a subset). Helpers: `snap.py` (viewport image with
an explicit camera, used for the renders and the photo overlay) and `save_doc.py` (save with a version message after
checking project and folder).

## Changing the model
Edit a user parameter in Fusion (*Modify → Change Parameters*) and re-run the scripts that use it (pavilion
dimensions → 2; levels, platform and track → 2–6). Each parameter comment gives the source and confidence; the
method behind each value is in [`../references/notes/dimensions.md`](../references/notes/dimensions.md).
