from __future__ import annotations

from frontend import pure_ast as ast  # PyCSL toolchain parses Python via its own pure-Python
                        # front-end (no stdlib `ast` / CPython `compile`).
import warnings
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, fields as _dc_fields, is_dataclass as _is_dc, replace as _dc_replace

# Import the AST nodes from Module 2
from frontend.Module2_Parser import (
    CSLNode, Requires, Ensures, Assigns, LoopInvariant, LoopVariant,
    ClassInvariant, Label as CSLLabel, FunctionVariant, Diverges, NoInline, SiblingConcrete, VerifyModule, PropagateFrame, FreshGlobals, Trusted, Abstract, Lemma, Uses,
    InterfaceClause, Reveal,
    GhostAssignDecl, GhostArraySetDecl, RaisesDecl, NoExceptionDecl,
    AllowFinalizerDecl, AllowIterationMutationDecl,
    BoundedIntDecl, ProofDecl,
    SharedDecl, DatatypeDecl, InductiveDecl, ThreadEntry, Acquires, Releases, CriticalSection,
    MutexInvariant, LockOrder, BinOp, Number,
    Act, ForExpand, Given, Complete, Disjoint, Old, UnaryOp, CSLBool,
    CheckPoint, HappyProperty, Preserves, Footprint, Var, Forall, FieldSubscript,
    MixinDecl, ProvidesDecl, SharedStateDecl, TouchesFieldDecl,
    MethodDependencyDecl, ComposeFromDecl,
)
import copy
from errors import PyCSLSemanticError
from frontend.Module1_Ingestor import PyCSLContract

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
    def _const_int(node: Any, var: str) -> int:
        """Resolve a `#@ for` range bound to an integer. v1: integer literal only
        (a `Number` with an integral value). Anything else is a hard, fail-loud
        error — never a silent fallback (sugar-for-spec.md §5.1)."""
        if isinstance(node, Number) and float(node.value).is_integer():
            return int(node.value)
        raise PyCSLSemanticError(
            f"`for {var} in range(...)`: range bound must be an integer literal "
            f"(got {type(node).__name__}); named-constant bounds are not yet supported",
            stage="Module3")

    @staticmethod
    def _subst_var(node: Any, var: str, m: int) -> Any:
        """Deep-copy `node`, replacing every `Var(name=var)` with `Number(m)`.
        The loop index becomes an integer literal — so the expansion is ground."""
        if isinstance(node, Var) and node.name == var:
            return Number(int(m))   # match source integer literals (`number` → Number(int))
        if _is_dc(node):
            repl = {f.name: PyCSLWeaver._subst_var(getattr(node, f.name), var, m)
                    for f in _dc_fields(node)}
            return _dc_replace(node, **repl)
        if isinstance(node, list):
            return [PyCSLWeaver._subst_var(x, var, m) for x in node]
        return node

    @staticmethod
    def _desugar_for(contracts: List[Any]) -> List[Any]:
        """Expand each `ForExpand` (`#@ for VAR in range(lo,hi):`) into ground
        requires/ensures: for each m in [lo, hi) (upper-exclusive), each body
        clause with VAR substituted by the literal m. Meaning-preserving — the
        output is exactly the hand-written clause sequence (sugar-for-spec.md §4)."""
        out: List[Any] = []
        for c in contracts:
            if not isinstance(c, ForExpand):
                out.append(c)
                continue
            lo = PyCSLWeaver._const_int(c.lo, c.var)
            hi = PyCSLWeaver._const_int(c.hi, c.var)
            if not c.clauses:
                raise PyCSLSemanticError(
                    f"`for {c.var} in range(...)`: empty body", stage="Module3")
            for m in range(lo, hi):
                for clause in c.clauses:
                    out.append(PyCSLWeaver._subst_var(clause, c.var, m))
        return out

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
    def _extract_mixin_directives(node: ast.FunctionDef, contracts: List[Any]) -> List[Any]:
        """Pull mixin directives (and the dependency contracts that follow them) off
        the contract list, attaching them to the method node, and RETURN the remaining
        contracts (the method's own requires/ensures/assigns/…) for normal dispatch.

        A `depends_method`/`requires_method` opens a window: subsequent `requires`/
        `ensures` clauses belong to that DEPENDENCY until the next `provides` or other
        mixin directive closes it. This is how `#@   ensures \\result >= 0` indented
        under `#@ depends_method emit: …` becomes emit's declared contract rather than
        the enclosing method's postcondition."""
        remaining: List[Any] = []
        open_dep = None   # the dict currently accumulating a dependency's clauses

        def close_dep() -> None:
            nonlocal open_dep
            if open_dep is not None:
                node.csl_method_deps.append(open_dep)
                open_dep = None

        for c in contracts:
            if isinstance(c, MethodDependencyDecl):
                close_dep()
                open_dep = {"method": c.method, "sig": c.sig, "kind": c.kind,
                            "requires": [], "ensures": []}
            elif isinstance(c, ProvidesDecl):
                close_dep()
                node.csl_provides.append(c.method)
            elif isinstance(c, SharedStateDecl):
                close_dep()
                node.csl_mixin_shared_state.append(c)
            elif isinstance(c, TouchesFieldDecl):
                close_dep()
                node.csl_touches_field.append(c)
            elif isinstance(c, (MixinDecl, ComposeFromDecl)):
                # Class-level markers that attach to the first method get ignored here;
                # the class node carries them (see visit_ClassDef).
                close_dep()
            elif open_dep is not None and isinstance(c, Requires):
                open_dep["requires"].append(c)
            elif open_dep is not None and isinstance(c, Ensures):
                open_dep["ensures"].append(c)
            else:
                # Anything else closes an open dependency window and is the method's own.
                close_dep()
                remaining.append(c)
        close_dep()
        return remaining

    @staticmethod
    def _dispatch_function_contracts(node: ast.FunctionDef, contracts: List[Any]) -> None:
        """Attach each parsed contract node to the matching `csl_*` field
        on the function-def AST node. `#@ for` blocks expand to ground
        requires/ensures, then Acts are desugared to requires/ensures."""
        contracts = PyCSLWeaver._desugar_for(contracts)
        contracts, node.csl_acts, entry_cps = PyCSLWeaver._desugar_acts(contracts)
        # complete/disjoint become function-entry `#@ assert` checkpoints on the
        # first body statement (discharged under the preconditions, on all paths).
        if entry_cps and getattr(node, "body", None):
            first = node.body[0]
            first.csl_checkpoints = list(entry_cps) + getattr(first, "csl_checkpoints", [])
        # Mixin pre-pass (Tier 1): extract mixin directives, and associate
        # `requires`/`ensures` clauses that FOLLOW a `depends_method`/`requires_method`
        # (and precede the next `provides`/structural directive) with that dependency
        # — mirroring the indentation in the source (`#@   ensures …`). The dependency's
        # contract becomes the abstract `val` against which the provider is verified
        # (S1) and refined (S2); it is NOT the method's own postcondition.
        contracts = PyCSLWeaver._extract_mixin_directives(node, contracts)
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
            elif isinstance(c, NoInline):
                node.csl_no_inline = True
            elif isinstance(c, SiblingConcrete):
                node.csl_sibling_concrete = True
            elif isinstance(c, VerifyModule):
                node.csl_verify_module = c.name
            elif isinstance(c, PropagateFrame):
                node.csl_propagate_frame = True
            elif isinstance(c, FreshGlobals):
                node.csl_fresh_globals = True
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
            elif isinstance(c, Lemma):
                node.csl_lemma = True
            elif isinstance(c, Uses):
                node.csl_uses.append(c.lemma)
            elif isinstance(c, InterfaceClause):
                if c.kind == "ensures":
                    node.csl_iface_ensures.append(c.payload)
                elif c.kind == "requires":
                    node.csl_iface_requires.append(c.payload)
                elif c.kind == "assigns":
                    node.csl_iface_assigns.append(c.payload)
            elif isinstance(c, Reveal):
                node.csl_reveal.append(c.fn)
            elif isinstance(c, Preserves):
                node.csl_preserves = True
            elif isinstance(c, Footprint):
                node.csl_footprints = getattr(node, "csl_footprints", []) + [c]
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
        node.csl_datatypes = []          # sum-types: #@ datatype decls (consolidated below)
        node.csl_inductives = []         # inductive.md: #@ inductive predicates (rules grouped below)
        node.csl_happy_properties = []   # populated by Module3_Weaver.process (hoisted)

        if 0 in self.contracts_map:
            for c in self.contracts_map[0]:
                if isinstance(c, DatatypeDecl):
                    node.csl_datatypes.append(c)
                elif isinstance(c, SharedDecl):
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

    @staticmethod
    def _is_trivial_new(fn: ast.FunctionDef) -> bool:
        """True if `__new__` is the default allocation: an optional docstring then a
        single `return super().__new__(cls...)` or `return object.__new__(cls...)`.
        Anything else (caching, conditionals, returning a stored/other instance) is
        non-trivial and rejected under UB-7.6 (see visit_ClassDef)."""
        body = [s for s in fn.body
                if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
        if len(body) != 1 or not isinstance(body[0], ast.Return):
            return False
        val = body[0].value
        if not (isinstance(val, ast.Call) and isinstance(val.func, ast.Attribute)
                and val.func.attr == "__new__"):
            return False
        recv = val.func.value
        # super().__new__ / super(C, cls).__new__
        if (isinstance(recv, ast.Call) and isinstance(recv.func, ast.Name)
                and recv.func.id == "super"):
            return True
        # object.__new__
        if isinstance(recv, ast.Name) and recv.id == "object":
            return True
        return False

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        node.csl_class_invariants = []
        node.csl_allow_finalizer = False   # UB-7.5 opt-in
        node.csl_is_mixin = False          # `#@ mixin` (Tier 1)
        node.csl_compose_from = []         # `#@ compose_from M1, M2, …` (Tier 1)

        if node.lineno in self.contracts_map:
            contracts = self.contracts_map[node.lineno]
            for c in contracts:
                if isinstance(c, ClassInvariant):
                    node.csl_class_invariants.append(c)
                elif isinstance(c, AllowFinalizerDecl):
                    node.csl_allow_finalizer = True
                elif isinstance(c, MixinDecl):
                    node.csl_is_mixin = True
                elif isinstance(c, ComposeFromDecl):
                    node.csl_compose_from = list(c.mixins)

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

        # UB-7.6 (base_op.md Tier A): a custom `__new__` is accepted only when it is
        # trivial — `return super().__new__(cls)` / `return object.__new__(cls)`, i.e.
        # the default allocation that `__init__` then populates. A non-trivial `__new__`
        # (returning a cached/singleton/other instance, or branching) interposes on
        # allocation in a way the record-construction model cannot soundly represent —
        # `C(...)` would no longer be a fresh `{...}` literal. Reject rather than fake it.
        for stmt in node.body:
            if (isinstance(stmt, ast.FunctionDef) and stmt.name == "__new__"
                    and not self._is_trivial_new(stmt)):
                raise PyCSLSemanticError(
                    f"Class '{node.name}' (line {stmt.lineno}): non-trivial `__new__` "
                    f"is rejected under UB-7.6. Allocation interposition (caching, "
                    f"singletons, returning a different instance, or conditional "
                    f"allocation) cannot be soundly modelled — construction `C(...)` is "
                    f"a fresh record literal. Only `return super().__new__(cls)` / "
                    f"`return object.__new__(cls)` is accepted (it is the default "
                    f"allocation, populated by `__init__`). "
                    f"See config/skills/pycsl-ub-catalog/SKILL.md §7.6."
                )

        self.generic_visit(node)

    @staticmethod
    def _attach_loop_contracts(node, contracts) -> None:
        """Attach loop-invariant / loop-variant / ghost-assign contracts to a While or
        For node (the part common to both visitors). `node.csl_invariants`,
        `csl_variants`, and `csl_ghost_assigns` must already be initialized."""
        for c in contracts:
            if isinstance(c, LoopInvariant):
                node.csl_invariants.append(c)
            elif isinstance(c, LoopVariant):
                node.csl_variants.append(c)
            elif isinstance(c, (GhostAssignDecl, GhostArraySetDecl)):
                node.csl_ghost_assigns.append(c)

    def visit_While(self, node: ast.While) -> Any:
        # Initialize the custom PyCSL fields
        node.csl_invariants = []
        node.csl_variants = []
        node.csl_ghost_assigns = []

        if node.lineno in self.contracts_map:
            self._attach_loop_contracts(node, self.contracts_map[node.lineno])

        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> Any:
        """Attach loop_invariant and loop_variant contracts to for loops."""
        node.csl_invariants = []
        node.csl_variants = []
        node.csl_ghost_assigns = []
        node.csl_allow_iteration_mutation = False   # UB-7.1 opt-in

        if node.lineno in self.contracts_map:
            contracts = self.contracts_map[node.lineno]
            self._attach_loop_contracts(node, contracts)
            for c in contracts:   # UB-7.1: for-only opt-in (not shared with While)
                if isinstance(c, AllowIterationMutationDecl):
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
        if not hasattr(python_ast, 'csl_datatypes'):
            python_ast.csl_datatypes = []
        if not hasattr(python_ast, 'csl_inductives'):
            python_ast.csl_inductives = []
        seen_shared = {d.variable for d in python_ast.csl_shared_decls}
        seen_dt = {d.name for d in python_ast.csl_datatypes}
        seen_ind = {i.name for i in python_ast.csl_inductives}
        for nodes in contracts_map.values():
            # inductive.md: an `#@ inductive p(…):` header carries its rules INLINE
            # (the indentation block folds header + `name: clause` lines into one
            # contract in Module 1; Module 2 parses the rules into `InductiveDecl.rules`).
            # Hoisted to module level like datatypes; no separate `#@ rule` grouping.
            for n in nodes:
                if isinstance(n, InductiveDecl):
                    if n.name not in seen_ind:
                        python_ast.csl_inductives.append(n)
                        seen_ind.add(n.name)
                    continue
                if isinstance(n, DatatypeDecl) and n.name not in seen_dt:
                    python_ast.csl_datatypes.append(n)
                    seen_dt.add(n.name)
                elif isinstance(n, SharedDecl) and n.variable not in seen_shared:
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
        trailing_checkpoints_by_line: Dict[int, List] = {}
        for line, nodes in trailing_contracts_map.items():
            ghosts = [n for n in nodes if isinstance(n, (GhostAssignDecl, GhostArraySetDecl))]
            if ghosts:
                trailing_ghost_assigns_by_line[line] = ghosts
            # A `#@ assert`/`#@ check` that is the LAST statement of a block lands in the
            # block FOOTER (Module1 `prev.footer`), i.e. the trailing-contracts map. Extract
            # it here (it was previously dropped — only ghost-assigns were pulled from
            # trailing) so it attaches as a TRAILING checkpoint emitted AFTER the block's
            # last statement, not silently lost.
            cps = [n for n in nodes if isinstance(n, CheckPoint)]
            if cps:
                trailing_checkpoints_by_line[line] = cps
        if not (labels_by_line or ghost_assigns_by_line or trailing_ghost_assigns_by_line
                or trailing_checkpoints_by_line or checkpoints_by_line):
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
            tcps = trailing_checkpoints_by_line.get(ast_node.lineno)
            if tcps:
                existing = getattr(ast_node, 'csl_trailing_checkpoints', [])
                ast_node.csl_trailing_checkpoints = existing + tcps

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
        # 07-1143 R3 (validation): every `#@ footprint NAME(arg)` must reference a declared
        # PARAMETRIC HAPPY `NAME` — a typo would silently confine nothing (a soundness
        # hole, since the method would appear constrained but get no per-site check).
        param_happy_names = {hp.name for hp in happy_props if hp.param is not None}
        for fn in funcs:
            for fpd in getattr(fn, "csl_footprints", []):
                if fpd.happy_name not in param_happy_names:
                    raise PyCSLSemanticError(
                        f"`footprint {fpd.happy_name}` on '{fn.name}' references no "
                        f"parametric HAPPY named '{fpd.happy_name}'. Declared parametric "
                        f"HAPPYs: {sorted(param_happy_names)}.")
        for hp in happy_props:
            except_set = set(hp.except_set)
            # General `targets`/`context` form (coherent with macsl): a NAMED property
            # attached to ONE target function as an `ensures` (postcond — H-R/H-E) or a
            # `requires` (precond — H-S). The clause is verified as an ordinary contract
            # (callee proves the ensures; every call site proves the requires), so the
            # H-S negative fails IN THE CALLER. A missing target is a hard error (a typo
            # would silently attach the property to nothing).
            if hp.context in ("postcond", "precond", "total"):
                target_fns = [fn for fn in funcs if fn.name == hp.target]
                if not target_fns:
                    raise PyCSLSemanticError(
                        f"`happy {hp.name}`: targets '{hp.target}', which is not a method in "
                        f"this module. Known methods: {sorted(fn.name for fn in funcs)}.")
                if hp.context == "total":
                    # H-D (totality / DoS): PyCSL functions are total by DEFAULT — Why3 emits a
                    # termination VC (each loop needs a `#@ loop variant`), so an attacker-driven
                    # unbounded loop fails to verify. This policy NAMES that guarantee and
                    # forbids the only opt-out: `#@ \diverges` on the target contradicts the
                    # totality claim and is a hard error.
                    for fn in target_fns:
                        if getattr(fn, "csl_diverges", False):
                            raise PyCSLSemanticError(
                                f"`happy {hp.name}`: total target '{hp.target}' is marked "
                                f"`#@ \\diverges` — it opts OUT of termination, contradicting "
                                f"the totality (H-D) claim. Remove `\\diverges`, or drop the "
                                f"`total` policy.")
                    continue
                for fn in target_fns:
                    if hp.context == "postcond":
                        fn.csl_ensures.append(Ensures(copy.deepcopy(hp.formula)))
                    else:
                        # H-S: the target ASSUMES the capability (a sound precondition on its
                        # own body — it is the guarded operation).
                        fn.csl_requires.append(Requires(copy.deepcopy(hp.formula)))
                if hp.context == "precond":
                    # H-S check-before-use: every CALL SITE must PROVE the capability. macsl
                    # gets this from WP's automatic call rule; PyCSL lowers a sibling
                    # `self.<m>(…)` to a CONTRACTLESS abstract val (no call-site obligation), so
                    # we inject the obligation explicitly as a `#@ check <formula>` BEFORE each
                    # `self.<target>(…)` call (the HAPPY check primitive). A caller that skipped
                    # the grant gets an unprovable VC IN THE CALLER — exactly macsl's
                    # `unauth_endpoint` red (../macsl tests/small_example/attacks.c). The
                    # target's own (recursive) self-call already assumes the precond, so skip it.
                    csites: List[tuple] = []
                    self._collect_self_call_sites(python_ast, hp.target, None, None, csites)
                    csites.sort(key=lambda t: (getattr(t[0], "lineno", 0),
                                               getattr(t[0], "col_offset", 0)))
                    for stmt, caller in csites:
                        if caller == hp.target:
                            continue
                        line = getattr(stmt, "lineno", 0)
                        cp = CheckPoint("check", copy.deepcopy(hp.formula),
                                        origin=(f"happy {hp.name} call-site precond before "
                                                f"self.{hp.target} L{line}"))
                        stmt.csl_checkpoints = getattr(stmt, "csl_checkpoints", []) + [cp]
                continue
            # 07-1143 R3: PARAMETRIC (per-object) form. A method binds the region via
            # `#@ footprint NAME(arg)`; at each point write `path[i]=v` it must prove the
            # index lies in the substituted region `[lo[param:=arg], hi[param:=arg])`. A
            # non-exempt method with NO footprint that writes the path is forbidden
            # (`check False`). (Per the design review: this proves CONTAINMENT — that
            # writes stay in-region — which composes with an indexed-`assigns` frame to
            # give per-object PRESERVATION.)
            if hp.param is not None:
                path = hp.protects[0]
                funcs2 = [n for n in ast.walk(python_ast) if isinstance(n, ast.FunctionDef)]
                fp_arg = {}
                for fn in funcs2:
                    for fpd in getattr(fn, "csl_footprints", []):
                        if fpd.happy_name == hp.name:
                            fp_arg[fn.name] = fpd.arg
                psites = []
                self._collect_protect_index_sites(python_ast, path, None, psites)
                psites.sort(key=lambda t: (getattr(t[0], "lineno", 0),
                                           getattr(t[0], "col_offset", 0)))
                for stmt, func_name, idx_ast in psites:
                    if func_name in except_set:
                        continue
                    line = getattr(stmt, "lineno", 0)
                    if func_name in fp_arg:
                        arg = fp_arg[func_name]
                        lo_s = self._subst_csl_param(hp.region_lo, hp.param, arg)
                        hi_s = self._subst_csl_param(hp.region_hi, hp.param, arg)
                        i_csl = self.parser_module.parse_contract(
                            "check (" + ast.unparse(idx_ast) + ")", line).expr
                        pred = BinOp(BinOp(lo_s, "<=", i_csl), "and",
                                     BinOp(i_csl, "<", hi_s))
                    else:
                        pred = CSLBool(False)   # non-exempt, no footprint → forbidden
                    origin = f"happy {hp.name}({hp.param}) protects {path} L{line}"
                    cp = CheckPoint("check", pred, origin=origin)
                    stmt.csl_checkpoints = getattr(stmt, "csl_checkpoints", []) + [cp]
                continue
            # 07-1143 R1/R2: the `protects <paths>` subsystem-ownership form — no method
            # outside `except` may DIRECTLY write any protected (possibly dotted) path.
            # Per-site check is `False` (forbidden outright); there is no region.
            if hp.protects:
                protected = set(hp.protects)
                # (R2 soundness) reject aliasing a protected base into a non-exempt local.
                self._check_protect_aliasing(python_ast, protected, except_set, None, hp.name)
                psites: List[tuple] = []
                self._collect_protect_sites(python_ast, protected, None, psites)
                psites.sort(key=lambda t: (getattr(t[0], "lineno", 0),
                                           getattr(t[0], "col_offset", 0)))
                for stmt, func_name, path in psites:
                    if func_name in except_set:
                        continue
                    origin = (f"happy {hp.name} protects {path} "
                              f"L{getattr(stmt, 'lineno', 0)}")
                    cp = CheckPoint("check", CSLBool(False), origin=origin)
                    stmt.csl_checkpoints = getattr(stmt, "csl_checkpoints", []) + [cp]
                # (R1.1) trust boundary: a non-exempt trusted/abstract method whose
                # `assigns` mentions a protected path (it has no body to scan) must opt in
                # with `#@ \preserves`, else it is a hard error.
                for fn in [n for n in ast.walk(python_ast) if isinstance(n, ast.FunctionDef)]:
                    if fn.name in except_set:
                        continue
                    if not (getattr(fn, "csl_trusted", False) or getattr(fn, "csl_abstract", False)):
                        continue
                    if getattr(fn, "csl_preserves", False):
                        continue
                    assigned = {self._target_dotted_path(t)
                                for a in getattr(fn, "csl_assigns", [])
                                for t in getattr(a, "targets", [])}
                    if assigned & protected:
                        raise PyCSLSemanticError(
                            f"`happy {hp.name}`: trusted/abstract method '{fn.name}' is "
                            f"not exempt and its `assigns` writes a protected path "
                            f"({', '.join(sorted(assigned & protected))}). Add "
                            f"`#@ \\preserves` to promise it preserves the protected "
                            f"fields, or add it to the `except` set.")
                continue
            # H-I1 (read confinement): the READ mirror of the R1 region form. No non-exempt
            # method may READ self.<field> inside [LO, HI). Soundness mirrors the write form:
            # (i) a per-READ-site `#@ check (index outside region)` in every non-exempt body;
            # (ii) aliasing the protected base is forbidden (a read via `x = self.field`
            #      would evade the per-site check); (iii) well-formedness (exempt names are
            #      methods; no dynamic exec in a non-exempt method — it could read anything);
            #      (iv) a non-exempt trusted/abstract method has no checkable body so it could
            #      read the region — it must be exempt. Realised entirely here (not in the IR
            #      `happy` blob), so the IR stays byte-identical for write-confinement files.
            if hp.context == "reading":
                # (ii) no aliasing the protected base into a non-exempt local.
                # `_check_protect_aliasing` catches the prefix alias `x = self`; we also
                # forbid the full-path alias `x = self.<field>` (a read through `x` would
                # evade the per-read check — closing a gap the shipped R1 write form leaves).
                self._check_protect_aliasing(
                    python_ast, {f"self.{hp.field}"}, except_set, None, hp.name)
                for fn in funcs:
                    if fn.name in except_set:
                        continue
                    for n in ast.walk(fn):
                        if (isinstance(n, ast.Assign)
                                and isinstance(n.value, ast.Attribute)
                                and isinstance(n.value.value, ast.Name)
                                and n.value.value.id == "self"
                                and n.value.attr == hp.field):
                            raise PyCSLSemanticError(
                                f"`happy {hp.name}`: aliasing the protected field "
                                f"'self.{hp.field}' into a local in non-exempt '{fn.name}' is "
                                f"forbidden — a read through the alias would evade the "
                                f"read-confinement check. Read through self.{hp.field} "
                                f"directly, or add '{fn.name}' to `except`.")
                # (iii) well-formedness, mirroring core_ir_semantic._check_happy (which is
                # skipped for reading properties): exempt names must be methods; a non-exempt
                # dynamic-exec method cannot be confined.
                method_names = {fn.name for fn in funcs}
                for nm in except_set:
                    if nm not in method_names:
                        raise PyCSLSemanticError(
                            f"`happy {hp.name}`: exempt function '{nm}' is not a method in "
                            f"this module. Known methods: {sorted(method_names)}.")
                for fn in funcs:
                    if fn.name in except_set:
                        continue
                    if any(isinstance(c, ast.Call) and isinstance(getattr(c, 'func', None), ast.Name)
                           and c.func.id == "exec" for c in ast.walk(fn)):
                        raise PyCSLSemanticError(
                            f"`happy {hp.name}`: method '{fn.name}' contains a dynamic "
                            f"`exec(...)`, which may read anything — add it to `except` or "
                            f"remove the exec.")
                # (i) per-read-site check.
                rsites: List[tuple] = []
                self._collect_field_read_sites(python_ast, hp.field, None, None, rsites)
                rsites.sort(key=lambda t: (getattr(t[0], "lineno", 0),
                                           getattr(t[0], "col_offset", 0)))
                for stmt, site, func_name in rsites:
                    if func_name in except_set:
                        continue
                    pred = self._happy_predicate(hp, site, getattr(stmt, "lineno", 0))
                    origin = (f"happy {hp.name} reads self.{hp.field} "
                              f"L{getattr(stmt, 'lineno', 0)}")
                    cp = CheckPoint("check", pred, origin=origin)
                    stmt.csl_checkpoints = getattr(stmt, "csl_checkpoints", []) + [cp]
                # (iv) trust boundary: a non-exempt trusted/abstract method could read the
                # region with no checkable body — it must be exempt.
                for fn in funcs:
                    if fn.name in except_set:
                        continue
                    if (getattr(fn, "csl_trusted", False)
                            or getattr(fn, "csl_abstract", False)):
                        lo, hi = (self._region_bound_str(hp.region_lo),
                                  self._region_bound_str(hp.region_hi))
                        raise PyCSLSemanticError(
                            f"`happy {hp.name}`: trusted/abstract function '{fn.name}' is "
                            f"not exempt and has no checkable body, so it could read the "
                            f"protected region [{lo}, {hi}) of self.{hp.field}. List it in "
                            f"`except` if it is a legitimate reader.")
                continue
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

    def _collect_protect_sites(self, node: ast.AST, protected: set,
                               cur_func, out: List[tuple]) -> None:
        """07-1143 R1/R2: collect `(stmt, enclosing_func_name, path)` for every direct
        write whose dotted base path is one of the `protected` paths."""
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                tgts = (child.targets if isinstance(child, ast.Assign)
                        else [child.target])
                for tgt in tgts:
                    p = self._target_dotted_path(tgt)
                    if p in protected:
                        out.append((child, cur_func, p))
            inner = child.name if isinstance(child, ast.FunctionDef) else cur_func
            self._collect_protect_sites(child, protected, inner, out)

    def _collect_protect_index_sites(self, node: ast.AST, path: str,
                                     cur_func, out: List[tuple]) -> None:
        """07-1143 R3: like `_collect_protect_sites` but for a single indexed path,
        capturing the subscript INDEX ast — `(stmt, enclosing_func_name, index_ast)` for
        every point write `<path>[i] = v`. (Slice/whole-array writes to a parametric path
        are not certifiable per-object; they are left to the non-footprint reject.)"""
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                tgts = (child.targets if isinstance(child, ast.Assign)
                        else [child.target])
                for tgt in tgts:
                    if isinstance(tgt, ast.Subscript) and \
                            self._target_dotted_path(tgt.value) == path:
                        sl = tgt.slice
                        if isinstance(sl, ast.Index):   # pre-3.9 wrapper
                            sl = sl.value
                        if not isinstance(sl, ast.Slice):
                            out.append((child, cur_func, sl))
            inner = child.name if isinstance(child, ast.FunctionDef) else cur_func
            self._collect_protect_index_sites(child, path, inner, out)

    @staticmethod
    def _subst_csl_param(node, param_name: str, repl):
        """07-1143 R3: return a deep copy of CSL expression `node` with every `Var` named
        `param_name` replaced by (a copy of) `repl` — binds a parametric HAPPY's region
        bounds to a method's footprint argument."""
        if isinstance(node, Var) and getattr(node, "name", None) == param_name:
            return copy.deepcopy(repl)
        if _is_dc(node):
            out = copy.deepcopy(node)
            for f in _dc_fields(out):
                v = getattr(out, f.name)
                if _is_dc(v) or isinstance(v, Var):
                    setattr(out, f.name, Module3_Weaver._subst_csl_param(v, param_name, repl))
                elif isinstance(v, list):
                    setattr(out, f.name, [Module3_Weaver._subst_csl_param(x, param_name, repl)
                                          if _is_dc(x) else x for x in v])
            return out
        return node

    def _check_protect_aliasing(self, node: ast.AST, protected: set, except_set: set,
                                cur_func, hp_name: str) -> None:
        """07-1143 R2 (soundness): a protected base path may not be ALIASED into a local
        in a non-exempt method — `x = world.fs` then `x.disk[i]=v` would evade the
        write-site check. Reject such aliasing as a hard error (sound-by-rejection, not
        deferred). A value path that is a proper prefix of any protected path is a
        protected base. Mirrors the inliner's `_check_no_aliasing` discipline."""
        prefixes = set()
        for p in protected:
            parts = p.split(".")
            for k in range(1, len(parts)):
                prefixes.add(".".join(parts[:k]))   # world, world.fs, … (proper prefixes)
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Assign) and isinstance(child.value, (ast.Attribute, ast.Name)):
                vpath = self._target_dotted_path(child.value)
                if vpath in prefixes and (cur_func is None or cur_func not in except_set):
                    raise PyCSLSemanticError(
                        f"`happy {hp_name}`: aliasing the protected base '{vpath}' into a "
                        f"local in non-exempt '{cur_func or '<module>'}' is forbidden — it "
                        f"would evade confinement. Write through the canonical protected "
                        f"path, or add the method to the `except` set if it is an owner.")
            inner = child.name if isinstance(child, ast.FunctionDef) else cur_func
            self._check_protect_aliasing(child, protected, except_set, inner, hp_name)

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

    @staticmethod
    def _subscript_read_site(sub: ast.Subscript, field: str):
        """If `sub` is a Load of `self.<field>[...]`, return its site descriptor (same
        shape as `_field_write_site`: point/slice), else None. The READ analogue used by
        H-I1 read confinement."""
        base = sub.value
        if not (isinstance(base, ast.Attribute)
                and isinstance(base.value, ast.Name)
                and base.value.id == "self"
                and base.attr == field):
            return None
        sl = sub.slice
        if isinstance(sl, ast.Index):              # pre-3.9 wrapper
            sl = sl.value
        if isinstance(sl, ast.Slice):
            return {"kind": "slice", "lower": sl.lower, "upper": sl.upper}
        return {"kind": "point", "index": sl}

    def _collect_self_call_sites(self, node: ast.AST, target: str, cur_func,
                                 cur_stmt, out: List[tuple]) -> None:
        """Collect `(enclosing_stmt, caller_func)` for every call `self.<target>(...)` —
        the H-S check-before-use call sites where the capability precondition is injected."""
        for child in ast.iter_child_nodes(node):
            new_func = child.name if isinstance(child, ast.FunctionDef) else cur_func
            new_stmt = child if isinstance(child, ast.stmt) else cur_stmt
            if (isinstance(child, ast.Call)
                    and isinstance(child.func, ast.Attribute)
                    and isinstance(child.func.value, ast.Name)
                    and child.func.value.id == "self"
                    and child.func.attr == target):
                if cur_stmt is not None:
                    out.append((cur_stmt, cur_func))
            self._collect_self_call_sites(child, target, new_func, new_stmt, out)

    def _collect_field_read_sites(self, node: ast.AST, field: str, cur_func,
                                  cur_stmt, out: List[tuple]) -> None:
        """Recursive descent collecting `(enclosing_stmt, site, func_name)` for every READ
        (Load) of `self.<field>[...]`. The check attaches to the nearest enclosing statement
        so it is discharged before the read executes. A `self.<field>[i] = v` LHS is a Store
        (write) and is NOT collected here — that is the H-T (write) form's concern."""
        for child in ast.iter_child_nodes(node):
            new_func = child.name if isinstance(child, ast.FunctionDef) else cur_func
            new_stmt = child if isinstance(child, ast.stmt) else cur_stmt
            if (isinstance(child, ast.Subscript)
                    and isinstance(getattr(child, "ctx", None), ast.Load)):
                site = self._subscript_read_site(child, field)
                if site is not None and cur_stmt is not None:
                    out.append((cur_stmt, site, cur_func))
            self._collect_field_read_sites(child, field, new_func, new_stmt, out)

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
