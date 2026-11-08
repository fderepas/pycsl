# The `_py_expr_*` wall — is a "structural-only dependency-compile" mode SOUND?

*External-review statement, 2026-07-14, produced by the self-tcb-reduction-driver as a breakability-unknown wall
escalated to the FABLE oracle. Self-contained: assumes no prior PyCSL knowledge. It asks the reviewer to adjudicate
a load-bearing **soundness** question the sub-loop cannot settle by reasoning, and to RUN a Why3 spike that decides
it. Every claim is reproducible from cited evidence.*

---

## 1. Global picture (what PyCSL is, and where this sits)

**PyCSL** is a deductive verifier for a Python subset: it compiles annotated Python through a 6-module pipeline
(Module1 Ingestor → Module2 Parser → Module3 Weaver → Module5 IREmitter → Module6 WhyMLTranspiler) into **WhyML**
(the [Why3](http://why3.org) language), discharged by SMT (Alt-Ergo, Z3). It **verifies a mirror of its own emitter**:
the compiler's WhyML-generation code is itself annotated Python that PyCSL proves. A self-verification campaign converts
the mirror's `\trusted` stubs (assumed contracts) into verified bodies, each held to three disjoint oracles: fidelity
to the live code, Why3 discharge, and corpus byte-diff-0 (real programs emit identically). The standing scope cut: the
fixed contract shape is `#@ requires True / ensures True / assigns <frame>` — type-safety + termination + frame ONLY,
never value-faithful. The 3-axiom Rocq/Lean ledger must stay at 3.

## 2. What just succeeded, and the exact remaining wall

A just-completed build (59 conversions, `\trusted` count 1154→1095, 35/35 self-annotation suite green, corpus
byte-diff = only 15 shared-theory files additive, ledger 3) converted the mirror's **CSL contract-AST → IR emitter**
handlers (`_csl_binop`, ~50 more). The mechanism: the CSL AST classes are `@dataclass`es, so the emitter auto-models
them as WhyML **records** (`type cslbinop = {cslbinop_left: emit_ir; ...}`); retyping a dataclass field annotation
`CSLNode`→`"ExprIR"` makes the child field the `emit_ir` IR-node sum, and the handler `_csl_binop` lowers to the real
constructor `(IrBinOp op (csl_to_ir left) (csl_to_ir right))` — a genuine, non-vacuous, provable body.

**The remaining ~20 handlers** are the *Python*-AST → IR emitter (`_py_expr_binop`, `_py_expr_name`,
`_py_expr_constant`, `_py_expr_unaryop`, `_py_expr_compare`, `_py_expr_attribute`, `_py_expr_subscript`, …). They have
the IDENTICAL construction shape, e.g.:
```python
def _py_expr_binop(self, expr: ast.BinOp) -> Dict[str, Any]:
    return {"type": "BinOp", "op": self._py_op_to_str(expr.op),
            "left": self._py_expr_to_ir(expr.left), "right": self._py_expr_to_ir(expr.right)}
```
But their input `expr: ast.BinOp` is a **pure_ast** node. `pure_ast.py` reimplements Python's `ast` module; its ~90
node classes have **no textual `class BinOp: ...`** — they are synthesized at runtime by a metaclass
(`_NODE_SPEC = {'BinOp': ('expr', ('left','op','right'), None), ...}` + `_build_nodes()` doing `type(name,(base,),body)`).
The emitter's record-population (`_collect_class_fields`, which fires only on a literal `ast.ClassDef` with a
`__init__` / `@dataclass` body) therefore NEVER sees them, so `ast.BinOp` is modeled as **opaque `int`**
(`val _py_expr_binop (expr: int) : int`), not a record — and the handler cannot read `expr.left`/`.right` to construct.

## 3. The candidate fix and the load-bearing SOUNDNESS question

A prototype ("route b") was built and reverted: teach the emitter to **synthesize a record `type_decl` for a node
from the `_NODE_SPEC` dict literal** (modeled on the existing `_synthesize_typeddict_functional` recognizer that turns
a module-level `TypedDict(...)` call into a record), with a small hand-authored per-node field-type table
(`BinOp: left=ExprIR, op=int, right=ExprIR`). This worked in isolation. But to make a CROSS-FILE importer (the Module5
mirror) SEE that `pure_ast.BinOp` is a record, the resolver (`ir_resolve.py::_process_dependency`) must compile
`pure_ast.py` to harvest its `type_decls` — and it runs the **full Module1→Module5 pipeline**, which **crashes in
Module3_Weaver** on pure_ast's deprecated `Num`/`Str`/`Ellipsis` compat shim (a class with a non-trivial `__new__`,
rejected by an undefined-behavior check "UB-7.6"). There is **no "structural-only" mode** that harvests a dependency's
record SHAPES while skipping its VERIFICATION.

**The question for the oracle (LOAD-BEARING, a SOUNDNESS question):** is it SOUND, within a deductive
self-verification, to add a **structural-only dependency-compile mode** that, when file A imports a type/record from
file B *purely to name it in A's own type signatures*, harvests B's `type_decl` SHAPES (field names + WhyML field
types) WITHOUT running B's semantic/UB/verification checks (Module3+) and WITHOUT proving B's own contracts in that
pass? The intuition FOR: a record shape is metadata (a Why3 `type t = {f: τ; ...}` declaration); A's proof discharges
against that DECLARATION, and B's own correctness is established when B is verified as a first-class unit elsewhere
(B is in the 35-file suite and proves standalone) — so importing B's *type shape* without re-verifying B is analogous
to trusting a type signature at a module boundary, which mainstream verifiers (Why3 `clone`/`use`, Dafny/Viper module
imports, F* interfaces) do routinely. The intuition AGAINST / the trap to check: does skipping B's checks let A
"verify" against a record shape that B's own verification would have REJECTED or ALTERED (e.g. a field type that B
only accepts under an invariant, or a UB-rejected class whose record shape is nonetheless emitted), thereby proving A
against a construct that has no sound B-side meaning? Is there a principled line — "shape-only import is sound iff the
harvested `type_decl` is independent of B's verification outcome" — and does the pure_ast case (records derived purely
from the static `_NODE_SPEC` table, no invariant, no proof dependency) sit on the sound side?

## 4. What this review must produce

Write `py-expr-structural-dep-wall-response.md` with a hand `.mlw` spike (proven with `why3 prove`, `^axiom ` = 0) and
a verdict:
- **BREAKABLE** (the structural-only shape-import is SOUND for this case) — with the soundness argument (why proving
  the importer against a shape-only-harvested record does NOT let it establish something false), the exact criterion
  distinguishing sound shape-import from unsound (does it require the record be verification-independent? invariant-free?),
  and a spike modelling a two-unit setup: unit B declares `type binop = {left: emit_ir; op: int; right: emit_ir}`
  (harvested WITHOUT proving B), unit A constructs `(IrBinOp (op_to_str b.op) (to_ir b.left) (to_ir b.right))` against
  it under `ensures True`, and A's type-safety VC discharges soundly. Show a NEGATIVE control: a case where shape-only
  import WOULD be unsound (if one exists), to sharpen the criterion.
- **BOUNDARY** (shape-only import is genuinely unsound / not soundly separable here) — with the spike evidence of what
  breaks.

That verdict — not prose — is the deliverable. It decides whether the ~20 non-list `_py_expr_*` handlers are a
buildable lever (structural-only mode + a mechanical per-node field-type table) or a genuine boundary. (List-bearing
nodes `If`/`Call`/`BoolOp`, whose fields are node LISTS, are OUT of scope here — they hit a separate
list-comprehension-lowering wall.)
