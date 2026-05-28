"""Test 0405 — UB-7.1: popping from the iterated list is rejected."""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires \length(arr) >= 0
#@ ensures True
#@ assigns arr[0..\length(arr)]
def pop_during_for(arr: list) -> None:
    for x in arr:
        arr.pop()


if __name__ == "__main__":
    pass
