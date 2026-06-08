"""Test 0647 — str local concatenation (07-2333-rev2, Gap 2 — enabled by TP-1).

With str locals binding as strings (TP-1), the existing `+`→concat dispatch (`_is_string_expr` →
`str_concat_op`) now fires for str locals, so `a + b` proves `== "hello"`. Gap 2 closes as a
consequence of TP-1 (the `+` machinery only needed the operands to be string-typed).
"""
# pycsl-flags: --memory-model hoare


#@ ensures \result == "hello"
#@ assigns \nothing
def test() -> str:
    a: str = "he"
    b: str = "llo"
    return a + b
