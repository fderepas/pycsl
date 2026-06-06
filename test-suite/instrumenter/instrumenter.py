"""AST rewriter that instruments annotated Python files with runtime contract checks.

Uses Modules 1–3 from the PyCSL pipeline to parse contracts, then rewrites
the Python source to inject assertions for all contract types.
"""

import ast
import sys
import os
from typing import List, Optional

# Add project root and instrumenter dir to path
_here = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.join(_here, '..', '..')
sys.path.insert(0, _project_root)
sys.path.insert(0, _here)

from Module1_Ingestor import Module1_Ingestor
from Module2_Parser import (
    Module2_Parser, CSLNode, Requires, Ensures, Assigns, LoopInvariant,
    LoopVariant, ClassInvariant, Label, Nothing, Var, FieldAccess,
    AssignsRegion, Old, SubscriptAccess
)
from Module3_Weaver import Module3_Weaver
from csl_to_python import translate, collect_old_refs, collect_at_refs


def instrument_source(source_code: str) -> str:
    """Instrument a Python source string with runtime contract checks.

    Returns the instrumented Python source.
    """
    # Step 1: Use Modules 1–3 to parse contracts and attach to AST
    ingestor = Module1_Ingestor(source_code)
    extracted = ingestor.process()
    parser = Module2_Parser()

    weaver = Module3_Weaver(source_code, extracted, parser)
    annotated_ast = weaver.process()

    # Step 2: Rewrite the AST
    rewriter = _InstrumentRewriter()
    new_ast = rewriter.visit(annotated_ast)
    ast.fix_missing_locations(new_ast)

    # Step 3: Unparse back to Python source
    return ast.unparse(new_ast)


def instrument_file(filepath: str) -> str:
    """Instrument a Python file and return the instrumented source."""
    with open(filepath, 'r') as f:
        source_code = f.read()
    return instrument_source(source_code)


