r"""Test 10128 -- run #8 route #611 r12 CONTROL (expected PASS): the same dependency with GENUINE unchecked-hash caches (`.pyc` and `.opt-1.pyc`, the compilation of the adjacent source): every loadable cache is provably the source's code object, so the import is accepted and the contract proves exactly as with no cache.
"""
# pycsl-expected: PASS
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r611r12/depok
import r611r12_dep


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    return r611r12_dep.inc(1)


if __name__ == "__main__":
    print(f())
