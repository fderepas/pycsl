# OPEN ROUTE #305 — A USER EXCEPTION CLASS NAMED LIKE A BUILTIN IS CONFLATED WITH THE BUILTIN (handler matching under no_exception)
**Status: REPAIRED (gen #37, 2026-10-23; opened the same day), Severity 1.** Red-team round 13; driver-reproduced on main (4/4 rc=0; CPython violates).
Witnesses `witnesses-r305/`: `class KeyError(Exception)` (NOT a LookupError) raised inside `try ... except LookupError` under
`no_exception \all` + `ensures \result == 1` proves (r25); a user `class LookupError` "catches" the builtin KeyError (r27); named
`no_exception KeyError` variant (r29); the builtin KeyError raised implicitly by `d[5]` is caught by a handler for the user's own
`KeyError` class (r30). Without no_exception the shape is refused by #175 (r31).
Mechanism: handler matching consults `exception_model.EXCEPTION_BASES` by NAME (`handler_catches`) and the WhyML exception tag is the
bare name, so the user class and the builtin share one tag and the builtin hierarchy. Emitted: `with LookupError -> ... | KeyError -> raise (Return 1)`.
A new carrier of the #75 class (a name-keyed oracle beats the user's own definition); #75's guard covers builtin functions only.
Repair direction: refuse (or give a distinct tag + the user's own bases to) any user class definition whose name shadows a builtin
exception name (or any name in EXCEPTION_BASES / the implicit-raise trigger set), and any handler/raise that names it; census also
imported-module classes with builtin names and `E = KeyError`-style aliases to user classes.

## REPAIR (2026-10-23, r305 executor, detached off 370e1875)
Sound refusal (the route's preferred direction): a distinct tag + the user's own bases would touch the WhyML
tag naming, `handler_catches`, the #175/#260/#272/#304 handler/raises machinery and the implicit-trigger
tags — measured disproportionate for a rare, adversarial shape; no model assumption is declared.

Probe table (`pycsl.py` rc; CPython ground truth = each file's `__main__`):

| shape | 370e1875 | after |
|---|---|---|
| r25 / 3780 user `class KeyError(Exception)` under `except LookupError`, `no_exception \all` | PROVED (cpy raises) | REFUSED R305 |
| r27 / 3781 user `class LookupError` "catches" builtin `KeyError` | PROVED | REFUSED R305 |
| r29 / 3782 named `no_exception KeyError` variant | PROVED | REFUSED R305 |
| r30 / 3783 implicit `KeyError` of `d[5]` caught by user-class handler | PROVED | REFUSED R305 |
| 3784 function-LOCAL `class KeyError` | PROVED | REFUSED R305 |
| 3785 class NESTED in a class body (`A.KeyError`) | FAIL | REFUSED R305 |
| 3786 IMPORTED module defines `class KeyError` (`raise sm.KeyError`) | FAIL | REFUSED R305 |
| probe: `from mod import KeyError` (dep defines the class) | PROVED | REFUSED R305 |
| r31 user `class KeyError(Base)` under `except Base` (no no_exception) | REFUSED #175 | REFUSED R305 |
| `KeyError = Mine` alias at module scope | REFUSED #131 | REFUSED #131 (runs first) |
| user `class error(Exception)` under `except OSError` | REFUSED (dead-handler check) | same |
| controls 3787 `MyKeyError(Exception)`, 3788 `class E(KeyError)` caught by `except E`, 3789 `from builtins import KeyError` | PASS | PASS |
| route #304 witnesses (29 files, `witnesses-r304/`) | — | rc identical base vs after (j02 still rc=0: #304 residual) |

Rule (inline in `_run_pipeline`, `pycsl.py`, right after the #181 dependency parse; no new def, no IR change,
ledger 3; `_run_pipeline` is `\trusted` in the mirror): over the main file AND every dependency module it
imports (transitively, the #181 resolver), any binding of a name in `EXCEPTION_BASES ∪ KNOWN_EXCEPTIONS ∪
{EnvironmentError, IOError}` is refused — a `class` statement at ANY depth (module, function, class body), and a
def / import binding (`import x as N`, `from m import N`) / Name store or del / parameter / `except ... as N`
in a module or function scope (a class-body binding is an attribute, not the name). `from builtins import N`
(rebinding the builtin to itself) is accepted. Code `PYCSL-R305-BUILTIN-EXCEPTION-NAME-SHADOWED`.
`error` (the `os.error` alias row of EXCEPTION_BASES) is included: a user `class error` would otherwise be an
OSError subclass to `handler_catches`.

Census (bindings of those names): pycsl-reference 1 (1375, `ValueError = KeyError`, already refused by #131 —
still refused by #131, which runs first); python-reference 0; mirror 0 (pure_ast `def error` is a METHOD);
live tree `src/pycsl` 0 relevant (pure_ast method; `agents/agent-rocq-proof-writer.py` local `error =`, never
ingested); `src/pycsl_lib` 1 — `re/__init__.py: error = PatternError`, not a dependency of any corpus file (the
#181 resolver reads the main file's directory and `--import-path`), so 0 movers; a program that puts
`pycsl_lib/re` on its import path and imports it is now refused (accepted residual: `re.error` aliasing a user
class under the name `error` IS the conflation this route closes).

Blast radius: corpus root 0 MOVED / 0 GONE / 0 APPEARED (2026 base / 2029 candidate, 3 new emitting sources =
controls 3787-3789); pyref 0/0/0 (2186/2186); mirror 0/0/0 (53/53, `--min-files 50`). No mover, nothing OWED.

Gates (rc): witnesses table above; byte-diff-sweep base/after rc=0/0; byte-diff-compare root rc=0, pyref rc=0;
mirror-emit-sweep base/after rc=0/0, compare rc=0; refusal-witness census +7 rows (3780-3786, REFUSAL) via the
plane's own `_census_row`, check-refusal-witness-coverage rc=0 (251 demonstrated, 5 undemonstrated = ceiling,
10 unmatchable = ceiling); check-self-annotate-sync.sh rc=0 (926 verbatim); self-annotate-mirror-check.sh rc=0
(53); run-soundness-planes.sh (fast) rc=0, 61/61; doc-coherency --check rc=0; check-assumed-facts rc=0 (85);
check-trusted-raises-honesty rc=0 (ratchet 61). `--slow` not run.
Residuals: the refusal is by binding, not by use — a program that binds `KeyError` but never raises or catches
it is refused too (no corpus/pyref/mirror instance). A dependency the #181 resolver cannot find (not under the
main file's directory or `--import-path`) is not read: such an import is already outside the modelled set.
