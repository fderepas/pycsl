"""Test 0875 — string-valued `or`/`and` soundness lock (NEGATIVE twin of 0874). # pycsl-expected: FAIL

The soundness floor for the string-valued `or`/`and` recognizer. `"a" or "b"`
faithfully returns "a" (the first operand is non-empty), never "b". The contract
CLAIMS the WRONG branch ("b"), which is FALSE of the real semantics, so it must
remain UNPROVEN (neither Alt-Ergo nor Z3 discharges it). If this test ever
PASSES, the string-ITE lowering has become unsound (a wrong-branch string `or`
proved green — severity-1).
"""
# pycsl-expected: FAIL


#@ ensures \result == "b"
def or_wrong_UNSOUND() -> str:
    """Returns "a" or "b" (== "a") but CLAIMS "b". FALSE — must not prove."""
    return "a" or "b"


if __name__ == "__main__":
    assert or_wrong_UNSOUND() == "a"
