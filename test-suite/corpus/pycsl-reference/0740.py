"""Test 0740 — `-> NoReturn` NR3 negative (dead successor rejected).

typing-engagement ty1 (28-0000-typing-spec-4): a statement following a call to
a NoReturn function is statically unreachable (NR3 — the callee's `false`
postcondition makes the continuation contradictory). PyCSL reports this as
dead code (`core_ir_semantic._check_noreturn_successors`).
"""
# pycsl-expected: FAIL
from typing import NoReturn


def g() -> NoReturn:
    raise Exception()


def caller() -> int:
    g()
    return 1  # dead code — unreachable

if __name__ == "__main__":
    print("FAIL (should not reach)")
