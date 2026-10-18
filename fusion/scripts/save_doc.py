# Saves the station document with a version message, after checking it lives in the right project and folder.
import adsk.core

DOC = 'Sporting El Soghra Station'
PROJECT = 'Eshera-Personal'
FOLDER = 'Alexandria Tram Station - Sporting El Soghra'


def save(msg):
    app = adsk.core.Application.get()
    doc = [d for d in app.documents if d.name == DOC][0]
    df = doc.dataFile
    if df.parentProject.name != PROJECT or df.parentFolder.name != FOLDER:
        raise RuntimeError('save guard: %s / %s' % (df.parentProject.name, df.parentFolder.name))
    doc.activate()
    ok = doc.save(msg)
    print('saved', ok, msg)


def run(_context: str):
    pass
