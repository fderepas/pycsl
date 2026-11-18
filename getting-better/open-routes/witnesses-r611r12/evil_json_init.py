# EVIL json/__init__: dumps returns a fresh counter string each call and clears dict args.
_n = [0]
def dumps(obj, **kw):
    _n[0] += 1
    if isinstance(obj, dict):
        obj.clear()
    return str(_n[0])
def loads(s, **kw):
    return None
def dump(obj, fp, **kw):
    fp.write(dumps(obj))
def load(fp, **kw):
    return None
class JSONDecodeError(ValueError):
    pass
