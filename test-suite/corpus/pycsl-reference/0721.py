"""Test 0721 — HAPPY H-S: check-before-use capability via targets/precond (positive).

`#@ happy authn: targets transfer precond self.session_authenticated == 1` makes the session
capability a PRECONDITION of `transfer`. The target ASSUMES it (its body), and every CALL
SITE must PROVE it — the meta-pass injects `#@ check self.session_authenticated == 1` before
each `self.transfer(...)`. Here `handle` grants the capability (after a mock token check)
before calling, so the call-site obligation discharges. This mirrors macsl's H-S, where a
plain `requires` is checked by WP's call rule (../macsl src/macsl.ml emit_requires).
"""
# pycsl-flags: --memory-model hoare
#@ happy authn:
#@     targets transfer
#@     precond self.session_authenticated == 1
class Bank:
    def __init__(self) -> None:
        self.session_authenticated: int = 0

    #@ requires True
    def transfer(self, amount: int) -> int:
        return amount                          # guarded op — assumes the capability

    #@ requires True
    def handle(self, amount: int) -> int:
        self.session_authenticated = 1         # grant AFTER (mock) token validation
        return self.transfer(amount)           # call-site precond `session_authenticated==1` holds
