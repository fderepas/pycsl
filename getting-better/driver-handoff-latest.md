# HANDOFF — read this FIRST on relaunch (written by the supervisor, 2026-08-26)

The previous driver turn and its bundle executor BOTH returned. Nothing was landed by the
bundle attempt; the tree was reverted clean. This file records what they measured so you do
NOT re-derive it. VERIFY before building on it (lesson: re-measure, never inherit — the last
driver was burned twice by inherited premises), but start from here.

## Method state: capability-first is REFUTED for this regime

THREE convergent yield-0 capability builds this window: L10 (20 candidates -> 0), L12 (10 -> 0),
L9 follow-on (4 -> 0). Every remaining stub needs TWO OR MORE UNRELATED capabilities at once.
Building a capability then hunting candidates is structurally guaranteed to yield zero here, and
the payoff gate then correctly discards working code (L12's ~120 working lines were discarded).

Corrected operating strategy: DEMAND-FIRST. Pick a target stub, CLOSE its blocker set by
ITERATED measurement, land the whole bundle as ONE increment, put the payoff gate on the BUNDLE.

## Method defect found (this is the upstream fix)

"First blocker" != "blocker set". The earlier measurement reported only the FIRST L3-tc error per
candidate. For `parse_implication` the recursion error MASKED two further blockers. Closing a set
requires iteratively removing each blocker until L3-tc PASSES. Scope any future bundle from a stub
whose set has been closed that way, never from a single first-error reading. The payoff gate did
its job twice; the fix is upstream of the gate, in CANDIDATE SELECTION.

## `parse_implication`: true closed blocker set is FIVE, not three

Built and VERIFIED WORKING (reproduce mechanically from this list; all were reverted):
1. union-local typing — Module5 `_union_ret_by_func` registry + `_union_call_ret_type`; Module6
   no-double-wrap on a union-returning call, record-carrier sentinel via `_record_default_literal`,
   carrier-FIELD projection, `_is_string_expr` routing so a projected `str` field uses `str_eq_op`.
   NOTE: unions are NOMINALLY distinct even when structurally identical -> a union value can be
   RETURNED but never PASSED as an argument. `_union_<scope>_<idx>` is name mangling, not scoping,
   so the type is visible at every caller and collisions are impossible.
2. recursive-method emission — new `IRScanner.calls_self_method(py_name, obj)` matching the one
   exact string `self.<own python name>`, wired at the `is_recursive` site by splitting the mangled
   `<selftype>__<method>`. Fail-closed; mutual recursion deliberately still undetected (fails loudly).
3. `#@ \variant \length(self.toks) - self.pos` on the mirror method.

STILL BLOCKING (outside the bundle, NOT yet built):
4. STRING-FORM UNION TYPE ALIAS. `src/self-annotate/src/proof2why3/ir.py:121` is literally
   `Term = 0  # pycsl: stubbed type alias (string form unsupported)`. The LIVE definition at
   `src/pycsl/proof2why3/ir.py:136` is a string-form 9-arm union alias:
   `Term = "Var | IntLit | BoolLit | App | BinOp | UnaryOp | Forall | Exists | Unsupported"`.
   The stub generator cannot express it, so every `-> Term` in the mirror lowers to `int`.
5. FROZEN-DATACLASS IMMUTABILITY. Even given a real `Term` sum type, the arm records emit MUTABLE
   (`binop @rho`) despite `@dataclass(frozen=True)` on all nine — THE EMITTER IGNORES `frozen`.
   This CORRECTS the earlier impl-doc premise that the Term family is immutable. IT IS NOT.

Residual error verbatim:
```
src/self-annotate/src/proof2why3/parser.mlw:418:20-75:
This expression has type PyCSL_Program.binop @rho, but is expected to have type int
```
i.e. `raise (Return { binop_op = "->"; binop_lhs = !lhs; binop_rhs = !rhs })` vs `exception Return int`.

## HIGHEST-DENSITY LEVER MEASURED THIS WINDOW — start here

Capabilities (4)+(5) are SHARED: together they are also the FIRST blocker for `parse_comparison`,
`parse_disjunction`, and `parse_atom` (`binop @rho` / `intlit @rho` vs `int`).
=> 4 of the 6 cursor stubs sit behind ONE pair of capabilities, and it is DEMAND-FIRST rather than
capability-first. Close that set by iterated measurement, then land it as one bundle with the payoff
gate on the bundle. Flag: `is_recursive` feeds emission for EVERY corpus program, so the corpus
byte-diff is the HIGH-RISK gate for any bundle including capability (2).
