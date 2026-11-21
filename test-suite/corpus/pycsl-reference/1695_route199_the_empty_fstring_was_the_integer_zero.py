r"""Test 1695 - ROUTE #199 carrier (gen #30): `f""` - an f-string with no segments - lowered to the LITERAL `0` (`expressions.py::_handle_fstring_expr`, `if not parts: return "0"`), while the very next arm lowers an all-string f-string to a faithful Why3 string. So `s = f""` then `s == ""` compared `0` against the empty string's hash `313406155` and DECIDED FALSE: this contract PROVED while CPython answers 1 (`f"" == ""` is True). The TRUE twin is test 1696, which was REFUSED before the repair and PROVES after it. `f""` now lowers to `stable_hash('""')`, the same constant the comparison emits - the empty string, written in the representation the empty case actually lives in. This file must FAIL.
"""
# pycsl-expected: FAIL

_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    s = f""
    if s == "":
        return 1
    return 2
