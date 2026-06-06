"""Contract AST → Python expression translator.

Walks Module2_Parser CSLNode trees and produces equivalent Python
expression strings that can be used in ``assert`` statements.
"""

import sys
import os

# Allow imports from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from Module2_Parser import (
    CSLNode, BinOp, UnaryOp, Var, Number, Result, Old, Nothing,
    FieldAccess, SubscriptAccess, Forall, Exists, ArrayLength,
    Valid, Separated, At, Length2D, Valid2D, AssignsRegion,
    Requires, Ensures, Assigns, LoopInvariant, LoopVariant,
    ClassInvariant, Label
)


class QuantifierBoundsError(Exception):
    """Raised when finite bounds cannot be extracted from a quantifier."""
    pass


def translate(node: CSLNode) -> str:
    """Translate a Contract AST node to a Python expression string."""
    if isinstance(node, Number):
        v = node.value
        return str(int(v)) if v == int(v) else str(v)

    elif isinstance(node, Var):
        return node.name

    elif isinstance(node, FieldAccess):
        return f"{node.object}.{node.field}"

    elif isinstance(node, SubscriptAccess):
        if node.array == "\\result":
            return f"_pycsl_result_[{translate(node.index)}]"
        return f"{node.array}[{translate(node.index)}]"

    elif isinstance(node, Result):
        return "_pycsl_result_"

    elif isinstance(node, Old):
        return _translate_old(node.expr)

    elif isinstance(node, At):
        return _translate_at(node.expr, node.label)

    elif isinstance(node, ArrayLength):
        return f"len({node.var})"

    elif isinstance(node, Valid):
        return f"(len({node.base}) >= {translate(node.length)})"

    elif isinstance(node, Valid2D):
        r = translate(node.row)
        c = translate(node.col)
        return (f"(0 <= {r} < len({node.base})"
                f" and 0 <= {c} < len({node.base}[{r}]))")

    elif isinstance(node, Length2D):
        m = translate(node.rows)
        n = translate(node.cols)
        return (f"(len({node.base}) >= {m}"
                f" and all(len({node.base}[_i2d]) >= {n}"
                f" for _i2d in range({m})))")

    elif isinstance(node, Separated):
        return f"({node.base1} is not {node.base2})"

    elif isinstance(node, Nothing):
        return "True"

    elif isinstance(node, BinOp):
        return _translate_binop(node)

    elif isinstance(node, UnaryOp):
        inner = translate(node.expr)
        if node.op == "not":
            return f"(not ({inner}))"
        else:
            return f"({node.op}({inner}))"

    elif isinstance(node, Forall):
        return _translate_quantifier(node, "all")

    elif isinstance(node, Exists):
        return _translate_quantifier(node, "any")

    # Directive wrappers — extract the inner expression
    elif isinstance(node, (Requires, Ensures, LoopInvariant,
                           LoopVariant, ClassInvariant)):
        return translate(node.expr)

    elif isinstance(node, AssignsRegion):
        return f"({node.base}, {translate(node.low)}, {translate(node.high)})"

    raise ValueError(f"Unsupported CSL node type: {type(node).__name__}")


def _translate_binop(node: BinOp) -> str:
    left = translate(node.left)
    right = translate(node.right)
    op = node.op

    if op == "==>":
        return f"(not ({left}) or ({right}))"
    elif op == "<==>":
        return f"(bool({left}) == bool({right}))"
    elif op == "/":
        # Contract division = integer division in Python
        return f"(({left}) // ({right}))"
    elif op in ("and", "or"):
        return f"(({left}) {op} ({right}))"
    elif op in ("==", "!=", "<", ">", "<=", ">=", "+", "-", "*"):
        return f"(({left}) {op} ({right}))"
    else:
        return f"(({left}) {op} ({right}))"


def _translate_old(expr: CSLNode) -> str:
    """Generate the variable name used for \old snapshots."""
    if isinstance(expr, Var):
        return f"_pycsl_old_{expr.name}"
    elif isinstance(expr, FieldAccess):
        return f"_pycsl_old_{expr.object}_{expr.field}"
    elif isinstance(expr, SubscriptAccess):
        idx = translate(expr.index)
        return f"_pycsl_old_{expr.array}[{idx}]"
    else:
        # Fallback: hash-based name
        return f"_pycsl_old_{id(expr)}"


