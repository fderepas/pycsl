"""Test 0407 — UB-7.1: `#@ allow_iteration_mutation` opts out.

Uses `--no-proof` to keep the test focused on the opt-in path (the
detector accepts the loop) — full proof would need loop invariants.
"""
# pycsl-flags: --no-proof
_ = 0  # anchor
#@ requires \length(arr) >= 0
#@ ensures True
#@ assigns arr[0..\length(arr)]
def explicit_mutate(arr: list) -> None:
    #@ allow_iteration_mutation
    for x in arr:
        arr.append(x + 1)
        return


if __name__ == "__main__":
    pass
