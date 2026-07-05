"""Test 0877 — set-model soundness lock (NEGATIVE twin of 0876). # pycsl-expected: FAIL

The soundness floor for the module-level constant string-set membership recognizer.
"no_such_axiom" is NOT in ROCQ_KERNEL_AXIOM_ALLOWLIST, so `name in ...` is faithfully
false. The contract CLAIMS the membership is True, which is FALSE of the real set, so
it must remain UNPROVEN (neither Alt-Ergo nor Z3 discharges it). If this test ever
PASSES, the disjunction membership lowering has become unsound (a non-member reported
present — severity-1).
"""
# pycsl-expected: FAIL
ROCQ_KERNEL_AXIOM_ALLOWLIST = {
    "propext",
    "Classical.choice",
    "Quot.sound",
}


#@ requires name == "no_such_axiom"
#@ ensures \result == True
def member_wrong_UNSOUND(name: str) -> bool:
    """"no_such_axiom" is absent (membership false) but CLAIMS True. FALSE — must not prove."""
    return name in ROCQ_KERNEL_AXIOM_ALLOWLIST


if __name__ == "__main__":
    # "no_such_axiom" is not in the set, so membership is False, but the contract
    # claims True. FALSE.
    assert member_wrong_UNSOUND("no_such_axiom") is False