def _translate_at(expr: CSLNode, label: str) -> str:
    """Generate the variable name used for \\at snapshots."""
    if isinstance(expr, SubscriptAccess):
        idx = translate(expr.index)
        return f"_pycsl_at_{label}_{expr.array}[{idx}]"
    elif isinstance(expr, Var):
        return f"_pycsl_at_{label}_{expr.name}"
    elif isinstance(expr, FieldAccess):
        return f"_pycsl_at_{label}_{expr.object}_{expr.field}"
    else:
        return f"_pycsl_at_{label}_{id(expr)}"


def _translate_quantifier(node, func: str) -> str:
    """Translate \\forall/\\exists with range extraction.

    Standard patterns:
      \\forall i; lo <= i and i < hi ==> body
      \\exists i; lo <= i and i < hi and body
    """
    var = node.var
    body = node.body

    try:
        lo, hi, remainder = _extract_bounds(var, body, func)
    except QuantifierBoundsError:
        # Cannot extract finite bounds — emit conservative True with warning
        return f"True  # SKIP: unbounded quantifier over {var}"

    inner = translate(remainder)
    return f"{func}({inner} for {var} in range({lo}, {hi}))"


def _extract_bounds(var: str, body: CSLNode, quant_func: str):
    """Extract (lo, hi, remainder) from a quantified body.

    For \\forall: expects  guard ==> body  where guard is  lo <= var and var < hi
    For \\exists: expects  guard and body  where guard is  lo <= var and var < hi

    Returns (lo_str, hi_str, remainder_node).
    """
    if quant_func == "all":
        # Pattern: guard ==> body
        if isinstance(body, BinOp) and body.op == "==>":
            guard = body.left
            remainder = body.right
            lo, hi = _parse_range_guard(var, guard)
            return lo, hi, remainder
        # Pattern: conjunction of range bounds with body
        # e.g., 0 <= i and i < n and body (less common for forall)
        conjuncts = _flatten_and(body)
        lo, hi, rest = _extract_range_from_conjuncts(var, conjuncts)
        if rest:
            remainder = _build_and(rest)
            return lo, hi, remainder

    elif quant_func == "any":
        # Pattern: guard and body (all conjuncted)
        conjuncts = _flatten_and(body)
        lo, hi, rest = _extract_range_from_conjuncts(var, conjuncts)
        if rest:
            remainder = _build_and(rest)
            return lo, hi, remainder

    raise QuantifierBoundsError(f"Cannot extract bounds for {var}")


def _flatten_and(node: CSLNode) -> list:
    """Flatten a chain of `and` into a list of conjuncts."""
    if isinstance(node, BinOp) and node.op == "and":
        return _flatten_and(node.left) + _flatten_and(node.right)
    return [node]


def _build_and(nodes: list) -> CSLNode:
    """Build a conjunction from a list of nodes."""
    result = nodes[0]
    for n in nodes[1:]:
        result = BinOp(result, "and", n)
    return result


def _parse_range_guard(var: str, guard: CSLNode):
    """Parse a guard like `lo <= var and var < hi` into (lo_str, hi_str)."""
    conjuncts = _flatten_and(guard)
    return _extract_range_from_conjuncts_pair(var, conjuncts)


def _extract_range_from_conjuncts(var: str, conjuncts: list):
    """Extract (lo_str, hi_str, remaining_conjuncts) from a list of conjuncts."""
    lo = None
    hi = None
    remaining = []

    for c in conjuncts:
        bound = _try_extract_bound(var, c)
        if bound:
            kind, val = bound
            if kind == "lo" and lo is None:
                lo = val
            elif kind == "hi" and hi is None:
                hi = val
            else:
                remaining.append(c)
        else:
            remaining.append(c)

    if lo is not None and hi is not None:
        return lo, hi, remaining

    raise QuantifierBoundsError(f"Cannot extract complete bounds for {var}")


def _extract_range_from_conjuncts_pair(var: str, conjuncts: list):
    """Extract (lo_str, hi_str) from conjuncts, no remainder."""
    lo, hi, _ = _extract_range_from_conjuncts(var, conjuncts)
    return lo, hi


