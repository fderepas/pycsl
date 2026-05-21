"""Test 0262 — Concurrent: acquires annotation on with block"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared val protected_by lock_a
#@ mutex_invariant lock_a: val >= 0
_ = 0  # anchor

import threading
lock_a = threading.Lock()
val = 0

#@ thread_entry
#@ \diverges
def worker() -> int:
    #@ acquires lock_a
    with lock_a:
        val += 1
    return 0

if __name__ == "__main__":
    print("PASS")
