# OPEN ROUTE #327 — TWO PYTHON NAMES LOWER TO ONE WhyML IDENTIFIER (whyml_ident case-fold / reserved-word prefix, no collision check)
**Status: REPAIRED (gen #37, 2026-10-24; candidate, see REPAIR), was OPEN (2026-10-24), Severity 1.** Red-team round 20; driver-reproduced on main a8dec3db..1333328f (rc=0; CPython violates).
Witnesses `witnesses-r327/`: `whyml_ident` lowercases a leading capital (N, n -> n) and prefixes reserved words (result -> py_result) with no
collision check: `N = len(xs); n = 0; return N == n` proves True (n40; emitted three `let n = ref ..` then `!n = !n`), n24, n09; reserved-word
prefix vs an existing `py_result`/`py_model` (n27, n14); global `K = mk()` vs param `k` -> `return K` returns the parameter (n31); `F = 0.5` vs a
param `f` also bypasses #325 (n06). Inlined int constants are safe. Needs no float — miscompiles plain int code.
Repair: make identifier mangling INJECTIVE per scope (e.g. encode case: `N` -> `n'U`/`_N` style, reserved-word prefix that cannot collide,
uniqueness check with a deterministic suffix), or refuse a program where two distinct source names (incl. globals vs locals/params,
generated names like _tu_*, py_*, v_, r) map to the same WhyML identifier in one scope. Census all identifier-mangling sites.

## REPAIR (2026-10-24, r327 executor off aa1cf01c; commits 329d3a10 (code), edf5b05e (corpus, census, docs) + route docs)
**Design (measured first).** Two options were priced on the AST of every file (`.r327tmp/scan.py`, approximation of the emitted names):
| option | root (3077) | pyref (510 incl. dirs) | mirror (53) |
|---|---|---|---|
| INJECTIVE encoding (case-marked `N`, collision-free keyword prefix) | ~1962 files re-emit | ~48 | ~48 (every whole-file proof re-OWED) |
| REFUSE a collision in a scope (landed) | 1 file (4260, already REFUSED by #325; message changes) | 0 | 0 |
The refusal was chosen: no mirror file and no previously-emitting corpus file is touched. The name-level scan found 12 more
hits, all `c = C()` (a class beside its instance): classes lower to the TYPE namespace and constructors are `Call`s, so the
landed rule reads only VALUE names and none of those 12 is refused (control 4309).
Rule `PYCSL-R327-IDENT-COLLISION`, inline in `_run_pipeline` just before Module 6, on the FINAL IR (after resolve /
monomorphize) — the mirror twin of `_run_pipeline` is `\trusted`, no new def, ledger 3:
- per function: formal parameters + every `Var` read (locals and the module-level globals it names) + every binding target
  (`target` / `targets` / quantifier `var` / comprehension and walrus targets) of body AND contracts must be injective under
  `whyml_ident`; a user name in the generated `_tu_*` tuple-binder space is refused;
- module level: IR function names + every module-level value binding read off the source (any nesting outside def / class
  bodies and the `if __name__ ...` driver; imports excluded — typing names are not values);
- classes: two `type_decls` names equal after `.lower()` (their method symbols `ab__m` fold).

**Census of identifier-mangling sites.** `identifiers.py::whyml_ident` (case fold, `py_` prefix, `_`, dots, non-ASCII) — every
value/function name: CHECKED by the rule above. `safe_mutex_name` (via whyml_ident, concurrent model): unchecked (mutex names are
not values the proof reads). `safe_exc_name` (strips leading `_`, deliberately merges `_Y` / `Y` aliases): RESIDUAL (exceptions).
`<Class>.lower() + "__" + method` (functions.py / scc.py / pycsl.py): CHECKED (class rule). Record fields (`whyml_ident(field)`):
`self.N` / `self.n` emit `{ mutable n; mutable n }`, which Why3 REJECTS ("Field n is used more than once") — fail-closed, not
refused. `fld.lstrip("_")` map-reader bases (expressions.py 11548 / 16756, statements.py 8331): mirror-specific shapes gated on
`_record_types` / `_variant_types`, not user-reachable — RESIDUAL. Generated binders `r` (`with Return r -> r`) and `v_`
(`Some v_ -> v_`) carry no user expression inside their scope (measured on n36 / n33: the user name outside the arm is the
global) — not a collision; their confusion of #325's TEXTUAL taint scan is route #328's.

**Probe table** (full proofs via heavy.sh; CPython rc 1 = contract violated):
| witness | corpus | base | after |
|---|---|---|---|
| n40 `N = len(xs); n = 0; N == n` | 4300 | rc=0 PROVED | rc=1 REFUSED R327 |
| n24 `Y = n; y = 0; return Y` | 4301 | rc=0 PROVED | rc=1 REFUSED R327 |
| n09 `K = 7; k = 3; return K` | 4302 | rc=0 PROVED | rc=1 REFUSED R327 |
| n31 global `K = mk()` vs param `k` | 4303 | rc=0 PROVED | rc=1 REFUSED R327 |
| n06 global `F = 0.5` vs param `f` | 4304 | rc=0 PROVED | rc=1 REFUSED R327 |
| n27 `result` vs `py_result` | 4305 | rc=0 PROVED | rc=1 REFUSED R327 |
| n14 `py_model` vs `model` | 4306 | rc=0 PROVED | rc=1 REFUSED R327 |
| functions `F` / `f` | 4307 | rc=1 FAIL (two `let function f`) | rc=1 REFUSED R327 |
| classes `Ab` / `AB` | 4308 | rc=1 FAIL (Why3 error) | rc=1 REFUSED R327 |
| module globals `k = three()`, `K = seven()` | 4311 | rc=1 REFUSED R325 | rc=1 REFUSED R327 |
| quantifier `\forall I` vs parameter `i` (q_quant2, not filed) | - | rc=1 (binder emitted as `I`: syntax error) | rc=1 REFUSED R327 |
| control `c = C()` | 4309 | rc=0 | rc=0 PROVED |
| control capitalised `N` with no twin | 4310 | rc=0 | rc=0 PROVED |

**Blast radius.** Corpus root (2190 base / 2194 candidate emitted, 4 new control sources): 0 MOVED, 0 GONE, 0 APPEARED; pyref
2186/2186 0/0/0; mirror 53/53 0/0/0 (`--min-files 50`) — no OWED proof, no latent false proof. The only existing corpus file whose
outcome text changes is 4260 (#325's lambda case-fold witness, REFUSED before and after; its refusal is now R327 — census row
re-measured). A first cut refused two MIRROR files (`frontend/__init__`, `frontend/ir_resolve`: the inlined dependency
`_subst_var` reads `isinstance(node, Var)` beside its parameter `var`); the class operand of `isinstance` / `issubclass` lowers
to a type tag spelled with the source name, never a variable, and is exempt (2a1e8474) — measured 53/53 after.
**Gates** (exit codes; logs in the r327 worktree, removed after the run): witness tables above (full proofs, heavy.sh);
byte-diff-compare root rc=0, pyref rc=0, mirror rc=0 (base worktree at aa1cf01c, compared once per tree);
check-self-annotate-sync.sh rc=0 (926 functions), self-annotate-mirror-check.sh rc=0 (53); run-soundness-planes.sh fast 61/61
rc=0; doc-coherency --check rc=0; check-assumed-facts rc=0 (ledger 3); check-trusted-raises-honesty rc=0 (61 silent, ratchet 61);
check-refusal-witness-coverage rc=0 (278 demonstrated / 5 not, ceiling 5; rows for 4300-4311, 4315-4323 written by `_census_row`,
paths of the main tree); check-dropped-mutation rc=0. `--slow` planes NOT run (heavy queue shared).
**Residuals.** (1) record FIELDS that fold (`self.N` / `self.n`) are not refused — Why3 rejects the record ("Field n is used more
than once"), fail-closed. (2) `safe_exc_name` merges `_E` and `E` on purpose (import aliases); two DISTINCT user exceptions so
named would share one `exception` — unmeasured, open. (3) the map-reader bases `fld.lstrip("_")` are mirror-only shapes. (4) a
contract quantifier binder is emitted with its SOURCE case (`forall I : int. ... i ...`), so an upper-case binder alone is a
Why3 error (fail-closed) — binders are not mangled consistently with their body occurrences; a lower-case binder is fine.
(5) the module-level scan reads simple Name bindings (incl. tuple / for / with / walrus targets via `ast` walk); names bound by
`global` inside a function are covered by the function scope only.
