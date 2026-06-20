# pycsl_lib/hlib — pure-Python hashlib module
# Specified: hash value is an uninterpreted function.
# Only length contracts are modelled. TCB: hash value, collision resistance.


#@ class invariant self._digest_length == 32
class Sha256:
    def __init__(self, data):
        self._input = []
        self._digest_length = 32
        if data != 0:
            self._input = data

    #@ ensures \length(\result) == 32
    def digest(self) -> list:
        return [0] * 32

    #@ ensures \length(\result) == 64
    def hexdigest(self) -> list:
        return [0] * 64

    #@ \trusted
    def update(self, data):
        i = 0
        n = len(data)
        while i < n:
            self._input.append(data[i])
            i = i + 1


#@ ensures \result._digest_length == 32
def new_sha256(data) -> Sha256:
    return Sha256(data)
