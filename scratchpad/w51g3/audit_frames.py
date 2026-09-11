#!/usr/bin/env python3
"""Audit: for every `\trusted` mirror stub, does its declared `assigns` COVER the
self.<field> writes of the LIVE emitter body it stands for?

A `\trusted` stub's contract is ASSUMED, not proved. So an `assigns` that omits a field
the live body really writes is a FALSE ASSUMPTION: callers are told the field survives the
call when it does not. (This is the trap found for `_handle_for_stmt` while re-trusting it.)
"""
import ast, os, re, sys

MIRROR = 'src/self-annotate/src'
LIVE = 'src/pycsl'

def live_path(mrel):
    return os.path.join(LIVE, mrel)

def self_writes(fn):
    w = set()
    for n in ast.walk(fn):
        if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            tgts = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in tgts:
                if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == 'self':
                    w.add(t.attr)
                if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Attribute) \
                   and isinstance(t.value.value, ast.Name) and t.value.value.id == 'self':
                    w.add(t.value.attr)
                if isinstance(t, (ast.Tuple, ast.List)):
                    for e in t.elts:
                        if isinstance(e, ast.Attribute) and isinstance(e.value, ast.Name) and e.value.id == 'self':
                            w.add(e.attr)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            o = n.func.value
            if isinstance(o, ast.Attribute) and isinstance(o.value, ast.Name) and o.value.id == 'self' \
               and n.func.attr in ('add','update','append','extend','pop','clear','remove','discard','setdefault'):
                w.add(o.attr)
    return w

def index_live(path):
    """(class, name) -> FunctionDef for the live file."""
    out = {}
    try:
        t = ast.parse(open(path).read())
    except Exception:
        return out
    for n in t.body:
        if isinstance(n, ast.ClassDef):
            for m in n.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    out[(n.name, m.name)] = m
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[(None, n.name)] = n
    return out

findings = []
checked = 0
no_live = 0
for root, _, files in os.walk(MIRROR):
    for f in files:
        if not f.endswith('.py'):
            continue
        mp = os.path.join(root, f)
        mrel = os.path.relpath(mp, MIRROR)
        lp = live_path(mrel)
        if not os.path.exists(lp):
            continue
        src = open(mp).read()
        lines = src.split('\n')
        live_idx = index_live(lp)
        try:
            mt = ast.parse(src)
        except Exception:
            continue
        def walk_cls(node, cls):
            global checked, no_live
            for m in node.body:
                if isinstance(m, ast.ClassDef):
                    walk_cls(m, m.name)
                    continue
                if not isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                # gather the #@ block immediately above the def
                start = m.lineno - 1
                i = start - 1
                block = []
                while i >= 0:
                    ln = lines[i].strip()
                    if ln.startswith('#@') or ln.startswith('#') or ln == '':
                        block.append(ln); i -= 1
                        if ln == '' and len(block) > 1: break
                        continue
                    if ln.startswith('@'):
                        i -= 1; continue
                    break
                block = list(reversed(block))
                txt = '\n'.join(block)
                if '\\trusted' not in txt:
                    continue
                mm = re.findall(r'#@ assigns ([^\n]*)', txt)
                if not mm:
                    continue
                decl = set()
                for fld in mm[-1].split(','):
                    fld = fld.strip()
                    if fld.startswith('self.'):
                        decl.add(fld[5:])
                lf = live_idx.get((cls, m.name))
                if lf is None:
                    no_live += 1
                    continue
                checked += 1
                w = self_writes(lf)
                missing = w - decl
                if missing:
                    findings.append((mrel, cls, m.name, sorted(missing), len(decl)))
        for n in mt.body:
            if isinstance(n, ast.ClassDef):
                walk_cls(n, n.name)
        walk_cls(mt, None)

print(f"[*] trusted-stub frame audit: {checked} \\trusted stub(s) with an `assigns` and a live counterpart")
print(f"    ({no_live} \\trusted stub(s) skipped — no live counterpart of the same (class, name))")
print(f"[{'!' if findings else '+'}] {len(findings)} stub(s) whose declared `assigns` OMITS a field the LIVE body writes")
for mrel, cls, name, missing, ndecl in sorted(findings):
    print(f"    {mrel}::{cls}.{name}  declared {ndecl} field(s), MISSING {len(missing)}: {', '.join(missing)}")
