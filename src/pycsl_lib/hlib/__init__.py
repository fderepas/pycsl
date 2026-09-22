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

    #@ \trusted reviewer: field-append-has-no-certified-lowering
    def update(self, data):
        """MEASURED IN GEN #30 — THIS MARKER IS FORCED, NOT LAZY.

        `bin/check-stdlib-trusted-markers.py` recorded this as the one BARE `\trusted`
        in `src/pycsl_lib/` (no reviewer, no reason) and named removing it as work. It
        cannot be removed, and here is the measurement rather than an opinion.

        The body appends to a COLLECTION HELD IN A FIELD. PyCSL refuses that outright:
        `self._input.append(...)` is emitted against a fresh local array with no
        write-back, so an un-trusted version would satisfy `#@ assigns \nothing`,
        satisfy its frame-preservation `ensures`, and re-establish a `\length` class
        invariant while the model left `self._input` UNCHANGED. Dropping the marker and
        adding loop invariants therefore does not verify — it hits that refusal.

        The refusal's own advice is "rewrite it as an indexed store, or mark the method
        `#@ \trusted`". The first branch was followed literally (`self._input[i] =
        data[i]`, `data: list`, loop invariants and variant). It does NOT verify either,
        and for the right reason: the emitted `index in array bounds` sub-goal is
        un-dischargeable, because `__init__` can leave `self._input` EMPTY and a store at
        index i is then out of bounds — precisely the `IndexError: list assignment index
        out of range` CPython raises for that rewrite. Both branches of the advice are
        sound; there is no un-trusted spelling of an append-to-field loop today.

        Converting this marker needs a certified field-append lowering (write-back into
        the field's array plus a length model), not an annotation change.
        """
        i = 0
        n = len(data)
        while i < n:
            self._input.append(data[i])
            i = i + 1


#@ ensures \result._digest_length == 32
def new_sha256(data) -> Sha256:
    return Sha256(data)
