"""Test 0276 — Concurrent: unprotected shared alongside thread_entry (ConcurrencyChecker warning path)"""
# pycsl-flags: --no-proof --memory-model concurrent
#@ shared request_count
#@ shared response_count
_ = 0  # anchor

request_count = 0
response_count = 0

#@ thread_entry
# NOTE: no `#@ \diverges` here. `handle`'s body is straight-line (no critical section,
# no loop, no call/recursion) so it provably terminates; an unjustified `#@ \diverges`
# is now a hard semantic error (Module4._validate_diverges, refactor.md Phase D2) — see
# the negative driver 0695. This driver exercises the ConcurrencyChecker unprotected-shared
# WARNING path, which still fires, and the emitted WhyML type-checks honestly.
def handle() -> int:
    request_count += 1
    response_count += 1
    return 0

if __name__ == "__main__":
    print("PASS")
