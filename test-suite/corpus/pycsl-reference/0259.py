"""Test 0259 — Concurrent: lock_order combined with mutex_invariant on each mutex"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared p protected_by lock_p
#@ shared q protected_by lock_q
#@ mutex_invariant lock_p: p >= 0
#@ mutex_invariant lock_q: q >= 0
#@ lock_order lock_p, lock_q
_ = 0  # anchor

import threading
lock_p = threading.Lock()
lock_q = threading.Lock()
p = 0
q = 0

#@ thread_entry
#@ \diverges
def worker() -> int:
    #@ acquires lock_p
    with lock_p:
        #@ acquires lock_q
        with lock_q:
            p += 1
            q += 1
    return 0

if __name__ == "__main__":
    print("PASS")
