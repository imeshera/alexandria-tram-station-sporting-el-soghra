# Dimension sheet v1 — Sporting El Soghra station

Refines the v0 sheet of the research dossier (2026-10-17) with the daylight video frames of 2024 and 22 June 2026,
the satellite crop and a **camera-matched overlay** of the owner's photo IMG_3282 on the Fusion model.
Every value below is a Fusion user parameter (`fusion/scripts/params.py`); the parameter comment repeats the source
and confidence.

Confidence: **HIGH** published or counted; **MED** measured with a good scale anchor; **LOW-MED** measured with a
weak anchor or one method; **LOW** inferred from oblique views; **E** estimate (no direct evidence).

Frame: X along the track (bearing ≈ 55°, + towards ENE), Y up from top of rail (TOR), Z across (+ towards the south
carriageway). Heights of the pavilion are given above the platform finished level (PFL).

## 1. Which building is in which source (important correction)

The dossier assumed that the 2024 (RoMvXY75jS8) and 2026 (O8mL_pUMLRQ) platform videos show the platform side of
the pavilion in the owner's photos. They do not: they show its **twin on the north platform**.

| Evidence | South pavilion (owner photos) | North pavilion (both videos) |
|---|---|---|
| Street it faces | South carriageway, Sporting Club wall behind the camera (EXIF heading 18–25°, camera GPS on the south carriageway, satellite) | Residential street with shops ("Daily" market) and Italianate villas directly behind the parapet (O8mL t11m30–t11m46) |
| Across the tracks | Tall residential blocks behind the pavilion (north side of Omar Lotfi St) | Sporting Club grounds, palms and club building (RoMvXY t00m40), long grey club-side wall (O8mL t11m30) |
| Canopy end | West end (left in every owner photo; facade bearing 55°) | East end (the camera walks west towards it; far pavilion lies further west across the tracks) |

The far pavilion visible across the tracks in O8mL t11m30, t11m46 and t11m56 is the owner's south pavilion: same
tile-roofed eave, platform-side arcade and canopy massing, ~25–40 m further west. **The two pavilions are
point-symmetric twins on staggered side platforms**: each stands at the street edge of its platform, with the
canopy and the stair to the street at its outer end. The model therefore builds one half (south pavilion, its
platform, track, embankment and stairs) and places the north twin as the same component turned 180° about a
vertical axis between the tracks (`twin_cx`).

Consequence: the platform-side details (arcade ribs, coffered eave, benches, boarded lights, doors) come from the
north twin and are assumed identical on the south pavilion. Its street side is only seen at night, from the south.

## 2. Scale anchors and methods

| Anchor | Value | Use |
|---|---|---|
| Brick dado | 12 courses × 70 mm (250×120×60 + 10 joint) = 0.84 m, counted on IMG_3281 | Vertical scale of the street facade |
| Arched light | semicircular head: rise = half the width | Horizontal foreshortening on the oblique facade (0.44 at bay 1 of IMG_3281), which fixes the bay width independently of the vanishing point |
| Satellite (Esri z19, 0.255 m/px) | light block ≈ 25 × 5 m | Overall roof plan |
| Camera match (IMG_3282, 35 mm-eq, f = 4099 px, vertical FOV 52.4°) | Fusion camera at x −28.5, y −1.55, z +19.0 m, heading 24.8° true (EXIF) = 30.2° off the facade line, pitched up 4.3° | Overlay of the model on the photo: three bays, arched lights, pilasters, consoles and the stair parapets line up; canopy and pavement were refitted from it |
| Track gauge | 1435 mm | Platform-side frames |
| Raml single-deck car | 16.25 m × 2.42 m (alexandria-tram-raml-221-223) | Platform edge offset, track centres (frames RoMvXY t02m20, t08m10) |

## 3. Pavilion

| Dimension | Model | Method | Confidence |
|---|---|---|---|
| Bays per long side | 3 | counted | HIGH |
| Bay pitch (pilaster centres) | **7.40 m** | IMG_3281 bay 1: 990 crop px / 0.44 foreshortening × brick scale = 7.4 m; satellite 25 m / 3.3; confirmed by the IMG_3282 overlay | MED-LOW |
| Building length (end to end) | 22.96 m (+ 1.5 m canopy) | 3 × 7.40 + 2 × 0.38 | MED-LOW |
| Depth, street face to platform wall | **2.70 m** (v0: ≈ 5 m) | satellite roof 5.05 m = depth + platform eave 1.9 + street eave 0.45; canopy fit on IMG_3282; through-views in O8mL t11m52/t12m00 show the street-side window ~2 m behind the platform-side one | LOW-MED |
| Wall thickness | 0.45 m | rendered brick, reveal depth in frames | E |
| Street plinth bottom below PFL | 0.90 m | the street wall stands on the slope crest, below the platform floor | LOW-MED |
| Brick dado height | 0.84 m | 12 courses | MED |
| Window sill | PFL + 0.96 m | plinth 0.12 + dado 0.84 | MED-LOW |
| Arched central light (clear) | **1.44 × 2.44 m** (sill to crown), crown PFL + 3.40 | semicircle rise vs width; v0 1.45 × 3.3 measured from the street-side base | LOW-MED |
| Side lights (clear) | 0.82 × 1.81 m, head PFL + 2.77 | IMG_3281 | LOW-MED |
| Pier between side light and arch | 0.86 m (with a 0.20 m brick strip) | IMG_3281 | LOW-MED |
| Pilaster face / projection | 0.76 / 0.13 m, block rustication 0.26 m courses | IMG_3281 | LOW-MED / LOW |
| Console (scroll bracket) | foot PFL + 2.90, top PFL + 5.25, projection 0.60, width 0.48 m | IMG_3281, overlay | LOW |
| Frieze / cornice | cornice PFL + 4.55 → 4.95 (eaves), projection 0.45 m | overlay; v0 eaves 6.0–6.6 m above the street-side base (= 5.1–5.7 above PFL) | LOW-MED |
| Roof | hipped, 27°, Roman/Marseille rolls at 0.21 m, ridge ≈ PFL + 6.6 m | no view from above; v0 E | LOW |
| End doorways | 1.25 m wide, crown PFL + 3.15 | O8mL t11m46 (arched opening under the canopy) | LOW |

