# Shared helpers for the Sporting El Soghra station build scripts.
#
# Frame (document is Y-up, API units are cm):
#   X along the track, + towards ENE (bearing ~55 deg), 0 = west end wall of the south pavilion
#   Y up, 0 = top of rail (TOR). Platform finished level (PFL) = plat_h.
#   Z across the track, + towards SSE (the south / Sporting Club carriageway), 0 = street face of the south pavilion.
#
# Geometry is made with TemporaryBRepManager and committed in one base feature per component, so a rebuild adds
# no timeline features. Every dimension comes from a user parameter (see params.py); re-run a build script after
# changing parameters.
import math, re
import adsk.core, adsk.fusion

DOC = 'Sporting El Soghra Station'
P = adsk.core.Point3D.create
Vec = adsk.core.Vector3D.create
UNION = adsk.fusion.BooleanTypes.UnionBooleanType
CUT = adsk.fusion.BooleanTypes.DifferenceBooleanType
ISECT = adsk.fusion.BooleanTypes.IntersectionBooleanType


def activate(name=DOC):
    """Activate OUR document by name (another session may be using Fusion) and return (app, design)."""
    app = adsk.core.Application.get()
    docs = [d for d in app.documents if d.name == name]
    if not docs:
        raise RuntimeError('document %r is not open' % name)
    doc = docs[0]
    if app.activeDocument != doc:
        doc.activate()
    design = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
    return app, design


class Prm:
    """p.name -> parameter value in API units (cm for lengths, rad for angles, plain number for counts)."""
    def __init__(self, design):
        self._d = design

    def __getattr__(self, n):
        prm = self._d.userParameters.itemByName(n)
        if prm is None:
            raise AttributeError('user parameter %s missing - run build_params.py' % n)
        return prm.value

    def i(self, n):
        return int(round(getattr(self, n)))


def base(n):
    return re.sub(r'( \(\d+\))+$', '', n)


def comp(parent, name, create=True):
    """Find (or create) the child component `name` directly under the component `parent`."""
    for o in parent.occurrences:
        if o.component.name == name:
            return o.component
    if not create:
        return None
    occ = parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    return occ.component


def wipe(c):
    f = c.features
    for i in range(f.baseFeatures.count - 1, -1, -1):
        f.baseFeatures.item(i).deleteMe()
    for i in range(c.bRepBodies.count - 1, -1, -1):
        c.bRepBodies.item(i).deleteMe()


def ptmap(axis):
    """2-D profile (u, v) + extrusion coordinate w -> 3-D point.
    axis 'z': profile in the XY plane (u=x, v=y), extruded along z.
    axis 'x': profile in the ZY plane (u=z, v=y), extruded along x.
    axis 'y': profile in the XZ plane (u=x, v=z), extruded along y."""
    if axis == 'z':
        return lambda u, v, w: (u, v, w)
    if axis == 'x':
        return lambda u, v, w: (w, v, u)
    return lambda u, v, w: (u, w, v)