class _InstrumentRewriter(ast.NodeTransformer):
    """Walks the annotated AST and injects runtime contract checks."""

    def __init__(self):
        super().__init__()
        self._class_invariants: List[CSLNode] = []
        self._current_class_name: Optional[str] = None

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        invariants = getattr(node, 'csl_class_invariants', [])
        old_invariants = self._class_invariants
        old_class = self._current_class_name
        self._class_invariants = invariants
        self._current_class_name = node.name

        self.generic_visit(node)

        # If there are class invariants, inject a checker method
        if invariants:
            checker = self._make_invariant_checker(invariants)
            node.body.insert(0, checker)

        self._class_invariants = old_invariants
        self._current_class_name = old_class
        return node

    def _make_invariant_checker(self, invariants: List[CSLNode]) -> ast.FunctionDef:
        """Create a _pycsl_check_invariant_(self) method."""
        body = []
        for inv in invariants:
            expr_str = translate(inv.expr)
            body.append(_make_assert(expr_str, f"Class invariant failed: {expr_str}"))
        return _make_function("_pycsl_check_invariant_", ["self"], body)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        self.generic_visit(node)

        requires = getattr(node, 'csl_requires', [])
        ensures = getattr(node, 'csl_ensures', [])
        assigns = getattr(node, 'csl_assigns', [])
        is_method = self._current_class_name is not None
        is_init = is_method and node.name == '__init__'

        new_body = []

        # Skip leading docstring
        doc_idx = 0
        if (node.body and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)):
            new_body.append(node.body[0])
            doc_idx = 1

        # Class invariant check at method entry (not for __init__)
        if is_method and self._class_invariants and not is_init:
            new_body.append(_make_expr_call("self._pycsl_check_invariant_"))

        # Collect \old references from ensures clauses and inject snapshots
        old_snapshots = []
        for ens in ensures:
            old_snapshots.extend(collect_old_refs(ens))

        # Deduplicate
        seen_snaps = set()
        for snap_var, src_expr in old_snapshots:
            if snap_var not in seen_snaps:
                seen_snaps.add(snap_var)
                new_body.append(_make_assign(snap_var, src_expr))

        # Preconditions
        for req in requires:
            expr_str = translate(req.expr)
            raw_contract = _contract_text(req)
            new_body.append(_make_assert(expr_str,
                                         f"Precondition failed: {raw_contract}"))

        # Frame condition snapshots (assigns)
        frame_snaps = self._make_frame_snapshots(assigns, node)
        new_body.extend(frame_snaps)

        # Process the original body, rewriting returns and loops
        original_body = node.body[doc_idx:]
        has_ensures = len(ensures) > 0
        has_invariant_check = is_method and self._class_invariants

        processed = self._process_body(original_body, ensures, assigns,
                                       has_invariant_check, is_init)
        new_body.extend(processed)

        # If function may fall through without return and has postconditions
        if has_ensures and not self._body_always_returns(processed):
            new_body.append(_make_assign("_pycsl_result_", "None"))
            for ens in ensures:
                expr_str = translate(ens.expr)
                new_body.append(_make_assert(expr_str,
                                             f"Postcondition failed: {expr_str}"))
            # Frame checks at fallthrough
            new_body.extend(self._make_frame_checks(assigns, node))
            if has_invariant_check:
                new_body.append(_make_expr_call("self._pycsl_check_invariant_"))

        node.body = new_body
        return node

    def _process_body(self, stmts, ensures, assigns, inv_check, is_init):
        """Process a list of statements, rewriting returns and loops."""
        result = []
        for stmt in stmts:
            if isinstance(stmt, ast.Return):
                result.extend(self._rewrite_return(stmt, ensures, assigns,
                                                   inv_check, is_init))
            elif isinstance(stmt, ast.While):
                result.append(self._rewrite_while(stmt))
            elif isinstance(stmt, ast.For):
                result.append(self._rewrite_for(stmt))
            elif isinstance(stmt, ast.If):
                stmt.body = self._process_body(stmt.body, ensures, assigns,
                                               inv_check, is_init)
                stmt.orelse = self._process_body(stmt.orelse, ensures, assigns,
                                                 inv_check, is_init)
                result.append(stmt)
            else:
                # Check for label annotations
                labels = getattr(stmt, 'csl_labels', [])
                if labels:
                    # Inject label snapshots (handled by ensures \at references)
                    for ens in ensures:
                        at_refs = collect_at_refs(ens)
                        for snap_var, label, src_expr in at_refs:
                            if label in labels:
                                result.append(_make_assign(snap_var, src_expr))
                result.append(stmt)
        return result

    def _rewrite_return(self, node: ast.Return, ensures, assigns,
                        inv_check, is_init):
        """Rewrite a return statement to capture result and check postconditions."""
        stmts = []

        # Capture return value
        if node.value is not None:
            capture = ast.Assign(
                targets=[ast.Name(id="_pycsl_result_", ctx=ast.Store())],
                value=node.value,
                lineno=node.lineno, col_offset=node.col_offset
            )
            stmts.append(capture)
        else:
            stmts.append(_make_assign("_pycsl_result_", "None"))

        # Postcondition checks
        for ens in ensures:
            expr_str = translate(ens.expr)
            stmts.append(_make_assert(expr_str,
                                      f"Postcondition failed: {expr_str}"))

        # Frame condition checks
        stmts.extend(self._make_frame_checks(assigns,
                                              self._current_func_node(node)))

        # Class invariant at method exit
        if inv_check:
            stmts.append(_make_expr_call("self._pycsl_check_invariant_"))

        # Actual return
        ret = ast.Return(
            value=ast.Name(id="_pycsl_result_", ctx=ast.Load()),
            lineno=node.lineno, col_offset=node.col_offset
        )
        stmts.append(ret)
        return stmts

    def _rewrite_while(self, node: ast.While) -> ast.While:
        """Inject loop invariant and variant checks around a while loop."""
        invariants = getattr(node, 'csl_invariants', [])
        variants = getattr(node, 'csl_variants', [])

        pre_stmts = []
        post_body = []
        post_loop = []

        # Invariant: check before loop
        for inv in invariants:
            expr_str = translate(inv.expr)
            pre_stmts.append(_make_assert(expr_str,
                                          f"Loop invariant init failed: {expr_str}"))

        # Variant: capture initial value before loop
        for i, var in enumerate(variants):
            expr_str = translate(var.expr)
            pre_stmts.append(_make_assign(f"_pycsl_variant_prev_{i}", expr_str))
            pre_stmts.append(_make_assert(
                f"_pycsl_variant_prev_{i} >= 0",
                f"Loop variant not non-negative at entry"))

        # End of iteration: check invariant preservation + variant decrease
        for inv in invariants:
            expr_str = translate(inv.expr)
            post_body.append(_make_assert(expr_str,
                                          f"Loop invariant preservation failed: {expr_str}"))

        for i, var in enumerate(variants):
            expr_str = translate(var.expr)
            post_body.append(_make_assign(f"_pycsl_variant_cur_{i}", expr_str))
            post_body.append(_make_assert(
                f"_pycsl_variant_cur_{i} >= 0",
                "Loop variant negative"))
            post_body.append(_make_assert(
                f"_pycsl_variant_cur_{i} < _pycsl_variant_prev_{i}",
                "Loop variant not decreasing"))
            post_body.append(_make_assign(f"_pycsl_variant_prev_{i}",
                                          f"_pycsl_variant_cur_{i}"))

        # Invariant: check after loop exits
        for inv in invariants:
            expr_str = translate(inv.expr)
            post_loop.append(_make_assert(expr_str,
                                          f"Loop invariant at exit failed: {expr_str}"))

        # Handle continue statements: insert invariant checks before each continue
        node.body = self._inject_before_continue(node.body, invariants, variants)

        # Append post-iteration checks to the loop body
        node.body.extend(post_body)

        # Build: pre_stmts + while + post_loop
        # We wrap this in an If(True) block to keep it as a single statement
        # Actually, we return a wrapper. The caller should flatten.
        # For simplicity, we modify the node and create a compound.
        wrapper_body = pre_stmts + [node] + post_loop
        if len(wrapper_body) == 1:
            return wrapper_body[0]
        # Return a compound as a module-level block
        # Use If(True) as a no-op wrapper to group statements
        # Actually, let's just return the while and handle pre/post outside
        # The cleanest approach: store pre/post on the node
        node._pycsl_pre = pre_stmts
        node._pycsl_post = post_loop
        return node

    def _rewrite_for(self, node: ast.For) -> ast.For:
        """Same as while, for `for` loops."""
        invariants = getattr(node, 'csl_invariants', [])
        variants = getattr(node, 'csl_variants', [])

        pre_stmts = []
        post_body = []
        post_loop = []

        for inv in invariants:
            expr_str = translate(inv.expr)
            pre_stmts.append(_make_assert(expr_str,
                                          f"Loop invariant init failed: {expr_str}"))

        for i, var in enumerate(variants):
            expr_str = translate(var.expr)
            pre_stmts.append(_make_assign(f"_pycsl_variant_prev_{i}", expr_str))
            pre_stmts.append(_make_assert(
                f"_pycsl_variant_prev_{i} >= 0",
                "Loop variant not non-negative at entry"))

        for inv in invariants:
            expr_str = translate(inv.expr)
            post_body.append(_make_assert(expr_str,
                                          f"Loop invariant preservation failed: {expr_str}"))

        for i, var in enumerate(variants):
            expr_str = translate(var.expr)
            post_body.append(_make_assign(f"_pycsl_variant_cur_{i}", expr_str))
            post_body.append(_make_assert(
                f"_pycsl_variant_cur_{i} >= 0",
                "Loop variant negative"))
            post_body.append(_make_assert(
                f"_pycsl_variant_cur_{i} < _pycsl_variant_prev_{i}",
                "Loop variant not decreasing"))
            post_body.append(_make_assign(f"_pycsl_variant_prev_{i}",
                                          f"_pycsl_variant_cur_{i}"))

        for inv in invariants:
            expr_str = translate(inv.expr)
            post_loop.append(_make_assert(expr_str,
                                          f"Loop invariant at exit failed: {expr_str}"))

        node.body = self._inject_before_continue(node.body, invariants, variants)
        node.body.extend(post_body)

        node._pycsl_pre = pre_stmts
        node._pycsl_post = post_loop
        return node

    def _inject_before_continue(self, stmts, invariants, variants):
        """Insert invariant checks before every `continue` statement."""
        result = []
        for stmt in stmts:
            if isinstance(stmt, ast.Continue):
                for inv in invariants:
                    expr_str = translate(inv.expr)
                    result.append(_make_assert(expr_str,
                                               f"Loop invariant before continue: {expr_str}"))
                for i, var in enumerate(variants):
                    expr_str = translate(var.expr)
                    result.append(_make_assign(f"_pycsl_variant_cur_{i}", expr_str))
                    result.append(_make_assert(
                        f"_pycsl_variant_cur_{i} >= 0",
                        "Loop variant negative"))
                    result.append(_make_assert(
                        f"_pycsl_variant_cur_{i} < _pycsl_variant_prev_{i}",
                        "Loop variant not decreasing"))
                    result.append(_make_assign(f"_pycsl_variant_prev_{i}",
                                               f"_pycsl_variant_cur_{i}"))
                result.append(stmt)
            elif isinstance(stmt, ast.If):
                stmt.body = self._inject_before_continue(stmt.body, invariants, variants)
                stmt.orelse = self._inject_before_continue(stmt.orelse, invariants, variants)
                result.append(stmt)
            else:
                result.append(stmt)
        return result

    def _make_frame_snapshots(self, assigns_list, func_node):
        """Create snapshot assignments for frame condition checking."""
        stmts = []
        for assigns_contract in assigns_list:
            for target in assigns_contract.targets:
                if isinstance(target, Nothing):
                    # Snapshot all mutable params
                    params = self._get_func_params(func_node)
                    for p in params:
                        stmts.append(_make_assign_raw(
                            f"_pycsl_frame_{p}",
                            f"__import__('copy').copy({p}) if isinstance({p}, list) else {p}"
                        ))
                elif isinstance(target, AssignsRegion):
                    stmts.append(_make_assign_raw(
                        f"_pycsl_frame_{target.base}",
                        f"list({target.base})"
                    ))
        return stmts

    def _make_frame_checks(self, assigns_list, func_node):
        """Create assertions that verify frame conditions at function exit."""
        stmts = []
        for assigns_contract in assigns_list:
            for target in assigns_contract.targets:
                if isinstance(target, Nothing):
                    params = self._get_func_params(func_node)
                    for p in params:
                        stmts.append(_make_assert(
                            f"(not isinstance({p}, list) or {p} == _pycsl_frame_{p})"
                            f" and (isinstance({p}, list) or {p} == _pycsl_frame_{p})",
                            f"Frame condition violated: {p} was modified but assigns \\nothing"
                        ))
                elif isinstance(target, AssignsRegion):
                    lo_str = translate(target.low)
                    hi_str = translate(target.high)
                    base = target.base
                    stmts.append(_make_assert(
                        f"_pycsl_frame_{base}[:{lo_str}] == {base}[:{lo_str}]"
                        f" and _pycsl_frame_{base}[{hi_str}:] == {base}[{hi_str}:]",
                        f"Frame condition violated: {base} modified outside [{lo_str}..{hi_str})"
                    ))
        return stmts

    def _get_func_params(self, func_node) -> List[str]:
        """Extract parameter names from a function node."""
        if func_node is None:
            return []
        if isinstance(func_node, ast.FunctionDef):
            return [arg.arg for arg in func_node.args.args if arg.arg != 'self']
        return []

    def _current_func_node(self, node):
        """Placeholder — ideally would track the enclosing function."""
        return None

    def _body_always_returns(self, stmts) -> bool:
        """Check if every code path in stmts ends with a return."""
        if not stmts:
            return False
        last = stmts[-1]
        if isinstance(last, ast.Return):
            return True
        if isinstance(last, ast.If):
            return (self._body_always_returns(last.body)
                    and self._body_always_returns(last.orelse))
        return False

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """Process the module, flattening loop pre/post statements."""
        self.generic_visit(node)
        node.body = self._flatten_loop_wrappers(node.body)
        return node

    def _flatten_loop_wrappers(self, stmts):
        """Flatten _pycsl_pre/_pycsl_post attached to loop nodes."""
        result = []
        for stmt in stmts:
            pre = getattr(stmt, '_pycsl_pre', [])
            post = getattr(stmt, '_pycsl_post', [])
            result.extend(pre)

            # Recurse into compound statements
            if isinstance(stmt, ast.FunctionDef):
                stmt.body = self._flatten_loop_wrappers(stmt.body)
            elif isinstance(stmt, (ast.While, ast.For)):
                stmt.body = self._flatten_loop_wrappers(stmt.body)
            elif isinstance(stmt, ast.If):
                stmt.body = self._flatten_loop_wrappers(stmt.body)
                stmt.orelse = self._flatten_loop_wrappers(stmt.orelse)
            elif isinstance(stmt, ast.ClassDef):
                stmt.body = self._flatten_loop_wrappers(stmt.body)

            result.append(stmt)
            result.extend(post)
        return result


