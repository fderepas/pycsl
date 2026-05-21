"""Test 0265 — Concurrent: acquires in a non-thread-entry helper called from thread_entry"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared items protected_by lock_items
#@ mutex_invariant lock_items: items >= 0
_ = 0  # anchor

import threading
lock_items = threading.Lock()
items = 0

def add_item() -> int:
    #@ acquires lock_items
    with lock_items:
        items += 1
    return 0

#@ thread_entry
#@ \diverges
def producer() -> int:
    add_item()
    return 0

if __name__ == "__main__":
    print("PASS")
