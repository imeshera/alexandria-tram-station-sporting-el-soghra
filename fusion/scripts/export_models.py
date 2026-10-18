# Exports models/Sporting El Soghra Station.f3d and .step WITHOUT the photo underlays.
# Procedure (each step its own call, saves upload in the background):
#   1. save the document (save_doc.py) and wait until the new version has uploaded;
#   2. close it and reopen the latest version (a canvas deleted in the session that created it can leave its
#      image in the archive; deleting it right after a fresh open does not);
#   3. run this script: deletes every canvas in memory, exports F3D + STEP, closes WITHOUT saving and reopens the
#      latest version, so the stored design keeps its underlay.
# Check afterwards: unzip -l "<f3d>" | grep -iE '\.(jpe?g|png)' must print nothing. The STEP is zipped for git.
import os, importlib.util
import adsk.core, adsk.fusion
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..', '..', 'models'))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


st = _load('ses_stlib', 'lib/stlib.py')


def reopen_latest(_context=''):
    """Close the station document (it must be unmodified) and open its latest saved version."""
    app = adsk.core.Application.get()
    doc = [d for d in app.documents if d.name == st.DOC][0]
    if doc.isModified:
        raise RuntimeError('document has unsaved changes')
    df = doc.dataFile
    latest = max(df.versions, key=lambda v: v.versionNumber)
    doc.close(False)
    nd = app.documents.open(latest)
    print('opened', nd.name, 'v%d' % nd.dataFile.versionNumber)


def run(_context: str, reopen=True):
    app, design = st.activate()
    doc = app.activeDocument
    if doc.isModified:
        raise RuntimeError('open the latest saved version first (reopen_latest)')
    df = doc.dataFile
    root = design.rootComponent
    n = root.canvases.count
    for i in range(n - 1, -1, -1):
        if not root.canvases.item(i).deleteMe():
            raise RuntimeError('canvas delete failed')
    print('canvases deleted in memory:', n)
    os.makedirs(OUT, exist_ok=True)
    em = design.exportManager
    base = os.path.join(OUT, st.DOC)
    ok1 = em.execute(em.createFusionArchiveExportOptions(base + '.f3d'))
    ok2 = em.execute(em.createSTEPExportOptions(base + '.step', root))
    print('f3d', ok1, 'step', ok2)
    doc.close(False)
    if reopen:
        latest = max(df.versions, key=lambda v: v.versionNumber)
        nd = app.documents.open(latest)
        print('reopened', nd.name, 'v%d' % nd.dataFile.versionNumber)
