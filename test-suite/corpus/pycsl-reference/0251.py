"""Test 0251 — Concurrent: critical section with protected_by and invariant preservation"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared x protected_by lock_a
#@ mutex_invariant lock_a: x >= 0
_ = 0  # anchor

import threading
lock_a = threading.Lock()
x = 0

#@ thread_entry
#@ \diverges
def increment() -> int:
    #@ critical lock_a
    with lock_a:
        x += 1
    return 0

#@ thread_entry
#@ \diverges
def read_and_check() -> int:
    #@ critical lock_a
    with lock_a:
        result = x
    return 0

if __name__ == "__main__":
    print("PASS")
