# OPEN ROUTE #279 — LIST ALIASING LOST BY `+=` AND BY CHAINED ASSIGNMENT
**Status: REPAIRED (gen #37, 2026-10-19; opened the same day), Severity 1.** Red-team round 6; driver-reproduced at 78162575 (rc=0; CPython AssertionError).
Witnesses `witnesses-r279/`. p117: `b = a; b += [1]; len(a)` proves 1 (emits `b := !b ++ ...` on a copy); the
aliased-list-mutation refusal fires for `.append` (p143) but not for `+=` on a list. p216: `a = b = []; b.append(1)`
proves `len(a) == 0` — chained assignment goes through a temp (`a := !_pycsl_multi_1; b := !_pycsl_multi_1`) that
the alias refusal does not see. Repair: treat list `+=` as an in-place mutation for the alias rule, and treat a
chained assignment of a mutable value as an alias binding (refuse or model).

## REPAIR (2026-10-19, worktree pycsl-r279 off 72ab1c57)
Probe table (`pycsl.py`, rc; CPython ground truth in each corpus file's `__main__`):

| shape | 72ab1c57 | after |
|---|---|---|
| `b = a; b += [1]; len(a)` (p117 / 3080) | PROVED | REFUSED |
| `a = b = []; b.append(1); len(a)` (p216 / 3081) | PROVED | REFUSED |
| rebind of a DECLARED name `b = a; b.append(2)` (3082) | PROVED | REFUSED |
| `for ..: b.append(i); b = a` (mutation at the loop top, 3083) | PROVED | REFUSED |
| `a = b = x` name source, `b.append` (3084) | PROVED | REFUSED |
| two-step `b = a; c = b; c += [2]` (3085) | PROVED | REFUSED |
| alias bound in an `if`, mutated after it (3086) | PROVED | REFUSED |
| list PARAMETER `b = xs; b += [1]` (3087), `b = xs; b.append` (q14), `b *= 2` (q7), `a = b = [0]; b += [1]` (q11) | FAIL (ill-typed) / PROVED (q11) | REFUSED |
| controls 3088: element store through an array alias; alias killed by a rebind (`b = a; b = []; b.append(i)` in a loop); read-only alias | PASS | PASS |
| `|=` on a set/dict alias (q5/q6), `xs += ..` on a list param (q9) | REFUSED (routes #59/#243, param `+=`) | REFUSED (unchanged) |

Rule (inline in `_handle_assign_stmt`, after route #81's fence; mirror twin `\trusted`; no new def/field;
new code `PYCSL-M6-MUTATION-THROUGH-COLLECTION-ALIAS`; route #81's message and code untouched so its witness
rows stand): a name-to-name binding `t = s` whose source is a list (array/seq local, list parameter) or a
chained-assignment temporary `_pycsl_multi_N` holding a list/dict/set starts a LIVE alias set `{t, s}`. The
statements after it are walked IN ORDER: a top-level `x = <live>` adds `x`, a top-level rebind of a live name to
anything else KILLS it, a nested name-to-name assignment touching a live name may add one. A mutation through a
live name refuses: a collection mutator method (append/extend/insert/remove/pop/clear/sort/reverse/update/
popitem/setdefault/add/discard/*_update), an augmented assignment with ANY operator (on a list `+=`/`*=` are in
place, the rest raise), and for a chained temporary an element store. If two or more names are still live when
the block ends, the alias ESCAPES it (next loop iteration, statements after an enclosing `if`): the class is
closed over every name-to-name assignment of the whole function and a mutation anywhere in it refuses (coarse:
may refuse a dead alias, never accepts a live one). Element stores through a plain list alias stay supported
(the array model shares the array; 1131 / 3088).
Census (AST, before the rule): chained assignments in corpus root + pyref + mirror = 3 (`a = b = 5`,
`p = q = three()` in 0971, `lower = upper = step = None` in mirror pure_ast) — none of a collection; list
`x += <display>` on a name: 8, none through an alias. A flow-INSENSITIVE first cut refused the mirror's
`pure_ast` parser (`posonly = args; args = []` then `args.append`, no alias) — measured with the mirror sweep
(1 GONE), which is why the kill rule exists.
Blast radius: corpus root 0 MOVED / 0 GONE / 0 APPEARED (1791 / 1791, plus the 20 new 3080-3099 sources), pyref
0/0/0 (2186/2186), mirror 0/0/0 (53/53). No mover, so no whole-file re-proof is owed.
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
Also now REFUSED by the rule (they were ill-typed, rc=1, before): chained dict/set/list-store aliases
(`a = b = {}` + store, `a = b = set()` + `add`, `a = b = [0]` + store: p247/p248/p249, q12) and a seq-promoted
alias mutated before the binding then stored through (q18/q19, escaping-alias leg).
Residuals (fail-closed today, not by this rule): a dict/set RE-bound alias (`a = b` with `a` declared, q21/q22)
and a list bound from a dict value (`x = d[0]; x.append`, q23) are ill-typed emissions (rc=1, never a success);
the chained OBJECT alias `a = b = A()` (p246) likewise. Parameter-aliasing probes p111/p112/p114
(`f(a, a)`, `m = [r, r]`) still PROVE: they are the separation (distinct-parameter) premise, outside this route.
