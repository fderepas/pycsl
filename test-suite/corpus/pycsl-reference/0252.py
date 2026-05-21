"""Test 0252 — Concurrent: two thread_entry functions sharing one counter"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared total protected_by lock_total
#@ mutex_invariant lock_total: total >= 0
_ = 0  # anchor

import threading
lock_total = threading.Lock()
total = 0

#@ thread_entry
#@ \diverges
def producer() -> int:
    #@ critical lock_total
    with lock_total:
        total += 1
    return 0

#@ thread_entry
#@ \diverges
def consumer() -> int:
    #@ critical lock_total
    with lock_total:
        total += 1
    return 0

if __name__ == "__main__":
    print("PASS")
