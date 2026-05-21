"""Test 0255 — Concurrent: nested acquire without lock_order → semantic error"""
# pycsl-expected: FAIL
#@ shared a protected_by lock_a
#@ shared b protected_by lock_b
_ = 0  # anchor

import threading
lock_a = threading.Lock()
lock_b = threading.Lock()
a = 0
b = 0

def bad_nested() -> int:
    #@ acquires lock_a
    with lock_a:
        #@ acquires lock_b
        with lock_b:
            a += 1
            b += 1
    return 0

if __name__ == "__main__":
    print("PASS")
