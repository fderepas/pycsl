# Advice probe (route #439, PYCSL-R430-CALLEE-UNDERIVABLE-HASH through an imported user module):
# witness 6621 with `\all` dropped from the caller. Expected: VERIFIES.
# pycsl-flags: --import-path ../../../../test-suite/corpus/pycsl-reference
from typing import Any, Dict
from multi_file_lib.r439_hashlib import h


#@ ensures \result == n + 1
def f(m: Dict[str, Any], n: int) -> int:
    return h(m, n)
