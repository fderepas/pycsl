-- Golden test fixture for lean2pycsl — dicts as `Nat → Option Nat`.
--
-- Mirrors src/rocq2pycsl/tests/golden/dict_insert_lookup. The arrow
-- type `Nat → Option Nat` passes through the (now-loosened) Lean
-- type-class quantification gate.

def dict_insert_lookup (d : Nat → Option Nat) (k v : Nat) : Nat := v

@[pycsl_spec "dict_insert_lookup"]
theorem dict_insert_lookup_correct :
  ∀ (d : Nat → Option Nat) (k v : Nat),
    dict_insert_lookup d k v = v := sorry
