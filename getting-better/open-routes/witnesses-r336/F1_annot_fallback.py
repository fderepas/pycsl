# F1: an annotation PyCSL does not recognise lowers to `int` (functions.py _symtype_to_whyml "Defaults to int")
from typing import Literal, Sequence, TypeAlias, Annotated, Optional, SupportsFloat, TypeAliasType
from fractions import Fraction
from decimal import Decimal
from numbers import Real

Num: TypeAlias = float
Num2 = float
type Num3 = float
Num4 = TypeAliasType("Num4", float)
S: TypeAlias = str
N: TypeAlias = None
B: TypeAlias = bytes

#@ ensures \result == True
def f_alias(x: Num) -> bool:
    return x % 1 == 0

#@ ensures \result == True
def f_plain_alias(x: Num2) -> bool:
    return x % 1 == 0

#@ ensures \result == True
def f_type_stmt(x: Num3) -> bool:
    return x % 1 == 0

#@ ensures \result == True
def f_aliastype(x: Num4) -> bool:
    return x % 1 == 0

#@ ensures \result == True
def f_annotated(x: Annotated[float, "m"]) -> bool:
    return x % 1 == 0

#@ ensures \result == True
def f_fraction(x: Fraction) -> bool:
    return x % 1 == 0

#@ ensures \result == True
def f_decimal(x: Decimal) -> bool:
    return x % 1 == 0

#@ ensures \result == True
def f_real(x: Real) -> bool:
    return x % 1 == 0

#@ ensures \result == True
def f_supportsfloat(x: SupportsFloat) -> bool:
    return x % 1 == 0

#@ ensures \result == True
def f_opt_alias(x: Optional[Num]) -> bool:
    if x is None:
        return True
    return x % 1 == 0

#@ no_exception \all
#@ ensures \result == 0
def f_alias_str(x: S) -> int:
    return x - x

#@ no_exception \all
#@ ensures \result == 0
def f_annotated_str(x: Annotated[str, "t"]) -> int:
    return x - x

#@ no_exception \all
#@ ensures \result == 1
def f_alias_none(x: N) -> int:
    return x * 0 + 1

#@ no_exception \all
#@ ensures \result == 1
def f_alias_bytes(x: B) -> int:
    return x * 0 + 1

#@ no_exception \all
#@ ensures \result == 0
def f_type_param(t: type) -> int:
    return t - t

#@ no_exception \all
#@ ensures \result == 1
def f_literal_none(x: Literal[None]) -> int:
    return x * 0 + 1

if __name__ == "__main__":
    import rt23h
    rt23h.check([
        ("f_alias", f_alias, (0.5,), True),
        ("f_plain_alias", f_plain_alias, (0.5,), True),
        ("f_type_stmt", f_type_stmt, (0.5,), True),
        ("f_aliastype", f_aliastype, (0.5,), True),
        ("f_annotated", f_annotated, (0.5,), True),
        ("f_fraction", f_fraction, (Fraction(1, 2),), True),
        ("f_decimal", f_decimal, (Decimal("0.5"),), True),
        ("f_real", f_real, (0.5,), True),
        ("f_supportsfloat", f_supportsfloat, (0.5,), True),
        ("f_opt_alias", f_opt_alias, (0.5,), True),
        ("f_alias_str", f_alias_str, ("a",), 0),
        ("f_annotated_str", f_annotated_str, ("a",), 0),
        ("f_alias_none", f_alias_none, (None,), 1),
        ("f_alias_bytes", f_alias_bytes, (b"a",), 1),
        ("f_type_param", f_type_param, (float,), 0),
        ("f_literal_none", f_literal_none, (None,), 1),
    ])
