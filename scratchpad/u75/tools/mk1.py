# mk1.py : write the u75 probes (benign: tiny int functions) under scratchpad/u75/probes/u75/<id>/P/
import os, textwrap
R = "/home/fabrice/git/pycsl-u75/scratchpad/u75/probes/u75"
B1 = "#@ ensures \\result == 1\n#@ assigns \\nothing\ndef one() -> int:\n    return 1\n"
C2 = "#@ ensures \\result == 2\n#@ assigns \\nothing\ndef one() -> int:\n    return 2\n"
K3 = "#@ ensures \\result == 3\n#@ assigns \\nothing\ndef three() -> int:\n    return 3\n"
P = {}
def put(pid, files):
    for rel, src in files.items():
        f = os.path.join(R, pid, "P", rel)
        os.makedirs(os.path.dirname(f), exist_ok=True)
        open(f, "w").write(textwrap.dedent(src).lstrip("\n"))
R1 = '''
class C:
    def __init__(self) -> None:
        self.b = 1


#@ ensures \\result == 4
def g({arg}) -> int:
    c = C()
    return c.b + three()


print("result", g({call}))
'''
def r1(pid, head, arg="", call="", extra=None, k=K3):
    put(pid, {"prog.py": head + R1.format(arg=arg, call=call), f"zv75{pid}/__init__.py": "",
              f"zv75{pid}/b.py": B1, f"zv75{pid}/k.py": k, **(extra or {})})
# Task 1 controls / fail-closed
r1("a1", f"from typing import List, Optional\nfrom zv75a1.k import three\n\n", "xs: Optional[List[int]]", "[1]")
r1("a2", f"import typing\nfrom zv75a2.k import three\n\n", "xs: typing.List[int]", "[1]")
r1("a3", f"import zv75a3.k\nfrom zv75a3.k import three\n\n\nclass D(zv75a3.k.Base):\n    pass\n\n", k=K3 + "\n\nclass Base:\n    pass\n")
r1("a4", f"from zv75a4.k import three, Base\n\n\nclass D(Base):\n    pass\n\n", k=K3 + "\n\nclass Base:\n    pass\n\n\nBase = Base\n")
r1("a5", f"from zv75a5.k import three, Base\n\n\nclass D(Base):\n    pass\n\n\n_G = globals()\n", k=K3 + "\n\nclass Base:\n    pass\n")
# Rule M (#636)
SRC = '''
class _Src:
    b = K
'''
KK = "class K:\n    @staticmethod\n    def one() -> int:\n        return 2\n\n"
G1 = '''

#@ ensures \\result == 1
def g() -> int:
    return {p}.b.one()


print("result", g())
'''
def m(pid, body):
    p = f"zv75{pid}"
    put(pid, {"prog.py": f"import {p}.b\nimport functools\n\n" + KK + "\nclass _Src:\n    b = K\n\n\n" + body.format(p=p) + G1.format(p=p),
              f"{p}/__init__.py": "", f"{p}/b.py": B1, f"{p}/c.py": C2})
m("c1", "m = {p}\nfunctools.update_wrapper(m, _Src, assigned=(\"b\",), updated=())\n")
m("c2", "def h(x: object) -> None:\n    functools.update_wrapper(x, _Src, assigned=(\"b\",), updated=())\n\n\nh({p})\n")
put("c3", {"prog.py": '''
import zv75c3.b
from zv75c3.b import one
import functools


def _two() -> int:
    return 2


functools.update_wrapper(one, _two, assigned=("__code__",), updated=())


#@ ensures \\result == 1
def g() -> int:
    return zv75c3.b.one()


print("result", g())
''', "zv75c3/__init__.py": "", "zv75c3/b.py": B1})
put("c4", {"prog.py": '''
import sys
import zv75c4.b
import zv75c4.k


#@ ensures \\result == 1
def g() -> int:
    return zv75c4.b.one()


print(zv75c4.k.CONST, len(sys.argv) > 0, sys.argv[0] != "")
if zv75c4.b is not None:
    print("result", g())
''', "zv75c4/__init__.py": "", "zv75c4/b.py": B1, "zv75c4/k.py": "CONST = 3\n"})
put("c7", {"prog.py": '''
import zv75c7.b
import zv75c7.k


#@ ensures \\result == 1
def g() -> int:
    return zv75c7.b.one()


print(isinstance(zv75c7.k.Base(), zv75c7.k.Base))
print("result", g())
''', "zv75c7/__init__.py": "", "zv75c7/b.py": B1, "zv75c7/k.py": "class Base:\n    pass\n"})
# #635 in a dependency function
put("d1", {"prog.py": '''
import zv75d1.b
from hw75d1 import run

run()


#@ ensures \\result == 1
def g() -> int:
    return zv75d1.b.one()


print("result", g())
''', "zv75d1/__init__.py": "", "zv75d1/b.py": B1, "zv75d1/c.py": C2, "hw75d1.py": '''
def run() -> None:
    import timeit
    timeit.timeit("import zv75d1, zv75d1.c; zv75d1.b = zv75d1.c", number=1)
'''})
# hook scan
HK = '''
import zv75{i}.b
from hw75{i} import three


#@ ensures \\result == 4
def g() -> int:
    return zv75{i}.b.one() + three()


print("result", g())
'''
def h(pid, dep):
    put(pid, {"prog.py": HK.format(i=pid), f"zv75{pid}/__init__.py": "", f"zv75{pid}/b.py": B1, f"hw75{pid}.py": dep + "\n\n" + K3})
h("e1", "def mk() -> int:\n    __getattr__ = 1\n    return __getattr__\n")
h("e2", "import builtins\n\n\ndef has_ga(x: object) -> bool:\n    return hasattr(x, \"__getattr__\")\n")
put("e3", {"prog.py": '''
from zv75e3 import b


#@ ensures \\result == 1
def g() -> int:
    return b.one()


print("result", g())
''', "zv75e3/__init__.py": '''
class K:
    @staticmethod
    def one() -> int:
        return 2


def _ga(name):
    if name == "b":
        return K
    raise AttributeError(name)


def _f(x=(__getattr__ := _ga)):
    return x
''', "zv75e3/b.py": B1})
print("ok")
