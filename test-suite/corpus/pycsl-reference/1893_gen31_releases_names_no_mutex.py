r"""Test 1893 — gen #31 WITNESS (expected FAIL): `#@ releases` names a mutex that does not
exist, and NOTHING downstream could ever have caught it.

`#@ releases` is documented as "informational in current WhyML output", and it is more than
informational-in-output: `Module3_Weaver.visit_With` sets `node.csl_releases` and **no
downstream stage reads it**. So a misspelled mutex there had no second chance — unlike
`#@ critical` and `#@ acquires`, which reach the IR as a `CriticalSection` and are caught
INDIRECTLY, and only when the block actually touches a protected shared variable, by the
protection analysis ("held mutexes are ['no_such_lock']"). That is the protection analysis
doing its job, not a name check: on a block that touches nothing shared, all three verified
silently. This file measured `[+] Verification SUCCESS!` before the repair.

`no_such_lock` is bound nowhere — it is a `NameError` in CPython — which is why the rule
is the WEAKEST one that catches the typo. A rule keyed on the mutex REGISTRY would forbid a
good program: a lock protecting an invariant PyCSL does not model is legitimately annotated
and legitimately absent from it.
"""
# pycsl-expected: FAIL
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
    #@ releases no_such_lock
    with lock_bal:
        balance += amount
    return 0
