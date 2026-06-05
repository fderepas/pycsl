namespace Pycsl.Reference.Json

inductive Json where
  | JNull : Json
  | JInt : Int → Json
  | JPair : Json → Json → Json

def mirror : Json → Json
  | .JNull => .JNull
  | .JInt n => .JInt n
  | .JPair a b => .JPair (mirror b) (mirror a)

theorem mirror_involution (j : Json) : mirror (mirror j) = j := by
  induction j with
  | JNull => rfl
  | JInt n => rfl
  | JPair a b iha ihb => simp [mirror, iha, ihb]

end Pycsl.Reference.Json