class Parts:
    """Collects temporary bodies by name (= material / part class); commit() unions each name into one body."""

    def __init__(self):
        self.tbm = adsk.fusion.TemporaryBRepManager.get()
        self.items = {}
        self.order = []

    # ---------- primitives (return the temporary body, NOT yet registered) ----------
    def B(self, x0, x1, y0, y1, z0, z1):
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        z0, z1 = min(z0, z1), max(z0, z1)
        ob = adsk.core.OrientedBoundingBox3D.create(P((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
                                                    Vec(1, 0, 0), Vec(0, 1, 0), x1 - x0, y1 - y0, z1 - z0)
        return self.tbm.createBox(ob)

    def OB(self, c, xd, yd, lx, ly, lz):
        xv = Vec(*xd); xv.normalize()
        yv = Vec(*yd)
        d = yv.dotProduct(xv)
        yv = Vec(yv.x - d * xv.x, yv.y - d * xv.y, yv.z - d * xv.z)    # exact orthogonality
        yv.normalize()
        ob = adsk.core.OrientedBoundingBox3D.create(P(*c), xv, yv, lx, ly, lz)
        return self.tbm.createBox(ob)

    def C(self, a, b, r, r2=None):
        return self.tbm.createCylinderOrCone(P(*a), r, P(*b), r if r2 is None else r2)

    def EC(self, a, b, rmaj, rmin, majdir):
        return self.tbm.createEllipticalCylinderOrCone(P(*a), rmaj, rmin, P(*b), rmaj, Vec(*majdir))

    def S(self, c, r):
        return self.tbm.createSphere(P(*c), r)

    def T(self, c, axis, R, r):
        return self.tbm.createTorus(P(*c), Vec(*axis), R, r)

    def prism(self, pts, axis, w0, w1):
        """Convex polygon pts [(u, v), ...] (either winding) extruded from w0 to w1 along `axis`."""
        m = ptmap(axis)
        us = [p[0] for p in pts]; vs = [p[1] for p in pts]
        pad = 1.0
        u0, u1, v0, v1 = min(us) - pad, max(us) + pad, min(vs) - pad, max(vs) + pad
        a = m(u0, v0, min(w0, w1)); b = m(u1, v1, max(w0, w1))
        body = self.B(a[0], b[0], a[1], b[1], a[2], b[2])
        area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                   for i in range(len(pts)))
        sgn = 1 if area > 0 else -1
        S = 4 * max(u1 - u0, v1 - v0) + 10
        wl = abs(w1 - w0) + 10
        wc = (w0 + w1) / 2
        for i in range(len(pts)):
            p0, p1 = pts[i], pts[(i + 1) % len(pts)]
            du, dv = p1[0] - p0[0], p1[1] - p0[1]
            L = math.hypot(du, dv)
            if L < 1e-6:
                continue
            nu, nv = sgn * dv / L, -sgn * du / L          # outward normal
            cu, cv = (p0[0] + p1[0]) / 2 + nu * S / 2, (p0[1] + p1[1]) / 2 + nv * S / 2
            c = m(cu, cv, wc)
            e1 = m(du / L, dv / L, 0); e2 = m(nu, nv, 0)
            # OB lengths: along e1, along e2, along the third axis (= extrusion)
            cutter = self.OB(c, e1, e2, S, S, wl)
            self.tbm.booleanOperation(body, cutter, CUT)
        return body

    # ---------- registration ----------
    def add(self, name, body):
        if body is None:
            raise RuntimeError('null body for ' + name)
        if name not in self.items:
            self.items[name] = []
            self.order.append(name)
        self.items[name].append(body)
        return body

    def box(self, name, x0, x1, y0, y1, z0, z1):
        return self.add(name, self.B(x0, x1, y0, y1, z0, z1))

    def cyl(self, name, a, b, r, r2=None):
        return self.add(name, self.C(a, b, r, r2))

    def cut(self, target, tool):
        self.tbm.booleanOperation(target, tool, CUT)
        return target

    def uni(self, target, tool):
        self.tbm.booleanOperation(target, tool, UNION)
        return target

    def isect(self, target, tool):
        self.tbm.booleanOperation(target, tool, ISECT)
        return target

    def copy(self, b):
        return self.tbm.copy(b)

    def merge(self, bodies):
        """Pairwise (tree) union of a list of temporary bodies -> one body."""
        bodies = [b for b in bodies if b is not None]
        while len(bodies) > 1:
            nxt = []
            for i in range(0, len(bodies) - 1, 2):
                self.tbm.booleanOperation(bodies[i], bodies[i + 1], UNION)
                nxt.append(bodies[i])
            if len(bodies) % 2:
                nxt.append(bodies[-1])
            bodies = nxt
        return bodies[0] if bodies else None

    def cut_all(self, name, tool):
        """Subtract tool from every registered body of `name`."""
        for b in self.items.get(name, []):
            self.tbm.booleanOperation(b, self.tbm.copy(tool), CUT)

    def transform_all(self, m):
        for n in self.items:
            for b in self.items[n]:
                self.tbm.transform(b, m)

    def commit(self, c, label, merge=True):
        """Replace everything in component c by the collected bodies, inside one base feature."""
        wipe(c)
        bf = c.features.baseFeatures.add()
        bf.startEdit()
        n = 0
        for name in self.order:
            bl = self.items[name]
            if merge:
                body = self.merge(bl)
                c.bRepBodies.add(body, bf).name = name
                n += 1
            else:
                for b in bl:
                    c.bRepBodies.add(b, bf).name = name
                    n += 1
        bf.finishEdit()
        bf.name = label
        return n


# ---------- moulding profiles ----------
# A profile is a list of 2-D pieces in (d, h): d = projection out of the wall face (cm), h = height above the
# moulding datum (cm):
#   ('r', d0, d1, h0, h1)            rectangle
#   ('q', cd, ch, r, qd, qh)         convex quarter round centred (cd, ch), quadrant signs qd, qh (+1/-1)
#   ('k', cd, ch, r, qd, qh)         concave quarter (cavetto): the square of side r in quadrant (qd, qh)
#                                    minus the circle centred (cd, ch)
def _piece_prism(pp, pc, m, w0, w1):
    """One profile piece -> temporary body. m maps (d, h, w) -> xyz."""
    kind = pc[0]
    if kind == 'r':
        _, d0, d1, h0, h1 = pc
        a = m(d0, h0, w0); b = m(d1, h1, w1)
        return pp.B(a[0], b[0], a[1], b[1], a[2], b[2])
    _, cd, ch, r, qd, qh = pc
    a = m(cd, ch, w0); b = m(cd, ch, w1)
    sq0 = m(cd, ch, w0); sq1 = m(cd + qd * r, ch + qh * r, w1)
    sq = pp.B(sq0[0], sq1[0], sq0[1], sq1[1], sq0[2], sq1[2])
    cy = pp.C(a, b, r)
    if kind == 'q':
        pp.isect(sq, cy)
        return sq
    # concave: the square on the other side of the circle centre
    sq0 = m(cd + qd * r, ch + qh * r, w0); sq1 = m(cd, ch, w1)
    sq = pp.B(sq0[0], sq1[0], sq0[1], sq1[1], sq0[2], sq1[2])
    pp.cut(sq, cy)
    return sq


def profile_run(pp, profile, origin, out, along, w0, w1, hscale=1.0):
    """Extrude a moulding profile along a straight wall run.
    origin: (x, y, z) of the datum on the wall face; out: unit vector out of the wall (x or z axis, +/-);
    along: 'x' or 'z' run axis; w0..w1 the run extent (absolute coordinate on that axis)."""
    ox, oy, oz = origin

    def m(d, h, w):
        h = h * hscale
        if along == 'x':
            return (w, oy + h, oz + out[2] * d)
        return (ox + out[0] * d, oy + h, w)
    bodies = [_piece_prism(pp, pc, m, w0, w1) for pc in profile]
    return pp.merge(bodies)


def profile_depth(profile):
    d = 0
    for pc in profile:
        if pc[0] == 'r':
            d = max(d, pc[1], pc[2])
        else:
            d = max(d, pc[1] + max(pc[4], 0) * pc[3])
    return d


def ring_moulding(pp, name, profile, y, x0, x1, z0, z1, sides='SNWE'):
    """Moulding around a rectangle x0..x1, z0..z1 (wall faces) at datum height y, with mitred external corners.
    sides: any of S (z1 face, out +z), N (z0, out -z), W (x0, out -x), E (x1, out +x)."""
    D = profile_depth(profile) + 0.5
    runs = {}
    if 'S' in sides:
        runs['S'] = lambda a, b: profile_run(pp, profile, (0, y, z1), (0, 0, 1), 'x', a, b)
    if 'N' in sides:
        runs['N'] = lambda a, b: profile_run(pp, profile, (0, y, z0), (0, 0, -1), 'x', a, b)
    if 'W' in sides:
        runs['W'] = lambda a, b: profile_run(pp, profile, (x0, y, 0), (-1, 0, 0), 'z', a, b)
    if 'E' in sides:
        runs['E'] = lambda a, b: profile_run(pp, profile, (x1, y, 0), (1, 0, 0), 'z', a, b)
    out = []
    for s, f in runs.items():
        if s in 'SN':
            out.append(f(x0, x1))
        else:
            out.append(f(z0, z1))
    # corners: intersection of the two runs extended into the corner square
    for a, b, cx, cz in (('S', 'W', x0 - D, z1 + D), ('S', 'E', x1 + D, z1 + D),
                         ('N', 'W', x0 - D, z0 - D), ('N', 'E', x1 + D, z0 - D)):
        if a in runs and b in runs:
            xa, xb = (x0 - D, x0) if b == 'W' else (x1, x1 + D)
            za, zb = (z1, z1 + D) if a == 'S' else (z0 - D, z0)
            ra = runs[a](xa, xb)
            rb = runs[b](za, zb)
            pp.isect(ra, rb)
            out.append(ra)
    body = pp.merge(out)
    pp.add(name, body)
    return body


def hip_roof(pp, x0, x1, z0, z1, y0, pitch, ridge_cap=None, ends=('W', 'E'), sides=('S', 'N'), lift=0.0):
    """Solid hipped roof over the eaves rectangle x0..x1, z0..z1 at eaves height y0, all planes at `pitch` (rad).
    Planes not listed in ends/sides are vertical (gable/abutment). lift raises every plane (for the tile envelope)."""
    t = math.tan(pitch)
    W = (z1 - z0) / 2
    H = W * t + abs(lift) + 50
    if ridge_cap:
        H = min(H, ridge_cap - y0 + abs(lift))
    body = pp.B(x0 - 50, x1 + 50, y0, y0 + H + 1, z0 - 50, z1 + 50)
    S = 6 * max(x1 - x0, z1 - z0) + 1000
    # each plane: passes through the eaves line at height y0 + lift/cos, inclined at pitch, material below it
    sn, cs = math.sin(pitch), math.cos(pitch)
    planes = []
    for side in sides:
        if side == 'S':
            planes.append(((0, 0, 1), z1))
        else:
            planes.append(((0, 0, -1), z0))
    for side in ends:
        if side == 'W':
            planes.append(((-1, 0, 0), x0))
        else:
            planes.append(((1, 0, 0), x1))
    for (nx, _, nz), edge in planes:
        # cutter: big box above the plane. Plane normal (outward, upward): (nx*sn, cs, nz*sn)
        n = (nx * sn, cs, nz * sn)
        # point on plane: eaves line point
        if nx == 0:
            p0 = ((x0 + x1) / 2, y0 + lift / cs, edge)
        else:
            p0 = (edge, y0 + lift / cs, (z0 + z1) / 2)
        c = (p0[0] + n[0] * S / 2, p0[1] + n[1] * S / 2, p0[2] + n[2] * S / 2)
        along = (0, 0, 1) if nx == 0 else (1, 0, 0)
        along = (1, 0, 0) if nx == 0 else (0, 0, 1)
        # second box axis = n
        cutter = pp.OB(c, along, n, S, S, S)
        pp.cut(body, cutter)
    if 'S' not in sides:
        pp.cut(body, pp.B(x0 - 100, x1 + 100, y0 - 1, y0 + H + 100, z1, z1 + 1000))
    if 'N' not in sides:
        pp.cut(body, pp.B(x0 - 100, x1 + 100, y0 - 1, y0 + H + 100, z0 - 1000, z0))
    if 'W' not in ends:
        pp.cut(body, pp.B(x0 - 1000, x0, y0 - 1, y0 + H + 100, z0 - 100, z1 + 100))
    if 'E' not in ends:
        pp.cut(body, pp.B(x1, x1 + 1000, y0 - 1, y0 + H + 100, z0 - 100, z1 + 100))
    return body
