"""Test 0407 — UB-7.1: `#@ allow_iteration_mutation` opts out.

`--no-proof` keeps the test focused on the opt-in path (the detector ACCEPTS the loop);
a full proof would need loop invariants.

RELAUNCH #48: `arr` is now a LOCAL rather than a PARAMETER, for the reason recorded in 0406
— route #49 made an `append` to a list PARAMETER a designed refusal, because the snapshot
lowering made it invisible to the caller. The detector's subject is unchanged: the SAME
container is iterated and mutated, and `#@ allow_iteration_mutation` is what lets it
through."""
# pycsl-flags: --no-proof
_ = 0  # anchor
#@ requires True
#@ ensures True
#@ assigns \nothing
def explicit_mutate() -> None:
    arr = [1, 2, 3]
    #@ allow_iteration_mutation
    for x in arr:
        arr.append(x + 1)
        return


if __name__ == "__main__":
    pass
