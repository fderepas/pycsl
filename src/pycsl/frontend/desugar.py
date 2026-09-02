"""#33 — THE MODULE-5 INPUT NORMALIZATION PASS (Python-AST -> Python-AST).

Every rewrite here exists because a Module 5 handler SILENTLY DROPS part of the node it is
given — a fail-OPEN erasure, invisible to every gate plane because the dropped construct
simply is not in the IR to be checked. Normalizing the INPUT is deliberate: the handlers
(`_py_expr_compare`, `_py_stmt_annassign`) are CONVERTED mirror methods whose models are
HAND-SYNTHESIZED bespoke lowerings keyed on the method name, so editing their bodies would
leave mirror-sync, L3-tc and the whole-file proof all GREEN while the model silently
stopped being the body. Rewriting the input instead leaves every such body byte-identical
and makes its bespoke model TRUE, because the shape it cannot express no longer reaches it.


## 1. CHAINED COMPARISONS

Python's `a < b < c` means `a < b and b < c`, with the middle operand evaluated EXACTLY
ONCE. Module 5's expression walker (`_py_expr_compare`) lowers a `Compare` node by reading
`ops[0]` and `comparators[0]` and DISCARDING the rest, so before this pass every chain lost
its tail: `if 2 <= a <= 3:` became `if (2 <= a)`.

That is not a harmless over-approximation. A guard that is TRUE MORE OFTEN than Python's
over-approximates the THEN branch (more states, still sound) but UNDER-approximates the
ELSE: every state with `a >= 2` and `a > 3` takes Python's else and the model's then, so
the else branch was proved over a strict SUBSET of the reachable states.

It was also an internal disagreement. The `#@` ANNOTATION grammar has always expanded
chains correctly (`#@ ensures 0 <= \\result < 256` emits `0 <= result && result < 256`), so
the two halves of the same file meant different things by `a <= b <= c`.

WHY A PRE-PASS AND NOT A FIX INSIDE `_py_expr_compare`. That method is CONVERTED in the
self-annotation mirror and its model is a HAND-SYNTHESIZED whole-body lowering
(`module6_whyml/functions.py::_emit_py_expr_compare_bespoke`) keyed on the METHOD NAME,
which emits the head comparison and nothing else. Changing the live body would leave
mirror-sync GREEN (the bodies would still match), L3-tc green and the proof green, while
the model silently stopped being the body — the exact faithfulness trap this campaign
exists to close. Normalizing the input instead leaves `_py_expr_compare` byte-identical and
makes its bespoke model's claim — "the head comparison is the whole node" — TRUE, because
after this pass no multi-operator `Compare` reaches Module 5 at all.

WHERE IT RUNS: `Module5_IREmitter.generate_json`, immediately before the walk. That is the
single choke point both Module 5 entry paths go through (`pycsl.py`'s main pipeline and
`ir_resolve.resolve`'s dependency sub-pipeline), so no caller can forget it.

EVALUATION ORDER IS THE SOUNDNESS ARGUMENT, AND NOTHING IS REFUSED. The naive expansion
mentions the middle operand TWICE while Python evaluates it once, so it is
semantics-preserving only when re-evaluating that operand is observationally identical.
Names, constants, attribute and subscript reads and arithmetic over them qualify (a
subscript that raises raises identically both times), as does a call to a pure, total,
deterministic builtin — `len`, `ord`, `abs`, `chr`, the spellings that actually occur in a
chain's middle (`2 <= len(xs) <= 3`, `32 <= ord(ch) <= 126`). `_chain_operand_repeatable`
decides exactly that, from a literal allow-list rather than a heuristic.

When the middle operand is NOT repeatable — `0 <= enc_range() < 256`, four of which are in
the reference corpus — it is NOT mentioned twice and it is NOT refused. It is bound by a
WALRUS on its first and only evaluation and read back in the next link:

    a <= f() <= b      ->      a <= (_pycsl_cmp_1 := f())  and  _pycsl_cmp_1 <= b

which is Python's own rule for a chain, written in Python. No purity assumption is needed
and no idiom is rejected. The temporary is numbered from a per-pass counter, never from
`id(...)`, because the emitted `.mlw` must be byte-reproducible across runs.


## 2. ANNOTATED STORES THROUGH A NON-NAME TARGET

`_py_stmt_annassign` is

    if isinstance(stmt.target, ast.Name) and stmt.value is not None:
        ir_stmts.append({"stmt": "Assign", ...})

so `self.x: int = 0` and `a[i]: int = v` — an AnnAssign whose target is an ATTRIBUTE or a
SUBSCRIPT — produce NO IR AT ALL. The store vanishes. `_py_stmt_assign` handles exactly
these targets, and handles them carefully: `self.f = v` becomes a `FieldAssign`, `p.f = v`
on a record-typed parameter becomes a caller-visible `FieldAssign`, `a[i].f = v` is
REFUSED with a diagnostic — its own comment records that the earlier silent drop was "an
UNSOUND fail-OPEN: a caller/body could prove the field UNCHANGED after a real mutation".
The annotated form is the same store with a type written on it, and it had the very bug
`_py_stmt_assign` was fixed for.

So `_normalize_annotated_stores` rewrites `<non-Name target>: T = v` into `<target> = v`
and lets `_py_stmt_assign` decide. `T` is a DECLARATION, not part of the store, and no
consumer reads it here — with ONE exception, which is why `__init__` is excluded: Module 5
`_collect_class_fields` and `module5/construction_synth` scan `__init__` bodies for
`self.x: T = ...` to recover the FIELD TYPE (that is how the mirror's own
`self._final_registry: List[Dict[str, PyVal]] = []` declares its type). Rewriting those
would erase the type, so they are left exactly as they are. Every other AnnAssign consumer
in the tree already filters on `isinstance(target, ast.Name)` and is unaffected.

CENSUS AT THE TIME OF WRITING: 0 in the reference corpus, 0 in the mirror, 0 in
`pycsl_lib`, 51 in the live emitter (`functions._reset_function_state`,
`Module6_WhyMLTranspiler.transpile`, `Module5_IREmitter.visit_Module`, ...). So this is
byte-inert today and it UNBLOCKS those state-reset methods for conversion.


## 3. `for ... else` / `while ... else` ARE REFUSED, NOT DROPPED

`_process_for` and `_process_while` read `target`/`iter`/`body` and `test`/`body`; neither
reads `orelse`. A loop `else` runs exactly when the loop finished WITHOUT `break`, and
dropping it removes a whole reachable path from the model while leaving the program's
behaviour unchanged — fail-OPEN in the same way as the two above. Modelling it needs a
break-flag lowering, which is a feature, not a normalization. Until that exists the honest
answer is a loud refusal: `_reject_loop_else` raises. CENSUS: 0 in the corpus, 0 in the
mirror, 0 in `pycsl_lib`, 2 in the live emitter (both inside `\trusted` mirror stubs, whose
bodies are never parsed by this pipeline). `try ... else` is NOT affected —
`_py_stmt_try` does carry `orelse` and `finalbody`.
"""
from __future__ import annotations

