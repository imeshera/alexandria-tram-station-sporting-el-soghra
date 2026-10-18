# Assigns weathered appearances by body name in every component (fast; re-run after any rebuild).
# Colours sampled from the 2024-26 daylight frames and the owner's night photos, slightly desaturated.
import os, importlib.util
import adsk.core, adsk.fusion
HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, rel):
    """Load a sibling module by path under a unique name (no sys.path changes: other Fusion sessions/scripts may
    have modules with the same names)."""
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


st = _load('ses_stlib', 'lib/stlib.py')

MATTE = 'Plastic - Matte (White)'
# appearance name: (library base, RGB)
LOOKS = {
    'SES Render (cream, weathered)': (MATTE, (212, 197, 165)),
    'SES Stone trim (weathered)': (MATTE, (224, 217, 199)),
    'SES Rustication (grey-white)': (MATTE, (205, 202, 192)),
    'SES Brick (red, weathered)': (MATTE, (146, 84, 70)),
    'SES Plinth (pink render)': (MATTE, (204, 158, 138)),
    'SES Roof tile (terracotta)': (MATTE, (176, 90, 60)),
    'SES Joinery (faded paint)': (MATTE, (170, 164, 150)),
    'SES Ironwork': ('Iron - Cast', (48, 44, 42)),
    'SES Glass (grey, dulled)': ('Glass (Grey)', None),
    'SES Terrazzo (red-brown)': (MATTE, (138, 80, 68)),
    'SES Door (green paint)': (MATTE, (72, 94, 80)),
    'SES Boarding (teal)': (MATTE, (96, 158, 148)),
    'SES Sign (white)': (MATTE, (234, 233, 228)),
    'SES Concrete (stained)': (MATTE, (186, 179, 166)),
    'SES Step tiles': (MATTE, (112, 76, 64)),
    'SES Earth': (MATTE, (128, 112, 90)),
    'SES Stone pitching': (MATTE, (112, 104, 92)),
    'SES Rubble': (MATTE, (172, 164, 148)),
    'SES Pavement': (MATTE, (170, 164, 154)),
    'SES Kerb': (MATTE, (160, 158, 152)),
    'SES Asphalt': (MATTE, (66, 66, 68)),
    'SES Rail (rusty)': ('Steel - Rough', (112, 84, 66)),
    'SES Sleeper': (MATTE, (150, 146, 138)),
    'SES Fastening': ('Steel - Rough', (70, 62, 56)),
    'SES Ballast': (MATTE, (118, 110, 98)),
    'SES Paving (cement tile)': (MATTE, (198, 190, 174)),
    'SES Coping': (MATTE, (176, 172, 164)),
    'SES OCS steel': ('Steel - Galvanized (Small)', None),
    'SES Insulator': (MATTE, (120, 70, 50)),
    'SES Copper wire': ('Copper - Patina', None),
}
BODY = {
    'Render': 'SES Render (cream, weathered)', 'Stone trim': 'SES Stone trim (weathered)',
    'Rustication': 'SES Rustication (grey-white)', 'Brick': 'SES Brick (red, weathered)',
    'Plinth': 'SES Plinth (pink render)', 'Roof tiles': 'SES Roof tile (terracotta)',
    'Window joinery': 'SES Joinery (faded paint)', 'Ironwork': 'SES Ironwork', 'Glass': 'SES Glass (grey, dulled)',
    'Bench': 'SES Terrazzo (red-brown)', 'Doors': 'SES Door (green paint)', 'Boarding': 'SES Boarding (teal)',
    'Signboards': 'SES Sign (white)', 'Concrete': 'SES Concrete (stained)', 'Stair parapets': 'SES Concrete (stained)',
    'Step tiles': 'SES Step tiles', 'Earth fill': 'SES Earth', 'Stone pitching': 'SES Stone pitching',
    'Rubble stones': 'SES Rubble', 'Pavement': 'SES Pavement', 'Kerb': 'SES Kerb', 'Asphalt': 'SES Asphalt',
    'Rails': 'SES Rail (rusty)', 'Sleepers': 'SES Sleeper', 'Rail fastenings': 'SES Fastening',
    'Ballast': 'SES Ballast', 'Platform structure': 'SES Concrete (stained)', 'Paving': 'SES Paving (cement tile)',
    'Copings': 'SES Coping', 'Parapets': 'SES Render (cream, weathered)', 'Parapet coping': 'SES Stone trim (weathered)',
    'Boundary wall': 'SES Concrete (stained)', 'OCS steel': 'SES OCS steel', 'OCS insulators': 'SES Insulator',
    'Contact wire': 'SES Copper wire',
}


def looks(app, design):
    lib = app.materialLibraries.itemByName('Fusion Appearance Library')
    out = {}
    for n, (b, rgb) in LOOKS.items():
        a = design.appearances.itemByName(n)
        if a is None:
            a = design.appearances.addByCopy(lib.appearances.itemByName(b), n)
        if rgb:
            for i in range(a.appearanceProperties.count):
                pr = a.appearanceProperties.item(i)
                if isinstance(pr, adsk.core.ColorProperty) and any(k in pr.id.lower() for k in ('color', 'albedo', 'diffuse')):
                    try:
                        pr.value = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
                    except Exception:
                        pass
        out[n] = a
    return out


def run(_context: str):
    app, design = st.activate()
    A = looks(app, design)
    n = miss = 0
    for c in design.allComponents:
        for b in c.bRepBodies:
            key = BODY.get(st.base(b.name))
            if key:
                b.appearance = A[key]
                n += 1
            else:
                miss += 1
                print('no look for', c.name, b.name)
    print('appearances set on %d bodies (%d unmatched)' % (n, miss))
