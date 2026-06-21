"""formal_bank_transfer.py — the shared HAPPY flagship (PyCSL edition of macsl small_example).

SIX named security policies on ONE money operation, `transfer`, composed (cf.
happy-roadmap-impl.md §0b and ../macsl tests/small_example/main.c):
  - H-R nonrepud_complete    : any balance change implies the audit log grew
  - H-R nonrepud_append_only : every earlier audit record is unchanged
  - H-T bal_integrity        : only `transfer` (and the `seed` bootstrap) may write a balance
  - H-S authn                : `transfer` is reachable only with the session capability
  - H-E priv_monotonic       : a transfer never RAISES a role (0=super-admin..2=user)
  - H-D availability         : `transfer` is TOTAL (always terminates — no attacker-induced DoS)

This is a STRICT SUPERSET of macsl's main.c, which composes the first five: macsl keeps H-D
off its flagship because main's accept-loop is intentionally infinite (`terminates \false`),
whereas PyCSL's straight-line `transfer` is genuinely total, so H-D composes here too.
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
#@ happy availability:
#@     targets transfer
#@     total
class Bank:
    #@ ensures \forall i; (0 <= i and i < 5) ==> self.role[i] == 0
    #@ ensures \forall i; (0 <= i and i < 5) ==> self.balance[i] == 0
    #@ ensures self.audit_len == 0
    #@ ensures self.session_authenticated == 0
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
    #@ assigns self.balance, self.audit, self.audit_len
    #@ ensures \result == 0 or \result == -1
    #@ ensures (self.role[s] <= 2 and \old(self.balance[s]) >= amount) ==> \result == 0
    #@ ensures \result == 0 ==> self.balance[s] == \old(self.balance[s]) - amount
    #@ ensures \result == 0 ==> self.balance[r] == \old(self.balance[r]) + amount
    #@ ensures \result == 0 ==> self.audit_len == \old(self.audit_len) + 1
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

    #@ requires v0 >= 0
    #@ requires v1 >= 0
    #@ assigns self.balance
    #@ ensures self.balance[0] == v0
    #@ ensures self.balance[1] == v1
    def seed(self, v0: int, v1: int) -> None:
        self.balance[0] = v0
        self.balance[1] = v1

    #@ requires 0 <= s and s < 5
    #@ requires 0 <= r and r < 5
    #@ requires s != r
    #@ requires amount > 0
    #@ requires self.audit_len < 1024
    def handle(self, s: int, r: int, amount: int) -> int:
        self.session_authenticated = 1
        return self.transfer(s, r, amount)


# --- formal test: the operation's observable CONSEQUENCE, via the PUBLIC API ---
# setup (seed two accounts) -> operate (transfer) -> observe (money moved, audit grew),
# over SYMBOLIC inputs. Calls only Bank's public surface; never touches internals.
#@ requires amount > 0
#@ requires src_bal >= amount
#@ requires src_bal < 200
#@ requires dst_bal >= 0
#@ requires dst_bal + amount < 200
def formal_transfer_moves_money(amount: int, src_bal: int, dst_bal: int) -> int:
    b = Bank()                       # role/balance all 0, audit_len 0  (ctor ensures)
    b.session_authenticated = 1      # grant the capability the H-S precond demands
    b.seed(src_bal, dst_bal)         # set up: fund source (acct 0) and dest (acct 1)
    rc = b.transfer(0, 1, amount)    # OPERATE: the money operation under test
    after_src = b.balance[0]         # observe: read the post-state back through the API
    after_dst = b.balance[1]
    after_len = b.audit_len
    # consequence: success path taken; money left src, arrived at dst; transfer audited
    #@ assert rc == 0
    #@ assert after_src == src_bal - amount
    #@ assert after_dst == dst_bal + amount
    #@ assert after_len == 1
    return rc
