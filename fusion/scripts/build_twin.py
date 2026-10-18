# Places the north twin: a second occurrence of "Station Half" turned 180 deg about the vertical axis
# x = twin_cx, z = (symmetry axis between the tracks). The north pavilion (seen in the 2024 and 2026 platform
# videos) is a point-symmetric copy of the south one: canopy at its east end, stairs to the north carriageway.
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

def run(_context: str):
    app, design = st.activate()
    p = st.Prm(design)
    g = build_site.geom(p)
    root = design.rootComponent
    half = st.comp(root, 'Station Half')
    m = adsk.core.Matrix3D.create()
    m.setToRotation(math.pi, adsk.core.Vector3D.create(0, 1, 0), adsk.core.Point3D.create(p.twin_cx, 0, g['zax']))
    occs = [o for o in root.occurrences if o.component == half]
    if len(occs) < 2:
        occ = root.occurrences.addExistingComponent(half, m)
    else:
        occ = occs[1]
        occ.transform2 = m
    if design.snapshots.hasPendingSnapshot:
        design.snapshots.add()
    print('twin occurrence', occ.name, 'axis x=%.2f m z=%.2f m' % (p.twin_cx / 100, g['zax'] / 100))
