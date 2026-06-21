"""Test 0723 — HAPPY H-R: audit non-repudiation (completeness + append-only), positive.

Two named postconditions on `transfer` (macsl's `\context(\postcond)`):
  - nonrepud_complete:   any balance change implies the audit log grew (every money
                         movement is recorded);
  - nonrepud_append_only: every earlier audit record is unchanged (the log is append-only).
`transfer` appends exactly one record at the new slot and bumps `audit_len`; the failing
(insufficient-funds) path touches neither, so both theorems hold. Mirrors macsl's
main.c `nonrepud_complete` / `nonrepud_append_only`.
"""
# pycsl-flags: --memory-model hoare
#@ class invariant \length(self.balance) >= 5
#@ class invariant \length(self.audit) >= 1024
#@ class invariant 0 <= self.audit_len and self.audit_len <= 1024
#@ happy nonrepud_complete:
#@     targets transfer
#@     postcond (\exists i; (0 <= i and i < 5) and self.balance[i] != \old(self.balance[i])) ==> self.audit_len > \old(self.audit_len)
#@ happy nonrepud_append_only:
#@     targets transfer
#@     postcond \forall i; (0 <= i and i < \old(self.audit_len)) ==> self.audit[i] == \old(self.audit[i])
class Bank:
    def __init__(self) -> None:
        self.balance: list = bytearray(5)
        self.audit: list = bytearray(1024)
        self.audit_len: int = 0

    #@ requires 0 <= s and s < 5
    #@ requires 0 <= r and r < 5
    #@ requires s != r
    #@ requires amount > 0
    #@ requires self.audit_len < 1024
    def transfer(self, s: int, r: int, amount: int) -> int:
        if self.balance[s] < amount:
            return -1
        self.balance[s] = self.balance[s] - amount
        self.balance[r] = self.balance[r] + amount
        self.audit[self.audit_len] = amount
        self.audit_len = self.audit_len + 1
        return 0
