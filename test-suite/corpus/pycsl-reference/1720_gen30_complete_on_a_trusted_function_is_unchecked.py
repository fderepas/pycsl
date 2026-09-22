r"""Test 1720 — gen #30: `#@ complete` / `#@ disjoint` on a BODYLESS function were unchecked
claims, and are now refused.

`_desugar_acts` turns `complete`/`disjoint` into function-ENTRY `#@ assert` checkpoints
stamped on the first body statement. A `\trusted` / `\abstract` body is never lowered, so
the stamp evaporates — the same shape as routes #210 and #211 in the `happy` forms.

MEASURED: the guards below (`x < 0` and `x > 100`) leave 0..100 covered by NEITHER act, so
`#@ complete small, big` is FALSE. Without `#@ \trusted` the file FAILS on its entry
assert, exactly as it should. WITH `#@ \trusted` it printed "Verification SUCCESS".

NOT A ROUTE, AND THE DISTINCTION IS RECORDED HONESTLY: the caller exploit was built and
REFUSED. A caller of `f` could NOT prove `\result == 1 or \result == 2` (CPython answers 7
for `x = 5`), so nothing downstream consumes the false completeness today. This file is
sound-by-rejection ahead of the day something does, and it cost nothing — no corpus file,
mirror file or stdlib stub carries `complete`/`disjoint` on a trusted function.

Controls: 0454 and 0455 (the act-block witnesses) still PROVE.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ act small:
#@     given x < 0
#@     ensures \result == 1
#@ act big:
#@     given x > 100
#@     ensures \result == 2
#@ complete small, big
#@ disjoint small, big
#@ \trusted
def f(x: int) -> int:
    if x < 0:
        return 1
    if x > 100:
        return 2
    return 7
