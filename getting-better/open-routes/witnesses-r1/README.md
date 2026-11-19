# Capability R1 (receiver-typed narrowing view) -- spike evidence (driver run #6, executor lvL)

Spike tree = run6-int54 (c914766a6) + `results/r1patch.py` applied to `src/pycsl/module6_whyml/expressions.py`
(`sp`); `spnr` = the same without the residual (`Constant.kind` / `UnaryOp.op` admitted); `spng` = without the
single-binding guard. Front end `--no-proof` x hoare / typed / store; full proofs default model.

- `refuse/` r01-r14: CPython breaks each claim (`VIOLATION contract`); REFUSED PYCSL-R567 at base AND under R1, every
  model (`results/user-probes-*.tsv`; r14 added with the guard). `results/proof.spnr.r01_const_kind.log`: WITHOUT the
  residual the false `ensures \result == 0` is PROVED -- the #567 misprojection (`kind_of` on an `ast.Constant`), which
  R1 refuses.
- `accept/` a01 / a04: REFUSED at base, emitted and PROVED under R1 (hoare); CPython agrees. a02 / a03 / a05: the R567
  refusal is lifted, then a PRE-EXISTING mirror-gated preamble gap (`option`, `unaryop_operand_of`, an int/emit_ir
  clash) fails L3 at base and spike alike.
- The 41 witnesses of routes #566 / #567 / #574 / #579 x 3 models: 123/123 verdicts identical base vs spike
  (`results/witnesses-*.tsv`).
- The six Module5 mirror bodies (verbatim live ports): REFUSED R567 at base, TC-OK under R1, and every emitted
  function block byte-identical to cv11's stand-in tree (the pre-lvG2 forms, proved whole-file before lvG2).
- `pre/p01_attr_value_svalue.py`: a PRE-EXISTING hole found on the way, NOT R1's: `ast.Attribute` (an IR class,
  never narrowed) `.value` lowers to `svalue_of` (the SUBSCRIPT projector, `IrOther ""` on an IrAttr), so
  `x.value.id == "self"` is false in the model; the false `ensures \result == 0` is PROVED at base
  (`results/proof.base.p01.log`), CPython returns 1 for `self.a`.
