"""Test 0256 — Concurrent: mutex invariant violated on release → proof failure"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model concurrent
#@ shared x protected_by lock_x
#@ mutex_invariant lock_x: x >= 0
_ = 0  # anchor

import threading
lock_x = threading.Lock()
x = 0

#@ thread_entry
#@ \diverges
def bad_worker() -> int:
    #@ critical lock_x
    with lock_x:
        x = -1
    return 0

if __name__ == "__main__":
    print("PASS")
