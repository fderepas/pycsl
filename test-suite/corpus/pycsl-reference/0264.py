"""Test 0264 — Concurrent: acquires in non-thread-entry function, local variable read from shared"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared count protected_by lock_count
#@ mutex_invariant lock_count: count >= 0
_ = 0  # anchor

import threading
lock_count = threading.Lock()
count = 0

def read_count() -> int:
    snapshot = 0
    #@ acquires lock_count
    with lock_count:
        snapshot = count
    return snapshot

if __name__ == "__main__":
    print("PASS")
