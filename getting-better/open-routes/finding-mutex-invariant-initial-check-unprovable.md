# FINDING (#49, gen #31) — `#@ mutex_invariant` cannot be PROVED, in any program
# (CLOSED the same day — see CLOSURE at the end)

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


---

## CLOSED (2026-09-23, gen #31) — and the first fix was necessary but NOT sufficient

**TWO things were wrong**, which is why the obvious repair was measured rather than
assumed.

**(1) The shared global was unconstrained.** `val counter : ref int` — the module's own
`counter = 0` never reached Module 6, because `collect_module_constants` deliberately
EXCLUDES `#@ shared` globals (they are mutable state and must not be inlined as literals in
contracts). The initial value is now carried on the `shared_vars` IR entry, emitted only
when the module-level binding is an int literal, and lowered as `let counter = ref 0`.

**(2) That was not enough, and the measurement is the point.** With the ref concrete, the
goal STAYED Unknown. `let _check_initial_<m> () : unit = assert { <m>_inv !v }` is a
PROGRAM FUNCTION, and Why3's WP for a function reading a mutable global has no information
about that global's current value — it quantifies over every reachable state. A concrete
initialiser tells it nothing.

The obligation the directive means to state is **"the module's INITIAL values satisfy the
mutex invariant"**, which is a question about literals. It is now emitted as one:

```whyml
  let counter = ref 0
  predicate lock_counter_inv (counter : int) = (counter >= 0)
  goal _check_initial_lock_counter : lock_counter_inv 0
```

MEASURED — and this pair is what the directive never had:

| file | invariant | initial | verdict |
|---|---|---|---|
| `1863` | `counter >= 0` | `0` | **SUCCESS, with the prover ON** |
| `1864` | `counter >= 1` | `0` | **FAILED** on `_check_initial_lock_counter` |

Before today those two were INDISTINGUISHABLE: both unprovable with the prover on, both
silently unchecked under `--no-proof`, which is the mode all 19 existing drivers use. They
are the first corpus drivers to run `#@ mutex_invariant` through the prover at all.

FALLBACK, deliberately kept: if ANY shared var the invariant is parameterized by has no
known module-level initialiser, the old function-with-assert form is emitted unchanged —
there is no literal to state the goal about, and an unconstrained `val ref` is exactly what
that case still has.

BLAST RADIUS, measured: all **35** corpus files declaring `#@ shared` keep their expected
verdicts. Byte-diff: **30 MOVED**, 0 GONE, 0 APPEARED — the 0250-0280 concurrent block plus
0417 — and the diff is exactly the two intended changes (`val v : ref int` -> `let v = ref
<init>`, and the assert-in-a-function -> the goal over literals). 2199 python-reference
`.mlw` byte-identical. NO mirror file declares `#@ shared` (the one grep hit in
`core_ir_semantic.py` is a docstring), so no mirror emission moves and no re-proof is owed.

Both edited functions — `Module5.visit_Module` and `preamble._emit_shared_state` — have
`\trusted` mirror twins, checked before the work started per lesson (n4).
