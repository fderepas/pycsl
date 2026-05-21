"""Test 0266 — Concurrent: nested acquires with lock_order declared"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared u protected_by lock_u
#@ shared v protected_by lock_v
#@ lock_order lock_u, lock_v
_ = 0  # anchor

import threading
lock_u = threading.Lock()
lock_v = threading.Lock()
u = 0
v = 0

#@ thread_entry
#@ \diverges
def swap_both() -> int:
    #@ acquires lock_u
    with lock_u:
        #@ acquires lock_v
        with lock_v:
            u += 1
            v += 1
    return 0

if __name__ == "__main__":
    print("PASS")
