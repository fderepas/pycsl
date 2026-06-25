"""Test 0700 — strings: IMPORTED str-FIELD record construct + read-back (Gap 2a).

Gap 2a (10-2006-convergence-spec-2): constructing an imported class with a `str` instance
field needs a TYPE-CORRECT record literal. Before the fix `Tmpl()` lowered to the ill-typed
`{ template = 0 }` (int default against a `string`-typed field, L3-tc ✗); after the fix the
`str` field defaults to the empty-string witness `{ template = "" }`.

This driver constructs the imported `Tmpl`, writes its `str` field via `set_template`, and
reads it back — proving the method's own read-after-write `ensures` (`self.template == t`)
propagates through the constructed instance.

STATUS — **PROVES**.
"""
# pycsl-flags: --memory-model hoare
from multi_file_lib.classmod_stub import Tmpl

t = Tmpl()


#@ ensures \result == n
#@ assigns t.template
def set_and_read(n: str) -> str:
    t.set_template(n)
    return t.template


if __name__ == "__main__":
    print("PASS")
