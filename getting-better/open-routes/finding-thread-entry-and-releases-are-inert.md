# FINDING (#49, gen #31) — `#@ thread_entry` and `#@ releases` are parsed, stored, and never read

**STATUS: CONFIRMED LIVE, by grep AND by measurement. NOT soundness routes.** Two more
directives with no enforced consequence, found the same way as the `#@ mixin` one: by
`bin/check-directive-enforcement.py` failing to find a violating program to write.

## `#@ thread_entry` — collected into a set nothing reads

`test-suite/annotations.md` row 10: *"Marks function as a concurrent thread entry point;
used with `--memory-model concurrent`."* The data path is complete right up to the
consumer, and then stops:

| stage | what happens |
|---|---|
| `Module2_Parser.py:1364` | `if kw == "thread_entry": self.advance(); return ThreadEntry()` |
| `Module3_Weaver.py:331` | `node.csl_thread_entry = True` |
| `ConcurrencyChecker.py:87` | `self._thread_entries.add(node.name)` |
| `ConcurrencyChecker.py` | **`_thread_entries` is assigned at line 65, written at line 88, and READ NOWHERE** (`grep -n _thread_entries` returns exactly those two lines) |
| `Module5_IREmitter.py:6734` | `func_ir["thread_entry"] = True` |
| Module 6 / `core_ir_semantic` | **no consumer** (`grep -rn thread_entry src/pycsl/module6_whyml/ src/pycsl/Module6_WhyMLTranspiler.py src/pycsl/core_ir_semantic.py` → nothing) |

Measured, not just grepped. The same module under
`--memory-model concurrent --strict-concurrent-checks`, one line apart:

| variant | result |
|---|---|
| unprotected write to a `#@ shared … protected_by` global, worker marked `#@ thread_entry` | REFUSED (UB-7.3) |
| the same file with `#@ thread_entry` DELETED | REFUSED (UB-7.3) — identical |

So the race check does not depend on the marker, and nothing else does either.

## `#@ releases` — stored on the `with` node, read by nothing

`Module2_Parser.py:1366` parses it, `Module3_Weaver.py:426` sets `node.csl_releases =
c.mutex`, and `grep -rn releases src/pycsl/ --include=*.py` finds no other use. This one is
at least **honestly documented** — annotations.md row 6 says "informational in current
WhyML output" and §11 says it "does not currently generate" anything — so it is a known
placeholder rather than a broken promise. Recorded here so the two live in one place.

## WHY NEITHER IS A ROUTE

An inert directive proves nothing false; it just fails to add the guarantee a reader might
take it for. `thread_entry`'s risk is the specific reading "the concurrency checks apply to
the functions I marked" — they apply to all of them, which is stricter, not weaker.

## CONSEQUENCE FOR THE PLANE

Both stay UNCOVERED in `bin/check-directive-enforcement.py`, with these measurements as the
reason. The plane's covered fraction is therefore a floor on *enforced* directives, not on
*parsed* ones — which is the number worth ratcheting.

Companion files: `finding-mixin-marker-has-no-teeth.md` (same shape, class scope) and
`finding-mutex-invariant-initial-check-unprovable.md` (a directive that bites but can never
be discharged).

Measured 2026-09-23.

## 2026-09-24 — THESE TWO ARE NOW THE ENTIRE UNCOVERED LIST

`bin/check-directive-enforcement.py` went 46 -> 51 of 53 in one session, and every
directive that left the uncovered list left because its stated reason for being there was
wrong: `reveal` (a limit of the harness, which then grew a multi-file `verdict()`),
`verify_module` ("needs a second module" — a lowercase group name is refused with one
class), `proof` ("needs real Rocq-Lean artifacts" — the axiom body is in Module 6's
`_AXIOM_REGISTRY`; the `.proofs/` trees belong to the separate audit tool),
`propagate_frame` (a reproducible trigger-term failure that holds for only ONE of the two
propagated frame shapes) and `sibling_concrete` (a reproducible Why3 result that holds for
only ONE of the directive's two documented halves).

`thread_entry` and `releases` are what is left, and they are the two that were never
excuses: there is no violating program because there is nothing to violate. That makes this
finding the ONLY remaining reason the directive plane is not at 53 of 53, and it upgrades
the finding from "two inert markers" to "the plane's entire outstanding debt".

The capabilities named in this file are unchanged; what changed is that nothing else is
queued behind them.

## ADDENDUM, same generation — `releases` is inert AND its NAME was never checked

"Inert" turned out to be the smaller half of what is wrong with `#@ releases`. Going back to
it to write the enforcement pair it cannot have, the obvious next question was whether it at
least validates its argument. It does not — and neither do its two siblings:

    with lock_bal:              (block touches NOTHING shared)
      #@ critical no_such_lock  -> [+] Verification SUCCESS!
      #@ acquires no_such_lock  -> [+] Verification SUCCESS!
      #@ releases no_such_lock  -> [+] Verification SUCCESS!

`no_such_lock` is bound nowhere in the file — a `NameError` in CPython. `releases` is the
one that could never have been caught, for the reason THIS file already records: nothing
reads `csl_releases`. The other two are caught only when the block actually touches a
protected shared variable, and then it is the PROTECTION analysis answering, not a name
check. That also corrected two of the silent-name sweep's controls — see
`finding-a-mutex-name-that-resolves-to-nothing.md` and wall-lesson (e5).

So this file's conclusion stands and gains a rider: the plane's outstanding debt is that
these two directives have nothing to violate, and until this generation the ARGUMENT of one
of them had nothing to be right about either.

Re-measured `thread_entry` independently while here, and this file's statement holds
exactly: `0269.py` with the `#@ thread_entry` line deleted still verifies, `_thread_entries`
is populated and read nowhere, and `func_ir["thread_entry"]` has no consumer anywhere in
`src/pycsl` outside the two agent prompt strings.
