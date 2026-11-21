# LADDER 4 PLAN — the `Constant` NUMBER arm (3 markers: atom, _pattern_number, closed_pattern)

CENSUS FIRST (lesson (p)). An existing value model for a Python literal ALREADY EXISTS:
`pyconst_val = PVNone | PVBool bool | PVInt int | PVStr string` (preamble.py:5896) with
`is_pv*` / `pv*_of` recognizers. It is the READER side (Module5's `_py_expr_constant`
reads a Constant node's value). It CANNOT be reused as-is for the CONSTRUCTION side:
`_parse_number` can return a FLOAT or a COMPLEX, and `pyconst_val` has no arm for either,
so an uninterpreted `val _parse_number (s:string) : pyconst_val` would CLAIM the result is
one of the four arms — false for a float. That is exactly the "mis-model a number" trap
`irconst` was built to avoid.

## The extension
`irconst = ICStr string | ICNone | ICNum irnum | ICBool bool | ICEllipsis`
with a fresh ABSTRACT `type irnum` declared before the emit_ir group, and the ALREADY
PRESENT `val _parse_number` retyped from `(s: int) : unit` to `(s: string) : irnum` by a
mirror-only RETURN INTERFACE (`def _parse_number(s: str) -> "PyNum"`).

An uninterpreted function is the SOUND abstraction here: it never asserts two literals are
equal and never asserts they differ. `0x3E8` and `1000` stay merely unrelated, which is a
weakness of the model, not a claim.

TCB accounting: no axiom, no ledger move; ONE new abstract TYPE, and `_parse_number`'s
abstract `val` already exists (it is retyped, not added). Three `val _parser__*` lines come
out. Net val set strictly negative.

## Per-site needs
- `_pattern_number` — CHEAPEST, take FIRST. Needs ICNum + the `UnaryOp` arm (exists) +
  `_N("USub")()` class-name-string rule (exists) + `sign` as a plain string local with the
  I-B `""` sentinel (FAITHFUL here: `sign` is only ever "-", "+" or None, so "" is
  distinguishable — do NOT reach for an `iropt_str` carrier).
- `atom` — needs ICNum, ICBool (True/False), ICEllipsis (`value=...`), plus RETURN
  INTERFACES on `strings`/`yield_expr`/`atom_paren`/`atom_list`/`atom_brace` (check which
  already have them) and the `Name` arm (exists). Joins the expression `let rec` group ->
  expect a group re-phasing (lesson (bh)/(bk) §3): price the variant SHAPE on the
  1-second emit oracle before any prover runs.
- `closed_pattern` — the largest: MatchValue / MatchSingleton (whose value comes from a
  STRING-KEYED DICT LITERAL indexed by `s` — check whether the const-dict lowering covers
  a literal dict, not just a module-level one) / MatchClass / MatchAs / `_sequence_pattern`.
  Take LAST; refute with a named capability if the dict-literal index is not covered.
