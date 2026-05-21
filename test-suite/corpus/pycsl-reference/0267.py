"""Test 0267 — Concurrent: releases combined with acquires on same with block"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared stock protected_by lock_stock
#@ mutex_invariant lock_stock: stock >= 0
_ = 0  # anchor

import threading
lock_stock = threading.Lock()
stock = 0

#@ thread_entry
#@ \diverges
def worker() -> int:
    #@ acquires lock_stock
    #@ releases lock_stock
    with lock_stock:
        stock += 1
    return 0

if __name__ == "__main__":
    print("PASS")
