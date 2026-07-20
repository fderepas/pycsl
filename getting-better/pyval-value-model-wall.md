# pyval-value-model-wall.md — the faithful heterogeneous `Dict[str,Any]` value model

**For review. State-of-the-art report on the highest-remaining wall on the self-tcb-reduction frontier —
the common root the giants front, the Dict-of-Dict collectors, the `.values()` tree-walkers, and two latent
faithfulness bugs all share. This build is user-authorized (a dedicated multi-session budget).**

## 1. Global picture
PyCSL lowers annotated Python to WhyML, discharged by Why3/SMT. The self-annotation effort mirrors the live
emitter into `src/self-annotate/src/` and drives its `#@ \trusted` stub count DOWN by converting each stub to a
verified body under a fixed contract (`requires True / ensures True / assigns <frame>`), gated by three disjoint
oracle planes (fidelity, whole-file Why3 proof, corpus byte-diff-0). Count is **1018**; ledger is **3 axioms**
(must stay 3). This run already exhausted the bounded frontier (masked whole-file-proof blockers + the
string-faithful-lowering capability: +4 conversions + 4 byte-inert emitter fixes). Every residual now routes to
ONE wall.

## 2. The wall — first seen
A Python `Dict[str, Any]` (or an IR node read as one) whose values have **DIFFERENT WhyML types in one body**.
Concrete, freshly measured (`stmt_control_flow.py::_render_match_pattern`, mirror line 557):
```python
new_pat = {"pattern": "Constructor", "ctor": arm_ctor, "captures": [ {...}, ... ]}
#          ^string literal          ^string VARIABLE   ^list-of-dict
```
PyCSL models this dict as a homogeneous `map int (option int)`. The string literal `"Constructor"` int-erases to
a hash (`2193169`); the string variable `arm_ctor` and the list `captures` **cannot** be int-coerced → the
emitted WhyML fails L3-tc (`type string/array, but expected int`). The identical wall in the giants front
(`_emit_ir_args_recv_ir`: `arg_ir.get("type")`→string vs `.get("values")`→array vs `[0]`→node) and the
Dict-of-Dict collectors (`_collect_typevar_registry`: `{"bound": bound, ...}` nested maps int-erasing).

## 3. The deeper truth — a modeling choice, NOT a fundamental limit
The homogeneous `map int (option int)` is a REPRESENTATION choice. Python's `Dict[str, Any]` value is a
heterogeneous tagged value. The faithful model is a **value variant** `pyval` + a **`map string pyval`** dict:
```
type pyval = PStr string | PInt int | PBool bool | PArr (seq pyval) | PMap (map string (option pyval))
           | PNode emit_ir   (* an IR sub-node — reuses the certified emit_ir ADT *)
```
Then `{"pattern": "Constructor", "ctor": arm_ctor, "captures": [...]}` builds a `map string pyval` with
`PStr "Constructor"`, `PStr arm_ctor` (faithful — the variable stays a string), `PArr [...]`; a read
`d["ctor"]` projects the `PStr` arm. No int-erasure; the string literal AND the variable AND the list all live
faithfully under one `pyval` type. The node arm reuses the **already-certified** `emit_ir` ADT
(`Phase2c`) so IR sub-node reads unify.

## 4. SOTA lens — the certified value-variant, the natural next ADT
PyCSL has already built + certified FOUR node/value ADTs this campaign: `emit_ir` (expr, Phase2c),
`stmt_ir`/`stmt_list`/`handler_list`/`match_case` (Phase2d), `pyast_stmt` (Phase2e), `pyconst_val` (value
variant, Phase2c). `pyval` is the SAME pattern — a value variant with a size measure — applied to the
heterogeneous-dict value. The precedent is direct: `pyconst_val` already models a tagged constant value
axiom-free. The NEW capability is the `map string pyval` heterogeneous dict + the `PArr (seq pyval)` /
`PMap` recursion, with a `size` measure for any fold's `variant`.

## 5. Honestly-costed routes
- **R1 (recommended): the `pyval` value-variant ADT + `map string pyval` dict + typed field-reader recognizers
  + a co-landing axiom-free `Phase2f_PyVal.v`/`.lean` certificate** (COUPLING RULE §5: a new WhyML value shape
  needs a side-car soundness cert; ledger stays 3, verified by `Print Assumptions`/`#print axioms`). Build
  bottom-up: (a) the `pyval` theory in `preamble.py` (variant + `size`); (b) a dict-literal emitter that builds
  `map string pyval` from `{k: v}` (faithful per-value tag); (c) typed readers (`d[k]` → project the arm);
  (d) the cert. Then convert `_render_match_pattern` (make-or-break target — the simplest heterogeneous dict
  build+read) and cascade to the collectors + giants. Multi-session; yield is the whole heterogeneous-dict
  class (the giants, ~the Dict collectors, stmt_control_flow, the 2 faithfulness bugs).
- **R0 (fallback if R1's spike refutes on a specific arm): a partial `pyval` covering only the arms the
  frontier actually needs** (`PStr | PInt | PArr | PNode`), deferring `PMap` recursion if it forces an axiom
  or a positivity wall.

## 6. Honest limits + certificate
The risk is Why3-structural, not conceptual: (a) does the `pyval` variant with `PArr (seq pyval)` + `PMap (map
string (option pyval))` **recursion** admit a well-founded `size` measure Why3 accepts (the mutual/nested
positivity the `irlist`/`stmt_list` bespoke-cons work already navigated)? (b) does a `map string pyval`
heterogeneous dict **typecheck + prove** a field read non-vacuously at full emit scale (not just a toy)? (c) does
the cert stay **axiom-free** (ledger 3)? Each is a spike question, not an assumption.

## 7. The make-or-break question for review
Is a **faithful `pyval` value variant + a `map string pyval` heterogeneous dict + a typed field read**
achievable as an **axiom-free, byte-diff-0-gated** WhyML shape that TYPECHECKS and PROVES non-vacuously — such
that `{"pattern":"Constructor","ctor":arm_ctor,"captures":[...]}` builds faithfully and `d["ctor"] = PStr
arm_ctor` projects the string variable WITHOUT int-erasure? Or does (a) the `PArr`/`PMap` recursion fail a
well-founded `size`/positivity check, (b) a `map string pyval` read fail to discharge at scale, or (c) the model
force a new axiom? **An oracle run — a hand `.mlw` with a minimal `pyval` (`PStr|PInt|PArr`), a `map string
pyval`, a build `{"pattern":PStr ..., "ctor":PStr <var>}`, and a driver proving `get d "ctor" = PStr <var>`
∧ an evil-twin mismatch fails — proved with `why3 prove -P alt-ergo`/`-P z3`, plus a `Print Assumptions`-style
axiom check — should CONFIRM or REFUTE before any emitter edit.**
