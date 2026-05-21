"""Test 0279 — Concurrent: mutex_invariant with compound expression"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared temp protected_by lock_temp
#@ mutex_invariant lock_temp: temp >= 0 and temp <= 100
_ = 0  # anchor

import threading
lock_temp = threading.Lock()
temp = 20

#@ thread_entry
#@ \diverges
def adjust_temp() -> int:
    #@ critical lock_temp
    with lock_temp:
        temp += 1
    return 0

if __name__ == "__main__":
    print("PASS")
