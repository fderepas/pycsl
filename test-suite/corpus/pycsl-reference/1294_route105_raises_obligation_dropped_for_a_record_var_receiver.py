# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL
"""1294 — (#49) ROUTE #105 EXPLOIT ARM: a `#@ no_exception E` caller calling through a
RECORD-VARIABLE receiver had its obligation discharged by NOBODY.

Route #100 repaired this clause for the `self.<m>` receiver. `_module_func_raises` is keyed
on the IR FUNCTION NAME (a method is `<cls>__<m>`), and route #100's `_r100n` flattened
`self.<m>` into that space — but handed every OTHER receiver its SOURCE spelling. The literal
string `"c.f"` is never a key of that registry, the lookup missed,
`_wrap_call_with_callee_raises_assert` returned `inner` UNTOUCHED, and the caller's
`#@ no_exception ValueError` became an unchecked assertion.

MEASURED AT ac2ef23e, and read off the emitted WhyML rather than inferred:

    self.f(k)  ->  begin assert { not ((k < 0)) };
                   try (self_f_1 k) with ValueError -> absurd end end     ->  FAILS
    c.f(k)     ->  (c_f_1 k)                                              ->  PROVES

with `#@ no_exception ValueError` as the caller's ONLY claim, while CPython `caller(-1)`
RAISES ValueError.

>>> A REPAIR KEYED ON A RECEIVER SPELLING COVERS THE RECEIVERS ITS AUTHOR HAD IN VIEW. The
>>> guard was written about the SYNTAX of the call site; the obligation is about WHICH
>>> CALLEE IS RESOLVED. The correct key was already being computed 600 lines above, in
>>> `_resolve_dotted_signature`, from the same two receiver maps — it was never threaded.

NOTE ON THE FIRST ATTEMPT AT THIS WITNESS, because it is the more useful half: written with a
FIELDLESS `Helper`, it FAILED at baseline, which looked like "the route is already closed".
Reading WHICH goal failed: a fieldless class is modelled `type helper = int`, so the callee's
`ensures \result >= 0` vanished along with the wrap and the failure was an unrelated
unprovable postcondition. A PROBE WHOSE OWN POSITIVE CONTROL REFUSES HAS MEASURED NOTHING —
that attempt is logged VACUOUS in probes.tsv, never folded into FAIL-CLOSED.

Must FAIL.
"""


class Helper:
    def __init__(self) -> None:
        self.tag = 0

    #@ raises ValueError when x0 < 0
    #@ ensures \result >= 0
    def f(self, x0: int) -> int:
        if x0 < 0:
            raise ValueError("neg")
        return x0


#@ no_exception ValueError
def caller(k: int) -> int:
    c = Helper()
    return c.f(k)
