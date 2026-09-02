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
import ast, os, re, subprocess, sys, textwrap


def _textwrap_dedent(t):
    return textwrap.dedent(t)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR_ROOT = os.path.join(ROOT, "src/self-annotate/src")
LIVE_ROOT = os.path.join(ROOT, "src/pycsl")
MIRROR = LIVE = MLW = None      # set from argv in main

# Facade / erasure markers, incl. the raise-side ones from lesson (qq).
MARKERS = [
    # ANY zero-argument opaque call, not just the `_0`-suffixed spelling. `PyCSLError.message`
    # emitted `(str_dunder_op ())` for `super().__str__()` — input-blind, and the `_0` pattern
    # missed it. `()` as a Why3 unit ARGUMENT is what makes this a facade; a genuine unit-typed
    # local or a `let _ = ... in ()` sequencing point is excluded by requiring the call to be
    # the whole parenthesised expression.
    (r"\(\s*[a-z_]\w* \(\)\s*\)", "0-ary opaque call (INPUT-BLIND)"),
    (r"isinstance_op 0 0", "isinstance facade"),
    (r"iter_length 0|iter_get 0", "iterable erased to a constant"),
    (r"= ref  in", "empty ref (call dropped)"),
    (r"\bget_[a-z_]+ ", "opaque attribute getter"),
    (r"[^\w](\d{6,})\b", "hashed literal (string erased to an int)"),
    (r"hasattr_check ", "hashed attribute name"),
    # (#31) A COMPREHENSION / GENERATOR ERASED TO A CONSTANT ARRAY. `any(<genexpr>)` and
    # `all(<genexpr>)` have no lowering, so the emitter applies the opaque `any_1`/`all_1`
    # to a FRESH CONSTANT `(Array.make 1 0)` — the generator, and every variable it reads,
    # is gone. Measured on `proof2why3.from_sexp._find_construct_idx`, which the repaired
    # signature-preserving port reported CLEAN: its whole discriminating test is
    # `any(... x[0] == "MutInd" ...)` and it emitted `any_1 (Array.make 1 0)`. Keyed on an
    # ARITY-SUFFIXED abstract op applied to a constant array, so the legitimate array-local
    # initialiser `let a = (Array.make 1024 0) in` is untouched.
    (r"[a-z_]\w*_\d+ \(Array\.make \d+ 0\)", "comprehension erased to a constant array"),
]

def _param_names(fn):
    a = fn.args
    return ([x.arg for x in a.posonlyargs] + [x.arg for x in a.args]
            + ([a.vararg.arg] if a.vararg else [])
            + [x.arg for x in a.kwonlyargs]
            + ([a.kwarg.arg] if a.kwarg else []))


def _find_live_fn(name, cls):
    src = open(LIVE).read(); lines = src.split("\n"); t = ast.parse(src)
    scopes = [t] + [n for n in ast.walk(t) if isinstance(n, ast.ClassDef)]
    for sc in scopes:
        if cls is not None and (not isinstance(sc, ast.ClassDef) or sc.name != cls):
            continue
        if cls is None and isinstance(sc, ast.ClassDef):
            continue
        for m in sc.body:
            if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name == name:
                return m, lines
    return None, lines


def live_src(name, cls):
    """The live `def` line(s) PLUS body, as one block (the legacy whole-def port)."""
    m, lines = _find_live_fn(name, cls)
    if m is None:
        return None
    return "\n".join(lines[m.lineno - 1:(m.body[-1].end_lineno or m.lineno)])


def live_body(name, cls):
    """(body_text, param_names) — the live body WITHOUT its `def` header.

    HARNESS FIX (#31), and it is the largest one this instrument has had. The port
    replaced the mirror's `def` line with the LIVE one, DISCARDING the mirror's signature.
    But the mirror's signature is not decoration: 188 of 466 `\trusted` stubs (40%) carry a
    REFINED model annotation the live source does not have — `val_ir: "ExprIR"` where live
    says `Dict[str, Any]`, `node: "Name"`, `rec: Dict[str, PyVal]` where live says `dict`,
    `-> "List[ExprIR]"` where live has no return annotation at all. Those annotations are
    exactly what selects the emit_ir reflection, the record projection and the typed return,
    and a REAL conversion keeps them (it deletes the `#@ \trusted` line and swaps the body,
    it does not rewrite the signature). By porting the live header the probe measured a
    DIFFERENT function from the one a conversion produces — and it measured it as the
    un-annotated, int-erased one, i.e. systematically HARDER. Every `Map.get val_ir "type"`
    verdict in the 2026-09-02 census is an artefact of this."""
    m, lines = _find_live_fn(name, cls)
    if m is None:
        return None, None
    start = m.body[0].lineno - 1
    end = m.body[-1].end_lineno or m.lineno
    return "\n".join(lines[start:end]), _param_names(m)

