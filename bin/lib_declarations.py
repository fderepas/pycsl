#!/usr/bin/env python3
r"""lib_declarations.py — THE ONE census of cross-mixin DECLARATIONS in the self-annotation
mirror, and their resolution to a DEFINITION through the LIVE MRO. Pure AST; no pycsl, no why3.

WHY (wall `cross-mixin-declaration-stubs`, driver run #3). A mirror file that calls a sibling
mixin's method cannot see it (each mirror file is transpiled on its own), so it carries a
bodyless LOCAL DECLARATION of it:

  * a `#@ \trusted` stub `def m(...)` inside class C, where the LIVE twin file's class C has NO
    `def m` (the live call resolves through the composite's MRO to another class), or
  * a `#@ requires_method m: <sig>` WINDOW (+ indented `#@   assigns/requires/ensures`) in the
    comment block of a method of class C.

Either one is emitted as an abstract `val` and ASSUMED by every caller in the file. Nothing
compared it with the definition: the census of 2026-10-30 found 12 + 0 declarations whose
frame was NARROWER than the definition's (3 of them load-bearing for 30 verified frames,
route #488). Two consumers import this file so they cannot disagree about the population:

  * `bin/check-trusted-frame-honesty.py` (R0 / B0): declared frame vs the LIVE definition's
    transitive `self` writes;
  * `bin/check-declaration-conformance.py` (R2a / B2): declaration vs the MIRROR twin of the
    definition (frame, raises, requires / ensures, signature).

RESOLUTION. For a declaration of `m` in class C, every live class D whose C3 MRO contains C
(C itself included) is an instance type the declaration's `self` can denote; in each, `m`
resolves to the first class of MRO(D) that defines it. The declaration's DEFINITION set is the
union over D of those resolved classes, minus C (C defines no `m`, by construction). A
declaration whose definition set is empty is DEAD; one with two or more is AMBIGUOUS. Both are
reported by the consumers, never silently passed.
"""
from __future__ import annotations

import ast
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trusted_markers as tm  # noqa: E402

LIVE_REL = "src/pycsl"
MIRROR_REL = "src/self-annotate/src"

# Clause keywords that START a new `#@` clause (anything else continues the previous one).
_KW = ("requires", "ensures", "assigns", "raises", "reads", "terminates", "decreases",
       "variant", "\\trusted", "pure", "no_exception", "behavior", "assumes", "exits",
       "ghost", "diverges", "allow_finalizer", "\\abstract", "sibling_concrete",
       "requires_method", "depends_method", "declared_in", "mutable_state")
_KW_RE = re.compile(r"^(\\?[A-Za-z_]+)")


# --------------------------------------------------------------------------- live graph
def live_graph(live_root):
    """{class: (path, [base names in order], {method names})}. First definition wins on a
    duplicate class name (same rule as `check-trusted-frame-honesty._parse_tree`, which keys
    by name)."""
    classes = {}
    for dirpath, _dirs, files in os.walk(live_root):
        if "__pycache__" in dirpath or "/agents" in dirpath or ".proofs" in dirpath:
            continue
        for fname in sorted(files):
            if not fname.endswith(".py"):
                continue
            path = os.path.join(dirpath, fname)
            try:
                tree = ast.parse(open(path, encoding="utf-8").read())
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue
            for node in tree.body:
                if not isinstance(node, ast.ClassDef) or node.name in classes:
                    continue
                bases = []
                for b in node.bases:
                    if isinstance(b, ast.Name):
                        bases.append(b.id)
                    elif isinstance(b, ast.Attribute):
                        bases.append(b.attr)
                meths = {c.name for c in node.body
                         if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef))}
                classes[node.name] = (path, bases, meths)
    return classes


def c3_mro(cls, classes, _memo=None):
    """C3 linearisation over class NAMES (unknown bases are leaves)."""
    memo = {} if _memo is None else _memo
    if cls in memo:
        return memo[cls]
    memo[cls] = [cls]                       # cycle guard
    bases = [b for b in classes.get(cls, (None, [], set()))[1]]
    seqs = [list(c3_mro(b, classes, memo)) for b in bases] + [list(bases)]
    out = [cls]
    while True:
        seqs = [s for s in seqs if s]
        if not seqs:
            break
        for s in seqs:
            head = s[0]
            if not any(head in t[1:] for t in seqs):
                break
        else:                               # inconsistent: fall back to DFS order
            head = seqs[0][0]
        out.append(head)
        for s in seqs:
            if s and s[0] == head:
                del s[0]
    memo[cls] = out
    return out


