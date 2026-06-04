from __future__ import annotations

import pure_ast as ast  # PyCSL toolchain parses Python via its own pure-Python
                        # front-end (no stdlib `ast` / CPython `compile`).
import warnings
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

# Import the AST nodes from Module 2
from Module2_Parser import (
    CSLNode, Requires, Ensures, Assigns, LoopInvariant, LoopVariant,
    ClassInvariant, Label as CSLLabel, FunctionVariant, Diverges, Trusted, Abstract,
    GhostAssignDecl, GhostArraySetDecl, RaisesDecl, NoExceptionDecl,
    AllowFinalizerDecl, AllowIterationMutationDecl,
    BoundedIntDecl, ProofDecl,
    SharedDecl, ThreadEntry, Acquires, Releases, CriticalSection,
    MutexInvariant, LockOrder, BinOp, Number,
    Act, Given, Complete, Disjoint, Old, UnaryOp, CSLBool,
    CheckPoint, HappyProperty, Preserves, Var, Forall, FieldSubscript,
)
import copy
from errors import PyCSLSemanticError
from Module1_Ingestor import PyCSLContract

# ---------------------------------------------------------
# 1. The AST Weaver
# ---------------------------------------------------------

class PyCSLWeaver(ast.NodeVisitor):
    """
    Traverses the standard Python AST and injects parsed contract nodes 
    directly into the AST objects.
    """
    def __init__(self, contracts_map: Dict[int, List[CSLNode]]) -> None:
        # We index the parsed contracts by the line number of the target node
        self.contracts_map = contracts_map

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
        node.csl_trusted = False
        node.csl_abstract = False
        node.csl_preserves = False        # `#@ \preserves` — HAPPY trust-boundary opt-in
        node.csl_reviewer = ""
        node.csl_raises = []
        node.csl_no_exception = []        # list of exception-name strings
        node.csl_no_exception_all = False # set by `no_exception \all` form
        node.csl_bounded_int = None
        node.csl_thread_entry = False
        node.csl_proof = []
        node.csl_acts = []                # pre-desugar Act/Complete/Disjoint (for Module4)

    @staticmethod
    def _act_guard(act: Act) -> CSLNode:
        """The act's guard: the conjunction of its `given` clauses (`True` if none)."""
        givens = [cl.expr for cl in act.clauses if isinstance(cl, Given)]
        if not givens:
            return CSLBool(True)
        g = givens[0]
        for extra in givens[1:]:
            g = BinOp(g, "and", extra)
        return g

    @staticmethod
    def _desugar_acts(contracts: List[Any]) -> Tuple[List[Any], List[Any]]:
        """Expand `act`/`complete`/`disjoint` into ordinary requires/ensures using
        the existing `==>` and `\\old`. A behavior `ensures E` under guard `A`
        becomes `ensures \\old(A) ==> E`; a `requires R` becomes `requires A ==> R`;
        `complete` becomes `ensures \\old(A1) || …`; `disjoint` becomes a per-pair
        `ensures not(\\old(Ai) && \\old(Aj))`. Returns (desugared_contracts,
        original_act_nodes). Unknown `complete`/`disjoint` names are dropped here and
        flagged by Module4 (`_validate_acts`)."""
        guards = {c.name: PyCSLWeaver._act_guard(c) for c in contracts if isinstance(c, Act)}
        out: List[Any] = []
        acts_meta: List[Any] = []
        entry_cps: List[Any] = []   # function-entry `#@ assert` for complete/disjoint
        for c in contracts:
            if isinstance(c, Act):
                acts_meta.append(c)
                A = guards[c.name]
                for cl in c.clauses:
                    if isinstance(cl, Requires):
                        out.append(Requires(BinOp(A, "==>", cl.expr)))
                    elif isinstance(cl, Ensures):
                        e = Ensures(BinOp(Old(A), "==>", cl.expr))
                        e.act_name = c.name                  # attribution (Module6 tag)
                        out.append(e)
                    elif isinstance(cl, Assigns):
                        out.append(cl)                       # §6: hoare no-op; pass through
                    # Given clauses are folded into the guard above.
            elif isinstance(c, Complete):
                acts_meta.append(c)
                # Function-entry assert: at entry the state IS the pre-state, so the
                # guards need no `\old`, and the obligation is discharged on ALL paths
                # (not just normal return) — discharging `Pre ⟹ ⋁ gᵢ`.
                gs = [guards[n] for n in c.names if n in guards]
                if gs:
                    disj = gs[0]
                    for g in gs[1:]:
                        disj = BinOp(disj, "or", g)
                    entry_cps.append(CheckPoint("assert", disj))
            elif isinstance(c, Disjoint):
                acts_meta.append(c)
                present = [n for n in c.names if n in guards]
                for i in range(len(present)):
                    for j in range(i + 1, len(present)):
                        pair = BinOp(guards[present[i]], "and", guards[present[j]])
                        entry_cps.append(CheckPoint("assert", UnaryOp("not", pair)))
            else:
                out.append(c)
        return out, acts_meta, entry_cps

    @staticmethod
    def _dispatch_function_contracts(node: ast.FunctionDef, contracts: List[Any]) -> None:
        """Attach each parsed contract node to the matching `csl_*` field
        on the function-def AST node. Acts are desugared to requires/ensures first."""
        contracts, node.csl_acts, entry_cps = PyCSLWeaver._desugar_acts(contracts)
        # complete/disjoint become function-entry `#@ assert` checkpoints on the
        # first body statement (discharged under the preconditions, on all paths).
        if entry_cps and getattr(node, "body", None):
            first = node.body[0]
            first.csl_checkpoints = list(entry_cps) + getattr(first, "csl_checkpoints", [])
        for c in contracts:
            if isinstance(c, Requires):
                node.csl_requires.append(c)
            elif isinstance(c, Ensures):
                node.csl_ensures.append(c)
            elif isinstance(c, Assigns):
                node.csl_assigns.append(c)
            elif isinstance(c, FunctionVariant):
                node.csl_function_variants.append(c)
            elif isinstance(c, Diverges):
                node.csl_diverges = True
            elif isinstance(c, Trusted):
                node.csl_trusted = True
                node.csl_reviewer = c.reviewer
                if not c.reviewer:
                    warnings.warn(
                        f"Function '{node.name}' (line {node.lineno}): "
                        f"\\trusted has no reviewer — add `reviewer: <name>` "
                        f"to document who is accountable for this trust assumption.",
                        stacklevel=2,
                    )
            elif isinstance(c, Abstract):
                node.csl_abstract = True
            elif isinstance(c, Preserves):
                node.csl_preserves = True
            elif isinstance(c, RaisesDecl):
                node.csl_raises.append(c)
            elif isinstance(c, NoExceptionDecl):
                if c.all_form:
                    node.csl_no_exception_all = True
                else:
                    for exc in c.exceptions:
                        if exc not in node.csl_no_exception:
                            node.csl_no_exception.append(exc)
            elif isinstance(c, BoundedIntDecl):
                node.csl_bounded_int = c.size
            elif isinstance(c, ProofDecl):
                node.csl_proof.append(c)
            elif isinstance(c, ThreadEntry):
                node.csl_thread_entry = True

    @staticmethod
    def _validate_function_contracts(node: ast.FunctionDef) -> None:
        """Post-attachment sanity checks: vacuous \\trusted ensures clauses
        get a warning; \\variant+\\diverges combination is a hard error."""
        if node.csl_trusted:
            for ens in node.csl_ensures:
                if (isinstance(ens.expr, BinOp) and ens.expr.op == '=='
                        and isinstance(ens.expr.left, Number)
                        and int(ens.expr.left.value) == 1
                        and isinstance(ens.expr.right, Number)
                        and int(ens.expr.right.value) == 1):
                    warnings.warn(
                        f"Function '{node.name}' (line {node.lineno}): "
                        f"\\trusted with vacuous 'ensures 1 == 1' — strengthen "
                        f"the contract or document why no property is verifiable.",
                        stacklevel=2,
                    )
        if node.csl_function_variants and node.csl_diverges:
            raise ValueError(
                f"Function '{node.name}' (line {node.lineno}): "
                f"\\variant and \\diverges are contradictory — "
                f"one asserts termination, the other denies it."
            )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self._init_function_csl_fields(node)
        # In standard `ast`, node.lineno points to the 'def' keyword.
        if node.lineno in self.contracts_map:
            self._dispatch_function_contracts(node, self.contracts_map[node.lineno])
        self._validate_function_contracts(node)
        self.generic_visit(node)

    def visit_Module(self, node: ast.Module) -> Any:
        """Attach module-level concurrency annotations (shared, mutex_invariant, lock_order)."""
        node.csl_shared_decls = []
        node.csl_mutex_invariants = {}
        node.csl_lock_order = None
        node.csl_happy_properties = []   # populated by Module3_Weaver.process (hoisted)

        if 0 in self.contracts_map:
            for c in self.contracts_map[0]:
                if isinstance(c, SharedDecl):
                    node.csl_shared_decls.append(c)
                elif isinstance(c, MutexInvariant):
                    node.csl_mutex_invariants[c.mutex] = c.expr
                elif isinstance(c, LockOrder):
                    node.csl_lock_order = c

        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> Any:
        """Attach acquire/release/critical annotations to with statements."""
        node.csl_critical_mutex = None
        node.csl_acquires = None
        node.csl_releases = None

        if node.lineno in self.contracts_map:
            for c in self.contracts_map[node.lineno]:
                if isinstance(c, CriticalSection):
                    node.csl_critical_mutex = c.mutex
                elif isinstance(c, Acquires):
                    node.csl_acquires = c.mutex
                elif isinstance(c, Releases):
                    node.csl_releases = c.mutex

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        node.csl_class_invariants = []
        node.csl_allow_finalizer = False   # UB-7.5 opt-in

        if node.lineno in self.contracts_map:
            contracts = self.contracts_map[node.lineno]
            for c in contracts:
                if isinstance(c, ClassInvariant):
                    node.csl_class_invariants.append(c)
                elif isinstance(c, AllowFinalizerDecl):
                    node.csl_allow_finalizer = True

        # UB-7.5: reject classes with `__del__` unless explicitly opted
        # in via #@ allow_finalizer. The finalizer protocol is
        # non-deterministic in CPython and cannot be soundly modelled.
        if not node.csl_allow_finalizer:
            for stmt in node.body:
                if isinstance(stmt, ast.FunctionDef) and stmt.name == "__del__":
                    raise PyCSLSemanticError(
                        f"Class '{node.name}' (line {node.lineno}): "
                        f"`__del__` finalizer is rejected under UB-7.5. "
                        f"Finalizer timing is non-deterministic in CPython "
                        f"and cannot be soundly modelled in WhyML. "
                        f"Either remove `__del__` or annotate the class "
                        f"with `#@ allow_finalizer` to acknowledge that "
                        f"any lifetime-dependent contracts are at risk. "
                        f"See config/skills/pycsl-ub-catalog/SKILL.md §7.5."
                    )

        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> Any:
        # Initialize the custom PyCSL fields
        node.csl_invariants = []
        node.csl_variants = []
        node.csl_ghost_assigns = []

        if node.lineno in self.contracts_map:
            contracts = self.contracts_map[node.lineno]
            for c in contracts:
                if isinstance(c, LoopInvariant):
                    node.csl_invariants.append(c)
                elif isinstance(c, LoopVariant):
                    node.csl_variants.append(c)
                elif isinstance(c, (GhostAssignDecl, GhostArraySetDecl)):
                    node.csl_ghost_assigns.append(c)

        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> Any:
        """Attach loop_invariant and loop_variant contracts to for loops."""
        node.csl_invariants = []
        node.csl_variants = []
        node.csl_ghost_assigns = []
        node.csl_allow_iteration_mutation = False   # UB-7.1 opt-in

        if node.lineno in self.contracts_map:
            contracts = self.contracts_map[node.lineno]
            for c in contracts:
                if isinstance(c, LoopInvariant):
                    node.csl_invariants.append(c)
                elif isinstance(c, LoopVariant):
                    node.csl_variants.append(c)
                elif isinstance(c, (GhostAssignDecl, GhostArraySetDecl)):
                    node.csl_ghost_assigns.append(c)
                elif isinstance(c, AllowIterationMutationDecl):
                    node.csl_allow_iteration_mutation = True

        self.generic_visit(node)

