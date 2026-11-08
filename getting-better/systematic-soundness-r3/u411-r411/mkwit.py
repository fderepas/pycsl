import os, re
G = "/home/fabrice/git/pycsl-u411/getting-better/systematic-soundness-r3/g2-r411-416/r411-held-witnesses"
C = "/home/fabrice/git/pycsl-u411/test-suite/corpus/pycsl-reference"
BASE = "77b33f239"
ren = {
    "6050_gen37_r411_latin1_literal_index_exc.py": "6200_r411_latin1_literal_index_exc.py",
    "6051_gen37_r411_latin1_contract_index.py": "6201_r411_latin1_contract_index.py",
    "6052_gen37_r411_latin1_index_eq.py": "6202_r411_latin1_index_eq.py",
    "6053_gen37_r411_latin1_contract_len.py": "6203_r411_latin1_contract_len.py",
    "6054_gen37_r411_latin1_concat_len.py": "6204_r411_latin1_concat_len.py",
    "6055_gen37_r411_ctl_latin1_literal.py": "6208_r411_ctl_latin1_literal.py",
}
for old, new in ren.items():
    t = open(os.path.join(G, old)).read()
    num = new[:4]
    t = re.sub(r"Test 605\d -- gen #37 route #411", f"Test {num} -- route #411", t, count=1)
    t = t.replace("base 4431ef86f", f"base {BASE}")
    open(os.path.join(C, new), "w").write(t)

HDR = 'r"""Test {n} -- route #411 ({exp}): {desc}\n"""\n# pycsl-expected: {e}\n'
extra = {
    "6205_r411_newline_contract_len.py": ("expected FAIL", "FAIL",
        r'`requires s == "\n"`, `ensures \result == 4` over `len(s)` (CPython 1; PROVED at base ' + BASE + r': Why3 1.8.2 prints `"\n"` to Z3 as `\x0A`, which SMT-LIB 2.6 reads as FOUR characters).',
        '#@ requires s == "\\n"\n#@ ensures \\result == 4\ndef f(s: str) -> int:\n    return len(s)\n\n\nif __name__ == "__main__":\n    r = f("\\n")\n    print("VIOLATION ensures" if r != 4 else "result", r)\n'),
    "6206_r411_tab_index_exc.py": ("expected FAIL", "FAIL",
        r'`t = "\t"; t[1]` under `no_exception \all` (CPython IndexError; PROVED at base ' + BASE + r': the tab literal was four characters to Z3).',
        '#@ no_exception \\all\ndef f() -> str:\n    t = "\\t"\n    return t[1]\n\n\nif __name__ == "__main__":\n    try:\n        print("result", f())\n    except Exception as e:\n        print("VIOLATION", type(e).__name__, e)\n'),
    "6207_r411_quote_contract_len.py": ("expected FAIL", "FAIL",
        r'`requires s == "a\"b"`, `ensures \result == 6` over `len(s)` (CPython 3; PROVED at base ' + BASE + r': `"` was printed `\x22`, four characters to Z3).',
        '#@ requires s == "a\\"b"\n#@ ensures \\result == 6\ndef f(s: str) -> int:\n    return len(s)\n\n\nif __name__ == "__main__":\n    r = f("a\\"b")\n    print("VIOLATION ensures" if r != 6 else "result", r)\n'),
}
for name, (exp, e, desc, body) in extra.items():
    open(os.path.join(C, name), "w").write(HDR.format(n=name[:4], exp=exp, desc=desc, e=e) + body)

ctl = open("/tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/u411/wit/c1_controls.py").read()
ctl = ctl.replace("# pycsl-expected: PASS\n", "")
desc = (r'CONTROL: escaped literals have their Python lengths and characters: `len("é") == 1`, '
        r'`len("\n") == 1`, `len("a\"b") == 3`, `len("a\\b") == 3`, `len("é" + s) == len(s) + 1`, '
        r'`s[0]` of `"é"` raises nothing, `len("x\t") == 2`, `"\n" != "\r"` (CPython agrees). '
        r'FAILED at base ' + BASE + ' (each such literal was 4 characters per escape to Z3), PROVED after the repair.')
main = '\n\nif __name__ == "__main__":\n    print(f1(), f2("\\n"), f3("a\\"b"), f4("a\\\\b"), f5("ab"), f6("é"), f7(), f8())\n'
open(os.path.join(C, "6209_r411_ctl_escaped_literals.py"), "w").write(
    HDR.format(n="6209", exp="expected PASS", desc=desc, e="PASS") + ctl.rstrip("\n") + main)
print("ok")
