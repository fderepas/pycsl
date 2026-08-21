from __future__ import annotations
from frontend import pure_ast as ast
import warnings
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, fields as _dc_fields, is_dataclass as _is_dc, replace as _dc_replace
from frontend.Module2_Parser import CSLNode, Requires, Ensures, Assigns, LoopInvariant, LoopVariant, ClassInvariant, Label as CSLLabel, FunctionVariant, Diverges, NoInline, SiblingConcrete, VerifyModule, PropagateFrame, FreshGlobals, Trusted, Abstract, Lemma, Uses, InterfaceClause, Reveal, GhostAssignDecl, GhostArraySetDecl, RaisesDecl, NoExceptionDecl, AllowFinalizerDecl, AllowIterationMutationDecl, BoundedIntDecl, ProofDecl, SharedDecl, DatatypeDecl, InductiveDecl, ThreadEntry, Acquires, Releases, CriticalSection, MutexInvariant, LockOrder, BinOp, Number, Act, ForExpand, Given, Complete, Disjoint, Old, UnaryOp, CSLBool, CheckPoint, HappyProperty, Preserves, Footprint, Var, Forall, FieldSubscript, MixinDecl, ProvidesDecl, SharedStateDecl, TouchesFieldDecl, MethodDependencyDecl, ComposeFromDecl, ConformsToDecl
import copy
from errors import PyCSLSemanticError
from frontend.Module1_Ingestor import PyCSLContract
""  # pycsl
class PyCSLWeaver(ast.NodeVisitor):
    '\n    Traverses the standard Python AST and injects parsed contract nodes \n    directly into the AST objects.\n    '
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self, contracts_map: Dict[int, List[CSLNode]]) -> None:
        self.contracts_map = contracts_map

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _init_function_csl_fields(node: ast.FunctionDef) -> None:
        pass

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _act_guard(act: Act) -> "ExprIR":
        """The act's guard: the conjunction of its `given` clauses (`True` if none)."""
        givens = [cl.expr for cl in act.clauses if isinstance(cl, Given)]
        if not givens:
            return CSLBool(True)
        g = givens[0]
        for extra in givens[1:]:
            g = BinOp(g, "and", extra)
        return g

    #@ requires True
    #@ ensures \result == node.value
    #@ assigns \nothing
    @staticmethod
    def _const_int(node: Any, var: str) -> int:
        if isinstance(node, Number) and float(node.value).is_integer():
            return int(node.value)
        raise PyCSLSemanticError(
            f"`for {var} in range(...)`: range bound must be an integer literal "
            f"(got {type(node).__name__}); named-constant bounds are not yet supported",
            stage="Module3")

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _subst_var(node: Any, var: str, m: int) -> Any:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _desugar_for(contracts: List[Any]) -> List[Any]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _desugar_acts(contracts: List[Any]) -> Tuple[List[Any], List[Any]]:
        return ([], {})

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _extract_mixin_directives(node: ast.FunctionDef, contracts: List[Any]) -> List[Any]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _dispatch_function_contracts(node: ast.FunctionDef, contracts: List[Any]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _validate_function_contracts(node: ast.FunctionDef) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def visit_Module(self, node: ast.Module) -> Any:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def visit_With(self, node: ast.With) -> Any:
        return None

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _is_trivial_new(fn: ast.FunctionDef) -> bool:
        body = [s for s in fn.body
                if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
        if len(body) != 1 or not isinstance(body[0], ast.Return):
            return False
        val = body[0].value
        if not (isinstance(val, ast.Call) and isinstance(val.func, ast.Attribute)
                and val.func.attr == "__new__"):
            return False
        recv = val.func.value
        if (isinstance(recv, ast.Call) and isinstance(recv.func, ast.Name)
                and recv.func.id == "super"):
            return True
        if isinstance(recv, ast.Name) and recv.id == "object":
            return True
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _attach_loop_contracts(node, contracts) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def visit_While(self, node: ast.While) -> Any:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def visit_For(self, node: ast.For) -> Any:
        return None


class Module3_Weaver:
    '\n    Coordinates the standard AST generation and the injection of contracts.\n    '
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self, source_code: str, extracted_data: List[PyCSLContract], parser_module: Any) -> None:
        self.source_code = source_code
        self.extracted_data = extracted_data
        self.parser_module = parser_module

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _parse_extracted_contracts(self) -> Tuple[Dict[int, List[CSLNode]], Dict[int, List[CSLNode]]]:
        return ([], {})

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _consolidate_module_concurrency(python_ast: ast.AST, contracts_map: Dict[int, List[CSLNode]]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _attach_labels_and_ghost_assigns(python_ast: ast.AST, contracts_map: Dict[int, List[CSLNode]], trailing_contracts_map: Dict[int, List[CSLNode]]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns contracts_map
    @staticmethod
    def _extract_happy_properties(contracts_map: Dict[int, List[CSLNode]]) -> List[HappyProperty]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _field_write_site(stmt: ast.stmt, field: str):
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _happy_predicate(self, hp: HappyProperty, site: dict, line: int) -> CSLNode:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _expand_happy_properties(self, python_ast: ast.AST, happy_props: List[HappyProperty]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _region_bound_str(node: CSLNode) -> str:
        return ""

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _canonical_preservation_ensures(hp: HappyProperty) -> "ExprIR":
        v = "__happy_i"
        guard = BinOp(BinOp(copy.deepcopy(hp.region_lo), "<=", Var(v)),
                      "and",
                      BinOp(Var(v), "<", copy.deepcopy(hp.region_hi)))
        eq = BinOp(FieldSubscript(hp.field, Var(v)),
                   "==",
                   Old(FieldSubscript(hp.field, Var(v))))
        return Ensures(Forall(v, BinOp(guard, "==>", eq)))

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _target_dotted_path(target: ast.AST):
        pass

    #@ requires True
    #@ ensures True
    #@ assigns out
    def _collect_protect_sites(self, node: ast.AST, protected: set, cur_func, out: List[tuple]) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                tgts = child.targets if isinstance(child, ast.Assign) else [child.target]
                for tgt in tgts:
                    p = self._target_dotted_path(tgt)
                    if p in protected:
                        out.append((child, cur_func, p))
            inner = child.name if isinstance(child, ast.FunctionDef) else cur_func
            self._collect_protect_sites(child, protected, inner, out)

    #@ requires True
    #@ ensures True
    #@ assigns out
    def _collect_protect_index_sites(self, node: ast.AST, path: str, cur_func, out: List[tuple]) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                tgts = child.targets if isinstance(child, ast.Assign) else [child.target]
                for tgt in tgts:
                    if isinstance(tgt, ast.Subscript) and \
                            self._target_dotted_path(tgt.value) == path:
                        sl = tgt.slice
                        if isinstance(sl, ast.Index):
                            sl = sl.value
                        if not isinstance(sl, ast.Slice):
                            out.append((child, cur_func, sl))
            inner = child.name if isinstance(child, ast.FunctionDef) else cur_func
            self._collect_protect_index_sites(child, path, inner, out)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _subst_csl_param(node, param_name: str, repl):
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _check_protect_aliasing(self, node: ast.AST, protected: set, except_set: set, cur_func, hp_name: str) -> None:
        pass

    #@ requires True
    #@ ensures True
    #@ assigns out
    def _collect_field_sites(self, node: ast.AST, field: str, cur_func, out: List[tuple]) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                site = self._field_write_site(child, field)
                if site is not None:
                    out.append((child, site, cur_func))
            inner_func = child.name if isinstance(child, ast.FunctionDef) else cur_func
            self._collect_field_sites(child, field, inner_func, out)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _subscript_read_site(sub: ast.Subscript, field: str):
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_self_call_sites(self, node: ast.AST, target: str, cur_func, cur_stmt, out: List[tuple]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _synthesize_selfcomp(self, python_ast: ast.AST, hp: HappyProperty) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_field_read_sites(self, node: ast.AST, field: str, cur_func, cur_stmt, out: List[tuple]) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def process(self) -> ast.AST:
        return None


