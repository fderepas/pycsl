"""Test 0261 — Concurrent: two thread_entry functions both respecting same lock_order"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared r protected_by lock_r
#@ shared s protected_by lock_s
#@ lock_order lock_r, lock_s
_ = 0  # anchor

import threading
lock_r = threading.Lock()
lock_s = threading.Lock()
r = 0
s = 0

#@ thread_entry
#@ \diverges
def worker_a() -> int:
    #@ acquires lock_r
    with lock_r:
        #@ acquires lock_s
        with lock_s:
            r += 1
    return 0

#@ thread_entry
#@ \diverges
def worker_b() -> int:
    #@ acquires lock_r
    with lock_r:
        #@ acquires lock_s
        with lock_s:
            s += 1
    return 0

if __name__ == "__main__":
    print("PASS")
