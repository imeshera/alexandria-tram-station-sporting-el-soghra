# Builds the components "Embankment", "Track" and "Platform" inside "Station Half".
# The half runs from the south street to the symmetry axis between the two tracks; the north half is the same
# component turned 180 deg about a vertical axis (build_twin.py), so everything here is built once.
#   Embankment: fill, stone-pitched street slope with rubble stones, pavement + kerb, carriageway strip.
#   Track: one 1435 mm track (flat-bottom rails, base plates, concrete sleepers, ballast bed).
#   Platform: deck with grooved cement tiles, tactile strip, edge copings, track-side wall, street-side parapet with
#   piers and coping, boundary wall where there is no platform.
import math
import random
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

def geom(p):
    """Shared cross-section numbers (cm)."""
    g = {}
    g['yP'] = p.plat_h
    g['yst'] = p.plat_h - p.street_drop                 # pavement top
    g['yb'] = p.plat_h - p.berm_drop                    # slope crest / formation level
    g['zEdge'] = -(p.depth + p.plat_w)
    g['zT'] = g['zEdge'] - p.edge_off                   # this half's track centre
    g['zax'] = g['zT'] - p.track_ctr / 2                # symmetry axis
    g['zcrest'] = p.para_t
    g['ztoe'] = g['zcrest'] + (g['yb'] - g['yst']) / math.tan(p.slope_ang)
    g['x0'] = p.site_x0
    g['x1'] = 2 * p.twin_cx - p.site_x0
    g['L'] = 2 * p.end_pad + p.n_bays * p.bay
    rh = p.street_drop / (p.st_n1 + p.st_n2)
    run1, run2 = p.st_n1 * p.st_tread, p.st_n2 * p.st_tread
    fl = p.st_w + 10
    g['rh'], g['run1'], g['run2'], g['fl'] = rh, run1, run2, fl
    g['xLE0'] = p.st_x + fl / 2 + run1                  # east half-landing, west edge
    g['xLW1'] = p.st_x - fl / 2 - run1                  # west half-landing, east edge
    g['xHL1'] = g['xLE0'] - run2                        # head landing east end
    g['xHL0'] = g['xLW1'] + run2                        # head landing west end
    # stair footprint (for cutting the slope): landings + end parapets, out to the outer parapet
    g['st_x0'] = g['xLW1'] - fl - p.st_para_t
    g['st_x1'] = g['xLE0'] + fl + p.st_para_t
    g['st_z1'] = g['zcrest'] + 3 * p.st_para_t + 2 * p.st_w
    return g


def run(_context: str):
    app, design = st.activate()
    p = st.Prm(design)
    half = st.comp(design.rootComponent, 'Station Half')
    g = geom(p)
    for name, fn in (('Embankment', embankment), ('Track', track), ('Platform', platform)):
        pp = st.Parts()
        fn(pp, p, g)
        n = pp.commit(st.comp(half, name), name + ' geometry')
        print(name, n, 'bodies')


