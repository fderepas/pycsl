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
    MethodDependencyDecl, ComposeFromDecl, ConformsToDecl,
)
import re
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
                            "requires": [], "ensures": [], "assigns": []}
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
            elif open_dep is not None and isinstance(c, Assigns):
                # (#32) A METHOD REQUIREMENT MAY DECLARE ITS FRAME. The window already
                # accepts `requires`/`ensures`; without `assigns` a `#@ requires_method`
                # dependency is FRAMELESS BY CONSTRUCTION, so its caller-side abstract
                # `val` declares no effect and every calling method may claim
                # `assigns \nothing` however much state the real provider writes.
                # Measured: that is the sole remaining MODEL-VISIBLE converted false frame
                # (`expressions._ifexpr_seq_arm`, whose `_seq_operand` requirement reaches
                # `_add_abstract_op`). An `assigns` OUTSIDE a window still closes it and is
                # the method's own, exactly as before -> no existing program changes.
                open_dep["assigns"].append(c)
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
        node.csl_conforms_to = []          # `#@ conforms_to P1, P2, …` (ty2 / PEP 544)

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
                elif isinstance(c, ConformsToDecl):
                    node.csl_conforms_to = list(c.protocols)

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
            # H-I2 (noninterference): synthesize a self-composition twin (macsl's approach —
            # ../macsl src/macsl.ml emit_selfcomp). NOT a new relational WP mechanism; a
            # twin function that calls the target twice and asserts equal results.
            if hp.context == "noninterference":
                self._synthesize_selfcomp(python_ast, hp)
                continue
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
                    # unbounded loop fails to verify. This policy NAMES that guarantee, and it
                    # must therefore reject every way of ESCAPING that VC. There are two, not
                    # one (route #93 — the comment here used to say "the only opt-out"):
                    #   (a) `#@ \diverges` on the target explicitly opts out of termination;
                    #   (b) `#@ \trusted` / `#@ \abstract` on the target make Module 6 emit it
                    #       as a bodyless `val` (contract only, NO goals), so there is no loop
                    #       and no termination VC to discharge — the guarantee this policy names
                    #       is simply absent.
                    # MEASURED for (b): 0728's shape with the target marked `\trusted` and a
                    # body of `while True: acc = acc + 1` VERIFIED, i.e. an availability policy
                    # proved of a function whose body cannot terminate. Controls: 0726 proves,
                    # 0727's `\diverges` is rejected, 0728's variant-less loop fails.
                    # Sound-by-rejection, and consistent with the three SIBLING happy forms,
                    # every one of which already carries an explicit trusted/abstract trust
                    # boundary: the `protects` form (R1.1) and the region-write form (C) demand
                    # `#@ \preserves`, and the `reading` form (iv) demands membership of
                    # `except`. H-D was the only form with no trust boundary at all.
                    for fn in target_fns:
                        if getattr(fn, "csl_diverges", False):
                            raise PyCSLSemanticError(
                                f"`happy {hp.name}`: total target '{hp.target}' is marked "
                                f"`#@ \\diverges` — it opts OUT of termination, contradicting "
                                f"the totality (H-D) claim. Remove `\\diverges`, or drop the "
                                f"`total` policy.")
                        if (getattr(fn, "csl_trusted", False)
                                or getattr(fn, "csl_abstract", False)):
                            marker = ("\\trusted" if getattr(fn, "csl_trusted", False)
                                      else "\\abstract")
                            raise PyCSLSemanticError(
                                f"`happy {hp.name}`: total target '{hp.target}' is marked "
                                f"`#@ {marker}`, so it is emitted as a bodyless `val` with no "
                                f"goals — there is no termination VC, and the totality (H-D) "
                                f"guarantee this policy names cannot be discharged for it. "
                                f"Give '{hp.target}' a verified body (each loop carrying a "
                                f"`#@ loop variant`), or drop the `total` policy.")
                    # (#49) ROUTE #206 — THE REPAIR ABOVE REJECTED THE TRUSTED TARGET AND
                    # NOT THE TRUSTED CALLEE. Route #93 closed "the target is bodyless";
                    # a target with a perfectly good body whose work is ONE CALL to a
                    # bodyless stub is the same situation one hop away, and the totality
                    # VC is just as absent. MEASURED:
                    #     #@ happy availability: targets parse total
                    #     class Parser:
                    #         #@ ensures \result >= 0
                    #         #@ \trusted
                    #         def spin(self, n: int) -> int:
                    #             acc: int = 0
                    #             while True:          # cannot terminate
                    #                 acc = acc + 1
                    #             return acc
                    #         #@ no_exception \all
                    #         #@ ensures \result >= 0
                    #         def parse(self, n: int) -> int:
                    #             return self.spin(n)
                    # printed "Verification SUCCESS" (witness 1711) — an AVAILABILITY
                    # policy, whose stated purpose is that an attacker-controlled input
                    # cannot cause non-termination, proved of a function that never
                    # returns. CPython hangs. Controls unchanged: 0726 proves, 0728 fails,
                    # 1254/1255 stay refused.
                    # THE RULE: the totality claim covers the target's WHOLE call graph
                    # inside this module, so no bodyless function may be reachable from
                    # it. Transitive over module-local definitions only — an import is
                    # already a hard error here ("targets '<name>', which is not a method
                    # in this module").
                    # (#49) ROUTE #208 — AND `\diverges` IS THE THIRD WAY IN, WHICH MY
                    # OWN #206 REPAIR MISSED TWENTY MINUTES AFTER WRITING IT. #93 rejects
                    # `#@ \diverges` ON THE TARGET as the first opt-out it ever named;
                    # #206 added bodyless CALLEES; a `\diverges` CALLEE has a body and no
                    # termination VC, which is the same erasure by the most EXPLICIT
                    # declaration of non-termination the language has. MEASURED: the 1711
                    # shape with `#@ \diverges` in place of `#@ \trusted` on `spin`
                    # printed "Verification SUCCESS" (witness 1715). The set below is
                    # therefore "every module-local function with NO termination VC",
                    # not "every bodyless one" — which is what the rule always meant.
                    _r206_bodyless = set()
                    for _r206_f in funcs:
                        if (getattr(_r206_f, "csl_trusted", False)
                                or getattr(_r206_f, "csl_abstract", False)
                                or getattr(_r206_f, "csl_diverges", False)):
                            _r206_bodyless.add(_r206_f.name)
                    if _r206_bodyless:
                        _r206_calls = {}
                        for _r206_f in funcs:
                            _r206_set = set()
                            for _r206_n in ast.walk(_r206_f):
                                if isinstance(_r206_n, ast.Call):
                                    _r206_fn = _r206_n.func
                                    if isinstance(_r206_fn, ast.Name):
                                        _r206_set.add(_r206_fn.id)
                                    elif isinstance(_r206_fn, ast.Attribute):
                                        _r206_set.add(_r206_fn.attr)
                            _r206_calls[_r206_f.name] = _r206_set
                        _r206_seen = set()
                        _r206_queue = [hp.target]
                        _r206_hit = ""
                        while _r206_queue:
                            _r206_cur = _r206_queue.pop()
                            if _r206_cur in _r206_seen:
                                continue
                            _r206_seen.add(_r206_cur)
                            for _r206_callee in sorted(_r206_calls.get(_r206_cur, ())):
                                if _r206_callee in _r206_bodyless:
                                    _r206_hit = _r206_callee
                                    break
                                if _r206_callee in _r206_calls:
                                    _r206_queue.append(_r206_callee)
                            if _r206_hit:
                                break
                        if _r206_hit:
                            raise PyCSLSemanticError(
                                f"`happy {hp.name}`: total target '{hp.target}' reaches "
                                f"'{_r206_hit}', which is marked `#@ \\trusted`, "
                                f"`#@ \\abstract` or `#@ \\diverges` and therefore carries "
                                f"NO termination VC (the first two are emitted as a "
                                f"bodyless `val` with no goals; the third opts out "
                                f"explicitly). A non-terminating body inside "
                                f"'{_r206_hit}' costs the target NOTHING — its call is "
                                f"assumed to return — so the totality (H-D) guarantee this "
                                f"policy names is absent for '{hp.target}' too. Give "
                                f"'{_r206_hit}' a verified body (each loop carrying a "
                                f"`#@ loop variant`), or drop the `total` policy.")
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
                    # FINDING w68 / co-landing fix. `_collect_self_call_sites` matches ONLY
                    # `self.<target>(…)`, so a call through any other receiver
                    # (`other.transfer(…)`) is not a site and gets NO capability check —
                    # while the target keeps ASSUMING the capability as a `requires`
                    # (MEASURED: the assumption is real). Today that asymmetry is fenced only
                    # by a COMPLETENESS GAP, not a guard: a non-`self` call is OPAQUE in the
                    # model and propagates no postcondition at all (measured). The day
                    # cross-object calls carry their callee's contract — an obvious and
                    # frequently-wanted gain, since today it makes every cross-object call
                    # useless for proof — the capability becomes assumable at a call site
                    # nobody checks.
                    # INJECTING the check at such a site instead would be UNSOUND: the
                    # formula speaks about `self`, and at `other.transfer(…)` the object whose
                    # capability matters is `other`; proving `self.session_authenticated`
                    # there proves it of the WRONG object. So reject — sound-by-rejection,
                    # matching every sibling happy form's trust boundary. Keyed on the CALLEE
                    # (`func.attr == hp.target`), not on the receiver's shape: route #91's
                    # lesson, key on what is being called.
                    # Spelled INLINE rather than as a helper for the #33 reason below.
                    for _nd in ast.walk(python_ast):
                        if not (isinstance(_nd, ast.Call)
                                and isinstance(_nd.func, ast.Attribute)
                                and _nd.func.attr == hp.target):
                            continue
                        _recv = _nd.func.value
                        if isinstance(_recv, ast.Name) and _recv.id == "self":
                            continue
                        try:
                            _shown = ast.unparse(_recv)
                        except Exception:
                            _shown = "<expr>"
                        raise PyCSLSemanticError(
                            f"`happy {hp.name}`: '{hp.target}' is guarded by a capability "
                            f"precondition, but it is called here as "
                            f"`{_shown}.{hp.target}(…)` (L{getattr(_nd, 'lineno', 0)}) — "
                            f"through a receiver other than `self`. The call-site capability "
                            f"check can only be injected at a `self.{hp.target}(…)` site: the "
                            f"guarding formula speaks about `self`, so proving it here would "
                            f"prove the capability of the WRONG object, while '{hp.target}' "
                            f"still ASSUMES it. Call it as `self.{hp.target}(…)`, or drop the "
                            f"`precond` policy.")
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
                # (R3b) WHOLE-PATH AND SLICE STORES — route #92. `_collect_protect_index_sites`
                # matches only a POINT write, and its docstring DEFERRED the rest: "Slice/
                # whole-array writes to a parametric path are not certifiable per-object; they
                # are left to the non-footprint reject." THERE WAS NO SUCH REJECT — the
                # `CSLBool(False)` above fires only on sites that collector already returned,
                # which are exactly the point writes, and this branch `continue`s before the
                # R1/R2 `protects` form (which keys on the DOTTED PATH and would have caught
                # both). Measured: a non-exempt, footprint-less `d.disk = a` AND
                # `d.disk[512:576] = a` each VERIFIED, while `ensures d.disk[512] == 7` — the
                # preservation of a cell inside object 0's region — REFUSED, so both stores
                # genuinely reached the protected region and neither was erased. A per-index
                # footprint check cannot constrain a whole-array or slice store, so the
                # deferral becomes what the docstring always claimed it was: a rejection.
                for fn in funcs2:
                    if fn.name in except_set or fn.name == "__init__":
                        continue
                    for nd in ast.walk(fn):
                        if not isinstance(nd, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                            continue
                        tgts = (nd.targets if isinstance(nd, ast.Assign) else [nd.target])
                        for tgt in tgts:
                            if self._target_dotted_path(tgt) != path:
                                continue
                            is_sub = isinstance(tgt, ast.Subscript)
                            sl = tgt.slice if is_sub else None
                            if isinstance(sl, ast.Index):        # pre-3.9 wrapper
                                sl = sl.value
                            if is_sub and not isinstance(sl, ast.Slice):
                                continue                        # point write: handled above
                            kind = "slice" if is_sub else "whole-array"
                            raise PyCSLSemanticError(
                                f"`happy {hp.name}({hp.param})`: non-exempt '{fn.name}' "
                                f"performs a {kind} store to the protected path '{path}' "
                                f"(line {getattr(nd, 'lineno', 0)}), which a per-index "
                                f"`#@ footprint` check cannot confine to one object's region. "
                                f"Write through {path}[i] one index at a time so each write is "
                                f"checked against the footprint, or add '{fn.name}' to the "
                                f"`except` set if it is a legitimate whole-path owner.")
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
            # (A2) WHOLE-FIELD REBINDING — route #91. `_field_write_site` matches only a
            # `Subscript` target, so `self.<field> = <expr>` (an `Attribute` target, which
            # REPLACES the whole array, protected region included) matched nothing and got
            # NO check at all. Measured: a non-exempt `def wipe(self, a: list): self.disk = a`
            # VERIFIED, while in the same file `ensures self.disk[1000] == 99` (an
            # attacker-chosen value inside the region) PROVED and the preservation claim
            # `== 7` REFUSED — so the model itself certified the region had changed while the
            # property claiming it had not was proved. Sound-by-rejection, mirroring the
            # `protects` form (whose `_collect_protect_sites` matches the DOTTED PATH and so
            # already catches this) and the reading form's alias rejection above. `__init__`
            # is exempt: it CREATES the field, so there is no prior region for the property
            # to be about.
            for fn in funcs:
                if fn.name in except_set or fn.name == "__init__":
                    continue
                for nd in ast.walk(fn):
                    if not isinstance(nd, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                        continue
                    tgts = (nd.targets if isinstance(nd, ast.Assign) else [nd.target])
                    for tgt in tgts:
                        if (isinstance(tgt, ast.Attribute)
                                and isinstance(tgt.value, ast.Name)
                                and tgt.value.id == "self"
                                and tgt.attr == hp.field):
                            lo, hi = (self._region_bound_str(hp.region_lo),
                                      self._region_bound_str(hp.region_hi))
                            raise PyCSLSemanticError(
                                f"`happy {hp.name}`: non-exempt '{fn.name}' REBINDS the whole "
                                f"field 'self.{hp.field}' (line "
                                f"{getattr(nd, 'lineno', 0)}), replacing the protected region "
                                f"[{lo}, {hi}) wholesale — a per-index check cannot constrain "
                                f"a whole-array store. Write through self.{hp.field}[i] so "
                                f"each index is checked, or add '{fn.name}' to the `except` "
                                f"set if it is a legitimate owner.")
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
        are not certifiable per-object. They are NOT returned here, and — route #92 — they
        were NOT caught by the `CSLBool(False)` non-footprint reject either, which fires only
        on the sites THIS collector returns. They are now rejected outright by clause (R3b)
        in the R3 branch of `_weave_happy`.)"""
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

    def _synthesize_selfcomp(self, python_ast: ast.AST, hp: HappyProperty) -> None:
        """H-I2 noninterference via SELF-COMPOSITION (macsl's emit_selfcomp). Synthesize a
        twin method `<target>__selfcomp` into the target's class: it takes the PUBLIC params
        once and each SECRET param twice (`_a`/`_b`), calls the target twice (public shared,
        secret split), and asserts the two results are equal. Verified modularly from the
        target's result-`ensures`: if the result depends on a secret, `ra == rb` is
        unprovable — a leak. No new relational WP mechanism; a synthesized 1-safety driver."""
        target_fn = None
        target_cls = None
        for node in ast.walk(python_ast):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == hp.target:
                        target_fn, target_cls = item, node
        if target_fn is None:
            raise PyCSLSemanticError(
                f"`happy {hp.name}`: noninterference targets '{hp.target}', which is not a "
                f"method of any class in this module.")
        secret = list(hp.secret or [])
        ann_of = {a.arg: getattr(a, "annotation", None) for a in target_fn.args.args}
        formal = [a.arg for a in target_fn.args.args if a.arg != "self"]
        if not formal:
            raise PyCSLSemanticError(
                f"`happy {hp.name}`: noninterference target '{hp.target}' has no parameters.")
        for s in secret:
            if s not in formal:
                raise PyCSLSemanticError(
                    f"`happy {hp.name}`: secret '{s}' is not a parameter of '{hp.target}' "
                    f"(parameters: {formal}).")
        # FINDING w67 / co-landing fix. The twin synthesized below attaches EXACTLY ONE
        # obligation — `assert (ra == rb)` over the two RESULTS. NOTHING IN IT COMPARES
        # `self` ACROSS THE TWO CALLS, so what the form buys is RESULT-noninterference while
        # its name invites the reader to hear noninterference. A target that returns
        # something secret-independent and writes the secret verbatim into an observable
        # field satisfies the obligation exactly as written.
        #
        # The twin CANNOT be strengthened to cover the state channel: it calls the target
        # twice on the SAME `self`, sequentially, so there is no second initial state
        # against which to compare a final state — a genuine 2-run state relation needs a
        # second `self`, which this synthesis does not have. Today the channel is fenced
        # only by a COMPLETENESS GAP: a noninterference target that writes ANY field — even
        # a literal `0`, with no secret in sight — already fails on the twin's own
        # postcondition (MEASURED, finding w67; a target that merely READS state proves).
        # That is an accident, not a guard, and the day self-composition works through
        # state it evaporates and the state channel is unguarded.
        #
        # So reject the shape the obligation does not cover. REACHABILITY-based, not a scan
        # of the target's own body, so a mutation reached through a helper cannot walk past
        # it — keying a confinement check on the syntactic shape of one function is exactly
        # what routes #91/#92 punished. A call through a NON-`self` receiver needs no
        # traversal: it is opaque in the model and propagates nothing (finding w68).
        # Spelled INLINE rather than as a helper for the #33 reason below.
        _methods: Dict[str, Any] = {}
        for _node in ast.walk(python_ast):
            if isinstance(_node, ast.ClassDef):
                for _item in _node.body:
                    if isinstance(_item, ast.FunctionDef):
                        _methods.setdefault(_item.name, _item)
        _seen: set = set()
        _work = [target_fn]
        _writer = None
        while _work and _writer is None:
            _fn = _work.pop()
            if _fn.name in _seen:
                continue
            _seen.add(_fn.name)
            for _a in getattr(_fn, "csl_assigns", []) or []:
                _txt = getattr(_a, "raw", None) or str(getattr(_a, "expr", _a))
                if "self." in _txt:
                    _writer = (_fn.name, _txt.strip())
                    break
            if _writer is not None:
                break
            for _nd in ast.walk(_fn):
                _tgts = []
                if isinstance(_nd, ast.Assign):
                    _tgts = list(_nd.targets)
                elif isinstance(_nd, (ast.AugAssign, ast.AnnAssign)):
                    _tgts = [_nd.target]
                for _t in _tgts:
                    _base = _t
                    while isinstance(_base, ast.Subscript):
                        _base = _base.value
                    if (isinstance(_base, ast.Attribute)
                            and isinstance(_base.value, ast.Name)
                            and _base.value.id == "self"):
                        _writer = (_fn.name, "self." + _base.attr)
                        break
                if _writer is not None:
                    break
                if (isinstance(_nd, ast.Call) and isinstance(_nd.func, ast.Attribute)
                        and isinstance(_nd.func.value, ast.Name)
                        and _nd.func.value.id == "self"
                        and _nd.func.attr in _methods):
                    _work.append(_methods[_nd.func.attr])
        if _writer is not None:
            _wfn, _wfield = _writer
            _via = ("" if _wfn == hp.target
                    else f" (reached from '{hp.target}' via `self.{_wfn}(…)`)")
            raise PyCSLSemanticError(
                f"`happy {hp.name}`: noninterference target '{hp.target}' can WRITE state — "
                f"`{_wfield}` in '{_wfn}'{_via}. The synthesized self-composition twin "
                f"asserts only that the two RESULTS are equal (`ra == rb`); it calls the "
                f"target twice on the same `self`, so it has no second initial state and "
                f"CANNOT compare final state. A secret written into a field is therefore "
                f"OUTSIDE the property this form proves. Make '{hp.target}' state-free (no "
                f"`self.<field>` store on any path it reaches, `assigns \\nothing`), or drop "
                f"the noninterference policy — it would not mean what its name says.")
        line = getattr(target_fn, "lineno", 0)
        secset = set(secret)

        def _arg(nm, ann):
            a = ast.arg(); a.arg = nm; a.annotation = ann; a.type_comment = None
            return a

        def _name(nm, store=False):
            n = ast.Name(); n.id = nm; n.ctx = ast.Store() if store else ast.Load(); return n

        def _call(suffix):
            f = ast.Attribute(); f.value = _name("self"); f.attr = hp.target; f.ctx = ast.Load()
            c = ast.Call(); c.func = f; c.keywords = []
            c.args = [_name(p + suffix if p in secset else p) for p in formal]
            return c

        def _assign(tgt, val):
            a = ast.Assign(); a.targets = [_name(tgt, store=True)]; a.value = val
            a.type_comment = None; return a

        # twin params: self + public-once + secret-twice (signature order).
        twin_args = [_arg("self", None)]
        for p in formal:
            if p in secset:
                twin_args += [_arg(p + "_a", ann_of.get(p)), _arg(p + "_b", ann_of.get(p))]
            else:
                twin_args.append(_arg(p, ann_of.get(p)))
        argsobj = ast.arguments()
        argsobj.posonlyargs = []; argsobj.args = twin_args; argsobj.vararg = None
        argsobj.kwonlyargs = []; argsobj.kw_defaults = []; argsobj.kwarg = None
        argsobj.defaults = []

        ret = ast.Return(); zero = ast.Constant(); zero.value = 0; zero.kind = None
        ret.value = zero
        body = [_assign("ra", _call("_a")), _assign("rb", _call("_b")), ret]

        twin = ast.FunctionDef()
        twin.name = hp.target + "__selfcomp"
        twin.args = argsobj; twin.body = body; twin.decorator_list = []
        twin.returns = None; twin.type_comment = None; twin.type_params = []
        PyCSLWeaver._init_function_csl_fields(twin)
        # The relational obligation: equal public inputs => equal public outputs.
        pred = self.parser_module.parse_contract("check (ra == rb)", line).expr
        ret.csl_checkpoints = [CheckPoint("assert", pred,
                                          origin=f"happy {hp.name} noninterference ra==rb")]
        twin.lineno = line; twin.col_offset = 0
        ast.fix_missing_locations(twin)
        target_cls.body.append(twin)

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

    # (#33) A CONTRACT BLOCK WITH NOTHING TO ATTACH TO IS DISCARDED, AND THE RUN STILL
    # SAYS "All contracts formally proven". An annotation block binds to the node that
    # FOLLOWS it; a block with no follower is dropped silently. Measured: a trailing
    # `#@ ensures \result == 99` after a function returning 1 reported
    # `[+] Verification SUCCESS! All contracts formally proven.` It cannot make a false
    # statement provable, so it is not an unsoundness — it is the tool reporting success
    # for work it did not do, which is the same dishonesty in a different place.
    # STATEMENT-LEVEL directives are excluded and that exclusion is load-bearing: a
    # trailing `#@ assert` IS the last statement of a body and attaches correctly (corpus
    # 0710/0711/0712 end exactly that way). Filtering by directive KIND turns three false
    # positives into zero. CENSUS: 0 in every population — `pycsl-reference`,
    # `python-reference`, the negative corpus, the mirror, `pycsl_lib` and the live
    # emitter — so this is byte-inert, and `bin/check-dropped-mutation.py`'s DANGLING
    # counter (a hard 0) keeps it that way.
    # SPELLED INLINE, not as a helper: a new method on this class becomes a new abstract
    # `val module3_weaver___reject_dangling_contract_block` in the emission of EVERY mirror
    # that imports the weaver (measured — `frontend/__init__` and `frontend/ir_resolve`
    # both gained a declaration line and would each need a whole-file re-proof for a check
    # whose census is 0). Same reason as `Module5_IREmitter._py_expr_call`'s `_fin`-family
    # recognizer and `desugar`'s repeatability walk.
    # (#34) WHICH DIRECTIVES EACH ANCHOR ACTUALLY CONSUMES. Every attachment site in this
    # file is an `if/elif` chain with NO `else`, so a directive that reaches an anchor whose
    # site does not name its class is DROPPED — silently, while the run still prints
    # "All contracts formally proven". `process` already refused ONE case of that (a `#@`
    # block with nothing after it to attach to); this is the same hazard one step later,
    # where the block DOES have a follower but the follower ignores it.
    #
    # MEASURED VICTIMS, before this refusal:
    #   · `src/pycsl_lib/re/_engine.py` — TWO `#@ class invariant` separated from
    #     `class ReMatch:` by `__slots__` and a blank line, so they landed on `__init__`'s
    #     FunctionDef anchor. `ReMatch` had NO invariants in the model.
    #   · `src/pycsl_lib/os/UnixInodeFileSystem.py::_pad_name` — an `#@ assigns` and THREE
    #     `#@ ensures` written AFTER the docstring, so they landed on the first body
    #     statement. The source comment beside them says they are "surfaced as top-level
    #     ensures so `_blit_dir_entry` can chain them"; they were not top-level anything.
    #   · corpus `0299` — a `#@ loop invariant` + `#@ loop variant` above a `return`.
    #   · corpus `0878`/`0880` and three mirror witness files — a stray `#@ ensures`
    #     above a statement.
    # `\trusted` is in the FunctionDef set, so a misplaced `\trusted` is now a hard error
    # rather than a marker that counts but does nothing.
    _STMT_LEVEL = (CSLLabel, CheckPoint, GhostAssignDecl, GhostArraySetDecl)
    _ANY_ANCHOR = (DatatypeDecl, InductiveDecl, SharedDecl, MutexInvariant, LockOrder,
                   HappyProperty)
    _FUNCTION_LEVEL = (Requires, Ensures, Assigns, FunctionVariant, Diverges, NoInline,
                       SiblingConcrete, VerifyModule, PropagateFrame, FreshGlobals,
                       Trusted, Abstract, Lemma, Uses, InterfaceClause, Reveal, Preserves,
                       Footprint, RaisesDecl, NoExceptionDecl, BoundedIntDecl, ProofDecl,
                       ThreadEntry, Act, ForExpand, Complete, Disjoint, Given,
                       MixinDecl, ProvidesDecl, SharedStateDecl, TouchesFieldDecl,
                       MethodDependencyDecl, ComposeFromDecl, ConformsToDecl)
    _ACCEPTS = {
        "FunctionDef": _FUNCTION_LEVEL,
        "ClassDef": (ClassInvariant, AllowFinalizerDecl, MixinDecl, ComposeFromDecl,
                     ConformsToDecl),
        "While": (LoopInvariant, LoopVariant) + _STMT_LEVEL,
        "For": (LoopInvariant, LoopVariant, AllowIterationMutationDecl) + _STMT_LEVEL,
        "With": (CriticalSection, Acquires, Releases) + _STMT_LEVEL,
        "SimpleStatement": _STMT_LEVEL,
        "TrailingSimpleStatement": _STMT_LEVEL,
        "Module": (),
    }

    def _reject_misplaced_directives(self) -> None:
        """Refuse a `#@` directive whose anchor's attachment site would ignore it."""
        for extraction in self.extracted_data:
            accepted = self._ACCEPTS.get(extraction.node_type)
            if accepted is None:
                continue
            for node in self.parser_module.parse_node_contracts(
                    extraction.contracts, extraction.line_number):
                if isinstance(node, self._ANY_ANCHOR) or isinstance(node, accepted):
                    continue
                raise PyCSLSemanticError(
                    f"line {extraction.line_number}: a "
                    f"`{type(node).__name__}` directive is attached to a "
                    f"{extraction.node_type} anchor "
                    f"('{extraction.node_name}'), which does not consume it — the "
                    f"clause would be SILENTLY DISCARDED while the run still reported "
                    f"'All contracts formally proven'. A `#@` block binds to the node "
                    f"that FOLLOWS it: move it directly above the "
                    f"`def`/`class`/loop it describes.")

    def process(self) -> ast.AST:
        _stmt_lvl = ("assert", "assume", "ghost", "loop", "label",
                     "reveal", "unfold", "havoc")
        _lines = self.source_code.split("\n")
        _i = 0
        while _i < len(_lines):
            if not _lines[_i].strip().startswith("#@"):
                _i += 1
                continue
            _j, _kinds, _first = _i, [], _i + 1
            _col0 = True
            while _j < len(_lines) and (_lines[_j].strip().startswith("#")
                                        or not _lines[_j].strip()):
                _m = re.match(r"#@\s+\\?([a-z_]+)", _lines[_j].strip())
                if _m:
                    _kinds.append(_m.group(1))
                    if _lines[_j].startswith((" ", "\t")):
                        _col0 = False
                _j += 1
            # (#34) THE STATEMENT-LEVEL EXEMPTION ONLY HOLDS WHEN THE BLOCK IS INDENTED.
            # `assert`/`ghost`/`label`/… are exempt from the end-of-file refusal because a
            # trailing `#@ assert` IS the last statement of a body — but that is true only
            # INSIDE a body. At column 0 there is no enclosing block: Module 1's `_assign`
            # takes the `elif nxt is None: pass` branch ("module-level trailing comment
            # (indent 0) -> ignored, as libcst") and the directive is discarded. Measured:
            #     def f() -> int: ... return 0
            #     #@ assert 1 == 2                <-- FALSE, AND NEVER CHECKED
            #     [+] Verification SUCCESS! All contracts formally proven.
            # So an at-EOF block gets the exemption only if it is indented.
            if _j >= len(_lines) and (_col0 or any(_k not in _stmt_lvl for _k in _kinds)):
                raise PyCSLSemanticError(
                    f"line {_first}: this `#@` contract block has nothing after it to "
                    f"attach to (it runs to end-of-file), so it would be SILENTLY "
                    f"DISCARDED while the run still reports 'All contracts formally "
                    f"proven'. Move it directly above the `def`/`class` it describes, or "
                    f"delete it. (Directives: {', '.join(_kinds) or '<none>'}.)")
            _i = _j
        contracts_map, trailing_contracts_map = self._parse_extracted_contracts()
        self._reject_misplaced_directives()
        happy_props = self._extract_happy_properties(contracts_map)
        python_ast = ast.parse(self.source_code)
        # (#49) ROUTES #118 + #119 — A FUNCTION NAME IS NOT A CONSTANT IN PYTHON. Every call is
        # resolved against the `def` of that name (module function or class method), and
        # nothing consulted a LATER rebinding of it. Measured, each PROVING a contract of the
        # original def while CPython ran the replacement: `inc = dec`; a class-body `m = n`; a
        # module walrus `if (inc := dec):`; `global inc`; `_g["inc"] = dec` through a
        # `globals()` alias (route #116's last carrier); and, surviving the first repair
        # (#119, order 2): `C.m = C.n`, `vars()["inc"] = dec`, `locals()["inc"] = dec`,
        # `setattr(sys.modules[__name__], "inc", dec)`, and ANY of these inside an IMPORTED
        # module (the first repair sat in `pycsl._run_pipeline`, which imported dependencies
        # never pass through — `ir_resolve` runs its own Module 1-3-5). There is no model of a
        # rebound function, so REFUSE. PLACED HERE because this is the one step BOTH pipelines
        # share and it already raises (so `check-trusted-raises-honesty` and the mirror
        # emissions do not move — a `raise` in `Module5.visit_Module` measurably did).
        # Keyed on the NAME being bound or the OBJECT being written through, never on the
        # statement kind (two earlier cuts that enumerated kinds were each walked past).
        #   (1) one pass per SCOPE (the module, every class body) over every child node except
        #       nested def/class/lambda bodies: a Name Store/Del, import alias, except-as or
        #       match capture of a def/class/method name AFTER its definition; a constant
        #       `exec("...")` whose text names one is refused outright;
        #   (2) `global <def name>` anywhere;
        #   (3) a subscript store/del, or a mutating method call, through `globals()`,
        #       `vars()`, `locals()`, a name bound to one of them, or any `.__dict__`;
        #   (4) an attribute store/del whose attribute is a def/class/method name, on any
        #       receiver except `self` (`self.<m> = fn` inside the class is fenced today by the
        #       function-as-value "Symbol is already defined" error and is a WATCH item);
        #   (5) `setattr`/`delattr` whose attribute is a def/class/method name or not a string
        #       literal, on any receiver except `self`.
        # CENSUS (all four trees): no site of (1)-(3); (4) only `self.` stores in pycsl_lib;
        # (5) one, python-reference 0078 (expected-FAIL).
        _rb_defs: Dict[str, int] = {}
        _rb_all: set = set()
        _rb_globs: set = set()
        _rb_scopes: list = []
        for _rb_st in python_ast.body:
            if isinstance(_rb_st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                _rb_defs.setdefault(_rb_st.name, _rb_st.lineno)
            if (isinstance(_rb_st, ast.Assign) and len(_rb_st.targets) == 1
                    and isinstance(_rb_st.targets[0], ast.Name)
                    and isinstance(_rb_st.value, ast.Call)
                    and isinstance(_rb_st.value.func, ast.Name)
                    and _rb_st.value.func.id in ("globals", "vars", "locals")):
                _rb_globs.add(_rb_st.targets[0].id)
        _rb_all.update(_rb_defs)
        # IMPORTED objects (a module alias or an imported name): an attribute write on one of
        # them monkeypatches ANOTHER module (`plainlib.inc = plainlib.dec`, `K.m = K.n` after
        # `from plainlib import K`) — measured PROVING, the first cut only knew this file's defs.
        _rb_objs: set = set(_rb_defs)
        # (#49) ROUTE #127 — the BUILTINS namespace is an object too: `__builtins__.len = seven`
        # (no import needed) proved `len([1, 2]) == 2` while Python returned 7 (the first cut
        # rooted only on imports and defs). `builtins` is covered once imported.
        _rb_objs.add("__builtins__")
        for _rb_x in ast.walk(python_ast):
            if isinstance(_rb_x, (ast.Import, ast.ImportFrom)):
                for _rb_a in _rb_x.names:
                    _rb_objs.add((_rb_a.asname or _rb_a.name).split(".")[0])
        # (#49) ROUTE #127 — ALIASES of an object root, and COMPUTED receivers. The rules below
        # were keyed on the SPELLING of the receiver root; `bm = __builtins__; bm.len = seven`,
        # `pm = plainlib; pm.inc = abs` and `getattr(__builtins__, "__dict__")["len"] = seven`
        # each proved the original contract while Python ran the replacement. A name bound
        # (anywhere, any scope) to an expression that REACHES an object root through
        # attribute/subscript steps, or through a dynamic accessor call (`getattr`, `vars`,
        # `globals`, `locals`, `type`, `__import__`, `eval`, `*.import_module`), is itself an
        # object root, to a fixpoint. A CALL of a def/class (`C()`, `mk()`) produces a value,
        # not the object, and taints nothing. An alias is never exempted as a "local".
        _rb_alias: set = set()
        _rb_retobj: set = set()
        _rb_grew = True
        while _rb_grew:
            _rb_grew = False
            for _rb_x in ast.walk(python_ast):
                _rb_pairs: list = []
                if isinstance(_rb_x, ast.Assign):
                    _rb_pairs = [(_rb_t, _rb_x.value) for _rb_t in _rb_x.targets]
                elif isinstance(_rb_x, (ast.AnnAssign, ast.NamedExpr)) and _rb_x.value is not None:
                    _rb_pairs = [(_rb_x.target, _rb_x.value)]
                elif isinstance(_rb_x, (ast.For, ast.AsyncFor)):
                    _rb_pairs = [(_rb_x.target, _rb_x.iter)]
                elif isinstance(_rb_x, ast.withitem) and _rb_x.optional_vars is not None:
                    _rb_pairs = [(_rb_x.optional_vars, _rb_x.context_expr)]
                elif (isinstance(_rb_x, (ast.FunctionDef, ast.AsyncFunctionDef))
                      and _rb_x.name not in _rb_retobj):
                    # a FUNCTION whose return value reaches an object root makes every call of
                    # it an object (`def get(): return __builtins__`, then `bm = get()`).
                    _rb_rq: list = list(_rb_x.body)
                    while _rb_rq:
                        _rb_ry = _rb_rq.pop()
                        if isinstance(_rb_ry, (ast.FunctionDef, ast.AsyncFunctionDef,
                                               ast.ClassDef, ast.Lambda)):
                            continue
                        if isinstance(_rb_ry, ast.Return) and _rb_ry.value is not None:
                            _rb_pairs.append((None, _rb_ry.value))
                        _rb_rq.extend(ast.iter_child_nodes(_rb_ry))
                for _rb_t, _rb_v in _rb_pairs:
                    # the value REACHES an object when any name in it (outside the arguments of
                    # an ordinary call, whose RESULT is a value) is an object root or alias, or
                    # it calls a dynamic accessor, or it calls a function that returns an object.
                    _rb_hit = False
                    _rb_vq: list = [_rb_v]
                    while _rb_vq and not _rb_hit:
                        _rb_e = _rb_vq.pop()
                        if isinstance(_rb_e, (ast.Lambda, ast.ListComp, ast.SetComp, ast.DictComp,
                                              ast.GeneratorExp)):
                            continue
                        if isinstance(_rb_e, ast.Call):
                            _rb_f = _rb_e.func
                            if ((isinstance(_rb_f, ast.Name)
                                 and _rb_f.id in ("globals", "locals", "type", "__import__", "eval"))
                                    or (isinstance(_rb_f, ast.Attribute)
                                        and _rb_f.attr == "import_module")
                                    or (isinstance(_rb_f, ast.Name) and _rb_f.id in _rb_retobj)):
                                _rb_hit = True
                            elif (isinstance(_rb_f, ast.Name) and _rb_f.id in ("getattr", "vars")
                                    and _rb_e.args):
                                _rb_vq.append(_rb_e.args[0])
                            continue
                        if isinstance(_rb_e, ast.Name):
                            _rb_hit = _rb_e.id in _rb_objs or _rb_e.id in _rb_alias
                            continue
                        _rb_vq.extend(ast.iter_child_nodes(_rb_e))
                    if not _rb_hit:
                        continue
                    if _rb_t is None:
                        _rb_retobj.add(_rb_x.name)
                        _rb_grew = True
                        break
                    _rb_tq: list = [_rb_t]
                    while _rb_tq:
                        _rb_tn = _rb_tq.pop()
                        if isinstance(_rb_tn, (ast.Tuple, ast.List)):
                            _rb_tq.extend(_rb_tn.elts)
                        elif isinstance(_rb_tn, ast.Starred):
                            _rb_tq.append(_rb_tn.value)
                        elif (isinstance(_rb_tn, ast.Name) and _rb_tn.id != "self"
                                and _rb_tn.id not in _rb_alias):
                            _rb_alias.add(_rb_tn.id)
                            _rb_grew = True
        _rb_mod_body: list = list(python_ast.body)
        _rb_scopes.append((_rb_mod_body, _rb_defs))
        for _rb_cls in ast.walk(python_ast):
            if isinstance(_rb_cls, ast.ClassDef):
                _rb_cdefs: Dict[str, int] = {}
                for _rb_cst in _rb_cls.body:
                    if isinstance(_rb_cst, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        _rb_cdefs.setdefault(_rb_cst.name, _rb_cst.lineno)
                _rb_all.update(_rb_cdefs)
                if _rb_cdefs:
                    _rb_scopes.append((list(_rb_cls.body), _rb_cdefs))
        # (#49) ROUTE #127 — the receivers a NON-LITERAL `setattr` may write through: a local
        # bound ONLY by assignments from an ordinary call (`out = copy.deepcopy(node)`, the
        # emitter's own idiom) in the innermost enclosing function. A PARAMETER is not one:
        # `__init_subclass__(cls): setattr(cls, n, ...)` rebinds a subclass's method (measured
        # PROVING, Python 2). Keyed by the id of each call node inside that function.
        _rb_inst: Dict[int, set] = {}
        for _rb_fn2 in ast.walk(python_ast):
            if not isinstance(_rb_fn2, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            _rb_callsets: set = set()
            _rb_other: set = set()
            _rb_calls2: list = []
            _rb_q2: list = list(_rb_fn2.body)
            while _rb_q2:
                _rb_y2 = _rb_q2.pop()
                if isinstance(_rb_y2, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
                                       ast.Lambda)):
                    continue
                _rb_is_call_assign = (
                    isinstance(_rb_y2, ast.Assign) and len(_rb_y2.targets) == 1
                    and isinstance(_rb_y2.targets[0], ast.Name)
                    and isinstance(_rb_y2.value, ast.Call)
                    and not (isinstance(_rb_y2.value.func, ast.Name)
                             and _rb_y2.value.func.id in ("getattr", "vars", "globals", "locals",
                                                          "type", "__import__", "eval")))
                if _rb_is_call_assign:
                    _rb_callsets.add(_rb_y2.targets[0].id)
                    _rb_q2.append(_rb_y2.value)
                    continue
                if isinstance(_rb_y2, ast.Name) and isinstance(_rb_y2.ctx, (ast.Store, ast.Del)):
                    _rb_other.add(_rb_y2.id)
                if isinstance(_rb_y2, ast.Call):
                    _rb_calls2.append(_rb_y2)
                _rb_q2.extend(ast.iter_child_nodes(_rb_y2))
            _rb_fa2 = _rb_fn2.args
            _rb_params2 = {_rb_ar.arg for _rb_ar in (
                list(getattr(_rb_fa2, "posonlyargs", []) or []) + list(_rb_fa2.args)
                + list(_rb_fa2.kwonlyargs)
                + [x for x in (_rb_fa2.vararg, _rb_fa2.kwarg) if x is not None])}
            _rb_inst_locals = _rb_callsets - _rb_other - _rb_params2
            for _rb_c2 in _rb_calls2:
                _rb_inst[id(_rb_c2)] = _rb_inst_locals
        _rb_bad: list = []
        _rb_stack: list = []
        for _rb_body, _rb_sdefs in _rb_scopes:
            for _rb_x in _rb_body:
                _rb_stack.append((_rb_x, _rb_sdefs, getattr(_rb_x, "lineno", 0)))
        while _rb_stack:
            _rb_s, _rb_scope_defs, _rb_line = _rb_stack.pop()
            if isinstance(_rb_s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
                                  ast.Lambda)):
                continue
            _rb_line = getattr(_rb_s, "lineno", None) or _rb_line
            _rb_names: list = []
            if isinstance(_rb_s, ast.Name) and isinstance(_rb_s.ctx, (ast.Store, ast.Del)):
                _rb_names.append(_rb_s.id)
            elif isinstance(_rb_s, (ast.Import, ast.ImportFrom)):
                _rb_names = [(_rb_a.asname or _rb_a.name).split(".")[0] for _rb_a in _rb_s.names]
            elif isinstance(_rb_s, (ast.ExceptHandler, ast.MatchAs)):
                if isinstance(getattr(_rb_s, "name", None), str):
                    _rb_names.append(_rb_s.name)
            elif hasattr(ast, "MatchStar") and isinstance(_rb_s, ast.MatchStar):
                if isinstance(getattr(_rb_s, "name", None), str):
                    _rb_names.append(_rb_s.name)
            for _rb_n in _rb_names:
                if _rb_n in _rb_scope_defs and _rb_line > _rb_scope_defs[_rb_n]:
                    _rb_bad.append(f"`{_rb_n}` rebound at line {_rb_line}")
            for _rb_x in ast.iter_child_nodes(_rb_s):
                _rb_stack.append((_rb_x, _rb_scope_defs, _rb_line))
        for _rb_n in ast.walk(python_ast):
            _rb_ln = getattr(_rb_n, "lineno", 0)
            # A CONSTANT `exec("...")` is spliced in as source later (`splice_constant_exec`),
            # AFTER this check. Its text is not parsed here (a `try/except SyntaxError` in this
            # method measurably added an `exception SyntaxError` to two mirror emissions), so it
            # is refused CONSERVATIVELY when it so much as names a def/class/imported object.
            if (isinstance(_rb_n, ast.Call) and isinstance(_rb_n.func, ast.Name)
                    and _rb_n.func.id == "exec" and _rb_n.args
                    and isinstance(_rb_n.args[0], ast.Constant)
                    and isinstance(_rb_n.args[0].value, str)):
                _rb_toks = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", _rb_n.args[0].value))
                if _rb_toks & (_rb_all | _rb_objs):
                    _rb_bad.append(f"a constant `exec` naming a function or class at line {_rb_ln}")
            if isinstance(_rb_n, ast.Global):
                for _rb_g in _rb_n.names:
                    if _rb_g in _rb_defs:
                        _rb_bad.append(f"`global {_rb_g}` at line {_rb_ln}")
            _rb_ns = None
            if isinstance(_rb_n, ast.Subscript) and isinstance(_rb_n.ctx, (ast.Store, ast.Del)):
                _rb_ns = _rb_n.value
            elif (isinstance(_rb_n, ast.Call) and isinstance(_rb_n.func, ast.Attribute)
                    and _rb_n.func.attr in ("update", "__setitem__", "__delitem__", "pop",
                                            "popitem", "setdefault", "clear")):
                _rb_ns = _rb_n.func.value
            _rb_ns_alias = False
            if _rb_ns is not None:
                _rb_e2 = _rb_ns
                while True:
                    if isinstance(_rb_e2, (ast.Attribute, ast.Subscript)):
                        _rb_e2 = _rb_e2.value
                    elif isinstance(_rb_e2, ast.Call):
                        _rb_f2 = _rb_e2.func
                        if ((isinstance(_rb_f2, ast.Name)
                             and _rb_f2.id in ("globals", "locals", "type", "__import__", "eval"))
                                or (isinstance(_rb_f2, ast.Attribute)
                                    and _rb_f2.attr == "import_module")):
                            _rb_ns_alias = True
                            break
                        if (isinstance(_rb_f2, ast.Name) and _rb_f2.id in ("getattr", "vars")
                                and _rb_e2.args):
                            _rb_e2 = _rb_e2.args[0]
                            continue
                        break
                    else:
                        if isinstance(_rb_e2, ast.Name) and (
                                _rb_e2.id in _rb_alias or _rb_e2.id == "__builtins__"):
                            _rb_ns_alias = True
                        break
            if _rb_ns is not None and (
                    (isinstance(_rb_ns, ast.Name) and (_rb_ns.id in _rb_globs
                                                       or _rb_ns.id == "__builtins__"))
                    # (#127) a subscript store / mutating call whose receiver chain roots at an
                    # ALIAS of an object, or passes through a dynamic accessor call.
                    or _rb_ns_alias
                    or (isinstance(_rb_ns, ast.Call) and isinstance(_rb_ns.func, ast.Name)
                        and _rb_ns.func.id in ("globals", "vars", "locals"))
                    # (#138) `__dict__` is one of FOUR attributes that hand out a namespace
                    # mapping. `f.__globals__.__setitem__("N", 5)` on a module def PROVED
                    # `f() == 3` (CPython 5) — the receiver is an Attribute, so neither the
                    # `_rb_globs` name rule nor the `__dict__` rule saw it. CENSUS of the four
                    # spellings over the five trees: 2 sites (1402, 1403), both already
                    # expected-FAIL route witnesses.
                    or (isinstance(_rb_ns, ast.Attribute)
                        and _rb_ns.attr in ("__dict__", "__globals__", "f_globals",
                                            "f_locals"))):
                _rb_bad.append(f"a write through a namespace dict at line {_rb_ln}")
            if (isinstance(_rb_n, ast.Attribute) and isinstance(_rb_n.ctx, (ast.Store, ast.Del))
                    and _rb_n.attr in _rb_all
                    and not (isinstance(_rb_n.value, ast.Name) and _rb_n.value.id == "self")):
                _rb_bad.append(f"attribute `.{_rb_n.attr}` rebound at line {_rb_ln}")
            _rb_sa = None
            if (isinstance(_rb_n, ast.Call) and isinstance(_rb_n.func, ast.Name)
                    and _rb_n.func.id in ("setattr", "delattr") and len(_rb_n.args) >= 2):
                _rb_sa = (_rb_n.args[0], _rb_n.args[1])
            elif (isinstance(_rb_n, ast.Call) and isinstance(_rb_n.func, ast.Attribute)
                    and _rb_n.func.attr in ("__setattr__", "__delattr__")):
                # `object.__setattr__(c, "m", f)` / `type.__setattr__(C, "m", f)`: the SAME
                # write as `setattr`, spelled as a dunder call. `super().__setattr__(name, v)`
                # and `self.__setattr__(...)` are the instance-level spelling (WATCH, as (4)).
                _rb_fv = _rb_n.func.value
                if not ((isinstance(_rb_fv, ast.Name) and _rb_fv.id == "self")
                        or (isinstance(_rb_fv, ast.Call) and isinstance(_rb_fv.func, ast.Name)
                            and _rb_fv.func.id == "super")):
                    if len(_rb_n.args) >= 2:
                        _rb_sa = (_rb_n.args[0], _rb_n.args[1])
            if _rb_sa is not None and not (isinstance(_rb_sa[0], ast.Name)
                                           and _rb_sa[0].id == "self"):
                _rb_a1 = _rb_sa[1]
                _rb_lit = isinstance(_rb_a1, ast.Constant) and isinstance(_rb_a1.value, str)
                # A NON-LITERAL attribute name is refused only on a class-or-module-like
                # receiver (a module-level def/class name, or any non-Name expression such as
                # `sys.modules[__name__]` / `type(x)`): `setattr(out, f.name, v)` on a plain
                # local object is the emitter's own dataclass-copy idiom (live Module3_Weaver,
                # measured: refusing it refused two MIRROR files that import it) and is the
                # instance-level WATCH case, like `self.<m> = fn`.
                _rb_recv_cls = ((not isinstance(_rb_sa[0], ast.Name)) or _rb_sa[0].id in _rb_objs
                                or _rb_sa[0].id in _rb_alias)
                if ((_rb_lit and (_rb_a1.value in _rb_all
                                  or (isinstance(_rb_sa[0], ast.Name)
                                      and (_rb_sa[0].id in _rb_objs
                                           or _rb_sa[0].id in _rb_alias))))
                        or (not _rb_lit and (_rb_recv_cls or not (
                            isinstance(_rb_sa[0], ast.Name)
                            and _rb_sa[0].id in _rb_inst.get(id(_rb_n), set()))))):
                    _rb_bad.append(f"`setattr`/`delattr` of a function name at line {_rb_ln}")
        # (6) ANY attribute store/del on an object that IS a module-level def or class, or an
        # IMPORTED module/name —
        # `inc.__code__ = dec.__code__` rewrites what `inc(...)` runs without touching a name.
        # Scope-aware: inside a function the receiver must not be a parameter or a local of
        # that function (pure_ast's `node.lineno = ...` stores on a PARAMETER named like a
        # module function, and is not a rebinding).
        _rb_fscopes: list = [(python_ast.body, set())]
        for _rb_fn in ast.walk(python_ast):
            if isinstance(_rb_fn, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                _rb_locals: set = set()
                _rb_fa = _rb_fn.args
                for _rb_arg in (list(getattr(_rb_fa, "posonlyargs", []) or []) + list(_rb_fa.args)
                                + list(_rb_fa.kwonlyargs)
                                + [x for x in (_rb_fa.vararg, _rb_fa.kwarg) if x is not None]):
                    _rb_locals.add(_rb_arg.arg)
                _rb_fbody = _rb_fn.body if isinstance(_rb_fn.body, list) else [_rb_fn.body]
                _rb_globals_decl: set = set()
                _rb_st2: list = list(_rb_fbody)
                while _rb_st2:
                    _rb_y = _rb_st2.pop()
                    if isinstance(_rb_y, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
                                          ast.Lambda)):
                        if hasattr(_rb_y, "name"):
                            _rb_locals.add(_rb_y.name)
                        continue
                    if isinstance(_rb_y, ast.Name) and isinstance(_rb_y.ctx, (ast.Store, ast.Del)):
                        _rb_locals.add(_rb_y.id)
                    if isinstance(_rb_y, (ast.Import, ast.ImportFrom)):
                        # an `import` inside a function still names a MODULE object: patching
                        # it is global. Never let it hide as a "local".
                        for _rb_a in _rb_y.names:
                            _rb_globals_decl.add((_rb_a.asname or _rb_a.name).split(".")[0])
                    if isinstance(_rb_y, ast.Global):
                        _rb_globals_decl.update(_rb_y.names)
                    _rb_st2.extend(ast.iter_child_nodes(_rb_y))
                _rb_fscopes.append((_rb_fbody, _rb_locals - _rb_globals_decl))
        for _rb_body, _rb_loc in _rb_fscopes:
            _rb_st3: list = list(_rb_body)
            while _rb_st3:
                _rb_z = _rb_st3.pop()
                if isinstance(_rb_z, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                    continue
                if isinstance(_rb_z, ast.Attribute) and isinstance(_rb_z.ctx, (ast.Store, ast.Del)):
                    # Walk the receiver CHAIN to its root (`a.b[0].c` -> `a`), noting any call
                    # on the way (`importlib.import_module("m").inc = dec`, `type(c).m = f`).
                    _rb_root = _rb_z.value
                    _rb_has_call = False
                    while isinstance(_rb_root, (ast.Attribute, ast.Subscript, ast.Call)):
                        if isinstance(_rb_root, ast.Call):
                            _rb_has_call = True
                            _rb_root = _rb_root.func
                        else:
                            _rb_root = _rb_root.value
                    _rb_root_id = _rb_root.id if isinstance(_rb_root, ast.Name) else None
                    if ((_rb_root_id in _rb_objs and _rb_root_id not in _rb_loc)
                            or _rb_root_id in _rb_alias
                            or (_rb_has_call and _rb_root_id != "self")):
                        _rb_bad.append(f"attribute `.{_rb_z.attr}` written on "
                                       f"`{_rb_root_id or '<expr>'}...` at line "
                                       f"{getattr(_rb_z, 'lineno', 0)}")
                _rb_st3.extend(ast.iter_child_nodes(_rb_z))
        # (8) INSTANCE-LEVEL shadowing of a method: `self.m = abs` in `__init__` makes `c.m(-3)`
        # call `abs` (measured PROVING the method's contract, Python 3). A builtin value slips
        # past the function-as-value error that fenced `self.m = fn` for an in-file `fn`, so the
        # earlier WATCH exemption was wrong. Keyed on the METHODS OF THE ENCLOSING CLASS AND ITS
        # IN-MODULE BASES (a same-named field of an unrelated class is not a shadow: pycsl_lib
        # `subproc` stores `self.returncode` beside another class's `returncode` method).
        # `setattr(self, <non-literal>, v)` is refused only in a class that has a non-dunder
        # method to shadow (pure_ast's node base sets its fields that way and has only dunders).
        _rb_cls_by_name: Dict[str, Any] = {}
        for _rb_c in ast.walk(python_ast):
            if isinstance(_rb_c, ast.ClassDef):
                _rb_cls_by_name.setdefault(_rb_c.name, _rb_c)
        for _rb_c in ast.walk(python_ast):
            if not isinstance(_rb_c, ast.ClassDef):
                continue
            _rb_meths: set = set()
            _rb_todo: list = [_rb_c]
            _rb_seen: set = set()
            while _rb_todo:
                _rb_k = _rb_todo.pop()
                if id(_rb_k) in _rb_seen:
                    continue
                _rb_seen.add(id(_rb_k))
                _rb_meths |= {_rb_s.name for _rb_s in _rb_k.body
                              if isinstance(_rb_s, (ast.FunctionDef, ast.AsyncFunctionDef))}
                for _rb_b in _rb_k.bases:
                    if isinstance(_rb_b, ast.Name) and _rb_b.id in _rb_cls_by_name:
                        _rb_todo.append(_rb_cls_by_name[_rb_b.id])
                    elif not (isinstance(_rb_b, ast.Name) and _rb_b.id == "object"):
                        # a base NOT defined in this module (imported, builtin, or an
                        # expression): its methods are invisible here. A non-literal
                        # `setattr(self, name, v)` could shadow any of them — measured
                        # `C(K)` with `setattr(self, name, value)` and `C("m", int).m()`
                        # PROVING `K.m`'s contract, Python 0.
                        _rb_meths.add("<foreign-base>")
            _rb_has_plain = any(not (_rb_m.startswith("__") and _rb_m.endswith("__"))
                                for _rb_m in _rb_meths)
            for _rb_q in ast.walk(_rb_c):
                _rb_ql = getattr(_rb_q, "lineno", 0)
                if (isinstance(_rb_q, ast.Attribute) and isinstance(_rb_q.ctx, (ast.Store, ast.Del))
                        and isinstance(_rb_q.value, ast.Name) and _rb_q.value.id == "self"
                        and _rb_q.attr in _rb_meths):
                    _rb_bad.append(f"method `{_rb_q.attr}` shadowed by `self.{_rb_q.attr}` at line {_rb_ql}")
                _rb_sargs = None
                if (isinstance(_rb_q, ast.Call) and isinstance(_rb_q.func, ast.Name)
                        and _rb_q.func.id in ("setattr", "delattr") and len(_rb_q.args) >= 2
                        and isinstance(_rb_q.args[0], ast.Name) and _rb_q.args[0].id == "self"):
                    _rb_sargs = _rb_q.args[1]
                elif (isinstance(_rb_q, ast.Call) and isinstance(_rb_q.func, ast.Attribute)
                        and _rb_q.func.attr in ("__setattr__", "__delattr__") and _rb_q.args
                        and ((isinstance(_rb_q.func.value, ast.Name) and _rb_q.func.value.id == "self")
                             or (isinstance(_rb_q.func.value, ast.Call)
                                 and isinstance(_rb_q.func.value.func, ast.Name)
                                 and _rb_q.func.value.func.id == "super"))):
                    _rb_sargs = _rb_q.args[0]
                elif (isinstance(_rb_q, ast.Call) and isinstance(_rb_q.func, ast.Attribute)
                        and _rb_q.func.attr in ("__setattr__", "__delattr__")
                        and len(_rb_q.args) >= 2 and isinstance(_rb_q.args[0], ast.Name)
                        and _rb_q.args[0].id == "self"):
                    # `object.__setattr__(self, name, v)`: the unbound spelling of the same write.
                    _rb_sargs = _rb_q.args[1]
                if _rb_sargs is not None:
                    _rb_slit = isinstance(_rb_sargs, ast.Constant) and isinstance(_rb_sargs.value, str)
                    if (_rb_slit and _rb_sargs.value in _rb_meths) or (not _rb_slit and _rb_has_plain):
                        _rb_bad.append(f"method shadowed through `setattr` on self at line {_rb_ql}")
        if _rb_bad:
            raise PyCSLSemanticError(
                "a function, method or class NAME is rebound after its definition ("
                + "; ".join(sorted(set(_rb_bad))) + "). Every call is resolved against the "
                "`def`, so the rebinding would be silently ignored (measured: `inc = dec` then "
                "`inc(3)` proved the `inc` contract while Python ran `dec`). Rebinding a "
                "function name is not modelled; give the new binding its own name.")
        # (#49) ROUTES #121, #122 (module-scope arm), #124 — THREE MORE WAYS A NAME'S RUNTIME
        # BINDING DIFFERS FROM THE `def` EVERY CALL IS RESOLVED AGAINST. Measured at 7c9dede2,
        # each PROVING a claim CPython contradicts:
        #   #121 a DECORATOR is silently dropped: `def swap(fn): return abs`, `@swap def inc`
        #        -> `inc(-3)` proved `inc`'s contract (-2), Python 3.
        #   #122 a def inside a module-level `if`/`try` competes with another binding of the
        #        name and the model keeps the TEXTUALLY LAST one: `if FLAG == 1: def inc (-1)
        #        else: def inc (+1)`, and the fallback idiom `try: from m import inc / except
        #        ImportError: def inc` — both proved the fallback's contract, Python ran the other.
        #   #124 `from m import *` AFTER a def rebinds the name: proved the def's contract.
        # Keyed on the NAME and its BINDING SITES, never on the statement kind:
        #   (a) a decorator is allowed only when every binding of its root name in the file is
        #       either absent (and the name is a modelled builtin/marker: `property`,
        #       `staticmethod`, `mutable_state`, `dataclass`), or exactly ONE canonical import
        #       (`dataclasses.dataclass`, `functools.lru_cache/cache/cached_property`,
        #       `contextlib.contextmanager`, `typing.overload`), or exactly ONE module-level
        #       IDENTITY def (`def mutable_state(cls): return cls`); `mod.attr` only through a
        #       plain `import mod` of those modules.
        #   (b) a module-scope def/class NESTED IN A COMPOUND STATEMENT whose name has any other
        #       module-scope binding.
        #   (c) a star import preceded by a module-scope binding of any name other than the
        #       anchor `_` (a `from __future__` import binds nothing here).
        # CENSUS (pycsl-reference, python-reference, 53 mirrors, pycsl_lib): decorators in use
        # are dataclass, staticmethod, property, mutable_state (identity defs or unbound),
        # cached_property, lru_cache, contextmanager (+ `_contextmanager` alias), `_identity`
        # (an identity def) — all allowed; (b) 0 sites (json/tool.py's two compound defs have no
        # competing binding); (c) 0 sites (three star imports, each right after `_ = 0`).
        _dc_canon = {("dataclasses", "dataclass"), ("functools", "lru_cache"),
                     ("functools", "cache"), ("functools", "cached_property"),
                     ("contextlib", "contextmanager"), ("typing", "overload")}
        _dc_mods = {_dc_m for (_dc_m, _dc_a) in _dc_canon}
        _dc_bare_ok = {"property", "staticmethod", "mutable_state", "dataclass"}
        # every binding site of every name, file-wide: name -> [(kind, detail, node)]
        _dc_sites: Dict[str, list] = {}
        for _dc_n in ast.walk(python_ast):
            if isinstance(_dc_n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                _dc_sites.setdefault(_dc_n.name, []).append(("def", None, _dc_n))
                if not isinstance(_dc_n, ast.ClassDef):
                    _dc_fa = _dc_n.args
                    for _dc_arg in (list(getattr(_dc_fa, "posonlyargs", []) or [])
                                    + list(_dc_fa.args) + list(_dc_fa.kwonlyargs)
                                    + [x for x in (_dc_fa.vararg, _dc_fa.kwarg) if x is not None]):
                        _dc_sites.setdefault(_dc_arg.arg, []).append(("other", None, _dc_n))
            elif isinstance(_dc_n, ast.Lambda):
                for _dc_arg in _dc_n.args.args:
                    _dc_sites.setdefault(_dc_arg.arg, []).append(("other", None, _dc_n))
            elif isinstance(_dc_n, ast.Name) and isinstance(_dc_n.ctx, (ast.Store, ast.Del)):
                _dc_sites.setdefault(_dc_n.id, []).append(("other", None, _dc_n))
            elif isinstance(_dc_n, ast.Import):
                for _dc_a in _dc_n.names:
                    _dc_sites.setdefault((_dc_a.asname or _dc_a.name).split(".")[0], []).append(
                        ("module", _dc_a.name if not _dc_a.asname or "." not in _dc_a.name
                         else None, _dc_n))
            elif isinstance(_dc_n, ast.ImportFrom):
                for _dc_a in _dc_n.names:
                    if _dc_a.name == "*":
                        continue
                    _dc_sites.setdefault(_dc_a.asname or _dc_a.name, []).append(
                        ("from", (_dc_n.module or "", _dc_a.name) if not _dc_n.level else None,
                         _dc_n))
            elif isinstance(_dc_n, (ast.ExceptHandler, ast.MatchAs)) or (
                    hasattr(ast, "MatchStar") and isinstance(_dc_n, ast.MatchStar)):
                if isinstance(getattr(_dc_n, "name", None), str):
                    _dc_sites.setdefault(_dc_n.name, []).append(("other", None, _dc_n))
            elif isinstance(_dc_n, (ast.Global, ast.Nonlocal)):
                for _dc_g in _dc_n.names:
                    _dc_sites.setdefault(_dc_g, []).append(("other", None, _dc_n))
        _dc_bad: list = []
        for _dc_n in ast.walk(python_ast):
            if not isinstance(_dc_n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            for _dc_d in _dc_n.decorator_list:
                _dc_t = _dc_d.func if isinstance(_dc_d, ast.Call) else _dc_d
                _dc_ok = False
                _dc_root = _dc_t.id if isinstance(_dc_t, ast.Name) else (
                    _dc_t.value.id if (isinstance(_dc_t, ast.Attribute)
                                       and isinstance(_dc_t.value, ast.Name)) else None)
                _dc_s = _dc_sites.get(_dc_root, []) if _dc_root is not None else []
                _dc_kind, _dc_det, _dc_node = ("", None, None)
                if len(_dc_s) == 1:
                    _dc_kind, _dc_det, _dc_node = _dc_s[0]
                if isinstance(_dc_t, ast.Name):
                    if not _dc_s:
                        # a STAR import may bind the name to anything, so a bare builtin/marker
                        # is trusted only in a module without one.
                        _dc_ok = _dc_t.id in _dc_bare_ok and not any(
                            isinstance(_dc_si, ast.ImportFrom)
                            and any(_dc_sa.name == "*" for _dc_sa in _dc_si.names)
                            for _dc_si in ast.walk(python_ast))
                    elif _dc_kind == "from" and _dc_det in _dc_canon:
                        # the recognizers downstream key on the SPELLING (`_is_memoized` on
                        # `lru_cache`/`cache`/`cached_property`, `is_property` on `property`,
                        # the CM fixpoint on a `...contextmanager` suffix): an ALIAS of a
                        # canonical decorator would be ACCEPTED here and IGNORED there
                        # (measured: `cached_property as memo_prop` proved route #94's stale
                        # read). So the bound name must be the canonical one.
                        _dc_dm, _dc_da = _dc_det
                        _dc_ok = (_dc_t.id == _dc_da
                                  or (_dc_da == "contextmanager"
                                      and _dc_t.id.endswith("contextmanager")))
                    elif (_dc_kind == "def" and isinstance(_dc_node, ast.FunctionDef)
                          and _dc_node in python_ast.body):
                        _dc_body = list(_dc_node.body)
                        _dc_first = _dc_body[0] if _dc_body else None
                        if (isinstance(_dc_first, ast.Expr)
                                and isinstance(_dc_first.value, ast.Constant)
                                and isinstance(_dc_first.value.value, str)):
                            _dc_body = _dc_body[1:]
                        _dc_fa = _dc_node.args
                        _dc_ret = _dc_body[0] if len(_dc_body) == 1 else None
                        _dc_p0 = _dc_fa.args[0] if len(_dc_fa.args) == 1 else None
                        # an identity def must not borrow the spelling of a decorator a
                        # recognizer gives MEANING to (`def property(f): return f` would make
                        # `c.x` read the getter's value while Python returns the function).
                        _dc_ok = (_dc_t.id not in ("property", "staticmethod", "classmethod",
                                                   "dataclass", "lru_cache", "cache",
                                                   "cached_property", "overload")
                                  and not _dc_t.id.endswith("contextmanager")
                                  and not _dc_node.decorator_list and _dc_p0 is not None
                                  and not getattr(_dc_fa, "posonlyargs", [])
                                  and not _dc_fa.kwonlyargs and _dc_fa.vararg is None
                                  and _dc_fa.kwarg is None and not _dc_fa.defaults
                                  and isinstance(_dc_ret, ast.Return)
                                  and isinstance(_dc_ret.value, ast.Name)
                                  and _dc_ret.value.id == _dc_p0.arg)
                elif _dc_root is not None:
                    _dc_ok = (_dc_kind == "module" and _dc_det == _dc_root
                              and _dc_root in _dc_mods and (_dc_root, _dc_t.attr) in _dc_canon)
                if not _dc_ok:
                    _dc_bad.append(f"decorator `{ast.unparse(_dc_d)}` on `{_dc_n.name}` "
                                   f"(line {_dc_n.lineno})")
        # (b) defs/classes inside compound statements, and every binding site, per SCOPE: the
        # module and EVERY CLASS BODY (function/class bodies nested in a scope are excluded).
        # A class body is a scope too: `class C: if FLAG == 1: def m (2) else: def m (1)`
        # proved `C().m() == 1` (the textually last), Python 2 — measured on the first cut,
        # which walked only the module.
        _dc_mscope: Dict[str, list] = {}
        _dc_scope_list: list = [(python_ast.body, "the module")]
        for _dc_cl in ast.walk(python_ast):
            if isinstance(_dc_cl, ast.ClassDef):
                _dc_scope_list.append((_dc_cl.body, f"class `{_dc_cl.name}`"))
        _dc_is_module = True
        for _dc_sbody, _dc_sname in _dc_scope_list:
            _dc_sites2: Dict[str, list] = {}
            _dc_nested: list = []
            _dc_stack2: list = [(_dc_x, False) for _dc_x in _dc_sbody]
            while _dc_stack2:
                _dc_x, _dc_in_compound = _dc_stack2.pop()
                if isinstance(_dc_x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    _dc_sites2.setdefault(_dc_x.name, []).append(_dc_x.lineno)
                    if _dc_in_compound:
                        _dc_nested.append(_dc_x)
                    for _dc_dd in _dc_x.decorator_list:
                        _dc_stack2.append((_dc_dd, _dc_in_compound))
                    continue
                if isinstance(_dc_x, ast.Lambda):
                    continue
                _dc_bn: list = []
                if isinstance(_dc_x, ast.Name) and isinstance(_dc_x.ctx, (ast.Store, ast.Del)):
                    _dc_bn.append(_dc_x.id)
                elif isinstance(_dc_x, ast.Import):
                    _dc_bn = [(_dc_a.asname or _dc_a.name).split(".")[0] for _dc_a in _dc_x.names]
                elif isinstance(_dc_x, ast.ImportFrom) and _dc_x.module != "__future__":
                    _dc_bn = [_dc_a.asname or _dc_a.name for _dc_a in _dc_x.names
                              if _dc_a.name != "*"]
                elif isinstance(_dc_x, (ast.ExceptHandler, ast.MatchAs)) or (
                        hasattr(ast, "MatchStar") and isinstance(_dc_x, ast.MatchStar)):
                    if isinstance(getattr(_dc_x, "name", None), str):
                        _dc_bn.append(_dc_x.name)
                for _dc_b in _dc_bn:
                    _dc_sites2.setdefault(_dc_b, []).append(getattr(_dc_x, "lineno", 0))
                _dc_cmp = _dc_in_compound or isinstance(_dc_x, (ast.If, ast.Try, ast.For,
                                                                ast.While, ast.With,
                                                                ast.AsyncFor, ast.AsyncWith)) \
                    or type(_dc_x).__name__ in ("TryStar", "Match")
                for _dc_c in ast.iter_child_nodes(_dc_x):
                    _dc_stack2.append((_dc_c, _dc_cmp))
            for _dc_x in _dc_nested:
                if len(_dc_sites2.get(_dc_x.name, [])) > 1:
                    _dc_bad.append(f"`{_dc_x.name}` defined inside a compound statement at line "
                                   f"{_dc_x.lineno} and bound elsewhere in {_dc_sname}")
            if _dc_is_module:
                _dc_mscope = _dc_sites2
            _dc_is_module = False
        # (c) a star import after a module-scope binding (a star import can only appear at
        # module scope, but it may sit inside a module-level `if`/`try`), or after ANOTHER star
        # import (measured: `from a import *; from b import *` proved a's `inc` while Python
        # ran b's — the wildcard resolver keeps the first).
        _dc_stars = sorted((_dc_x.lineno, _dc_x.module) for _dc_x in ast.walk(python_ast)
                           if isinstance(_dc_x, ast.ImportFrom)
                           and any(_dc_a.name == "*" for _dc_a in _dc_x.names))
        _dc_first_star = True
        for _dc_sl, _dc_sm in _dc_stars:
            if not _dc_first_star:
                _dc_bad.append(f"a second star import `from {_dc_sm} import *` at line {_dc_sl}")
            _dc_first_star = False
        for _dc_x in ast.walk(python_ast):
            if isinstance(_dc_x, ast.ImportFrom) and any(_dc_a.name == "*" for _dc_a in _dc_x.names):
                _dc_prior = sorted(_dc_b for _dc_b, _dc_ls in _dc_mscope.items()
                                   if _dc_b != "_" and any(_dc_l < _dc_x.lineno for _dc_l in _dc_ls))
                if _dc_prior:
                    _dc_bad.append(f"`from {_dc_x.module} import *` at line {_dc_x.lineno} after "
                                   f"a binding of `{_dc_prior[0]}`")
        if _dc_bad:
            raise PyCSLSemanticError(
                "a name's runtime binding is not the `def` the model resolves it to ("
                + "; ".join(sorted(set(_dc_bad))) + "). A decorator whose effect is not "
                "modelled is silently dropped (measured: a decorator returning `abs` proved the "
                "undecorated contract); a def inside `if`/`try` that competes with another "
                "binding is resolved to the textually last one; a star import after a def "
                "rebinds it. None of these is modelled: use a modelled decorator (or an "
                "identity decorator `def d(f): return f`), give each definition its own "
                "name, or move the star import above every definition.")
        # (#49) ROUTES #130-#133 — FOUR MORE PLACES WHERE A NAME'S RUNTIME VALUE IS NOT THE ONE
        # THE MODEL READS. Measured at 65237fdb, each PROVING a claim CPython contradicts:
        #   #130 an IMPORTED name bound twice: `from plainlib import inc` then `from starlib
        #        import inc` (or `inc = plainlib.dec`, `import a as m; import b as m`, a from-import
        #        in a module `if`/`else`, a function-local import of another `inc`) — the model
        #        keeps the FIRST import (#118 rule (1) keys on this file's defs only).
        #   #131 a BUILTIN shadowed by an assignment: module `len = sum`, a local `len = sum`, a
        #        module `for max in [min]` — `len(xs)` still lowered to the builtin length.
        #   #132 the module/class CONSTANT FOLDERS (`module_collect.collect_module_*`,
        #        `_collect_class_constants`) take "bound exactly once" from the TOP-LEVEL
        #        single-name `Assign`/`AnnAssign` statements only: `N = 3; N += 2`, `if ...: N = 5`,
        #        `N, M = 5, 6`, `for N in [5]`, `setattr(sys.modules[__name__], "N", 5)`, a class
        #        body `N += 2`, and a folded str dict MUTATED (`OP.update(...)`, `OP["a"] = "c"`,
        #        `d = OP; d["a"] = "c"` in a function) all read the first literal.
        #   #133 a def NESTED IN A METHOD is lifted to a method of the class under its own name:
        #        named like a method of that class, it REPLACED the method's body and dropped its
        #        postcondition (`C.h` claiming 2 over `return 1` proved).
        # CENSUS (pycsl-reference, python-reference, 53 mirrors, pycsl_lib): #130 witness 1342
        # (already refused) and pycsl_lib json/tool.py (not ingested); #131 0 sites; #132 0 sites
        # beyond an unread `_`/`__all__`, plus pycsl_lib json/encoder.py `ESCAPE_DCT.setdefault`
        # (a genuine mutation of a folded dict); #133 0 sites.
        _nb_bad: list = []
        _nb_builtin_names = frozenset((
            "ArithmeticError", "AssertionError", "AttributeError", "BaseException", "BaseExceptionGroup",
            "BlockingIOError", "BrokenPipeError", "BufferError", "BytesWarning", "ChildProcessError",
            "ConnectionAbortedError", "ConnectionError", "ConnectionRefusedError", "ConnectionResetError",
            "DeprecationWarning", "EOFError", "Ellipsis", "EncodingWarning", "EnvironmentError",
            "Exception", "ExceptionGroup", "False", "FileExistsError", "FileNotFoundError",
            "FloatingPointError", "FutureWarning", "GeneratorExit", "IOError", "ImportError",
            "ImportWarning", "IndentationError", "IndexError", "InterruptedError", "IsADirectoryError",
            "KeyError", "KeyboardInterrupt", "LookupError", "MemoryError", "ModuleNotFoundError",
            "NameError", "None", "NotADirectoryError", "NotImplemented", "NotImplementedError", "OSError",
            "OverflowError", "PendingDeprecationWarning", "PermissionError", "ProcessLookupError",
            "PythonFinalizationError", "RecursionError", "ReferenceError", "ResourceWarning",
            "RuntimeError", "RuntimeWarning", "StopAsyncIteration", "StopIteration", "SyntaxError",
            "SyntaxWarning", "SystemError", "SystemExit", "TabError", "TimeoutError", "True", "TypeError",
            "UnboundLocalError", "UnicodeDecodeError", "UnicodeEncodeError", "UnicodeError",
            "UnicodeTranslateError", "UnicodeWarning", "UserWarning", "ValueError", "Warning",
            "ZeroDivisionError", "abs", "aiter", "all", "anext", "any", "ascii", "bin", "bool",
            "breakpoint", "bytearray", "bytes", "callable", "chr", "classmethod", "compile", "complex",
            "copyright", "credits", "delattr", "dict", "dir", "divmod", "enumerate", "eval", "exec", "exit",
            "filter", "float", "format", "frozenset", "getattr", "globals", "hasattr", "hash", "help",
            "hex", "id", "input", "int", "isinstance", "issubclass", "iter", "len", "license", "list",
            "locals", "map", "max", "memoryview", "min", "next", "object", "oct", "open", "ord", "pow",
            "print", "property", "quit", "range", "repr", "reversed", "round", "set", "setattr", "slice",
            "sorted", "staticmethod", "str", "sum", "super", "tuple", "type", "vars", "zip"))
        # binding sites per SCOPE (the module, every class body, every function body), not
        # descending into nested def/class/lambda bodies nor into comprehension targets:
        # name -> list of (kind, key, node); kind in def/store/import; key identifies an import.
        _nb_scopes: list = [("module", python_ast.body, None)]
        for _nb_x in ast.walk(python_ast):
            if isinstance(_nb_x, ast.ClassDef):
                _nb_scopes.append(("class", _nb_x.body, _nb_x))
            elif isinstance(_nb_x, (ast.FunctionDef, ast.AsyncFunctionDef)):
                _nb_scopes.append(("function", _nb_x.body, _nb_x))
        _nb_sites_of: Dict[int, Dict[str, list]] = {}
        for _nb_kind, _nb_body, _nb_owner in _nb_scopes:
            _nb_sites: Dict[str, list] = {}
            _nb_st: list = list(_nb_body)
            while _nb_st:
                _nb_y = _nb_st.pop()
                if isinstance(_nb_y, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    _nb_sites.setdefault(_nb_y.name, []).append(("def", None, _nb_y))
                    _nb_st.extend(_nb_y.decorator_list)
                    continue
                if isinstance(_nb_y, ast.Lambda):
                    continue
                if type(_nb_y).__name__ == "comprehension":
                    _nb_st.append(_nb_y.iter)
                    _nb_st.extend(_nb_y.ifs)
                    continue
                if isinstance(_nb_y, ast.Name) and isinstance(_nb_y.ctx, (ast.Store, ast.Del)):
                    _nb_sites.setdefault(_nb_y.id, []).append(("store", None, _nb_y))
                elif isinstance(_nb_y, ast.Import):
                    for _nb_a in _nb_y.names:
                        _nb_root = _nb_a.name.split(".")[0]
                        _nb_key = f"import {_nb_a.name}" if _nb_a.asname else f"import {_nb_root}"
                        _nb_sites.setdefault(_nb_a.asname or _nb_root, []).append(
                            ("import", _nb_key, _nb_y))
                elif isinstance(_nb_y, ast.ImportFrom):
                    for _nb_a in _nb_y.names:
                        if _nb_a.name == "*":
                            continue
                        _nb_sites.setdefault(_nb_a.asname or _nb_a.name, []).append(
                            ("import", f"from {_nb_y.level} {_nb_y.module} {_nb_a.name}", _nb_y))
                elif type(_nb_y).__name__ in ("ExceptHandler", "MatchAs", "MatchStar"):
                    if isinstance(getattr(_nb_y, "name", None), str):
                        _nb_sites.setdefault(_nb_y.name, []).append(("store", None, _nb_y))
                _nb_st.extend(ast.iter_child_nodes(_nb_y))
            _nb_sites_of[id(_nb_body)] = _nb_sites
        _nb_msites = _nb_sites_of.get(id(python_ast.body), {})
        # (#130) an imported name with any other binding site of a different key, per scope; a
        # function-local import of a name the module binds differently.
        for _nb_kind, _nb_body, _nb_owner in _nb_scopes:
            _nb_sites = _nb_sites_of.get(id(_nb_body), {})
            for _nb_n, _nb_ss in _nb_sites.items():
                _nb_ikeys = {_nb_k for (_nb_sk, _nb_k, _nb_nd) in _nb_ss if _nb_sk == "import"}
                if not _nb_ikeys:
                    continue
                _nb_allkeys = {_nb_k for (_nb_sk, _nb_k, _nb_nd) in _nb_ss}
                if len(_nb_allkeys) > 1:
                    _nb_bad.append(f"imported name `{_nb_n}` bound again in the same scope")
                if _nb_kind == "function" and _nb_n in _nb_msites:
                    _nb_mkeys = {_nb_k for (_nb_sk, _nb_k, _nb_nd) in _nb_msites[_nb_n]}
                    if _nb_mkeys != _nb_ikeys:
                        _nb_bad.append(f"imported name `{_nb_n}` in function "
                                       f"`{_nb_owner.name}` shadows a module binding")
        # (#131) a builtin name bound by a store in a scope where it is also called.
        for _nb_kind, _nb_body, _nb_owner in _nb_scopes:
            if _nb_kind == "class":
                continue
            _nb_sites = _nb_sites_of.get(id(_nb_body), {})
            _nb_shadow = {_nb_n for _nb_n, _nb_ss in _nb_sites.items()
                          if _nb_n in _nb_builtin_names
                          and any(_nb_sk == "store" for (_nb_sk, _nb_k, _nb_nd) in _nb_ss)}
            # a PARAMETER named like a builtin is a binding too: `def f(len, xs): return
            # len(xs)` lowered the call as the array length (`f(sum, [5]) == 1` proved, CPython 5).
            if _nb_kind == "function":
                _nb_pa = _nb_owner.args
                for _nb_a in (list(getattr(_nb_pa, "posonlyargs", []) or []) + list(_nb_pa.args)
                              + list(_nb_pa.kwonlyargs)
                              + [x for x in (_nb_pa.vararg, _nb_pa.kwarg) if x is not None]):
                    if _nb_a.arg in _nb_builtin_names:
                        _nb_shadow.add(_nb_a.arg)
            # `from builtins import sum as len` binds a builtin name to ANOTHER builtin; the
            # import resolver treats a `builtins` import as the builtin of the bound name
            # (measured past the first cut: `len([5]) == 1` proved, CPython 5).
            for _nb_n, _nb_ss in _nb_sites.items():
                for _nb_sk, _nb_k, _nb_nd in _nb_ss:
                    if (_nb_sk == "import" and isinstance(_nb_nd, ast.ImportFrom)
                            and _nb_nd.module in ("builtins", "__builtin__")):
                        for _nb_a in _nb_nd.names:
                            if _nb_a.asname and _nb_a.asname != _nb_a.name:
                                _nb_bad.append(f"builtin `{_nb_a.name}` imported as "
                                               f"`{_nb_a.asname}`")
            if not _nb_shadow:
                continue
            # any LOAD of the rebound name in that scope (a call, `raise ValueError`, `except
            # KeyError`, an `isinstance` argument): the first cut keyed on CALLS of a short
            # list and was walked past by `ValueError = KeyError` (a `raise`/`except` pair
            # proved the handler did not run, CPython 2). Census: 0 sites in the five trees.
            _nb_where = python_ast if _nb_owner is None else _nb_owner
            for _nb_c in ast.walk(_nb_where):
                if (isinstance(_nb_c, ast.Name) and isinstance(_nb_c.ctx, ast.Load)
                        and _nb_c.id in _nb_shadow):
                    _nb_bad.append(f"builtin `{_nb_c.id}` rebound by an assignment and "
                                   f"read at line {getattr(_nb_c, 'lineno', 0)}")
        # (#132) a module/class constant the folders take as bound once (one top-level
        # single-name Assign/AnnAssign of a literal) that is READ (a load, or a `#@` token)
        # and has another binding site in its scope, is named by a literal setattr on a
        # module-like receiver, or — a dict/set/list literal — is mutated or aliased anywhere.
        _nb_readers = frozenset((
            "get", "items", "keys", "values", "copy", "count", "index", "__contains__",
            "__getitem__", "union", "intersection", "difference", "issubset", "issuperset",
            "isdisjoint", "symmetric_difference"))
        _nb_pure_calls = frozenset((
            "len", "sorted", "list", "tuple", "set", "frozenset", "dict", "any", "all", "sum",
            "min", "max", "enumerate", "zip", "reversed", "str", "repr", "bool", "isinstance"))
        _nb_exec_names: set = set()
        _nb_parent: Dict[int, Any] = {}
        for _nb_x in ast.walk(python_ast):
            for _nb_c in ast.iter_child_nodes(_nb_x):
                _nb_parent[id(_nb_c)] = _nb_x
        _nb_contract_toks: set = set()
        for _nb_line in self.source_code.splitlines():
            if _nb_line.lstrip().startswith("#@"):
                _nb_contract_toks.update(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", _nb_line))
        _nb_loads: set = set()
        _nb_attr_loads: set = set()
        for _nb_x in ast.walk(python_ast):
            if isinstance(_nb_x, ast.Name) and isinstance(_nb_x.ctx, ast.Load):
                _nb_loads.add(_nb_x.id)
            elif isinstance(_nb_x, ast.Attribute) and isinstance(_nb_x.ctx, ast.Load):
                _nb_attr_loads.add(_nb_x.attr)
        for _nb_kind, _nb_body, _nb_owner in _nb_scopes:
            if _nb_kind == "function":
                continue
            _nb_sites = _nb_sites_of.get(id(_nb_body), {})
            _nb_once: Dict[str, list] = {}
            for _nb_ch in _nb_body:
                _nb_tg = None
                _nb_val = None
                if (isinstance(_nb_ch, ast.Assign) and len(_nb_ch.targets) == 1
                        and isinstance(_nb_ch.targets[0], ast.Name)):
                    _nb_tg = _nb_ch.targets[0]
                    _nb_val = _nb_ch.value
                elif (isinstance(_nb_ch, ast.AnnAssign) and isinstance(_nb_ch.target, ast.Name)
                        and _nb_ch.value is not None):
                    _nb_tg = _nb_ch.target
                    _nb_val = _nb_ch.value
                if _nb_tg is not None:
                    _nb_once.setdefault(_nb_tg.id, []).append((_nb_tg, _nb_val))
            for _nb_n, _nb_rows in _nb_once.items():
                if len(_nb_rows) != 1:
                    continue
                _nb_tg, _nb_val = _nb_rows[0]
                _nb_lit = (isinstance(_nb_val, ast.Constant)
                           or (isinstance(_nb_val, ast.UnaryOp)
                               and isinstance(_nb_val.operand, ast.Constant)))
                _nb_mut = (isinstance(_nb_val, (ast.Dict, ast.Set, ast.List, ast.Tuple))
                           or (isinstance(_nb_val, ast.Call) and isinstance(_nb_val.func, ast.Name)
                               and _nb_val.func.id in ("frozenset", "set")))
                # (#134) the same premise in two more single-binding recognizers: route #116's
                # `F("name")(args)` resolver takes `G = globals()` as bound once from the TOP-LEVEL
                # statements (`if True: G = {"inc": dec}` escaped: `F("inc")(3)` proved `inc`'s
                # result, CPython ran `dec`), and `collect_module_globals` takes `g = C(...)`
                # (a module-defined class) the same way.
                _nb_obj = (_nb_kind == "module" and isinstance(_nb_val, ast.Call)
                           and isinstance(_nb_val.func, ast.Name)
                           and (_nb_val.func.id in ("globals", "vars", "locals")
                                or any(isinstance(_nb_cd, ast.ClassDef)
                                       and _nb_cd.name == _nb_val.func.id
                                       for _nb_cd in python_ast.body)))
                if not (_nb_lit or _nb_mut or _nb_obj):
                    continue
                _nb_read = (_nb_n in _nb_contract_toks
                            or (_nb_n in _nb_loads if _nb_kind == "module"
                                else (_nb_n in _nb_attr_loads or _nb_n in _nb_loads)))
                if not _nb_read:
                    continue
                _nb_why = ""
                if any(_nb_nd is not _nb_tg for (_nb_sk, _nb_k, _nb_nd) in _nb_sites.get(_nb_n, [])):
                    _nb_why = "bound again in its scope"
                if _nb_kind == "module" and not _nb_why:
                    for _nb_x in ast.walk(python_ast):
                        if (isinstance(_nb_x, ast.Call) and isinstance(_nb_x.func, ast.Name)
                                and _nb_x.func.id in ("setattr", "delattr") and len(_nb_x.args) >= 2
                                and isinstance(_nb_x.args[1], ast.Constant)
                                and _nb_x.args[1].value == _nb_n
                                and not (isinstance(_nb_x.args[0], ast.Name)
                                         and _nb_x.args[0].id not in _rb_objs
                                         and _nb_x.args[0].id not in _rb_alias)):
                            _nb_why = "written by a literal `setattr`"
                            break
                # a MUTABLE literal of a shape a folder takes (a str-keyed dict, a str set, a list
                # of str tuples; a class-body str set): EVERY reference to the object must sit in
                # a read position — keyed on the object, never on the spelling of a write (the
                # first cut enumerated `d = OP` and was walked past by `d, e = OP, 1`, `for d in
                # [OP]` and `L = [OP]`). One level of aliasing into a plain name is allowed when
                # every load of that name is itself a read position.
                _nb_shape = _nb_val
                if (isinstance(_nb_shape, ast.Call) and isinstance(_nb_shape.func, ast.Name)
                        and _nb_shape.func.id == "set" and len(_nb_shape.args) == 1):
                    _nb_shape = _nb_shape.args[0]
                _nb_escape = False
                if isinstance(_nb_shape, ast.Set):
                    _nb_escape = all(isinstance(_nb_e, ast.Constant) and isinstance(_nb_e.value, str)
                                     for _nb_e in _nb_shape.elts)
                elif isinstance(_nb_shape, ast.Dict) and _nb_kind == "module":
                    _nb_escape = bool(_nb_shape.keys) and all(
                        isinstance(_nb_e, ast.Constant) and isinstance(_nb_e.value, str)
                        for _nb_e in _nb_shape.keys)
                elif isinstance(_nb_shape, ast.List) and _nb_kind == "module":
                    _nb_escape = bool(_nb_shape.elts) and all(
                        isinstance(_nb_e, ast.Tuple) for _nb_e in _nb_shape.elts)
                if _nb_escape and not _nb_why:
                    _nb_refs: list = []
                    for _nb_x in ast.walk(python_ast):
                        if (_nb_kind == "module" and isinstance(_nb_x, ast.Name)
                                and _nb_x.id == _nb_n and _nb_x is not _nb_tg):
                            _nb_refs.append(_nb_x)
                        elif (_nb_kind == "class" and isinstance(_nb_x, ast.Attribute)
                                and _nb_x.attr == _nb_n):
                            _nb_refs.append(_nb_x)
                        elif (_nb_kind == "class" and isinstance(_nb_x, ast.Name)
                                and _nb_x.id == _nb_n and _nb_x is not _nb_tg):
                            _nb_refs.append(_nb_x)
                    _nb_aliases: set = set()
                    _nb_depth = 0
                    while _nb_refs and not _nb_why:
                        _nb_next: list = []
                        for _nb_r in _nb_refs:
                            _nb_p = _nb_parent.get(id(_nb_r))
                            if not isinstance(getattr(_nb_r, "ctx", None), ast.Load):
                                _nb_why = "mutated or rebound"
                            elif (isinstance(_nb_p, ast.Attribute) and _nb_p.value is _nb_r
                                    and _nb_p.attr in _nb_readers):
                                continue
                            elif (isinstance(_nb_p, ast.Subscript) and _nb_p.value is _nb_r
                                    and isinstance(_nb_p.ctx, ast.Load)):
                                continue
                            elif isinstance(_nb_p, ast.BinOp):
                                continue
                            elif (isinstance(_nb_p, ast.Compare) and _nb_r is not _nb_p.left
                                    and all(isinstance(_nb_o, (ast.In, ast.NotIn))
                                            for _nb_o in _nb_p.ops)):
                                continue
                            elif (type(_nb_p).__name__ in ("For", "AsyncFor", "comprehension")
                                    and getattr(_nb_p, "iter", None) is _nb_r):
                                continue
                            elif (isinstance(_nb_p, ast.Call) and _nb_r in _nb_p.args
                                    and isinstance(_nb_p.func, ast.Name)
                                    and _nb_p.func.id in _nb_pure_calls):
                                continue
                            elif (_nb_depth == 0
                                    and isinstance(_nb_p, (ast.Assign, ast.AnnAssign, ast.NamedExpr))
                                    and _nb_p.value is _nb_r):
                                _nb_tgts = (list(_nb_p.targets) if isinstance(_nb_p, ast.Assign)
                                            else [_nb_p.target])
                                for _nb_t in _nb_tgts:
                                    if isinstance(_nb_t, ast.Name):
                                        _nb_aliases.add(_nb_t.id)
                                    else:
                                        _nb_why = "aliased"
                            else:
                                _nb_why = "aliased or mutated"
                            if _nb_why:
                                break
                        if _nb_depth == 0 and _nb_aliases and not _nb_why:
                            for _nb_x in ast.walk(python_ast):
                                if (isinstance(_nb_x, ast.Name) and _nb_x.id in _nb_aliases
                                        and isinstance(_nb_x.ctx, ast.Load)):
                                    _nb_next.append(_nb_x)
                        _nb_refs = _nb_next
                        _nb_depth = _nb_depth + 1
                if _nb_why:
                    _nb_where = "the module" if _nb_owner is None else f"class `{_nb_owner.name}`"
                    _nb_bad.append(f"constant `{_nb_n}` of {_nb_where} {_nb_why}")
                _nb_exec_names.add(_nb_n)
        # a CONSTANT `exec("...")` is spliced in as source AFTER this check: refuse one whose text
        # names a builtin, an imported name, or a folded constant (measured: `exec("len = sum")`
        # proved `len([5]) == 1` past the first cut).
        for _nb_n, _nb_ss in _nb_msites.items():
            if any(_nb_sk == "import" for (_nb_sk, _nb_k, _nb_nd) in _nb_ss):
                _nb_exec_names.add(_nb_n)
        for _nb_x in ast.walk(python_ast):
            if (isinstance(_nb_x, ast.Call) and isinstance(_nb_x.func, ast.Name)
                    and _nb_x.func.id == "exec" and _nb_x.args
                    and isinstance(_nb_x.args[0], ast.Constant)
                    and isinstance(_nb_x.args[0].value, str)):
                _nb_toks = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", _nb_x.args[0].value))
                if _nb_toks & (_nb_exec_names | _nb_builtin_names):
                    _nb_bad.append(f"a constant `exec` naming a builtin, an imported name or a "
                                   f"constant at line {getattr(_nb_x, 'lineno', 0)}")
        # (#135) MODULE-SCOPE and CLASS-BODY code is never lowered: the weaver is its only
        # fence, and #127's alias taint keys on how a value is SPELLED (an ordinary call
        # "produces a value"). `m = ident(plainlib); m.inc = plainlib.dec`, `(lambda:
        # plainlib)()`, `[x for x in [plainlib]][0]`, `ident(x=plainlib)` and
        # `setattr(ident(plainlib), "inc", ...)` each proved the original `inc` (CPython ran
        # `dec`). Keyed on the SINK: in those scopes an attribute store/delete, or a
        # `setattr`/`delattr`, is allowed only on a receiver rooted at a name whose every
        # binding in the file is a literal or a call of a class defined in this module (a
        # fresh object), or at a name with no module-scope binding at all.
        _nb_fresh_ok: Dict[str, bool] = {}
        _nb_modcls = {_nb_cd.name for _nb_cd in python_ast.body if isinstance(_nb_cd, ast.ClassDef)}
        _nb_has_star = any(isinstance(_nb_x, ast.ImportFrom)
                           and any(_nb_a.name == "*" for _nb_a in _nb_x.names)
                           for _nb_x in ast.walk(python_ast))
        # (#137) THE NODES THAT ACTUALLY RUN WHEN THE MODULE (or a class body) RUNS. The first
        # cut walked `iter_child_nodes` and `continue`d on every FunctionDef and Lambda, so
        # THREE module-scope execution sites were never scanned at all (each PROVED the
        # original `inc` while CPython ran `dec`):
        #   a LAMBDA BODY called in place — `(lambda m: setattr(m, "inc", plainlib.dec))
        #   (plainlib)` — where #119 rule (6) also exempts the lambda's PARAMETER receiver;
        #   the same lambda in a CLASS BODY;
        #   a def's DEFAULT ARGUMENT / annotation / decorator expression, all evaluated at
        #   DEFINITION time — `def h(z = (lambda m: setattr(m, "inc", ...))(plainlib))`.
        # A def's BODY is NOT executed here and stays out (an in-function patch is fenced by
        # the value model). A lambda's body is admitted fail-closed: whether it is called in
        # place cannot be read off the syntax.
        # NO NESTED `def` HERE: this file is mirrored, `check-mirror-coverage` counts nested
        # FunctionDefs, and the first cut's two helpers were LIFTED into methods and emitted
        # as two extra abstract `val`s in `frontend/__init__` and `frontend/ir_resolve` (the
        # two mirrors that ingest this one) — 2 MOVED on the mirror byte-diff.
        _nb_lam_params: set = set()
        _nb_mx_of: Dict[int, list] = {}
        for _nb_kind, _nb_body, _nb_owner in _nb_scopes:
            if _nb_kind == "function":
                continue
            _nb_out: list = []
            _nb_stk: list = list(_nb_body)
            while _nb_stk:
                _nb_y = _nb_stk.pop()
                if isinstance(_nb_y, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                    _nb_ar = _nb_y.args
                    _nb_stk.extend([_nb_d for _nb_d in (_nb_ar.defaults or [])
                                    if _nb_d is not None])
                    _nb_stk.extend([_nb_d for _nb_d in (_nb_ar.kw_defaults or [])
                                    if _nb_d is not None])
                    if isinstance(_nb_y, ast.Lambda):
                        for _nb_a in (list(getattr(_nb_ar, "posonlyargs", []) or [])
                                      + list(_nb_ar.args) + list(_nb_ar.kwonlyargs)
                                      + [_nb_v for _nb_v in (_nb_ar.vararg, _nb_ar.kwarg)
                                         if _nb_v is not None]):
                            _nb_lam_params.add(_nb_a.arg)
                        _nb_stk.append(_nb_y.body)
                        continue
                    _nb_stk.extend(_nb_y.decorator_list)
                    _nb_stk.extend([_nb_a.annotation
                                    for _nb_a in (list(getattr(_nb_ar, "posonlyargs", []) or [])
                                                  + list(_nb_ar.args) + list(_nb_ar.kwonlyargs)
                                                  + [_nb_v for _nb_v in (_nb_ar.vararg,
                                                                         _nb_ar.kwarg)
                                                     if _nb_v is not None])
                                    if _nb_a.annotation is not None])
                    if _nb_y.returns is not None:
                        _nb_stk.append(_nb_y.returns)
                    continue
                if isinstance(_nb_y, ast.ClassDef):
                    # the class BODY is its own scope entry in `_nb_scopes`; only the header
                    # expressions run here.
                    _nb_stk.extend(_nb_y.decorator_list)
                    _nb_stk.extend(_nb_y.bases)
                    _nb_stk.extend(_nb_y.keywords)
                    continue
                _nb_out.append(_nb_y)
                _nb_stk.extend(ast.iter_child_nodes(_nb_y))
            _nb_mx_of[id(_nb_body)] = _nb_out
        # the bindings that a module-scope / class-body receiver name refers to: those in the
        # module and class bodies themselves (a function-local binding is another variable).
        _nb_mnodes: list = []
        for _nb_kind, _nb_body, _nb_owner in _nb_scopes:
            if _nb_kind == "function":
                continue
            _nb_mnodes.extend(_nb_mx_of.get(id(_nb_body), []))
        for _nb_x in _nb_mnodes:
            _nb_pairs: list = []
            if isinstance(_nb_x, ast.Assign):
                for _nb_t in _nb_x.targets:
                    _nb_pairs.append((_nb_t, _nb_x.value))
            elif isinstance(_nb_x, (ast.AnnAssign, ast.NamedExpr)):
                _nb_pairs.append((_nb_x.target, _nb_x.value))
            elif isinstance(_nb_x, (ast.For, ast.AsyncFor)):
                _nb_pairs.append((_nb_x.target, None))
            elif type(_nb_x).__name__ == "withitem" and _nb_x.optional_vars is not None:
                _nb_pairs.append((_nb_x.optional_vars, None))
            # (#137) the first cut enumerated the binding forms its author pictured, and a
            # name bound by any OTHER form fell to the `not _nb_has_star` DEFAULT, i.e. FRESH.
            # Measured: `[setattr(m, "inc", plainlib.dec) for m in [plainlib]]` at module
            # scope proved the original `inc` (CPython ran `dec`) — the sink saw the
            # `setattr`, but the comprehension target `m` was never recorded.
            elif isinstance(_nb_x, ast.AugAssign):
                _nb_pairs.append((_nb_x.target, None))
            elif type(_nb_x).__name__ == "comprehension":
                _nb_pairs.append((_nb_x.target, None))
            elif type(_nb_x).__name__ in ("ExceptHandler", "MatchAs", "MatchStar"):
                if isinstance(getattr(_nb_x, "name", None), str):
                    _nb_fresh_ok[_nb_x.name] = False
            elif isinstance(_nb_x, (ast.Import, ast.ImportFrom)):
                for _nb_a in _nb_x.names:
                    if _nb_a.name != "*":
                        _nb_fresh_ok[_nb_a.asname or _nb_a.name.split(".")[0]] = False
            for _nb_t, _nb_v in _nb_pairs:
                _nb_good = (isinstance(_nb_t, ast.Name) and _nb_v is not None
                            and (isinstance(_nb_v, (ast.Constant, ast.Dict, ast.List, ast.Set))
                                 or (isinstance(_nb_v, ast.Call)
                                     and isinstance(_nb_v.func, ast.Name)
                                     and _nb_v.func.id in _nb_modcls)))
                for _nb_tn in ast.walk(_nb_t):
                    if isinstance(_nb_tn, ast.Name) and not isinstance(_nb_tn.ctx, ast.Load):
                        _nb_fresh_ok[_nb_tn.id] = _nb_fresh_ok.get(_nb_tn.id, True) and _nb_good
        # a LAMBDA PARAMETER is bound by the caller, not by the module: it describes no
        # object this file can see (the `(lambda m: setattr(m, ...))(plainlib)` carrier).
        for _nb_n in _nb_lam_params:
            _nb_fresh_ok[_nb_n] = False
        # `__builtins__` is never bound by this file, so the "no module-scope binding" exemption
        # would have made THE builtin namespace the one receiver every sink here trusts.
        _nb_fresh_ok["__builtins__"] = False
        # (#138) the mutating DICT methods #118 already enumerates. At module/class-body scope
        # they are the same sink as a subscript store, one spelling over: `f.__globals__
        # .__setitem__("N", 5)` PROVED `f() == 3` (CPython 5) past gen #26's draft-9, whose
        # subscript rule keys on the PATH but never sees a method call.
        _nb_mutators = frozenset(("update", "__setitem__", "__delitem__", "pop", "popitem",
                                  "setdefault", "clear"))
        for _nb_kind, _nb_body, _nb_owner in _nb_scopes:
            if _nb_kind == "function":
                continue
            for _nb_y in _nb_mx_of.get(id(_nb_body), []):
                _nb_recv = None
                if isinstance(_nb_y, ast.Attribute) and isinstance(_nb_y.ctx, (ast.Store, ast.Del)):
                    _nb_recv = _nb_y.value
                elif (isinstance(_nb_y, ast.Call) and isinstance(_nb_y.func, ast.Name)
                        and _nb_y.func.id in ("setattr", "delattr") and _nb_y.args):
                    _nb_recv = _nb_y.args[0]
                # (#138) a `getattr` AT MODULE/CLASS-BODY SCOPE hands out an object this file
                # cannot describe, and gen #26's computed-getattr arm scoped itself TWICE by
                # things an alias defeats: by the RECEIVER'S NAME (`_nb_imported` is file-wide,
                # so `b = builtins; getattr(b, "set" + "attr")(plainlib, "inc", plainlib.dec)`
                # walked past it) and by the SYNTACTIC SHAPE `Call(func=Call(getattr, ...))`
                # (so `sa = getattr(builtins, "set" + "attr"); sa(...)` walked past it too).
                # BOTH PROVED `plainlib.inc(3) == 4`; CPython returns 2. Keyed on the PATH, like
                # every other sink here. CENSUS of module/class-scope `getattr`: 2 sites, both
                # already-expected-FAIL route witnesses (1351, 1396); 0 in python-reference, the
                # 53 mirrors, `pycsl_lib` and `src/pycsl` (the emitter's own
                # `getattr(self, handler_name)(node)` dispatch is inside function bodies).
                elif (isinstance(_nb_y, ast.Call) and isinstance(_nb_y.func, ast.Name)
                        and _nb_y.func.id == "getattr" and _nb_y.args):
                    _nb_recv = _nb_y.args[0]
                # (#138) ... and a MUTATING DICT METHOD on a receiver this file cannot describe.
                # CENSUS: 12 module/class-scope sites over the five trees — 1401 (already
                # expected-FAIL) plus eleven whose receiver IS a fresh name (`b = Buffer()` in
                # 0192, `ESCAPE_DCT` and `_EMIT_IR_HANDLER_ATTR_PROJ`, both module dict
                # literals), so no live program changes verdict.
                elif (isinstance(_nb_y, ast.Call) and isinstance(_nb_y.func, ast.Attribute)
                        and _nb_y.func.attr in _nb_mutators):
                    _nb_recv = _nb_y.func.value
                # a SUBSCRIPT store is the same sink one spelling over. #118's rule
                # enumerates the DICT spellings that name a namespace (`globals()[k]`,
                # `vars()[k]`, `<mod>.__dict__[k]`), and two more reach the very same
                # dict: `f.__globals__["N"] = 5` on a module def and
                # `inspect.currentframe().f_globals["N"] = 5` both PROVED `N == 3`
                # (CPython 5). Keyed on the PATH being written, not on the spelling:
                # at module/class-body scope the receiver must be a name this file can
                # describe. CENSUS of non-Name receivers: 2 in pycsl-reference (1326 and
                # 1351, both already expected-FAIL), 0 everywhere else.
                elif isinstance(_nb_y, ast.Subscript) and isinstance(_nb_y.ctx,
                                                                     (ast.Store, ast.Del)):
                    _nb_recv = _nb_y.value
                if _nb_recv is not None:
                    # the receiver itself must be that name: a deeper chain (`m.x.inc`,
                    # `ms[0].inc`) reaches an object the binding does not describe (measured
                    # past the first cut: `m = H(plainlib); m.x.inc = ...` and `ms =
                    # [ident(plainlib)]; ms[0].inc = ...` both proved the original `inc`).
                    # a name with no module-scope binding is exempt only in a file without a
                    # star import (`from aliaslib import *` exporting `pm = plainlib`, then
                    # `pm.inc = plainlib.dec`, proved the original `inc` past the second cut).
                    if not (isinstance(_nb_recv, ast.Name)
                            and _nb_fresh_ok.get(_nb_recv.id, not _nb_has_star)):
                        _nb_bad.append(f"an attribute or item written, or a namespace reached, "
                                       f"at {_nb_kind} scope on a computed receiver at line "
                                       f"{getattr(_nb_y, 'lineno', 0)}")
        # (#136) A DYNAMIC `exec`, AND AN `eval` THAT CAN BIND, REBIND NAMES WHOSE VALUES THE
        # MODEL HAS ALREADY FOLDED OR RESOLVED — and NOTHING downstream models the value.
        # `exec_splice.py` splices only a CONSTANT single-argument `exec` and defers the rest
        # to "scope havoc + frame taint, P5a/P5a'"; both handlers were located and neither
        # touches a value: `_scope_dyn_exec` only withholds the `\in_scope` decided-FALSE
        # direction, and `exec_havoc … writes {int_mem}` exists only in the typed/store
        # memory model. The same docstring (and `_has_dynamic_exec`) assert that eval "does
        # not inject names" — false since 3.8's walrus. Measured, each PROVING what CPython
        # contradicts: module-scope `exec("N" + " = 5")` over a folded `N = 3`; `S = "N = 5";
        # exec(S)`; `exec("le" + "n = sum")` then `len([5]) == 1`; `exec("in" + "c = dec")`
        # over an imported `inc`; `exec("in" + "c = lambda y: y - 1")` over a module def;
        # `eval("(N := 5)")`; and, inside a function, `exec(code, globals())` and
        # `eval("(N := 5)", globals())`.
        # SCOPED TO WHERE THE BINDING REACHES THE MODULE NAMESPACE: assignments made by a
        # bare `exec`/`eval` go to the LOCALS mapping, which IS the module globals at module
        # and class-body scope and is a discarded snapshot inside a function. So a bare call
        # in a function body is left alone (corpus 0638/0639/0644 keep demonstrating the
        # `\in_scope` havoc and the frame taint); an explicit mapping argument is refused
        # anywhere. CENSUS: pycsl-reference 3 dynamic execs (0638 0639 0644, all bare and
        # in a function/method), python-reference 2 evals (0109 0217, constant, no walrus),
        # 53 mirrors 0, pycsl_lib 0.
        _nb_ns_builtins = frozenset(("exec", "eval", "setattr", "delattr", "globals",
                                     "vars", "locals", "getattr"))
        _nb_modexec_ids = {id(_nb_x) for _nb_x in _nb_mnodes}
        for _nb_x in ast.walk(python_ast):
            if not (isinstance(_nb_x, ast.Call) and isinstance(_nb_x.func, ast.Name)
                    and _nb_x.func.id in ("exec", "eval")):
                continue
            _nb_src = _nb_x.args[0] if _nb_x.args else None
            _nb_const = (isinstance(_nb_src, ast.Constant)
                         and isinstance(_nb_src.value, str))
            if _nb_x.func.id == "eval":
                # an `eval` BINDS through a walrus — and also through any namespace
                # builtin its expression reaches. The first cut keyed on `:=` alone and
                # was walked past by `eval("globals().update({'N': 5})")` and
                # `eval("exec('N = 5')")`, both of which PROVED `N == 3` (CPython 5).
                # A constant text naming none of them cannot rebind anything
                # (python-reference 0109/0217 are `eval("2 + 3")` — no identifiers).
                # (#138) ... AND THE TOKEN RULE IS STILL A SPELLING RULE. An eval text that
                # reaches the namespace WITHOUT naming one of the eight walks past it:
                # `eval("f.__globals__.__setitem__('N', 5)")` PROVED `f() == 3` (CPython 5).
                # A text can only bind or mutate through a CALL, an ATTRIBUTE, a SUBSCRIPT or
                # an `=`; a text with none of `( . [ =` is a closed arithmetic/literal
                # expression. The text is NOT parsed here on purpose — a `try/except
                # SyntaxError` in this method measurably added an `exception SyntaxError` to
                # two mirror emissions (see the constant-`exec` note above). CENSUS of the
                # eleven constant `eval`/`exec` texts over the five trees: the three that
                # PASS today are all `eval("2 + 3")` (1397, python-reference 0109 and 0217),
                # which contains none of the four characters; every other one already FAILS.
                # `exec` is deliberately NOT given this rule: a constant `exec` is SPLICED IN
                # AS REAL SOURCE by `splice_constant_exec` and is modelled (0642, 0643).
                _nb_binds = ((not _nb_const) or (":=" in _nb_src.value)
                             or any(_nb_ch in _nb_src.value for _nb_ch in "(.[=")
                             or bool(set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*",
                                                    _nb_src.value)) & _nb_ns_builtins))
            else:
                _nb_binds = not _nb_const
            if not _nb_binds:
                continue
            # (#138) the LOCATION gate is about where an ASSIGNMENT lands (the locals mapping,
            # which is a discarded snapshot inside a function). A text that MUTATES THROUGH A
            # CALL does not care: a bare in-function `eval("f.__globals__.__setitem__('N', 5)")`
            # reaches the real module globals and PROVED `f() == 3` (CPython 5). So a constant
            # text carrying a call, an attribute or a subscript is refused wherever it stands.
            # ... and a NON-CONSTANT text is unknown, so it reaches too: `S =
            # "f.__globals__.__setitem__('N', 5)"` with a bare in-function `eval(S)` PROVED
            # `f() == 3` (CPython 5) past the constant-text form of this widening. CENSUS of
            # dynamic `eval`: 0 in pycsl-reference, python-reference, the 53 mirrors and
            # `pycsl_lib`; 1 in `src/pycsl` (`module6_whyml/auto_trust.py:188`), whose mirror
            # method is `\trusted` and carries no body. `exec` keeps the location gate: its
            # constant form is spliced in as real source and its dynamic form is what 0638,
            # 0639, 0644 and 1397 exercise.
            _nb_reach = (_nb_x.func.id == "eval"
                         and ((not _nb_const)
                              or any(_nb_ch in _nb_src.value for _nb_ch in "(.[")))
            if (_nb_reach or len(_nb_x.args) > 1 or _nb_x.keywords
                    or id(_nb_x) in _nb_modexec_ids):
                _nb_bad.append(f"a dynamic `{_nb_x.func.id}` that can bind into the module "
                               f"namespace at line {getattr(_nb_x, 'lineno', 0)}")
        # (#136/#137, SECOND CUT — found by carrier-rerun on this block's own first cut)
        # EVERY RECOGNIZER THAT GUARDS THE NAMESPACE KEYS ON THE SPELLING OF A BUILTIN —
        # #118's namespace-dict rule, #119's `setattr`/`delattr` rule, #127's computed
        # `getattr`, the two arms just above. ONE ALIAS DEFEATS THEM ALL AT ONCE, and both
        # spellings PROVED against the first cut of this very block: `sa = setattr;
        # sa(plainlib, "inc", plainlib.dec)` (CPython 2) and `ex = exec; ex("N" + " = 5")`
        # (CPython 5). So a namespace-reaching builtin read ANYWHERE other than as the
        # CALLEE of a call is refused — keyed on the read, not on the twenty spellings of a
        # write. CENSUS over pycsl-reference, python-reference, the 53 mirrors, `pycsl_lib`
        # and `src/pycsl`: 0 sites. `__import__` is deliberately NOT in the list — no
        # recognizer keys on it and python-reference 0127 reads it as a value.
        _nb_callees = {id(_nb_x.func) for _nb_x in ast.walk(python_ast)
                       if isinstance(_nb_x, ast.Call) and isinstance(_nb_x.func, ast.Name)}
        _nb_imported: set = set()
        for _nb_x in ast.walk(python_ast):
            if isinstance(_nb_x, ast.Import):
                for _nb_a in _nb_x.names:
                    _nb_imported.add(_nb_a.asname or _nb_a.name.split(".")[0])
            elif isinstance(_nb_x, ast.ImportFrom):
                for _nb_a in _nb_x.names:
                    if _nb_a.name != "*":
                        _nb_imported.add(_nb_a.asname or _nb_a.name)
        for _nb_x in ast.walk(python_ast):
            if (isinstance(_nb_x, ast.Name) and isinstance(_nb_x.ctx, ast.Load)
                    and _nb_x.id in _nb_ns_builtins and id(_nb_x) not in _nb_callees):
                _nb_bad.append(f"the namespace builtin `{_nb_x.id}` read as a value at line "
                               f"{getattr(_nb_x, 'lineno', 0)}")
            # the same builtin reached as an ATTRIBUTE — `import builtins;
            # builtins.setattr(plainlib, "inc", plainlib.dec)` PROVED past the cut above,
            # and #127's `__builtins__` rules do not name the `builtins` MODULE. Census of
            # `.exec/.eval/.setattr/.delattr/.globals/.vars/.locals/.getattr` over the five
            # trees: 0 sites.
            elif isinstance(_nb_x, ast.Attribute) and _nb_x.attr in _nb_ns_builtins:
                _nb_bad.append(f"the namespace builtin `{_nb_x.attr}` reached as an "
                               f"attribute at line {getattr(_nb_x, 'lineno', 0)}")
            # ... and reached by a `getattr` ON A NAMESPACE OBJECT that is then CALLED:
            # `getattr(builtins, "set" + "attr")(plainlib, "inc", plainlib.dec)` names none
            # of the spellings above. #127 already refuses a computed `getattr` on the WRITE
            # side; this is its read side.
            # SCOPED TO A NAMESPACE RECEIVER — `__builtins__` or an IMPORTED name. The first
            # cut refused EVERY `getattr(...)(...)` on a census I read off a TRUNCATED
            # listing ("the 333 sites are all `_N(cls)(...)`"): the real count of
            # `getattr(obj, name)(...)` is 2 in the mirrors and 5 in `src/pycsl` — the
            # emitter's own `getattr(self, handler_name)(node)` dispatch — and the mirror
            # emission sweep caught it as FOUR GONE mirrors. A `self`/local receiver is not
            # a namespace and is untouched; census under the scoped rule: 0 live sites.
            elif (isinstance(_nb_x, ast.Call) and isinstance(_nb_x.func, ast.Call)
                    and isinstance(_nb_x.func.func, ast.Name)
                    and _nb_x.func.func.id == "getattr"
                    and _nb_x.func.args
                    and isinstance(_nb_x.func.args[0], ast.Name)
                    and (_nb_x.func.args[0].id == "__builtins__"
                         or _nb_x.func.args[0].id in _nb_imported)):
                _nb_bad.append(f"a `getattr` on a namespace object used as a callee at "
                               f"line {getattr(_nb_x, 'lineno', 0)}")
            # ... and the NAMESPACE DICT ITSELF, escaping into an arbitrary call. #118's
            # rule keys on a SUBSCRIPT STORE through it, so `operator.setitem(globals(),
            # "N", 5)` and `dict.update(globals(), N=5)` both PROVED `N == 3` (CPython 5)
            # past the cut above. A NO-ARGUMENT `globals()`/`vars()`/`locals()` IS the
            # module namespace; it may only be bound to a plain name (route #116's
            # `_g = globals()` idiom, itself fenced by #134) or read through a subscript.
            # `vars(self)` HAS an argument — an ordinary object's `__dict__`, not a
            # namespace — and is untouched. CENSUS of no-arg calls: 4 `_g = globals()`
            # (allowed) + 1326's `vars()["inc"] = dec` (already refused by #118) in
            # pycsl-reference, 1 `_g = globals()` in the mirrors, 0 in python-reference
            # and pycsl_lib.
            elif (isinstance(_nb_x, ast.Call) and isinstance(_nb_x.func, ast.Name)
                    and _nb_x.func.id in ("globals", "vars", "locals")
                    and not _nb_x.args and not _nb_x.keywords):
                _nb_p = _nb_parent.get(id(_nb_x))
                _nb_ok = False
                if (isinstance(_nb_p, (ast.Assign, ast.AnnAssign, ast.NamedExpr))
                        and _nb_p.value is _nb_x):
                    _nb_tg = (list(_nb_p.targets) if isinstance(_nb_p, ast.Assign)
                              else [_nb_p.target])
                    _nb_ok = all(isinstance(_nb_t, ast.Name) for _nb_t in _nb_tg)
                elif (isinstance(_nb_p, ast.Subscript) and _nb_p.value is _nb_x
                        and isinstance(_nb_p.ctx, ast.Load)):
                    _nb_ok = True
                if not _nb_ok:
                    _nb_bad.append(f"the module namespace dict `{_nb_x.func.id}()` used "
                                   f"outside a name binding or a subscript read at line "
                                   f"{getattr(_nb_x, 'lineno', 0)}")
        # (#138) THE SAME MAPPING, REACHED AS AN ATTRIBUTE. Gen #26's draft-9 gave the no-arg
        # `globals()`/`vars()`/`locals()` spelling an ESCAPE rule (it may only be bound to a
        # plain name or read through a subscript) and gave `f.__globals__["N"] = 5` a SINK rule
        # (the subscript store is keyed on the path). Neither covers the mapping FLOWING INTO A
        # CALL under the attribute spelling, and three shapes proved `f() == 3` while CPython
        # returned 5: `f.__globals__.__setitem__("N", 5)` (receiver), `dict.__setitem__(
        # f.__globals__, "N", 5)` and `operator.setitem(f.__globals__, "N", 5)` (argument — the
        # unbound-method spelling also makes the sink's receiver the name `dict`, which has no
        # module binding and so defaulted to FRESH). So the ESCAPE rule, not a sink rule, is the
        # one that generalizes: these four attributes ARE a namespace mapping wherever they
        # appear. CENSUS over the five trees: 2 sites (1402, 1403), both already expected-FAIL.
        # The bare NAME `__builtins__` is deliberately NOT given this rule — python-reference
        # 0127 passes `__builtins__` to `hasattr` and reads `__builtins__.__import__`, and it
        # PASSES today; #127's own rules already cover writing through it.
        _nb_ns_attrs = frozenset(("__globals__", "f_globals", "f_locals", "__dict__"))
        for _nb_x in ast.walk(python_ast):
            if not (isinstance(_nb_x, ast.Attribute) and _nb_x.attr in _nb_ns_attrs):
                continue
            _nb_p = _nb_parent.get(id(_nb_x))
            _nb_ok = False
            if (isinstance(_nb_p, (ast.Assign, ast.AnnAssign, ast.NamedExpr))
                    and _nb_p.value is _nb_x):
                _nb_tg = (list(_nb_p.targets) if isinstance(_nb_p, ast.Assign)
                          else [_nb_p.target])
                _nb_ok = all(isinstance(_nb_t, ast.Name) for _nb_t in _nb_tg)
            elif (isinstance(_nb_p, ast.Subscript) and _nb_p.value is _nb_x
                    and isinstance(_nb_p.ctx, ast.Load)):
                _nb_ok = True
            if not _nb_ok:
                _nb_bad.append(f"the namespace mapping `.{_nb_x.attr}` used outside a name "
                               f"binding or a subscript read at line "
                               f"{getattr(_nb_x, 'lineno', 0)}")
        # (#142) THE ONE ESCAPE BOTH RULES ALLOW — "it may be bound to a plain NAME" — HANDS OUT
        # AN UNGUARDED HANDLE ON THE NAMESPACE, and every sink in this block is keyed on the
        # spelling of the mapping, not on the name now holding it. Measured against the two
        # rules above: `_g = globals(); dict.update(_g, N=5)`, `_g = globals();
        # operator.setitem(_g, "N", 5)` and `_g = f.__globals__; dict.update(_g, N=5)` each
        # PROVED `f() == 3` while CPython returns 5 (the unbound-method spelling also makes the
        # module-scope sink's receiver the name `dict`, which has no module binding and is
        # FRESH). The allowance exists for route #116's `_g = globals()` idiom, whose ONLY use
        # is a subscript READ — so that is exactly what the name is now permitted to do.
        # CENSUS over the five trees of a name bound to a no-argument `globals()`/`vars()`/
        # `locals()` or to one of the four namespace attributes, USED anywhere other than a
        # subscript read: ONE site, 1322's `_g["inc"] = dec`, already an expected-FAIL witness.
        _nb_nsnames: set = set()
        for _nb_x in ast.walk(python_ast):
            if not isinstance(_nb_x, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                continue
            _nb_v = _nb_x.value
            if _nb_v is None:
                continue
            _nb_isns = ((isinstance(_nb_v, ast.Call) and isinstance(_nb_v.func, ast.Name)
                         and _nb_v.func.id in ("globals", "vars", "locals")
                         and not _nb_v.args and not _nb_v.keywords)
                        or (isinstance(_nb_v, ast.Attribute) and _nb_v.attr in _nb_ns_attrs))
            if not _nb_isns:
                continue
            for _nb_t in (list(_nb_x.targets) if isinstance(_nb_x, ast.Assign)
                          else [_nb_x.target]):
                if isinstance(_nb_t, ast.Name):
                    _nb_nsnames.add(_nb_t.id)
        if _nb_nsnames:
            for _nb_x in ast.walk(python_ast):
                if not (isinstance(_nb_x, ast.Name) and isinstance(_nb_x.ctx, ast.Load)
                        and _nb_x.id in _nb_nsnames):
                    continue
                _nb_p = _nb_parent.get(id(_nb_x))
                if not (isinstance(_nb_p, ast.Subscript) and _nb_p.value is _nb_x
                        and isinstance(_nb_p.ctx, ast.Load)):
                    _nb_bad.append(f"the name `{_nb_x.id}`, bound to the module namespace "
                                   f"mapping, used outside a subscript read at line "
                                   f"{getattr(_nb_x, 'lineno', 0)}")
        # NOT EXTENDED TO THE COMPUTED SPELLING: `getattr(f, "__globals__")["N"] = 5` and
        # `getattr(f, "__glo" + "bals__")["N"] = 5` were both probed and BOTH ARE REFUSED AT
        # HEAD (a Why3 typing failure on the subscript store through the accessor's result), so
        # a string-argument rule here would add refusal surface that closes nothing measured.
        # (#133) a def nested in a method, named like a method of that class or of an in-module
        # base (the lift emits it as that method).
        _nb_cls_by_name: Dict[str, Any] = {}
        for _nb_x in ast.walk(python_ast):
            if isinstance(_nb_x, ast.ClassDef):
                _nb_cls_by_name.setdefault(_nb_x.name, _nb_x)
        for _nb_x in ast.walk(python_ast):
            if not isinstance(_nb_x, ast.ClassDef):
                continue
            _nb_meths: set = set()
            _nb_todo: list = [_nb_x]
            _nb_seen: set = set()
            while _nb_todo:
                _nb_k = _nb_todo.pop()
                if id(_nb_k) in _nb_seen:
                    continue
                _nb_seen.add(id(_nb_k))
                _nb_meths |= {_nb_s.name for _nb_s in _nb_k.body
                              if isinstance(_nb_s, (ast.FunctionDef, ast.AsyncFunctionDef))}
                for _nb_b in _nb_k.bases:
                    if isinstance(_nb_b, ast.Name) and _nb_b.id in _nb_cls_by_name:
                        _nb_todo.append(_nb_cls_by_name[_nb_b.id])
            for _nb_m in _nb_x.body:
                if not isinstance(_nb_m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                _nb_q: list = list(_nb_m.body)
                while _nb_q:
                    _nb_z = _nb_q.pop()
                    if isinstance(_nb_z, ast.ClassDef):
                        continue
                    if isinstance(_nb_z, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
                            _nb_z.name in _nb_meths):
                        _nb_bad.append(f"`{_nb_z.name}` defined inside method "
                                       f"`{_nb_x.name}.{_nb_m.name}` at line {_nb_z.lineno}")
                    _nb_q.extend(ast.iter_child_nodes(_nb_z))
        if _nb_bad:
            raise PyCSLSemanticError(
                "a name's runtime value is not the one the model reads ("
                + "; ".join(sorted(set(_nb_bad))) + "). An imported name bound twice keeps the "
                "FIRST import (measured: `from plainlib import inc` then `from starlib import "
                "inc` proved the plainlib contract); a builtin rebound by an assignment is still "
                "lowered as the builtin (`len = sum` then `len([5]) == 1` proved); a module or "
                "class constant is folded to its first literal although it is rebound or mutated "
                "(`N = 3; N += 2` proved `N == 3`); a def nested in a method replaces the method "
                "of the same name; a DYNAMIC `exec`, or an `eval` that binds through a walrus, "
                "rebinds names into the module namespace and no part of the model sees the new "
                "value (`exec(\"N\" + \" = 5\")` proved `N == 3`); and an attribute written at "
                "module or class-body scope must have a receiver this file can describe — a "
                "lambda parameter, a comprehension target and an imported module are not "
                "(`(lambda m: setattr(m, \"inc\", other))(mod)` proved the original `inc`). "
                "Give each binding its own name, treat a folded constant as immutable, and "
                "keep a dynamic `exec`/`eval` out of module and class-body scope.")
        # (#49) ROUTE #120 — ATTRIBUTE-ACCESS HOOKS ARE NOT MODELLED. Every method call and field
        # store is resolved statically; a class-level hook that intercepts the lookup or the
        # store is never consulted. Measured at c01ef653, both PROVING what CPython contradicts:
        # a `__getattribute__` that redirects `m` to `n` (`C().m()` proved `\result == 1`,
        # Python 2), and a `__setattr__` that drops `a = 5` (`self.a = 5; return self.a` proved
        # `\result == 5`, Python 0). `__getattr__` is NOT refused: it runs only when normal
        # lookup FAILS, and an unmodelled attribute read is already an opaque fresh value.
        # CENSUS: `__getattribute__` 0 sites; `__setattr__` 1 (python-reference 0076,
        # expected-FAIL); `__delattr__` 0.
        for _hk_cls in ast.walk(python_ast):
            if isinstance(_hk_cls, ast.ClassDef):
                for _hk_st in _hk_cls.body:
                    # a hook INSTALLED BY ASSIGNMENT (`__getattribute__ = _redirect`) is the same
                    # hook; measured refused only by incidental Why3 errors before this.
                    _hk_names = ([_hk_st.name] if isinstance(_hk_st, (ast.FunctionDef,
                                                                     ast.AsyncFunctionDef))
                                 else [_hk_t.id for _hk_x in ([_hk_st.target] if isinstance(
                                           _hk_st, (ast.AnnAssign, ast.AugAssign)) else
                                           getattr(_hk_st, "targets", []) or [])
                                       for _hk_t in ast.walk(_hk_x) if isinstance(_hk_t, ast.Name)])
                    _hk_hit = [_hk_n for _hk_n in _hk_names
                               if _hk_n in ("__getattribute__", "__setattr__", "__delattr__",
                                            # (#49) ROUTE #128 — the DESCRIPTOR protocol is the
                                            # same hook on the attribute's class: `x = Seven()`
                                            # with `__get__ -> 7` made `C().x` read 7 while
                                            # `\result == 42` PROVED. Census: pyref 0078 only
                                            # (expected-FAIL).
                                            "__get__", "__set__", "__delete__", "__set_name__")]
                    if _hk_hit:
                        raise PyCSLSemanticError(
                            f"Class '{_hk_cls.name}' (line {_hk_cls.lineno}) defines "
                            f"`{_hk_hit[0]}`, an attribute-access hook the model does not "
                            f"consult: every method call and field store is resolved "
                            f"statically, so the hook would be silently ignored (measured: a "
                            f"`__getattribute__` redirecting `m` to `n` proved `m`'s contract; "
                            f"a `__setattr__` dropping a store proved the store happened). "
                            f"Attribute-access hooks are not modelled; remove the hook.")
        # (#34) A `#@` CONTRACT ON AN `async def` IS SILENTLY DISCARDED, AND THE RUN THEN
        # REPORTS "All contracts formally proven". Module 1 extracts an `AsyncFunctionDef`
        # under the SAME `FunctionDef` anchor as a plain `def`, so the contract IS parsed
        # and lands in `contracts_map` — but `PyCSLWeaver` has only `visit_FunctionDef`,
        # so the clauses are never attached, and Module 5's `visit_FunctionDef` never
        # fires either, so the whole coroutine is absent from the emitted WhyML. Measured
        # before this refusal:
        #     class C:
        #         #@ ensures \result == 1        <-- FALSE OF THE PROGRAM
        #         async def m(self) -> int:
        #             return 2
        # emitted a module with no `m` at all and printed
        # `[+] Verification SUCCESS! All contracts formally proven.`
        # Coroutines are not modelled (no suspension/resumption semantics), so the honest
        # answer is a refusal rather than a silent drop. Refused only when a contract was
        # actually extracted for the `async def`: an UNCONTRACTED coroutine claims nothing,
        # and refusing it would reject files whose async code is irrelevant to the proof
        # (11 such definitions live in `python-reference`, all nested, all uncontracted).
        for _n in ast.walk(python_ast):
            if isinstance(_n, ast.AsyncFunctionDef) and _n.lineno in contracts_map:
                raise PyCSLSemanticError(
                    f"Coroutine '{_n.name}' (line {_n.lineno}) carries a `#@` contract, "
                    f"but `async def` is NOT MODELLED: the weaver attaches contracts only "
                    f"to `FunctionDef`, and the IR emitter has no `AsyncFunctionDef` "
                    f"visitor, so both the contract and the whole coroutine body would be "
                    f"silently DROPPED while the run still reports 'All contracts formally "
                    f"proven'. Remove the contract, or make the function synchronous.")
        # (#49) ROUTES #122 (nested arm) + #126 — A NESTED `def` IS LIFTED TO A SIBLING OF ITS
        # ENCLOSING FUNCTION UNDER ITS OWN NAME, and two things the lift does not preserve were
        # measured PROVING what CPython contradicts:
        #   #122 two sibling functions each defining a helper `h` (+1 / -1) emit ONE `let h`
        #        (the textually last), and a nested def named like a MODULE function replaces it;
        #   #126 a name the nested def reads from its ENCLOSING function (a parameter, a local,
        #        a captured list it writes through) becomes ONE GLOBAL opaque `val constant`:
        #        `f(x): def h(): return x` made `f(1) - f(2) == 0` provable (Python -1).
        # Only the emitter knows whether the lifted body is ever lowered (a `\trusted` /
        # `\abstract` parent emits it as a bodyless `val`; converted mirror methods pair some
        # lifted walkers bespoke), so the facts are MARKED here and REFUSED in Module 6
        # `_emit_function`, next to the `nonlocal_writes` refusal of the same shape:
        #   `csl_lifted_collision`  the def is nested in a function and another non-method def
        #                           in the file has the same name;
        #   `csl_closure_captures`  the names it (or a lambda/comprehension inside it) reads that
        #                           are bound by an enclosing function and not by itself — the
        #                           enclosing functions' own nested def names excluded (they are
        #                           lifted beside it, under the collision rule).
        _lf_rows: list = []
        _lf_stack: list = [(_lf_n, [], "module") for _lf_n in python_ast.body]
        while _lf_stack:
            _lf_n, _lf_chain, _lf_scope = _lf_stack.pop()
            if isinstance(_lf_n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if _lf_scope != "class":
                    _lf_rows.append((_lf_n, _lf_chain))
                for _lf_c in ast.iter_child_nodes(_lf_n):
                    _lf_stack.append((_lf_c, _lf_chain + [_lf_n], "function"))
                continue
            if isinstance(_lf_n, ast.ClassDef):
                for _lf_c in _lf_n.body:
                    _lf_stack.append((_lf_c, _lf_chain, "class"))
                continue
            for _lf_c in ast.iter_child_nodes(_lf_n):
                _lf_stack.append((_lf_c, _lf_chain, _lf_scope))
        _lf_count: Dict[str, int] = {}
        for _lf_n, _lf_chain in _lf_rows:
            _lf_count[_lf_n.name] = _lf_count.get(_lf_n.name, 0) + 1
        # other bindings a lifted helper's name competes with: every import alias (file-wide),
        # every class name, and every module-scope assignment target (measured: a nested helper
        # `inc` replaced an IMPORTED `inc` for a sibling function, Python 2 vs proved 4).
        _lf_others: set = set()
        for _lf_x in ast.walk(python_ast):
            if isinstance(_lf_x, (ast.Import, ast.ImportFrom)):
                for _lf_al in _lf_x.names:
                    _lf_others.add((_lf_al.asname or _lf_al.name).split(".")[0])
            elif isinstance(_lf_x, ast.ClassDef):
                _lf_others.add(_lf_x.name)
        _lf_mq: list = list(python_ast.body)
        while _lf_mq:
            _lf_x = _lf_mq.pop()
            if isinstance(_lf_x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
                continue
            if isinstance(_lf_x, ast.Name) and not isinstance(_lf_x.ctx, ast.Load):
                _lf_others.add(_lf_x.id)
            _lf_mq.extend(ast.iter_child_nodes(_lf_x))
        for _lf_n, _lf_chain in _lf_rows:
            if not _lf_chain:
                continue
            if _lf_count.get(_lf_n.name, 0) > 1 or _lf_n.name in _lf_others:
                _lf_n.csl_lifted_collision = True
            # names bound by the nested def itself (params, stores, imports, defs, globals),
            # and names it loads (descending into lambdas/comprehensions, not nested defs).
            _lf_own: set = set()
            _lf_loads: set = set()
            _lf_fa = _lf_n.args
            for _lf_a in (list(getattr(_lf_fa, "posonlyargs", []) or []) + list(_lf_fa.args)
                          + list(_lf_fa.kwonlyargs)
                          + [x for x in (_lf_fa.vararg, _lf_fa.kwarg) if x is not None]):
                _lf_own.add(_lf_a.arg)
            _lf_q: list = list(_lf_n.body)
            while _lf_q:
                _lf_y = _lf_q.pop()
                if isinstance(_lf_y, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    _lf_own.add(_lf_y.name)
                    continue
                if isinstance(_lf_y, ast.Lambda):
                    for _lf_a in _lf_y.args.args:
                        _lf_own.add(_lf_a.arg)
                if isinstance(_lf_y, ast.Name):
                    if isinstance(_lf_y.ctx, ast.Load):
                        _lf_loads.add(_lf_y.id)
                    else:
                        _lf_own.add(_lf_y.id)
                elif isinstance(_lf_y, (ast.Import, ast.ImportFrom)):
                    for _lf_al in _lf_y.names:
                        _lf_own.add((_lf_al.asname or _lf_al.name).split(".")[0])
                elif isinstance(_lf_y, ast.Global):
                    _lf_own.update(_lf_y.names)
                elif isinstance(_lf_y, ast.ExceptHandler) and isinstance(_lf_y.name, str):
                    _lf_own.add(_lf_y.name)
                _lf_q.extend(ast.iter_child_nodes(_lf_y))
            _lf_encl: set = set()
            _lf_encl_defs: set = set()
            for _lf_f in _lf_chain:
                _lf_ga = _lf_f.args
                for _lf_a in (list(getattr(_lf_ga, "posonlyargs", []) or []) + list(_lf_ga.args)
                              + list(_lf_ga.kwonlyargs)
                              + [x for x in (_lf_ga.vararg, _lf_ga.kwarg) if x is not None]):
                    _lf_encl.add(_lf_a.arg)
                _lf_globals: set = set()
                _lf_q2: list = list(_lf_f.body)
                while _lf_q2:
                    _lf_z = _lf_q2.pop()
                    if isinstance(_lf_z, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        _lf_encl_defs.add(_lf_z.name)
                        continue
                    if isinstance(_lf_z, (ast.ClassDef, ast.Lambda)):
                        continue
                    if isinstance(_lf_z, ast.Name) and not isinstance(_lf_z.ctx, ast.Load):
                        _lf_encl.add(_lf_z.id)
                    elif isinstance(_lf_z, (ast.Import, ast.ImportFrom)):
                        for _lf_al in _lf_z.names:
                            _lf_encl.add((_lf_al.asname or _lf_al.name).split(".")[0])
                    elif isinstance(_lf_z, ast.Global):
                        _lf_globals.update(_lf_z.names)
                    elif isinstance(_lf_z, ast.ExceptHandler) and isinstance(_lf_z.name, str):
                        _lf_encl.add(_lf_z.name)
                    _lf_q2.extend(ast.iter_child_nodes(_lf_z))
                _lf_encl -= _lf_globals
            # inside a METHOD the lifted def is itself emitted as a method of the class, so
            # `self` is its own parameter, not a capture.
            _lf_root_args = _lf_chain[0].args.args if _lf_chain else []
            if _lf_root_args and _lf_root_args[0].arg == "self":
                _lf_own.add("self")
            _lf_caps = sorted((_lf_loads - _lf_own) & (_lf_encl - _lf_encl_defs))
            if _lf_caps:
                _lf_n.csl_closure_captures = _lf_caps
        PyCSLWeaver(contracts_map).visit(python_ast)
        python_ast.csl_happy_properties = happy_props
        self._consolidate_module_concurrency(python_ast, contracts_map)
        self._attach_labels_and_ghost_assigns(python_ast, contracts_map, trailing_contracts_map)
        self._expand_happy_properties(python_ast, happy_props)
        return python_ast
