"""Test 0735 — negative: reassigning a module-level `Final` name (F1).

typing-engagement ty1 (27-0000-typing-spec-3): a module-level `Final` name may
be written ONLY at its declaration. A reassignment inside a function body is a
static error, raised by `core_ir_semantic._check_final` (F1 arm — a syntactic
write-site check, NOT a VC). The run terminates with a PIPELINE ERROR (exit 1).
Note: the runtime would happily execute the reassignment (FR3 — the runtime
does NOT enforce the write-restriction); the rejection is a static-plane
judgment only (FD1 divergence).
"""
# pycsl-expected: FAIL
from typing import Final

x: Final[int] = 5

#@ assigns \nothing
def f() -> int:
    x = 10
    return x