def resolve(cls, name, classes, _mros=None):
    """Sorted list of (defining class, live path) that `self.<name>` on a `cls` receiver
    resolves to, over every live class whose MRO contains `cls` (see module docstring)."""
    mros = _mros if _mros is not None else {c: c3_mro(c, classes) for c in classes}
    found = set()
    for d, mro in mros.items():
        if cls not in mro:
            continue
        for k in mro:
            if k in classes and name in classes[k][2]:
                if k != cls:
                    found.add((k, classes[k][0]))
                break
    return sorted(found)


# --------------------------------------------------------------------------- contracts
def _clauses(raw_lines):
    """Merge `#@` lines (already stripped of the `#@` prefix) into clauses."""
    out = []
    for body in raw_lines:
        body = body.strip()
        m = _KW_RE.match(body)
        kw = m.group(1) if m else ""
        if kw in _KW or not out:
            out.append(body)
        else:
            out[-1] += " " + body
    return [re.sub(r"\s+", " ", c).strip() for c in out]


def def_block(lines, node):
    """(own clauses, [windows]) of the comment block above `node` (decorators included).

    A window is `{"name", "sig", "clauses", "line"}`: a `#@ requires_method m: sig` line and
    the following `#@` lines indented by >= 2 spaces after `#@`. A `#@` line indented by < 2
    spaces closes the window (the Weaver's rule: it is the enclosing method's own clause)."""
    first = min([node.lineno] + [d.lineno for d in node.decorator_list])
    i = first - 2
    block = []
    while i >= 0:
        s = lines[i].strip()
        if s.startswith("#") or s == "" or s.startswith("@"):
            if s.startswith("#@"):
                block.append((i + 1, s))
            i -= 1
            continue
        break
    block.reverse()
    own, windows, cur = [], [], None
    for lineno, s in block:
        rest = s[2:]
        indented = re.match(r"^\s{2,}\S", rest) is not None
        body = rest.strip()
        if body.startswith("requires_method ") or body.startswith("depends_method "):
            kind, _, spec = body.partition(" ")
            nm, _, sig = spec.partition(":")
            cur = {"kind": kind, "name": nm.strip(), "sig": sig.strip(), "raw": [],
                   "line": lineno}
            windows.append(cur)
            continue
        if cur is not None and indented:
            cur["raw"].append(body)
            continue
        cur = None
        own.append(body)
    for w in windows:
        w["clauses"] = _clauses(w.pop("raw"))
    return _clauses(own), windows


def by_kw(clauses):
    d = {}
    for c in clauses:
        kw = c.split()[0] if c.split() else ""
        d.setdefault(kw, []).append(c[len(kw):].strip())
    return d


def frame(clauses):
    """(set of normalised assigns targets, present?) -- `\\nothing` and an absent clause are
    both the empty frame (both emit a `val` with no `writes`); `self.x` -> `self.x`."""
    targets, present = set(), False
    for a in by_kw(clauses).get("assigns", []):
        present = True
        for t in re.split(r",(?![^\[]*\])", a):
            t = re.sub(r"\s+", "", t)
            if t and t != "\\nothing":
                targets.add(t)
    return targets, present


def raises(clauses):
    out = set()
    for r in by_kw(clauses).get("raises", []):
        for t in r.split(","):
            t = t.strip()
            if t:
                out.add(t)
    return out


def prepost(clauses, kw):
    """Non-trivial clauses of `kw` (a literal `True` claims nothing and is normalised out)."""
    return sorted(c for c in by_kw(clauses).get(kw, []) if c not in ("True", "true", "\\true"))


# --------------------------------------------------------------------------- census
def _mirror_files(mirror_root):
    out = []
    for dirpath, _dirs, files in os.walk(mirror_root):
        if "__pycache__" in dirpath or ".proofs" in dirpath:
            continue
        for f in files:
            if f.endswith(".py"):
                out.append(os.path.join(dirpath, f))
    return sorted(out)


