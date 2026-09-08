#!/usr/bin/env python3
r"""A PRESENCE OR TRUTH TEST DECIDED FROM A **TYPE** — the twenty-seventh plane.

THE GAP THIS PLANE EXISTS TO CLOSE, and route #50 lived in it for the whole campaign.
Two planes already watch a Module-6 lowering that answers a Why3 CONSTANT:

    bin/check-constant-fallthrough.py         the FALL-THROUGH of a handler
    bin/check-singleton-constant-lowering.py  an arm keyed on an IR NODE KIND

Route #50 was neither. Its arm was keyed on the operand's **TYPE** — "this expression is
string-typed and we are inside a `@mutable_state` class" — and it answered the literal
`false` for `x is None`. Both existing planes looked straight past it, and the comment above
it called it "a sound always-present model" while
`scratchpad/w49/route50/r50.py` proved `\result == 7` where Python returns 0.

THE PRINCIPLE THE BASELINE ENFORCES, in one sentence: **a presence or truth test may only be
DECIDED by a fact about the BINDING, never by a fact about the TYPE.** A type says what
values may be stored; it does not say which one is stored here. Where the model has a
binding fact — a live `None` record, a known collection size, a definite assignment — the
decision is faithful and this plane wants it. Where it has only a type, the honest answers
are an opaque test or a refusal.

WHAT IT CHECKS. Every `if` in `src/pycsl/module6_whyml/` whose test mentions an emitter
REGISTRY or TYPE predicate (a `self._…` attribute, a `getattr(self, "_…")`, a `_is_…`
recogniser) and whose body's first statement returns a Why3 BOOL CONSTANT — `"true"`,
`"false"`, or a two-armed `"true" if C else "false"`. Each such arm must carry a baseline
entry saying WHICH FACT justifies deciding. The key is (function, registry-signature,
literal) — never a line number — so it survives ordinary edits and fires when a NEW arm
appears, when a known one changes its answer, or when a baseline entry outlives its arm.

    OPEN entries are allowed and are NOT failures: an arm whose justification is known to be
    wrong, recorded WITH the route file that says so. That is how the 26th plane records its
    one DROPPED cell, and it keeps the gate green about a defect it NAMES rather than
    silently.

USAGE
    bin/check-type-keyed-constant-answers.py [--verbose]
"""
import argparse
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "src", "pycsl", "module6_whyml")

