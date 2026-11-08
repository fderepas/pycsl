r"""Test 1798 — WITNESS: `--verify-imports` refusing an imported module that does not verify.

ROUTE #212's certificate (`PYCSL-SEM-IMPORT-UNVERIFIED`). The flag is OFF by default, and
this file only fires the refusal when it is given — so the corpus runner sees it as a plain
file and the `# pycsl-flags:` line supplies the flag. The imported module's own contract is
FALSE of its body (`assigns \nothing` over a write), so it does not verify, and the
importing program must not be allowed to believe it.

One of the refusals `bin/check-refusal-witness-coverage.py` could not even SEE until import
ALIASES were resolved: it is raised as `_PyCSLSemErr212`.
"""
# pycsl-expected: FAIL
# pycsl-flags: --verify-imports --import-path test-suite/fixtures/route212-dep
from badlib import bump

_ = 0  # anchor


#@ requires n >= 0
#@ ensures \result >= 0
def go(n: int) -> int:
    return bump(n)
