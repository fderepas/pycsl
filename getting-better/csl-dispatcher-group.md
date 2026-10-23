# `csl-dispatcher-group` — making the `_csl_*` family concrete in one `let rec … with` group

*A self-contained state-of-the-art report, written for an INDEPENDENT reviewer who has the
repository and the oracles but not this session's reasoning.*

## 1. The global picture

PyCSL is a deductive verifier for annotated Python. A six-module pipeline lowers a Python
file plus `#@` contract comments to WhyML, which Why3 discharges with Alt-Ergo and Z3.

The project also verifies ITSELF. `src/self-annotate/src/` holds a MIRROR of the live
compiler in `src/pycsl/`: for each live method the mirror holds either

* a **`\trusted` stub** — a signature plus a contract, no body. Module 6 emits it as an
  abstract `val`; Why3 ASSUMES the contract. This is the self-hosted TCB.
* or a **converted method** — the live body ported VERBATIM (a fidelity gate,
  `bin/check-self-annotate-sync.sh`, compares the two texts), which Why3 must PROVE.

The campaign's job is to move methods from the first category to the second, and — equally —
to make sure the contracts on both sides are TRUE of the live source. `bin/count-trusted-
directives.py` reports the size of the TCB: **491 markers / 516 grep-substring** at the start
of this session.

Four gate planes must hold on every increment:
1. **fidelity** — `bin/check-self-annotate-sync.sh` ∧ `bin/self-annotate-mirror-check.sh`
   (standing baseline: 2 DIVERGED, 3 mirrors drifted).
2. **whole-file proof** — `PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py <mirror> --import-path
   src/pycsl --provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,'` must report 0 non-Valid.
3. **corpus byte-inertness** — `bin/byte-diff-sweep.sh` over 814 reference programs must be
   byte-identical to a worktree-at-HEAD baseline.
4. **frame honesty** — `bin/check-trusted-frame-honesty.py`, a static check that a declared
   `#@ assigns \nothing` is not false of the live body.

A fifth, non-gating metric: `bin/check-shadowed-selfcalls.py`, which counts CONVERTED methods
whose call sites nevertheless go through an abstract `val self__<m>_<n>` shadow instead of the
real emitted symbol. Baseline **14 methods / 125 sites**.

The proof-axiom ledger must stay at exactly **3**.

## 2. The wall as it stood

`PyCSLToJSONEmitter._csl_to_ir` is the CSL-contract expression dispatcher:

```python
def _csl_to_ir(self, node):
    handler_name = self._CSL_HANDLERS.get(type(node))
    if handler_name is None:
        raise PyCSLIRError(...)
    return getattr(self, handler_name)(node)
```

`_CSL_HANDLERS` is a 79-entry class-level dict mapping CSL AST classes to method NAMES; the
75 `_csl_*` handlers it names are ALREADY converted, and most of them call `self._csl_to_ir`
back. So the family is one large mutual recursion.

Until this session the dispatcher's calls were routed through an abstract shadow
`val self__csl_to_ir_1 (x0: emit_ir) : emit_ir` — **92 of the 125 shadowed call sites in the
whole tree, the single largest item on that metric.** A prior relaunch recorded this as a
CERTIFIED-BOUNDARY with three blockers:

1. **unlisted write effect** — a member reaches `_csl_in`, which writes
   `self._fresh_var_counter`, while every member declared `#@ assigns \nothing`.
2. **unlisted exception** — `_callee_raised_direct` looks callees up by their `self.<m>`
   spelling while the raises registry is keyed by the qualified `<class>__<m>`, so a callee's
   `#@ raises` is invisible to its sibling callers. A fix was measured byte-inert and then
   REVERTED because `_callee_raised_direct`'s own mirror is a facade.
3. **Why3 requires an effect summary to be EXACT** and rejects over-declaration in BOTH
   directions (`this write effect does not happen in the expression`, `this expression does
   not raise exception X`). The record concluded this cannot be made exact "by construction",
   because the IR-level analysis and the emitted body disagree: `_csl_mktuple`'s
   `[self._csl_to_ir(e) for e in node.elts]` lowers to `(IrMkTupleN (list_content_comp_3 …))`
   over a PURE, EFFECT-FREE oracle, and the per-element call is GONE.