# ---------------------------------------------------------------------------
# THE BASELINE.  (function, registry-signature, literal) -> the fact that justifies
# DECIDING.  Anything not listed here is a FAILURE, whether it is new or un-triaged.
# ---------------------------------------------------------------------------
BASELINE = {
    ("_handle_binop", "_current_self_type+_is_string_expr+_mutable_state_classes",
     "false|true"):
        "OPEN -- ROUTE #51. This is route #50's third answer, the always-present `false` "
        "kept for a name the function never binds to `None`, and it is exactly as far as "
        "a SYNTACTIC binding fact reaches. It is WRONG for a local bound from a call that "
        "returns None while declaring `-> str` (shape (a)) and for a `self.<str-field>` a "
        "caller stores None into (shape (b)); both PROVE a contract false of their "
        "program. Recorded with its census and a scoped recommendation in "
        "getting-better/open-routes/route51-scalar-annotation-lie.md. Kept as an entry "
        "rather than removed so this plane stays green about a defect it NAMES.",
    ("_handle_binop", "_current_emitting_func+_func_return_type+"
     "_module_method_return_annotations", "false|true"):
        "route #44's FAITHFUL arm: `\\result` in a function whose PYTHON return annotation "
        "is a plain scalar can never be the None singleton. The fact is the annotation AND "
        "the WhyML type together -- the annotation gate is load-bearing, because an "
        "`Optional[_Tok]` return degenerates to the WhyML type `int` and the WhyML type "
        "alone fired on `_Parser.accept_op`. Route #51 is the reminder that an annotation "
        "is only a fact while nothing contradicts it; here the contradiction would be a "
        "`return None` in a scalar-annotated function, which is #51's own census.",
    ("_handle_binop", "_ghost_tuple_vars", "false|true"):
        "a GHOST TUPLE local is constructed by the emitter itself at the binding site "
        "(`union_info = self._match_subject_union_info(...)`) and there is no path on "
        "which the model leaves it unbound -- the binding fact is that the emitter wrote "
        "the binding. Not a type claim about an arbitrary value.",
    ("_handle_binop", "_is_emit_ir_expr", "false|true"):
        "the emit_ir ALWAYS-PRESENT model. The faithful arms above it (the `IrSliceN` "
        "optional-bound test and the `_EMIT_IR_EXTRA_NODE_KEYS_BY_FUNC` discriminant) fire "
        "wherever the model actually carries the optionality; what remains is a sub-node "
        "the reflection model constructs as present. STATED SCOPE, and it is a claim about "
        "the CONTRACTS rather than about the lowering: it is sound for the type-safety+frame "
        "contracts the mirror carries, because deleting a branch cannot make an `ensures "
        "True` false and neither arm writes a self-field. A mirror method with a real "
        "`ensures` reaching this arm would break that argument -- and nothing checks that "
        "today, which is the named follow-up.",
    ("_to_bool", "_emit_ir_local_vars+_is_emit_ir_expr", "true"):
        "the truthiness twin of the emit_ir always-present arm above, on the same stated "
        "scope and with the same named follow-up.",
    ("_to_bool", "_current_self_type+_current_symbol_table+_mutable_state_classes", "true"):
        "`if <dict/set param>:` as a PRESENT-guard before a membership test. The dict/set "
        "is modelled as a `map` with no int value, so the default `<> 0` coercion is a TYPE "
        "ERROR rather than a wrong answer, and `true` is the over-approximation that lets "
        "the real check -- the `in` that follows -- happen. Same stated scope as the "
        "emit_ir arms: an EMPTY dict is falsy in Python, so a contract that depends on the "
        "else branch would be proved over a subset. @mutable_state-gated.",
    ("_to_bool", "_current_self_type+_mutable_state_classes", "true"):
        "`if sl.get(\"lower\"):` -- a present-guard on an emit_ir SUB-NODE projection "
        "(`svalue_of`/`object_of`/`sindex_of`/`arg0_of`), i.e. the same always-present "
        "model reached through a projector instead of a local. Same stated scope.",
    ("_to_bool", "_hvalmap_local_vars", "true"):
        "`if not vinfo:` on a nested-map local (`map string (option hval)`). A map has no "
        "int value, so the default coercion is a type error; the real projection happens in "
        "the returned tuple. Same stated scope as the dict/set arm.",
    ("_to_bool", "_rebound_collections", "true|false"):
        "route #31's REPAIR, not its defect: a collection whose SIZE the emitter knows "
        "exactly (`_known_collection_sizes`, and only while the name is not in "
        "`_rebound_collections`) has an EXACT truth value. That is a binding fact, not a "
        "type fact, and the unknown-size case falls through to `Array.length x <> 0`.",
    ("_handle_isinstance", "_is_emit_ir_expr", "true"):
        "`isinstance(<emit_ir>, dict)` is STRUCTURALLY true in the reflection model -- "
        "every reflected IR node IS a Python dict -- so this is not a decision about a "
        "value, it is the model's own type discipline. The real discrimination is the "
        "conjoined `.get(\"type\") == K` read of the same node.",
    ("_handle_isinstance", "_pyval_locals", "true"):
        "the pyval twin of the emit_ir `isinstance(..., dict)` arm, on the same terms: an "
        "`hval` subject IS a Python dict in the reflection model.",
    ("_handle_in_globals_expr", "_module_binding_names", "true"):
        "`\\in_globals(n)` is deliberately THREE-VALUED and this is its decided-TRUE side: "
        "the name is a declared module binding, which is a fact about the module, not a "
        "type. The decided-FALSE side is never emitted (an import or an `exec` may inject "
        "a name), so the unsound direction does not exist here.",
    ("_handle_in_scope_expr", "_scope_must", "true"):
        "`\\in_scope(n)` decided-TRUE by DEFINITE ASSIGNMENT: a parameter, or a top-level "
        "assignment before any branch or return. A binding fact by construction.",
    ("_handle_in_scope_expr", "_scope_all+_scope_dyn_exec+_scope_params", "false"):
        "the decided-FALSE side of the same three-valued lowering: the name is neither a "
        "parameter nor assigned ANYWHERE in the function. It is WITHHELD after a dynamic "
        "`exec`, which havocs the binding set -- the gate that makes the false direction "
        "safe.",
    ("_handle_separated_expr", "_value_semantic", "true"):
        "`\\separated` under the VALUE-semantic memory model, where arrays are Why3 values "
        "rather than heap regions: two distinct values cannot alias, so separation is a "
        "theorem of the model, not an assumption about a binding. Under the heap models the "
        "real `separated` predicate is emitted.",
    ("_expr_to_whyml", "_in_spec", "true|false"):
        "a Python `True`/`False` LITERAL in a specification context is the Why3 `true`/"
        "`false`. The value is the constant -- there is no binding to be uncertain about. "
        "(Two sites, the bool-literal arm and its `Bool` node twin.)",
}


