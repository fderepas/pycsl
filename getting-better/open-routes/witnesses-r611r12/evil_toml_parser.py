# EVIL tomllib/_parser: loads returns a fresh counter each call.
_n = [0]
class TOMLDecodeError(ValueError):
    pass
def loads(s, /, *, parse_float=float):
    _n[0] += 1
    return {"a": _n[0]}
def load(fp, /, *, parse_float=float):
    return loads(fp.read().decode())
