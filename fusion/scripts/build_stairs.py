# Builds the component "Stairs" inside "Station Half": the double-return concrete staircase from the street
# pavement to the platform at the west end of the pavilion (owner photos IMG_3277 / 3281 / 3282 / 3286).
#   - a common foot on the pavement at x = st_x;
#   - two lower flights rising east and west along the embankment (st_n1 risers each) to half landings;
#   - two upper return flights (st_n2 risers each) climbing back towards the centre to a head landing at PFL,
#     which opens onto the platform under the west canopy;
#   - sloping concrete parapets with newels, tiled treads and risers with nosings.
# Interpretation and riser count: LOW confidence (see references/notes/dimensions.md, section Stairs).
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

CONC, TREAD, PARA = 'Concrete', 'Step tiles', 'Stair parapets'


def run(_context: str):
    app, design = st.activate()
    p = st.Prm(design)
    half = st.comp(design.rootComponent, 'Station Half')
    g = build_site.geom(p)
    pp = st.Parts()
    build(pp, p, g)
    n = pp.commit(st.comp(half, 'Stairs'), 'Stairs geometry')
    print('Stairs', n, 'bodies; riser %.1f cm, %d + %d risers' % (g['rh'], p.st_n1, p.st_n2))


def flight(pp, x_start, direction, n, y0, rh, tread, za, zb, ybase):
    """n risers starting at x_start (bottom nosing line) going `direction` (+1/-1), first tread at y0 + rh."""
    out = []
    for k in range(n):
        xa = x_start + direction * k * tread
        xb = x_start + direction * (k + 1) * tread
        yt = y0 + (k + 1) * rh
        if k == n - 1:
            xb = xa + direction * tread          # last riser lands on the landing
        out.append(pp.B(xa, xb, ybase, yt - 2.5, za, zb))
        pp.box(TREAD, xa - direction * 2.5, xb, yt - 2.5, yt, za, zb)                    # tread tile + nosing
        pp.box(TREAD, xa - direction * 0.0, xa + direction * 2.0, yt - rh, yt - 2.5, za, zb)   # riser tile
    return out


def sloped_parapet(pp, xa, ya, xb, yb_, ph, za, zb, ybase):
    """Parapet whose top follows the pitch line from (xa, ya) to (xb, yb_), raised by ph."""
    if xa > xb:
        xa, xb, ya, yb_ = xb, xa, yb_, ya
    pts = [(xa, ybase), (xb, ybase), (xb, yb_ + ph), (xa, ya + ph)]
    body = pp.prism(pts, 'z', za, zb)
    pp.add(PARA, body)
    # coping strip on top
    t = math.atan2(yb_ - ya, xb - xa)
    Lc = math.hypot(xb - xa, yb_ - ya)
    c = ((xa + xb) / 2, (ya + yb_) / 2 + ph + 2.5 / math.cos(t), (za + zb) / 2)
    pp.add(PARA, pp.OB(c, (math.cos(t), math.sin(t), 0), (-math.sin(t), math.cos(t), 0), Lc, 5, (zb - za) + 6))
    return body


def build(pp, p, g):
    yst, yP, rh = g['yst'], g['yP'], g['rh']
    tr, w, pt, ph = p.st_tread, p.st_w, p.st_para_t, p.st_para_h
    n1, n2 = p.i('st_n1'), p.i('st_n2')
    xs, fl = p.st_x, g['fl']
    zc = g['zcrest']                              # platform parapet outer face
    # z bands (street = +z): upper flights next to the platform, then a middle wall, then the lower flights
    zu0, zu1 = zc + pt, zc + pt + w
    zm0, zm1 = zu1, zu1 + pt
    zl0, zl1 = zm1, zm1 + w
    zo0, zo1 = zl1, zl1 + pt
    y1 = yst + n1 * rh                            # half landing level
    base = yst - 30
    mass = []
    # foot landing (one shallow step up from the pavement is the first riser of each flight)
    mass.append(pp.B(xs - fl / 2, xs + fl / 2, base, yst + 1, zl0, zo1))
    # lower flights
    mass += flight(pp, xs + fl / 2, 1, n1, yst, rh, tr, zl0, zl1, base)
    mass += flight(pp, xs - fl / 2, -1, n1, yst, rh, tr, zl0, zl1, base)
    xLE0, xLE1 = g['xLE0'], g['xLE0'] + fl
    xLW1, xLW0 = g['xLW1'], g['xLW1'] - fl
    # half landings (full depth of both bands)
    for a, b in ((xLE0, xLE1), (xLW0, xLW1)):
        mass.append(pp.B(a, b, base, y1 - 2.5, zu0 - pt, zo1))
        pp.box(TREAD, a, b, y1 - 2.5, y1, zu0, zl1)
    # upper return flights (towards the centre) to the head landing
    mass += flight(pp, xLE0, -1, n2, y1, rh, tr, zu0, zu1, base)
    mass += flight(pp, xLW1, 1, n2, y1, rh, tr, zu0, zu1, base)
    xh0, xh1 = g['xHL0'], g['xHL1']
    mass.append(pp.B(xh0, xh1, base, yP - 3, zu0 - pt, zu1))
    pp.box(TREAD, xh0, xh1, yP - 3, yP, zu0 - pt, zu1)
    # solid mass behind the lower flights (under the upper flights / head landing) and the middle wall
    mass.append(pp.B(xLW0, xLE1, base, y1 - 2.5, zu0 - pt, zm1))
    pp.add(CONC, pp.merge(mass))

    # parapets
    # outer parapet of the lower flights (z zo0..zo1), sloped, with newels at the foot
    for d in (1, -1):
        xa = xs + d * fl / 2
        xb = xa + d * n1 * tr
        sloped_parapet(pp, xa, yst, xb, y1, ph, zo0, zo1, base)
        pp.box(PARA, xa - 18, xa + 18, base, yst + ph + 25, zo0 - 3, zo1 + 3)   # newel
        pp.box(PARA, xa - 21, xa + 21, yst + ph + 25, yst + ph + 31, zo0 - 6, zo1 + 6)
    # landing outer parapets (street side and the ends)
    for a, b, e in ((xLE0, xLE1, xLE1), (xLW0, xLW1, xLW0)):
        pp.box(PARA, a, b, base, y1 + ph, zo0, zo1)
        ea, eb = (e, e + pt) if e == xLE1 else (e - pt, e)
        pp.box(PARA, ea, eb, base, y1 + ph, zu0 - pt, zo1)
        pp.box(PARA, min(ea, a) - 3, max(eb, b) + 3, y1 + ph, y1 + ph + 6, zo0 - 3, zo1 + 3)
    # middle wall: between the lower flights and the upper flights / head landing
    pp.box(PARA, xLW0, xLE1, base, y1 + ph, zm0, zm1)
    top = pp.prism([(xLE0, y1 + ph), (xh1, yP + ph), (xh0, yP + ph), (xLW1, y1 + ph)], 'z', zm0, zm1)
    pp.add(PARA, top)
    pp.box(PARA, xh0, xh1, yP + ph, yP + ph + 6, zm0 - 3, zm1 + 3)
