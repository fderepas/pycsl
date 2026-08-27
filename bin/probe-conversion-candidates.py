#!/usr/bin/env python3
r"""probe-conversion-candidates.py — measure whether a `\trusted` mirror stub would convert,
WITHOUT the L3-tc-only over-reporting that wall-lessons (hh) documents.

For each candidate it ports the LIVE body into the mirror un-trusted, emits the file,
classifies the result, and ALWAYS restores the tree (a `finally`, so an exception or a
Ctrl-C still restores). It NEVER leaves the tree dirty and NEVER commits anything.

VERDICTS
  CLEAN            L3-tc passes, the function is emitted as a real DEFINITION, and none of
                   the facade/erasure markers below fire. The only verdict worth acting on —
                   and still only a CANDIDATE: it does not run the proof, so a missing loop
                   invariant/variant still surfaces later (measured on `_with_parenthesized`).
  ERASURE          emitted as a definition, but a marker fired. Listed with the markers.
  VAL              silently re-abstracted by the auto-trust valve (wall-lessons (hh)).
  ABSENT           not emitted as a standalone function (dunders, constructors).
  L3TC-FAIL        does not type-check; the last emitter line is reported, and TABULATING
                   THOSE LINES ACROSS A WHOLE FILE IS THE POINT — it ranks the blockers.
  NO-TRUSTED-STUB  UNMEASURED, not clean: the stub is not in the canonical bodyless shape
                   (a `#@ \trusted` block directly above a `def` whose body is exactly
                   `pass` or a one-line `return`), so the harness declined to touch it.
                   Report it as coverage loss, never as a negative result. (4 of 178 on
                   `pure_ast.py`; several in `module6_whyml/identifiers.py`.)

CAVEAT — this is a CANDIDATE FILTER, not a gate. It ports the body VERBATIM with no added
annotations, so a stub that needs a `#@ loop invariant`, a `#@ \variant`, a return
annotation or a small emitter capability shows up as L3TC-FAIL/ERASURE even though it is
convertible. A CLEAN verdict still has to survive the real battery (proof, corpus byte-diff,
mirror emission diff, fidelity, `check-untrusted-emitted`).

MARKERS (the facade-detector list this campaign has paid for)
  - a 0-ARY opaque val `f ()` where the source passes an argument — INPUT-BLIND;
  - `isinstance_op 0 0` — both operands erased (wall-lessons (ff));
  - `iter_length 0` / `iter_get 0` — an iterable erased to a constant, so N distinct
    sequences collapse to one;
  - `= ref  in` — a call dropped entirely;
  - an opaque `get_<attr>` getter where a record field read was expected;
  - a 6+-digit literal — a STRING erased to its hash;
  - RESULT ERASURE — the body computes its locals faithfully and then returns a BARE
    LITERAL because the source's `return <constructed value>` had no lowering. This one is
    structural (compare the source's last statement with the emitted last expression) and it
    is the marker that caught `_import_as_name` / `_dotted_as_name` after the regex list had
    already called them CLEAN;
  - a `while` with no `variant` — L3-tc cannot see it, but the proof will fail.

Usage:  bin/probe-conversion-candidates.py <mirror.py> [Class:name | name ...]
        (no candidates => every `\trusted` stub in the file)
"""
import ast, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR_ROOT = os.path.join(ROOT, "src/self-annotate/src")
LIVE_ROOT = os.path.join(ROOT, "src/pycsl")
MIRROR = LIVE = MLW = None      # set from argv in main

# Facade / erasure markers, incl. the raise-side ones from lesson (qq).
MARKERS = [
    (r"\b\w+_0 \(\)", "0-ary opaque val (INPUT-BLIND)"),
    (r"isinstance_op 0 0", "isinstance facade"),
    (r"iter_length 0|iter_get 0", "iterable erased to a constant"),
    (r"= ref  in", "empty ref (call dropped)"),
    (r"\bget_[a-z_]+ ", "opaque attribute getter"),
    (r"[^\w](\d{6,})\b", "hashed literal (string erased to an int)"),
    (r"hasattr_check ", "hashed attribute name"),
]

def live_src(name, cls):
    src = open(LIVE).read(); lines = src.split("\n"); t = ast.parse(src)
    scopes = [t] + [n for n in ast.walk(t) if isinstance(n, ast.ClassDef)]
    for sc in scopes:
        if cls is not None and (not isinstance(sc, ast.ClassDef) or sc.name != cls):
            continue
        if cls is None and isinstance(sc, ast.ClassDef):
            continue
        for m in sc.body:
            if isinstance(m, ast.FunctionDef) and m.name == name:
                return "\n".join(lines[m.lineno-1:(m.body[-1].end_lineno or m.lineno)])
    return None

STUB = re.compile(r"^(?P<ind>[ \t]*)#@ \\trusted reviewer: pycsl-self-annotate\n"
                  r"(?P<cts>(?:[ \t]*#@ .*\n)*)"
                  r"(?P<ind2>[ \t]*)def (?P<name>\w+)\((?P<args>[^\n]*)\):\n"
                  r"(?P=ind2)    (?:pass|return .*)\n", re.M)

