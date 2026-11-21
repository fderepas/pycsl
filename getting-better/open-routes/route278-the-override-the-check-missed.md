# OPEN ROUTE #278 — `--check-behavioral-subtyping` IGNORES RAISES AND MRO-INHERITED OVERRIDES
**Status: REPAIRED (gen #37, 2026-10-19; opened the same day), Severity 1.** The check is now also the default (route #277). Red-team round 6; driver-reproduced at 78162575 WITH the flag (rc=0; CPython ValueError / AssertionError).
Witnesses `witnesses-r278/`. p091: `B.m` raises an undeclared ValueError; `use(a: A)` claims `no_exception \all`
over `a.m()` — the refinement goal compares requires/ensures only (not raises/no_exception), and #272's
undeclared-callee-raise rule resolves `a.m()` by static type A only. p092: `class B(M, A): pass` inherits `m`
from mixin M (returns 2) — override pairs are recorded only for methods DEFINED in the subclass, not for ones
the MRO supplies from another base. Repair: raises refinement (override's raises ⊆ base's declared raises) and
override pairs computed over the MRO-resolved method of every subclass.

## REPAIR (2026-10-19, r277 executor, off 72ab1c57; lands with route #277)

**Rules** (inline, no new def, ledger 3 — no axiom; every edited method's mirror twin is `\trusted`):
- **MRO pairs** (`ir_resolve.apply_inheritance`, after the merge): for every class S with a C3
  MRO, the provider P of name t (first class of the MRO defining or BINDING t) must refine every
  later X of that MRO that defines t: pair `(p__t, x__t)` unless already recorded (or S's own clone
  of P's method is already paired with X). Constructors excluded. A CLASS-BODY binding provider has
  no function, so its pair is refused by the existing `PYCSL-SUBTYPING-PAIR` (message now names the
  binding case and advises `def` or `--assume-class-exact`).
- **Raise conditions in the goal** (`_render_refinement_goal`): per declared `raises E when c_S` of
  the override, `((pre_X) /\ (c_S)) -> (c_X1 \/ ...)` over X's clauses for E or an ancestor.
- **PYCSL-SEM-OVERRIDE-REFINEMENT** (`_run_pipeline`, after route #272, which now also computes its
  escaping/declared/HIDDEN-OUT sets when a pair is to be judged): R1 the override may let escape
  only exceptions the base declares and its `no_exception` does not exclude (an undeclared raise
  only where the base's covering clause is unconditional; `*` never); R2 the base's `no_exception`
  set is kept; R3 if the base declares `assigns`, the override declares one naming only base
  locations — except a location rooted at a `self` field the base class does not have; R4 the
  override takes at least the base's positional parameters, and every one the base contract
  mentions keeps its position.

**Probe table** (rc; CPython in `__main__`; "flag" = `--check-behavioral-subtyping` at 72ab1c57):

| shape | 72ab1c57 default / flag | after (default) |
|---|---|---|
| p091 / **3104** undeclared `ValueError` in `B.m`, `use` `no_exception \all` | PROVED / PROVED | REFUSED (R1) |
| p092 / **3105** `class B(M, A): pass`, fieldless mixin `M.m == 2` | PROVED / PROVED | FAIL (`m__m_refines_a`) |
| g5 / **3106** provider through `M(N)` | PROVED / PROVED | FAIL (`n__m_refines_a`) |
| g6 / **3107** fieldless `A`, `B(A): pass`, `C(B).m == 2` (coverage) | FAIL (contract-free call) / FAIL, no goal | FAIL, goal `c__m_refines_a` built |
| g1 / **3108** `m = lambda self: 2` overriding `A.m` | PROVED / PROVED | REFUSED (PYCSL-SUBTYPING-PAIR) |
| g2 / **3109** override writes `self.v` against `assigns \nothing` | PROVED / PROVED | REFUSED (R3) |
| g3 / **3110** `m(self, y, x)` vs `m(self, x, y)` | PROVED / PROVED | REFUSED (R4) |
| **3111** `raises ValueError when k > 3` vs base `when k > 5`, caller `no_exception ValueError` | PROVED / PROVED | FAIL (raise-condition conjunct) |
| **3112** override drops base `no_exception \all` (`--strict-no-exception-propagation`; coverage) | refused (implicit-raise rule) | REFUSED (R2) |
| **3113** controls: keep `no_exception`, narrower raise condition, sub-only field write | PASS | PASS (4 goals Valid) |

Following the new refusal's advice (audited FOLLOWABLE): 3104/3109/3110 with the extra raise /
write removed or the parameters in base order VERIFY; 3104 and 3108 under `--assume-class-exact`
VERIFY (declared).

**A REAL MIRROR FINDING (route #268 family), repaired.** R3 refused the mirror
`Module6_WhyMLTranspiler.py`: the `\trusted` cross-mixin stub `statements.py::_expr_to_whyml`
declared a frame WITHOUT `_abstract_ops`, `_dict_locals`, `_quant_record_binders`,
`_quant_scalar_binders`, all four fields of `StatementEmissionMixin` that the MRO provider
(`expressions.py::_expr_to_whyml`) writes. So the VERIFIED mirror callers `_emit_array_local_reassign`
and `_seq_operand` carried frame postconditions (`ensures { self._abstract_ops = old ... }` etc.)
that the real provider violates — false frame claims in the mirror. The stub frame was widened to
its provider's, and `check-assigns-underdeclaration` then (correctly) required the two callers'
`assigns` to name the fields too (HOLE-D 7 -> 0, no further cascade). `pure_ast.py`'s
`_Unparser.visit` vs `NodeVisitor.visit` (`assigns \nothing`) is admitted by R3's field rule
(`NodeVisitor` has no fields).

**Blast radius (one landing with #277/#281).** Corpus byte-diff vs a base worktree at 72ab1c57:
root 1791 base / 1804 candidate, **9 MOVED** — 0444, 0445, 1347, 1448, 1449, 1453, 1568, 1582, 2781,
each BYTE-IDENTICAL to the base emission under `--check-behavioral-subtyping` (only the default
flipped; no extra pair from the MRO pass), re-proved: verdicts unchanged except 0445 (now expected
FAIL) — **2 GONE** 1343/1344 (route #123 class-body-binding witnesses, expected FAIL, now refused by
the binding pair), 0 APPEARED, 15 new sources; `byte-diff-compare` with those declared rc=0.
pyref 2186/2186 **0 MOVED** (0206 runs with `--assume-class-exact`; without it it gains the goal
`c__who_refines_b` and FAILS). Mirror 53/53 **3 MOVED**: `Module6_WhyMLTranspiler` (22 `true`
goals + the widened stub frame), `frontend__pure_ast` (3 `true` goals), `module6_whyml__statements`
(stub frame + the two callers' frames: 6 frame `ensures` dropped, 3 `writes` widened); all three
type-check (rc=0). Stdlib + conformance/negative emission (93 files): 0 moved.
**Ledgers** (lesson d5): refusal-witness census — rows of 1343/1344 (VERIFY-FAIL -> REFUSAL),
1805/1806 (stale REFUSAL rows from before gen #31; VERIFY-FAIL at 72ab1c57 too), 1833 (message
edited) re-measured by running, plus 0445 and the 13 new expected-FAIL witnesses; coverage 238
demonstrated / 4 undemonstrated (ceiling 5). Advice audit: PYCSL-SUBTYPING-PAIR and the #216
dunder refusal re-audited (hash updated), the new refusal audited FOLLOWABLE (143/157). Frontend
goldens: 38/38 (0445's line numbers kept).

**Gates** (logs in the r277 scratchpad, every leg tee'd with its rc): witnesses 3100-3119 table above
(base/after rc measured per file); byte-diff-sweep base rc=0 / after rc=0; byte-diff-compare root rc=0
with the 9 movers + 2 refusals DECLARED, pyref rc=0 (0 MOVED); mirror-emit-sweep base/after rc=0,
compare rc=0 with the 3 movers declared; the 3 moved mirror .mlw `why3 --type-only` rc=0;
check-self-annotate-sync.sh rc=0 (921 verbatim); self-annotate-mirror-check.sh rc=0 (53);
doc-coherency rc=0; run-soundness-planes.sh fast rc=0 (61/61 green after the ledger updates);
`--slow` 83/84 green — the one RED, `check-assigns-writes-survival` (TRAP 1447 > 1445), is
PRE-EXISTING: the same plane at 72ab1c57 on the base mirror emission gives TRAP 1447 (rc=1) with
the identical 1447 TRAP rows, so this landing neither causes nor moves it.
**OWED** (not proved here — the LOW heavy slot never freed in 70 min): whole-file proofs of the 3
moved mirror files. `module6_whyml__statements` is the one with real content: two verified methods
(`_emit_array_local_reassign`, `_seq_operand`) lose 6 FALSE frame `ensures` (weaker obligations) and
their callers lose those facts (`check-assigns-underdeclaration` HOLE/HOLE-D 0); the Transpiler moves
by the same stub frame plus 22 goals and `pure_ast` by 3 goals, every goal literally
`((true) -> (true)) /\ ((true) -> (true))`.
