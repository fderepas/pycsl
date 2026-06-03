"""Formal driver for the ast stub: thin annotated wrappers over ast's
parse/walk/dump helpers. Exercises visitor dispatch via parse, walk,
and fix_missing_locations. Verified end-to-end (no \trusted) via
`pycsl src/pycsl_lib/ast_demo.py`."""
import ast


#@ requires source >= 0 and optimize >= -1
#@ ensures \result >= -1
#@ assigns \nothing
def demo_parse(source: int, optimize: int) -> int:
    """Parse source into an AST, returning a node handle (>= 0) — or -1 if the
    source is syntactically invalid. `ast.parse` is \\abstract and raises
    SyntaxError on bad input; this wrapper catches it, so it is TOTAL (never
    propagates the exception) — the C3 `check_code` parse pattern in miniature."""
    try:
        return ast.parse(source, 0, 0, 0, 0, optimize, 0)
    except SyntaxError:
        return -1


#@ requires node >= 0
#@ ensures True
#@ assigns \nothing
def demo_walk(node: int) -> int:
    """Walk an AST node; returns an iterator handle."""
    return ast.walk(node)


#@ requires node >= 0
#@ ensures \result == node
#@ assigns \nothing
def demo_fix_locations(node: int) -> int:
    """Fix missing source locations on an AST; returns the same node."""
    return ast.fix_missing_locations(node)


#@ requires node >= 0
#@ ensures True
#@ assigns \nothing
def demo_dump(node: int) -> int:
    """Dump an AST to a string representation."""
    return ast.dump(node, 0, 0, 0, 0, 0)


# ── check_code: a FunctionAnalyzer over ast.NodeVisitor (B1+B2+B4+C2) ──
# The literal "## Formal test drivers" example, rendered as a verified driver.
# WHAT IS PROVEN: the analyzer's LOGIC — `check_code` returns 0 or 1 (from the
# ternary) and is TOTAL (a `try/except SyntaxError` wrapper around the \abstract
# parser). The concrete `check_code(source_code) == 1` for a specific string is
# NOT a Why3 proof — it rests on the opaque `ast.parse` and the reflective
# `visit_<Node>` dispatch, neither of which PyCSL models. (Honest per the plan;
# the string outcome is a runtime fact, not a verified one.)
#
# FunctionAnalyzer deliberately carries NO own class invariant: a subclass that
# adds an invariant ON TOP OF an inherited base invariant currently can't be
# constructed in a driver (the merged record's two `invariant` clauses give an
# Unknown construction VC — a known gap; base-only OR sub-only invariant is
# fine). The result bound `\result ∈ {0,1}` comes from the ternary, not a field
# invariant, so the demo needs no FunctionAnalyzer invariant.
class FunctionAnalyzer(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.everything_fine = 1

    #@ ensures \result >= 0
    #@ assigns self.everything_fine
    def visit_FunctionDef(self, node: int) -> int:
        # Flag a non-lowercase function name that is not a dunder. The string
        # predicates are uninterpreted 0/1 ops (B2); the demo exercises the
        # control-flow consequence, not their concrete truth value.
        if not node.name.islower() and not (node.name.startswith('__') and node.name.endswith('__')):
            self.everything_fine = 0
        return self.generic_visit(node)


#@ requires source >= 0
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def check_code(source: int) -> int:
    try:
        tree = ast.parse(source, 0, 0, 0, 0, 0, 0)
        analyzer = FunctionAnalyzer()
        r = analyzer.visit(tree)
        return 1 if analyzer.everything_fine == 1 else 0
    except SyntaxError:
        return 0


# ── literal_eval safety (the JSON example's "why it's safe") ────────
# A try/except (ValueError, SyntaxError) wrapper around ast.literal_eval is
# TOTAL: malicious / malformed input is blocked (returns 0), never executes
# code. The safe-path dict read-back (`data['threshold'] == 42`) is DEFERRED —
# it needs `d[k]=v` and a dict-returning literal_eval (see the plan).
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def safe_literal_eval(user_input: int) -> int:
    try:
        data = ast.literal_eval(user_input)
        return 1
    except (ValueError, SyntaxError):
        return 0
