r"""Test 1894 — gen #31 CONTROL for 1893 (expected PASS): the same file, mutex spelled right.

Byte-identical to 1893 but for `#@ releases lock_bal`. The refusal is about a NAME that
resolves to nothing, not about `#@ releases` — the same control discipline routes #13 and
#223 pay for. If this one ever goes red, the check has started refusing a directive that
names a real lock.
"""
# pycsl-expected: PASS
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
