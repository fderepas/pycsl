"""set-model FALSE-TWIN driver — must be UNPROVEN.

"no_such_axiom" is NOT in ROCQ_KERNEL_AXIOM_ALLOWLIST, so `name in ...` is faithfully
false. The contract CLAIMS the membership is True, which is FALSE of the real set, so
it must NOT prove. A green proof here would mean the disjunction membership lowering is
unsound (a non-member reported present — severity-1).
"""
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
    assert member_wrong_UNSOUND("no_such_axiom") is False
