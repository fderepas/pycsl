"""How many reference drivers prove their contract WITHOUT the construct they name?

MECHANICAL PROXY, deliberately conservative: a driver is TRIVIALLY DISCHARGED when

  * the verified function has exactly one `#@ ensures`, and it is `\result == <int>`;
  * the function's body ENDS in a top-level `return <that same int>`;
  * the function contains NO OTHER `return`.

Then the postcondition follows from the tail return alone, and every statement above it
is irrelevant to the proof — whatever construct the driver is named for.  Python
`assert`s are DROPPED by Module 6 (a settled fact of this campaign), so an
`x = <construct>; assert <property>; return 0` driver is exactly this shape.
"""
import ast, os, re, sys

root = sys.argv[1] if len(sys.argv) > 1 else "test-suite/corpus/python-reference"
ENS = re.compile(r"^#@\s+ensures\s+\\result\s*==\s*(-?\d+)\s*$")
OTHER = re.compile(r"^#@\s+(requires|assigns|loop|\\variant|raises|ensures)\b")

trivial, total, expected_fail = [], 0, 0
for dp, dn, fn in os.walk(root):
    dn[:] = [d for d in dn if d not in ('.git', '__pycache__')]
    for f in sorted(fn):
        if not f.endswith(".py"):
            continue
        p = os.path.join(dp, f)
        src = open(p, encoding="utf-8", errors="replace").read()
        if "# pycsl-expected: FAIL" in src:
            expected_fail += 1
            continue
        try:
            t = ast.parse(src)
        except Exception:
            continue
        lines = src.split("\n")
        for n in t.body:
            if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            total += 1
            # contract block: the `#@` lines directly above the def
            i = n.lineno - 2
            block = []
            while i >= 0 and lines[i].lstrip().startswith("#@"):
                block.append(lines[i].strip())
                i -= 1
            ens = [ENS.match(b) for b in block]
            ens = [m for m in ens if m]
            others = [b for b in block if OTHER.match(b) and not ENS.match(b)]
            if len(ens) != 1 or others:
                continue
            want = int(ens[0].group(1))
            rets = [r for r in ast.walk(n) if isinstance(r, ast.Return)]
            if len(rets) != 1:
                continue
            body = [s for s in n.body
                    if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
            if not body or not isinstance(body[-1], ast.Return):
                continue
            v = body[-1].value
            if isinstance(v, ast.Constant) and v.value == want:
                trivial.append("%s::%s" % (os.path.relpath(p), n.name))

print("root                 : %s" % root)
print("expected-FAIL drivers: %d (skipped)" % expected_fail)
print("annotated functions  : %d" % total)
print("TRIVIALLY DISCHARGED : %d  (%.0f%%)" % (len(trivial), 100.0*len(trivial)/max(total,1)))
for t_ in trivial[:25]:
    print("    %s" % t_)
if len(trivial) > 25:
    print("    ... and %d more" % (len(trivial)-25))
