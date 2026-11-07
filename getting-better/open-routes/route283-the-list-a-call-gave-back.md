# OPEN ROUTE #283 — A LIST RETURNED BY A USER FUNCTION: append WRITES SLOT 0, len NEVER GROWS, ALIAS AND FRAME LOST
**Status: REPAIRED (gen #37, 2026-10-20; opened the same day), Severity 1.** Red-team round 7; driver-reproduced at 83aa79bd (p143/p130/p003/p019 rc=0; CPython AssertionError).
Witnesses `witnesses-r283/`. `b = ident(a); b.append(1)` lowers to `let b = (ident a) in b[!b_len] <- 1; b_len := !b_len + 1` with
`b_len` starting at 0 and `len` reading `Array.length`: the append overwrites b[0] (p130 claims b[0]==9, CPython 5), the length is
frozen (p143 len==1, CPython 2), and when `ident` returns its parameter the alias is lost (p003/p012/p017) and an `assigns \nothing`
caller mutates its own parameter through it (p019). Only `append` (+=/extend/insert/pop/clear/remove fail closed, p151-p156). #279's
alias refusal sees name-to-name aliases only. Repair: model or refuse `append` on a list local bound from a call result (length
counter must start at the real length; a returned parameter must be treated as an alias), census every list-from-call binding shape.

## REPAIR (2026-10-20, worktree pycsl-r283b off 7be313fe)
Root cause (located on the p143 `--no-proof --keep-mlw` emission): `_emit_body_code` declares `let <t>_len = ref 0`
for EVERY `.append` target, and `_handle_expr_stmt`'s array arm lowers the append to `t[!t_len] <- v; t_len := !t_len
+ 1`. The counter is right only for the `Array.make 1024 0` shadow it was built for. A local that Module5's
seq-promotion (`_detect_seq_promotion`) does not seed as a list — bound from a call/method result, a `*` repetition,
a conditional, a loop/walrus/unpack target, a dict value, an object field — keeps its real array and gets the 0
counter: the append overwrites slot 0 and `len` reads the frozen counter. A second, independent carrier sits on the
SEQ side: an ANNOTATED local (`b: List[int] = ident(a)`) IS seq-promoted and bound as `ref (snapshot (ident a))`,
a COPY, so a returned alias is lost there too; #279's trigger is `vt == "Var"` only.

Probe table (`pycsl.py`, rc; CPython ground truth in each corpus file's `__main__`; base = 7be313fe):

| shape | base | after |
|---|---|---|
| `b = ident([5]); b.append(9); len(b)` (p143 / 3300) | PROVED | REFUSED (A) |
| `... return b[0]` == 9 (p130 / 3301) | PROVED | REFUSED (A) |
| `b = ident(a); b.append(1); len(a)` (p003, p012, p017 / 3302) | PROVED | REFUSED (A) |
| `assigns \nothing` caller, `b = ident(a)` on its parameter (p019 / 3303) | PROVED | REFUSED (A) |
| FRESH `b = [0] * 3; b.append(9); len(b) == 1` (census / 3304) | PROVED | REFUSED (A) |
| annotated `b: List[int] = ident(a); b.append(1); len(a)` (3305) | PROVED | REFUSED (B) |
| annotated `b += [1]` through the returned alias (3306) | PROVED | REFUSED (B) |
| `b: List[int] = a if c > 0 else [9]; b.append(1)` (3307) | PROVED | REFUSED (B) |
| annotated twin of p019, parameter under `assigns \nothing` (3308) | PROVED | REFUSED (B) |
| `b: List[int] = ident(ident(a))` (3309) | PROVED | REFUSED (B) |
| controls 3310: `b: List[int] = ident([5]); b.append(9); len(b) == 2`; read-only returned alias; `sorted(a)` copy mutated; plain annotated local | PASS | PASS |
| other binding shapes, unannotated (method result, `x if c else [7]`, `or`, comprehension, `a[:]`, `.copy()`, `a + [6]`, tuple element, walrus, unpack, loop append, `d[0]`, `s.split()`, `list(map(..))`, for-target, nested element) | FAIL (ill-typed / unproven) | REFUSED (A), or unchanged FAIL (`list(a)`, `list(map(..))`, `list(range(..))`, `sorted(a)`, `list(reversed(a))`, unannotated `b = ident(a); b += [1]`, annotated tuple element / method-field, reverse-direction `a.append` with `len(b)`) |
| `extend`/`insert`/`pop`/`clear`/`sort`/`reverse` through a returned alias | REFUSED (#280 family) | unchanged |
| element store through a returned alias (`b = ident(a); b[0] = 7; a[0]`, annotated and reverse) | FAIL (unproven) | unchanged FAIL |

Rules (both inline, lesson a4; both enclosing methods have `\trusted` mirror twins; no new def/field):
- (A) `_handle_expr_stmt`, the array-counter `.append` arm (after #13b's `self.<field>` refusal, whose text is
  untouched): REFUSED outright, `PYCSL-WHYML-APPEND-UNTRACKED-LIST`. Measured population of the arm at 7be313fe:
  ZERO `X[!X_len] <-` append emissions in corpus root (1827 .mlw), pyref (2186) and the mirror (53) — the only
  `[!X_len] <-` lines are #49's literal-rebind lowering, a different site. Every local list that is appended to
  and type-checks already reaches the seq arm. Initialising the counter from `Array.length` was considered and
  rejected: the fixed-size array cannot grow, so it would only turn each append into an out-of-bounds goal.
- (B) `_handle_assign_stmt`, #279's block: a SEQ-PROMOTED target bound from a non-name, non-literal,
  non-comprehension, non-slice RHS collects PARTNERS — every list name (array/seq local, 1-D array param, list
  formal) inside the RHS, including a method-call receiver, except under a constructor that builds a fresh list
  (literal, comprehension, slice, `+`/`*`, `list`/`sorted`/`bytes`/`bytearray`/`len`, `.copy()`). Partners join
  #279's live set, so the same flow-sensitive walk (kill-on-rebind, whole-function closure when the alias
  escapes its block) refuses a mutation through the target OR a partner, with its own message,
  `PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS` (#279's message and code are untouched, so its census rows stand).
  No callee-freshness analysis: `b: List[int] = double(a); b.append(1)` with a FRESH-returning `double` is
  refused too (coarse; corpus population 0 — measured by the byte-diff below).
Census (AST over the sources; list local bound from a call/method/conditional/subscript and then mutated):
root 10 rows, all DICT stores (`c = Counter(..); c[k] = ..` in 0498-0514, route #59's 1128/1129/1519/2812);
pyref 0; mirror 16 rows (string `+=` accumulators, `\trusted` bodies, 2 `extend`, 1 `append` in
`Module6_WhyMLTranspiler`) — none reaches either rule (mirror 0 MOVED / 0 GONE).
Blast radius: corpus root 0 MOVED / 0 GONE / 0 APPEARED (1827 / 1827 + 1 new emitting source, 3310; 3300-3309 are
refused), pyref 0/0/0 (2186/2186), mirror 0/0/0 (53/53). No mover, so no whole-file re-proof is owed.
Gates (logs in the r283b scratchpad): witnesses 3300-3309 rc=0 -> rc=1 (refused, codes as tabled), control 3310
rc=0 -> rc=0; the 6 route witnesses (p003 p012 p017 p019 p130 p143) rc=0 -> rc=1. byte-diff-sweep base/after rc=0;
byte-diff-compare root rc=0 and pyref rc=0 (`--min-files 2000`); mirror-emit-sweep base/after rc=0, compare
`--min-files 50` rc=0. check-self-annotate-sync.sh rc=0 (923 verbatim); self-annotate-mirror-check.sh rc=0 (53).
`run-soundness-planes.sh` (fast) 60 of 61 green, the one RED `check-refusal-witness-coverage` = the predicted
ledger (two new refusal sites, undemonstrated 6): +10 census rows recorded by RUNNING the 10 witnesses through the
plane's own `_census_row` (not `--append-new`, which would also re-measure ~230 unrelated rowless witnesses),
then the plane alone rc=0 (242 demonstrated, 4 undemonstrated, ceiling 5). Slow planes run individually (the
battery exceeds the 9-minute foreground cap): check-param-mutator-visibility, check-open-route-carriers,
count-trusted-directives, check-hashed-literal-purity / check-clause-survival / check-emitted-function-coverage
(on the after emission), check-swallowed-exceptions, check-computed-rhs-erasure, check-internal-crash-free — all
rc=0. Not run: the remaining 14 slow planes (prover/mirror/emission planes; every emission they read is
byte-identical to base). Ledger unchanged (3 axioms); no `\trusted` marker added; no owed proof.
Residuals (fail-closed today, not by this rule): an object-field partner (`b: List[int] = c.get()` returning
`self.xs`, then appended) is ill-typed (rc=1); element stores through a returned alias emit and do not prove the
false claims probed (store visibility is #282's PARAM-DISJOINT territory when it crosses a parameter); a
fresh-returning callee is refused (completeness, see B); `b = a[:]; b.append(1)` (unannotated) is now refused (A)
instead of an unproven FAIL.

