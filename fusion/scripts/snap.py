# Viewport image with an explicit camera (activates the station document by name).
# snap(path, eye, target, w, h, ortho=False, fit=False, ext=None): eye/target in metres in the model frame
# (X along track, Y up from top of rail, Z towards the south street). ext = ortho view extent in metres.
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

def snap(path, eye, target, w=1800, h=1100, ortho=False, fit=False, ext=None, persp=None, up=(0, 1, 0)):
    app, design = st.activate()
    vp = app.activeViewport
    cam = vp.camera
    cam.isSmoothTransition = False
    cam.eye = adsk.core.Point3D.create(*[v * 100 for v in eye])
    cam.target = adsk.core.Point3D.create(*[v * 100 for v in target])
    cam.upVector = adsk.core.Vector3D.create(*up)
    cam.cameraType = (adsk.core.CameraTypes.OrthographicCameraType if ortho
                      else adsk.core.CameraTypes.PerspectiveCameraType)
    if persp:
        cam.perspectiveAngle = persp
    if ortho and ext:
        cam.viewExtents = ext * 100
    vp.camera = cam
    if fit:
        vp.fit()
    vp.refresh()
    adsk.doEvents()
    ok = vp.saveAsImageFile(path, w, h)
    if not ok:
        adsk.doEvents()
        ok = vp.saveAsImageFile(path, w, h)
    print('saved', ok, os.path.basename(path))
    return ok


def run(_context: str):
    pass
