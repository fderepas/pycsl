-- Golden test fixture for lean2pycsl — tuple return values.
--
-- Mirrors src/rocq2pycsl/tests/golden/divmod_pair. Lean's `.fst`/`.snd`
-- method syntax maps to `Proj` (rendered as `\result[0]`/`\result[1]`)
-- — the dot-syntax lowering in lean2pycsl.translator.lean recognizes
-- `t.fst` on a variable whose head is lowercase.

def divmod_pair (a b : Int) : Int × Int := (a / b, a % b)

@[pycsl_spec "divmod_pair"]
theorem divmod_pair_fst : ∀ (a b : Int),
  b ≠ 0 → (divmod_pair a b).fst = a / b := sorry

@[pycsl_spec "divmod_pair"]
theorem divmod_pair_snd : ∀ (a b : Int),
  b ≠ 0 → (divmod_pair a b).snd = a % b := sorry