def declarations(root, classes=None, marker_re=None):
    """Every declaration of the mirror under repo `root`. Each is a dict:
       kind      'stub' | 'window'
       path      mirror file (repo-relative); rel = path below the mirror root
       cls, name declaring class and method name
       clauses   the declaration's own clauses (window: its indented clauses)
       node      the stub's FunctionDef (None for a window); host = window's host def name
       defs      [(defining class, live path)] via `resolve`
    A stub is a def carrying a `\\trusted` marker (or, with `marker_re`, any of its own
    clauses matching it -- used for the `#@ declared_in` class) whose LIVE twin class has no
    `def <name>`."""
    live_root = os.path.join(root, LIVE_REL)
    mirror_root = os.path.join(root, MIRROR_REL)
    classes = classes if classes is not None else live_graph(live_root)
    mros = {c: c3_mro(c, classes) for c in classes}
    out = []
    for path in _mirror_files(mirror_root):
        rel = os.path.relpath(path, mirror_root)
        src = open(path, encoding="utf-8").read()
        lines = src.split("\n")
        tree = ast.parse(src)
        live_path = os.path.join(live_root, rel)
        live_q = set()
        if os.path.exists(live_path):
            lt = ast.parse(open(live_path, encoding="utf-8").read())
            live_q = set(tm.qualnames(lt).values())
        for cnode in tree.body:
            if not isinstance(cnode, ast.ClassDef):
                continue
            for fn in cnode.body:
                if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                own, windows = def_block(lines, fn)
                q = "%s.%s" % (cnode.name, fn.name)
                is_marked = tm._block_marker_line(lines, fn.lineno) is not None
                if marker_re is not None and any(marker_re.match(c) for c in own):
                    is_marked = True
                # `#@ declared_in` (B4) is ALWAYS a declaration-class marker, whatever the
                # caller passes: a consumer that forgot `marker_re` must not lose it.
                decl_in = [c[len("declared_in"):].strip() for c in own
                           if re.match(r"^declared_in\b", c)]
                if decl_in:
                    is_marked = True
                if is_marked and q not in live_q:
                    out.append({"kind": "stub", "path": os.path.relpath(path, root),
                                "rel": rel, "cls": cnode.name, "name": fn.name,
                                "declared_in": decl_in,
                                "trusted_marker": tm._block_marker_line(lines, fn.lineno)
                                is not None,
                                "clauses": [c for c in own if not c.startswith("\\trusted")],
                                "node": fn, "lines": lines, "host": None,
                                "line": fn.lineno,
                                "defs": resolve(cnode.name, fn.name, classes, mros)})
                for w in windows:
                    if w["kind"] != "requires_method":
                        continue
                    out.append({"kind": "window", "path": os.path.relpath(path, root),
                                "rel": rel, "cls": cnode.name, "name": w["name"],
                                "clauses": w["clauses"], "node": None, "lines": lines,
                                "host": fn.name, "line": w["line"], "sig": w["sig"],
                                "defs": resolve(cnode.name, w["name"], classes, mros)})
    return out


def declared_in_markers(root):
    """Every `#@ declared_in` directive in the mirror, as (repo-relative path, qualname, line,
    target text) -- over ALL defs at any nesting (module level and nested defs included), so a
    marker placed on something that is NOT a declaration is seen (the B2 plane refuses it)."""
    out = []
    mirror_root = os.path.join(root, MIRROR_REL)
    for path in _mirror_files(mirror_root):
        src = open(path, encoding="utf-8").read()
        if "declared_in" not in src:
            continue
        lines = src.split("\n")
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node, m, q in tm.iter_declared_in_defs(tree, lines):
            out.append((os.path.relpath(path, root), q, m + 1,
                        re.sub(r"^#@\s*declared_in\b", "", lines[m].strip()).strip()))
        # a directive line attached to no def at all
        att = {m for _n, m, _q in tm.iter_declared_in_defs(tree, lines)}
        for i, l in enumerate(lines):
            if tm.DECL_MARKER.match(l.strip()) and i not in att:
                out.append((os.path.relpath(path, root), None, i + 1, l.strip()))
    return out


