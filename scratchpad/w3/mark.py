#!/usr/bin/env python3
"""Add or remove `#@ sibling_concrete` on the mirror stub(s) of a method."""
import sys, re, ast

def blocks(path):
    src = open(path).read()
    lines = src.split('\n')
    tree = ast.parse(src)
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef):
            out.append((n.name, n.lineno - 1))
    return lines, out

def firstclause(lines, defline):
    """index of the FIRST contiguous `#@` line above defline"""
    i = defline - 1
    first = None
    while i >= 0 and (lines[i].strip().startswith('#') or lines[i].strip().startswith('@')
                      or lines[i].strip() == ''):
        if lines[i].strip().startswith('#@ '):
            first = i
        i -= 1
    return first

def apply(path, meth, add=True):
    lines, defs = blocks(path)
    hits = [d for (nm, d) in defs if nm == meth]
    if len(hits) != 1:
        return 0
    d = hits[0]
    fi = firstclause(lines, d)
    if fi is None:
        return 0
    ind = lines[fi][:len(lines[fi]) - len(lines[fi].lstrip())]
    marker = ind + '#@ sibling_concrete'
    if add:
        if any(l.strip() == '#@ sibling_concrete' for l in lines[max(0, d-40):d]):
            return 0
        lines.insert(fi, marker)
    else:
        idx = [i for i in range(max(0, d-40), d) if lines[i].strip() == '#@ sibling_concrete']
        if not idx:
            return 0
        del lines[idx[-1]]
    open(path, 'w').write('\n'.join(lines))
    return 1

if __name__ == '__main__':
    mode, meth = sys.argv[1], sys.argv[2]
    n = 0
    for p in sys.argv[3:]:
        n += apply(p, meth, add=(mode == 'add'))
    print(f"{mode} {meth}: {n} file(s)")
