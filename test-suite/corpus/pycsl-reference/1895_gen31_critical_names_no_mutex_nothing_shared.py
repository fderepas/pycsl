r"""Test 1895 — gen #31 WITNESS (expected FAIL): `#@ critical` names a mutex that does not
exist, in a block that touches nothing shared.

The companion to 1893, and the one that corrects an earlier claim of mine. A silent-name
sweep recorded `#@ critical` among the directives that REFUSE an unknown name. It does
not — the file that produced that verdict wrote to a protected shared variable inside the
block, so the refusal came from the protection analysis ("held mutexes are
['no_such_lock']"). With nothing shared touched, this file measured
`[+] Verification SUCCESS!` before the repair.

That asymmetry is the whole content of the finding: three directives that all name a mutex,
none of which validated the name, two of them masked by a DIFFERENT check that happens to
fire on the programs people write.
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
def touch() -> int:
    local = 10
    #@ critical no_such_lock
    with lock_bal:
        local = local + 1
    return local