## 3. What was actually done, and the deeper truth

The record's blocker (3) is a claim about the WHOLE family. It is true of exactly TWO
members, and the way to find that out is to stop reasoning about it and let Why3 say so.

`scratchpad/w3/fix_assigns.py` drives the emitter in a loop and reacts to its error messages,
editing only `#@` directives on the mirror:

* `this expression produces an unlisted write effect` → set `#@ assigns self._fresh_var_counter`
* `this write effect does not happen in the expression` → set `#@ assigns \nothing`
* `this expression raises unlisted exception E` → add `#@ raises E when True`
* `this expression does not raise exception E` → drop it
* `this expression does not diverge` → drop `#@ \diverges`

It converged in **57 iterations to `L3-tc ✓`**, having also added `#@ sibling_concrete` to all
75 members (which is what makes them one `let rec … with` group instead of separate `let`s).

The resulting split is exact and is the report's central claim:

* **56 of 75** members carry the HONEST `#@ assigns self._fresh_var_counter`.
* **19** carry `#@ assigns \nothing`, and of those **17 are genuine LEAVES** — an AST walk
  shows they make NO self-call at all, so `\nothing` is true of the source too.
* **Exactly 2** are the erasure the record generalised over the whole family:
  `_csl_mktuple` and `_csl_call_expr`, the only two whose bodies contain
  `[self._csl_to_ir(e) for e in …]`.

So blocker (1) is cleared by declaring the truth; blocker (2) is cleared by declaring
`#@ raises PyCSLIRError/PyCSLSemanticError when True` on the 53 members that can propagate
one (this does NOT need the reverted registry fix — an explicit contract is a second, working
route); and blocker (3) shrinks from "the family" to two named methods.

Termination: the group cannot carry a derivable measure, so 74 members carry `#@ \diverges`
(which ASSERTS NOTHING and therefore cannot be the source of a false claim). The dispatcher
itself is BESPOKE-emitted by `module6_whyml/functions.py::_emit_pyx_dispatcher_bespoke`, a
SECOND PRODUCER that synthesises the contract block itself; the mirror had never carried
`#@ \diverges` on it, so the first proof run returned **1481/1595 Valid with all 114 failures
being `Sub-goal termination of pycsltojsonemitter___csl_to_ir'vc`**. Adding the directive puts
`diverges` on the dispatcher's `with` clause.

## 4. Measured effects

* `bin/check-shadowed-selfcalls.py --emit-dir <emitted>`: **14 methods / 125 sites →
  13 / 33.** The 92 `_csl_to_ir` sites are gone.
* Emission diff over all 52 mirrors: exactly **4** change (`Module5_IREmitter`,
  `frontend/__init__`, `frontend/ir_resolve`, `pycsl.py`); all 52 still `L3-tc ✓`.
* The mirror diff contains **0 non-directive lines** — only `#@` comments changed, so the
  fidelity gate is preserved by construction.
* `\trusted` count is UNCHANGED (491): every one of these 75 methods was already converted.
  This increment buys FAITHFULNESS and FRAME HONESTY, not a count reduction.
* No new axiom; ledger stays 3.

## 5. Honest limits

* `#@ raises E when True` gives an exceptional postcondition of `true`, i.e. it constrains
  nothing. It is the weakest honest declaration, not a proof that the exception is rare.
* `#@ \diverges` buys PARTIAL correctness only. The group is not proved terminating.
* The two erased members remain erased: their `#@ assigns \nothing` is exact for the EMITTED
  body and false for the SOURCE. The named capability that would fix them is a faithful
  comprehension lowering for `[self.<m>(e) for e in xs]` that performs the call in sequence
  and threads emitter state. A hand `.mlw` spike for that shape proves
  (`scratchpad/w3/spike_cc.mlw`, Alt-Ergo Valid), including its `writes` propagation and the
  negative control (`scratchpad/w3/spike_cc_neg2.mlw`, explicit `writes {  }` correctly
  REJECTED with `this expression produces an unlisted write effect`).
* Whole-file proof cost is materially higher: the first run produced no prover result for
  ~50 minutes before flushing 1595 goals, against 1199 for the same file unchanged.
