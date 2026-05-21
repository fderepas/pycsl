"""Test 0257 — Concurrent: lock_order with two mutexes, nested acquisition in correct order"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared a protected_by lock_a
#@ shared b protected_by lock_b
#@ lock_order lock_a, lock_b
_ = 0  # anchor

import threading
lock_a = threading.Lock()
lock_b = threading.Lock()
a = 0
b = 0

#@ thread_entry
#@ \diverges
def worker() -> int:
    #@ acquires lock_a
    with lock_a:
        #@ acquires lock_b
        with lock_b:
            a += 1
            b += 1
    return 0

if __name__ == "__main__":
    print("PASS")
