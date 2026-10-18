# Builds the root component "Overhead Line": centre poles between the tracks with twin cantilevers and one
# contact wire per track (context; positions and heights are estimates).
import math
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
build_site = _load('ses_build_site', 'build_site.py')

WIRE_H = 580.0       # contact wire above TOR (cm) - E (raised for the double-deck cars)
POLE_H = 820.0
SPAN = 3200.0


def run(_context: str):
    app, design = st.activate()
    p = st.Prm(design)
    g = build_site.geom(p)
    pp = st.Parts()
    zax, zT = g['zax'], g['zT']
    zT2 = 2 * zax - zT
    x0, x1 = g['x0'], g['x1']
    cx = p.twin_cx
    k = math.floor((cx - x0) / SPAN)
    xs = [cx + j * SPAN for j in range(-k, k + 1)]
    for x in xs:
        pp.cyl('OCS steel', (x, g['yb'], zax), (x, POLE_H, zax), 14, 10)
        pp.cyl('OCS steel', (x, g['yb'], zax), (x, g['yb'] + 40, zax), 22)
        for zt in (zT, zT2):
            pp.cyl('OCS steel', (x, WIRE_H + 70, zax), (x, WIRE_H + 70, zt), 3.5)
            pp.cyl('OCS steel', (x, WIRE_H + 160, zax), (x, WIRE_H + 72, zt + (zt - zax) * 0.1), 2.0)
            pp.cyl('OCS steel', (x, WIRE_H + 70, zt), (x, WIRE_H + 1, zt), 1.2)
            pp.cyl('OCS insulators', (x, WIRE_H + 70, zax + (zt - zax) * 0.15), (x, WIRE_H + 70, zax + (zt - zax) * 0.30), 5)
    for zt in (zT, zT2):
        pp.cyl('Contact wire', (x0, WIRE_H, zt), (x1, WIRE_H, zt), 0.6)
    n = pp.commit(st.comp(design.rootComponent, 'Overhead Line'), 'Overhead line geometry')
    print('OCS', n, 'bodies,', len(xs), 'poles')
