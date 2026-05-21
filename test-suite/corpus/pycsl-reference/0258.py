"""Test 0258 — Concurrent: lock_order with three mutexes acquired in sequence"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared x protected_by lock_x
#@ shared y protected_by lock_y
#@ shared z protected_by lock_z
#@ lock_order lock_x, lock_y, lock_z
_ = 0  # anchor

import threading
lock_x = threading.Lock()
lock_y = threading.Lock()
lock_z = threading.Lock()
x = 0
y = 0
z = 0

#@ thread_entry
#@ \diverges
def worker() -> int:
    #@ acquires lock_x
    with lock_x:
        #@ acquires lock_y
        with lock_y:
            #@ acquires lock_z
            with lock_z:
                x += 1
                y += 1
                z += 1
    return 0

if __name__ == "__main__":
    print("PASS")
