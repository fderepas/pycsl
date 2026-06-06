-- Golden test fixture for lean2pycsl — ghost_list operations.
--
-- Mirrors src/rocq2pycsl/tests/golden/list_length_after_append. The
-- `length (List.append l1 l2)` form exercises the cross-prover
-- recognition of `List.append` → `ListAppend` and `List.length` →
-- `Length`.

def list_length_after_append (n : Nat) : Nat := n

@[pycsl_spec "list_length_after_append"]
theorem list_length_after_append_eq :
  ∀ (n : Nat) (l1 l2 : List Nat),
    n + List.length l1 + List.length l2 =
      list_length_after_append n + List.length (List.append l1 l2) := sorry