def mirror_def(root, live_path, cls, name):
    """(FunctionDef, lines, own clauses, trusted?) of the MIRROR twin of a live definition, or
    None when the mirror does not carry that file / class / method."""
    live_root = os.path.join(root, LIVE_REL)
    rel = os.path.relpath(live_path, live_root)
    mpath = os.path.join(root, MIRROR_REL, rel)
    if not os.path.exists(mpath):
        return None
    src = open(mpath, encoding="utf-8").read()
    lines = src.split("\n")
    for cnode in ast.parse(src).body:
        if isinstance(cnode, ast.ClassDef) and cnode.name == cls:
            for fn in cnode.body:
                if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and fn.name == name:
                    own, _w = def_block(lines, fn)
                    trusted = tm._block_marker_line(lines, fn.lineno) is not None
                    return (fn, lines, [c for c in own if not c.startswith("\\trusted")],
                            trusted, os.path.relpath(mpath, root))
    return None


# --------------------------------------------------------------------------- mirror records
def mirror_classes(root):
    """{class: (mirror path, [bases], {mirror-defined methods}, {annotated class-body fields},
    {visible direct bases})} over the whole mirror. The annotated class-body fields ARE the
    emitted record of a `@dataclass` mixin (measured equal on statements / stmt_control_flow /
    expressions / expr_ghost_collections at 8fdfce794); a class without them is emitted
    opaque. A direct base is VISIBLE (its mirror contracts are imported into this class's unit)
    when the file imports it `from M import B` and `M` resolves to a mirror file RELATIVE TO THE
    IMPORTING FILE'S DIRECTORY -- else pycsl falls back to `--import-path src/pycsl`, the
    un-annotated live tree. Measured: the root-level `Module6_WhyMLTranspiler.mlw` carries
    `statementemissionmixin` (124 mentions) while `module6_whyml/statements.mlw` carries no
    `controlflowstmtmixin` at all although StatementEmissionMixin inherits it."""
    out = {}
    for path in _mirror_files(os.path.join(root, MIRROR_REL)):
        try:
            tree = ast.parse(open(path, encoding="utf-8").read())
        except SyntaxError:
            continue
        imported = {}
        for n in tree.body:
            if isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
                cand = os.path.join(os.path.dirname(path), *n.module.split(".")) + ".py"
                for al in n.names:
                    imported[al.asname or al.name] = os.path.exists(cand)
        for n in tree.body:
            if not isinstance(n, ast.ClassDef) or n.name in out:
                continue
            bases = [b.id if isinstance(b, ast.Name) else b.attr
                     for b in n.bases if isinstance(b, (ast.Name, ast.Attribute))]
            meths = {c.name for c in n.body if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef))}
            ann = {c.target.id for c in n.body
                   if isinstance(c, ast.AnnAssign) and isinstance(c.target, ast.Name)}
            local = {c.name for c in tree.body if isinstance(c, ast.ClassDef)}
            vis = [b for b in bases if b in local or imported.get(b)]
            out[n.name] = (os.path.relpath(path, root), bases, meths, ann, vis)
    return out


def mirror_selected_in(cls, name, mclasses):
    """Mirror composites D whose UNIT applies `cls`'s declaration of `<name>` to D's own record:
    `cls` is D itself or a VISIBLE direct base of D, and among D followed by its visible direct
    bases (declaration order, the MRO restricted to what the unit sees) `cls` is the first that
    defines `<name>`. Measured: `Module6_WhyMLTranspiler`'s `_track_collection_metadata` val is
    minted from statements.py's declaration (StatementEmissionMixin precedes
    TypeInferenceMixin in the mirror composite's bases)."""
    sel = []
    for d, v in mclasses.items():
        if d == cls or cls not in v[4]:
            continue
        for k in [d] + v[4]:
            if k in mclasses and name in mclasses[k][2]:
                if k == cls:
                    sel.append(d)
                break
    return sorted(sel)


def composite_record(d, mclasses):
    """Approximate record of a composite's unit: its own annotated fields and those of its
    visible direct bases (the flattened union)."""
    v = mclasses.get(d)
    if not v:
        return set()
    out = set(v[3])
    for b in v[4]:
        if b in mclasses:
            out |= mclasses[b][3]
    return out
