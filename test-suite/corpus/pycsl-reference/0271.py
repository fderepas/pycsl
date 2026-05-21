"""Test 0271 — Concurrent: two-mutex acquires-releases with lock_order"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared c1 protected_by lock_c1
#@ shared c2 protected_by lock_c2
#@ lock_order lock_c1, lock_c2
_ = 0  # anchor

import threading
lock_c1 = threading.Lock()
lock_c2 = threading.Lock()
c1 = 0
c2 = 0

#@ thread_entry
#@ \diverges
def update_both() -> int:
    #@ acquires lock_c1
    #@ releases lock_c1
    with lock_c1:
        #@ acquires lock_c2
        #@ releases lock_c2
        with lock_c2:
            c1 += 1
            c2 += 1
    return 0

if __name__ == "__main__":
    print("PASS")
