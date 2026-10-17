# OPEN ROUTE #264 — READING A NEVER-ASSIGNED LOCAL IS MODELLED AS 0 (UnboundLocalError IGNORED)

**Status: REPAIRED (gen #36, 2026-10-17; opened the same day), Severity 1.** Red-team round 3; driver-reproduced at HEAD 13451c8d (s03/s04/s06 rc=0;
CPython UnboundLocalError). Witnesses `witnesses-r264/`: s04 (`if c: y = 1` then `return y`), s03 (`n += 1` with n
unbound), s06 (`del x; return x`), s01/s07 (module global assigned without `global` -> local, read first).
Mechanism: every local is hoisted as `let y = ref 0 in` with no definite-assignment check; `del name` emits `()`.
PyCSL claims normal termination by default, so a raising path proving a postcondition is unsound.
Repair: a definite-assignment analysis (Python scoping: a name assigned anywhere in the function is local); a read
that is not definitely assigned on every path is refused (or an unprovable `assert false` on that path); `del x`
makes x unassigned.

## REPAIR (2026-10-17, branch r264 off 283d1033, landed with #265)

**Rule** (inline in `pycsl.py::_run_pipeline`, after Module 5 + the IR checks, before Module 6; mirror twin
`\trusted`; no new `def`): a MUST-ASSIGN (definite-assignment) dataflow per lowered function, over a CFG of its
body built with Python's scoping. LOCALS = params + every name the function's own scope binds (assign / augassign /
annotated-with-value / `for` / `with ... as` / `except ... as` / walrus, incl. a walrus inside a comprehension /
`import` / nested `def`/`class` / `match` captures / `del`) minus `global`/`nonlocal`. A read (or `del`) of a local
not bound on EVERY path reaching it is REFUSED (`PYCSL-SEM-UNBOUND-LOCAL`). Graph facts: loop bodies may run zero
times, except `while True` and `for` over a constant NON-EMPTY `range(...)` (first iteration certain; `range` not
rebound in the file); `break`/`continue`/`return`/`raise` end their path; exception edges from a `try` body carry the
state BEFORE the raising op; `except E as e` UNBINDS `e` at handler end; `finally` analysed on the normal and the
exceptional path; a `with` body may exit through a suppressed exception; a `match` without an unguarded irrefutable
arm falls through; `and`/`or`/`if-else` operands and comprehension bodies are conditional (a walrus there binds
nothing definitely); an expression statement calling a same-file function / `self.` method EVERY definition of which
ends in `raise` with no `return` ends its path (the parsers' `self._err(...)` idiom). Unreachable code is not refused.
`\trusted`/`\abstract` functions (and everything nested in them) are skipped: their bodies are never modelled.

**Probe table** (283d1033 -> after; CPython raises `UnboundLocalError` for every FAIL row):

| file | shape | base | after |
|------|-------|------|-------|
| 2790 | `if c: y = 1` / `return y` | PROVED | REFUSED |
| 2791 | `n += 1`, `n` bound nowhere | PROVED | REFUSED |
| 2792 | `x = 1; del x; return x` | PROVED | REFUSED |
| 2793 | module `n = 5`, `n += 1` without `global` | PROVED | REFUSED |
| 2794 | `y` bound only in a `while` body, `n <= 0` | PROVED | REFUSED |
| 2795 | `y` bound only by `case 1:`, no catch-all | PROVED | REFUSED |
| 2796 | `y` bound only in a `for k in range(n)` body, `n <= 0` | PROVED | REFUSED |
| 2797 | control: `if`/`elif`/`else` all bind | PROVED | PROVED |
| 2798 | control: `for k in range(3): y = 5` / `return y` | PROVED | PROVED |

witnesses-r264/ s01/s03/s04/s06/s07: all PROVED at base, all REFUSED after.

**Blast radius** (measured with a CPython-`ast` run of the shipped block over every population, then the real
pipeline): pycsl-reference 31 files / 47 reads — 24 PASS `--no-proof` concurrency drivers (0250-0253, 0257-0263,
0265-0267, 0269-0271, 0274, 0276-0280, 1894) whose `#@ thread_entry` workers do `counter += 1` on a `#@ shared`
module global WITHOUT `global` (each an `UnboundLocalError` in CPython): SOURCE REPAIRED, each gains the missing
`global <names>` line right under its `def` — emission byte-identical (0 MOVED), so their verdicts stand on a now-
valid program; 6 expected-FAIL witnesses (0254, 0255, 0691, 1741, 1893, 1993) keep their OWN refusal (they are
refused earlier, by the concurrency checks / Module 3 / route #233's Module-5 guard — verified); 1026 cleared by the
constant-`range` rule (still VERIFY-FAIL). python-reference: 1 (0177, `for i in range(100)` + `break`) cleared by the
same rule. Mirror: 12 reads in 4 files, all in `\trusted` functions (`audit_proof_reverify.verify_rocq_file` /
`verify_lean_file`, `pycsl.main`) or behind a no-return `self._err`/`self.error` call (`Module2_Parser.
_parse_happy_region`, `pure_ast._sequence_pattern`) — 0 refused. `pycsl_lib/json/encoder.py` (3 reads of a
path-correlated `markerid`) was already REFUSED (baselined in `check-stdlib-modules-verify`).

**Gates**: corpus root 1740 -> 1743 (+3 new PASS controls), 0 MOVED / 0 GONE / 0 APPEARED (the 24 source-repaired
drivers are byte-identical); pyref 2186/2186 0 MOVED / 0 GONE; mirror 53/53 0 MOVED / 0 GONE (no re-proof owed);
refusal-witness census +11 rows (own witnesses only, via `_census_row`), 222 demonstrated / 5 undemonstrated; advice
audit +2 FOLLOWABLE (the `global` advice is limited to READS, because a write through `global` is refused by the
global-write guard — measured). Planes: `run-soundness-planes.sh` 61/61 green; `--slow` 81/84, the 3 reds
(stdlib-modules-verify, getattr-erasure, assigns-writes-survival) exactly the 3 already red at base — the stdlib
REFUSED set is identical base vs patched (17/17); check-self-annotate-sync + self-annotate-mirror-check rc=0;
mirror-coverage 549/41 unchanged.

**Residuals** (stated, not hidden): a closure/lambda reading an enclosing local at CALL time and the deferred parts
of a generator expression are not tracked; a `self.<m>` no-return call trusts that no subclass overrides `<m>` with
a returning body; a `with` is treated as possibly-suppressing (sound, may refuse a correct program using a
non-suppressing context manager — 0 such sites in the populations).