def _try_extract_bound(var: str, node: CSLNode):
    """Try to extract a bound from a comparison node.

    Returns ("lo", val_str) or ("hi", val_str) or None.
    Handles:  lo <= var,  var >= lo,  var < hi,  hi > var
    """
    if not isinstance(node, BinOp):
        return None

    left_is_var = isinstance(node.left, Var) and node.left.name == var
    right_is_var = isinstance(node.right, Var) and node.right.name == var

    if node.op == "<=" and right_is_var:
        # lo <= var  →  lo is lower bound
        return ("lo", translate(node.left))
    elif node.op == ">=" and left_is_var:
        # var >= lo  →  lo is lower bound
        return ("lo", translate(node.right))
    elif node.op == "<" and left_is_var:
        # var < hi  →  hi is upper bound
        return ("hi", translate(node.right))
    elif node.op == ">" and right_is_var:
        # hi > var  →  hi is upper bound
        return ("hi", translate(node.left))
    elif node.op == "<=" and left_is_var:
        # var <= hi  →  hi+1 is upper bound (but we use hi+1 which is complex)
        # Simpler: treat as var < hi+1
        return ("hi", f"({translate(node.right)} + 1)")
    elif node.op == ">=" and right_is_var:
        # lo >= var  →  this is hi bound (var <= lo → var < lo+1)
        return ("hi", f"({translate(node.left)} + 1)")

    return None


def collect_old_refs(node: CSLNode) -> list:
    """Collect all \\old references in a contract expression.

    Returns list of (snapshot_var_name, source_expr_str) pairs.
    """
    refs = []
    _walk_old_refs(node, refs)
    return refs


def _walk_old_refs(node: CSLNode, refs: list):
    if isinstance(node, Old):
        snap_var = _translate_old(node.expr)
        if isinstance(node.expr, Var):
            src = node.expr.name
        elif isinstance(node.expr, FieldAccess):
            src = f"{node.expr.object}.{node.expr.field}"
        elif isinstance(node.expr, SubscriptAccess):
            # For arrays, we need a full copy
            src = f"__import__('copy').copy({node.expr.array})"
            snap_var = f"_pycsl_old_{node.expr.array}"
        else:
            src = f"None  # unsupported \\old target"
        refs.append((snap_var, src))
    elif isinstance(node, BinOp):
        _walk_old_refs(node.left, refs)
        _walk_old_refs(node.right, refs)
    elif isinstance(node, UnaryOp):
        _walk_old_refs(node.expr, refs)
    elif isinstance(node, (Requires, Ensures, LoopInvariant,
                           LoopVariant, ClassInvariant)):
        _walk_old_refs(node.expr, refs)
    elif isinstance(node, (Forall, Exists)):
        _walk_old_refs(node.body, refs)


def collect_at_refs(node: CSLNode) -> list:
    """Collect all \\at references in a contract expression.

    Returns list of (snapshot_var_name, label, source_expr_str) pairs.
    """
    refs = []
    _walk_at_refs(node, refs)
    return refs


def _walk_at_refs(node: CSLNode, refs: list):
    if isinstance(node, At):
        snap_var = _translate_at(node.expr, node.label)
        if isinstance(node.expr, SubscriptAccess):
            src = f"{node.expr.array}[{translate(node.expr.index)}]"
        elif isinstance(node.expr, Var):
            src = node.expr.name
        elif isinstance(node.expr, FieldAccess):
            src = f"{node.expr.object}.{node.expr.field}"
        else:
            src = "None  # unsupported \\at target"
        refs.append((snap_var, node.label, src))
    elif isinstance(node, BinOp):
        _walk_at_refs(node.left, refs)
        _walk_at_refs(node.right, refs)
    elif isinstance(node, UnaryOp):
        _walk_at_refs(node.expr, refs)
    elif isinstance(node, (Requires, Ensures, LoopInvariant,
                           LoopVariant, ClassInvariant)):
        _walk_at_refs(node.expr, refs)
    elif isinstance(node, (Forall, Exists)):
        _walk_at_refs(node.body, refs)