def stub_span(mirror_src, name, cls):
    r"""Locate the `\trusted` stub for `cls.name` in the mirror, AST-first.

    Returns `(start_line, end_line, kept_block)` as 0-based inclusive line indices covering
    the marker line through the end of the `def`, plus the `#@`/comment/decorator lines to
    KEEP (everything in the block except the `\trusted` marker itself). Returns None if the
    function is absent or carries no marker.

    AST-based rather than a body regex because the mirror is HETEROGENEOUS: some stubs are
    bodyless (`pass` / a one-line `return`), some carry the REAL live body under the marker
    (`pycsl.py`, `audit_proof_reverify.py`, `Module6_WhyMLTranspiler.py`, `statements.py` —
    67+ functions), and decorators (`@staticmethod`, `@property`) sit between the block and
    the `def`. A regex over the body shape silently missed every one of those as
    NO-TRUSTED-STUB."""
    lines = mirror_src.split("\n")
    tree = ast.parse(mirror_src)
    target = None
    scopes = [(None, tree)] + [(c.name, c) for c in ast.walk(tree)
                               if isinstance(c, ast.ClassDef)]
    for scope_name, sc in scopes:
        if scope_name != cls:
            continue
        for m in sc.body:
            if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name == name:
                target = m
                break
        if target is not None:
            break
    if target is None:
        return None
    first = target.decorator_list[0].lineno - 1 if target.decorator_list else target.lineno - 1
    i = first - 1
    marker = None
    kept = []
    while i >= 0:
        st = lines[i].strip()
        if st.startswith("#@") or st.startswith("#") or st.startswith("@") or st == "":
            if MARKER_RE.match(st):
                marker = i
                break
            kept.append(lines[i])
            i -= 1
            continue
        break
    if marker is None:
        return None
    kept.reverse()
    end = (target.end_lineno or target.lineno) - 1
    # The mirror's own `def` header — from the `def` line through the last line before the
    # first body statement — and its parameter names. Kept verbatim by the port so the
    # mirror's MODEL ANNOTATIONS survive (see `live_body`).
    hdr_start = target.lineno - 1
    hdr_end = target.body[0].lineno - 1          # exclusive
    header = lines[hdr_start:hdr_end]
    return marker, end, kept, header, _param_names(target), hdr_start


MARKER_RE = re.compile(r"^#@\s*\\trusted\b")


def probe(name, cls):
    orig = open(MIRROR).read()
    body = live_src(name, cls)
    if body is None:
        return name, "NO-LIVE-SOURCE", []
    span = stub_span(orig, name, cls)
    if span is None:
        return name, "NO-TRUSTED-STUB", []
    marker_i, end_i, kept, m_header, m_params, hdr_i = span
    lines = orig.split("\n")
    ind = lines[marker_i][:len(lines[marker_i]) - len(lines[marker_i].lstrip())]
    # (#31) SIGNATURE-PRESERVING PORT. Keep the MIRROR's `def` header (its model
    # annotations select the emit_ir reflection, the record projection and the typed
    # return) and splice in the LIVE BODY — which is exactly what a real conversion does.
    # Requires the two parameter LISTS to agree; when they do not, the mirror stub is a
    # different function from the live one and the honest report is the legacy whole-def
    # port, flagged so the divergence is visible rather than silent.
    _lbody, _lparams = live_body(name, cls)
    _sig_note = []
    if _lbody is not None and _lparams is not None and _lparams == m_params:
        _hind = m_header[0][:len(m_header[0]) - len(m_header[0].lstrip())]
        _bl = _lbody.split("\n")
        _bind = _bl[0][:len(_bl[0]) - len(_bl[0].lstrip())] if _bl else ""
        _want = _hind + "    "
        _bodyp = "\n".join((_want + l[len(_bind):] if l.startswith(_bind)
                            else _want + l.lstrip()) if l.strip() else l
                           for l in _bl)
        ported = "\n".join([(ind + h[len(_hind):] if h.startswith(_hind) else ind + h.lstrip())
                            for h in m_header]
                           + [(ind + l[len(_hind):] if l.startswith(_hind) else l)
                              for l in _bodyp.split("\n")])
        new = "\n".join(lines[:marker_i] + kept + ported.split("\n") + lines[end_i + 1:])
        return _probe_emit(name, cls, orig, new, _sig_note)
    if _lparams is not None and _lparams != m_params:
        _sig_note = [f"PARAM-LIST DIVERGES mirror={m_params} live={_lparams}"]
    # HARNESS BUG, FOUND AND FIXED 2026-09-01 (#29). The re-indentation stripped a FIXED
    # four spaces from every body line and then prefixed the MIRROR stub's indentation.
    # For a METHOD (mirror `ind` = 4 spaces, live body indented 4) that is the identity.
    # For a MODULE-LEVEL function the mirror `ind` is EMPTY, so the strip flattened the
    # whole body to column 0 and the ported file did not even PARSE — the harness then
    # reported the SyntaxError as `L3TC-FAIL  ['expected an indented block (got …)']`,
    # i.e. as a real conversion blocker. MEASURED BLAST RADIUS: 133 of the 352 L3TC-FAIL
    # verdicts across the whole mirror tree (38%) were this bug, not a blocker — every
    # module-level `\trusted` stub in `pycsl.py` (29), `ir_resolve.py` (15),
    # `monomorphize.py` (14), `audit_proof.py` (12), `audit_proof_reverify.py` (11),
    # `canonical.py` (11), `sertop.py` (6), `normalize.py` (6) and more.
    # Re-indent RELATIVE to the live def's own indentation instead.
    _blines = body.split("\n")
    _lind = _blines[0][:len(_blines[0]) - len(_blines[0].lstrip())] if _blines else ""
    ported = "\n".join((ind + l[len(_lind):] if l.startswith(_lind) else ind + l.lstrip())
                       if l.strip() else l
                       for l in _blines)
    new = "\n".join(lines[:marker_i] + kept + ported.split("\n") + lines[end_i + 1:])
    return _probe_emit(name, cls, orig, new, _sig_note)


