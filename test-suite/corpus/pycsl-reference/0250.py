"""Test 0250 — Concurrent: shared variable declaration with mutex invariant"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared counter protected_by lock_counter
#@ mutex_invariant lock_counter: counter >= 0
_ = 0  # anchor

import threading
lock_counter = threading.Lock()
counter = 0

#@ thread_entry
#@ \diverges
def worker() -> int:
    #@ critical lock_counter
    with lock_counter:
        counter += 1
    return 0

if __name__ == "__main__":
    print("PASS")