## 4. Platform side (from the north twin)

| Dimension | Model | Method | Confidence |
|---|---|---|---|
| Piers | 0.90 m wide, 0.25 m proud, block rustication, impost at PFL + 2.9 | t11m52, t11m56 | LOW-MED |
| Eave projection | 1.90 m beyond the platform wall | t11m46–t11m52 (bench + paving widths) | LOW |
| Eave soffit / fascia | soffit PFL + 4.25, fascia to 4.95 | t11m52 | LOW |
| Transverse arch ribs | 0.40 m thick, quarter-elliptic soffit from the pier impost to the eave front | t11m46, t11m52 ("arcade" seen along the platform) | LOW |
| Coffers | 2 per bay, two-step recess 6 + 6 cm | t11m52 (yellow recessed panels) | LOW |
| Benches | 1.80 × 0.48 m terrazzo slab with rounded ends, seat 0.46 m, on two pedestals | t11m52, t11m56 | LOW-MED |
| Door | middle bay: the arched light continues to the floor as a double door (green/boarded) | t12m00 caption "doors (green/boarded)"; position assumed | LOW |
| Boarded side lights | teal boards in the east side light of each bay | t11m56 | LOW |

## 5. West canopy

| Dimension | Model | Method | Confidence |
|---|---|---|---|
| Projection beyond the end wall | **1.50 m** (v0 2.5–3 m) | least-squares fit of the canopy's visible corners in the IMG_3282 overlay: 1.2–1.4 m | LOW-MED |
| Extent across | street eave line (+0.45) to the platform eave front (−4.60) | overlay fit (−4.6 to −4.8) and t11m30 | LOW-MED |
| Soffit / fascia | PFL + 4.25, fascia 0.60 m, coffered soffit (2 panels) | IMG_3281, t11m46 | LOW |
| Corners | chamfered 0.65 m on the outer corners | t11m46 | LOW |

## 6. Platform, track and embankment

| Dimension | Model | Method | Confidence |
|---|---|---|---|
| PFL above top of rail | 0.35 m | kerb ≈ 2.5 rail heights in t11m30–t11m46 | LOW-MED |
| PFL above the street pavement | 3.40 m | v0 (base 1.9 m above eye + 1.5 m) and 20 risers of 170 mm | LOW-MED |
| Platform wall to edge | 3.20 m (1.30 m beyond the eave front) | frames | LOW |
| Track centre to platform edge | 1.38 m | car half-width 1.21 + gap | LOW-MED |
| Track centres | 3.40 m | frames, car width | LOW |
| Platform length | 56 m (x −30 → +26), the north one mirrored | frames: platform continues beyond the pavilion; opposite the north pavilion there is no south platform (t11m30) | LOW |
| Stagger | symmetry axis at x = 25.1 m: north pavilion x ≈ 27.2 → 52.7 m | bearing of the far pavilion in t11m30 (~36 m ahead), satellite | LOW |
| Street slope | 38°, stone-pitched, crest at PFL − 0.90 | owner photos | LOW-MED |
| Pavement | 1.80 m | kerb line in the IMG_3282 overlay | LOW-MED |
| Parapets | 1.00 m high, 0.30 m thick, piers every 2.6 m | t11m30–t11m46 | LOW-MED |
| Paving | 300 mm grooved cement tiles, ribbed strip behind 450 mm copings | t11m46, t12m04 | MED |

## 7. Stairs

Seen only from the street, at night, and the steps are hidden by the parapets. Interpretation (IMG_3277, IMG_3281,
IMG_3282, IMG_3286):

- a common foot on the pavement just west of the canopy (`st_x` = −3.8 m);
- two lower flights rising **east and west** along the slope from that foot (the "\ /" parapets of IMG_3277), with
  the solid wall under the head landing (graffiti "طب") behind them;
- half landings at the ends; the east landing lies at the base of the street wall below bay 1, as in the photos;
- two upper return flights climbing back towards the centre between the platform parapet and a middle wall (the
  "0117170" parapet of IMG_3281 rising towards the canopy pier) to a head landing at PFL that opens onto the
  platform under the canopy.

**Risers:** visible step bands at the foot of the east flight in IMG_3277 measure ≈ 32 px at ≈ 17 m (f = 2811 px),
i.e. ≈ 0.19 m, and the flight spans ≈ 2.4 m of height → **14 risers per lower flight** and **6 per upper flight**,
20 × 170 mm = 3.40 m in all (v0: 20–21). Treads 280 mm, flights 1.50 m between 0.25 m parapets. Confidence LOW.

## 8. Measurements that would most improve the model

1. **Stairs:** count the risers of each flight, measure one riser and tread, and note where the flights turn
   (two minutes on site would replace the weakest part of the model).
2. **Building depth and canopy:** pace the west end wall (street face to platform face) and the canopy projection.
3. **Bay pitch and brick course:** tape one pilaster-to-pilaster bay and one 12-course dado.
4. **Eave height and roof:** one photo of the street facade square-on with a person against a pilaster; one view of
   the roof from a balcony on Arfy Pasha St.
5. **Stagger:** pace from the south pavilion's east end to the north pavilion's west end along the track.
6. Platform-side square-on shots of the **south** pavilion (doors, benches, coffers) to confirm the twin assumption.
