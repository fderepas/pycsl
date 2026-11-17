# EVIL hashlib replacement: every sha256() object has a fresh counter digest.
_n = [0]
class _H:
    def __init__(self, b=b''):
        _n[0] += 1
        self._v = _n[0]
    def update(self, b):
        pass
    def hexdigest(self):
        return "%064x" % self._v
    def digest(self):
        return self._v.to_bytes(32, "big")
def sha256(b=b'', **kw):
    return _H(b)
def md5(b=b'', **kw):
    return _H(b)
