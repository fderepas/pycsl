"""Test 0274 — Concurrent: mixed protected and unprotected shared variables"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared counter protected_by lock_c
#@ mutex_invariant lock_c: counter >= 0
#@ shared config_flag
_ = 0  # anchor

import threading
lock_c = threading.Lock()
counter = 0
config_flag = 1

#@ thread_entry
#@ \diverges
def worker() -> int:
    #@ critical lock_c
    with lock_c:
        counter += 1
    return 0

def get_config() -> int:
    return config_flag

if __name__ == "__main__":
    print("PASS")
