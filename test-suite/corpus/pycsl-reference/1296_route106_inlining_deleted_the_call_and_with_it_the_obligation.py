# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL
"""1296 — (#49) ROUTE #106 EXPLOIT ARM: a method call on a MODULE-GLOBAL instance is
INLINED, so it never reaches the call-site wrap at all — and the callee's raise became the
CALLER's own emitted `raises { ValueError }` while the caller declared
`#@ no_exception ValueError`.

This SURVIVED route #105's repair, which is what makes it its own route rather than a
footnote. #105 threads the receiver resolution into `_wrap_call_with_callee_raises_assert`,
but that wrap lives at a CALL SITE, and `frontend/ir_inline.py` runs EARLIER, on the IR, and
SPLICES THE CALLEE BODY IN. By the time Module 6 looks, there is no call left to wrap.

MEASURED AT ac2ef23e — the emitted WhyML states the contradiction out loud:

    let caller (k: int) : int
      raises { ValueError }                    <- Why3 is TOLD the function raises
    = let _inl_res__inl1 = ref 0 in
      if (k < 0) then begin raise ValueError end; ...

and PyCSL reported `Verification SUCCESS! All contracts formally proven.` for a function whose
source says `#@ no_exception ValueError`. CPython `caller(-1)` RAISES. The emitted signature
contradicted the source directive and NOTHING compared the two.

It was inlined EVEN WHEN THE CALLEE WAS `\trusted`: `val helper__f` was emitted and never
called, so the trust boundary was spliced straight through.

>>> A TRANSFORMATION THAT REMOVES A SYNTACTIC FORM REMOVES EVERY OBLIGATION KEYED ON THAT
>>> FORM. Inlining is semantics-preserving for the VALUE and silently not for the CHECK,
>>> because the check was attached to the CALL NODE rather than to the CALLEE.

THE REPAIR PRESERVES THE CAPABILITY RATHER THAN REFUSING: such a callee is treated as
`#@ no_inline` FOR THIS CALLER ONLY, so the call survives to Module 6 and lands on the
existing, already-gated wrap. Nothing that used to be accepted is rejected — the obligation
simply becomes visible, which is what the user asked for by writing `no_exception`.

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


_h = Helper()


#@ no_exception ValueError
def caller(k: int) -> int:
    return _h.f(k)
