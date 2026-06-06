-- Golden test fixture for lean2pycsl — strings.
--
-- Mirrors src/rocq2pycsl/tests/golden/concat_length. Lean's
-- `String.length` and `s.length` both lower to `StrLength`, and
-- `String.append` lowers to `StrConcat`.

def concat_length (s t : String) : Nat := s.length + t.length

@[pycsl_spec "concat_length"]
theorem concat_length_correct : ∀ (s t : String),
  concat_length s t = String.length s + String.length t := sorry
