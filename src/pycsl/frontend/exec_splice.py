"""07-1839 P5b — constant `exec("…")` straight-line splice (the TOOL parser family).

A call `exec("<source>")` whose argument is a compile-time string CONSTANT is the same parser
front-end the toolchain already runs (`pure_ast.parse`), so the statements it would execute are
known at verification time. This pass replaces the `exec(...)` expression-statement with the parsed
statements spliced in place — making the code verification-equivalent to writing those statements
inline (08-0350-spec-rev4 §8.5).

Soundness rests on the WHITELIST, not on constancy: only straight-line assignments and pure
expression-statements are admitted. ALL control flow (`return`/`if`/`while`/`for`/`with`/`try`/
`break`/`continue`), `import`, nested `def`/`class`, and nested `exec` are REJECTED (fail-loud) —
splicing them would alter the control-flow graph, breaking the inline-equivalence. Invariant-bearing
loops are a separate CFG-aware sub-phase (P5e).

A DYNAMIC `exec` (non-constant argument) is left untouched here; it is handled conservatively
downstream (scope havoc + frame taint, P5a/P5a').
"""
from __future__ import annotations

from frontend import pure_ast as ast
from errors import PyCSLParseError

# Straight-line only: assignments and pure expression statements. Anything else changes the CFG.
_WHITELIST = (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Expr)


def _is_constant_exec(call: object) -> bool:
    return (isinstance(call, ast.Call)
            and isinstance(getattr(call, "func", None), ast.Name)
            and call.func.id == "exec"
            and len(getattr(call, "args", [])) == 1
            and isinstance(call.args[0], ast.Constant)
            and isinstance(call.args[0].value, str))


def _contains_exec(node: object) -> bool:
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call) and isinstance(getattr(sub, "func", None), ast.Name) \
                and sub.func.id == "exec":
            return True
    return False


class _ExecSplicer(ast.NodeTransformer):
    def visit_Expr(self, node):
        self.generic_visit(node)
        val = getattr(node, "value", None)
        if not _is_constant_exec(val):
            return node
        src = val.args[0].value
        try:
            spliced = ast.parse(src).body
        except Exception as exc:  # noqa: BLE001 — surface any parser failure as a syntax error
            raise PyCSLParseError(f"exec(...) literal failed to parse: {exc}")
        for stmt in spliced:
            if not isinstance(stmt, _WHITELIST):
                raise PyCSLParseError(
                    f"exec(...) splice rejects '{type(stmt).__name__}': only straight-line "
                    f"assignments and pure expressions are allowed (control flow, import, "
                    f"def/class, nested exec are forbidden — they would change the CFG)")
            if _contains_exec(stmt):
                raise PyCSLParseError("exec(...) splice rejects a nested exec(...)")
            ast.copy_location(stmt, node)
            ast.fix_missing_locations(stmt)
        # NodeTransformer splices a returned list of statements in place of the single Expr.
        return spliced if spliced else node


def splice_constant_exec(tree: ast.AST) -> ast.AST:
    """Replace every constant-`exec` expression-statement with its parsed straight-line body.
    No-op (byte-identical emission) for any file that contains no constant `exec`."""
    return _ExecSplicer().visit(tree)
