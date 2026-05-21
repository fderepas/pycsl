"""Test 0269 — Concurrent: acquires and releases pair with mutex invariant"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared balance protected_by lock_bal
#@ mutex_invariant lock_bal: balance >= 0
_ = 0  # anchor

import threading
lock_bal = threading.Lock()
balance = 100

#@ thread_entry
#@ \diverges
def deposit() -> int:
    amount = 10
    #@ acquires lock_bal
    #@ releases lock_bal
    with lock_bal:
        balance += amount
    return 0

if __name__ == "__main__":
    print("PASS")
