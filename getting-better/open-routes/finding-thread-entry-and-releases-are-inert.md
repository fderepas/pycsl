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
