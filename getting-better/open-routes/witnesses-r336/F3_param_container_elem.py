# F3: a PARAMETERISED (non-bare) container annotation drops a float element/value type -> int
from typing import Sequence, Collection, Tuple, MutableSequence, Deque, Mapping, Iterable, List, Dict, Annotated, TypeAlias
from collections import deque
from fractions import Fraction
Vec = List[float]
D: TypeAlias = Dict[str, float]

#@ ensures \result == True
def f_sequence(xs: Sequence[float]) -> bool:
    if len(xs) > 0:
        return xs[0] % 1 == 0
    return True

#@ ensures \result == True
def f_collection(xs: Collection[float]) -> bool:
    if len(xs) > 0:
        return xs[0] % 1 == 0
    return True

#@ ensures \result == True
def f_tuple585(xs: tuple[float, ...]) -> bool:
    if len(xs) > 0:
        return xs[0] % 1 == 0
    return True

#@ ensures \result == True
def f_tuple_var(xs: Tuple[float, ...]) -> bool:
    if len(xs) > 0:
        return xs[0] % 1 == 0
    return True

#@ ensures \result == True
def f_mutseq(xs: MutableSequence[float]) -> bool:
    if len(xs) > 0:
        return xs[0] % 1 == 0
    return True

#@ ensures \result == True
def f_deque(xs: Deque[float]) -> bool:
    if len(xs) > 0:
        return xs[0] % 1 == 0
    return True

#@ ensures \result == True
def f_mapping(d: Mapping[str, float]) -> bool:
    if "a" in d:
        return d["a"] % 1 == 0
    return True

#@ ensures \result == True
def f_iterable(xs: Iterable[float]) -> bool:
    for x in xs:
        if x % 1 != 0:
            return False
    return True

#@ ensures \result == True
def f_list_annotated(xs: List[Annotated[float, "u"]]) -> bool:
    if len(xs) > 0:
        return xs[0] % 1 == 0
    return True

#@ ensures \result == True
def f_dict_fraction(d: Dict[str, Fraction]) -> bool:
    if "a" in d:
        return d["a"] % 1 == 0
    return True

#@ ensures \result == True
def f_list_alias(xs: Vec) -> bool:
    if len(xs) > 0:
        return xs[0] % 1 == 0
    return True

#@ ensures \result == True
def f_dict_alias(d: D) -> bool:
    if "a" in d:
        return d["a"] % 1 == 0
    return True

if __name__ == "__main__":
    import rt23h
    rt23h.check([
        ("f_sequence", f_sequence, ([0.5],), True),
        ("f_collection", f_collection, ([0.5],), True),
        ("f_tuple585", f_tuple585, ((0.5,),), True),
        ("f_tuple_var", f_tuple_var, ((0.5,),), True),
        ("f_mutseq", f_mutseq, ([0.5],), True),
        ("f_deque", f_deque, (deque([0.5]),), True),
        ("f_mapping", f_mapping, ({"a": 0.5},), True),
        ("f_iterable", f_iterable, ([0.5],), True),
        ("f_list_annotated", f_list_annotated, ([0.5],), True),
        ("f_dict_fraction", f_dict_fraction, ({"a": Fraction(1, 2)},), True),
        ("f_list_alias", f_list_alias, ([0.5],), True),
        ("f_dict_alias", f_dict_alias, ({"a": 0.5},), True),
    ])
