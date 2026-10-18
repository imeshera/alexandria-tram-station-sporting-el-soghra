# User parameters of the Sporting El Soghra station model: (name, expression, unit, comment).
# Comment = value source and confidence (HIGH / MED / LOW-MED / LOW / E = estimate). See
# references/notes/dimensions.md for the method behind each number. Heights named *_h are above the platform
# finished level (PFL) unless the comment says otherwise.
PARAMS = [
    # ---------------- site, track, platform ----------------
    ('gauge', '1435 mm', 'mm', 'Track gauge, standard - HIGH (published)'),
    ('rail_h', '142 mm', 'mm', 'Rail height (flat-bottom rail, ~49 kg/m class) - E'),
    ('track_ctr', '3400 mm', 'mm', 'Track centres (double track) - LOW (frames, Raml car 2.42 m wide)'),
    ('edge_off', '1380 mm', 'mm', 'Track centre to platform edge (car half-width 1.21 + gap) - LOW-MED'),
    ('plat_h', '350 mm', 'mm', 'PFL above top of rail - LOW-MED (frames O8mL t11m30-46: kerb ~2 rail heights)'),
    ('street_drop', '3400 mm', 'mm', 'PFL above the street pavement - LOW-MED (dossier v0 3.4 m; 20 risers of 170)'),
    ('plat_w', '3200 mm', 'mm', 'Pavilion platform-wall face to platform edge - LOW (frames, bench + 2 widths)'),
    ('plat_x0', '-30000 mm', 'mm', 'West end of the south platform (x) - LOW (frames: platform ~57 m, > 3-car set)'),
    ('plat_x1', '26000 mm', 'mm', 'East end of the south platform (x) - LOW (opposite the north pavilion is no platform)'),
    ('twin_cx', '25100 mm', 'mm', 'x of the vertical 180-deg symmetry axis that maps the south half onto the north '
                                  'twin (stagger) - LOW (frame O8mL t11m30 bearing, satellite)'),
    ('site_x0', '-40000 mm', 'mm', 'West end of the modelled embankment/track (x)'),
    ('slope_ang', '38 deg', 'deg', 'Street-side stone-pitched embankment slope - LOW-MED (owner photos)'),
    ('berm_drop', '900 mm', 'mm', 'Top of the slope (crest) below PFL = base of the street-side plinth - LOW-MED'),
    ('pave_w', '1800 mm', 'mm', 'Street pavement width at the toe of the slope - LOW-MED (kerb line in the IMG_3282 overlay)'),
    ('road_w', '7500 mm', 'mm', 'Carriageway width (context only) - LOW (satellite)'),
    ('para_h', '1000 mm', 'mm', 'Street-side platform parapet height above PFL - LOW-MED (frames)'),
    ('para_t', '300 mm', 'mm', 'Parapet thickness - LOW-MED'),
    ('para_pier', '2600 mm', 'mm', 'Parapet pier spacing - LOW (frames)'),
    ('tile', '300 mm', 'mm', 'Platform paving tile (cement tile, grooved) - MED (frames, tactile tiles)'),
    ('sleeper_pitch', '650 mm', 'mm', 'Sleeper spacing - E'),

    # ---------------- pavilion: plan ----------------
    ('n_bays', '3', '', 'Bays on each long side - HIGH (counted)'),
    ('bay', '7400 mm', 'mm', 'Bay pitch, pilaster centre to centre - MED-LOW (IMG_3281 bay 1 with brick scale; '
                             'satellite 25 m / 3.3). v0 dossier 7.5-8.6'),
    ('pil_w', '760 mm', 'mm', 'Street pilaster face width - LOW-MED'),
    ('pil_p', '130 mm', 'mm', 'Street pilaster projection from wall face - LOW'),
    ('pier_w', '900 mm', 'mm', 'Platform-side pier width - LOW-MED (frames t11m56)'),
    ('pier_p', '250 mm', 'mm', 'Platform-side pier projection - LOW-MED'),
    ('depth', '2700 mm', 'mm', 'Pavilion depth, street face to platform-wall face - LOW-MED (satellite roof 5 m = '
                             'depth + peave + ovh; canopy fit on IMG_3282 with the calibrated camera)'),
    ('wall_t', '450 mm', 'mm', 'Wall thickness (rendered brick) - E'),
    ('end_pad', '380 mm', 'mm', 'Building end beyond the outer pilaster centre (half pilaster) - LOW'),

    # ---------------- pavilion: heights above PFL ----------------
    ('plinth_h', '120 mm', 'mm', 'Plinth band top above PFL (platform side) - LOW-MED'),
    ('dado_h', '840 mm', 'mm', 'Brick dado: 12 courses x 70 mm - MED (counted IMG_3281)'),
    ('course', '70 mm', 'mm', 'Brick course (250x120x60 + 10 joint) - MED'),
    ('arch_w', '1440 mm', 'mm', 'Central arched light, clear width - LOW-MED (semicircle rise vs width, IMG_3281)'),
    ('arch_top', '3400 mm', 'mm', 'Central light, crown of the clear opening - LOW-MED'),
    ('side_w', '820 mm', 'mm', 'Side light clear width - LOW-MED'),
    ('side_top', '2770 mm', 'mm', 'Side light head - LOW-MED'),
    ('mull_w', '860 mm', 'mm', 'Pier between side light and arched light - LOW-MED (IMG_3281)'),
    ('frieze_h', '4550 mm', 'mm', 'Top of frieze = underside of main cornice - LOW-MED'),
    ('eave_h', '4950 mm', 'mm', 'Top of cornice = roof eaves line - LOW-MED (v0: 6.0-6.6 m above street-side base)'),
    ('cons_foot', '2900 mm', 'mm', 'Console (scroll bracket) foot = pilaster shaft top - LOW-MED'),
    ('cons_top', '5250 mm', 'mm', 'Console cap top (rises above the eaves) - LOW'),
    ('cons_p', '600 mm', 'mm', 'Console projection at the top - LOW'),
    ('cons_w', '480 mm', 'mm', 'Console width - LOW'),
    ('roof_pitch', '27 deg', 'deg', 'Roof pitch (Marseille / Roman tile) - LOW (E, from eave/ridge views)'),
    ('ovh', '450 mm', 'mm', 'Street-side and end eaves overhang (cornice) - LOW'),
    ('ceil_h', '4250 mm', 'mm', 'Interior ceiling - E'),

    # ---------------- platform side: eave / arcade ----------------
    ('peave', '1900 mm', 'mm', 'Platform eave projection beyond the platform-wall face - LOW (frames t11m46-52)'),
    ('soffit_h', '4250 mm', 'mm', 'Platform eave soffit - LOW'),
    ('rib_t', '400 mm', 'mm', 'Transverse arch rib thickness (along track) - LOW'),
    ('rib_spring', '2900 mm', 'mm', 'Rib springing on the pier face - LOW'),
    ('bench_l', '1800 mm', 'mm', 'Bench length - LOW-MED (frames)'),
    ('bench_d', '480 mm', 'mm', 'Bench seat depth - LOW-MED'),
    ('bench_h', '460 mm', 'mm', 'Bench seat height - MED'),

    # ---------------- west canopy and doors ----------------
    ('can_p', '1500 mm', 'mm', 'Canopy projection beyond the west end wall - LOW-MED (fit on IMG_3282: 1.2-1.4; '
                             'v0 guess 2.5-3)'),
    ('can_soffit', '4950 mm', 'mm', 'Canopy soffit, level with the main eaves - LOW-MED (IMG_3282 overlay: 0.7 m above '
                                   'the platform eave soffit; t11m46 canopy above the eave)'),
    ('can_fascia', '600 mm', 'mm', 'Canopy fascia depth - LOW'),
    ('can_chamf', '650 mm', 'mm', 'Canopy plan corner chamfer - LOW (frames: canted corners)'),
    ('door_w', '1250 mm', 'mm', 'End-wall arched doorway clear width - LOW (frame t11m46)'),
    ('door_top', '3150 mm', 'mm', 'End-wall doorway crown - LOW'),

    # ---------------- stairs (street side, west end) ----------------
    ('st_x', '-3100 mm', 'mm', 'Stair centre line (common foot) x - LOW (IMG_3277, IMG_3282 overlay)'),
    ('st_n1', '14', '', 'Risers, each lower flight (street to half landing) - LOW (IMG_3277: ~4 risers in 0.13 of '
                        'flight height)'),
    ('st_n2', '6', '', 'Risers, each upper return flight (half landing to PFL) - LOW'),
    ('st_tread', '230 mm', 'mm', 'Tread going - LOW (parapet pitch in the IMG_3282 overlay is steeper than 31 deg)'),
    ('st_w', '1500 mm', 'mm', 'Flight width between parapets - LOW (v0 1.5-2 m)'),
    ('st_para_t', '250 mm', 'mm', 'Stair parapet thickness - LOW-MED'),
    ('st_para_h', '900 mm', 'mm', 'Stair parapet height above the pitch line - LOW'),
]
