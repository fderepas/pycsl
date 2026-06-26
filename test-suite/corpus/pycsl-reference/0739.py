"""Test 0739 — `-> NoReturn` NR2a negative (normal return rejected).

typing-engagement ty1 (28-0000-typing-spec-4): a `-> NoReturn` function whose
body contains a `return` statement is a static error (NR2a — a `return` is a
normal-exit path; the `false` postcondition would be unprovable). PyCSL
rejects this at the static-semantics seam (`core_ir_semantic._check_noreturn`).
"""
# pycsl-expected: FAIL


def bad() -> NoReturn:
    return 1

if __name__ == "__main__":
    print("FAIL (should not reach)")
