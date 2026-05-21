"""Test 0268 — Concurrent: releases annotation on with block, local variable only inside"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared shared_val protected_by lock_sv
#@ mutex_invariant lock_sv: shared_val >= 0
_ = 0  # anchor

import threading
lock_sv = threading.Lock()
shared_val = 0

def helper() -> int:
    local = 0
    #@ releases lock_sv
    with lock_sv:
        local += 1
    return local

if __name__ == "__main__":
    print("PASS")
