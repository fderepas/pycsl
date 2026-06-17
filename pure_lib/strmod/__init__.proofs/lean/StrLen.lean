/- Validation of Pycsl.Strmod.StrLen.length_nonneg — Lean 4 mirror of
   ../rocq/StrLen.v.

   The STRING-UNIVERSAL length-non-negativity fact that pins every
   "result is a string" leaf in pure_lib/strmod (template_substitute /
   template_safe_substitute / _format_field_nonempty / Template.substitute /
   Template.safe_substitute / Formatter.format).

   The Why3 axiom is

       forall s : string. String.length s >= 0

   i.e. EVERY string — whatever transform produced it — has non-negative
   length. True of an ARBITRARY result string, so it is a generic lemma about
   the abstract string type, no transform definition required.

   Faithful interpretation of the Why3 symbols (same model as
   ../../../../test-suite/corpus/pycsl-reference/0708.proofs):
     - Why3 `string`        <-> `List Int` (a char is its code).
     - `String.length s`    <-> `(s.length : Int)` — the int char count, which
                                is `Int.ofNat _`, non-negative by construction.
     - `>=` (Why3 int order) <-> `Int` `≥`.

   Verified under Lean 4.31.0 (core only, no Mathlib). No sorry. -/

namespace Pycsl
namespace Strmod
namespace StrLen

/-- A Why3 `string` is modelled as its list of character codes. -/
abbrev String := List Int

/-- `String.length s` (Why3 int) is the int count of characters. -/
def str_length (s : String) : Int := (s.length : Int)

/-- The universal fact: the length of ANY string is non-negative. True of an
    arbitrary result string regardless of the transform that produced it. -/
theorem length_nonneg (s : String) : str_length s ≥ 0 := by
  unfold str_length
  exact Int.natCast_nonneg s.length

#print axioms length_nonneg

end StrLen
end Strmod
end Pycsl
