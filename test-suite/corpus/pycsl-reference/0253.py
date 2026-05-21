"""Test 0253 — Concurrent: two mutexes protecting two independent variables"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared a protected_by lock_a
#@ shared b protected_by lock_b
#@ mutex_invariant lock_a: a >= 0
#@ mutex_invariant lock_b: b >= 0
_ = 0  # anchor

import threading
lock_a = threading.Lock()
lock_b = threading.Lock()
a = 0
b = 0

#@ thread_entry
#@ \diverges
def worker_a() -> int:
    #@ critical lock_a
    with lock_a:
        a += 1
    return 0

#@ thread_entry
#@ \diverges
def worker_b() -> int:
    #@ critical lock_b
    with lock_b:
        b += 1
    return 0

if __name__ == "__main__":
    print("PASS")
