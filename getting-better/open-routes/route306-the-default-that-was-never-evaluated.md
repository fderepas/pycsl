# OPEN ROUTE #306 — `d.get(k, default)` EVALUATES `default` LAZILY (Python evaluates it eagerly): its writes and its raises vanish
**Status: REPAIRED (gen #37, 2026-10-23; opened the same day), Severity 1.** Red-team round 13; driver-reproduced on main (5/5 rc=0; CPython violates).
Witnesses `witnesses-r306/`: `return d.get(1, 10 // x)` under `no_exception \all`, `requires 1 in d` proves (e22; CPython f({1:4},0)
raises ZeroDivisionError); index default `xs[i]` (e27, in_bounds checked only on the None arm); a callee `bump(xs)` with declared
`assigns xs[0]` passed as the default never runs in the model, so `ensures xs[0] == 0` proves WITHOUT no_exception (e10, e23); aliased
call (e32). e31 (`self.d.get`) lowers the same lazy way (failed only for lack of field knowledge; likely exploitable with an invariant).
Mechanism: expressions.py (~13934) emits `(match Map.get d k with | Some v_ -> v_ | None -> <default> end)`, so every effect and every
exception obligation of `<default>` lives on the None arm only. TypedDict `.get` evaluates eagerly (held); getattr(o,a,dflt) refused.
Repair: bind the default first (`let dflt = <default> in match ... | None -> dflt end`), preserving left-to-right order (receiver, key,
default) — or refuse a non-pure default. Census every lazy-arm lowering of an eagerly-evaluated Python argument (dict.get, dict.pop
default, setdefault, next(it, default), getattr default, min/max default=, str methods with default args).

## REPAIR (2026-10-23, r306 executor off 370e1875; commits 7d5af8a3 + 04dcd733 + 0bacb5ae + da973273 + route docs)
Probe table (`pycsl.py`, rc; CPython ground truth in each corpus file's `__main__`; probes in `scratch-r306/` of the
r306 worktree, corpus copies 3800-3819):

| shape | 370e1875 | after |
|---|---|---|
| e10 local dict, present key, default `bump(xs)` (assigns xs[0]), claim `xs[0] == 0` (3800) | PROVED | FAIL (goal unproven) |
| e22 `d.get(1, 10 // x)` under `no_exception \all` (3801) | PROVED | FAIL |
| e23 param dict + `1 in d`, default `bump(xs)` (3802) | PROVED | FAIL |
| e27 `d.get(1, a[5])` under `no_exception \all` (3803) | PROVED | FAIL |
| e31 `self.d.get(1, 10 // x)` (3804) | FAIL (no field knowledge) | FAIL (default now eager: div obligation on every path) |
| e32 param dict, `d.get(1, 10 // x)` (3805) | PROVED | FAIL |
| TypedDict `t.get("a", bump(xs))` — default DROPPED by the record lowering (3806) | PROVED | FAIL |
| TypedDict `t.get("a", 10 // x)` under `no_exception \all` (3807) | PROVED | FAIL |
| str-keyed `d.get("a", 10 // x)` / `d.get("a", bump(xs))` (3808/3809) | PROVED / PROVED | FAIL / FAIL |
| key-before-default order `d.get(bump(xs), bump(xs))`, claim 9 (CPython 7) (3810) | FAIL | FAIL |
| `Dict[str, PyVal]` `d.get("k", 10 // x)` (3811) | PROVED | FAIL |
| module-const str->str dict `OP_MAP.get("a", s[5])` (chained ITE, default in last `else`) (3812) | PROVED | FAIL |
| `m = max(s, default=bump(xs))` — `default` DROPPED (`max_1 ...`) (3813) | PROVED | REFUSED (route #275 keyword gate) |
| chained hval `d.get("a", {}).get("k", 10 // x)` (probe c12, not in corpus) | FAIL (L3-tc, pre-existing hval->int local) | FAIL (same; emission now binds the default) |
| `Dict[str, Any]` `d.get("a", 10 // x)` returning Any (probe c08) | FAIL (timeout) | FAIL |
| CONTROLS: literal defaults (3814), `d.get(2, 10 // x)` with `x != 0` (3815), missing key + callee default `xs[0] == 1` (3816), self-field guarded (3818), const-dict guarded (3819) | PASS | PASS |
| COVERAGE: PRESENT key + callee default, `xs[0] == 1` (3817) | FAIL | PASS |

Rules (inline, no new def, no new raise site, ledger 3, no IR change; `_lower_dict_get_call` has no mirror twin,
`_handle_call_expr` and `_reset_function_state` mirror twins are `\trusted`):
- "Atomic" default = `Number`/`String`/`Bool`/`None`/`Var`, a unary op on a `Number`, or an EMPTY dict/set/list
  literal (no effect, no raise). Every atomic default keeps its old emission byte-for-byte; spec contexts
  (`_in_spec`) are untouched (logic terms have no effects).
- `_lower_dict_get_call` body-local/param dict (int and str keys, hval codomain) and self-field dict: a non-atomic
  default is let-bound BEFORE the match, `(let dflt_r306 = D in match Map.get R k with ... | None -> dflt_r306 end)`;
  a non-atomic key is bound before it (`let k_r306 = K in`), so the order is Python's (receiver attribute, key,
  default) and the lookup reads the receiver AFTER the default ran (the bound `dict.get` sees the default's
  mutation of the same dict).
- hval receivers (`<pyval-expr>.get(k, D)`, both the plain and the route-#252 `no_exception` R5 form, and the K7
  pyval-local form): same binder; in the R5 form it sits after the receiver's AttributeError assert.
- record/TypedDict `.get("f", D)` (`_record_get_field`, which drops the default): a non-atomic D is evaluated for
  its effects/obligations, `(let _ = D in t.f)`.
- module-const str->str dict `.get(k, D)` chained ITE: a non-atomic key is bound once (it was REPEATED in every
  test, i.e. re-evaluated) and a non-atomic D bound before the chain.
- `max`/`min` `default=` (route #275 keyword gate in `_reset_function_state`): allowed only when atomic; otherwise
  REFUSED (the lowering drops the keyword). Message extended in place; the site stays DEMONSTRATED (3813).

CENSUS of lazy-arm / dropped lowerings of an eagerly-evaluated argument (grep of every `None -> {` /
`| None ->` producer in `module6_whyml` plus the default-dropping recognisers):
- REPAIRED: the six `.get` producers above + max/min `default=`.
- ALREADY EAGER / FAIL-CLOSED: `next(it, D)` (abstract `next_2 ... D`, an application argument, evaluated);
  `d.pop(k, D)` and `d.setdefault(k, D)` REFUSED (receiver mutation unmodelled / KeyError row); `getattr(o, a, D)`
  REFUSED under `no_exception` (not on the never-raises list); option-record `.get` (`_option_record_get_field`)
  takes a LITERAL default only.
- NOT USER DEFAULTS (internal sentinel arms, ν-typed missing placeholders, generic_fold `None ->` recursion arms,
  subscript `d[k]` KeyError arms, IfExpr `None` arm of `x if x is not None else y` — Python evaluates `y` lazily
  there, so the arm is faithful).
- RESIDUAL (mirror-only, unmeasured as exploitable): the emit_ir projection `.get("<field>", D)` recognisers
  (`_EMIT_IR_PROJ`, `_scoped2`) drop D; every corpus/pyref/mirror use has a literal/empty default (0 MOVED).
- RESIDUAL: a default that REBINDS the receiver name (`d.get(k, (d := {}))`) reads the rebound value; walrus in a
  `.get` default is not otherwise modelled.

Blast radius: corpus root 0 MOVED / 0 GONE / 0 APPEARED (2026 base / 2045 candidate, 19 new sources; 3813 refuses),
pyref 0/0/0 (2186/2186), mirror 0/0/0 (53/53). No mover, so no M1 re-proof and no OWED whole-file proof. (The root
and pyref compares were run twice: once after the dict.get commit, once after the const-dict commit; both 0/0/0.)
Gates (logs under the r306 scratchpad): witnesses rc=0 -> rc=1 (table); controls PASS; byte-diff-compare root rc=0,
pyref rc=0; mirror-emit-sweep base/after rc=0, compare `--min-files 50` rc=0; check-self-annotate-sync.sh rc=0 (926
un-trusted methods verbatim); self-annotate-mirror-check.sh rc=0; run-soundness-planes.sh fast 61/61 rc=0 (on the final
tree); doc-coherency --check rc=0; check-assumed-facts rc=0; check-refusal-witness-coverage rc=0 (250 demonstrated /
5, census rows for 3800-3813 measured by `_census_row`). Ledger 3.
