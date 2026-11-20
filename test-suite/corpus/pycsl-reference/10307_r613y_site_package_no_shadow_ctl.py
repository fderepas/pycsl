r"""Test 10307 -- run #8 u58, review rt69 G6 (PASS control). The program imports the installed `lark`, and no
resolution root holds a module named like anything lark (or any installed package) imports. Emitted.
`--no-proof`: an emission control (the refusal it controls is a resolver verdict); `lark` is installed for
the venv interpreter pycsl runs under, not for /usr/bin/python3, which check-corpus-executes uses to load
PASS drivers (the python-reference lark drivers are `--no-proof` for the same reason).
"""
# pycsl-expected: PASS
# pycsl-flags: --no-proof
import lark


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return len("abc")


if __name__ == "__main__":
    print("result", f())
