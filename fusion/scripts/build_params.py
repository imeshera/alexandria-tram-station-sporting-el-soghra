# Creates the user parameters from params.py (missing ones only; pass force=True to reset every expression and
# comment to the values in params.py).
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
params = _load('ses_params', 'params.py')

import adsk.core


def run(_context: str, force=False):
    app, design = st.activate()
    up = design.userParameters
    added = changed = 0
    for n, e, u, c in params.PARAMS:
        p = up.itemByName(n)
        if p is None:
            up.add(n, adsk.core.ValueInput.createByString(e), u, c)
            added += 1
        elif force and (p.expression != e or p.comment != c):
            p.expression = e
            p.comment = c
            changed += 1
    print('parameters: %d added, %d reset, %d total' % (added, changed, up.count))
