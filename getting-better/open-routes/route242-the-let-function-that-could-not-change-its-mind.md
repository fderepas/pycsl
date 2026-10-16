# ROUTE #242 (REPAIRED) — A `let function` WHOSE BODY IS NONDETERMINISTIC IS ONE VALUE PER ARGUMENT

**Status: REPAIRED (gen #36, 2026-10-16; opened 2026-10-15), Severity 1.** Recorded as a residual by the #240/#241 repair executor
(present before and after that repair); driver-reproduced at HEAD 961346bb — all three witnesses rc=0
"Verification SUCCESS"; CPython prints 0 for each.

## Witnesses
- `let_function_bool_true_vs_one.py`: `h(x: int)` returns 1 iff `isinstance(x, bool)`; `m()` returns 1 iff
  `h(True) == h(1)` — `\result == 1` PROVES (CPython: 1 vs 0 -> m() = 0).
- `let_function_type_is_bool.py`: same with `type(x) == bool`.
- `let_function_generator_twice_equal.py`: `r()` returns a generator; `r() == r()` proves (two distinct
  generator objects compare unequal in CPython).

## Mechanism
A Python function with no writes is emitted as a Why3 `let function`. Why3 treats a `let function` as a
mathematical function of its arguments, so a fresh `(any int)` / opaque program `val` call inside its body is
fixed per argument: measured `let function r () = (any int)` proves `r () = r ()`. Combined with `True`
lowering to `1`, `h(True)` and `h(1)` are the same term.

## Repair direction
A function whose body (transitively) contains a nondeterministic construct — `any`, a call to an opaque
program `val` without a functional spec, an erased value — must not be a `let function` (emit `let`, so each
call is a fresh evaluation), or the model must distinguish `True` from `1` where it matters. Check how spec
contexts that reference such a function are handled (they need the function form): refuse those references
or provide a contract-only `val function` whose result is constrained only by the postcondition.
Also check route #237's contract-side `hval_isinst_opaque h "bool"` (True and 1 are both `HInt 1`).

## Probe table (hand `.mlw`, `why3 prove -P z3`; base = f0fc0201; logs `scratchpad/r242/hand/`, `hand.log`)
| probe | shape | result |
|---|---|---|
| (a) | `let function r () = any int`; `if r () = r () then 1 else 0` ensures `= 1` | **Valid** — accepted, frozen |
| (b) | `let function h x = if op x then 1 else 0` over a program `val op`; `h 1 = h 1`; `goal forall x. h x = h x` | accepted by Why3, both **Valid** |
| (c) | same body as a plain `let h` | `m'vc` **Unknown** — two calls, two values |
| (d)/(h) | contract `ensures { result = h y }` with `let function h` / plain `let h` | Valid / L3-tc `unbound function or predicate symbol 'h'` |
| (e)/(f) | caller of an impure-body `let function` vs `let`, claim `result ∈ {0,1}` | both **Unknown**: a `let function` with a non-logic body gives callers ONLY determinism + spec usability, no body facts |
| (g) | plain `let h x = x + 1` (no contract), caller claims `h 2 = 3` | Valid (Why3 infers the post of a simple `let`) |

(c) WHY `let function`: Module 5 `_detect_purity` marks a function `pure` iff `assigns \nothing`, not
`\diverges`, not `\trusted`; `scc.emits_as_logic_symbol` then makes it a logic symbol, so contracts can name
it (`ensures \result == sq(y)`), callers get congruence, and `_emitted_logic_funcs` lets a call comprehension
lift `result[i] = g(src[i])`. A contract reference to a non-logic function was already fail-closed (L3-tc,
measured `scratchpad/r242/p/spec_ref_impure.py`).

(d) CENSUS at base (`census.py` over the f0fc0201 sweep): 125 corpus files / 241 `let function` blocks whose
body reads `any` or some program `val` (most are specified builtin models: `str_length_op` ...). By kind of
callee `val`: 53 pinned (`result = ..`), 47 partial (`sorted_1`, `str_sub_op`, user method `c_get_0`), 95 no
`ensures`; 8 `any` bodies. pyref: 0 (no contracts, so nothing is `pure`). The landed rule (below) moves 54
corpus files and 11 mirror files.

## Repair landed (gen #36, 2026-10-16)
`functions._emit_function` (the wrapper; its mirror twin is a `\trusted` stub, so no re-port) post-processes
each emitted block: a body that reads a NONDETERMINISTIC device is emitted as a plain `let [rec]` (header
keyword only; body, contract, variant unchanged) and the name leaves `_emitted_logic_funcs`. Devices:
- `any` (an erased value, a generator, a havoc);
- a call to an abstract-op program `val` whose contract does NOT PIN its result (scalar
  `ensures { result = .. }` / `result <-> ..`, or an array's length AND every cell) — unknown external calls,
  undecided `isinstance`/`type` tests (`py_isinstance_bool_int_op`, `py_type_1`), filesystem probes, a user
  method's partial contract (`c_roll_0`), partial builtin models (`sorted_1`, `str_sub_op`: a completeness
  cost only);
- a call to a bodyless user `val` (`\trusted`/`\abstract`) whose contract does not pin its result;
- a call to a function already found nondeterministic (SCC order puts callees first; plain `let`s are tracked
  too, so `g() = r()` over a contract-less generator `r` is caught).
A contract reference to a demoted function fails L3-tc (`unbound function or predicate symbol`), the existing
fail-closed answer for any non-logic function in a spec (2274). Deterministic bodies are untouched.
No new def, raise, refusal or axiom; ledger 3. The new per-module set `self._r242_nondet` is declared in the
mirror stub's `#@ assigns` clause (`check-assigns-underdeclaration` asked for it: TRAP 4 > 3; emission-inert).

## Witnesses (corpus, `gen36_r242`; CPython ground truth `scratchpad/r242/ground.log`)
False claims PROVED at f0fc0201, FAIL after: 2270 (`h(True) == h(1)`, isinstance), 2271 (`type(x) == bool`),
2272 (`r() == r()` generators), 2273 (through a contract-less plain `let`), 2277 (`\trusted` callee with a
partial contract), 2278 (method call with a partial contract) — post Unknown/Timeout; 2274 (contract
`\result == h(1)` for `k() = h(True)`) — fail-closed L3-tc `unbound function or predicate symbol 'h'`.
Controls PASS at base and after: 2275 (a deterministic `let function` used in a contract), 2276 (a
nondeterministic function called once, its declared contract used).

## Gates (logs: `/tmp/claude-1000/.../scratchpad/r242/`)
- Witnesses: `witness.log` (2270-2277), `witness-2278.log`.
- Corpus byte-diff vs a fresh f0fc0201 worktree: root 1574 baseline / 1583 candidate, 54 MOVED, 0 GONE,
  0 APPEARED, 9 new sources; pyref 2198/2198, 0 MOVED. Every MOVED diff is header-only
  (`let [rec] function f` -> `let [rec] f`). All 54 re-proved at base and after (`m1.log`, `m1b.log`,
  `m1c.log`): every verdict kept (PASS/PASS or FAIL/FAIL), so no proved claim depended on the frozen
  determinism.
- Mirror: 11 MOVED (header-only), `why3 --type-only` clean: `frontend/{Module1_Ingestor, desugar,
  exec_splice, module_collect, pure_ast}`, `module6_whyml/{identifiers, scc}`, `proof2why3/{extract_lean_meta,
  sertop}`, `proof_axiom_allowlist`, `pycsl`. The 16 demoted functions re-proved per function
  (`-T PyCSL_Program -G <fn>'vc`): 23 goals, 0 non-Valid. Whole-file re-proofs queued to the driver.
- Planes 61/61; sync rc=0 (915 verbatim); mirror-check rc=0. Ledger 3.

## Residuals (NOT repaired here)
- **Contract-side `hval_isinst_opaque` (route #237) is a function of the hval, and `True`/`1` are both
  `HInt 1`.** `#@ requires d["a"] == d["b"]` / `#@ ensures isinstance(d["a"], bool) == isinstance(d["b"],
  bool)` on `f(d: Dict[str, PyVal])` PROVES (congruence); CPython `f({"a": True, "b": 1})` meets the
  precondition (`True == 1`) and violates the postcondition. Reproducer `scratchpad/r242/res/spec_bool.py`.
  Needs its own route (a spec has no fresh value; refuse an opaque `HInt` arm in a contract).
- A multi-member SCC of pure functions keeps its `with function` chain even when a member is
  nondeterministic (it is recorded as nondeterministic for callers); not exploited.
- Bespoke fold groups emitted outside `_emit_function` (e.g. 0956's `fvs__binders` over the opaque
  `fvs__set_add`) keep `let function`; the callee is a deterministic set-add, contract `ensures True`.