# ── AST construction helpers ─────────────────────────────────────────

def _make_assert(expr_str: str, msg: str) -> ast.Assert:
    """Create an assert statement from a Python expression string."""
    test = ast.parse(expr_str, mode='eval').body
    return ast.Assert(
        test=test,
        msg=ast.Constant(value=msg),
        lineno=0, col_offset=0
    )


def _make_assign(target_name: str, value_expr_str: str) -> ast.Assign:
    """Create: target_name = value_expr_str"""
    value = ast.parse(value_expr_str, mode='eval').body
    return ast.Assign(
        targets=[ast.Name(id=target_name, ctx=ast.Store())],
        value=value,
        lineno=0, col_offset=0
    )


def _make_assign_raw(target_name: str, value_expr_str: str) -> ast.Assign:
    """Create an assignment, handling complex expressions."""
    try:
        value = ast.parse(value_expr_str, mode='eval').body
    except SyntaxError:
        value = ast.Constant(value=None)
    return ast.Assign(
        targets=[ast.Name(id=target_name, ctx=ast.Store())],
        value=value,
        lineno=0, col_offset=0
    )


def _make_expr_call(call_str: str) -> ast.Expr:
    """Create an expression statement: call_str()"""
    call = ast.parse(f"{call_str}()", mode='eval').body
    return ast.Expr(value=call, lineno=0, col_offset=0)


def _make_function(name: str, args: List[str], body: List[ast.stmt]) -> ast.FunctionDef:
    """Create a simple function definition."""
    if not body:
        body = [ast.Pass(lineno=0, col_offset=0)]
    return ast.FunctionDef(
        name=name,
        args=ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg=a, lineno=0, col_offset=0) for a in args],
            vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]
        ),
        body=body,
        decorator_list=[],
        returns=None,
        lineno=0, col_offset=0
    )


def _contract_text(node: CSLNode) -> str:
    """Get a human-readable text of a contract for error messages."""
    return translate(node.expr) if hasattr(node, 'expr') else str(node)
