"""#33 — CHAINED-COMPARISON DESUGARING, a Python-AST normalization pre-pass.

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
"""
from __future__ import annotations

from frontend import pure_ast as ast

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


def desugar_chained_comparisons(tree: ast.AST) -> ast.AST:
    """Rewrite every multi-operator `Compare` into the `and`-chain Python means by it.
    No-op (byte-identical emission) for any file that contains no chained comparison."""
    return _ChainDesugarer().visit(tree)
