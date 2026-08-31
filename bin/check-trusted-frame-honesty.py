#!/usr/bin/env python3
"""check-trusted-frame-honesty — the FOURTH plane of the self-annotation gate battery.

WHAT IT MEASURES.  A `\\trusted` mirror stub's contract is ASSUMED, never checked: Module 6
emits it as an abstract `val` and Why3 takes it on faith.  So a stub that declares
`#@ assigns \\nothing` while the LIVE method it stands for really does mutate `self` state
states something FALSE, and every converted caller is entitled to assume the field is
unchanged across the call.  That is an unsoundness the proof planes cannot see: the
whole-file proof is GREEN, the corpus byte-diff is 0, and the mirror-sync gate is happy,
because a `\\trusted` stub HAS no body to check the claim against.

This is the trusted-surface twin of the CONVERTED-body frame gap that the object-state
write model closed (`module6_whyml/abstract_ops.py::_add_abstract_op`): there, an abstract
`setattr_*` had no effect, so a mutating body satisfied `assigns \\nothing` vacuously, and
Why3 now rejects it.  Here there is no body at all, so only this static check can see it.

HOW.  Parse the live tree, compute each function's DIRECT `self.<attr> = ...` stores, then
propagate along the call graph to a fixpoint.  `self.<m>()` resolves inside the caller's
class, its transitive bases, and — when the caller is itself a MIXIN — the bases of every
composite that mixes it in (so a mixin calling a sibling mixin resolves, while two
unrelated SUBCLASSES of a common base do not bleed into each other).  Module-level calls
resolve within the same file.  The analysis is an OVER-approximation of the call graph and
an UNDER-approximation of the mutation set (it does not model aliasing or `setattr()`), so
the number it reports is a LOWER BOUND on the false-frame surface.

TWO NUMBERS, AND THE SECOND IS THE ONE THAT BITES.  The headline count is every offending
stub.  The RATCHETED count is the subset whose class is `@mutable_state`, i.e. whose `self`
is emitted as a Why3 RECORD WITH REAL FIELDS: only there can a converted caller actually
READ the field and rely on the missing `writes`.  For an opaque-self class the field is not
modelled at all (reads go through unconstrained `getattr_*` oracles), so the annotation is
dishonest to a HUMAN reader but the model claims nothing false.  Correcting one of those is
cosmetic; correcting a `@mutable_state` one changes the emitted `val` and can break a caller
that was relying on the false assumption — which is exactly the point of finding it.

RATCHET.  The counts may go down, never up.  Lower them deliberately when a stub is
converted or its `#@ assigns` is corrected.
"""
import argparse
import ast
import collections
import os
import sys

RATCHET = 7           # MODEL-VISIBLE offenders: `@mutable_state` class AND a modelled field
TOTAL_RATCHET = 77    # every offender, including opaque-self classes
LIVE_ROOT = "src/pycsl"
MIRROR_ROOT = "src/self-annotate/src"


def _parse_tree(root):
    """(classes, bases, funcs) over every .py under `root`."""
    classes, funcs = {}, {}
    bases = collections.defaultdict(set)
    for dirpath, _dirs, files in os.walk(root):
        if "__pycache__" in dirpath:
            continue
        for fname in sorted(files):
            if not fname.endswith(".py"):
                continue
            path = os.path.join(dirpath, fname)
            try:
                tree = ast.parse(open(path).read())
            except (OSError, SyntaxError):
                continue
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    funcs[(path, "", node.name)] = node
                elif isinstance(node, ast.ClassDef):
                    classes[node.name] = path
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            bases[node.name].add(base.id)
                        elif isinstance(base, ast.Attribute):
                            bases[node.name].add(base.attr)
                    for member in node.body:
                        if isinstance(member, ast.FunctionDef):
                            funcs[(path, node.name, member.name)] = member
    return classes, bases, funcs


def _transitive_bases(cls, bases, seen=None):
    seen = set() if seen is None else seen
    out = set()
    for base in bases.get(cls, ()):
        if base in seen:
            continue
        seen.add(base)
        out.add(base)
        out |= _transitive_bases(base, bases, seen)
    return out


