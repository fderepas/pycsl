"""Test 0560 — negative: a non-terminating lemma cannot prove False (the true boundary).

`bogus` recurses on `n` UNCHANGED (no structurally-decreasing argument, no `#@ \variant`)
while claiming `ensures 1 == 2`. Why3's termination VC fails ("Cannot prove termination"),
so the lemma's conclusion is NEVER exported — you cannot prove `False` by ill-founded
recursion. This is the genuine soundness boundary for recursive lemmas: **Why3 owns
termination/well-foundedness** (it infers structural variants and rejects ill-founded
recursion), so PyCSL no longer requires `#@ \variant` (remains-2.md decision A). Contrast
0570, where a structurally-recursive lemma with no variant PROVES.

Committed `# pycsl-expected: FAIL` and STAYS failing.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ lemma
#@ ensures 1 == 2
#@ assigns \nothing
def bogus(n: int) -> None:
    bogus(n)
