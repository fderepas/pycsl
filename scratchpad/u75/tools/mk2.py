# mk2.py : write the u75 corpus witnesses 10490-10500 and their helpers (benign: tiny int functions)
import os, textwrap
C = "/home/fabrice/git/pycsl-u75/test-suite/corpus/pycsl-reference"
B1 = "#@ ensures \\result == 1\n#@ assigns \\nothing\ndef one() -> int:\n    return 1\n"
C2 = "#@ ensures \\result == 2\n#@ assigns \\nothing\ndef one() -> int:\n    return 2\n"
K3 = "#@ ensures \\result == 3\n#@ assigns \\nothing\ndef three() -> int:\n    return 3\n"
def put(rel, src):
    f = os.path.join(C, rel)
    assert not os.path.exists(f), f
    os.makedirs(os.path.dirname(f), exist_ok=True)
    open(f, "w").write(textwrap.dedent(src).lstrip("\n") if src else "")
def pkg(p, c=True):
    put(f"{p}/__init__.py", "")
    put(f"{p}/b.py", B1)
    if c:
        put(f"{p}/c.py", C2)
G = '''

#@ ensures \\result == 1
def g() -> int:
    return {p}.b.one()


if __name__ == "__main__":
    print("result", g())
'''
def W(n, doc, exp, body):
    put(n + ".py", 'r"""' + doc.strip() + '\n"""\n# pycsl-expected: ' + exp + "\n" + body)

# ---- route #635 ----
pkg("zu75a")
W("10490_r635_timeit_string_rebinds_submodule_false", """
Test 10490 -- run #9 u75, review rt83 s2, route #635 (FAIL, PRE-EXISTING). The program runs a source STRING
through `timeit.timeit`, and the string replaces the submodule attribute `zu75a.b` with the sibling module
zu75a.c, so `cd <tree root> && python <this file>` prints "result 2". pycsl never reads the string (a plain
`exec` of it is refused by the rebound-name rule); main L21 PROVED the claim below. REFUSED:
PYCSL-SEM-IMPORT-STATE-MANIPULATED (route #326's list gains `timeit`, u75).""", "FAIL",
  "import zu75a.b\nimport timeit\n\ntimeit.timeit(\"import zu75a, zu75a.c; zu75a.b = zu75a.c\", number=1)\n" + G.format(p="zu75a"))
pkg("zu75b")
W("10491_r635_code_interpreter_runsource_rebinds_submodule_false", """
Test 10491 -- run #9 u75, review rt83 s3, route #635 (FAIL, PRE-EXISTING). The program runs a source STRING
through `code.InteractiveInterpreter().runsource`, which replaces the submodule attribute `zu75b.b` with
zu75b.c, so `cd <tree root> && python <this file>` prints "result 2"; main L21 PROVED the claim below.
REFUSED: PYCSL-SEM-IMPORT-STATE-MANIPULATED (route #326's list gains `code`, u75).""", "FAIL",
  "import zu75b.b\nimport code\n\ncode.InteractiveInterpreter().runsource(\"import zu75b, zu75b.c; zu75b.b = zu75b.c\")\n" + G.format(p="zu75b"))
pkg("zu75c")
put("zu75c_run.py", '''
def run() -> None:
    import timeit
    timeit.timeit("import zu75c, zu75c.c; zu75c.b = zu75c.c", number=1)
''')
W("10492_r635_dependency_function_runs_timeit_string_false", """
Test 10492 -- run #9 u75, route #635 (FAIL). A DEPENDENCY function (zu75c_run.run) imports `timeit` and
runs a source string that replaces the submodule attribute `zu75c.b` with zu75c.c; the program calls it,
so `cd <tree root> && python <this file>` prints "result 2". Route #326 judges only the program's imports
(main L21 refuses this file through route #483, which follows the top-level call into the function).
REFUSED: PYCSL-SEM-IMPORT-STATE-MANIPULATED (u75: any reached module other than the program importing a
standard-library module that imports by name or runs source strings).""", "FAIL",
  "import zu75c.b\nfrom zu75c_run import run\n\nrun()\n" + G.format(p="zu75c"))
# ---- route #636 ----
KK = "class K:\n    @staticmethod\n    def one() -> int:\n        return 2\n\n\n"
pkg("zu75d", c=False)
W("10493_r636_update_wrapper_sets_package_submodule_false", """
Test 10493 -- run #9 u75, review rt83 u1, route #636 (FAIL, PRE-EXISTING). The program hands the package
MODULE OBJECT to `functools.update_wrapper(zu75d, _Src, assigned=("b",), updated=())`, which runs
`setattr(zu75d, "b", _Src.b)` inside the standard library and replaces the submodule attribute `zu75d.b`
with the class K, so `cd <tree root> && python <this file>` prints "result 2". No store of the program is
seen; main L21 PROVED the claim below. REFUSED: PYCSL-SEM-IMPORT-MODULE-VALUE (u75, rule M).""", "FAIL",
  "import zu75d.b\nimport functools\n\n" + KK + "class _Src:\n    b = K\n\n\nfunctools.update_wrapper(zu75d, _Src, assigned=(\"b\",), updated=())\n" + G.format(p="zu75d"))
pkg("zu75e", c=False)
W("10494_r636_update_wrapper_replaces_dependency_function_false", """
Test 10494 -- run #9 u75, review rt83 v2, route #636 (FAIL, PRE-EXISTING). The program hands the SUBMODULE
object `zu75e.b` to `functools.update_wrapper(zu75e.b, K, assigned=("one",), updated=())`, which replaces
the dependency function `zu75e.b.one` with `K.one` (returns 2), so `cd <tree root> && python <this file>`
prints "result 2"; main L21 PROVED the claim below. REFUSED: PYCSL-SEM-IMPORT-MODULE-VALUE (u75, rule M).""",
  "FAIL", "import zu75e.b\nimport functools\n\n" + KK + "functools.update_wrapper(zu75e.b, K, assigned=(\"one\",), updated=())\n" + G.format(p="zu75e"))