def embankment(pp, p, g):
    x0, x1 = g['x0'], g['x1']
    yst, yb, zc, zt, zax = g['yst'], g['yb'], g['zcrest'], g['ztoe'], g['zax']
    pts = [(zax, yst - 40), (zt, yst - 40), (zt, yst), (zc, yb), (zax, yb)]
    pp.add('Earth fill', pp.prism(pts, 'x', x0, x1))
    # stone pitching skin on the slope (30 cm) with rubble stones proud of it
    th = 30.0
    sn = math.sin(p.slope_ang)
    cs = math.cos(p.slope_ang)
    sk = [(zt, yst), (zc, yb), (zc - th / sn, yb), (zt - th / sn, yst)]
    pp.add('Stone pitching', pp.prism(sk, 'x', x0, x1))
    rnd = random.Random(7)
    stones = []
    slope_len = (yb - yst) / sn
    # slope direction (z, y) going up: (-cs, sn); outward normal (sn, cs)
    xx = -2200.0
    while xx < 3500.0:
        s = 15.0
        while s < slope_len - 10:
            zz = zt - cs * s
            yy = yst + sn * s
            lx, ly, lz = rnd.uniform(20, 38), rnd.uniform(10, 18), rnd.uniform(16, 30)
            ang = rnd.uniform(-0.6, 0.6)
            tilt = rnd.uniform(-0.25, 0.25)
            c = (xx + rnd.uniform(-7, 7), yy + cs * 3.0, zz + sn * 3.0)
            xd = (math.cos(ang), math.sin(tilt) * 0.5, math.sin(ang) * 0.3)
            # second axis roughly along the slope normal, rocked a little
            nrm = (rnd.uniform(-0.2, 0.2), cs, sn + rnd.uniform(-0.2, 0.2))
            # make yd perpendicular to xd
            dot = xd[0] * nrm[0] + xd[1] * nrm[1] + xd[2] * nrm[2]
            yd = (nrm[0] - dot * xd[0], nrm[1] - dot * xd[1], nrm[2] - dot * xd[2])
            stones.append(pp.OB(c, xd, yd, lx, ly, lz))
            s += rnd.uniform(24, 32)
        xx += rnd.uniform(30, 38)
    pp.add('Rubble stones', pp.merge(stones))
    # the stair block replaces the slope in its footprint
    cutter = pp.B(g['st_x0'], g['st_x1'], yst - 0.5, yb + 200, zc + 0.5, g['st_z1'] + 50)
    for n in ('Earth fill', 'Stone pitching', 'Rubble stones'):
        pp.cut_all(n, cutter)
    # pavement, kerb, road strip
    pw = p.pave_w
    pp.box('Pavement', x0, x1, yst - 40, yst, zt - 1, zt + pw)
    pp.box('Kerb', x0, x1, yst - 40, yst + 1, zt + pw, zt + pw + 25)
    pp.box('Asphalt', x0, x1, yst - 40, yst - 15, zt + pw + 25, zt + pw + 25 + p.road_w)
    # pavement joints every 1 m
    xx = math.ceil(x0 / 100) * 100
    while xx < x1:
        for b in pp.items['Pavement']:
            pp.cut(b, pp.B(xx - 0.4, xx + 0.4, yst - 0.5, yst + 1, zt - 2, zt + pw + 1))
        xx += 100


def track(pp, p, g):
    x0, x1 = g['x0'], g['x1']
    zT, zax, zE, yb = g['zT'], g['zax'], g['zEdge'], g['yb']
    rh = p.rail_h
    hw, hh, ww, fw, fh = 6.7, 4.2, 1.5, 12.5, 1.2
    for sgn in (-1, 1):
        zc = zT + sgn * (p.gauge / 2 + hw / 2)
        r = [pp.B(x0, x1, -hh, 0, zc - hw / 2, zc + hw / 2),
             pp.B(x0, x1, -rh + fh, -hh, zc - ww / 2, zc + ww / 2),
             pp.B(x0, x1, -rh, -rh + fh, zc - fw / 2, zc + fw / 2),
             pp.B(x0, x1, -hh - 1.0, -hh, zc - 2.0, zc + 2.0),
             pp.B(x0, x1, -rh + fh, -rh + fh + 1.0, zc - 3.5, zc + 3.5)]
        pp.add('Rails', pp.merge(r))
    ys = -rh - 1.0
    sl, plates = [], []
    xx = x0 + p.sleeper_pitch / 2
    while xx < x1:
        sl.append(pp.B(xx - 12.5, xx + 12.5, ys - 20, ys, zT - 130, zT + 130))
        for sgn in (-1, 1):
            zc = zT + sgn * (p.gauge / 2 + 3.35)
            plates.append(pp.B(xx - 9, xx + 9, ys, ys + 1.0, zc - 15, zc + 15))
            for sz in (-1, 1):
                plates.append(pp.B(xx - 2, xx + 2, ys + 1.0, -rh + 2.5, zc + sz * 7.5 - 1.2, zc + sz * 7.5 + 1.2))
        xx += p.sleeper_pitch
    pp.add('Sleepers', pp.merge(sl))
    pp.add('Rail fastenings', pp.merge(plates))
    pp.box('Ballast', x0, x1, yb, ys - 5, zax, zE)


