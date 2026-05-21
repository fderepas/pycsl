"""Test 0260 — Concurrent: nested critical sections with lock_order"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared m protected_by lock_m
#@ shared n protected_by lock_n
#@ lock_order lock_m, lock_n
_ = 0  # anchor

import threading
lock_m = threading.Lock()
lock_n = threading.Lock()
m = 0
n = 0

#@ thread_entry
#@ \diverges
def updater() -> int:
    #@ critical lock_m
    with lock_m:
        #@ critical lock_n
        with lock_n:
            m += 1
            n += 1
    return 0

if __name__ == "__main__":
    print("PASS")
