r"""Test 1741 — WITNESS for `PYCSL-SEM-CONCURRENCY`: acquiring locks against the declared
`#@ lock_order`.

0260 and 0261 are the POSITIVE witnesses (two workers both respecting `lock_r, lock_s`).
The violation — a worker taking `lock_s` first and then `lock_r` — had no witness, which
`bin/check-refusal-witness-coverage.py` measured along with 129 others. A declared lock
order whose violation is never demonstrated is a deadlock-freedom claim resting on a check
nobody has seen fire.
"""
# pycsl-expected: FAIL
# pycsl-flags: --no-proof --memory-model concurrent --strict-concurrent-checks
#@ shared r protected_by lock_r
#@ shared s protected_by lock_s
#@ lock_order lock_r, lock_s
_ = 0  # anchor

import threading
lock_r = threading.Lock()
lock_s = threading.Lock()
r = 0
s = 0


#@ thread_entry
#@ \diverges
def worker_a() -> int:
    #@ acquires lock_s
    with lock_s:
        #@ acquires lock_r
        with lock_r:
            r += 1
    return 0
