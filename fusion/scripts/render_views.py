# Saves the standard viewport renders into docs/renders/ (repo-relative). run(ctx, only=[names]) for a subset.
import os, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', '..', 'docs', 'renders'))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# name: (eye m, target m, kwargs)
VIEWS = {
    'station-aerial-sw': ((-32, 28, 42), (14, 0, -10), {}),
    'station-aerial-ne': ((75, 30, -55), (25, 0, -10), {}),
    'street-facade-sw': ((-26, 0.2, 21), (6, 2.6, -1.0), {'persp': 0.75}),
    'street-elevation': ((11.5, 1.5, 80), (11.5, 1.5, 0), {'ortho': True, 'ext': 34}),
    'west-end-elevation': ((-80, 1.5, -2.5), (0, 1.5, -2.5), {'ortho': True, 'ext': 20}),
    'plan': ((25, 90, -6), (25, 0, -6), {'ortho': True, 'ext': 75, 'up': (1, 0, 0)}),
    'platform-south-looking-east': ((-6, 2.0, -7.0), (12, 2.4, -2.0), {'persp': 0.75}),
    'platform-north-twin': ((55, 2.0, -14.0), (35, 2.6, -17.5), {'persp': 0.75}),
    'detail-canopy': ((-6.5, 1.8, 5.5), (-0.6, 4.6, -1.5), {'persp': 0.7}),
    'detail-arcade': ((23.5, 1.7, -5.0), (10, 3.6, -3.0), {'persp': 0.75}),
    'detail-window': ((4.1, 2.3, 5.0), (4.1, 2.5, 0), {'persp': 0.7}),
    'detail-stairs': ((-9, 1.0, 12), (-2, -0.5, 1), {'persp': 0.8}),
}


def run(_context: str, only=None, w=2000, h=1200):
    sn = _load('ses_snap', 'snap.py')
    os.makedirs(OUT, exist_ok=True)
    for name, (eye, target, kw) in VIEWS.items():
        if only and name not in only:
            continue
        path = os.path.join(OUT, name + '.png')
        sn.snap(path, eye, target, w=w, h=h, **kw)
        sn.snap(path, eye, target, w=w, h=h, **kw)      # second capture: the first can come back blank
