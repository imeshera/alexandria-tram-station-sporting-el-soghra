# Builds the component "Pavilion" (inside "Station Half"): the Italianate station pavilion of the south platform.
# Street (south, +z) facade: rusticated pilasters with scroll consoles, tripartite windows (arched central light with
# archivolt and keystone, narrow side lights under hood cornices), brick dado panels, pink plinth, cornice.
# Platform (north, -z) side: rusticated piers, the same tripartite windows, transverse arch ribs carrying a deep
# eave with a coffered soffit, benches. West end: tile-roofed canopy with chamfered corners and coffered soffit,
# arched doorways in both end walls. Hipped Marseille/Roman-tile roof with roll tiles, hip and ridge cappings.
# Frame and units: see lib/stlib.py. Re-run after any parameter change.
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

RENDER, TRIM, RUST, BRICK, PLINTH = 'Render', 'Stone trim', 'Rustication', 'Brick', 'Plinth'
TILE, TIMBER, IRON, GLASS, BENCH, DOOR, SIGN, BOARD = ('Roof tiles', 'Window joinery', 'Ironwork', 'Glass',
                                                     'Bench', 'Doors', 'Signboards', 'Boarding')

CORNICE = [('r', 0, 8, 0, 12), ('q', 8, 20, 8, 1, -1), ('r', 0, 8, 12, 20), ('r', 0, 38, 20, 31),
           ('r', 0, 42, 31, 35), ('r', 0, 45, 35, 40)]
FASCIA = [('r', 0, 5, 0, 6), ('r', 0, 3, 6, 52), ('r', 0, 10, 52, 58), ('q', 10, 58, 5, 1, 1), ('r', 0, 10, 58, 63),
          ('r', 0, 16, 63, 70)]
HOOD = [('r', 0, 3, 0, 10), ('r', 0, 7, 10, 14), ('q', 7, 14, 6, 1, 1), ('r', 0, 7, 14, 20), ('r', 0, 15, 20, 25),
        ('r', 0, 17, 25, 28)]


def run(_context: str):
    app, design = st.activate()
    p = st.Prm(design)
    root = design.rootComponent
    half = st.comp(root, 'Station Half')
    pav = st.comp(half, 'Pavilion')
    pp = st.Parts()
    build(pp, p)
    n = pp.commit(pav, 'Pavilion geometry')
    print('Pavilion: %d bodies' % n)


