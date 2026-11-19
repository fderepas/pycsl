# Wall: faithful in-place `list.append` through a parameter (blocks the 22-marker C bucket)

**Status:** state-of-the-art wall statement (U). Awaiting an INDEPENDENT fable review with an oracle artifact.
**Base loop:** self-tcb-reduction of the PyCSL self-annotation mirror (`src/self-annotate/src/`).
**Author:** driver (may be tainted — the fable reviewer must independently confirm/refute from the repo + oracle, NOT from this prose).

## 1. The stubs this wall blocks (the demand)

22 `#@ \trusted` statement-emitter handlers in the M5 mirror
(`src/self-annotate/src/frontend/Module5_IREmitter.py`, live source in `src/pycsl/frontend/Module5_IREmitter.py`):

`_py_stmts_to_ir` (central dispatch), `_emit_ghost_assign`, `_process_for`, `_process_if`,
`_process_while`, and `_py_stmt_{assign,augassign,return,while,for,if,continue,assert,raise,annassign,expr,try,with,pass,break,delete,match}`.

Every one has the same structural shape: it takes a Python list parameter (call it `ir_stmts:
List[Dict[str,Any]]`) and **mutates it in place** via `ir_stmts.append({"stmt": K, ...})`, returning
`None`. The dispatcher `_py_stmts_to_ir` calls these handlers and then **reads `ir_stmts` back** to
assemble the function body. So the observable behavior is: *callee appends to a list the caller holds
a reference to; caller reads the appended elements afterward.*

## 2. The claim to adjudicate (CONFIRM or REFUTE with an oracle artifact)

**CLAIM A (model):** PyCSL currently lowers a Python `list` parameter to an immutable `seq`
snapshot, and `list.append(v)` to `s := Seq.snoc s v` on a **local `ref`** that is a *copy* of the
parameter — so a mutation performed by a callee on a passed list is **NOT visible to the caller**.
Candidate code to inspect: the seq-promotion path in `src/pycsl/module6_whyml/statements.py`
(the `snapshot`/`Seq.snoc`/`ref` machinery — grep `snapshot`, `Seq.snoc`, `seq-promotion`,
`_coerce_to_int`), and how a List parameter's frame (`#@ assigns <list>`) lowers to a Why3 `writes`
clause.

**CLAIM B (false green):** because of CLAIM A, porting these handlers verbatim yields a Why3 proof
that reports SUCCESS but is UNSOUND / vacuous: (i) the appended node's content is not observable to
the caller; (ii) distinct handlers (`_py_stmt_pass`, `_py_stmt_break`, `_py_stmt_continue`) may emit
**byte-identical** WhyML because the node tag is erased; (iii) the declared `#@ assigns ir_stmts`
frame lowers to an empty `writes { }` (a mutation the model does not actually perform on a
caller-visible region). Any of (i)-(iii) is a Gate-C reject.

**CLAIM C (what a faithful conversion requires):** a sound model of *in-place append through a
parameter* — a caller-visible mutable region for `ir_stmts` (e.g. a `ref (seq stmt_ir)` parameter
with a real `writes { ir_stmts }`, or an aliased array with caller-visible cell + length writes),
such that after `handler(...); read ir_stmts`, the caller observes the appended element. Plus a
statement-IR ADT (`stmt_ir`, sibling of the certified `emit_ir` ADT; `stmt_ir` references `emit_ir`
for expr children, no mutual recursion) so the node tag is preserved rather than erased to `0`.

## 3. The question for fable (Gate R)

1. **CONFIRM or REFUTE CLAIM A + CLAIM B** with an INDEPENDENT oracle artifact — e.g. write a tiny
   hand `.mlw` (a proc that appends to a passed list-param + a caller that reads it back) and run
   `why3 prove`, OR emit a 2-line PyCSL program that mutates a passed list and `grep` the generated
   WhyML (`pycsl <f> --keep-mlw`) to show whether the append writes the caller's region or a local
   copy. State exactly what the model does.
2. **Is this a genuine CERTIFIED-BOUNDARY or a BREAKABLE wall?** i.e. does a SOUND extension exist
   (CLAIM C) that PyCSL can adopt without (a) an added axiom, (b) breaking the corpus byte-diff on
   the existing "build-and-return a list" programs (which the current materialize-on-return model
   serves correctly), and (c) breaking the frame-fidelity of every other List-param method? If a
   sound in-place-append model coexists with the existing return-a-list model, the wall is BREAKABLE
   and worth a build; if the two models are fundamentally in tension (e.g. every List param would
   have to become mutable, perturbing the corpus), it is a boundary to record.
3. If BREAKABLE: sketch the make-or-break SPIKE (one handler, e.g. `_py_stmt_pass` or
   `_py_stmt_return`, proven with a *non-vacuous* `writes { ir_stmts }` frame + a real `stmt_ir`
   ctor, plus a driver that observes the appended node) that the next run must pass before the
   22-marker family build is authorized.

## 4. Constraints the fix must honor (base-loop L)

- Fixed contract shape `#@ requires True / ensures True / assigns <frame>` (type-safety + frame only).
- 3-axiom ledger unchanged (`proof_axiom_allowlist.py`); any new value shape (`stmt_ir`) co-lands an
  AXIOM-FREE `src/formal-semantics/` certificate (Rocq `Print Assumptions` closed + Lean only stdlib
  kernel axioms) — the `Phase2c_PyConstVal.v` / `PyConstVal.lean` precedent from commit `2b2927bc`.
- Corpus byte-diff 0 on the reference corpus; full self-annotation suite 35/35; mirror-check 52/52.
- Non-vacuity: distinct handlers must emit distinct WhyML; the frame must be a real `writes`, not `{ }`.

## 5. Current base-loop state (context, not authority)

HEAD `2b2927bc`; trusted count 1075; suite 35/35; ledger 3. The value-variant capability
(`pyconst_val` ADT + certificate) landed this run (feeds the `stmt_ir` expr-child modeling). The
cheap-conversion frontier is measured-exhausted (a 99-stub census: buckets A≈0 / B=3 / C=22 / D=1 /
E=45 leave-trusted / F=27); C is the largest remaining lever and is gated entirely on this wall.
