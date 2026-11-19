r"""Test 10225 -- run #8 u55, review rt66 g09 (FAIL). No import at all. Ubuntu's stdlib-directory
sitecustomize installs apport_python_hook, whose excepthook runs `import apport.report` on an uncaught
exception; the --import-path root (CPython: PYTHONPATH) holds a local `apport/` package, which
/usr/bin/python3 loads. The startup-hook closure (sitecustomize / usercustomize / .pth, module by module
through the site directories) now feeds the judged name set. REFUSED: PYCSL-SEM-IMPORT-TRANSITIVE-SHADOW.
ENVIRONMENT NOTE: the name is judged only where an installed startup hook reaches `apport`.
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613x/g09


#@ requires x > 0
#@ ensures \result == 10 // x
#@ assigns \nothing
def f(x: int) -> int:
    return 10 // x


if __name__ == "__main__":
    print("result", f(5))
    raise ValueError("uncaught on purpose")
