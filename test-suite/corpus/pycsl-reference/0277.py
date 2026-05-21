"""Test 0277 — Concurrent: thread_entry with multiple sequential critical sections"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared processed protected_by lock_proc
#@ shared failed protected_by lock_fail
#@ mutex_invariant lock_proc: processed >= 0
#@ mutex_invariant lock_fail: failed >= 0
_ = 0  # anchor

import threading
lock_proc = threading.Lock()
lock_fail = threading.Lock()
processed = 0
failed = 0

#@ thread_entry
#@ \diverges
def handler() -> int:
    #@ critical lock_proc
    with lock_proc:
        processed += 1
    #@ critical lock_fail
    with lock_fail:
        failed += 1
    return 0

if __name__ == "__main__":
    print("PASS")
