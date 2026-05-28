"""Test 0415 — UB-7.3: unprotected shared variable under --strict-concurrent-checks."""
# pycsl-flags: --memory-model concurrent --strict-concurrent-checks
# pycsl-expected: FAIL
_ = 0  # anchor
#@ shared counter
import threading
counter = 0


#@ thread_entry
#@ \diverges
#@ requires True
#@ ensures True
#@ assigns \nothing
def worker() -> int:
    return 0


if __name__ == "__main__":
    pass
