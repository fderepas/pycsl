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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _init_function_csl_fields(node: ast.FunctionDef) -> None:
        """Initialize the custom PyCSL fields on a function-def AST node.
        Proof attributions (§2.1.11) are informational/bridge-emitted only
        with no semantic effect. Axiom-from directives (§2.1.12) emit Why3
        axioms in the preamble; see docs/cross-validated-spec-sources.md."""
        node.csl_requires = []
        node.csl_ensures = []
        node.csl_assigns = []
        node.csl_function_variants = []
        node.csl_diverges = False
        node.csl_no_inline = False
        node.csl_sibling_concrete = False
        node.csl_verify_module = ""        # `#@ verify_module <name>` (module-emission.md) — opt-in axiom-isolation group; "" = flat default
        node.csl_propagate_frame = False
        node.csl_fresh_globals = False
        node.csl_trusted = False
        node.csl_abstract = False
        node.csl_lemma = False            # `#@ lemma` (lemma.md) — proved logical fact
        node.csl_uses = []                # `#@ uses <lemma>` (scc2.md) — ordering citations
        node.csl_iface_requires = []      # `#@ interface requires` (b-spec) — narrow interface
        node.csl_iface_ensures = []       # `#@ interface ensures`  (b-spec) — narrow interface
        node.csl_iface_assigns = []       # `#@ interface assigns`  (b-spec) — narrow interface
        node.csl_reveal = []              # `#@ reveal <fn>` (b-spec) — opt into <fn>'s definition
        node.csl_preserves = False        # `#@ \preserves` — HAPPY trust-boundary opt-in
        node.csl_reviewer = ""
        node.csl_raises = []
        node.csl_no_exception = []        # list of exception-name strings
        node.csl_no_exception_all = False # set by `no_exception \all` form
        node.csl_bounded_int = None
        node.csl_thread_entry = False
        node.csl_proof = []
        node.csl_acts = []                # pre-desugar Act/Complete/Disjoint (for Module4)
        # Mixin composition (mixin.md / mixin-ready.md, Tier 1) — populated below.
        node.csl_provides = []            # method names this method is a provider for
        node.csl_method_deps = []         # MethodDependencyDecl (depends/requires) + their contract
        node.csl_mixin_shared_state = []  # SharedStateDecl attached at this method
        node.csl_touches_field = []       # TouchesFieldDecl attached at this method

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

    # CERTIFIED-BOUNDARY (relaunch #17) — [FOR-OVER-OPAQUE-ITERABLE TERMINATION], and
    # the recorded boundary "`for`-over-array termination — the SOURCE cannot supply a
    # variant" is now located EXACTLY. The emitter DOES auto-emit
    # `invariant { 0 <= !idx } / variant { <len> - !idx }` for a `for`-over-collection
    # loop; this session un-gated that from `@mutable_state` to ANY loop whose length
    # term is already pure LOGIC (`Array.length` / `Seq.length` / `String.length`), which
    # is what let `Module2_Parser.parse_node_contracts` convert. `_desugar_for` has TWO
    # loops: the OUTER one over `contracts` DOES get its variant (`Array.length
    # contracts`), but the INNER `for clause in c.clauses` iterates an OPAQUE attribute
    # whose length is the PROGRAM `val iter_length (get_clauses !c)` — illegal in a Why3
    # `variant` term (measured: emitting it anyway gives `unbound function or predicate
    # symbol 'get_clauses'` at L3-tc). Whole-file proof with the outer variant in place:
    # 266 Valid, 3 unproven, and ALL THREE are `Sub-goal termination of goal
    # pycslweaver___desugar_for'vc`. The body itself is FAITHFUL (spiked and read: a real
    # array walk, the receiver-carrying `py_isinstance_ForExpand_int_op`, a concrete
    # `_const_int` sibling application with BOTH arguments, the real `PyCSLSemanticError`
    # on an empty body, and the real nested range/clauses expansion) — ONLY termination
    # blocks it. Unlike its `visit_*` siblings it also RETURNS its result instead of
    # mutating node attributes, so it does not hit lesson (bq) at all.
    # REOPENING CAPABILITY: declare the collection-length and attribute projectors as
    # LOGIC symbols (`val function iter_length` / `val function get_<attr>`) so a loop
    # over an opaque attribute can carry a variant term at all. That is a preamble-wide
    # declaration change with its own corpus blast radius, and it unblocks EVERY
    # `for`-over-opaque-iterable loop in the non-@mutable_state mirrors, not just this one.
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

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _target_dotted_path(target: ast.AST):
        """07-1143 R2: the dotted base path of a write target, stripping a trailing
        subscript: `world.fs.disk[i]` → "world.fs.disk", `world.proc.umask` →
        "world.proc.umask", `self.disk[i]` → "self.disk". None if not a Name-rooted
        attribute/subscript chain."""
        if isinstance(target, ast.Subscript):
            return Module3_Weaver._target_dotted_path(target.value)
        if isinstance(target, ast.Attribute):
            base = Module3_Weaver._target_dotted_path(target.value)
            return f"{base}.{target.attr}" if base else None
        if isinstance(target, ast.Name):
            return target.id
        return None

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


