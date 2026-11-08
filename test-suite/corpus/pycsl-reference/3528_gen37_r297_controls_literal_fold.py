r"""Test 3528 -- gen #37 route #297 (expected PASS): CONTROLS: an all-literal dict/tuple/set literal (local
and inline) keeps its fold, counted DISTINCT under Python equality; a list/tuple with a plain
non-literal element keeps its size and its literal positions.
"""
# pycsl-expected: PASS
from typing import List, Dict, Set, Tuple, Optional


#@ ensures \result == 1
#@ assigns \nothing
def dict_lit_read() -> int:
    d: Dict[int, int] = {0: 1, 1: 2}
    return d[0]


#@ ensures \result == 2
#@ assigns \nothing
def dict_lit_len() -> int:
    d: Dict[int, int] = {0: 1, 1: 2}
    return len(d)


#@ ensures \result == 2
#@ assigns \nothing
def tuple_lit_read() -> int:
    t = (1, 2)
    return t[1]


#@ ensures \result == 2
#@ assigns \nothing
def tuple_lit_len() -> int:
    t = (1, 2)
    return len(t)


#@ ensures \result == 2
#@ assigns \nothing
def set_lit_len() -> int:
    s = {1, 2, 2}
    return len(s)


#@ ensures \result == 2
#@ assigns \nothing
def set_str_len() -> int:
    s = {"a", "b", "a"}
    return len(s)


#@ ensures \result == 3
#@ assigns \nothing
def inline_tuple_len() -> int:
    return len((1, 2, 3))


#@ ensures \result == 2
#@ assigns \nothing
def inline_set_len() -> int:
    return len({1, 2, 1})


#@ ensures \result == 1
#@ assigns \nothing
def inline_dict_len() -> int:
    return len({1: 2, True: 3})


#@ ensures \result == 5
#@ assigns \nothing
def list_nonlit_elem_read(a: int) -> int:
    xs: List[int] = [a, 5]
    return xs[1]


#@ ensures \result == 2
#@ assigns \nothing
def list_nonlit_elem_len(a: int) -> int:
    xs: List[int] = [a, 5]
    return len(xs)


#@ ensures \result == 2
#@ assigns \nothing
def tuple_nonlit_elem_len(a: int) -> int:
    t = (a, 5)
    return len(t)

if __name__ == "__main__":
    assert dict_lit_read() == 1 and dict_lit_len() == 2
    assert tuple_lit_read() == 2 and tuple_lit_len() == 2
    assert set_lit_len() == 2 and set_str_len() == 2
    assert inline_tuple_len() == 3 and inline_set_len() == 2 and inline_dict_len() == 1
    assert list_nonlit_elem_read(9) == 5 and list_nonlit_elem_len(9) == 2
    assert tuple_nonlit_elem_len(9) == 2
