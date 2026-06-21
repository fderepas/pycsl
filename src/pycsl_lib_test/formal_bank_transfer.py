"""formal_bank_transfer.py — the shared HAPPY flagship (PyCSL edition of macsl small_example).

FIVE named security policies on ONE money operation, `transfer`, composed (cf.
happy-roadmap-impl.md §0b and ../macsl tests/small_example/main.c):
  - H-R nonrepud_complete    : any balance change implies the audit log grew
  - H-R nonrepud_append_only : every earlier audit record is unchanged
  - H-T bal_integrity        : only `transfer` (and the `seed` bootstrap) may write a balance
  - H-S authn                : `transfer` is reachable only with the session capability
  - H-E priv_monotonic       : a transfer never RAISES a role (0=super-admin..2=user)
"""
# pycsl-flags: --memory-model hoare
#@ class invariant \length(self.role) >= 5
#@ class invariant \length(self.balance) >= 5
#@ class invariant \length(self.audit) >= 1024
#@ class invariant 0 <= self.audit_len and self.audit_len <= 1024
#@ happy bal_integrity:
#@     region 0 .. 5
#@     writes self.balance outside region
#@     except transfer, seed
#@ happy nonrepud_complete:
#@     targets transfer
#@     postcond (\exists i; (0 <= i and i < 5) and self.balance[i] != \old(self.balance[i])) ==> self.audit_len > \old(self.audit_len)
#@ happy nonrepud_append_only:
#@     targets transfer
#@     postcond \forall i; (0 <= i and i < \old(self.audit_len)) ==> self.audit[i] == \old(self.audit[i])
#@ happy priv_monotonic:
#@     targets transfer
#@     postcond \forall i; (0 <= i and i < 5) ==> self.role[i] >= \old(self.role[i])
#@ happy authn:
#@     targets transfer
#@     precond self.session_authenticated == 1
class Bank:
    def __init__(self) -> None:
        self.role: list = bytearray(5)
        self.balance: list = bytearray(5)
        self.audit: list = bytearray(1024)
        self.audit_len: int = 0
        self.session_authenticated: int = 0

    #@ requires 0 <= s and s < 5
    #@ requires 0 <= r and r < 5
    #@ requires s != r
    #@ requires amount > 0
    #@ requires self.audit_len < 1024
    def transfer(self, s: int, r: int, amount: int) -> int:
        if self.role[s] > 2:
            return -1
        if self.balance[s] < amount:
            return -1
        self.balance[s] = self.balance[s] - amount
        self.balance[r] = self.balance[r] + amount
        self.audit[self.audit_len] = amount
        self.audit_len = self.audit_len + 1
        return 0

    #@ requires 0 <= i and i < 5
    #@ requires v >= 0
    def seed(self, i: int, v: int) -> None:
        self.balance[i] = v

    #@ requires 0 <= s and s < 5
    #@ requires 0 <= r and r < 5
    #@ requires s != r
    #@ requires amount > 0
    #@ requires self.audit_len < 1024
    def handle(self, s: int, r: int, amount: int) -> int:
        self.session_authenticated = 1
        return self.transfer(s, r, amount)