def guard_tokens(test):
    toks = set()
    for n in ast.walk(test):
        if isinstance(n, ast.Attribute) and n.attr.startswith("_"):
            toks.add(n.attr)
        elif (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
              and n.func.id == "getattr" and len(n.args) >= 2
              and isinstance(n.args[1], ast.Constant)
              and isinstance(n.args[1].value, str)):
            toks.add(n.args[1].value)
    return sorted(t for t in toks if t.startswith("_"))


def bool_constant_answer(stmt):
    if not isinstance(stmt, ast.Return) or stmt.value is None:
        return None
    v = stmt.value
    if isinstance(v, ast.Constant) and isinstance(v.value, str) and v.value in ("true", "false"):
        return v.value
    if isinstance(v, ast.IfExp):
        parts = [x.value for x in (v.body, v.orelse)
                 if isinstance(x, ast.Constant) and isinstance(x.value, str)]
        if len(parts) == 2 and set(parts) <= {"true", "false"}:
            return "|".join(parts)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    hits = []
    for fn in sorted(os.listdir(D)):
        if not fn.endswith(".py"):
            continue
        path = os.path.join(D, fn)
        src = open(path, errors="replace").read()
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for f in ast.walk(tree):
            if not isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for node in ast.walk(f):
                if not isinstance(node, ast.If):
                    continue
                for st in node.body:
                    lit = bool_constant_answer(st)
                    if lit is None:
                        continue
                    toks = guard_tokens(node.test)
                    if not toks:
                        continue          # node-kind-keyed: the 25th plane owns it
                    hits.append((f.name, "+".join(toks), lit, fn, node.lineno))

    keys = {(a, b, c) for a, b, c, _f, _l in hits}
    unknown = sorted(k for k in keys if k not in BASELINE)
    stale = sorted(set(BASELINE) - keys)
    opens = sorted(k for k in keys if k in BASELINE and BASELINE[k].startswith("OPEN"))

    if args.verbose:
        for nm, sig, lit, fn, ln in sorted(hits):
            mark = "NEW " if (nm, sig, lit) not in BASELINE else "    "
            print(f"{mark}{fn}:{ln}  {nm}  [{sig}]  -> {lit}")

    for nm, sig, lit in unknown:
        print(f"[!] type-keyed-constant-answers: `{nm}` answers the Why3 constant "
              f"`{lit}` under the registry/type guard [{sig}], and no baseline entry says "
              f"WHICH FACT justifies deciding. A TYPE is not such a fact. PROBE IT END TO "
              f"END: a driver whose contract is FALSE of the program, with Python run to "
              f"confirm the true answer. Then classify it here or make the answer opaque.")
    for k in stale:
        print(f"[!] type-keyed-constant-answers: baseline entry {k} matches no arm — the "
              f"lowering changed and the classification is stale.")
    print(f"[*] type-keyed-constant-answers: {len(keys)} registry/type-keyed arm(s) "
          f"answering a Why3 bool constant; {len(opens)} recorded OPEN.")
    for k in opens:
        print(f"    OPEN  {k[0]}  [{k[1]}] -> {k[2]}")
    if unknown or stale:
        return 1
    print("[+] type-keyed-constant-answers: OK — every arm classified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
