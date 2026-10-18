# Build log: Sporting El Soghra station

Decisions, measurements and Fusion API gotchas, in the order they happened.

## 2026-10-17 — Research review and the twin
- Inputs: the research dossier (identification, history, status, v0 dimensions), the owner's nine night photos of
  the street side (22 Jan 2026), a satellite crop and video frames of 2024 (RoMvXY75jS8) and 22 June 2026
  (O8mL_pUMLRQ). Approach and code style follow the Raml tram repositories.
- **The platform videos show the north twin, not the photographed pavilion.** Across the tracks in the videos lie
  the Sporting Club grounds; behind the parapet, residential buildings with shops; the camera walks west towards
  an end canopy; and the owner's pavilion appears across the tracks further west (O8mL t11m30/46/56). The
  station has two point-symmetric pavilions on staggered side platforms, each with its canopy and street stair at
  its outer end. Details in `references/notes/dimensions.md` §1.
- Consequence for the model: build one half and instance it turned 180° about a vertical axis between the tracks.
  Platform-side details come from the north twin and are applied to both.
- Platform side, read from the frames: rusticated piers; transverse arch ribs with quarter-elliptic soffits from
  the pier impost to the eave front (the "arcade" seen along the platform); a deep eave with a two-step coffered
  soffit and stepped corbels at each rib head; tripartite windows as on the street side; terrazzo benches with
  rounded ends; a teal-boarded light per bay; green doors. The end walls under the canopies have arched doorways.
- Stairs (night photos only): a double-return stair — common foot on the pavement, lower flights rising east and
  west along the slope, half landings, upper flights returning to a head landing at platform level under the
  canopy. 14 + 6 risers of 170 mm (riser bands in IMG_3277 at the foot of the east flight).

## 2026-10-17 — Fusion setup
- Document **Sporting El Soghra Station** in *Eshera-Personal / Alexandria Tram Station - Sporting El Soghra*:
  new document, `designIntent = HybridDesignIntentType`, mm display units, saved with `saveAs` into the folder.
  Another agent drives Fusion at the same time, so every script activates the document by name, and saves check
  project and folder first (`save_doc.py`).
- Fully scripted, unlike the tram models: geometry is built with `TemporaryBRepManager` (boxes, oriented boxes,
  cylinders, elliptical cylinders, tori, convex prisms as boxes cut by half-space boxes) and committed in one base
  feature per component, one body per material. A rebuild replaces the base feature, so the timeline stays short
  and rebuilds are fast (pavilion ≈ 3–7 s, site ≈ 25–33 s, mostly the rubble stones and tile joints).
- Mouldings: a profile is a list of rectangles and convex/concave quarter rounds in (projection, height); runs are
  extruded per wall face and external corners are the **intersection** of the two runs extended into the corner
  square, which gives true mitres.
- Hipped roofs: a box cut by one inclined half-space box per roof plane. Roll tiles: one cylinder per roll down
  each plane, the union trimmed by the same roof raised by 1.6 roll radii (so rolls stop cleanly at hips and
  ridge), plus hip and ridge cappings.
- Brick dado panels: the panel with sunk bed joints and staggered perpends is built once per size at the origin
  and copied (`tbm.copy` + transform) to every position; the platform side uses a 180° rotation about Y (a mirror
  matrix would invert the body).

### Fusion API gotchas
- **Module-name clashes with other scripts in the same Fusion session.** The first version put the scripts folder
  on `sys.path` and imported `params` and `lib.stlib`; a concurrent session had its own `params` module cached and
  the import silently returned the wrong one. All scripts now load siblings by path with
  `importlib.util.spec_from_file_location` under unique names (`ses_stlib`, `ses_params`, ...) and never touch
  `sys.path`.
- `OrientedBoundingBox3D.create` rejects a width direction that is not exactly perpendicular to the length
  direction ("invalid argument widthDirection"); `Parts.OB` re-orthogonalises it.
- Long MCP calls time out (a full rebuild + appearance pass, or a save) but finish in Fusion. Wait, then verify
  read-only before re-running.
- The first `Viewport.saveAsImageFile` after a camera change can come back nearly empty; capture twice.
- `Camera.perspectiveAngle` is the **vertical** field of view for a portrait image: 0.914 rad reproduced the
  35 mm-equivalent iPhone crop (f = 4099 px on 4032 px height) exactly.

## 2026-10-17 — Camera-matched overlay and pass 1b
- IMG_3282 (35 mm-eq crop of the main camera) matched with a Fusion camera at x −28.5, y −1.55, z +19.0 m
  (eye 1.5 m above the far pavement), heading 24.8° true from EXIF (30.2° off the facade line), pitched up 4.3°,
  vertical FOV 0.914 rad. Render and photo blended with ffmpeg (`blend=all_mode=average`).
- With bay 7.40 m, arched light 1.44 m and the brick-course vertical scale, the three bays, arched lights,
  pilasters, consoles and the cornice line up with the photo. This confirms the bay pitch (v0 range 7.5–8.6 m).
- The overlay showed the v0 canopy (2.8 m projection, soffit at the platform-eave level) far too big and too low.
  A least-squares fit of the canopy corners gave 1.2–1.4 m projection and a cross extent reaching the platform
  eave front at z ≈ −4.6 to −4.8 m. Together with the satellite roof depth (≈ 5 m) this gives a building depth
  of **2.70 m** (v0 ≈ 5 m) with a 1.90 m platform eave. Canopy now 1.50 m, soffit at the eaves line (4.95 m above
  PFL), its own four-sided hipped roof.
- The overlay also put the kerb ~1 m closer (pavement 1.8 m) and showed the stair parapets steeper than 31°: tread
  230 mm, foot moved to x = −3.1 m. The lower-flight parapet now coincides with the photo.

## Open questions
- Building depth, canopy projection and stair geometry rest on one night photo and the satellite block; a tape
  measure on site would settle them (`references/notes/dimensions.md` §8).
- Stagger of the two pavilions (symmetry axis x = 25.1 m) is from one bearing in a video frame.
- Interior (none seen): an open waiting hall with a flat ceiling at 4.25 m is assumed.