# ---------------------------------------------------------
# 2. The Weaver Interface
# ---------------------------------------------------------

class Module3_Weaver:
    """
    Coordinates the standard AST generation and the injection of contracts.
    """
    def __init__(self, source_code: str, extracted_data: List[PyCSLContract], parser_module: Any) -> None:
        self.source_code = source_code
        self.extracted_data = extracted_data
        self.parser_module = parser_module

    def _parse_extracted_contracts(self) -> Tuple[Dict[int, List[CSLNode]], Dict[int, List[CSLNode]]]:
        """Parse all extracted contract strings into Contract AST nodes.
        TrailingSimpleStatement contracts (ghost as last line in a block)
        are kept separate so Module5 can emit them AFTER their anchor
        statement."""
        contracts_map: Dict[int, List[CSLNode]] = {}
        trailing_contracts_map: Dict[int, List[CSLNode]] = {}
        for extraction in self.extracted_data:
            parsed_nodes = self.parser_module.parse_node_contracts(
                extraction.contracts, extraction.line_number)
            if extraction.node_type == "TrailingSimpleStatement":
                trailing_contracts_map.setdefault(extraction.line_number, []).extend(parsed_nodes)
            else:
                contracts_map[extraction.line_number] = parsed_nodes
        return contracts_map, trailing_contracts_map

    @staticmethod
    def _consolidate_module_concurrency(python_ast: ast.AST,
                                         contracts_map: Dict[int, List[CSLNode]]) -> None:
        """Consolidate module-level concurrency annotations from all
        contracts. SharedDecl, MutexInvariant, LockOrder may appear
        anywhere in the file (module header or as leading_lines of any
        statement), so we scan globally."""
        if not hasattr(python_ast, 'csl_shared_decls'):
            python_ast.csl_shared_decls = []
        if not hasattr(python_ast, 'csl_mutex_invariants'):
            python_ast.csl_mutex_invariants = {}
        if not hasattr(python_ast, 'csl_lock_order'):
            python_ast.csl_lock_order = None
        seen_shared = {d.variable for d in python_ast.csl_shared_decls}
        for nodes in contracts_map.values():
            for n in nodes:
                if isinstance(n, SharedDecl) and n.variable not in seen_shared:
                    python_ast.csl_shared_decls.append(n)
                    seen_shared.add(n.variable)
                elif isinstance(n, MutexInvariant) and n.mutex not in python_ast.csl_mutex_invariants:
                    python_ast.csl_mutex_invariants[n.mutex] = n.expr
                elif isinstance(n, LockOrder) and python_ast.csl_lock_order is None:
                    python_ast.csl_lock_order = n

    @staticmethod
    def _attach_labels_and_ghost_assigns(
            python_ast: ast.AST,
            contracts_map: Dict[int, List[CSLNode]],
            trailing_contracts_map: Dict[int, List[CSLNode]]) -> None:
        """Attach label and ghost-assign nodes to their target statement
        nodes. Labels appear in contracts_map keyed by the line of the
        labeled statement."""
        labels_by_line: Dict[int, List[str]] = {}
        ghost_assigns_by_line: Dict[int, List] = {}
        checkpoints_by_line: Dict[int, List] = {}
        for line, nodes in contracts_map.items():
            names = [n.name for n in nodes if isinstance(n, CSLLabel)]
            if names:
                labels_by_line[line] = names
            ghosts = [n for n in nodes if isinstance(n, (GhostAssignDecl, GhostArraySetDecl))]
            if ghosts:
                ghost_assigns_by_line[line] = ghosts
            cps = [n for n in nodes if isinstance(n, CheckPoint)]
            if cps:
                checkpoints_by_line[line] = cps
        trailing_ghost_assigns_by_line: Dict[int, List] = {}
        for line, nodes in trailing_contracts_map.items():
            ghosts = [n for n in nodes if isinstance(n, (GhostAssignDecl, GhostArraySetDecl))]
            if ghosts:
                trailing_ghost_assigns_by_line[line] = ghosts
        if not (labels_by_line or ghost_assigns_by_line or trailing_ghost_assigns_by_line
                or checkpoints_by_line):
            return
        for ast_node in ast.walk(python_ast):
            if not (isinstance(ast_node, ast.stmt) and hasattr(ast_node, 'lineno')):
                continue
            labels = labels_by_line.get(ast_node.lineno)
            if labels:
                ast_node.csl_labels = labels
            cps = checkpoints_by_line.get(ast_node.lineno)
            if cps:
                existing = getattr(ast_node, 'csl_checkpoints', [])
                ast_node.csl_checkpoints = existing + cps
            ghosts = ghost_assigns_by_line.get(ast_node.lineno)
            if ghosts:
                existing = getattr(ast_node, 'csl_ghost_assigns', [])
                ast_node.csl_ghost_assigns = existing + ghosts
            trailing = trailing_ghost_assigns_by_line.get(ast_node.lineno)
            if trailing:
                existing = getattr(ast_node, 'csl_trailing_ghost_assigns', [])
                ast_node.csl_trailing_ghost_assigns = existing + trailing

    @staticmethod
    def _extract_happy_properties(
            contracts_map: Dict[int, List[CSLNode]]) -> List[HappyProperty]:
        """Pull every module-level `HappyProperty` out of `contracts_map` (a folded
        `happy NAME:` block lands on whichever node the module-header prepend attached
        it to — typically the first class/function). Removing them here means the
        per-node weaver dispatch never sees a HAPPY; they are re-attached to the module
        node and consumed by the meta-pass `_expand_happy_properties`. Mirrors the
        global rescan in `_consolidate_module_concurrency`."""
        out: List[HappyProperty] = []
        for line, nodes in contracts_map.items():
            kept = [n for n in nodes if not isinstance(n, HappyProperty)]
            out.extend(n for n in nodes if isinstance(n, HappyProperty))
            contracts_map[line] = kept
        return out

    # --- HAPPY meta-pass (meta.md Stage B): expand a module-level region-disjointness
    #     property into a per-site `#@ check` at every write of the shared field, in
    #     every method other than the exempt (legitimate-writer) set. -------------
    @staticmethod
    def _field_write_site(stmt: ast.stmt, field: str):
        """If `stmt` writes `self.<field>[...]`, return a descriptor of the written
        location, else None. Descriptor: {"kind": "point", "index": expr} or
        {"kind": "slice", "lower": expr|None, "upper": expr|None}. Covers `Assign`,
        `AnnAssign` and `AugAssign` (augmented subscript = point write)."""
        targets = []
        if isinstance(stmt, ast.Assign):
            targets = stmt.targets
        elif isinstance(stmt, (ast.AnnAssign, ast.AugAssign)):
            targets = [stmt.target]
        for tgt in targets:
            if not isinstance(tgt, ast.Subscript):
                continue
            base = tgt.value
            if not (isinstance(base, ast.Attribute)
                    and isinstance(base.value, ast.Name)
                    and base.value.id == "self"
                    and base.attr == field):
                continue
            sl = tgt.slice
            if isinstance(sl, ast.Index):          # pre-3.9 wrapper (pure_ast mirrors CPython)
                sl = sl.value
            if isinstance(sl, ast.Slice):
                return {"kind": "slice", "lower": sl.lower, "upper": sl.upper}
            return {"kind": "point", "index": sl}
        return None

    def _happy_predicate(self, hp: HappyProperty, site: dict, line: int) -> CSLNode:
        """Build the CSL disjointness predicate for one write site of a HAPPY, as a
        CSL AST (so it is identical to a hand-written `#@ check`). `lo`/`hi` are the
        HAPPY's region bounds (reused, deep-copied); each Python index expression is
        rendered to source and re-parsed via `parse_contract("check …")`."""
        lo = lambda: copy.deepcopy(hp.region_lo)
        hi = lambda: copy.deepcopy(hp.region_hi)

        def to_csl(py_expr):
            src = ast.unparse(py_expr)
            return self.parser_module.parse_contract("check (" + src + ")", line).expr

        if site["kind"] == "point":
            return BinOp(BinOp(to_csl(site["index"]), "<", lo()),
                         "or",
                         BinOp(to_csl(site["index"]), ">=", hi()))
        # slice [lower, upper): disjoint from [lo, hi) iff upper <= lo or lower >= hi.
        lower, upper = site["lower"], site["upper"]
        below = BinOp(to_csl(upper), "<=", lo()) if upper is not None else None
        above = BinOp(to_csl(lower), ">=", hi()) if lower is not None else None
        if below is not None and above is not None:
            return BinOp(below, "or", above)
        # An open end can only be certified disjoint from the closed side it clears:
        # `self.f[:b]` (no lower) ⇒ b <= lo;  `self.f[a:]` (no upper) ⇒ a >= hi.
        return below if below is not None else above

    def _expand_happy_properties(self, python_ast: ast.AST,
                                 happy_props: List[HappyProperty]) -> None:
        """For each HAPPY, walk every function and inject a `#@ check` (a synthesized
        `CheckPoint`) at every direct write site of the shared field, except in the
        exempt (legitimate-writer) methods. Soundness is by universal coverage of body
        write-sites (meta.md composition theorem, clause 1); the trusted boundary
        (clause 2) is handled separately. Sites are processed in (lineno, col) order
        for determinism; each injected check is tagged with an `origin` for attribution."""
        if not happy_props:
            return
        funcs = [n for n in ast.walk(python_ast) if isinstance(n, ast.FunctionDef)]
        for hp in happy_props:
            except_set = set(hp.except_set)
            # (A) Body coverage: a per-site `#@ check` at every direct write of the
            # field in every non-exempt body-verified function (theorem clause 1).
            sites: List[tuple] = []
            self._collect_field_sites(python_ast, hp.field, None, sites)
            sites.sort(key=lambda t: (getattr(t[0], "lineno", 0),
                                      getattr(t[0], "col_offset", 0)))
            for stmt, site, func_name in sites:
                if func_name in except_set:
                    continue
                pred = self._happy_predicate(hp, site, getattr(stmt, "lineno", 0))
                origin = (f"happy {hp.name} @ self.{hp.field} "
                          f"L{getattr(stmt, 'lineno', 0)}")
                cp = CheckPoint("check", pred, origin=origin)
                stmt.csl_checkpoints = getattr(stmt, "csl_checkpoints", []) + [cp]
            # (C) Trust boundary: a non-exempt trusted/abstract function has no
            # checkable body, so it could write the protected region. It must opt in
            # with `#@ \preserves`, which synthesizes the canonical region-preservation
            # `ensures` (assumed at the boundary, theorem clause 2). Absent the marker
            # is a hard error — the clause has teeth.
            for fn in funcs:
                if fn.name in except_set:
                    continue
                if not (getattr(fn, "csl_trusted", False)
                        or getattr(fn, "csl_abstract", False)):
                    continue
                if not getattr(fn, "csl_preserves", False):
                    lo, hi = (self._region_bound_str(hp.region_lo),
                              self._region_bound_str(hp.region_hi))
                    raise PyCSLSemanticError(
                        f"`happy {hp.name}`: trusted/abstract function '{fn.name}' is "
                        f"not exempt and has no checkable body, so it could write the "
                        f"protected region [{lo}, {hi}) of self.{hp.field}. Add "
                        f"`#@ \\preserves` to promise it preserves the region "
                        f"(an assumed postcondition), or list it in `except`."
                    )
                fn.csl_ensures.append(self._canonical_preservation_ensures(hp))

    @staticmethod
    def _region_bound_str(node: CSLNode) -> str:
        """Render a region bound (a CSL expr) for a diagnostic message."""
        v = getattr(node, "value", None)
        if v is not None:
            return str(int(v)) if float(v).is_integer() else str(v)
        return getattr(node, "name", "<expr>")

    @staticmethod
    def _canonical_preservation_ensures(hp: HappyProperty) -> Ensures:
        """Build `ensures \\forall v; (lo <= v and v < hi) ==> self.field[v] ==
        \\old(self.field[v])` for one HAPPY — the canonical region-preservation
        postcondition the meta-pass attaches to an opted-in trusted/abstract writer.
        Synthesized (not pattern-matched) so the guard always covers the full region."""
        v = "__happy_i"
        guard = BinOp(BinOp(copy.deepcopy(hp.region_lo), "<=", Var(v)),
                      "and",
                      BinOp(Var(v), "<", copy.deepcopy(hp.region_hi)))
        eq = BinOp(FieldSubscript(hp.field, Var(v)),
                   "==",
                   Old(FieldSubscript(hp.field, Var(v))))
        return Ensures(Forall(v, BinOp(guard, "==>", eq)))

    def _collect_field_sites(self, node: ast.AST, field: str,
                             cur_func, out: List[tuple]) -> None:
        """Recursive descent collecting `(stmt, site, enclosing_func_name)` for every
        write of `self.<field>[...]`. `cur_func` is the name of the nearest enclosing
        FunctionDef (the writer)."""
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                site = self._field_write_site(child, field)
                if site is not None:
                    out.append((child, site, cur_func))
            inner_func = child.name if isinstance(child, ast.FunctionDef) else cur_func
            self._collect_field_sites(child, field, inner_func, out)

    def process(self) -> ast.AST:
        contracts_map, trailing_contracts_map = self._parse_extracted_contracts()
        happy_props = self._extract_happy_properties(contracts_map)
        python_ast = ast.parse(self.source_code)
        PyCSLWeaver(contracts_map).visit(python_ast)
        python_ast.csl_happy_properties = happy_props
        self._consolidate_module_concurrency(python_ast, contracts_map)
        self._attach_labels_and_ghost_assigns(python_ast, contracts_map, trailing_contracts_map)
        self._expand_happy_properties(python_ast, happy_props)
        return python_ast