pkg("zu75f", c=False)
W("10495_r636_module_through_local_function_to_update_wrapper_false", """
Test 10495 -- run #9 u75, route #636 (FAIL). The package module object is passed to a PROGRAM function
`h(x)`, whose body hands its parameter to `functools.update_wrapper(x, _Src, assigned=("b",), updated=())`:
the submodule attribute `zu75f.b` becomes the class K, so `cd <tree root> && python <this file>` prints
"result 2". The store happens in the standard library; main L21 PROVED the claim below. REFUSED:
PYCSL-SEM-IMPORT-MODULE-VALUE (u75, rule M: any value use of a module object, a program callee included).""",
  "FAIL", "import zu75f.b\nimport functools\n\n" + KK + "class _Src:\n    b = K\n\n\ndef h(x: object) -> None:\n    functools.update_wrapper(x, _Src, assigned=(\"b\",), updated=())\n\n\nh(zu75f)\n" + G.format(p="zu75f"))
# ---- controls (u73 over-refusals o4 - o7, rule M) ----
R1 = '''

class C:
    def __init__(self) -> None:
        self.b = 1


#@ ensures \\result == 4
def g({arg}) -> int:
    c = C()
    return c.b + three()


if __name__ == "__main__":
    print("result", g({call}))
'''
pkg("zu75g", c=False); put("zu75g/k.py", K3)
W("10496_r631o_parameter_annotation_typing_alias_beside_store_ctl", """
Test 10496 -- run #9 u75, review rt83 o5 (u73 INTRODUCED over-refusal, PASS). A parameter annotation
`List[int]` (`from typing import List`) beside an unrelated `self.b = 1` (b is also a submodule name of the
package zu75g the walk meets): a typing alias is no module object, so the annotation is no module escape and
the store stays unjudged; `cd <tree root> && python <this file>` prints "result 4" and pycsl proves it
(u73 refused it with PYCSL-SEM-IMPORT-PACKAGE-SUBMODULE-REBOUND).""", "PASS",
  "from typing import List\nfrom zu75g.k import three\n" + R1.format(arg="xs: List[int]", call="[1]"))
pkg("zu75h", c=False); put("zu75h/k.py", K3 + "\n\nclass Base:\n    pass\n")
W("10497_r631o_imported_class_as_base_beside_store_ctl", """
Test 10497 -- run #9 u75, review rt83 o4 (u73 INTRODUCED over-refusal, PASS). A CLASS imported from a
local module (`from zu75h.k import Base`) used as a class base beside an unrelated `self.b = 1`: a class
base that is a class never reaches `__mro_entries__` (PEP 560 calls it only for non-type bases), so it is no
module escape; `cd <tree root> && python <this file>` prints "result 4" and pycsl proves it.""", "PASS",
  "from zu75h.k import three, Base\n\n\nclass D(Base):\n    pass\n" + R1.format(arg="", call=""))
HK = '''import {p}.b
from {h} import three


#@ ensures \\result == 4
def g() -> int:
    return {p}.b.one() + three()


if __name__ == "__main__":
    print("result", g())
'''
pkg("zu75i", c=False)
put("zu75i_proxy.py", "def _fwd(self, name):\n    raise AttributeError(name)\n\n\nclass P:\n    __getattr__ = _fwd\n\n\n" + K3)
W("10498_r631o_dependency_class_body_getattr_ctl", """
Test 10498 -- run #9 u75, review rt83 o6 (u73 INTRODUCED over-refusal, PASS). A reached dependency binds
`__getattr__` in a CLASS body (`class P: __getattr__ = _fwd`, a proxy idiom): a class attribute, no module
hook; `cd <tree root> && python <this file>` prints "result 4" and pycsl proves it (u73 refused it with
PYCSL-SEM-IMPORT-MODULE-HOOK).""", "PASS", HK.format(p="zu75i", h="zu75i_proxy"))
pkg("zu75j", c=False)
put("zu75j_probe.py", "def has_ga(x: object) -> bool:\n    return hasattr(x, \"__getattr__\")\n\n\n" + K3)
W("10499_r631o_dependency_hasattr_hook_name_read_ctl", """
Test 10499 -- run #9 u75, review rt83 o7 (u73 INTRODUCED over-refusal, PASS). A reached dependency READS
the name `__getattr__` with `hasattr(x, "__getattr__")`: no hook is bound; `cd <tree root> && python <this
file>` prints "result 4" and pycsl proves it (u73 refused it with PYCSL-SEM-IMPORT-MODULE-HOOK).""", "PASS",
  HK.format(p="zu75j", h="zu75j_probe"))
pkg("zu75k", c=False); put("zu75k/k.py", "CONST = 3\n")
W("10500_r636o_module_constant_and_stdlib_attribute_arguments_ctl", """
Test 10500 -- run #9 u75, route #636 control (PASS). The program passes a local module's literal constant
`zu75k.k.CONST` and the standard-library attributes `sys.argv` to `print` / `len`, and tests a submodule
in an `if` (an operator / test position): none of them hands a module object (or a local function / class)
out, so rule M does not refuse; `cd <tree root> && python <this file>` prints "result 1" and pycsl proves
it.""", "PASS", '''import sys
import zu75k.b
import zu75k.k


#@ ensures \\result == 1
def g() -> int:
    return zu75k.b.one()


if __name__ == "__main__":
    print(zu75k.k.CONST, len(sys.argv) > 0)
    if zu75k.b is not None:
        print("result", g())
''')
print("ok")
