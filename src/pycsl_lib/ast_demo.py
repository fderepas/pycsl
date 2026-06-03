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
