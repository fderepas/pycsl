#!/usr/bin/env python3
r"""port-one-mirror-body.py — replace ONE mirror function's BODY with its live twin's.

Promoted from `scratchpad` in gen #31 because `bin/screen-conversion-candidate.sh` drives
it, and a screening tool whose porter lives in a scratch directory is a screening tool that
stops existing at the end of a session.

The mirror keeps its own `def` line (its type annotations are its modelling layer and the
fidelity plane PERMITS them to differ — `_normalize` de-annotates before comparing) and its
`#@` contract lines. Only the statements change.

ABORTS rather than guesses:
  * the name must resolve to exactly ONE def in each file (qualified, so `Class.method`)
  * the mirror body must be a FACADE (`pass` / `return None` / `return <literal>`), because
    replacing a real body is a different and much more dangerous operation
  * a docstring in the mirror body is preserved; the live docstring is not copied over it

Usage:  port_one.py <tree> <relative/path.py> <function> [--convert]
        --convert also deletes the governing `#@ \trusted` line (line-prefix match, never a
        substring — wall-lesson (j6)).
"""
import ast, io, os, sys


def find(path, fn):
    """Resolve `fn` to definitions in `path`.

    `fn` may be a BARE name (`cur`) or a QUALIFIED one (`_ContractParser.__init__`,
    `Mixin._collect.rec`). The qualified form exists because eight bare names in the
    conversion list resolve to FIFTEEN definitions between them — `pure_ast.py` alone has
    five `__init__`s — and a tool that can only say "ambiguous" about those is a tool that
    leaves fifteen candidates unscreened. The authoritative source of the qualified name is
    `getting-better/trusted-reasons.tsv`, which carries one row per live marker.
    """
    src = io.open(path, encoding="utf-8").read()
    lines = src.split("\n")
    tree = ast.parse(src)
    hits = []
    qualified = "." in fn

    def walk(n, pre):
        for c in ast.iter_child_nodes(n):
            if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef)):
                q = pre + c.name
                if (q == fn) if qualified else (c.name == fn):
                    hits.append(c)
                walk(c, q + ".")
            elif isinstance(c, ast.ClassDef):
                walk(c, pre + c.name + ".")
            else:
                walk(c, pre)

    walk(tree, "")
    return src, lines, hits


def is_facade(node):
    st = [x for x in node.body
          if not (isinstance(x, ast.Expr) and isinstance(x.value, ast.Constant)
                  and isinstance(x.value.value, str))]
    return len(st) == 1 and (isinstance(st[0], ast.Pass)
                             or (isinstance(st[0], ast.Return)
                                 and (st[0].value is None
                                      or isinstance(st[0].value, ast.Constant))))


def body_span(node, lines):
    """(first, last) 0-based line indices of the body, docstring EXCLUDED."""
    body = list(node.body)
    if (body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)):
        body = body[1:]
    if not body:
        return None
    first = body[0].lineno - 1
    # `ast.walk` yields context nodes (`Load`, `Store`, ...) that carry NO position at all,
    # so `getattr(x, "end_lineno", x.lineno)` raised AttributeError on the fallback — and the
    # crash happened BEFORE the file was written, so the caller saw an unmodified tree and a
    # traceback it did not recognise as an abort. The first port screen reported
    # **PORTS+LOWERS** for ten candidates it had never ported. Filter for a position first.
    last = max([x.end_lineno for x in ast.walk(body[-1])
                if getattr(x, "end_lineno", None) is not None]
               or [body[-1].lineno]) - 1
    return first, last


def main():
    tree_root, rel, fn = sys.argv[1], sys.argv[2], sys.argv[3]
    convert = "--convert" in sys.argv[4:]
    mp = os.path.join(tree_root, "src/self-annotate/src", rel)
    lp = os.path.join(tree_root, "src/pycsl", rel)
    msrc, mlines, mhits = find(mp, fn)
    lsrc, llines, lhits = find(lp, fn)
    if len(mhits) != 1 or len(lhits) != 1:
        print("ABORT: %s::%s resolves to %d mirror / %d live def(s)"
              % (rel, fn, len(mhits), len(lhits)))
        return 2
    m, l = mhits[0], lhits[0]
    if not is_facade(m) and "--replace" not in sys.argv[4:]:
        print("ABORT: the mirror body of %s::%s is not a facade "
              "(pass --replace to overwrite a REAL body; that is the DIFFERS population, "
              "where the mirror holds a different program from live and replacing it is the "
              "point rather than an accident)" % (rel, fn))
        return 2
    ms, ls = body_span(m, mlines), body_span(l, llines)
    if ms is None or ls is None:
        print("ABORT: empty body")
        return 2
    m_indent = len(mlines[ms[0]]) - len(mlines[ms[0]].lstrip())
    l_indent = len(llines[ls[0]]) - len(llines[ls[0]].lstrip())
    shift = m_indent - l_indent
    new_body = []
    for ln in llines[ls[0]:ls[1] + 1]:
        if not ln.strip():
            new_body.append("")
        elif shift >= 0:
            new_body.append(" " * shift + ln)
        else:
            if ln[:-shift].strip():
                print("ABORT: cannot dedent %r by %d" % (ln, -shift))
                return 2
            new_body.append(ln[-shift:])
    out = mlines[:ms[0]] + new_body + mlines[ms[1] + 1:]

    if convert:
        # delete the governing `#@ \trusted` line: scan upward from the def / first decorator
        first = (min(d.lineno for d in m.decorator_list) if m.decorator_list else m.lineno) - 1
        i = first - 1
        killed = None
        while i >= 0 and (not out[i].strip() or out[i].lstrip().startswith("#")):
            if out[i].lstrip().startswith("#@ \\trusted"):
                killed = i
                break
            i -= 1
        if killed is None:
            print("ABORT: no governing `#@ \\trusted` line to delete")
            return 2
        del out[killed]

    io.open(mp, "w", encoding="utf-8").write("\n".join(out))
    print("ported %s::%s (%d body line(s)%s)"
          % (rel, fn, len(new_body), ", marker deleted" if convert else ""))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                       # noqa: BLE001
        # A CRASH MUST LOOK LIKE AN ABORT. The screen classifies on the first word; an
        # unhandled traceback did not start with ABORT, so the screen carried on and emitted
        # the UNPORTED file. A tool that fails silently reports success.
        print("ABORT: %s: %s" % (type(exc).__name__, exc))
        sys.exit(2)
