"""Test 0280 — Concurrent: two shared vars protected by same mutex, both updated in critical section"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared total_in protected_by lock_io
#@ shared total_out protected_by lock_io
#@ mutex_invariant lock_io: total_in >= 0 and total_out >= 0
_ = 0  # anchor

import threading
lock_io = threading.Lock()
total_in = 0
total_out = 0

#@ thread_entry
#@ \diverges
def io_worker() -> int:
    #@ critical lock_io
    with lock_io:
        total_in += 1
        total_out += 1
    return 0

if __name__ == "__main__":
    print("PASS")
