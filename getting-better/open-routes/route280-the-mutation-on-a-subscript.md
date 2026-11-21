# OPEN ROUTE #280 — A MUTATOR CALLED ON A SUBSCRIPTED / CALL-RESULT RECEIVER IS DROPPED
**Status: REPAIRED (gen #37, 2026-10-19; opened the same day), Severity 1.** Red-team round 6; driver-reproduced at 78162575 (7 files rc=0; CPython AssertionError).
Witnesses `witnesses-r280/`: `d[k].append/pop/clear`, `d.get(0, []).append`, `t[0].append` emit body-less stubs
(`let _ = (append_1 1)`, `pop_0 ()`) that never touch the receiver, so frame/`\old`/alias claims prove falsely
(p228 `assigns \nothing`; p230/p237/p240 value claims; p223/p233/p251 aliased local). The "mutator with no certified
lowering" refusal only checks plain-name receivers; list-of-lists receivers already fail closed (p227/p234/p235).
Repair: refuse (or model) every receiver mutator whose receiver is not a plain name with a certified lowering —
census all mutator names (append/extend/insert/pop/remove/clear/sort/reverse/update/setdefault/add/discard/...).

## REPAIR (2026-10-19, worktree pycsl-r279 off 72ab1c57)
Probe table (`pycsl.py`, rc; CPython ground truth in each corpus file's `__main__`):

| shape | 72ab1c57 | after |
|---|---|---|
| `d[0].append(1)` under `assigns \nothing`, `len(d[0]) == \old(..)` (p228 / 3089) | PROVED | REFUSED |
| `d[0].pop(); len(d[0]) == 1` (p230 / 3090) | PROVED | REFUSED |
| `d.get(0, []).append(1)` then `len(a)` (p233 / 3091) | PROVED | REFUSED |
| `t[0].append(1)` then `len(a)` (p251 / 3092) | PROVED | REFUSED |
| `d[0].clear()`, `d[0] == \old(d[0])` (p237 / 3093) | PROVED | REFUSED |
| USER method writing its receiver on a tuple element `t[0].bump()` (q1 / 3094) | PROVED | REFUSED |
| user method on a call result `c.me().bump()` (q2 / 3095) | PROVED | REFUSED |
| `super().bump()` in an override declared `assigns \nothing` (q30 / 3096) | PROVED | REFUSED |
| `d[0].append(1)` aliasing `a` (p223 / 3098), `d[0].append(1); return len(d[0])` (p240 / 3099) | PROVED | REFUSED |
| list-of-lists / set-in-dict / dict-in-dict receivers (p226/p227/p232/p234/p235/p238/p239, q3/q4) | FAIL (opaque or ill-typed, by accident) | REFUSED |
| no-`assigns` writer (q24), transitive writer `t[0].go()` -> `self.bump()` (q25) | not proved (timeout) | REFUSED |
| controls 3097: `assigns \nothing` method on a tuple element; a READ `len(d[0])` | PASS | PASS |
| 1581/1582/1615/pyref 0060 (`C(0).sget()`, `super().sget()`, `C().go(-1)`, `C(6).get()`: pure callees) | emitted | emitted, byte-identical |

How the list-of-lists receivers "already failed closed" (measured): not by a refusal — `m[0].append(1)`
lowered to `append_2 m[0] 1` and the follow-up `len(m[0])` to an opaque `iter_length`, or the receiver term was
ill-typed for the int-model op (L3-tc). Same stub, same dropped effect; they FAILED only because the claim
around them could not be stated. The repair makes that a deliberate refusal at the stub site.
Rule (inline in `_handle_call_expr`'s generic receiver-carrying fallback — the one site every computed-receiver
method call reaches when no recognizer models it; mirror twin `\trusted`; the method already raised
`PyCSLSemanticError`; no new def/field; code `PYCSL-M6-MUTATOR-ON-COMPUTED-RECEIVER`): a call whose receiver is
not a dotted name (subscript, tuple element, call result, attribute of one, `super()`) is REFUSED when its
method name is (a) a collection mutator — list/dict/set (`append extend insert remove pop clear sort reverse
update popitem setdefault add discard intersection_update difference_update symmetric_difference_update`), deque
(`appendleft popleft extendleft rotate`), OrderedDict `move_to_end`, the in-place dunders (`__setitem__
__delitem__ __iadd__ __isub__ __imul__ __ior__ __iand__ __ixor__`) — or (b) the name of a same-file method that
may write its receiver: a least fixpoint over methods — declared `assigns` other than `\nothing`, or (no declared
frame) a body with a field/element store, `global`/`nonlocal`, a call handed `self`, or a call whose short name is
a mutator or already a writer. Name-keyed across classes (a collision only refuses more), except that a
`super()` receiver leaves out the CURRENT class's own override (it runs a base method): the mirror's
`_Unparser.traverse` calls `super().visit` = `NodeVisitor.visit` (`assigns \nothing`) while `_Unparser.visit`
writes `_source` — the name-only cut refused mirror pure_ast (1 GONE) and three pure-callee corpus witnesses
(1581/1582/1615, pyref 0060), both measured and both now inert.
Census (AST over corpus root + pyref + mirror + pycsl_lib, collection mutator on a non-dotted receiver): 3 sites,
all mirror — `groups.setdefault(g, []).append(..)` in `_verify_module_groups` (BESPOKE whole-function lowering,
never reaches the fallback: emission byte-identical), and two in `\trusted` bodies (`_transpile_modular`,
`audit_proof._audit_one_prover`).
Blast radius: corpus root 0 MOVED / 0 GONE / 0 APPEARED (1791/1791 + 20 new sources), pyref 0/0/0 (2186/2186),
mirror 0/0/0 (53/53). No mover, no owed re-proof.
Gates (logs under the r279 scratchpad; all run at 92bf0097's tree, base = worktree at 72ab1c57): witnesses
3080-3086/3089-3096/3098/3099 rc=0 -> rc=1 (refused), 3087 rc=1 (ill-typed) -> rc=1 (refused), controls 3088/3097
rc=0 -> rc=0; the 9 route witnesses (p117 p216 p223 p228 p230 p233 p237 p240 p251) rc=0 -> rc=1. byte-diff-sweep
base/after rc=0; byte-diff-compare root rc=0 (1791/1791) and pyref rc=0 (2186/2186); mirror-emit-sweep base/after
rc=0, compare `--min-files 50` rc=0 (53/53). check-self-annotate-sync.sh rc=0 (921 verbatim);
self-annotate-mirror-check.sh rc=0 (53). refusal-witness census +18 rows (3080-3087, 3089-3096, 3098, 3099) via the
plane's own `--append-new`, keeping only these rows (the run also re-measured ~230 pre-existing rows without a
census entry; not committed): refusal-witness-coverage OK (238 demonstrated, 5 undemonstrated = ceiling).
`run-soundness-planes.sh --slow` rc=1: 83 of 84 green, the one RED `check-assigns-writes-survival` (TRAP 1447 >
1445) is PRE-EXISTING — measured identical (1447) on the base tree with the base mirror emission, which is
byte-identical to this one. Ledger unchanged (3 axioms); no `\trusted` marker added; no owed whole-file proof.
Residuals: `x = d[0]; x.append(1); len(d[0])` (q23 — a plain-name receiver bound FROM a dict value) and
`self.d[0].append(1)` (p236) are fail-closed by an ill-typed / unbound emission, not by this rule.
