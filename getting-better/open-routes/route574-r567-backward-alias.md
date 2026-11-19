# OPEN ROUTE #574 — ROUTE #567's NON-IR NARROWING FOLLOWS ALIASES IN ONE DIRECTION ONLY: `dv = node; if isinstance(dv, DictView): ... node.kind` IS NOT REFUSED AND `node.kind` IS STILL LOWERED TO kind_of node (the emit_ir tag), THE SAME MISPROJECTION AS #567
**Status: REPAIRED (run #5, executor u32 off b105e8d87 = run5-int48, branch run5-u32; annotations §7.574). Opened as: OPEN, Severity 1 (model-level, like #567: the false claim is a theorem of the model; full proofs are solver-bound). Opened in driver run #5, 2026-11-06, from executor lvG2's report (exemption removal, 012547a1e).** Exemplar witnesses-r574/h567_backward_alias.py (CPython: is_keys_view(DictView("d", "keys")) returns 1 under `ensures \result == 0`); control witnesses-r574/h567_ctl_forward.py (the forward alias, refused by PYCSL-R567). Measured by lvG2 with --no-proof on run5-lvG2 (emission contains kind_of for the backward form; the forward form is refused).

## REPAIR (run #5, executor u32, base run5-int48 b105e8d87, branch run5-u32)
- RULE (`expressions.py::_handle_attribute_expr`, the #567 narrowing table; mirror twin `\trusted`; inline, no new def,
  no new emitter field, no axiom): the table is closed to a fixpoint, flow-insensitively, under every ALIAS EDGE of the
  emitted function's body -- `t = v` / `t: T = v`, a field store `o.f = v` (target path `o.f`), a walrus (also inside
  the `isinstance` argument), a tuple unpacking (pairwise against a tuple display, else every target against the whole
  value), a `for` / comprehension target against its iterable, an item store `xs[i] = v` and a container mutator
  `xs.append(v)` / `extend` / `insert` / `add` / `update` / `setdefault` / `appendleft` / `extendleft` -- in BOTH
  directions (backward: a target that is, or prefixes, a narrowed path narrows the value). A value is split into the
  paths it may evaluate to (both arms of `a if c else b`, both operands of `and` / `or`, a walrus's value and target,
  every element of a display). COARSE edges (a display element, a subscript, an unpacking without a matching display,
  a loop / comprehension target, an item store, a container mutator) narrow the other side with EVERY attribute; an
  `isinstance` whose argument goes through a subscript narrows its coarsened path with every attribute; a field store
  into a narrowed object narrows the stored value (every attribute) when the class may carry that field; a path deeper
  than four fields is cut to its first four, every attribute. When in doubt the edge is coarse (refuse).
- WITNESSES (`--no-proof`, x default / typed / store; all in witnesses-r574/: b01-b15 probes, c01 control): witnesses-r574
  `h567_backward_alias` EMITTED at base -> 3/3 PYCSL-R567-EMITIR-ATTR-ON-NONIR; forward control `h567_ctl_forward`
  3/3 R567 at base and HEAD. Probe family (all EMITTED x 3 at base): backward, 2-chain, siblings (`a = node; b = node`),
  re-binding, annotated assignment, walrus in the test, conditional-expression arm, `or` operand, tuple unpacking,
  `for` over a display, list display + subscript, item store, `.append` -> 13/13 x 3 REFUSED R567 (the `.append` probe:
  hoare R567, typed / store an unrelated PIPELINE ERROR at base and HEAD). Unchanged (EMITTED at base and HEAD): a
  read of an attribute the tested class does not carry (`node.name`, DictView has no `name`); an unrelated alias
  (`dv = other`); a walrus FORWARD read `dv.kind` (`isinstance(dv := node, ..)`: the walrus local is not an emit_ir
  value -- `get_kind !dv` on an int ref, ill-typed, so Why3 typing refuses it; not a projector read).
- CORPUS (ids 9190-9199): 9190 (the exemplar) / 9191 (chain) / 9192 (siblings) / 9193 (re-binding) / 9194 (walrus in
  the test) / 9195 (conditional arm) / 9196 (tuple unpacking) / 9197 (list display + subscript) FAIL: EMITTED at base x
  3 models, REFUSED R567 at HEAD x 3; CPython returns 1 for `DictView("d", "keys")` in every one (`ensures \result ==
  0` false). Controls 9198 (unrelated alias, `node.kind` kept) / 9199 (backward alias tested against `ast.Name`, an IR
  class, `node.id` kept) PASS at base and HEAD (full default-model proofs: Verification SUCCESS x 2 x 2); 9190 at base: Verification FAILED
  (the 110-arm `kind_of` split is solver-bound, as #567's 9025). #567's 9025-9027 / 9030-9035 unchanged: the
  same R567 messages at HEAD, the emitting ones byte-identical.
- BYTE-DIFF vs u32base (b105e8d87): root 3002 -> 3004 .mlw, 0 MOVED / 0 GONE / 0 APPEARED (+2 new sources, 9198 / 9199);
  python-reference 2185 0 / 0 / 0.
- rt43 / rt44 149 controls: verdicts identical (149/149), the 22 emissions byte-identical.
- MIRROR (bin/mirror-emit-sweep.sh vs u32base): 53/53 EMITTED; 52 byte-identical, `frontend/Module5_IREmitter.py`
  MOVED: with the alias-closed rule `_collect_type_params` is refused (`b.value.id`, `b` a `for` target over
  `node.bases`, `node` narrowed by `isinstance(node, ast.ClassDef)`, a non-IR class: an element of a narrowed object's
  field has an unknown class). It is RE-TRUSTED in a SEPARATE commit (`\trusted` 406 -> 407, markers 378 -> 379; the
  driver decides): the only moved lines are that function (`let` -> `val`, same `requires/ensures True`, no caller in
  the emission) and three preamble declarations only it used. Without that commit the Module5 mirror file is GONE.
- Fidelity: check-self-annotate-sync rc 0, self-annotate-mirror-check rc 0, doc-coherency rc 0. PLANES. Ledger 3.
- RESIDUALS (named): a call's result is not an alias edge (`dv = ident(node)`, interprocedural); a method call on a
  computed receiver (`f().append(node)`); `with ... as`; `type(x) is C` / `x.__class__` tests (as #567); the six +
  one mirror re-trusts (driver-backlog "routes #566 / #567 mirror re-trusts").
