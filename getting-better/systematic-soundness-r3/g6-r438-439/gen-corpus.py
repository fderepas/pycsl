import os, textwrap
C = "/home/fabrice/git/pycsl-g6/test-suite/corpus/pycsl-reference/"
B = "PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises TypeError (the `__main__` driver prints VIOLATION)."
def W(i, name, route, desc, body, call, exp="FAIL", now=None, imports=""):
    if exp == "FAIL":
        head = f"Test {i} -- route #{route} (expected FAIL): {desc} {B} Now REFUSED ({now})."
    else:
        head = f"Test {i} -- route #{route} (expected PASS): CONTROL: {desc} PROVED at base and candidate."
    src = f'r"""{head}\n"""\n# pycsl-expected: {exp}\n{imports}' + textwrap.dedent(body).strip("\n") + "\n\n\n"
    src += 'if __name__ == "__main__":\n    try:\n        r = ' + call + '\n        print("result", r)\n    except Exception as e:\n        print("VIOLATION", type(e).__name__, e)\n'
    open(C + f"{i}_{name}.py", "w").write(src)
RG = "PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM"
UR = "PYCSL-R349-UNHASHABLE-RECORD"
CU = "PYCSL-R430-CALLEE-UNDERIVABLE-HASH"
# ---- #438 (red-team 34 witnesses, witnesses-r438/)
W(6600, "r438_hash_bare_tuple_param", 438, "red team 34 w00: `hash(t)` of a parameter `t: tuple` under `no_exception \\all`; `f(([1],))`.", '''
#@ no_exception \\all
def f(t: tuple) -> int:
    return hash(t)
''', "f(([1],))", now=RG)
W(6601, "r438_set_bare_tuple_param", 438, "red team 34 y00: `{t}` of a parameter `t: tuple`.", '''
#@ no_exception \\all
def f(t: tuple) -> int:
    s = {t}
    return len(s)
''', "f(([1],))", now=RG)
W(6602, "r438_set_typing_Tuple_param", 438, "red team 34 y01: `{t}` of a parameter `t: typing.Tuple` (un-parameterised).", '''
#@ no_exception \\all
def f(t: Tuple) -> int:
    s = {t}
    return len(s)
''', "f(([1],))", now=RG, imports="from typing import Tuple\n\n")
W(6603, "r438_ret_bare_tuple_set", 438, "red team 34 u1: a callee `-> tuple` returning a `Tuple[List[int], int]`; the caller hashes `{g(t)}` bound to a local.", '''
def g(t: Tuple[List[int], int]) -> tuple:
    return t


#@ no_exception \\all
def f(t: Tuple[List[int], int]) -> int:
    k = g(t)
    s = {k}
    return len(s)
''', "f(([1], 1))", now=RG, imports="from typing import List, Tuple\n\n")
W(6604, "r438_ifexp_bare_tuple", 438, "red team 34 w04: `{t if c else ()}` with `t: tuple`.", '''
#@ no_exception \\all
def f(t: tuple, c: bool) -> int:
    s = {t if c else ()}
    return len(s)
''', "f(([1],), True)", now=RG)
W(6605, "r438_tuple_in_tuple", 438, "red team 34 w05: `{(1, t)}` with `t: tuple` (a component).", '''
#@ no_exception \\all
def f(t: tuple) -> int:
    s = {(1, t)}
    return len(s)
''', "f(([1],))", now=RG)
W(6606, "r438_walrus_bare_tuple", 438, "red team 34 w06: `{(u := t)}` with `t: tuple`.", '''
#@ no_exception \\all
def f(t: tuple) -> int:
    s = {(u := t)}
    return len(s)
''', "f(([1],))", now=RG)
W(6607, "r438_typing_Tuple_ret", 438, "red team 34 w07: `{g3(t)}` with `g3(..) -> Tuple` (un-parameterised).", '''
def g3(t: Tuple[List[int], int]) -> Tuple:
    return t


#@ no_exception \\all
def f(t: Tuple[List[int], int]) -> int:
    s = {g3(t)}
    return len(s)
''', "f(([1], 1))", now=RG, imports="from typing import List, Tuple\n\n")
W(6608, "r438_method_bare_tuple", 438, "red team 34 w11: a method hashing its parameter `t: tuple`.", '''
class C:
    #@ no_exception \\all
    def m(self, t: tuple) -> int:
        s = {t}
        return len(s)
''', "C().m(([1],))", now=RG)
W(6609, "r438_ret_bare_tuple_hash", 438, "red team 34 y13: `hash(k)` with `k = g2(t)`, `g2(..) -> tuple`.", '''
def g2(t: Tuple[List[int], int]) -> tuple:
    return t


#@ no_exception \\all
def f(t: Tuple[List[int], int]) -> int:
    k = g2(t)
    return hash(k)
''', "f(([1], 1))", now=RG, imports="from typing import List, Tuple\n\n")
W(6610, "r438_field_bare_tuple", 438, "red team 34 y14: `{r.t}` of a field annotated `tuple`.", '''
class R:
    def __init__(self, t: tuple) -> None:
        self.t: tuple = t


#@ no_exception \\all
def f(r: R) -> int:
    s = {r.t}
    return len(s)
''', "f(R(([1],)))", now=RG)
W(6611, "r438_nested_bare_tuple_component", 438, "NEW latent: `{t}` with `t: Tuple[int, tuple]` (a bare `tuple` COMPONENT); `f((1, ([1],)))`.", '''
#@ no_exception \\all
def f(t: Tuple[int, tuple]) -> int:
    s = {t}
    return len(s)
''', "f((1, ([1],)))", now=RG, imports="from typing import Tuple\n\n")
W(6612, "r438_set_of_bare_tuple_elements", 438, "NEW latent: `set(xs)` with `xs: List[tuple]` hashes each element (a hashed iterable).", '''
#@ no_exception \\all
def f(xs: List[tuple]) -> int:
    s = set(xs)
    return len(s)
''', "f([([1],)])", now=RG, imports="from typing import List\n\n")
W(6613, "r438_claimed_caller_bare_tuple_callee", 438, "NEW latent (#430 channel): a `no_exception \\all` caller of an UN-CLAIMED same-file callee hashing `t: tuple`.", '''
#@ ensures \\result == 1
def h(t: tuple) -> int:
    s = {t}
    return 1


#@ no_exception \\all
#@ ensures \\result == 1
def caller(t: tuple) -> int:
    return h(t)
''', "caller(([1],))", now=CU)
# ---- #439
W(6615, "r439_protocol_value_hashed", 439, "red team 34 pp08: `{c}` with `c: Pr`, `class Pr(Protocol)` with `__len__` (a list satisfies it structurally); `f([1])`.", '''
class Pr(Protocol):
    def __len__(self) -> int:
        ...


#@ no_exception \\all
def f(c: Pr) -> int:
    s = {c}
    return len(s)
''', "f([1])", now=UR, imports="from typing import Protocol\n\n")
W(6616, "r439_callable_value_hashed", 439, "red team 34 pp11: `{c}` with `c: Callable[[], int]`, called with an instance of a class with `__call__` and `__hash__ = None`.", '''
class Cc:
    __hash__ = None

    def __call__(self) -> int:
        return 1


#@ no_exception \\all
def f(c: Callable[[], int]) -> int:
    s = {c}
    return len(s)
''', "f(Cc())", now=UR, imports="from typing import Callable\n\n")
W(6617, "r439_hashable_abc_value_hashed", 439, "NEW latent: `hash(c)` with `c: Hashable` (structural: `([1],)` is `Hashable`, its hash raises).", '''
#@ no_exception \\all
def f(c: Hashable) -> int:
    return hash(c)
''', "f(([1],))", now=UR, imports="from typing import Hashable\n\n")
W(6618, "r439_typing_dot_protocol_value", 439, "NEW latent: `{c}` with `c: Pr`, `class Pr(typing.Protocol)` spelled through the module.", '''
class Pr(typing.Protocol):
    def __len__(self) -> int:
        ...


#@ no_exception \\all
def f(c: Pr) -> int:
    s = {c}
    return len(s)
''', "f([1])", now=UR, imports="import typing\n\n")
W(6619, "r439_supports_int_value_hashed", 439, "NEW latent: `{c}` with `c: SupportsInt` (a `typing` Protocol; an unhashable class with `__int__` satisfies it).", '''
class I:
    __hash__ = None

    def __int__(self) -> int:
        return 1


#@ no_exception \\all
def f(c: SupportsInt) -> int:
    s = {c}
    return len(s)
''', "f(I())", now=UR, imports="from typing import SupportsInt\n\n")
W(6620, "r439_usermod_callee_module_import", 439, "red team 34 j5: `import multi_file_lib.r439_hashlib as hl`; `hl.h(m)` where the UN-CLAIMED imported `h` hashes `m.get(\"a\")` (`Dict[str, Any]`).", '''
#@ no_exception \\all
#@ ensures \\result == 1
def f(m: Dict[str, Any]) -> int:
    return hl.h(m)
''', 'f({"a": [1]})', now=CU, imports="from typing import Any, Dict\nimport multi_file_lib.r439_hashlib as hl\n\n")
W(6621, "r439_usermod_callee_from_import", 439, "red team 34 j6: `from multi_file_lib.r439_hashlib import h`; `h(m)`, the UN-CLAIMED imported `h` hashes `m.get(\"a\")`.", '''
#@ no_exception \\all
#@ ensures \\result == 1
def f(m: Dict[str, Any]) -> int:
    return h(m)
''', 'f({"a": [1]})', now=CU, imports="from typing import Any, Dict\nfrom multi_file_lib.r439_hashlib import h\n\n")
W(6622, "r439_usermod_callee_transitive", 439, "NEW latent: the imported `mid(m)` (no set display of its own) calls `h(m)` of ANOTHER user module that hashes `m.get(\"a\")`.", '''
#@ no_exception \\all
#@ ensures \\result == 1
def f(m: Dict[str, Any]) -> int:
    return mid(m)
''', 'f({"a": [1]})', now=CU, imports="from typing import Any, Dict\nfrom multi_file_lib.r439_hashmid import mid\n\n")
W(6624, "r439_setattr_computed_name_field", 439, "red team 34 s0: `setattr(self, nm, [1])` in `__init__` (a computed name), then `{r.x}` with `x: int`; `f(R(\"x\"))`.", '''
class R:
    def __init__(self, nm: str) -> None:
        self.x: int = 1
        setattr(self, nm, [1])


#@ no_exception \\all
def f(r: R) -> int:
    s = {r.x}
    return len(s)
''', 'f(R("x"))', now=RG)
W(6625, "r439_dict_store_computed_name_field", 439, "NEW latent: `self.__dict__[nm] = [1]` (a computed key), then `{r.x}`.", '''
class R:
    def __init__(self, nm: str) -> None:
        self.x: int = 1
        self.__dict__[nm] = [1]


#@ no_exception \\all
def f(r: R) -> int:
    s = {r.x}
    return len(s)
''', 'f(R("x"))', now=RG)
W(6626, "r439_vars_update_field", 439, "NEW latent: `vars(self).update(kw)` (computed names), then `{r.x}`.", '''
class R:
    def __init__(self, kw: Dict[str, List[int]]) -> None:
        self.x: int = 1
        vars(self).update(kw)


#@ no_exception \\all
def f(r: R) -> int:
    s = {r.x}
    return len(s)
''', 'f(R({"x": [1]}))', now=RG, imports="from typing import Dict, List\n\n")
W(6627, "r439_setattr_computed_name_class_attr", 439, "NEW latent: `setattr(C, nm, [1])` (a computed name) rebinding the class attribute `C.K = 1`, then `{C.K}`.", '''
class C:
    K = 1


def put(nm: str) -> None:
    setattr(C, nm, [1])


#@ no_exception \\all
def f() -> int:
    s = {C.K}
    return len(s)
''', 'put("K") or f()', now=RG)
# ---- controls
W(6640, "r438_control_typed_tuples", 438, "a PARAMETERISED tuple (`Tuple[int, str]`, `Tuple[int, ...]`, a field `Tuple[str, int]`, a tuple display of typed values) hashed under `no_exception \\all`, and a bare `t: tuple` hashed in an UN-claimed function (its TypeError is ambient there), are not refused.", '''
class R:
    def __init__(self, t: Tuple[str, int]) -> None:
        self.t: Tuple[str, int] = t


#@ no_exception \\all
#@ ensures \\result == n + 1
def f(a: Tuple[int, str], b: Tuple[int, ...], r: R, n: int) -> int:
    s = {a, (1, "x")}
    k = {b: 1}
    u = {r.t}
    return n + 1


#@ ensures \\result == n + 1
def g(t: tuple, n: int) -> int:
    s = {t}
    return n + 1
''', 'f((1, "a"), (1, 2), R(("x", 1)), 1) + g((1,), 1)', exp="PASS", imports="from typing import Tuple\n\n")
W(6641, "r439_control_protocol_not_hashed", 439, "a file with a `Protocol` class and a `Callable` parameter that are NOT hashed, an `int` / `str` hashed under `no_exception \\all`, and a `setattr` with a CONSTANT-free file (no computed-name store) hashing a typed field, are not refused.", '''
class Pr(Protocol):
    def __len__(self) -> int:
        ...


class R:
    def __init__(self, x: int) -> None:
        self.x: int = x


#@ no_exception \\all
#@ ensures \\result == n + 1
def f(c: Pr, cb: Callable[[], int], k: str, r: R, n: int) -> int:
    s = {k, "a"}
    u = {r.x}
    return n + 1
''', 'f([1], lambda: 1, "k", R(2), 1)', exp="PASS", imports="from typing import Callable, Protocol\n\n")
W(6642, "r439_control_usermod_claimed_callee", 439, "a `no_exception \\all` caller of imported user-module functions that CLAIM `no_exception \\all` (hashing a `str`) or hash nothing (`int` arithmetic) is not refused.", '''
#@ no_exception \\all
#@ ensures \\result == n + 2
def f(k: str, n: int) -> int:
    return hs(k, n) + inc(n) - n
''', 'f("a", 1)', exp="PASS", imports="from multi_file_lib.r439_okhash import hs, inc\n\n")
W(6643, "r439_control_setattr_unclaimed", 439, "a file with `setattr(self, nm, v)` (a computed name): a field hashed in an UN-claimed function, and a typed parameter hashed under `no_exception \\all`, are not refused.", '''
class R:
    def __init__(self, nm: str) -> None:
        self.x: int = 1
        setattr(self, nm, 2)


#@ ensures \\result == n + 1
def g(r: R, n: int) -> int:
    s = {r.x}
    return n + 1


#@ no_exception \\all
#@ ensures \\result == n + 1
def f(k: int, n: int) -> int:
    s = {k}
    return n + 1
''', 'g(R("y"), 1) + f(3, 1)', exp="PASS")
L = C + "multi_file_lib/"
open(L + "r439_hashlib.py", "w").write('''"""Helper for corpus 6620 / 6621 (route #439): an UN-CLAIMED function hashing an underivable value."""
from typing import Any, Dict


#@ ensures \\result == 1
def h(m: Dict[str, Any]) -> int:
    s = {m.get("a")}
    return 1
''')
open(L + "r439_hashmid.py", "w").write('''"""Helper for corpus 6622 (route #439): an UN-CLAIMED function that hashes nothing itself but calls
the user module r439_hashlib's `h`, which does."""
from typing import Any, Dict
from multi_file_lib.r439_hashlib import h


#@ ensures \\result == 1
def mid(m: Dict[str, Any]) -> int:
    return h(m)
''')
open(L + "r439_okhash.py", "w").write('''"""Helper for corpus 6642 (route #439 control): a CLAIMED hashing function and one that hashes nothing."""


#@ no_exception \\all
#@ ensures \\result == n + 1
def hs(k: str, n: int) -> int:
    s = {k}
    return n + 1


#@ ensures \\result == n + 1
def inc(n: int) -> int:
    return n + 1
''')
