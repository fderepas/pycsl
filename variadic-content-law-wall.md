# The variadic-comprehension wall — is a content-law abstract op FAITHFUL or a FACADE?

*External-review statement, 2026-07-15, self-tcb-reduction-driver, escalated to the FABLE oracle. Self-contained.
Asks the reviewer to adjudicate, WITH A WHY3 SPIKE, one load-bearing non-vacuity question the sub-loop cannot settle
(it has mistaken facades for faithful lowerings THREE times this campaign, so it distrusts its own judgment here).*

## 1. Global picture
**PyCSL** compiles annotated Python → **WhyML** (Why3), discharged by SMT. It **self-verifies a MIRROR of its own
emitter**: the emitter's WhyML-generation code is annotated Python that PyCSL proves. A campaign converts the mirror's
`\trusted` stubs to verified bodies under a FIXED contract shape `#@ requires True / ensures True / assigns <frame>`
— **type-safety + termination + frame ONLY, never value-faithful**. A converted body must (a) `--fun`/whole-file
**discharge** under that contract, (b) be **byte-diff-0** on the 767-program reference corpus (real programs emit
identically), and (c) be **NON-VACUOUS**: "reads real accessors, no opaque projection" — a body that reads its node
and builds a real value, NOT a stub. The anti-facade rule is the crux: introducing a NEW opaque trusted `val`
primitive to make a body "prove" is a FACADE and is forbidden (reverted 3× this campaign).

## 2. The setting — the expr construction family (already converted, non-facade)
The emitter lowers a Python/CSL AST node to a JSON-IR dict `{"type": K, ...}`; the mirror models these as an `emit_ir`
WhyML variant (`IrBinOp string emit_ir emit_ir | IrVar string | ...`). A handler like `_csl_binop(node) ->
{"type":"BinOp","op":node.op,"left":self._csl_to_ir(node.left),"right":self._csl_to_ir(node.right)}` lowers to the REAL
constructor `(IrBinOp node.op (csl_to_ir node.left) (csl_to_ir node.right))` — reads node's fields, calls the trusted
recursion hub `csl_to_ir` (a `val ... : emit_ir`, the sanctioned recursion primitive, like a dispatcher). 60+ handlers
converted this way, non-vacuously. That is the accepted baseline.

## 3. The wall — the VARIADIC handlers
The remaining handlers build a node with a LIST child via a MAP comprehension:
```python
def _csl_mktuple(self, node): return {"type":"MkTuple","elts":[self._csl_to_ir(e) for e in node.elts]}
```
`node.elts` is `array emit_ir` (a list of child IR nodes); the body maps the trusted dispatcher `csl_to_ir` over it to
produce a `list emit_ir`, carried by a variadic ctor `IrMkTupleN (list emit_ir)`. TWO prior attempts to lower this were
REVERTED as facades because they modeled the whole comprehension as an opaque `val list_comp (src): array emit_ir`
with ONLY a length law (`ensures { Array.length result = Array.length src }`) — the map computation was unpinned.