def platform(pp, p, g):
    yP, yb, zE = g['yP'], g['yb'], g['zEdge']
    px0, px1 = p.plat_x0, p.plat_x1
    L = g['L']
    tile = p.tile
    deck = pp.B(px0, px1, yb, yP - 12, zE, 0)
    pp.add('Platform structure', deck)
    # paving: 12 cm tiles+bed over the deck, grooved joints (5 mm x 3 mm)
    zc0 = zE + 45
    pav = pp.B(px0, px1, yP - 12, yP, zc0, 0)
    tools = []
    xx = px0 + tile
    while xx < px1:
        tools.append(pp.B(xx - 0.25, xx + 0.25, yP - 0.3, yP + 1, zc0, 0))
        xx += tile
    zz = zc0 + tile
    while zz < 0:
        tools.append(pp.B(px0, px1, yP - 0.3, yP + 1, zz - 0.25, zz + 0.25))
        zz += tile
    # tactile / ribbed strip behind the copings (ribs along the platform)
    for k in range(12):
        z = zc0 + 2.5 + k * 5
        tools.append(pp.B(px0, px1, yP - 0.4, yP + 1, z - 1.0, z + 1.0))
    pp.cut(pav, pp.merge(tools))
    pp.add('Paving', pav)
    # edge copings with nosing, joints every 90 cm
    cop = pp.B(px0, px1, yP - 12, yP, zE - 5, zc0)
    pp.cut(cop, pp.B(px0 - 1, px1 + 1, yP - 13, yP - 6, zE - 6, zE - 0.0))
    xx = px0 + 90
    tools = []
    while xx < px1:
        tools.append(pp.B(xx - 0.4, xx + 0.4, yP - 0.6, yP + 1, zE - 6, zc0 + 1))
        xx += 90
    pp.cut(cop, pp.merge(tools))
    pp.add('Copings', cop)
    # street-side parapet (outside the pavilion and the stair head), piers with caps
    gaps = [(g['xHL0'], L)]
    segs = []
    a = px0
    for g0, g1 in gaps:
        segs.append((a, g0))
        a = g1
    segs.append((a, px1))
    pt = p.para_t
    for a, b in segs:
        if b - a < 10:
            continue
        pp.box('Parapets', a, b, yb, yP + p.para_h - 8, 0, pt)
        pp.box('Parapet coping', a - 2, b + 2, yP + p.para_h - 8, yP + p.para_h, -4, pt + 4)
        # inner bench ledge, as along the north platform today
        n = max(1, int(round((b - a) / p.para_pier)))
        for k in range(n + 1):
            x = a + (b - a) * k / n
            x0_, x1_ = max(a, x - 22), min(b, x + 22)
            pp.box('Parapets', x0_, x1_, yP, yP + p.para_h + 20, -6, pt + 6)
            pp.box('Parapet coping', x0_ - 3, x1_ + 3, yP + p.para_h + 20, yP + p.para_h + 26, -9, pt + 9)
    # deck and paving filling the parapet gap between the platform and the stair head landing
    pp.box('Platform structure', g['xHL0'], 0, yb, yP - 12, 0, pt)
    pp.box('Paving', g['xHL0'], 0, yP - 12, yP, 0, pt)
    # boundary wall along the street-side crest where this half has no platform
    hw = yP + 90
    pp.box('Boundary wall', g['x0'], px0, yb, hw, 0, pt)
    pp.box('Boundary wall', px1, g['x1'], yb, hw, 0, pt)
    pp.box('Parapet coping', g['x0'], px0, hw, hw + 6, -3, pt + 3)
    pp.box('Parapet coping', px1, g['x1'], hw, hw + 6, -3, pt + 3)
