r"""Test 1863 — gen #31: a `#@ mutex_invariant` DISCHARGED, with the prover on.

The first corpus driver ever to run `#@ mutex_invariant` through the prover. Every one of
the 19 that declared the directive before today passes `--no-proof`, and of the five
concurrent drivers that DO run the prover, none declares one — because the obligation could
not be discharged IN ANY PROGRAM.

TWO THINGS WERE WRONG, and the first was necessary but not sufficient.

  1. The shared global was emitted `val counter : ref int` — UNCONSTRAINED — because the
     module's own `counter = 0` never reached Module 6 (`collect_module_constants`
     deliberately excludes `#@ shared` globals: they are mutable state and must not be
     inlined as literals in contracts). Now carried on the `shared_vars` IR entry and
     emitted `let counter = ref 0`.

  2. The initial check was a PROGRAM FUNCTION:
         let _check_initial_lock_counter () : unit = assert { lock_counter_inv !counter }
     and Why3's WP for a function reading a mutable global has NO information about that
     global's current value — it quantifies over every reachable state. Measured: with the
     ref made concrete the goal STAYED Unknown. The obligation this is meant to state is
     "the module's INITIAL values satisfy the invariant", which is a question about
     literals, so it is now emitted as one:
         goal _check_initial_lock_counter : lock_counter_inv 0

This file declares `counter >= 0` with `counter = 0` and a body that writes 0 while holding
the lock. It VERIFIES with the prover on. Its twin `1864` declares `counter >= 1` over the
same initial 0 and FAILS on the initial-state goal — which is the whole point: the check
now distinguishes.

Recorded in `getting-better/open-routes/finding-mutex-invariant-initial-check-unprovable.md`.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model concurrent --strict-concurrent-checks
#@ shared counter protected_by lock_counter
#@ mutex_invariant lock_counter: counter >= 0
import threading
lock_counter = threading.Lock()
counter = 0
_ = 0  # anchor


#@ thread_entry
#@ \diverges
def worker() -> int:
    #@ critical lock_counter
    with lock_counter:
        counter = 0
    return 0
