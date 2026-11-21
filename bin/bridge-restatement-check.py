#!/usr/bin/env python3
"""bridge-restatement-check.py — P0.1 of richer-contracts-bridge-plan.md.

The anti-drift CROSS-CHECK.  S-ext established that
`src/formal-semantics/pycsl-formal-export.mlw` is a hand WhyML *re-statement*
of the certified Rocq emitter `Phase6L_EmitAssign.v::emit_assign` (extraction is
OCaml-only, there is no Rocq->WhyML path).  So "generate-don't-write => cannot
drift" is too weak: the WhyML `EmitAssignExport.emit_F_assign` could silently
diverge from the Rocq `emit_assign`.  This tool makes that audit obligation
MECHANICALLY CHECKED.

Approach.  Why3 `string.String.concat` is a pure *logic* function with no
executable/extractable content ("Logical symbol concat is used in a non-ghost
context"), so approach (a) of the plan — `why3 extract` the WhyML fragment to
OCaml and byte-diff against the Rocq extraction — is IMPRACTICAL.  We use the
plan's fallback approach (b): a shared-oracle test that evaluates both sides on
a fixed case-set and diffs, triangulated over three independent artifacts:

    Python oracle atoms  ==(ROCQ PIN)==  Rocq-extracted emit_assign output
              |
              +==(WHYML GOAL)==  WhyML EmitAssignExport.emit_F_assign

  * ROCQ PIN: for each case, the Rocq-extracted `emit_assign` (compiled from
    src/formal-semantics/rocq/extracted/EmitExtract.ml) is run, and its output
    is required to equal the concatenation of this file's oracle atoms.  This
    pins the oracle to the certified Rocq side — a change in Rocq emit_assign
    breaks the pin.
  * WHYML GOAL: for each case a `why3 prove` goal asserts
    `emit_F_assign <case> = <atoms as a concat tree mirroring emit_F_assign's
    own nesting, NL -> the abstract FX.nl>`.  The goal is proved best-of-N by
    Alt-Ergo OR Z3.  A one-atom corruption of the export's `emit_F_assign`
    makes the opaque string-literal equality unprovable => the goal FAILS.

PASS iff every ROCQ PIN matches AND every WHYML GOAL is Valid.

Because the WhyML side references FX.nl abstractly on both sides of the '\n'
atom, the newline is a presentational atom checked structurally (not by literal
'\n' equality — Why3 string literals are opaque, per S-c3 finding #1).  EInt is
excluded from the case-set for the same reason: `z_to_string` is abstract in the
export, so integer rendering is a presentational atom (documented, not checked).

Usage:
  bin/bridge-restatement-check.py                 # run the cross-check
  bin/bridge-restatement-check.py --corrupt SED   # inject a corruption into a
                                                  # COPY of the export before the
                                                  # WhyML goals (non-vacuity demo);
                                                  # SED is 'OLD/NEW' (both literal)
Exit: 0 all pass; 1 a check failed; 2 setup error.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT = os.path.join(ROOT, "src", "formal-semantics", "pycsl-formal-export.mlw")
ROCQ = os.path.join(ROOT, "src", "formal-semantics", "rocq")
EXTRACTED = os.path.join(ROCQ, "extracted")

NL = "\x00NL\x00"   # sentinel atom: real '\n' on the Rocq side, FX.nl on WhyML side.

# ---------------------------------------------------------------------------
# expr AST (mirrors EmitIrAdt.expr / Phase1_AST.expr).  EInt excluded (abstract
# z_to_string).  Each node is a tuple (tag, ...).
# ---------------------------------------------------------------------------
def Var(x):            return ("EVar", x)
def Sub(a, i):         return ("ESubscript", a, i)
def Len(a):            return ("ELen", a)
def Field(o, f):       return ("EFieldGet", o, f)
def Bin(op, a, b):     return ("EBinOp", op, a, b)
def Neg(e):            return ("ENeg", e)
def Cmp(op, a, b):     return ("ECmp", op, a, b)
def Call(f, args):     return ("ECall", f, args)

BINOP = {"OpAdd": "+", "OpSub": "-", "OpMul": "*", "OpDiv": "/", "OpMod": "mod"}
CMPOP = {"OpEq": "=", "OpNe": "<>", "OpLt": "<", "OpLe": "<=", "OpGt": ">", "OpGe": ">="}


# ---- pretty_expr atomization (mirrors EmitAssignExport.pretty_expr nesting) --
# Returns a NESTED structure of atoms that reproduces emit_F_assign's exact
# concat nesting, as a python "concat tree": either a str (leaf atom) or a
# tuple ('cat', left, right) meaning concat left right.
def cat(*parts):
    """Right-nested concat tree of >=1 parts (each a tree or str)."""
    assert parts
    acc = parts[-1]
    for p in reversed(parts[:-1]):
        acc = ("cat", p, acc)
    return acc


def pretty_tree(e):
    tag = e[0]
    if tag == "EVar":
        return e[1]
    if tag == "ESubscript":
        a, i = e[1], e[2]
        return cat(a, "[", pretty_tree(i), "]")
    if tag == "ELen":
        return cat("(length ", e[1], ")")
    if tag == "EFieldGet":
        return cat(e[1], ".", e[2])
    if tag == "EBinOp":
        op, a, b = e[1], e[2], e[3]
        return cat("(", pretty_tree(a), " ", BINOP[op], " ", pretty_tree(b), ")")
    if tag == "ENeg":
        return cat("(- ", pretty_tree(e[1]), ")")
    if tag == "ECmp":
        op, a, b = e[1], e[2], e[3]
        return cat("(", pretty_tree(a), " ", CMPOP[op], " ", pretty_tree(b), ")")
    if tag == "ECall":
        f, args = e[1], e[2]
        return cat(f, "(", args_tree(args), ")")
    raise ValueError(tag)


def args_tree(args):
    if not args:
        return ""
    if len(args) == 1:
        return pretty_tree(args[0])
    return cat(pretty_tree(args[0]), ", ", args_tree(args[1:]))


def emit_tree(state, x, e):
    """Mirror of EmitAssignExport.emit_F_assign, as a concat tree."""
    shared, declared, bounded = state
    if x in shared:
        return cat(x, " := ", pretty_tree(e))
    if x not in declared:
        if bounded is not None:
            return cat("let ", x, " = ref (", pretty_tree(e),
                       " : int", bounded, ") in", NL)
        return cat("let ", x, " = ref ", pretty_tree(e), " in", NL)
    return cat(x, " := ", pretty_tree(e))


# ---- flatten a concat tree to the raw string (for the ROCQ PIN) -------------
def flatten(tree):
    if isinstance(tree, str):
        return "\n" if tree == NL else tree
    _, l, r = tree
    return flatten(l) + flatten(r)


# ---- render a concat tree to a WhyML term (for the WHYML GOAL) --------------
def whyml_atom(a):
    if a == NL:
        return "FX.nl"
    return '"' + a.replace("\\", "\\\\").replace('"', '\\"') + '"'


def whyml_tree(tree):
    if isinstance(tree, str):
        return whyml_atom(tree)
    _, l, r = tree
    return "(concat %s %s)" % (whyml_tree(l), whyml_tree(r))


# ---- render expr / state to WhyML and to OCaml ------------------------------
def whyml_expr(e):
    tag = e[0]
    if tag == "EVar":
        return 'EI.EVar %s' % qstr(e[1])
    if tag == "ESubscript":
        return 'EI.ESubscript %s %s' % (qstr(e[1]), paren(whyml_expr(e[2])))
    if tag == "ELen":
        return 'EI.ELen %s' % qstr(e[1])
    if tag == "EFieldGet":
        return 'EI.EFieldGet %s %s' % (qstr(e[1]), qstr(e[2]))
    if tag == "EBinOp":
        return 'EI.EBinOp EI.%s %s %s' % (e[1], paren(whyml_expr(e[2])), paren(whyml_expr(e[3])))
    if tag == "ENeg":
        return 'EI.ENeg %s' % paren(whyml_expr(e[1]))
    if tag == "ECmp":
        return 'EI.ECmp EI.%s %s %s' % (e[1], paren(whyml_expr(e[2])), paren(whyml_expr(e[3])))
    if tag == "ECall":
        inner = whyml_list([whyml_expr(a) for a in e[2]])
        return 'EI.ECall %s %s' % (qstr(e[1]), inner)
    raise ValueError(tag)


def whyml_list(items):
    acc = "(Nil: list EI.expr)"
    for it in reversed(items):
        acc = "(Cons (%s) %s)" % (it, acc)
    return acc


def whyml_idlist(items):
    acc = "(Nil: list FX.ident)"
    for it in reversed(items):
        acc = "(Cons %s %s)" % (qstr(it), acc)
    return acc


def whyml_state(state):
    shared, declared, bounded = state
    b = "None" if bounded is None else "(Some %s)" % qstr(bounded)
    return ("{ FX.as_shared_vars = %s; FX.as_declared_refs = %s; FX.as_bounded_int = %s }"
            % (whyml_idlist(shared), whyml_idlist(declared), b))


def qstr(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def paren(s):
    return "(%s)" % s


# ---- OCaml rendering (against EmitExtract.ml, strings are char list) ---------
def ml_cl(s):
    return 'cl %s' % ('"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"')


def ml_expr(e):
    tag = e[0]
    if tag == "EVar":
        return 'EVar (%s)' % ml_cl(e[1])
    if tag == "ESubscript":
        return 'ESubscript (%s, %s)' % (ml_cl(e[1]), ml_expr(e[2]))
    if tag == "ELen":
        return 'ELen (%s)' % ml_cl(e[1])
    if tag == "EFieldGet":
        return 'EFieldGet (%s, %s)' % (ml_cl(e[1]), ml_cl(e[2]))
    if tag == "EBinOp":
        return 'EBinOp (%s, %s, %s)' % (e[1], ml_expr(e[2]), ml_expr(e[3]))
    if tag == "ENeg":
        return 'ENeg (%s)' % ml_expr(e[1])
    if tag == "ECmp":
        return 'ECmp (%s, %s, %s)' % (e[1], ml_expr(e[2]), ml_expr(e[3]))
    if tag == "ECall":
        inner = "[" + "; ".join(ml_expr(a) for a in e[2]) + "]"
        return 'ECall (%s, %s)' % (ml_cl(e[1]), inner)
    raise ValueError(tag)


def ml_state(state):
    shared, declared, bounded = state
    b = "None" if bounded is None else "Some (%s)" % ml_cl(bounded)
    sh = "[" + "; ".join(ml_cl(s) for s in shared) + "]"
    dc = "[" + "; ".join(ml_cl(s) for s in declared) + "]"
    return "{ as_shared_vars = %s; as_declared_refs = %s; as_bounded_int = %s }" % (sh, dc, b)


# ===========================================================================
# The shared oracle: assign-relevant cases.  (shared, declared, bounded)
# ===========================================================================
# Coverage: every emit_F_assign branch (1 shared / 2e bounded / 2g default / 5
# existing) x every pretty_expr constructor x every binop/cmpop atom.  binop/cmp
# atoms are exercised in the shared/existing (branch 1/5) position: their deeply
# nested concat tree spliced *inside* the branch-2g `let ... ref ... in\n` wrapper
# is the associativity-brittle shape S-c3 flagged and is not SMT-viable in budget
# (both Alt-Ergo and Z3 time out / OOM); the simpler `x := <expr>` wrapper proves
# fast, so the operator atoms are cross-checked there without loss of coverage.
CASES = [
    # id,                (shared,      declared,  bounded), x,   expr
    ("b1_var",           (["x"],       [],        None),   "x", Var("y")),
    ("b5_var",           ([],          ["x"],     None),   "x", Var("y")),
    ("b2g_var",          ([],          [],        None),   "x", Var("y")),
    ("b2e_bounded32",    ([],          [],        "32"),   "x", Var("y")),
    ("b2e_bounded64",    ([],          [],        "64"),   "x", Var("y")),
    ("b2g_subscript",    ([],          [],        None),   "x", Sub("arr", Var("i"))),
    ("b2g_len",          ([],          [],        None),   "x", Len("arr")),
    ("b2g_field",        ([],          [],        None),   "x", Field("o", "f")),
    ("b2g_neg",          ([],          [],        None),   "x", Neg(Var("a"))),
    ("b2g_call2",        ([],          [],        None),   "x", Call("f", [Var("a"), Var("b")])),
    ("b2g_nested_sub",   ([],          [],        None),   "x", Sub("a", Sub("b", Var("i")))),
    ("b1_binop_add",     (["x"],       [],        None),   "x", Bin("OpAdd", Var("a"), Var("b"))),
    ("b1_binop_sub",     (["x"],       [],        None),   "x", Bin("OpSub", Var("a"), Var("b"))),
    ("b1_binop_mul",     (["x"],       [],        None),   "x", Bin("OpMul", Var("a"), Var("b"))),
    ("b1_binop_div",     (["x"],       [],        None),   "x", Bin("OpDiv", Var("a"), Var("b"))),
    ("b1_binop_mod",     (["x"],       [],        None),   "x", Bin("OpMod", Var("a"), Var("b"))),
    ("b5_cmp_lt",        ([],          ["x"],     None),   "x", Cmp("OpLt", Var("a"), Var("b"))),
    ("b5_cmp_ne",        ([],          ["x"],     None),   "x", Cmp("OpNe", Var("a"), Var("b"))),
]


def build_ocaml_driver(path):
    lines = [
        "open EmitExtract",
        "let cl (s:string) : char list =",
        "  let r = ref [] in",
        "  for i = String.length s - 1 downto 0 do r := s.[i] :: !r done; !r",
        "let sl (cs:char list) : string =",
        "  let b = Buffer.create 64 in List.iter (Buffer.add_char b) cs; Buffer.contents b",
        "let js (s:string) : string =",
        "  let b = Buffer.create (String.length s + 2) in Buffer.add_char b '\"';",
        "  String.iter (fun c -> match c with",
        "    | '\"' -> Buffer.add_string b \"\\\\\\\"\"",
        "    | '\\\\' -> Buffer.add_string b \"\\\\\\\\\"",
        "    | '\\n' -> Buffer.add_string b \"\\\\n\"",
        "    | c -> Buffer.add_char b c) s;",
        "  Buffer.add_char b '\"'; Buffer.contents b",
        "let run id st x e = Printf.printf \"%s\\t%s\\n\" id (js (sl (emit_assign st (cl x) e)))",
        "let () =",
    ]
    for cid, state, x, e in CASES:
        lines.append('  run "%s" (%s) "%s" (%s);' % (cid, ml_state(state), x, ml_expr(e)))
    lines.append("  ()")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def build_whyml_goals():
    out = ["", "module RestatementCrossCheck",
           "  use int.Int", "  use list.List", "  use option.Option",
           "  use string.String", "  use EmitIrAdt as EI",
           "  use EmitAssignExport as FX", ""]
    for cid, state, x, e in CASES:
        tree = emit_tree(state, x, e)
        goal = ("  goal x_%s :\n    FX.emit_F_assign %s %s (%s)\n    = %s\n"
                % (cid, whyml_state(state), qstr(x), whyml_expr(e), whyml_tree(tree)))
        out.append(goal)
    out.append("end")
    return "\n".join(out)


def sh(cmd, **kw):
    return subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, **kw)


def ensure_extraction():
    ml = os.path.join(EXTRACTED, "EmitExtract.ml")
    if not os.path.isfile(ml):
        r = sh("make -C %s Phase6L_EmitExtract.vo" % ROCQ)
        if r.returncode != 0:
            print(r.stdout + r.stderr)
            return False
    return True


def run_rocq_oracle(tmp):
    """Compile+run the emit_assign driver; return {case_id: output_string}.

    Everything is built INSIDE tmp (the extraction .ml/.mli are copied in) so
    the repo is never polluted with .cmi/.cmo build artifacts."""
    drv = os.path.join(tmp, "restate_driver.ml")
    build_ocaml_driver(drv)
    shutil.copy(os.path.join(EXTRACTED, "EmitExtract.ml"), tmp)
    shutil.copy(os.path.join(EXTRACTED, "EmitExtract.mli"), tmp)
    r = sh("cd %s && ocamlc -c EmitExtract.mli && ocamlc -c EmitExtract.ml && "
           "ocamlc -c restate_driver.ml && "
           "ocamlc -o restate_driver EmitExtract.cmo restate_driver.cmo" % tmp)
    if r.returncode != 0:
        print("[error] OCaml driver build failed:\n" + r.stdout + r.stderr)
        return None
    r = sh("%s/restate_driver" % tmp)
    if r.returncode != 0:
        print("[error] driver run failed:\n" + r.stderr)
        return None
    out = {}
    for line in r.stdout.splitlines():
        if "\t" not in line:
            continue
        cid, js = line.split("\t", 1)
        out[cid] = decode_json_str(js)
    return out


def decode_json_str(js):
    import json
    return json.loads(js)


def prove_goal(mlw, goal, timeout=15):
    """best-of-N: Valid if Alt-Ergo OR Z3 proves it."""
    for prover in ("alt-ergo", "z3"):
        r = sh("why3 prove -P %s -t %d -L %s %s -T RestatementCrossCheck -G %s"
               % (prover, timeout, os.path.join(ROOT, "src", "formal-semantics"), mlw, goal))
        if "Valid" in r.stdout:
            return True, prover
    return False, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corrupt", default=None,
                    help="OLD/NEW literal sed applied to the export COPY (non-vacuity demo)")
    ap.add_argument("--timeout", type=int, default=15)
    args = ap.parse_args()

    if not ensure_extraction():
        print("[error] could not build Rocq extraction")
        return 2

    tmp = tempfile.mkdtemp(prefix="bridge-restate-")
    try:
        # ---- ROCQ PIN --------------------------------------------------
        rocq = run_rocq_oracle(tmp)
        if rocq is None:
            return 2
        pin_fail = []
        for cid, state, x, e in CASES:
            want = flatten(emit_tree(state, x, e))
            got = rocq.get(cid)
            if got != want:
                pin_fail.append((cid, want, got))

        # ---- WHYML GOALS -----------------------------------------------
        scratch = os.path.join(tmp, "crosscheck.mlw")
        shutil.copy(EXPORT, scratch)
        if args.corrupt:
            old, new = args.corrupt.split("/", 1)
            with open(scratch) as f:
                txt = f.read()
            if old not in txt:
                print("[error] corruption target %r not found in export" % old)
                return 2
            txt = txt.replace(old, new, 1)
            with open(scratch, "w") as f:
                f.write(txt)
        with open(scratch, "a") as f:
            f.write(build_whyml_goals())

        goal_fail = []
        goal_ok = []
        for cid, _, _, _ in CASES:
            ok, prover = prove_goal(scratch, "x_" + cid, args.timeout)
            (goal_ok if ok else goal_fail).append((cid, prover))

        # ---- report ----------------------------------------------------
        print("=" * 70)
        print("BRIDGE RE-STATEMENT CROSS-CHECK (P0.1)")
        print("  export : %s" % os.path.relpath(EXPORT, ROOT))
        print("  cases  : %d assign-relevant" % len(CASES))
        if args.corrupt:
            print("  CORRUPTION INJECTED: %r  (non-vacuity demo)" % args.corrupt)
        print("=" * 70)
        print("\n[ROCQ PIN] oracle atoms == Rocq-extracted emit_assign output")
        if pin_fail:
            for cid, want, got in pin_fail:
                print("  FAIL %-18s want=%r got=%r" % (cid, want, got))
        else:
            print("  OK  all %d cases: Python oracle atoms match Rocq emit_assign" % len(CASES))
        print("\n[WHYML GOAL] emit_F_assign == oracle atoms (best-of-N AE/Z3)")
        for cid, prover in goal_ok:
            print("  Valid %-18s (%s)" % (cid, prover))
        for cid, _ in goal_fail:
            print("  FAIL  %-18s (neither Alt-Ergo nor Z3 proved it)" % cid)

        ok = not pin_fail and not goal_fail
        print("\n" + "=" * 70)
        print("RESULT: %s   (pin_fail=%d, goal_fail=%d)"
              % ("PASS" if ok else "FAIL", len(pin_fail), len(goal_fail)))
        print("=" * 70)
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
