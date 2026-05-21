"""Test 0254 — Concurrent: unprotected write to shared variable → semantic error"""
# pycsl-expected: FAIL
#@ shared counter protected_by lock_counter
_ = 0  # anchor

import threading
lock_counter = threading.Lock()
counter = 0

def bad_worker() -> int:
    counter += 1
    return counter

if __name__ == "__main__":
    print("PASS")
