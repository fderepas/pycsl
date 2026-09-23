# FINDING (#49, gen #31) — `#@ mutex_invariant` cannot be PROVED, in any program

**STATUS: CONFIRMED LIVE by measurement. NOT a soundness route — it OVER-rejects.**
Filed because the consequence is a coverage hole that looks like a passing corpus:
every driver that uses the directive avoids the proof plane, and nothing says why.

## THE MEASUREMENT

Source (`--memory-model concurrent --strict-concurrent-checks`, proof ON):

```python
#@ shared counter protected_by lock_counter
#@ mutex_invariant lock_counter: counter >= 0
import threading
lock_counter = threading.Lock()
counter = 0
...
#@ thread_entry
#@ \diverges
def worker() -> int:
    #@ critical lock_counter
    with lock_counter:
        counter = 0        # the invariant HOLDS at release
    return 0
```

FAILS. The emitted WhyML says exactly why:

```whyml
  val counter : ref int                                   (* <-- UNCONSTRAINED *)
  predicate lock_counter_inv (counter : int) = (counter >= 0)
  let _check_initial_lock_counter () : unit =
    assert { lock_counter_inv !counter }                  (* <-- UNPROVABLE *)
```

The module-level initialiser `counter = 0` is **dropped**; the shared variable is emitted
as an unconstrained `val ref int`. So the initial-state obligation asserts the invariant of
an arbitrary integer and is unprovable for **any invariant that is not vacuously true** —
independently of the program. The release-point obligation inside `worker` is emitted
correctly and IS discharged (`worker'vc` sub-goals come back Valid); the only unproven goal
in the file is `_check_initial_lock_counter`.

## THE CONSEQUENCE, AND WHY IT IS WORTH A FILE

`grep`ped the reference corpus: **19 drivers declare `#@ mutex_invariant` and all 19 pass
`--no-proof`**, except `0691`/`0256`, which are `# pycsl-expected: FAIL`. Of the five
concurrent drivers that DO run the prover (`0272`, `0273`, `0275`, plus two expected-FAIL),
**not one declares a `mutex_invariant`.** So the directive's proof obligation has never been
discharged by anything in the tree, and the corpus cannot notice: `--no-proof` reports
"WhyML generated AND type-checks; proof skipped", which is an honest message about a
different question.

The net position of `#@ mutex_invariant` today: under `--no-proof` it is not checked (by
design, and the banner says so), and with proof on it cannot pass. There is no configuration
in which a user gets the guarantee the directive names.

## WHY THIS IS NOT A ROUTE

Nothing false is proved. A program that breaks its invariant fails, and a program that keeps
it also fails — the failure is fail-CLOSED and the TCB is unchanged. It is a defect of
completeness plus a measurement gap, not an unsoundness.

## THE FIX, WHEN SOMEONE PRICES IT

Emit the module-level initialiser as the shared ref's initial value (`let counter = ref 0`
rather than `val counter : ref int`), or constrain it with the declared invariant *as a
proof obligation on the initialiser* rather than on an arbitrary value. Either makes the
initial check meaningful; the second is the one that keeps `val` for genuinely external
state. Until then, `bin/check-directive-enforcement.py` leaves `mutex_invariant` in its
UNCOVERED list rather than writing a pair whose satisfying half cannot pass — the plane
refuses to certify a directive by lowering the bar to what the implementation does.

Measured 2026-09-23. Files: `$SCRATCH/g31/pairs/mi_v.py`, `mi_s.py` (both FAIL).
