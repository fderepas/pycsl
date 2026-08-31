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

THE CONVERTED SURFACE (added 2026-08-31, relaunch #19) -- THE PLANE'S OWN BLIND SPOT.
The check above was scoped to `\\trusted` stubs on the reasoning that a CONVERTED method
has a body, so Why3 checks its frame.  Measured against the emitted `.mlw`, that reasoning
is only half true, and the half that fails is the half that matters:

  - IN ITS OWN FILE a converted method really is checked.  Module 6 emits an explicit
    `writes {  }` for `#@ assigns \\nothing` (NOT an omitted clause), and Why3 rejects an
    under-declared frame -- confirmed by spike: an omitted `writes` is INFERRED and
    silently accepted, an explicit empty one raises `this expression produces an unlisted
    write effect`.  But what it is checked against is the EMITTED body, which is an
    ERASURE of the live one: the very calls that do the writing are commonly lowered to
    effect-free abstract `val`s, so `writes {  }` can be true of the emission and false of
    the source.
  - IN EVERY OTHER FILE the method appears as a caller-side abstract `val` minted from the
    SAME declared `#@ assigns` (e.g. `val self__seq_init_expr_3 ... writes {
    self._current_self_type, self._in_spec, self._string_local_vars }`).  That `val` has
    no body, so the frame is ASSUMED there exactly as a `\\trusted` stub's is -- and a
    converted method declaring a false `assigns \\nothing` hands every cross-file caller
    an unchecked "this field did not change".

So the converted population is the same hazard one step removed, and no plane sees it: the
fidelity gate compares bodies, not frames; the whole-file proof checks the erased emission;
the byte-diff and the vacuity probe are blind to it.  It is reported as a SECOND population
with its own two ratchets.  First measurement: 567 converted methods declare
`assigns \\nothing`, 69 stand for a live body that transitively writes `self` (12 directly),
2 MODEL-VISIBLE -- `ControlFlowStmtMixin._handle_return_stmt` (18 fields, via-callee) and
`proof2why3/parser.py::_Parser.__init__` (2 fields, direct; a constructor, so it belongs to
the constructor bucket the trusted plane also bottoms out in).

TABLE-AWARE DISPATCH (added 2026-08-31, relaunch #19) -- WHY THE NUMBERS WENT UP.
The call-graph walk resolved `self.<m>(...)` by attribute name only, so it could not see a
DISPATCHER: `handler = self._TABLE.get(type(node))` followed by `getattr(self, handler)(x)`
names its callee through a class-level dict literal.  That is precisely how the emitter's
`_csl_to_ir` / `_py_expr_to_ir` reach their handlers, so the analysis was blind to the
methods whose frames matter most.  Handler tables are now collected (class- and
module-level `NAME = {K: "method", ...}`) and an edge is added to every method a table
names -- but ONLY from a body that also performs a `getattr(self, ...)` call, so a body
that merely TESTS membership in a table contributes nothing.  Measured: every table edge in
the tree comes from a genuine dispatcher (tightening the rule changed no count).

The ratchets were RAISED to the new measurements -- 3/73 -> 6/76 trusted, 2/69 -> 63/130
converted.  That is a MEASUREMENT improvement, not a tree regression: the same tree was
always this dishonest, the gate could not see it.  The three NEW trusted model-visible
offenders (`_get_mutex_invariant_ir`, `_csl_list_to_ir`, `_py_stmts_to_ir`) and 60 of the
new converted ones are ONE fact: the whole `_csl_*` handler family declares
`#@ assigns \\nothing` while reaching `_csl_in`, which writes `self._fresh_var_counter` --
and `_csl_in`'s OWN mirror declares that write honestly.  This is the same `unlisted write
effect` the `_csl_to_ir` CERTIFIED-BOUNDARY already names as the first of its three
blockers; the gate now MEASURES it instead of only recording it in prose.

MODEL-VISIBILITY IS DECIDED BY THE EMITTED RECORD (added 2026-08-31, relaunch #19).
The tool now EMITS every mirror itself (~35 s, needs `why3` on PATH) and asks the direct
question: does this file's emitted `type <cls> = { ... }` actually DECLARE the field?  The
previous source-assignment heuristic -- "the mirror file assigns `self.<f>` somewhere" -- is
wrong in BOTH directions, and both were measured:
  - OVER: `ControlFlowStmtMixin._handle_return_stmt` was reported model-visible for
    `_comp_content_counter` / `_current_params` / `_current_self_type` /
    `_frame_trigger_active`, and the emitted `type controlflowstmtmixin` carries NONE of
    those four.  (It stays model-visible for a DIFFERENT pair, `_func_return_type` and
    `_in_spec`, which the record does carry -- so the verdict survives and its REASON does
    not.)
  - UNDER: `ExpressionEmissionMixin._ifexpr_seq_arm` was reported unmodelled and the
    emitted `type expressionemissionmixin` carries FOUR of its written fields.  That one
    raised CONVERTED_RATCHET from 2 to 3.
`--emit-dir DIR` reuses an existing emitted-mirror directory (either naming scheme);
`--no-emit` falls back to the heuristic and the ratchets then do NOT apply.

RATCHET.  The counts may go down, never up -- EXCEPT when the analysis itself gets sharper,
which must be stated in this docstring with what it newly sees, as the paragraph above does.
Lower them deliberately when a stub is converted or its `#@ assigns` is corrected.
"""
import argparse
import ast
import collections
import os
import re
import shutil
import sys
import tempfile

RATCHET = 3           # MODEL-VISIBLE offenders: `@mutable_state` class AND a modelled field
TOTAL_RATCHET = 73    # every offender, including opaque-self classes
CONVERTED_RATCHET = 3         # the CONVERTED surface, model-visible (see the note below)
CONVERTED_TOTAL_RATCHET = 69  # the CONVERTED surface, every offender
LIVE_ROOT = "src/pycsl"
MIRROR_ROOT = "src/self-annotate/src"


def _string_dict_tables(node):
    """Class- or module-level `NAME = {K: "method_name", ...}` handler tables.

    Returns {table_name: [method_name, ...]}.  A DISPATCHER resolves its callee through
    such a table plus `getattr(self, handler_name)`, which no attribute-based call-graph
    walk can see -- so without this the analysis silently misses exactly the methods that
    matter most.  Values may be plain string constants or `X.attr` spellings."""
    out = {}
    for member in node.body:
        if not isinstance(member, (ast.Assign, ast.AnnAssign)):
            continue
        val = member.value
        if not isinstance(val, ast.Dict):
            continue
        names = []
        for v in val.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                names.append(v.value)
            elif isinstance(v, ast.Attribute):
                names.append(v.attr)
        if not names:
            continue
        tgts = member.targets if isinstance(member, ast.Assign) else [member.target]
        for tgt in tgts:
            if isinstance(tgt, ast.Name):
                out[tgt.id] = names
    return out


def _parse_tree(root):
    """(classes, bases, funcs, tables) over every .py under `root`."""
    classes, funcs = {}, {}
    tables = {}
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
            tables.update(_string_dict_tables(tree))
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    funcs[(path, "", node.name)] = node
                elif isinstance(node, ast.ClassDef):
                    tables.update(_string_dict_tables(node))
                    classes[node.name] = path
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            bases[node.name].add(base.id)
                        elif isinstance(base, ast.Attribute):
                            bases[node.name].add(base.attr)
                    for member in node.body:
                        if isinstance(member, ast.FunctionDef):
                            funcs[(path, node.name, member.name)] = member
    return classes, bases, funcs, tables


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


def _self_write_fixpoint(classes, bases, funcs, tables=None):
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
        # TABLE-AWARE DISPATCH.  `handler = self._TABLE.get(type(x))` followed by
        # `getattr(self, handler)(...)` is invisible to the attribute walk above, and it is
        # exactly how the emitter's DISPATCHERS call their handlers -- the methods whose
        # frames matter most.  An edge is added to every method a table names ONLY when the
        # body ALSO performs a `getattr(self, ...)` call, which is the dispatch idiom; a
        # body that merely TESTS membership in a table gets no edges.
        _dyn_self = any(
            isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id == "getattr" and n.args
            and isinstance(n.args[0], ast.Name) and n.args[0].id == "self"
            for n in ast.walk(fn))
        if _dyn_self:
            for n in ast.walk(fn):
                tname = None
                if isinstance(n, ast.Attribute) and n.attr in (tables or {}):
                    tname = n.attr
                elif isinstance(n, ast.Name) and n.id in (tables or {}):
                    tname = n.id
                if tname:
                    for m in tables[tname]:
                        edges.add(("self", m))
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


def _emitted_record_fields(emit_dir, mirror_root):
    """PER MIRROR FILE and PER CLASS, the fields the EMITTED record actually declares.

    This is the DIRECT oracle for model-visibility, and it strictly refines the
    source-assignment heuristic below.  Module 5 does not promote every `self.<f> = ...`
    it sees into the emitted record -- it drops the ones it cannot type -- so a file can
    assign a field that its `.mlw` record does not carry, and a missing `writes` for such a
    field cannot mislead any prover.  MEASURED: `ControlFlowStmtMixin._handle_return_stmt`
    was reported MODEL-VISIBLE for `_comp_content_counter` / `_current_params` /
    `_current_self_type` / `_frame_trigger_active`, and the emitted
    `type controlflowstmtmixin = { ... }` carries NONE of the four.  Declaring the honest
    frame on it emits `writes {  }` unchanged, because the emitter filters the clause
    through the same record labels.

    `emit_dir` holds one `.mlw` per mirror, named by the mirror's repo-relative path with
    `/` replaced by `_` (what `scratchpad/w2/keepsweep.sh` produces).  Returns
    {mirror_path: {whyml_record_name: {field, ...}}}; a file with no entry falls back to
    the heuristic."""
    out = {}
    rec_re = re.compile(r"^  type ([a-z0-9_]+) = \{(.*?)\}", re.M)
    fld_re = re.compile(r"mutable ([A-Za-z_0-9]+):")
    for dirpath, _dirs, files in os.walk(mirror_root):
        if "__pycache__" in dirpath:
            continue
        for fname in sorted(files):
            if not fname.endswith(".py"):
                continue
            path = os.path.join(dirpath, fname)
            # Two naming schemes are in use for an emitted-mirror directory:
            # `scratchpad/w2/keepsweep.sh` keys by the REPO-relative path, while
            # `bin/check-shadowed-selfcalls.py --emit-dir` keys by the MIRROR-relative one.
            # Accept both, so either tool's output can be fed here.
            mlw = None
            for key in (path.replace(os.sep, "_") + ".mlw",
                        os.path.relpath(path, mirror_root)[:-3].replace(os.sep, "_") + ".mlw"):
                cand = os.path.join(emit_dir, key)
                if os.path.exists(cand):
                    mlw = cand
                    break
            if mlw is None:
                continue
            txt = open(mlw).read()
            out[path] = {m.group(1): set(fld_re.findall(m.group(2)))
                         for m in rec_re.finditer(txt)}
    return out


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


def _mirror_nothing_stubs(mirror_root, want_trusted=True):
    """Every mirror method that declares `#@ assigns \\nothing`.

    `want_trusted=True`  -> the `\\trusted` stubs (the ASSUMED-contract population).
    `want_trusted=False` -> the CONVERTED methods (the second population, see the
    CONVERTED SURFACE note in the module docstring)."""
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
                        if (trusted == want_trusted) and nothing:
                            out.append((path, cls, child.name))
            walk(tree, "")
    return out


def _emit_all(out_dir):
    """Emit every mirror's `.mlw` into `out_dir` (needs `why3` on PATH)."""
    import glob
    import subprocess
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    py = os.path.join(root, ".venv", "bin", "python3")
    if not os.path.exists(py):
        py = sys.executable
    env = dict(os.environ, PYTHONHASHSEED="0")
    for src in sorted(glob.glob(os.path.join(root, MIRROR_ROOT, "**", "*.py"),
                                recursive=True)):
        mlw = src[:-3] + ".mlw"
        if os.path.exists(mlw):
            os.remove(mlw)
        subprocess.run([py, os.path.join(root, "src", "pycsl", "pycsl.py"), src,
                        "--import-path", os.path.join(root, "src", "pycsl"),
                        "--no-proof", "--keep-mlw"],
                       cwd=root, env=env,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(mlw):
            rel = os.path.relpath(src, os.path.join(root, MIRROR_ROOT))
            shutil.move(mlw, os.path.join(out_dir, rel[:-3].replace(os.sep, "_") + ".mlw"))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", action="store_true",
                    help="list every offending stub with its transitive write set")
    ap.add_argument("--ratchet", type=int, default=RATCHET)
    ap.add_argument("--total-ratchet", type=int, default=TOTAL_RATCHET)
    ap.add_argument("--no-emit", action="store_true",
                    help="skip emission and fall back to the OVER/UNDER-approximating "
                         "source-assignment heuristic (the ratchets do NOT apply).")
    ap.add_argument("--emit-dir",
                    help="directory of emitted .mlw (scratchpad/w2/keepsweep.sh output). "
                         "With it, MODEL-VISIBLE is decided by the EMITTED record's fields "
                         "instead of the over-approximating source-assignment heuristic.")
    ap.add_argument("--converted-ratchet", type=int, default=CONVERTED_RATCHET)
    ap.add_argument("--converted-total-ratchet", type=int,
                    default=CONVERTED_TOTAL_RATCHET)
    args = ap.parse_args()

    classes, bases, funcs, tables = _parse_tree(LIVE_ROOT)
    direct, trans = _self_write_fixpoint(classes, bases, funcs, tables)

    ms_classes = _mutable_state_classes(MIRROR_ROOT)
    modelled = _mirror_modelled_fields(MIRROR_ROOT)
    _tmp = None
    _edir = args.emit_dir
    if _edir is None and not args.no_emit:
        _tmp = tempfile.mkdtemp(prefix="frame-honesty-")
        _emit_all(_tmp)
        _edir = _tmp
    emitted = _emitted_record_fields(_edir, MIRROR_ROOT) if _edir else {}
    if _tmp is not None:
        shutil.rmtree(_tmp, ignore_errors=True)

    def _visible(cls, path, writes):
        """Is a missing `writes` for any of `writes` something a prover can be misled by?

        With `--emit-dir` this is the DIRECT question: does the file's emitted record for
        `cls` declare the field?  Without it, fall back to the source-assignment heuristic,
        which OVER-APPROXIMATES (see `_emitted_record_fields`)."""
        if cls not in ms_classes:
            return False
        recs = emitted.get(path)
        if recs is not None:
            flds = recs.get(cls.lower())
            if flds is None:
                return False
            return any(w in flds for w in writes)
        return any(w in modelled.get(path, ()) for w in writes)

    def _population(want_trusted):
        stubs = _mirror_nothing_stubs(MIRROR_ROOT, want_trusted)
        offenders = []
        for path, cls, name in stubs:
            live_key = (LIVE_ROOT + path[len(MIRROR_ROOT):], cls, name)
            writes = trans.get(live_key)
            if writes:
                offenders.append((path, cls, name, sorted(writes),
                                  bool(direct.get(live_key)), path))
        visible = [o for o in offenders if _visible(o[1], o[5], o[3])]
        return stubs, offenders, visible

    def _report(tag, stubs, offenders, visible):
        n_direct = sum(1 for o in offenders if o[4])
        print("[*] %s: %d method(s) declare `#@ assigns \\nothing`; "
              "%d stand for a live body that transitively writes `self` state "
              "(%d write DIRECTLY); %d of those are MODEL-VISIBLE (`@mutable_state` class)."
              % (tag, len(stubs), len(offenders), n_direct, len(visible)))
        if args.verbose:
            for path, cls, name, writes, is_direct, _p in sorted(offenders,
                                                                 key=lambda o: -len(o[3])):
                rel = path[len(MIRROR_ROOT) + 1:]
                print("    %-40s %-44s %3d %-10s %-13s %s"
                      % (rel, (cls + "." + name if cls else name)[:44], len(writes),
                         "DIRECT" if is_direct else "via-callee",
                         "MODEL-VISIBLE" if _visible(cls, path, writes)
                         else "unmodelled", writes[:4]))

    rc = 0

    def _ratchet(tag, pairs, why):
        nonlocal rc
        for label, got, want in pairs:
            if got > want:
                print("[!] %s: %s RATCHET BROKEN — %d > %d. %s" % (tag, label, got, want, why))
                rc = 1
            elif got < want:
                print("[+] %s: %s %d < ratchet %d — lower the constant."
                      % (tag, label, got, want))

    t_stubs, t_off, t_vis = _population(True)
    _report("trusted-frame-honesty", t_stubs, t_off, t_vis)
    _ratchet("trusted-frame-honesty",
             (("model-visible", len(t_vis), args.ratchet),
              ("total", len(t_off), args.total_ratchet)),
             "A `\\trusted` stub's `assigns` is ASSUMED, never checked, so a false one is "
             "an unsoundness no proof plane can see.")

    c_stubs, c_off, c_vis = _population(False)
    _report("converted-frame-honesty", c_stubs, c_off, c_vis)
    _ratchet("converted-frame-honesty",
             (("model-visible", len(c_vis), args.converted_ratchet),
              ("total", len(c_off), args.converted_total_ratchet)),
             "A CONVERTED method's `writes {  }` is checked against the EMITTED body, "
             "which is an ERASURE of the live one — and every OTHER file's caller-side "
             "abstract `val` is minted from the same declared `assigns`, so it inherits "
             "the false frame UNCHECKED.")

    if rc == 0:
        print("[+] frame-honesty: OK (trusted ratchets %d/%d, converted ratchets %d/%d)."
              % (args.ratchet, args.total_ratchet,
                 args.converted_ratchet, args.converted_total_ratchet))
    return rc


if __name__ == "__main__":
    sys.exit(main())