def _probe_emit(name, cls, orig, new, sig_note):
    body = live_src(name, cls) or ""
    try:
        open(MIRROR, "w").write(new)
        env = dict(os.environ, PATH="/home/fabrice/.opam/framac-coq8/bin:" + os.environ["PATH"],
                   PYTHONHASHSEED="0")
        r = subprocess.run([sys.executable, os.path.join(ROOT, "src/pycsl/pycsl.py"), MIRROR,
                            "--import-path", os.path.join(ROOT, "src/pycsl"),
                            "--no-proof", "--keep-mlw"],
                           capture_output=True, text=True, cwd=ROOT, env=env, timeout=300)
        if "L3-tc ✓" not in r.stdout:
            # HARNESS FIX (#29): "the last non-empty line" is NOT the diagnosis. why3
            # prints its `File "…", line N` locator BEFORE the message and a long tail of
            # `Warning, … unused variable` lines can follow, and the pipeline's own
            # traceback echoes a SOURCE line last — so the recorded reason was frequently
            # an unrelated fragment (`_union_c8_walk(s.get("body", …))` was reported as the
            # blocker for 126 candidates across the tree). Prefer the first line that
            # actually reads like a diagnosis, and fall back to the tail only if none does.
            _ls = [l for l in (r.stdout + r.stderr).split("\n") if l.strip()]
            _DIAG_RE = (r"but is expected to have type|unbound |syntax error|"
                        r"cannot be used as pure|cannot be applied|This pattern has type|"
                        r"expected an indented block|not supported|Unsupported|"
                        r"rejected under|UnsupportedFeature|Error:")
            # HARNESS FIX (#31): why3 WRAPS a type-mismatch diagnosis across physical lines,
            # so the FIRST line matching the pattern is often the CONTINUATION
            # (`but is expected to have type int`) while the informative half
            # (`This expression has type <T>,`) sits on the line above. Measured on the
            # 2026-09-02 whole-tree census: 76 of 385 L3TC-FAIL verdicts -- 20% -- recorded a
            # blocker carrying NO source type, which silently MERGES unrelated families in the
            # ranked blocker census the ladder navigates by. Rebuild the wrapped paragraph by
            # walking back to the diagnosis opener (bounded, and never past the `File "..."`
            # locator why3 prints ahead of every message).
            _idx = [i for i, l in enumerate(_ls) if re.search(_DIAG_RE, l)]
            if _idx:
                i = _idx[0]
                j = i
                while (j > 0 and i - j < 4
                       and not re.match(r'^\s*File "', _ls[j - 1])
                       and not re.match(r"^\s*(This expression has type|This pattern has type|"
                                        r"This function |Error:)", _ls[j])):
                    j -= 1
                tail = [" ".join(l.strip() for l in _ls[j:i + 1])]
            else:
                tail = _ls[-1:]
            return name, "L3TC-FAIL", sig_note + tail
        txt = open(MLW).read() if os.path.exists(MLW) else ""
        pat = re.compile(r"^  (let(?: rec)?(?: function)?|val)\s+([A-Za-z0-9_]+)[^\n]*\n(?:(?!^  (?:let|val|type|exception|axiom|goal|lemma)\b).*\n)*", re.M)
        blk = None; kind = None
        for m in pat.finditer(txt):
            n = m.group(2)
            if n == name or n.endswith("_" + name) or n.endswith(name):
                kind, blk = m.group(1), m.group(0); break
        if blk is None:
            return name, "ABSENT", sig_note
        if kind == "val":
            return name, "VAL(re-abstracted)", sig_note
        found = list(sig_note) + [d for rx, d in MARKERS if re.search(rx, blk)]
        # YIELD ERASURE (#31). Module 6 has no generator model: `yield <v>` lowers to
        # `let _ = 0 in ()` and the surrounding `def` is emitted as an ordinary function,
        # so a generator's ENTIRE meaning — the sequence it produces — vanishes while the
        # emitted body still looks like real work. `pure_ast.iter_child_nodes` was banked
        # as a conversion in relaunch #30 in exactly that state, and NOTHING in this
        # marker list saw it. Structural, from the LIVE source: a value-carrying `yield`
        # whose emitted counterpart is `unit`-returning or contains the dropped-value
        # placeholder. The gate that ENFORCES this is `bin/check-yield-erasure.py`; this
        # marker keeps a generator from ever being reported CLEAN here first.
        try:
            _lt = ast.parse(body if body.startswith("def") else _textwrap_dedent(body))
        except Exception:
            _lt = None
        if _lt is not None:
            _vy = 0
            for _fn in _lt.body:
                if not isinstance(_fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                _stack = list(_fn.body)
                while _stack:
                    _n = _stack.pop()
                    if isinstance(_n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                        continue
                    if isinstance(_n, ast.Yield) and _n.value is not None:
                        _vy += 1
                    elif isinstance(_n, ast.YieldFrom):
                        _vy += 1
                    for _c in ast.iter_child_nodes(_n):
                        _stack.append(_c)
            if _vy and (blk.split("\n")[0].rstrip().endswith(": unit")
                        or "let _ = 0 in ()" in blk):
                found.append(f"YIELD ERASURE ({_vy} value-yield(s) dropped)")
        # RESULT ERASURE (the defect the marker list missed on `_import_as_name` /
        # `_dotted_as_name`): the body computes its locals faithfully and then RETURNS A
        # BARE LITERAL, because the source's `return <constructed value>` had no lowering.
        # The emitted function is then a constant on its return value while still looking
        # like real work. Detected structurally: the source's last statement is a `return`
        # of something that is NOT a literal, but the emitted body's final expression IS a
        # bare literal.
        blines = [l for l in blk.rstrip().split("\n") if l.strip()]
        last = blines[-1].strip() if blines else ""
        # SAME HARNESS BUG as the re-indentation above (#29): a fixed 4-space strip
        # flattens a MODULE-LEVEL live body to column 0 and this `ast.parse` raises
        # IndentationError, which is NOT caught — it aborted the whole sweep partway
        # through `pycsl.py` and `ir_resolve.py`. Dedent relative to the live def's own
        # indentation instead.
        _sl = body.split("\n")
        _si = _sl[0][:len(_sl[0]) - len(_sl[0].lstrip())] if _sl else ""
        src_t = ast.parse("\n".join((l[len(_si):] if l.startswith(_si) else l.lstrip())
                                     if l.strip() else l
                                     for l in _sl))
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
        # SELF-FIELD / PARAM ERASURE — the structural input-blindness check, and the one
        # that caught the SECOND round of false CLEANs. `ReverifyReport.ok` reads
        # `self.qualname_results` and emitted `all_1 (Array.make 1 0)`: the container was
        # replaced by a freshly-built constant, so the field vanished from the body
        # entirely. Any self-field or parameter the SOURCE reads must APPEAR in the
        # emitted body; the emitter renames (`self.f` -> `self.f`, params keep their name
        # or gain a `v_` prefix), so a substring test is the right granularity.
        reads = {n.attr for n in ast.walk(src_fn)
                 if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
                 and n.value.id == "self"}
        gone = sorted(f for f in reads if f not in blk)
        if gone:
            found.append(f"SELF-FIELD ERASURE (read in source, absent from body: {gone})")
        params = [a.arg for a in src_fn.args.args if a.arg != "self"]
        used_params = {a.arg for a in src_fn.args.args if a.arg != "self"
                       and any(isinstance(n, ast.Name) and n.id == a.arg
                               for n in ast.walk(src_fn))}
        pgone = sorted(pp for pp in params if pp in used_params and pp not in blk)
        if pgone:
            found.append(f"PARAM ERASURE (used in source, absent from body: {pgone})")
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
