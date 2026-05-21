"""Test 0270 — Concurrent: releases annotation in thread_entry function"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared flag protected_by lock_flag
#@ mutex_invariant lock_flag: flag >= 0
_ = 0  # anchor

import threading
lock_flag = threading.Lock()
flag = 0

#@ thread_entry
#@ \diverges
def signal_thread() -> int:
    #@ acquires lock_flag
    #@ releases lock_flag
    with lock_flag:
        flag += 1
    return 0

if __name__ == "__main__":
    print("PASS")
