# Runs the whole build in order: parameters, pavilion, site (embankment/track/platform), stairs, twin,
# overhead line, appearances. Each step can also be run on its own.
import os, time

ORDER = ['build_params.py', 'build_pavilion.py', 'build_site.py', 'build_stairs.py', 'build_twin.py',
         'build_ocs.py', 'build_appearance.py']


def run(_context: str, steps=None):
    here = os.path.dirname(os.path.abspath(__file__))
    for s in steps or ORDER:
        t = time.time()
        path = os.path.join(here, s)
        ns = {'__name__': 'fusion_script', '__file__': path}
        exec(compile(open(path).read(), path, 'exec'), ns)
        ns['run'](_context)
        print('%s: %.1f s' % (s, time.time() - t))