## 4. The candidate — reuse the EXISTING projection-comprehension machinery (with a CONTENT LAW)
PyCSL ALREADY lowers list comprehensions in CORPUS user code. For a projection comprehension `[p.x for p in a]` it
emits an abstract op with a **per-index CONTENT LAW** (this is the accepted, corpus-proven lowering — reference
programs 0769/0770 prove with it):
```
val list_content_comp_N (src: array <rec>) : array int
  ensures { Array.length result = Array.length src }
  ensures { forall i. 0 <= i < Array.length src -> result[i] = (let c = src[i] in get_x c) }
```
where `get_x` is an ABSTRACT `val function` representing the `.x` projection (not tied to any concrete field-read
implementation; it is uninterpreted, and a consumer's own `a[k].x` lowers to the SAME `get_x` so they denote one value).

A spike extended this SAME machinery to the variadic map: for `[csl_to_ir(e) for e in node.elts]` it emits
```
val function emit_ir_disp__csl_to_ir (e: emit_ir) : emit_ir            (* abstract, fresh *)
val list_content_comp_0 (src: array emit_ir) : list emit_ir
  ensures { Length.length result = Array.length src }
  ensures { forall i. 0 <= i < Array.length src -> nth i result = (let c = src[i] in emit_ir_disp__csl_to_ir c) }
```
and the handler body is `(IrMkTupleN (list_content_comp_0 node.elts))`. Under the `ensures True` contract the handler
just needs to TYPE-CHECK (it does); the content law is EXTRA. **The one deliberate design choice:** `emit_ir_disp__csl_to_ir`
is a FRESH abstract `val function`, NOT identified with the program-side dispatcher symbol `csl_to_ir`
(`self__csl_to_ir_1`) that `_csl_binop` etc. actually call. So the content law says "each output element is SOME
deterministic function of the corresponding input" — pinning the STRUCTURE (per-index, length-preserving, function-of-
input) but leaving that function uninterpreted, exactly as `get_x` is uninterpreted for the projection case.

## 5. The load-bearing question for the oracle (RUN a spike, don't just reason)
Under this campaign's TYPE-SAFETY-ONLY (`ensures True`) contract + its NON-VACUITY rule ("reads real accessors, no
opaque projection; no new opaque trusted `val` to force a proof"):

**Is `list_content_comp_0` (an abstract `val` with the per-index CONTENT law over a FRESH abstract `emit_ir_disp`) a
SANCTIONED comprehension lowering — the same fidelity level as the accepted projection `list_content_comp_N`/`get_x`
— or is it a FACADE that the non-vacuity rule must REJECT?** Specifically:
(a) Does the fact that `emit_ir_disp__csl_to_ir` is a FRESH uninterpreted symbol (NOT the program's `csl_to_ir`) make
    the content law VACUOUS (trivially satisfiable — the abstract op could return anything, and `emit_ir_disp` is just
    named for it), degrading it to the length-only facade in disguise? OR does the per-index `nth i result = disp(src[i])`
    STRUCTURE (a length-preserving, element-wise, deterministic-function-of-input law) carry real content that a
    length-only law does not — matching the `get_x` precedent, which is ALSO a fresh uninterpreted symbol?
(b) Is there a principled line: "a comprehension abstract op is non-vacuous iff its content law is per-index +
    length-preserving + the per-element function is a genuine (even if abstract) function of the source element" — and
    does the projection precedent (`get_x`) sit on the same side as the variadic (`emit_ir_disp`)? Or does the
    projection case have an extra property (a REAL consumer that shares `get_x`, giving it observational content) that
    the mirror's `_csl_mktuple` lacks (no consumer shares `emit_ir_disp`), pushing the variadic to the FACADE side?
(c) RUN a Why3 spike: model both a length-only op and a per-index-content-law op over an abstract per-element function,
    under `ensures True`, and judge whether the content-law version establishes anything the length-only one does not —
    e.g. does a hostile "returns a constant list" implementation satisfy the content law? (If a constant-returning op
    can satisfy `nth i result = disp(src[i])` for a FRESH `disp`, the law is vacuous → FACADE.)

## 6. Deliverable
Write `variadic-content-law-wall-response.md`: the `.mlw` spike (proven, `^axiom `=0), the negative control from 5(c),
the derived criterion, and a VERDICT — **SANCTIONED** (the content-law abstract op is non-vacuous, same level as the
accepted projection comprehension — variadic is buildable) or **FACADE** (it is vacuous / the fresh-`disp` law adds
nothing over length-only — REJECT, the variadic stays trusted). Be adversarial: TRY to show it vacuous before endorsing.
That verdict decides whether ~13 variadic handlers (`_csl_mktuple`/`call_expr` + `_py_expr_tuple`/`list`/`set`/`call`/…)
are a buildable lever or a boundary.