def probe(name, cls):
    orig = open(MIRROR).read()
    body = live_src(name, cls)
    if body is None:
        return name, "NO-LIVE-SOURCE", []
    hit = None
    for m in STUB.finditer(orig):
        if m.group("name") == name:
            hit = m; break
    if hit is None:
        return name, "NO-TRUSTED-STUB", []
    ind = hit.group("ind")
    ported = "\n".join((ind + l[4:] if l.startswith("    ") else ind + l)
                       for l in body.split("\n"))
    new = orig[:hit.start()] + hit.group("cts") + ported + "\n" + orig[hit.end():]
    try:
        open(MIRROR, "w").write(new)
        env = dict(os.environ, PATH="/home/fabrice/.opam/framac-coq8/bin:" + os.environ["PATH"],
                   PYTHONHASHSEED="0")
        r = subprocess.run([sys.executable, os.path.join(ROOT, "src/pycsl/pycsl.py"), MIRROR,
                            "--import-path", os.path.join(ROOT, "src/pycsl"),
                            "--no-proof", "--keep-mlw"],
                           capture_output=True, text=True, cwd=ROOT, env=env, timeout=300)
        if "L3-tc ✓" not in r.stdout:
            tail = [l for l in (r.stdout + r.stderr).split("\n") if l.strip()][-1:]
            return name, "L3TC-FAIL", tail
        txt = open(MLW).read() if os.path.exists(MLW) else ""
        pat = re.compile(r"^  (let(?: rec)?(?: function)?|val)\s+([A-Za-z0-9_]+)[^\n]*\n(?:(?!^  (?:let|val|type|exception|axiom|goal|lemma)\b).*\n)*", re.M)
        blk = None; kind = None
        for m in pat.finditer(txt):
            n = m.group(2)
            if n == name or n.endswith("_" + name) or n.endswith(name):
                kind, blk = m.group(1), m.group(0); break
        if blk is None:
            return name, "ABSENT", []
        if kind == "val":
            return name, "VAL(re-abstracted)", []
        found = [d for rx, d in MARKERS if re.search(rx, blk)]
        # RESULT ERASURE (the defect the marker list missed on `_import_as_name` /
        # `_dotted_as_name`): the body computes its locals faithfully and then RETURNS A
        # BARE LITERAL, because the source's `return <constructed value>` had no lowering.
        # The emitted function is then a constant on its return value while still looking
        # like real work. Detected structurally: the source's last statement is a `return`
        # of something that is NOT a literal, but the emitted body's final expression IS a
        # bare literal.
        blines = [l for l in blk.rstrip().split("\n") if l.strip()]
        last = blines[-1].strip() if blines else ""
        src_t = ast.parse("\n".join(l[4:] if l.startswith("    ") else l
                                     for l in body.split("\n")))
        src_fn = src_t.body[0]
        src_last = src_fn.body[-1]
        src_returns_value = (isinstance(src_last, ast.Return) and src_last.value is not None
                             and not isinstance(src_last.value, ast.Constant))
        if src_returns_value and re.fullmatch(r'(0|""|Seq\.empty|\(\)|None)', last):
            found.append(f"RESULT ERASURE (returns bare `{last}`)")
        # A `while` with no `variant` cannot discharge termination at proof time; L3-tc
        # alone will not show it (measured on `_dotted_as_name`).
        if re.search(r"^\s*while ", blk, re.M) and "variant" not in blk:
            found.append("while without a variant (termination will fail)")
        return name, ("CLEAN" if not found else "ERASURE"), found
    finally:
        open(MIRROR, "w").write(orig)
        if os.path.exists(MLW):
            os.remove(MLW)

def all_trusted(path):
    """Every `\trusted` stub in the mirror file, as (class, name)."""
    import re as _re
    src = open(path).read(); lines = src.split("\n"); t = ast.parse(src)
    mk = _re.compile(r"^#@\s*\\trusted\b")
    def tr(n):
        i = n.lineno - 2
        while i >= 0:
            l = lines[i].strip()
            if l.startswith("#@") or l.startswith("#") or l.startswith("@") or l == "":
                if mk.match(l):
                    return True
                i -= 1
                continue
            return False
        return False
    out = []
    for c in ast.walk(t):
        if isinstance(c, ast.ClassDef):
            for m in c.body:
                if isinstance(m, ast.FunctionDef) and tr(m) and m.name != "__init__":
                    out.append((c.name, m.name))
    for m in t.body:
        if isinstance(m, ast.FunctionDef) and tr(m):
            out.append((None, m.name))
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    MIRROR = os.path.abspath(sys.argv[1])
    rel = os.path.relpath(MIRROR, MIRROR_ROOT)
    LIVE = os.path.join(LIVE_ROOT, rel)
    MLW = MIRROR[:-3] + ".mlw"
    if not os.path.exists(LIVE):
        print(f"[!] no live counterpart for {rel}")
        raise SystemExit(2)
    cands = []
    for a in sys.argv[2:]:
        cands.append(tuple(a.split(":")) if ":" in a else (None, a))
    if not cands:
        cands = all_trusted(MIRROR)
    for cls, nm in cands:
        n, verdict, extra = probe(nm, cls or None)
        print(f"{verdict:20s} {cls or '<module>'}.{n}  {extra if extra else ''}")
