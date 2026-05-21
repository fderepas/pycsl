"""Test 0278 — Concurrent: critical section with conditional logic inside body"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared items protected_by lock_items
#@ mutex_invariant lock_items: items >= 0
_ = 0  # anchor

import threading
lock_items = threading.Lock()
items = 0

#@ thread_entry
#@ \diverges
def conditional_worker() -> int:
    #@ critical lock_items
    with lock_items:
        if items < 100:
            items += 1
    return 0

if __name__ == "__main__":
    print("PASS")
