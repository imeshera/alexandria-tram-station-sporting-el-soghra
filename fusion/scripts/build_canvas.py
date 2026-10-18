# Adds a camera-matched reference canvas (photo underlay) for overlay checks, plus a named view that reproduces
# the photo's camera. The image itself is not in the repository: pass its path, e.g.
#   run(ctx, image='<path>/IMG_3282.JPG', key='IMG_3282')
# The canvas lies on a plane perpendicular to the camera axis, `dist` metres in front of the camera (behind the
# station), scaled so that it exactly fills the view from the named view. Its light bulb is switched off after
# creation (turn it on in the browser to compare). Exports must be made with all canvases deleted (see README).
import math
import os, importlib.util
import adsk.core, adsk.fusion
HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


st = _load('ses_stlib', 'lib/stlib.py')

# camera calibrations (metres, model frame); f in pixels of the full image; w, h image size in pixels
CAMERAS = {
    # owner's photo, iPhone 14 Pro Max main camera at 35 mm-eq crop, 22 Jan 2026 (see references/notes/dimensions.md)
    'IMG_3282': dict(eye=(-28.5, -1.55, 19.0), dirn=(0.864, 0.075, -0.503), f=4099.0, w=2268, h=4032),
}


def delete_canvases(design, key=''):
    """Delete canvases (name starting with key) of the root component. Canvas.deleteMe can fail on a canvas
    created in the same transaction as a later error; then the canvas is removed through the timeline, which is
    only safe when it is the last timeline item."""
    root = design.rootComponent
    n = 0
    for i in range(root.canvases.count - 1, -1, -1):
        cv = root.canvases.item(i)
        if not cv.name.startswith(key):
            continue
        try:
            cv.deleteMe()
        except Exception:
            tl = design.timeline
            to = cv.timelineObject
            if to is None or to.index != tl.count - 1:
                raise
            to.rollTo(True)
            tl.deleteAllAfterMarker()
            tl.moveToEnd()
        n += 1
    return n


def run(_context: str, image=None, key='IMG_3282', dist=70.0, opacity=60):
    app, design = st.activate()
    root = design.rootComponent
    cam = CAMERAS[key]
    if image is None:
        raise RuntimeError('pass image=<path to the photo>')
    d = adsk.core.Vector3D.create(*cam['dirn']); d.normalize()
    r = d.crossProduct(adsk.core.Vector3D.create(0, 1, 0)); r.normalize()      # camera right
    up = r.crossProduct(d); up.normalize()
    e = adsk.core.Point3D.create(*[v * 100 for v in cam['eye']])
    D = dist * 100
    C = adsk.core.Point3D.create(e.x + d.x * D, e.y + d.y * D, e.z + d.z * D)
    W = D * cam['w'] / cam['f']
    H = D * cam['h'] / cam['f']
    # remove an earlier canvas of the same key
    delete_canvases(design, key)
    for i in range(root.features.baseFeatures.count - 1, -1, -1):
        if root.features.baseFeatures.item(i).name == 'Canvas plane ' + key:
            root.features.baseFeatures.item(i).deleteMe()
    bf = root.features.baseFeatures.add()
    bf.startEdit()
    pin = root.constructionPlanes.createInput()
    pin.setByPlane(adsk.core.Plane.createUsingDirections(C, r, up))
    pin.targetBaseOrFormFeature = bf
    plane = root.constructionPlanes.add(pin)
    plane.name = 'Canvas plane ' + key
    bf.finishEdit()
    bf.name = 'Canvas plane ' + key
    ci = root.canvases.createInput(image, plane)
    pl = ci.plane
    O, pu, pv = pl.origin, pl.uDirection, pl.vDirection
    pu.normalize(); pv.normalize()
    co = O.vectorTo(C)
    a, b = W * r.dotProduct(pu), H * up.dotProduct(pu)
    c_, d_ = W * r.dotProduct(pv), H * up.dotProduct(pv)
    m = adsk.core.Matrix2D.create()
    m.setWithArray([a, b, co.dotProduct(pu) - 0.5 * a - 0.5 * b,
                    c_, d_, co.dotProduct(pv) - 0.5 * c_ - 0.5 * d_,
                    0, 0, 1])
    ci.transform = m
    ci.opacity = opacity
    ci.isDisplayedThrough = False
    cv = root.canvases.add(ci)
    cv.name = key + ' (camera-matched underlay)'
    # named view reproducing the photo camera
    vp = app.activeViewport
    camo = vp.camera
    camo.isSmoothTransition = False
    camo.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
    camo.eye = e
    camo.target = adsk.core.Point3D.create(e.x + d.x * 3000, e.y + d.y * 3000, e.z + d.z * 3000)
    camo.upVector = adsk.core.Vector3D.create(0, 1, 0)
    camo.perspectiveAngle = 2 * math.atan(cam['h'] / 2 / cam['f'])
    vp.camera = camo
    for i in range(design.namedViews.count - 1, -1, -1):
        if design.namedViews.item(i).name == key:
            design.namedViews.item(i).deleteMe()
    design.namedViews.add(camo, key)
    print('canvas', cv.name, 'W %.1f m H %.1f m at %.0f m' % (W / 100, H / 100, dist))
    return cv
