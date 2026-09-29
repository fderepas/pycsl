"""Test 0644 — a dynamic exec is a worst-case mutator under HAPPY confinement (07-1839 P5).

A constant exec is spliced away before Module4 (P5b), so any exec reaching the HAPPY validator is
DYNAMIC and may write anything — including the protected region. A non-exempt method containing one
therefore cannot be confined by a HAPPY property: it is rejected with a hard error (the same teeth as
a non-exempt `\trusted` mutator without `#@ \preserves`, test 0462). To use exec here one must add the
method to the property's `except` set (acknowledging it as a trusted writer).

(#49) gen #33, ROUTE #229 — THIS FILE IS NOW REFUSED BEFORE IT REACHES THE DEMONSTRATION
ABOVE, AND THAT IS A REAL LOSS OF COVERAGE, recorded here rather than left to be discovered.
A bare dynamic `exec` inside a function was believed confined ("its assignments land in the
discarded locals snapshot"); a `global` declaration inside the exec'd text redirects the
assignment into the GLOBALS mapping, which at function scope is the real module globals, and
a witness PROVED `\result == 3` where CPython returns 5 (route229, corpus 1917). The text is
DYNAMIC, so the emitter cannot read it and cannot tell this file's safe `exec` from that one;
the only sound position is to refuse a non-constant `exec` wherever it stands.

So this file stays expected-FAIL and still FAILS, but by a REFUSAL rather than by the
mechanism it was written to exercise. The `\in_scope` havoc and the frame-taint machinery
still exist in the emitter and are no longer reachable from the corpus language — which
raises a question worth someone's time: IS THAT MACHINERY NOW DEAD CODE? It is recorded in
the gen #33 handoff as an open follow-up, not answered here.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ class invariant \length(self.disk) >= 4096
#@ happy region_integrity:
#@     region 512 .. 2560
#@     writes self.disk outside region
#@     except _write_meta
class Store:
    def __init__(self) -> None:
        self.disk: list = bytearray(4096)

    def _write_meta(self, i: int, v: int) -> None:
        self.disk[i] = v

    def run(self, code: str) -> None:
        exec(code)
