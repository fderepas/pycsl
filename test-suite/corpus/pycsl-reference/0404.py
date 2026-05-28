"""Test 0404 — UB-7.1: appending to the iterated list is rejected."""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires \length(arr) >= 0
#@ ensures True
#@ assigns arr[0..\length(arr)]
def append_during_for(arr: list) -> None:
    for x in arr:
        arr.append(x + 1)


if __name__ == "__main__":
    pass