def _self_write_fixpoint(classes, bases, funcs):
    tbases = {c: _transitive_bases(c, bases) for c in classes}
    descendants = collections.defaultdict(set)
    for cls in classes:
        for base in tbases[cls]:
            descendants[base].add(cls)
    resolvable = {}
    for cls in classes:
        scope = {cls} | tbases[cls]
        for sub in descendants[cls]:          # cls is a MIXIN of `sub`
            scope |= {sub} | tbases[sub]
        resolvable[cls] = scope

    by_name = collections.defaultdict(list)
    for key in funcs:
        by_name[key[2]].append(key)

    direct, calls = {}, {}
    for key, fn in funcs.items():
        direct[key] = {
            n.attr for n in ast.walk(fn)
            if isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store)
            and isinstance(n.value, ast.Name) and n.value.id == "self"
        }
        edges = set()
        for n in ast.walk(fn):
            if not isinstance(n, ast.Call):
                continue
            target = n.func
            if (isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name)
                    and target.value.id == "self"):
                edges.add(("self", target.attr))
            elif isinstance(target, ast.Name):
                edges.add(("mod", target.id))
        calls[key] = edges

    def targets(key, kind, name):
        path, cls, _ = key
        out = []
        for cand in by_name.get(name, ()):
            cpath, ccls, _ = cand
            if kind == "self":
                if ccls and cls and ccls in resolvable.get(cls, {cls}):
                    out.append(cand)
            elif ccls == "" and cpath == path:
                out.append(cand)
        return out

    trans = {k: set(v) for k, v in direct.items()}
    for _ in range(50):
        changed = False
        for key in funcs:
            acc = set(trans[key])
            for kind, name in calls[key]:
                for tgt in targets(key, kind, name):
                    acc |= trans[tgt]
            if acc != trans[key]:
                trans[key] = acc
                changed = True
        if not changed:
            break
    return direct, trans


def _mirror_modelled_fields(mirror_root):
    """PER MIRROR FILE, the `self.<f>` names that file itself assigns.

    Module 5 registers a record field from an assignment IN THE FILE BEING EMITTED, and
    each mirror file is transpiled on its own, so the question "can a converted caller read
    this field?" is a PER-FILE question.  Two coarser tests were tried and both
    over-counted: the raw offender list rewards a purely cosmetic annotation fix on an
    opaque-self class, and a repo-wide field set still counts a class the file emits as
    `type <cls> = int` (measured: `GhostSpecOpsMixin` is decorated `@mutable_state` and its
    own `.mlw` still declares `type ghostspecopsmixin = int`, so a `writes { self._f }` on
    its val is an UNBOUND SYMBOL, not a frame).  A field the emitting file never assigns is
    not part of that file's record, so a missing `writes` for it cannot mislead the prover.
    """
    out = collections.defaultdict(set)
    for dirpath, _dirs, files in os.walk(mirror_root):
        if "__pycache__" in dirpath:
            continue
        for fname in sorted(files):
            if not fname.endswith(".py"):
                continue
            path = os.path.join(dirpath, fname)
            try:
                tree = ast.parse(open(path).read())
            except (OSError, SyntaxError):
                continue
            for n in ast.walk(tree):
                if (isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store)
                        and isinstance(n.value, ast.Name) and n.value.id == "self"):
                    out[path].add(n.attr)
    return out


def _mutable_state_classes(mirror_root):
    """Mirror classes decorated `@mutable_state` — the ones whose `self` becomes a Why3
    record with real, caller-readable fields."""
    out = set()
    for dirpath, _dirs, files in os.walk(mirror_root):
        if "__pycache__" in dirpath:
            continue
        for fname in sorted(files):
            if not fname.endswith(".py"):
                continue
            try:
                tree = ast.parse(open(os.path.join(dirpath, fname)).read())
            except (OSError, SyntaxError):
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                for dec in node.decorator_list:
                    name = (dec.id if isinstance(dec, ast.Name)
                            else dec.attr if isinstance(dec, ast.Attribute) else None)
                    if name == "mutable_state":
                        out.add(node.name)
    return out


