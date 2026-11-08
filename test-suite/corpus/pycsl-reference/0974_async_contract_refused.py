"""Test 0974 — a `#@` contract on an `async def` is REFUSED, because it was SILENTLY
DISCARDED while the run reported "All contracts formally proven".

This is Module 3's `#@`-ATTACHMENT surface, audited the same mechanical way as the Module 5
dispatch table. `Module1_Ingestor` emits an `AsyncFunctionDef` under the SAME `FunctionDef`
anchor as a plain `def` (`if t in ("FunctionDef", "AsyncFunctionDef"): return
mk("FunctionDef", nm)`), so the contract IS extracted and IS parsed into `contracts_map`.
But `PyCSLWeaver` defines only `visit_FunctionDef`, so the clauses are never attached to
the node; and `PyCSLToJSONEmitter` has no `AsyncFunctionDef` visitor either, so the whole
coroutine never reaches the IR. Measured, before the refusal:

    class C:
        #@ ensures \result == 1                <-- FALSE OF THE PROGRAM
        async def m(self) -> int:
            return 2

    [+] Verification SUCCESS! All contracts formally proven.

The emitted WhyML contained no `m` at all; for a file whose ONLY function is the coroutine
the emitted module was `module PyCSL_Program use int.Int ... end` — empty — and the run
still printed the success banner.

SCOPE OF THE REFUSAL. Only a CONTRACT-CARRYING `async def` is refused. An uncontracted
coroutine claims nothing, and refusing it would reject files whose async code is irrelevant
to the proof — 11 such definitions live in `python-reference` (0098, 0099, 0152, 0207,
0208, 0209), every one nested inside a synchronous function and every one uncontracted. The
refusal is therefore INERT on all four populations: 0 contracted coroutines in
`pycsl-reference`, `python-reference`, the mirror, `src/pycsl_lib` and the live emitter.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL


class C:
    #@ requires True
    #@ ensures self.v == 0
    #@ assigns self.v
    def __init__(self) -> None:
        self.v: int = 0

    #@ requires True
    #@ ensures \result == 2
    #@ assigns \nothing
    async def m(self) -> int:
        return 2
