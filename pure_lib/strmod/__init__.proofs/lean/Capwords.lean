/- Lean 4 mirror of the Rocq Capwords proof. Core only (no Mathlib).
   Cross-validates Pycsl.Strmod.Capwords.capwords_length_nongrowing and
   capwords_empty: a faithful CPython string.capwords model on List Int. -/
namespace Pycsl
namespace Strmod
namespace Capwords

abbrev String := List Int
def str_length (s : String) : Int := (s.length : Int)

def is_ws (c : Int) : Bool :=
  c == 32 || c == 9 || c == 10 || c == 13 || c == 12 || c == 11

def to_upper (c : Int) : Int := if 97 ≤ c && c ≤ 122 then c - 32 else c
def to_lower (c : Int) : Int := if 65 ≤ c && c ≤ 90 then c + 32 else c

def capitalize (w : String) : String :=
  match w with
  | [] => []
  | c :: rest => to_upper c :: rest.map to_lower

theorem capitalize_length (w : String) : (capitalize w).length = w.length := by
  cases w with
  | nil => rfl
  | cons c rest => simp [capitalize, List.length_map]

def push (w : String) (acc : List String) : List String :=
  match w with | [] => acc | _ => w :: acc

def split_aux (s : String) (cur : String) : List String :=
  match s with
  | [] => push cur []
  | c :: tl => if is_ws c then push cur (split_aux tl []) else split_aux tl (cur ++ [c])

def split_ws (s : String) : List String := split_aux s []

/- single-space-separated join (structural, no overlapping patterns). -/
def join_tail : List String → String
  | [] => []
  | t :: rest => (32 :: t) ++ join_tail rest
def join_sp : List String → String
  | [] => []
  | t :: rest => t ++ join_tail rest

def capwords_def (s : String) : String :=
  join_sp ((split_ws s).map capitalize)

/- empty law -/
theorem capwords_empty : capwords_def [] = [] := rfl

/- length non-growing -/
-- join_tail length depends only on per-token lengths (+1 each)
theorem join_tail_length (ts : List String) :
    (join_tail ts).length = (ts.map (·.length)).foldr (fun n acc => 1 + n + acc) 0 := by
  induction ts with
  | nil => rfl
  | cons t rest IH =>
    show ((32 :: t) ++ join_tail rest).length
          = ((t.length :: rest.map (·.length)).foldr (fun n acc => 1 + n + acc) 0)
    simp only [List.length_append, List.length_cons, List.foldr_cons]
    rw [IH]; omega

theorem join_sp_length (ts : List String) :
    (join_sp ts).length =
      (ts.map (·.length)).foldr (fun n acc => 1 + n + acc) 0
        - (if ts.isEmpty then 0 else 1) := by
  cases ts with
  | nil => rfl
  | cons t rest =>
    show (t ++ join_tail rest).length
          = ((t.length :: rest.map (·.length)).foldr (fun n acc => 1 + n + acc) 0) - 1
    simp only [List.length_append, List.foldr_cons]
    rw [join_tail_length]; omega

-- capitalize preserves the per-token length list
theorem map_length_capitalize (ts : List String) :
    (ts.map capitalize).map (·.length) = ts.map (·.length) := by
  induction ts with
  | nil => rfl
  | cons t rest IH => simp only [List.map_cons, capitalize_length, IH]

theorem join_sp_map_capitalize_length (ts : List String) :
    (join_sp (ts.map capitalize)).length = (join_sp ts).length := by
  rw [join_sp_length, join_sp_length, map_length_capitalize]
  simp [List.isEmpty_map]

-- bound on split_aux
theorem join_sp_push_le (w : String) (ts : List String) :
    (join_sp (push w ts)).length ≤
      w.length + (match ts with | [] => 0 | _ => 1 + (join_sp ts).length) := by
  cases w with
  | nil => simp only [push, join_sp, List.length_nil]; split <;> simp
  | cons a w' =>
    simp only [push]
    cases ts with
    | nil =>
      show (join_sp [a :: w']).length ≤ (a :: w').length + 0
      show ((a :: w') ++ join_tail []).length ≤ (a :: w').length + 0
      simp [join_tail]
    | cons t rest =>
      show (join_sp ((a :: w') :: t :: rest)).length
            ≤ (a :: w').length + (1 + (join_sp (t :: rest)).length)
      show ((a :: w') ++ join_tail (t :: rest)).length
            ≤ (a :: w').length + (1 + (join_sp (t :: rest)).length)
      show ((a :: w') ++ join_tail (t :: rest)).length
            ≤ (a :: w').length + (1 + (t ++ join_tail rest).length)
      simp only [List.length_append]
      show (a :: w').length + ((32 :: t) ++ join_tail rest).length
            ≤ (a :: w').length + (1 + (t.length + (join_tail rest).length))
      simp only [List.length_append, List.length_cons]
      omega

theorem split_aux_bound (s : String) :
    ∀ cur : String, (join_sp (split_aux s cur)).length ≤ cur.length + s.length := by
  induction s with
  | nil =>
    intro cur
    show (join_sp (push cur [])).length ≤ cur.length + 0
    cases cur with
    | nil => simp [push, join_sp]
    | cons a c' => simp only [push]; show ((a::c') ++ join_tail []).length ≤ _; simp [join_tail]
  | cons c tl IH =>
    intro cur
    show (join_sp (if is_ws c then push cur (split_aux tl []) else split_aux tl (cur ++ [c]))).length
          ≤ cur.length + (c :: tl).length
    by_cases h : is_ws c = true
    · rw [if_pos h]
      cases cur with
      | nil =>
        simp only [push]
        have := IH []
        simp only [List.length_nil, List.length_cons, Nat.zero_add] at this ⊢
        omega
      | cons a c' =>
        have hp := join_sp_push_le (a :: c') (split_aux tl [])
        have hi := IH []
        cases hsa : split_aux tl [] with
        | nil =>
          rw [hsa] at hp hi
          simp only [List.length_cons, List.length_nil, Nat.zero_add] at hp hi ⊢
          omega
        | cons x xs =>
          rw [hsa] at hp hi
          simp only [List.length_cons, List.length_nil, Nat.zero_add] at hp hi ⊢
          omega
    · rw [if_neg h]
      have := IH (cur ++ [c])
      simp only [List.length_append, List.length_cons, List.length_nil] at this ⊢
      omega

theorem capwords_length_nongrowing (s : String) :
    str_length (capwords_def s) ≤ str_length s := by
  unfold str_length capwords_def split_ws
  rw [join_sp_map_capitalize_length]
  have := split_aux_bound s []
  simp only [List.length_nil, Nat.zero_add] at this
  exact_mod_cast this

#print axioms capwords_empty
#print axioms capwords_length_nongrowing

end Capwords
end Strmod
end Pycsl