from frontend import pure_ast as ast
from errors import PyCSLParseError

# Calls that may be mentioned twice by the expansion: pure, total, deterministic
# projections of their argument, with no state and no I/O. A literal tuple, not a
# heuristic — widening it is a deliberate soundness decision.
_REPEATABLE_CALLS = ("len", "ord", "abs", "chr")

# Node kinds that are never safe to re-evaluate: they bind, suspend, or build.
_NON_REPEATABLE = (ast.Await, ast.NamedExpr, ast.Yield, ast.YieldFrom,
                   ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)


def _chain_operand_repeatable(node: object) -> bool:
    """Is `node` safe to EVALUATE TWICE, as the chain expansion does?"""
    for sub in ast.walk(node):
        if isinstance(sub, _NON_REPEATABLE):
            return False
        if isinstance(sub, ast.Call):
            if not (isinstance(getattr(sub, "func", None), ast.Name)
                    and sub.func.id in _REPEATABLE_CALLS
                    and not getattr(sub, "keywords", [])):
                return False
    return True


class _ChainDesugarer(ast.NodeTransformer):
    def __init__(self) -> None:
        # A DETERMINISTIC counter, not `id(node)`: the emitted `.mlw` must be reproducible
        # byte-for-byte across runs, and an object address is not.
        self._n = 0

    def visit_Compare(self, node):
        self.generic_visit(node)
        ops = getattr(node, "ops", [])
        comparators = getattr(node, "comparators", [])
        if len(ops) <= 1:
            return node
        links = []
        left = node.left
        for k in range(len(ops)):
            right = comparators[k]
            if k + 1 < len(ops) and not _chain_operand_repeatable(right):
                # NOT SAFE TO MENTION TWICE — so DO NOT mention it twice. Bind it with a
                # walrus on its FIRST (and only) evaluation and read the binding in the
                # next link: `a <= (_t := f()) and _t <= b`. That is exactly Python's own
                # rule for a chain — the middle operand is evaluated once — expressed in
                # Python itself, so no purity assumption is needed and no idiom is refused.
                self._n += 1
                tmp = "_pycsl_cmp_%d" % (self._n,)
                bind = ast.NamedExpr(target=ast.Name(id=tmp, ctx=ast.Store()), value=right)
                ast.copy_location(bind, node)
                ast.fix_missing_locations(bind)
                link = ast.Compare(left=left, ops=[ops[k]], comparators=[bind])
                nxt_left = ast.Name(id=tmp, ctx=ast.Load())
                ast.copy_location(nxt_left, node)
                ast.fix_missing_locations(nxt_left)
            else:
                link = ast.Compare(left=left, ops=[ops[k]], comparators=[right])
                nxt_left = right
            ast.copy_location(link, node)
            ast.fix_missing_locations(link)
            links.append(link)
            left = nxt_left
        out = ast.BoolOp(op=ast.And(), values=links)
        ast.copy_location(out, node)
        ast.fix_missing_locations(out)
        return out


