r"""Test 10223 -- run #8 u55, review rt66 g01 (FAIL). The program imports only `zoneinfo`, whose
`_tzpath` calls `sysconfig.get_config_var` at import time; sysconfig imports its build data by a
COMPUTED name (`_sysconfigdata__linux_x86_64-linux-gnu` on this interpreter). The --import-path root holds
a local file of that name, which CPython loads. REFUSED: PYCSL-SEM-IMPORT-TRANSITIVE-SHADOW (the judged
name set now holds every module entry of the stdlib directories). PLATFORM NOTE: the name is the one
x86_64 Linux CPython 3.14 builds; elsewhere the file is inert and the witness emits.
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613x/g01
import zoneinfo


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return 1


if __name__ == "__main__":
    print("result", f())