def build(pp, p):
    _PANELS.clear()
    yP = p.plat_h
    nb = p.i('n_bays')
    bay, epad = p.bay, p.end_pad
    L = 2 * epad + nb * bay
    D, wt = p.depth, p.wall_t
    zN = -D                                  # platform-wall face
    zE = -(D + p.peave)                      # platform eave front
    yb = yP - p.berm_drop                    # street-side base
    xs = [epad + k * bay for k in range(nb + 1)]   # pilaster / pier centres
    xc = [epad + (k + 0.5) * bay for k in range(nb)]
    aw, sw, mw = p.arch_w, p.side_w, p.mull_w
    sill = yP + p.plinth_h + p.dado_h
    spring = yP + p.arch_top - aw / 2
    stop = yP + p.side_top
    off = aw / 2 + mw + sw / 2               # side light centre offset

    # ------------------------------------------------------------------ walls
    walls = [pp.B(0, L, yb, yP + p.eave_h, -wt, 0),                 # street wall (down to the slope crest)
             pp.B(0, L, yP - 60, yP + p.soffit_h, zN, zN + wt),     # platform wall
             pp.B(0, wt, yP - 60, yP + p.eave_h, zN, 0),            # west end wall
             pp.B(L - wt, L, yP - 60, yP + p.eave_h, zN, 0),        # east end wall
             pp.B(0, L, yP + p.ceil_h, yP + p.eave_h, zN, 0),       # ceiling slab / roof plate
             pp.B(0, L, yP - 60, yP, zN, 0)]                        # floor slab
    wall = pp.merge(walls)

    # openings (both long walls)
    for x in xc:
        for z0, z1 in ((-wt - 1, 1), (zN - 1, zN + wt + 1)):
            pp.cut(wall, pp.B(x - aw / 2, x + aw / 2, sill, spring, z0, z1))
            pp.cut(wall, pp.C((x, spring, z0), (x, spring, z1), aw / 2))
            for sx in (-1, 1):
                c = x + sx * off
                pp.cut(wall, pp.B(c - sw / 2, c + sw / 2, sill, stop, z0, z1))
    # platform-side door in the middle bay (central light taken down to the floor) - LOW
    xm = xc[nb // 2]
    pp.cut(wall, pp.B(xm - aw / 2, xm + aw / 2, yP, sill + 1, zN - 1, zN + wt + 1))
    # end-wall doorways
    dw = p.door_w
    dspring = yP + p.door_top - dw / 2
    zc = -D / 2
    for x0, x1 in ((-1, wt + 1), (L - wt - 1, L + 1)):
        pp.cut(wall, pp.B(x0, x1, yP, dspring, zc - dw / 2, zc + dw / 2))
        pp.cut(wall, pp.C((x0, dspring, zc), (x1, dspring, zc), dw / 2))
    pp.add(RENDER, wall)

    # brick dado recesses are cut into the render on both faces, then filled with brick bodies
    for s, zface in ((1, 0.0), (-1, zN)):
        face(pp, p, s, zface, xc, sill, spring, stop, off, wall, yP, xm)

    # ------------------------------------------------------------------ street plinth, pilasters, consoles
    pp.box(PLINTH, -2, L + 2, yb, yP + p.plinth_h, -wt, 5)                   # pink plinth band, 5 cm proud
    pp.box(TRIM, -2, L + 2, yP + p.plinth_h, yP + p.plinth_h + 3, -wt, 7)        # weathering fillet
    for k, x in enumerate(xs):
        pilaster(pp, p, x, k, nb, L, yb, yP)
        console(pp, p, x, yP)
    # end-wall corner quoins on the two street corners are part of pilaster(); end faces get a plinth too
    for x0, x1 in ((-5, 0), (L, L + 5)):
        pp.box(PLINTH, x0, x1, yP - 60, yP + p.plinth_h, zN, 0)

    # ------------------------------------------------------------------ main cornice (street + ends)
    st.ring_moulding(pp, TRIM, CORNICE, yP + p.frieze_h, 0, L, zN, 0, sides='SWE')
    # frieze band under the cornice
    pp.box(TRIM, -2, L + 2, yP + p.frieze_h - 18, yP + p.frieze_h, -wt, 2)

    # ------------------------------------------------------------------ platform side: piers, ribs, eave
    zP = zN - p.pier_p
    for k, x in enumerate(xs):
        x0, x1 = max(0, x - p.pier_w / 2), min(L, x + p.pier_w / 2)
        pp.box(RENDER, x0, x1, yP, yP + p.rib_spring, zP, zN)
        rusticate(pp, x0, x1, yP + p.plinth_h, yP + p.rib_spring - 16, 'N', zP, 3.0, 22)
        pp.box(TRIM, x0 - 4, x1 + 4, yP + p.rib_spring - 16, yP + p.rib_spring, zP - 8, zN)    # impost
        pp.box(PLINTH, x0 - 2, x1 + 2, yP, yP + p.plinth_h, zP - 3, zN)                       # pier base
        # transverse arch rib: rectangle minus quarter ellipse centred at the eave front / springing
        r0, r1 = x - p.rib_t / 2, x + p.rib_t / 2
        if k == 0:
            r0, r1 = 0, p.rib_t
        if k == nb:
            r0, r1 = L - p.rib_t, L
        rib = pp.B(r0, r1, yP + p.rib_spring, yP + p.soffit_h + 1, zE, zP)
        a = (zP - zE)
        b = p.soffit_h - p.rib_spring
        el = pp.EC((r0 - 1, yP + p.rib_spring, zE), (r1 + 1, yP + p.rib_spring, zE),
                   max(a, b), min(a, b), (0, 0, 1) if a >= b else (0, 1, 0))
        pp.cut(rib, el)
        pp.add(RENDER, rib)
        # archivolt-like edge band on the rib soffit: a thin projecting band following the curve
        band = pp.EC((r0 - 3, yP + p.rib_spring, zE), (r1 + 3, yP + p.rib_spring, zE),
                     max(a, b), min(a, b), (0, 0, 1) if a >= b else (0, 1, 0))
        inner = pp.EC((r0 - 4, yP + p.rib_spring, zE), (r1 + 4, yP + p.rib_spring, zE),
                      max(a, b) - 7, min(a, b) - 7, (0, 0, 1) if a >= b else (0, 1, 0))
        pp.cut(band, inner)
        pp.isect(band, pp.B(r0 - 3, r1 + 3, yP + p.rib_spring, yP + p.soffit_h, zE, zP))
        pp.add(TRIM, band)
        # stepped corbels under the soffit at the rib head (three steps)
        for j in range(3):
            w = p.rib_t / 2 + 12 + 10 * j
            pp.box(TRIM, max(-0.0, x - w) if k else 0, min(L, x + w) if k < nb else L,
                   yP + p.soffit_h - 30 + 10 * j, yP + p.soffit_h - 20 + 10 * j, zE + 4, zE + 60 - 12 * j)
    # eave slab with coffers
    eave = pp.B(0, L, yP + p.soffit_h, yP + p.eave_h, zE, zN)
    for k in range(nb):
        x0 = xs[k] + p.rib_t / 2 + 25
        x1 = xs[k + 1] - p.rib_t / 2 - 25
        n_c = 2
        w = (x1 - x0 - 20 * (n_c - 1)) / n_c
        for j in range(n_c):
            a0 = x0 + j * (w + 20)
            pp.cut(eave, pp.B(a0, a0 + w, yP + p.soffit_h - 1, yP + p.soffit_h + 6, zE + 25, zN - 25))
            pp.cut(eave, pp.B(a0 + 10, a0 + w - 10, yP + p.soffit_h - 1, yP + p.soffit_h + 12, zE + 35, zN - 35))
    pp.add(RENDER, eave)
    st.ring_moulding(pp, TRIM, FASCIA, yP + p.soffit_h, 0, L, zE, zN, sides='NE')

    # benches on the platform side, one per bay
    for x in xc:
        if x == xm:
            continue
        bench(pp, p, x, zP if False else zN, yP)

    # ------------------------------------------------------------------ end walls: doorways, quoins, signs
    for xw, sgn in ((0.0, -1), (L, 1)):
        door(pp, p, xw, sgn, zc, dw, dspring, yP)
    # signboards on the west end face, near the street corner (owner photos IMG_3281)
    pp.box(SIGN, -5.0, -3.2, yP + 215, yP + 262, -175, -95)
    pp.box(SIGN, -5.0, -3.2, yP + 285, yP + 325, -165, -105)
    pp.box(SIGN, -5.0, -3.2, yP + 340, yP + 395, -185, -85)

    # ------------------------------------------------------------------ west canopy
    canopy(pp, p, yP, zE)

    # ------------------------------------------------------------------ roof
    y0 = yP + p.eave_h
    rx0, rx1, rz0, rz1 = -p.ovh * 0, L + p.ovh, zE, p.ovh
    roof = st.hip_roof(pp, rx0, rx1, rz0, rz1, y0, p.roof_pitch, ends=('W', 'E'))
    pp.add(TILE, roof)
    tiles(pp, rx0, rx1, rz0, rz1, y0, p.roof_pitch, ends=('W', 'E'))


# ====================================================================== facade details
def face(pp, p, s, zface, xc, sill, spring, stop, off, wall, yP, xm):
    """Window surrounds, sill band, brick dado, hoods, joinery and glass on one long face.
    s=+1 street face at z=0 (out +z); s=-1 platform face at z=zN (out -z)."""
    aw, sw, mw = p.arch_w, p.side_w, p.mull_w
    wt = p.wall_t

    def zf(d):
        return zface + s * d

    def fb(name, xa, xb, ya, yb, da, db):
        return pp.box(name, xa, xb, ya, yb, zf(da), zf(db))

    def ring(name, x, y, r0, r1, da, db, lo=None):
        b = pp.C((x, y, zf(da)), (x, y, zf(db)), r1)
        pp.cut(b, pp.C((x, y, zf(da) - s), (x, y, zf(db) + s), r0))
        pp.isect(b, pp.B(x - r1 - 1, x + r1 + 1, y if lo is None else lo, y + r1 + 1, zf(da) - 1, zf(db) + 1))
        return pp.add(name, b)

    ys0 = yP + p.plinth_h
    for x in xc:
        door_bay = (s < 0 and x == xm)
        xl, xr = x - off - sw / 2, x + off + sw / 2
        # sill band across the tripartite window
        if not door_bay:
            fb(TRIM, xl - 12, xr + 12, sill - 7, sill, 0, 6)
            fb(TRIM, xl - 8, xr + 8, sill - 11, sill - 7, 0, 3)
        else:
            for c in (x - off, x + off):
                fb(TRIM, c - sw / 2 - 12, c + sw / 2 + 12, sill - 7, sill, 0, 6)
        # brick dado panels under each light (recess cut into render, brick body + course joints)
        lights = [(x - off, sw), (x + off, sw)] + ([] if door_bay else [(x, aw)])
        for c, w in lights:
            x0, x1 = c - w / 2 - 6, c + w / 2 + 6
            y0, y1 = ys0 + 2, sill - 11
            pp.cut(wall, pp.B(x0, x1, y0, y1, zf(-3), zf(1)))
            pp.add(BRICK, brick_panel(pp, p, x1 - x0, y1 - y0, (x0 + x1) / 2, y0, zface, s))
        # narrow brick strips in the mullions
        for sx in (-1, 1):
            cm = x + sx * (aw / 2 + mw / 2)
            pp.cut(wall, pp.B(cm - 10, cm + 10, sill, stop, zf(-3), zf(1)))
            fb(BRICK, cm - 10, cm + 10, sill, stop, -3, -0.6)
        # archivolt: brick band, moulded ring, outer fillet; jamb strips down to the sill; keystone
        r = aw / 2
        ring(BRICK, x, spring, r, r + 14, -0.5, 3)
        ring(TRIM, x, spring, r + 14, r + 26, 0, 7)
        ring(TRIM, x, spring, r + 26, r + 30, 0, 4)
        ybot = yP if door_bay else sill
        for sx in (-1, 1):
            a = x + sx * r
            b2 = x + sx * (r + 14)
            fb(BRICK, min(a, b2), max(a, b2), ybot, spring, -0.5, 3)
            a = x + sx * (r + 14)
            b2 = x + sx * (r + 26)
            fb(TRIM, min(a, b2), max(a, b2), ybot, spring, 0, 7)
            # impost block at the springing
            fb(TRIM, min(x + sx * (r - 2), x + sx * (r + 30)), max(x + sx * (r - 2), x + sx * (r + 30)),
               spring - 10, spring, 0, 9)
        key = pp.prism([(x - 11, spring + r - 2), (x + 11, spring + r - 2), (x + 15, spring + r + 36),
                        (x - 15, spring + r + 36)], 'z', zf(0), zf(11))
        pp.add(TRIM, key)
        pp.box(TRIM, x - 17, x + 17, spring + r + 36, spring + r + 40, min(zf(0), zf(13)), max(zf(0), zf(13)))
        # side lights: architrave and hood cornice running to the archivolt
        for sx in (-1, 1):
            c = x + sx * off
            fb(TRIM, c - sw / 2 - 10, c - sw / 2, sill, stop, 0, 4)
            fb(TRIM, c + sw / 2, c + sw / 2 + 10, sill, stop, 0, 4)
            fb(TRIM, c - sw / 2 - 10, c + sw / 2 + 10, stop, stop + 10, 0, 4)
            ha = c - sx * (sw / 2 + 18)                      # outer end of the hood
            hb = x + sx * (r + 2)                            # inner end, tucked into the archivolt
            a0, a1 = min(ha, hb), max(ha, hb)
            hood = st.profile_run(pp, HOOD, (0, stop + 10, zface), (0, 0, s), 'x', a0, a1)
            pp.add(TRIM, hood)
        # joinery + glass
        joinery(pp, p, s, zface, x, sill, spring, stop, off, yP, door_bay)


_PANELS = {}


def brick_panel(pp, p, w, h, cx, y0, zface, s):
    """Brick panel (stretcher bond, 1 cm joints sunk 6 mm) built once per size at the origin, then copied:
    local x centred on 0, y from 0, depth d along +z (front face at d = -0.6). s=-1 turns it 180 deg about Y."""
    key = (round(w, 1), round(h, 1))
    if key not in _PANELS:
        br = pp.B(-w / 2, w / 2, 0, h, -3, -0.6)
        n = max(1, int(round(h / p.course)))
        tools = []
        for j in range(1, n):
            yj = h * j / n
            tools.append(pp.B(-w / 2 - 1, w / 2 + 1, yj - 0.5, yj + 0.5, -1.2, 0))
        for j in range(n):
            ya, yb = h * j / n, h * (j + 1) / n
            xx = -w / 2 + (13 if j % 2 else 0) + 26
            while xx < w / 2 - 2:
                tools.append(pp.B(xx - 0.5, xx + 0.5, ya, yb, -1.2, 0))
                xx += 26
        pp.cut(br, pp.merge(tools))
        _PANELS[key] = br
    b = pp.copy(_PANELS[key])
    m = adsk.core.Matrix3D.create()
    if s < 0:
        m.setToRotation(math.pi, adsk.core.Vector3D.create(0, 1, 0), adsk.core.Point3D.create(0, 0, 0))
    m.translation = adsk.core.Vector3D.create(cx, y0, zface)
    pp.tbm.transform(b, m)
    return b


def joinery(pp, p, s, zface, x, sill, spring, stop, off, yP, door_bay):
    aw, sw = p.arch_w, p.side_w
    wt = p.wall_t
    zmid = zface - s * (wt * 0.55)            # frame plane, set back in the reveal

    def zz(t):
        return zmid + s * t

    fw = 6.0                                   # frame member
    # side lights: outer frame, one transom, one mullion, glass (platform side: boarded in bays 2 and 3)
    for sx in (-1, 1):
        c = x + sx * off
        x0, x1, y0, y1 = c - sw / 2, c + sw / 2, sill, stop
        fr = pp.B(x0, x1, y0, y1, zz(-3), zz(3))
        pp.cut(fr, pp.B(x0 + fw, x1 - fw, y0 + fw, y1 - fw, zz(-4), zz(4)))
        pp.add(TIMBER, fr)
        yt = y1 - 55
        pp.box(TIMBER, x0, x1, yt - 2.5, yt + 2.5, zz(-2.5), zz(2.5))
        pp.box(TIMBER, c - 2, c + 2, y0, yt, zz(-2), zz(2))
        for yy in (y0 + (yt - y0) / 3, y0 + 2 * (yt - y0) / 3):
            pp.box(TIMBER, x0, x1, yy - 1.5, yy + 1.5, zz(-1.5), zz(1.5))
        if s < 0 and sx > 0:
            # boarded-up light (teal-painted boards), as on the platform side today
            pp.box(BOARD, x0 + 2, x1 - 2, y0 + 2, y1 - 2, zz(8), zz(12))
        else:
            pp.box(GLASS, x0 + fw, x1 - fw, y0 + fw, y1 - fw, zz(-0.3), zz(0.3))
    # central arched light
    r = aw / 2
    if door_bay:
        # double door with arched fanlight
        y_tr = spring
        fr = pp.B(x - r, x + r, yP, y_tr + 6, zz(-4), zz(4))
        pp.cut(fr, pp.B(x - r + fw, x + r - fw, yP - 1, y_tr, zz(-5), zz(5)))
        pp.add(TIMBER, fr)
        for sx in (-1, 1):
            a, b = (x - r + fw, x - 0.5) if sx < 0 else (x + 0.5, x + r - fw)
            leaf = pp.B(a, b, yP + 1, y_tr - 0.5, zz(-2.5), zz(2.5))
            for yy in (yP + 25, yP + 110, yP + 195):
                pp.cut(leaf, pp.B(a + 9, b - 9, yy, yy + 70, zz(1.5), zz(3.5)))
            pp.add(DOOR, leaf)
        fan = pp.C((x, spring, zz(-2)), (x, spring, zz(2)), r)
        pp.isect(fan, pp.B(x - r, x + r, spring + 6, spring + r, zz(-3), zz(3)))
        pp.add(GLASS, fan)
        for k in range(1, 5):
            ang = math.pi * k / 5
            c0 = (x, spring + 6, zz(0))
            c1 = (x + (r - 2) * math.cos(ang), spring + (r - 2) * math.sin(ang), zz(0))
            pp.cyl(IRON, c0, c1, 1.0)
        return
    ring = pp.C((x, spring, zz(-3)), (x, spring, zz(3)), r)
    pp.cut(ring, pp.C((x, spring, zz(-4)), (x, spring, zz(4)), r - fw))
    pp.isect(ring, pp.B(x - r - 1, x + r + 1, spring, spring + r + 1, zz(-5), zz(5)))
    pp.add(TIMBER, ring)
    pp.box(TIMBER, x - r, x - r + fw, sill, spring, zz(-3), zz(3))
    pp.box(TIMBER, x + r - fw, x + r, sill, spring, zz(-3), zz(3))
    pp.box(TIMBER, x - r, x + r, sill, sill + fw, zz(-3), zz(3))
    pp.box(TIMBER, x - r, x + r, spring - 2.5, spring + 2.5, zz(-2.5), zz(2.5))       # transom at springing
    pp.box(TIMBER, x - 2, x + 2, sill, spring + r - fw, zz(-2.5), zz(2.5))           # central mullion
    g = pp.B(x - r + fw, x + r - fw, sill + fw, spring, zz(-0.3), zz(0.3))
    gt = pp.C((x, spring, zz(-0.3)), (x, spring, zz(0.3)), r - fw)
    pp.isect(gt, pp.B(x - r, x + r, spring, spring + r, zz(-1), zz(1)))
    pp.uni(g, gt)
    pp.add(GLASS, g)
    if s > 0:
        grille(pp, x, r, sill, spring, zface - s * 9)


def grille(pp, x, r, sill, spring, zg):
    """Wrought-iron grille in the street-side arched lights: verticals, rails, arch bar and C-scrolls."""
    rb = 0.9
    n = 9
    for j in range(n):
        xx = x - r + 2 + (2 * r - 4) * (j + 0.5) / n
        dx = xx - x
        top = spring + math.sqrt(max(0.0, (r - 2) ** 2 - dx * dx))
        pp.cyl(IRON, (xx, sill + 1, zg), (xx, top, zg), rb)
    for yy in (sill + 12, sill + (spring - sill) * 0.5, spring):
        pp.cyl(IRON, (x - r + 1, yy, zg), (x + r - 1, yy, zg), rb)
    arc = pp.T((x, spring, zg), (0, 0, 1), r - 3, rb)
    pp.isect(arc, pp.B(x - r, x + r, spring, spring + r, zg - 5, zg + 5))
    pp.add(IRON, arc)
    # scrolls: two tiers of paired C-scrolls and a circle in the head
    yy = [sill + 12 + (spring - sill - 12) * f for f in (0.25, 0.75)]
    for yc in yy:
        for sx in (-1, 1):
            cx = x + sx * r * 0.42
            t = pp.T((cx, yc, zg), (0, 0, 1), r * 0.30, rb * 0.8)
            pp.isect(t, pp.B(cx, cx + sx * r, yc - r, yc + r, zg - 5, zg + 5))     # C-scroll opening inwards
            pp.add(IRON, t)
    pp.add(IRON, pp.T((x, spring + r * 0.45, zg), (0, 0, 1), r * 0.28, rb * 0.8))


# ====================================================================== pilasters, consoles, piers
def rusticate(pp, x0, x1, y0, y1, side, zface, proj, hb):
    """Block rustication (alternating long/short blocks with sunk joints) on a pier face.
    side 'S' -> face at zface, out +z; 'N' -> out -z. proj = block projection, hb = block course height (cm)."""
    s = 1 if side == 'S' else -1
    n = max(1, int(round((y1 - y0) / hb)))
    h = (y1 - y0) / n
    w = x1 - x0
    for j in range(n):
        ya, yb = y0 + j * h + 1.2, y0 + (j + 1) * h - 1.2
        inset = 0 if j % 2 == 0 else w * 0.12
        pp.box(RUST, x0 + inset, x1 - inset, ya, yb, zface, zface + s * proj)


def pilaster(pp, p, x, k, nb, L, yb, yP):
    pw, pr = p.pil_w, p.pil_p
    x0, x1 = x - pw / 2, x + pw / 2
    if k == 0:
        x0, x1 = 0, pw
    if k == nb:
        x0, x1 = L - pw, L
    top = yP + p.cons_foot
    pp.box(RENDER, x0, x1, yb, top, -1, pr - 3)                                   # shaft core
    pp.box(PLINTH, x0 - 3, x1 + 3, yb, yP + p.plinth_h + 4, -1, pr + 3)            # base block
    pp.box(TRIM, x0 - 3, x1 + 3, yP + p.plinth_h + 4, yP + p.plinth_h + 10, -1, pr + 5)
    rusticate(pp, x0, x1, yP + p.plinth_h + 10, top - 14, 'S', pr - 3, 3.0, 26)
    pp.box(TRIM, x0 - 5, x1 + 5, top - 14, top, -1, pr + 7)                        # cap
    # corner pilasters: quoins wrap round the end face
    if k in (0, nb):
        xe, sgn = (0, -1) if k == 0 else (L, 1)
        n = max(1, int(round((top - 14 - yP - p.plinth_h - 10) / 26)))
        h = (top - 14 - yP - p.plinth_h - 10) / n
        for j in range(n):
            ya, ybb = yP + p.plinth_h + 10 + j * h + 1.2, yP + p.plinth_h + 10 + (j + 1) * h - 1.2
            depth = 70 if j % 2 == 0 else 52
            pp.box(RUST, xe, xe + sgn * 3.0, ya, ybb, -depth, pr - 3)
        pp.box(RENDER, xe, xe + sgn * 0.5, yb, top, -60, pr - 3)


def console(pp, p, x, yP):
    """Large scroll console on a street pilaster: lower volute, cavetto body, upper volute, cap above the eaves."""
    w = p.cons_w
    x0, x1 = x - w / 2, x + w / 2
    f = yP + p.cons_foot
    H = p.cons_top - p.cons_foot
    P = p.cons_p
    d1 = p.pil_p + 12            # body front at the bottom
    hb = H - 35                  # underside of cap
    body = [pp.B(x0, x1, f, f + hb, 0, d1)]
    cav = pp.B(x0, x1, f + 55, f + 150, d1, P - 8)
    a, b = (P - 8 - d1), 95.0
    el = pp.EC((x0 - 1, f + 55, P - 8), (x1 + 1, f + 55, P - 8), max(a, b), min(a, b), (0, 1, 0) if b >= a else (0, 0, 1))
    pp.cut(cav, el)
    body.append(cav)
    body.append(pp.B(x0, x1, f + 150, f + hb, d1, P - 8))
    body.append(pp.C((x0, f + 15, d1 - 2), (x1, f + 15, d1 - 2), 15))                 # lower volute
    body.append(pp.C((x0, f + hb - 26, P - 18), (x1, f + hb - 26, P - 18), 26))       # upper volute
    con = pp.merge(body)
    # sunk side panels on both cheeks
    for xa, xb in ((x0 - 1, x0 + 1.5), (x1 - 1.5, x1 + 1)):
        pp.cut(con, pp.B(xa, xb, f + 40, f + hb - 50, 5, d1 - 4))
    pp.add(TRIM, con)
    # volute eyes (bosses on the cheeks)
    for yy, dd, rr in ((f + 15, d1 - 2, 6), (f + hb - 26, P - 18, 10)):
        pp.cyl(TRIM, (x0 - 1.5, yy, dd), (x1 + 1.5, yy, dd), rr)
    # cap: abacus and top block rising above the eaves
    pp.box(TRIM, x0 - 6, x1 + 6, f + hb, f + hb + 15, -1, P + 10)
    pp.box(TRIM, x0 - 2, x1 + 2, f + hb + 15, f + H, -1, P)


def bench(pp, p, x, zN, yP):
    bl, bd, bh = p.bench_l, p.bench_d, p.bench_h
    z0, z1 = zN - bd, zN - 2
    seat = pp.B(x - bl / 2 + bd / 2, x + bl / 2 - bd / 2, yP + bh - 8, yP + bh, z0, z1)
    for sx in (-1, 1):
        pp.uni(seat, pp.C((x + sx * (bl / 2 - bd / 2), yP + bh - 8, (z0 + z1) / 2),
                          (x + sx * (bl / 2 - bd / 2), yP + bh, (z0 + z1) / 2), (z1 - z0) / 2))
    pp.add(BENCH, seat)
    for sx in (-1, 1):
        pp.box(RENDER, x + sx * (bl / 2 - 45) - 14, x + sx * (bl / 2 - 45) + 14, yP, yP + bh - 8, z0 + 6, z1)


def door(pp, p, xw, sgn, zc, dw, dspring, yP):
    """End-wall arched doorway: archivolt, keystone, boarded double doors with fanlight."""
    wt = p.wall_t
    r = dw / 2

    def xf(d):
        return xw + sgn * d
    # archivolt on the outer face
    for r0, r1, dd, name in ((r, r + 14, 3, TRIM), (r + 14, r + 20, 6, TRIM)):
        b = pp.C((xf(0), dspring, zc), (xf(dd), dspring, zc), r1)
        pp.cut(b, pp.C((xf(-1), dspring, zc), (xf(dd + 1), dspring, zc), r0))
        pp.isect(b, pp.B(min(xf(-1), xf(dd + 1)), max(xf(-1), xf(dd + 1)), dspring, dspring + r1 + 1,
                         zc - r1 - 1, zc + r1 + 1))
        pp.add(name, b)
        for sz in (-1, 1):
            a, bb = zc + sz * r0, zc + sz * r1
            pp.box(name, xf(0), xf(dd), yP, dspring, min(a, bb), max(a, bb))
    pp.add(TRIM, pp.prism([(zc - 10, dspring + r - 2), (zc + 10, dspring + r - 2), (zc + 13, dspring + r + 30),
                           (zc - 13, dspring + r + 30)], 'x', xf(0), xf(9)))
    # doors set mid-wall (inner plane)
    xm = xw - sgn * wt * 0.5
    fr = pp.B(xm - 4, xm + 4, yP, dspring + 6, zc - r, zc + r)
    pp.cut(fr, pp.B(xm - 5, xm + 5, yP - 1, dspring, zc - r + 6, zc + r - 6))
    pp.add(TIMBER, fr)
    for sz in (-1, 1):
        a, b = (zc - r + 6, zc - 0.5) if sz < 0 else (zc + 0.5, zc + r - 6)
        leaf = pp.B(xm - 2.5, xm + 2.5, yP + 1, dspring - 0.5, a, b)
        # vertical boarding grooves
        zz = a + 12
        while zz < b - 4:
            pp.cut(leaf, pp.B(xm + sgn * 2.5 - 0.6, xm + sgn * 2.5 + 0.6, yP + 1, dspring - 0.5, zz - 0.5, zz + 0.5))
            zz += 12
        pp.add(DOOR, leaf)
    fan = pp.C((xm - 1.5, dspring, zc), (xm + 1.5, dspring, zc), r)
    pp.isect(fan, pp.B(xm - 2, xm + 2, dspring + 6, dspring + r, zc - r, zc + r))
    pp.add(BOARD, fan)


# ====================================================================== canopy
def chamfer_poly(x0, x1, z0, z1, c, west_only=True):
    if west_only:
        return [(x1, z1), (x0 + c, z1), (x0, z1 - c), (x0, z0 + c), (x0 + c, z0), (x1, z0)]
    return [(x1 - c, z1), (x0 + c, z1), (x0, z1 - c), (x0, z0 + c), (x0 + c, z0), (x1 - c, z0), (x1, z0 + c), (x1, z1 - c)]


def canopy(pp, p, yP, zE):
    x0, x1, z0, z1 = -p.can_p, 0.0, zE, p.ovh
    c = p.can_chamf
    ys = yP + p.can_soffit
    yt = ys + p.can_fascia
    slab = pp.prism(chamfer_poly(x0, x1, z0, z1, c), 'y', ys, yt)
    # coffers in the soffit (two stepped panels)
    zm = (z0 + z1) / 2
    for za, zb in ((z0 + 45, zm - 15), (zm + 15, z1 - 45)):
        pp.cut(slab, pp.B(x0 + 45, x1 - 35, ys - 1, ys + 8, za, zb))
        pp.cut(slab, pp.B(x0 + 57, x1 - 47, ys - 1, ys + 15, za + 12, zb - 12))
    pp.add(RENDER, slab)
    # fascia mouldings: drip band at the bottom, cap mouldings at the top
    for dd, ya, yb in ((3, ys, ys + 6), (6, yt - 18, yt - 12), (10, yt - 12, yt - 6), (14, yt - 6, yt)):
        b = pp.prism(chamfer_poly(x0 - dd, x1, z0 - dd, z1 + dd, c + dd * 0.41), 'y', ya, yb)
        pp.cut(b, pp.B(x0 + 30, x1 + 1, ya - 1, yb + 1, z0 + 30, z1 - 30))
        pp.add(TRIM, b)
    # stepped corbels under the canopy edge at the street and platform corners of the end wall
    for zz, sz in ((z1, -1), (z0, 1)):
        for j in range(3):
            pp.box(TRIM, -60 + 12 * j, 0, ys - 30 + 10 * j, ys - 20 + 10 * j,
                   min(zz + sz * 2, zz + sz * (40 - 10 * j)), max(zz + sz * 2, zz + sz * (40 - 10 * j)))
    # canopy roof: hipped on three sides, abutting the end wall
    roof = st.hip_roof(pp, x0 - 14, x1 + 60, z0 - 14, z1 + 14, yt, p.roof_pitch, ends=('W', 'E'))
    pp.add(TILE, roof)
    tiles(pp, x0 - 14, x1 + 60, z0 - 14, z1 + 14, yt, p.roof_pitch, ends=('W', 'E'))


# ====================================================================== tiles
def tiles(pp, x0, x1, z0, z1, y0, pitch, ends=('W', 'E')):
    """Roman-tile rolls on every pitched plane, trimmed by a raised hip envelope; hip and ridge cappings."""
    r = 6.0                      # roll radius
    pitch_x = 21.0               # roll spacing
    lift = r * 1.6
    t = math.tan(pitch)
    W = (z1 - z0) / 2
    yR = y0 + W * t
    sn, cs = math.sin(pitch), math.cos(pitch)
    rolls = []
    # long sides (S and N): rolls run down the slope, spaced along x
    for side in ('S', 'N'):
        zs = z1 if side == 'S' else z0
        sz = -1 if side == 'S' else 1                         # inward direction along z
        n_ = (0, cs, -sz * sn)                                # outward normal of this plane
        off = r * 0.45
        xx = x0 + pitch_x / 2
        while xx < x1:
            a = (xx, y0 + n_[1] * off - 2.0 * t, zs - sz * 2.0 + n_[2] * off)
            b = (xx, yR + n_[1] * off, zs + sz * W + n_[2] * off)
            rolls.append(pp.C(a, b, r))
            xx += pitch_x
    for side in ends:
        xs_ = x0 if side == 'W' else x1
        sx = 1 if side == 'W' else -1
        n_ = (-sx * sn, cs, 0)
        off = r * 0.45
        zz = z0 + pitch_x / 2
        while zz < z1:
            a = (xs_ - sx * 2.0 + n_[0] * off, y0 + n_[1] * off - 2.0 * t, zz)
            b = (xs_ + sx * W + n_[0] * off, yR + n_[1] * off, zz)
            rolls.append(pp.C(a, b, r))
            zz += pitch_x
    body = pp.merge(rolls)
    env = st.hip_roof(pp, x0 - 3, x1 + 3, z0 - 3, z1 + 3, y0 - 3, pitch, ends=ends, lift=lift)
    pp.isect(body, env)
    pp.add(TILE, body)
    # cappings along hips and the ridge (ridge along the longer plan direction)
    rc = 9.0
    up = rc * 0.5
    caps = []
    four = ('W' in ends and 'E' in ends)
    zc, xc = (z0 + z1) / 2, (x0 + x1) / 2
    if four and (x1 - x0) < (z1 - z0):
        Wx = (x1 - x0) / 2
        yr = y0 + Wx * t
        caps.append(pp.C((xc, yr + up, z0 + Wx), (xc, yr + up, z1 - Wx), rc))
        for xe in (x0, x1):
            for ze, zr in ((z0, z0 + Wx), (z1, z1 - Wx)):
                caps.append(pp.C((xe, y0 + up, ze), (xc, yr + up, zr), rc))
    else:
        xr0 = x0 + W if 'W' in ends else x0
        xr1 = x1 - W if 'E' in ends else x1
        if xr1 > xr0:
            caps.append(pp.C((xr0, yR + up, zc), (xr1, yR + up, zc), rc))
        for side, xe, xr in (('W', x0, xr0), ('E', x1, xr1)):
            if side in ends:
                for ze in (z0, z1):
                    caps.append(pp.C((xe, y0 + up, ze), (xr, yR + up, zc), rc))
    for cbody in caps:
        pp.add(TILE, cbody)