def _mirror_nothing_stubs(mirror_root):
    """Every `\\trusted` mirror stub that declares `#@ assigns \\nothing`."""
    out = []
    for dirpath, _dirs, files in os.walk(mirror_root):
        if "__pycache__" in dirpath:
            continue
        for fname in sorted(files):
            if not fname.endswith(".py"):
                continue
            path = os.path.join(dirpath, fname)
            src = open(path).read()
            lines = src.splitlines()
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue

            def walk(node, cls):
                for child in node.body:
                    if isinstance(child, ast.ClassDef):
                        walk(child, child.name)
                    elif isinstance(child, ast.FunctionDef):
                        first = (min(d.lineno for d in child.decorator_list)
                                 if child.decorator_list else child.lineno) - 1
                        i = first - 1
                        trusted = nothing = False
                        while i >= 0 and (lines[i].strip().startswith("#")
                                          or lines[i].strip() == ""):
                            stripped = lines[i].lstrip()
                            # LINE PREFIX, never substring: a prose mention of the marker
                            # inside a comment block must not count.
                            if stripped.startswith("#@") and "\\trusted" in stripped:
                                trusted = True
                            if stripped == "#@ assigns \\nothing":
                                nothing = True
                            i -= 1
                        if trusted and nothing:
                            out.append((path, cls, child.name))
            walk(tree, "")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", action="store_true",
                    help="list every offending stub with its transitive write set")
    ap.add_argument("--ratchet", type=int, default=RATCHET)
    ap.add_argument("--total-ratchet", type=int, default=TOTAL_RATCHET)
    args = ap.parse_args()

    classes, bases, funcs = _parse_tree(LIVE_ROOT)
    direct, trans = _self_write_fixpoint(classes, bases, funcs)

    stubs = _mirror_nothing_stubs(MIRROR_ROOT)
    offenders = []
    for path, cls, name in stubs:
        live_key = (LIVE_ROOT + path[len(MIRROR_ROOT):], cls, name)
        writes = trans.get(live_key)
        if writes:
            offenders.append((path, cls, name, sorted(writes),
                              bool(direct.get(live_key)), path))

    ms_classes = _mutable_state_classes(MIRROR_ROOT)
    modelled = _mirror_modelled_fields(MIRROR_ROOT)
    visible = [o for o in offenders
               if o[1] in ms_classes and any(w in modelled.get(o[5], ()) for w in o[3])]
    n_direct = sum(1 for o in offenders if o[4])
    print("[*] trusted-frame-honesty: %d `\\trusted` stub(s) declare `#@ assigns \\nothing`; "
          "%d stand for a live body that transitively writes `self` state "
          "(%d write DIRECTLY); %d of those are MODEL-VISIBLE (`@mutable_state` class)."
          % (len(stubs), len(offenders), n_direct, len(visible)))
    if args.verbose:
        for path, cls, name, writes, is_direct, _p in sorted(offenders, key=lambda o: -len(o[3])):
            rel = path[len(MIRROR_ROOT) + 1:]
            print("    %-40s %-44s %3d %-10s %-13s %s"
                  % (rel, (cls + "." + name if cls else name)[:44], len(writes),
                     "DIRECT" if is_direct else "via-callee",
                     "MODEL-VISIBLE" if (cls in ms_classes
                                        and any(w in modelled.get(path, ()) for w in writes))
                     else "unmodelled", writes[:4]))
    rc = 0
    for label, got, want in (("model-visible", len(visible), args.ratchet),
                             ("total", len(offenders), args.total_ratchet)):
        if got > want:
            print("[!] trusted-frame-honesty: %s RATCHET BROKEN — %d > %d. A `\\trusted` "
                  "stub's `assigns` is ASSUMED, never checked, so a false one is an "
                  "unsoundness no proof plane can see." % (label, got, want))
            rc = 1
        elif got < want:
            print("[+] trusted-frame-honesty: %s %d < ratchet %d — lower the constant."
                  % (label, got, want))
    if rc == 0:
        print("[+] trusted-frame-honesty: OK (model-visible ratchet %d, total ratchet %d)."
              % (args.ratchet, args.total_ratchet))
    return rc


if __name__ == "__main__":
    sys.exit(main())