def reject_loop_else(tree: ast.AST) -> None:
    """Refuse `for ... else` / `while ... else`, which Module 5 would silently DROP."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.While)) and node.orelse:
            raise PyCSLParseError(
                "`for ... else` / `while ... else` is not modelled: the `else` clause runs "
                "exactly when the loop finished without `break`, and the IR emitter reads "
                "only the loop body, so the clause would be silently DROPPED from the "
                "model. Rewrite it with an explicit flag.")


def normalize_annotated_stores(tree: ast.AST) -> None:
    """Rewrite `<attribute-or-subscript>: T = v` into `<target> = v`, which Module 5 lowers.

    `__init__` is EXCLUDED: its annotated `self.x: T = ...` statements are where the record
    field TYPES are read from."""
    protected = set()
    for node in ast.walk(tree):
        if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == "__init__"):
            for sub in ast.walk(node):
                if isinstance(sub, ast.AnnAssign):
                    protected.add(id(sub))
    for node in ast.walk(tree):
        for field in ("body", "orelse", "finalbody"):
            stmts = getattr(node, field, None)
            if not isinstance(stmts, list):
                continue
            for i in range(len(stmts)):
                st = stmts[i]
                if (isinstance(st, ast.AnnAssign) and st.value is not None
                        and not isinstance(st.target, ast.Name)
                        and id(st) not in protected):
                    rewritten = ast.Assign(targets=[st.target], value=st.value)
                    ast.copy_location(rewritten, st)
                    ast.fix_missing_locations(rewritten)
                    stmts[i] = rewritten


def desugar_chained_comparisons(tree: ast.AST) -> ast.AST:
    """Rewrite every multi-operator `Compare` into the `and`-chain Python means by it.
    No-op (byte-identical emission) for any file that contains no chained comparison."""
    return _ChainDesugarer().visit(tree)
