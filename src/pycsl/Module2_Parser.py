from __future__ import annotations

from dataclasses import dataclass
from typing import List, Union, Any, Optional
from lark import Lark, Transformer, v_args
from lark.exceptions import LarkError
from errors import PyCSLParseError

# ---------------------------------------------------------
# 1. Contract AST Nodes (The Internal Representation)
# ---------------------------------------------------------

@dataclass
class CSLNode:
    pass

class ContractWrapper(CSLNode): pass   # Requires, Ensures, LoopInvariant, LoopVariant
class QuantifierNode(CSLNode): pass    # Forall, Exists
class SingleExprNode(CSLNode): pass    # UnaryOp, Old

@dataclass
class Requires(ContractWrapper):
    expr: CSLNode

@dataclass
class Ensures(ContractWrapper):
    expr: CSLNode

@dataclass
class Assigns(CSLNode):
    targets: List[CSLNode]

@dataclass
class Given(CSLNode):
    """An `act`'s guard clause (`given <expr>`). ACSL `assumes`, pre-state."""
    expr: CSLNode

@dataclass
class Act(CSLNode):
    """A named guarded case: `act NAME:` with body clauses (Given/Requires/
    Ensures/Assigns). Desugared in Module3 to ordinary requires/ensures."""
    name: str
    clauses: List[CSLNode]

@dataclass
class Complete(CSLNode):
    """`complete b1, b2, …` — the acts' guards cover every input."""
    names: List[str]

@dataclass
class Disjoint(CSLNode):
    """`disjoint b1, b2, …` — at most one act's guard holds at a time."""
    names: List[str]

@dataclass
class Preserves(CSLNode):
    """`#@ \\preserves` on a `\\trusted`/`\\abstract` method — opts the function into
    the HAPPY trust boundary (meta.md Stage B, option C). The meta-pass synthesizes
    and attaches the canonical region-preservation `ensures` for every module HAPPY
    over a field this function does not legitimately write, so callers may assume the
    region is untouched. A non-exempt trusted/abstract function WITHOUT this marker is
    a hard error (theorem clause 2 has teeth)."""
    pass

@dataclass
class HappyProperty(CSLNode):
    """A module-level HAPPY (High-level Assertion-Producing PYthon requirement):
    `#@ happy NAME: region LO .. HI writes self.FIELD outside region except f, g`.
    Declares one cross-cutting region-disjointness property; Module3's meta-pass
    expands it into a per-site `#@ check` (a `CheckPoint`) at every write site of
    `self.FIELD` in every method other than the exempt set. Desugars entirely to
    the Stage-A check primitive — no new IR/backend. See `meta.md` Stage B."""
    name: str
    field: str            # the shared instance field, e.g. "disk" (target = self.<field>)
    region_lo: CSLNode    # region lower bound (inclusive); None for the `protects` form
    region_hi: CSLNode    # region upper bound (exclusive); None for the `protects` form
    except_set: List[str] # method names allowed to write the region (the legitimate writers)
    context: str = "writing"
    # 07-1143 R1/R2: the subsystem-ownership form. When non-None, this HAPPY forbids
    # ANY direct write to any of these (possibly dotted, e.g. `world.fs.disk`) protected
    # paths by a non-exempt method — the per-site check is `False` (forbidden outright),
    # there is no region. `field`/`region_*` are unused in this form.
    protects: Optional[List[str]] = None

@dataclass
class LoopInvariant(ContractWrapper):
    expr: CSLNode

@dataclass
class LoopVariant(ContractWrapper):
    expr: CSLNode

@dataclass
class BinOp(CSLNode):
    left: CSLNode
    op: str
    right: CSLNode

@dataclass
class UnaryOp(SingleExprNode):
    op: str
    expr: CSLNode

@dataclass
class Var(CSLNode):
    name: str

@dataclass
class Number(CSLNode):
    value: float

@dataclass
class StringLiteral(CSLNode):
    value: str

@dataclass
class Result(CSLNode):
    pass

@dataclass
class Old(SingleExprNode):
    expr: CSLNode

@dataclass
class Nothing(CSLNode):
    pass

@dataclass
class FieldAccess(CSLNode):
    object: str   # "self"
    field: str

@dataclass
class FieldSubscript(CSLNode):
    """Represents `self.<field>[i]` — subscript of an instance ARRAY field in a
    contract. Enables region-preservation postconditions such as
    `\\forall i; (lo <= i and i < hi) ==> self.disk[i] == \\old(self.disk[i])`
    on a `\\trusted`/`\\abstract` writer (meta.md Stage B, option C)."""
    field: str       # the field name (no "self." prefix), e.g. "disk"
    index: CSLNode

@dataclass
class ClassInvariant(CSLNode):
    expr: CSLNode

@dataclass
class SubscriptAccess(CSLNode):
    array: str
    index: CSLNode

@dataclass
class Forall(QuantifierNode):
    var: str
    body: CSLNode
    # quantification.md: typed/bounded binder. `binder_type=None` ⇒ legacy int
    # path (emits `forall var : int.` verbatim → byte-identical). `domain` is the
    # `in S` bounded term (P3), else None.
    binder_type: Optional[str] = None
    domain: Optional[CSLNode] = None

@dataclass
class Exists(QuantifierNode):
    var: str
    body: CSLNode
    binder_type: Optional[str] = None
    domain: Optional[CSLNode] = None

@dataclass
class ArrayLength(CSLNode):
    var: str

@dataclass
class AssignsRegion(CSLNode):
    """Represents `arr[lo..hi]` inside an assigns clause (frame condition region)."""
    base: str       # array parameter name
    low: CSLNode    # lower bound expression (inclusive)
    high: CSLNode   # upper bound expression (exclusive)

@dataclass
class Valid(CSLNode):
    """Represents `\\valid(arr, n)` — memory region [arr, arr+n) is allocated."""
    base: str
    length: CSLNode

@dataclass
class Separated(CSLNode):
    """Represents `\\separated(a, na, b, nb)` — regions [a,a+na) and [b,b+nb) don't overlap."""
    base1: str
    length1: CSLNode
    base2: str
    length2: CSLNode

@dataclass
class Label(CSLNode):
    """Represents a `#@ label L` program point annotation."""
    name: str

@dataclass
class CheckPoint(CSLNode):
    """A statement-level proof obligation attached to the following statement:
    `#@ assert P` (prove-and-assume — P becomes a hypothesis afterward) or
    `#@ check P` (prove-and-discard). Distinct from the Python `assert` statement,
    which is a runtime check the prover ignores."""
    kind: str        # "assert" | "check"
    expr: CSLNode
    origin: str = None   # attribution for synthesized obligations (e.g. a HAPPY); None when hand-written

@dataclass
class At(CSLNode):
    """Represents `\\at(expr, L)` — value of expr at program point L."""
    expr: CSLNode
    label: str

@dataclass
class Length2D(CSLNode):
    """Represents `\\length2d(arr, m, n)` — arr has m rows each of length n."""
    base: str
    rows: CSLNode
    cols: CSLNode

@dataclass
class Valid2D(CSLNode):
    """Represents `\\valid2d(arr, i, j)` — (i,j) is a valid 2D index into arr."""
    base: str
    row: CSLNode
    col: CSLNode

@dataclass
class FunctionVariant(CSLNode):
    """Represents `#@ \\variant <expr>` or `#@ \\variant (<expr>, <ordering>)`."""
    expr: CSLNode
    ordering: Optional[str] = None   # None → integer, str → named well-founded relation

@dataclass
class Diverges(CSLNode):
    """Represents `#@ \\diverges` — function may not terminate."""
    pass

@dataclass
class Trusted(CSLNode):
    """Represents `#@ \\trusted` — function body is not verified.
    Optional `reviewer` identifies who is accountable for the trust assumption."""
    reviewer: str = ""

@dataclass
class Abstract(CSLNode):
    """Represents `#@ \\abstract` — the function is emitted as a bodyless WhyML
    `val` defined SOLELY by its contract (+ any cited `#@ proof` axioms). Unlike
    `\\trusted` (a Python body that is present but unchecked), an `\\abstract`
    declaration asserts there is no meaningful body to check — the contract IS
    the definition. Sound: an uninterpreted `val` constrains callers only by its
    spec. Used for irreducibly-opaque operations (e.g. `ast.literal_eval`, which
    IS Python's parser) where the honest model is `val + ensures/raises + cited
    axiom`, not an unverified body. Does NOT count as `\\trusted`."""

@dataclass
class Lemma(CSLNode):
    """Represents `#@ lemma` (lemma.md) — the function is a PROVED logical fact.
    It lowers to a WhyML `let [rec] lemma name (params) : unit requires {H}
    ensures {C} [variant {m}] = <proof body>`: Why3 verifies the body against the
    contract, then makes `forall params. H -> C` available to later goals. Unlike
    `\\trusted` (assumed) and `#@ proof` (proved elsewhere, an axiom), a lemma
    introduces NO axiom that isn't itself checked. A recursive lemma's self-calls
    are the induction hypotheses; it MUST carry `#@ \\variant` (soundness)."""

@dataclass
class Uses(CSLNode):
    """Represents `#@ uses <lemma>` (scc2.md) — a NON-instantiating citation that the
    function's verification relies on lemma `<lemma>`'s general fact. Its only effect
    is an ordering edge (the cited lemma is emitted before this function, so its
    `forall …` fact is in scope to discharge e.g. a `\\forall`-over-a-recursive-
    datatype goal). It emits no WhyML of its own; it is consumed by the SCC edge
    collector (`scc.py`)."""
    lemma: str

@dataclass
class CSLBool(CSLNode):
    """Represents True/False literals in contract expressions."""
    value: bool

@dataclass
class CSLNone(CSLNode):
    """Represents None literal in contract expressions."""
    pass

@dataclass
class CSLIn(CSLNode):
    """Represents `x in arr` membership test in contracts."""
    element: CSLNode
    collection: CSLNode

@dataclass
class CSLNotIn(CSLNode):
    """Represents `x not in arr` negated membership test in contracts."""
    element: CSLNode
    collection: CSLNode

@dataclass
class CSLSlice(CSLNode):
    """Represents `arr[lo:hi]` slice notation in contracts."""
    collection: str
    low: CSLNode
    high: CSLNode

@dataclass
class ChainedSubscript(CSLNode):
    """Represents `arr[i][j]` chained subscript access (2D array element)."""
    array: str
    index1: CSLNode
    index2: CSLNode

@dataclass
class CallExpr(CSLNode):
    """Represents a function call in a contract expression."""
    func: str
    args: List[CSLNode]

@dataclass
class IsSorted(CSLNode):
    """Represents `\\is_sorted(a, lo, hi)` — array is sorted in range."""
    base: str
    lo: CSLNode
    hi: CSLNode

@dataclass
class ArrayEq(CSLNode):
    """Represents `\\array_eq(a, b)` — two arrays have equal length and
    equal elements at every index (extensional content equality)."""
    left: CSLNode
    right: CSLNode

@dataclass
class Permutation(CSLNode):
    """Represents `\\permutation(a, b)` — `a` is a permutation of `b` (same
    multiset of elements). Unlike `\\array_eq` it does NOT unfold to a
    first-order formula; it lowers to an uninterpreted Why3 `predicate permut`
    that a proof-assistant-imported axiom constrains (no-more-int A2b Gap 1)."""
    left: CSLNode
    right: CSLNode

@dataclass
class Sum(CSLNode):
    """Represents `\\sum(a, lo, hi)` — sum of array elements in range."""
    base: str
    lo: CSLNode
    hi: CSLNode

@dataclass
class GhostAssignDecl(CSLNode):
    """Represents `ghost var = expr` or `ghost var += expr` in contracts."""
    target: str
    value: CSLNode
    op: str           # "=" or "+=" or "-=" or "*="
    declared_type: str = "int"   # "int" | "string" | "array" | "list" |
                                  # "tuple2" | "tuple3" | "tuple4" |
                                  # "dict" | "set"

# --- Ghost tuple nodes ---

@dataclass
class MkTupleExpr(CSLNode):
    """\\mktuple(a, b[, c[, d]]) — construct a ghost tuple."""
    elts: List[CSLNode]

@dataclass
class FstExpr(CSLNode):
    """\\fst(t) — first component of a ghost tuple."""
    tuple_expr: CSLNode

@dataclass
class SndExpr(CSLNode):
    """\\snd(t) — second component of a ghost tuple."""
    tuple_expr: CSLNode

@dataclass
class ProjExpr(CSLNode):
    """\\proj(t, i) — ith component of a ghost tuple (i must be a literal)."""
    tuple_expr: CSLNode
    index: CSLNode

@dataclass
class CtorTest(CSLNode):
    """\\is_ctor(x, Ctor) — true iff `x` was built with constructor `Ctor`
    (A5b: a datatype discriminator usable in a contract)."""
    var: str
    ctor: str

@dataclass
class CtorPayload(CSLNode):
    """\\payload(x, Ctor[, i]) — the i-th payload of `x` viewed as constructor
    `Ctor` (A5b: a datatype projector usable in a contract; `i` defaults to 0)."""
    var: str
    ctor: str
    index: int = 0

# --- Ghost string nodes ---

@dataclass
class StrConcatExpr(CSLNode):
    """s ^ t — string concatenation in ghost / contract context."""
    left: CSLNode
    right: CSLNode

@dataclass
class StrLengthExpr(CSLNode):
    r"""\str_length(s) — length of a ghost string variable."""
    string: CSLNode

@dataclass
class StrSubExpr(CSLNode):
    r"""\str_sub(s, lo, hi) — substring of ghost string s from lo to hi."""
    string: CSLNode
    lo: CSLNode
    hi: CSLNode

# --- Ghost array nodes ---

@dataclass
class GhostCopyExpr(CSLNode):
    """\\copy(arr) — snapshot of an array into a ghost array."""
    arr: str   # CNAME of the source array

@dataclass
class GhostCopyRangeExpr(CSLNode):
    """\\copy_range(arr, lo, hi) — bounded snapshot: arr[lo..hi-1] into a new ghost array."""
    arr: str       # CNAME of the source array
    lo: CSLNode    # lower bound (inclusive)
    hi: CSLNode    # upper bound (exclusive)

@dataclass
class GhostMakeExpr(CSLNode):
    """\\make(n, v) — create a ghost array of length n filled with v."""
    size: CSLNode
    default: CSLNode

# --- Ghost dict nodes ---

@dataclass
class MapEmptyExpr(CSLNode):
    """\\empty_map — an empty ghost dictionary (total map defaulting to 0)."""
    pass

@dataclass
class MapGetExpr(CSLNode):
    """\\map_get(d, k) — look up key k in ghost dict d."""
    dict_expr: CSLNode
    key: CSLNode

@dataclass
class MapSetExpr(CSLNode):
    """\\map_set(d, k, v) — return ghost dict d with d[k] := v."""
    dict_expr: CSLNode
    key: CSLNode
    value: CSLNode

@dataclass
class MapEqExpr(CSLNode):
    """\\map_eq(d1, d2) — extensional equality of two ghost dicts."""
    left: CSLNode
    right: CSLNode

@dataclass
class HasKeyExpr(CSLNode):
    """\\has_key(d, k) — true iff ghost dict d has a present (non-None) value at key k."""
    dict_expr: CSLNode
    key: CSLNode

@dataclass
class MapRemoveExpr(CSLNode):
    """\\map_remove(d, k) — return ghost dict d with key k removed (set to None/absent)."""
    dict_expr: CSLNode
    key: CSLNode

# --- Ghost set nodes ---

@dataclass
class SetEmptyExpr(CSLNode):
    """\\set_empty — the empty ghost set."""
    pass

@dataclass
class SetAddExpr(CSLNode):
    """\\set_add(s, x) — ghost set with x added."""
    set_expr: CSLNode
    elem: CSLNode

@dataclass
class SetRemoveExpr(CSLNode):
    """\\set_remove(s, x) — ghost set with x removed."""
    set_expr: CSLNode
    elem: CSLNode

@dataclass
class SetMemExpr(CSLNode):
    """\\set_mem(x, s) — x is a member of ghost set s."""
    elem: CSLNode
    set_expr: CSLNode

@dataclass
class SetUnionExpr(CSLNode):
    """\\set_union(s1, s2) — union of two ghost sets."""
    left: CSLNode
    right: CSLNode

@dataclass
class SetInterExpr(CSLNode):
    """\\set_inter(s1, s2) — intersection of two ghost sets."""
    left: CSLNode
    right: CSLNode

@dataclass
class SetDiffExpr(CSLNode):
    """\\set_diff(s1, s2) — set difference s1 \\ s2."""
    left: CSLNode
    right: CSLNode

@dataclass
class SetCardExpr(CSLNode):
    """\\set_card(s, lo, hi) — cardinality of s restricted to [lo, hi)."""
    set_expr: CSLNode
    lo: CSLNode
    hi: CSLNode

@dataclass
class SetSubsetExpr(CSLNode):
    """\\set_subset(s1, s2) — s1 is a subset of s2."""
    left: CSLNode
    right: CSLNode

@dataclass
class SetEqExpr(CSLNode):
    """\\set_eq(s1, s2) — extensional equality of two ghost sets."""
    left: CSLNode
    right: CSLNode

# --- Ghost list nodes ---

@dataclass
class NilExpr(CSLNode):
    """\\nil — the empty ghost list."""
    pass

@dataclass
class ConsExpr(CSLNode):
    """\\cons(x, l) — prepend x to ghost list l."""
    head: CSLNode
    tail: CSLNode

@dataclass
class HdExpr(CSLNode):
    """\\hd(l) — head of ghost list l (requires l non-empty)."""
    list_expr: CSLNode

@dataclass
class TlExpr(CSLNode):
    """\\tl(l) — tail of ghost list l (requires l non-empty)."""
    list_expr: CSLNode

@dataclass
class ListLengthExpr(CSLNode):
    """\\list_length(l) — length of ghost list l."""
    list_expr: CSLNode

@dataclass
class NthExpr(CSLNode):
    """\\nth(l, i) — ith element of ghost list l (requires 0 <= i < length)."""
    list_expr: CSLNode
    index: CSLNode

@dataclass
class MemExpr(CSLNode):
    """\\mem(x, l) — x appears in ghost list l."""
    elem: CSLNode
    list_expr: CSLNode

@dataclass
class AppendExpr(CSLNode):
    """\\append(l1, l2) — concatenation of two ghost lists."""
    left: CSLNode
    right: CSLNode

@dataclass
class GhostArraySetDecl(CSLNode):
    """ghost arr[i] = expr — in-place assignment to a ghost array element."""
    target: str
    index: CSLNode
    value: CSLNode

@dataclass
class RaisesDecl(CSLNode):
    """Represents `raises ExcType when condition` in contracts."""
    exc_type: str
    condition: CSLNode

@dataclass
class NoExceptionDecl(CSLNode):
    """Represents `no_exception E1, E2, ...` or `no_exception \\all`.

    Turns implicit Python exceptions into proof obligations: every IR
    operation that could raise one of `exceptions` must be preceded by an
    assertion discharging its trigger condition (see exception_model.py).

    `all_form=True` is the wildcard form; `exceptions` is empty in that case
    and the function context expands to the full Phase 1 exception set at
    transpilation time.
    """
    exceptions: List[str]
    all_form: bool = False

@dataclass
class AllowFinalizerDecl(CSLNode):
    """Represents `#@ allow_finalizer` — opts a class with `__del__` out
    of UB-7.5's hard rejection. Place on the `class` line.
    """
    pass

@dataclass
class AllowIterationMutationDecl(CSLNode):
    """Represents `#@ allow_iteration_mutation` — opts a `for` loop out
    of UB-7.1's hard rejection. Place on the `for` line.
    """
    pass

@dataclass
class BoundedIntDecl(CSLNode):
    """Represents `assumes bounded_int(N)` in contracts."""
    size: int

@dataclass
class ProofDecl(CSLNode):
    """Represents `#@ proof <prover> <qualname>` — cites a Rocq or
    Lean theorem as the justification for a Why3 axiom in the WhyML
    preamble.

    Emits an `axiom <name> : <body>` line in the transpiled WhyML.
    The body is looked up from a per-test manifest or hand-curated
    mapping during the MVP phase, and from `proof2why3` extraction
    once that pipeline exists (see docs/cross-validated-spec-sources.md).
    """
    prover: str    # "rocq" | "lean"
    qualname: str  # the pycsl_target string


# --- Concurrency annotation nodes ---

@dataclass
class SharedDecl(CSLNode):
    """Represents `shared VAR protected_by MUTEX` or `shared VAR` (unprotected)."""
    variable: str
    mutex: Optional[str] = None

@dataclass
class DatatypeDecl(CSLNode):
    """Represents `#@ datatype Name = C1 | C2(int) | C3(int, int)` — an algebraic
    (sum) type. `variants` is a list of (constructor_name, [payload_type_names]).
    `type_params` (A5d) holds the declared type parameters of a *parametric*
    datatype `#@ datatype Option[T] = …`; empty for a monomorphic one."""
    name: str
    variants: list
    type_params: list = None

@dataclass
class InductiveDecl(CSLNode):
    """Represents an `#@ inductive p(params):` least-fixpoint relation (inductive.md).
    `signature` is the rendered param string `"(n: int)"`; `rules` is a list of
    `(rule_name, horn_clause_expr)` parsed inline from the indentation block. `members`
    (inductive.md P2) holds any `with q(params): …` mutually-inductive group members as
    `(name, signature, rules)` tuples. Lowers to a Why3 `inductive p (params) = | Rule :
    clause … [with q … = | …]` (no closing `end`)."""
    name: str
    signature: str
    rules: list = None
    members: list = None

# --- Mixin composition nodes (mixin.md / mixin-ready.md, Tier 1) ---
# S0 surface: these parse and attach to their class/method node; Module3 weaves
# them onto `csl_*` fields (S0), and the Module4 composition pass (S2) consumes
# them. Downstream stages that don't yet recognise them ignore them silently.

@dataclass
class MixinDecl(CSLNode):
    """Represents `#@ mixin` — marks a class as a composable mixin (a trait whose
    provided methods are verified once against its declared dependencies, then
    flattened into a composer via `#@ compose_from`)."""
    pass

@dataclass
class ProvidesDecl(CSLNode):
    """Represents `#@ provides <m>` — the following method is a provided operation
    of this mixin (a candidate provider for a sibling's `depends_method`)."""
    method: str

@dataclass
class SharedStateDecl(CSLNode):
    """Represents `#@ shared_state <name>: <type>` (D1) — a field declared as
    deliberately-shared facade state. Multiple mixins may read/write it; it is NOT
    an owned-field conflict. A write must still appear in the method's `assigns`."""
    name: str
    type_str: str

@dataclass
class TouchesFieldDecl(CSLNode):
    """Represents `#@ touches_field <name>: <type>` — an OWNED field of this mixin.
    At most one mixin may own a given name (two owners → conflict → Tier 2)."""
    name: str
    type_str: str

@dataclass
class MethodDependencyDecl(CSLNode):
    """Represents `#@ depends_method <m>: <sig>` (D2, a CONCRETE dependency on a
    sibling/core provider) or `#@ requires_method <m>: <sig>` (an ABSTRACT operation
    the composing class must supply). Both are modelled as an abstract `val` against
    which the mixin is verified once; composition discharges provider ⊑ declared."""
    method: str
    sig: str          # rendered signature string, e.g. "(self, x: int) -> int"
    kind: str         # "depends" | "requires"

@dataclass
class ComposeFromDecl(CSLNode):
    """Represents `#@ compose_from M1, M2, …` — marks a class as composing the named
    mixins. Synthesizes the composition obligations (unique provider per dependency,
    provider-refines-dependency, init-hook) checked by the Module4 pass (S2)."""
    mixins: list

@dataclass
class ThreadEntry(CSLNode):
    """Represents `thread_entry` — marks a function as a concurrent thread entry point."""
    pass

@dataclass
class Acquires(CSLNode):
    """Represents `acquires MUTEX` — marks a mutex acquire point."""
    mutex: str

@dataclass
class Releases(CSLNode):
    """Represents `releases MUTEX` — marks a mutex release point."""
    mutex: str

@dataclass
class CriticalSection(CSLNode):
    """Represents `critical MUTEX` — marks a `with` block as a critical section."""
    mutex: str

@dataclass
class MutexInvariant(CSLNode):
    """Represents `mutex_invariant MUTEX: EXPR` — invariant held when mutex is unlocked."""
    mutex: str
    expr: CSLNode

@dataclass
class LockOrder(CSLNode):
    """Represents `lock_order M1, M2, ...` — total order on mutex acquisition to prevent deadlock."""
    order: List[str]

# ---------------------------------------------------------
# 2. The EBNF Grammar
# ---------------------------------------------------------

PYCSL_GRAMMAR = r"""
    ?start: contract

    ?contract: precondition
             | postcondition
             | assigns
             | loop_invariant
             | loop_variant
             | class_invariant
             | label_decl
             | assert_decl
             | check_decl
             | function_variant
             | function_variant_structural
             | diverges_decl
             | trusted_decl
             | abstract_decl
             | lemma_decl
             | uses_decl
             | preserves_decl
             | ghost_assign
             | ghost_aug_assign
             | ghost_array_set
             | raises_decl
             | no_exception_decl
             | allow_finalizer_decl
             | allow_iteration_mutation_decl
             | bounded_int_decl
             | proof_decl
             | datatype_decl
             | inductive_decl
             | mixin_decl
             | provides_decl
             | shared_state_decl
             | touches_field_decl
             | depends_method_decl
             | requires_method_decl
             | compose_from_decl
             | shared_decl
             | thread_entry_decl
             | acquires_decl
             | releases_decl
             | critical_decl
             | mutex_invariant_decl
             | lock_order_decl
             | act_block
             | complete_decl
             | disjoint_decl
             | happy_decl
             | happy_protects_decl

    precondition: "requires" expr
    postcondition: "ensures" expr

    // Guarded contract cases (Module1 folds each `act NAME:` block into one
    // contract string; clauses are keyword-delimited so no indentation here).
    act_block: "act" CNAME ":" act_clause+
    ?act_clause: given_clause | precondition | postcondition | assigns
    given_clause: "given" expr
    complete_decl: "complete" act_names
    disjoint_decl: "disjoint" act_names
    act_names: CNAME ("," CNAME)*

    // Module-level HAPPY meta-property (Module1 folds the `happy NAME:` block into
    // one contract string; clauses are keyword-delimited). v1 surface: a region
    // [LO, HI) that a named shared field must not be written into, except by an
    // allowlisted set of methods. See `meta.md` Stage B and `Module3._expand_happy_properties`.
    happy_decl: "happy" CNAME ":" "region" expr RANGE_OP expr "writes" "self" "." CNAME "outside" "region" ("except" act_names)?

    // 07-1143 R1/R2: subsystem ownership form — no method outside `except` may directly
    // write ANY of the (possibly dotted/nested) protected fields. Desugars to a per-site
    // `#@ check False` at every direct write of a protected path in a non-exempt method.
    happy_protects_decl: "happy" CNAME ":" "protects" dotted_path_list ("except" act_names)?
    dotted_path_list: dotted_path ("," dotted_path)*
    dotted_path: CNAME ("." CNAME)*

    // Extracted alias from group to prevent Lark GrammarError
    assigns: "assigns" assigns_target
    ?assigns_target: assigns_region_list
                   | expr_list 
                   | "\\nothing" -> nothing

    assigns_region_list: assigns_region ("," assigns_region)*
    assigns_region: CNAME "[" expr RANGE_OP expr "]"

    loop_invariant: "loop" "invariant" expr
    loop_variant: "loop" "variant" expr
    class_invariant: "class" "invariant" expr
    label_decl: "label" CNAME
    assert_decl: "assert" expr
    check_decl: "check" expr
    function_variant: "\\variant" expr
    function_variant_structural: "\\variant" "(" expr "," CNAME ")"
    diverges_decl: "\\diverges"
    trusted_decl: "\\trusted" ("reviewer" ":" REVIEWER_ID)?
    abstract_decl: "\\abstract"
    lemma_decl: "lemma"
    uses_decl: "uses" CNAME
    preserves_decl: "\\preserves"
    REVIEWER_ID: /[A-Za-z0-9._@-]+/
    ghost_assign: "ghost" CNAME ":" GHOST_TYPE "=" expr -> ghost_assign_typed
              | "ghost" CNAME "=" expr -> ghost_assign_untyped
    ghost_aug_assign: "ghost" CNAME GHOST_AUG_OP expr
    ghost_array_set: "ghost" CNAME "[" expr "]" "=" expr
    raises_decl: "raises" CNAME "when" expr

    // no_exception — implicit exceptions become proof obligations
    // (see config/skills/pycsl-exception-model). The bare-name form lists
    // specific exceptions; the `\all` form expands at transpilation to the
    // full Phase 1 set and requires the function's raises set to be empty.
    no_exception_decl: "no_exception" "\\all" -> no_exception_all_decl
                     | "no_exception" exception_name_list -> no_exception_list_decl
    exception_name_list: CNAME ("," CNAME)*

    // UB-7.5 — opt-in to `__del__` despite the default rejection
    allow_finalizer_decl: "allow_finalizer"
    // UB-7.1 — opt-in to mutating the iterated container inside a for loop
    allow_iteration_mutation_decl: "allow_iteration_mutation"

    bounded_int_decl: "assumes" "bounded_int" "(" NUMBER ")"

    // §2.1.12 Proof citation — emits a Why3 axiom in the WhyML preamble
    // whose body is provided by the cited Rocq or Lean theorem under
    // <test>.proofs/{rocq,lean}/. See docs/cross-validated-spec-sources.md.
    // `PROVER_ID` is restricted to {rocq, lean} by the terminal.
    // `QUALNAME` is a dotted identifier path (e.g. Pycsl.Reference.Gcd.gcd_step).
    proof_decl: "proof" PROVER_ID QUALNAME
    PROVER_ID: "rocq" | "lean"
    QUALNAME: CNAME ("." CNAME)*

    // Expression hierarchy (handles operator precedence and left-recursion)
    // Quantifiers can appear at top level or as the RHS of ==>, and, or.
    ?expr: implication
         | "\\forall" CNAME ";" expr -> forall_expr
             | "\\forall" CNAME ":" CNAME ";" expr -> forall_typed_expr
             | "\\forall" CNAME "in" expr ";" expr -> forall_in_expr
             | "\\forall" CNAME ":" CNAME "in" expr ";" expr -> forall_typed_in_expr
             | "\\forall" CNAME ("," CNAME)+ ";" expr -> forall_multi_expr
         | "\\exists" CNAME ";" expr -> exists_expr
             | "\\exists" CNAME ":" CNAME ";" expr -> exists_typed_expr
             | "\\exists" CNAME "in" expr ";" expr -> exists_in_expr
             | "\\exists" CNAME ":" CNAME "in" expr ";" expr -> exists_typed_in_expr
             | "\\exists" CNAME ("," CNAME)+ ";" expr -> exists_multi_expr
         | "\\exist"  CNAME ";" expr -> exists_expr
             | "\\exist"  CNAME ":" CNAME ";" expr -> exists_typed_expr
             | "\\exist"  CNAME "in" expr ";" expr -> exists_in_expr
             | "\\exist"  CNAME ":" CNAME "in" expr ";" expr -> exists_typed_in_expr
             | "\\exist"  CNAME ("," CNAME)+ ";" expr -> exists_multi_expr

    ?implication: logical_or | implication IMPL_OP impl_rhs
    ?impl_rhs: logical_or
             | "\\forall" CNAME ";" expr -> forall_expr
             | "\\forall" CNAME ":" CNAME ";" expr -> forall_typed_expr
             | "\\forall" CNAME "in" expr ";" expr -> forall_in_expr
             | "\\forall" CNAME ":" CNAME "in" expr ";" expr -> forall_typed_in_expr
             | "\\forall" CNAME ("," CNAME)+ ";" expr -> forall_multi_expr
             | "\\exists" CNAME ";" expr -> exists_expr
             | "\\exists" CNAME ":" CNAME ";" expr -> exists_typed_expr
             | "\\exists" CNAME "in" expr ";" expr -> exists_in_expr
             | "\\exists" CNAME ":" CNAME "in" expr ";" expr -> exists_typed_in_expr
             | "\\exists" CNAME ("," CNAME)+ ";" expr -> exists_multi_expr
             | "\\exist"  CNAME ";" expr -> exists_expr
             | "\\exist"  CNAME ":" CNAME ";" expr -> exists_typed_expr
             | "\\exist"  CNAME "in" expr ";" expr -> exists_in_expr
             | "\\exist"  CNAME ":" CNAME "in" expr ";" expr -> exists_typed_in_expr
             | "\\exist"  CNAME ("," CNAME)+ ";" expr -> exists_multi_expr

    ?logical_or: logical_and | logical_or OR_OP or_rhs
    ?or_rhs: logical_and
           | "\\forall" CNAME ";" expr -> forall_expr
             | "\\forall" CNAME ":" CNAME ";" expr -> forall_typed_expr
             | "\\forall" CNAME "in" expr ";" expr -> forall_in_expr
             | "\\forall" CNAME ":" CNAME "in" expr ";" expr -> forall_typed_in_expr
             | "\\forall" CNAME ("," CNAME)+ ";" expr -> forall_multi_expr
           | "\\exists" CNAME ";" expr -> exists_expr
             | "\\exists" CNAME ":" CNAME ";" expr -> exists_typed_expr
             | "\\exists" CNAME "in" expr ";" expr -> exists_in_expr
             | "\\exists" CNAME ":" CNAME "in" expr ";" expr -> exists_typed_in_expr
             | "\\exists" CNAME ("," CNAME)+ ";" expr -> exists_multi_expr
           | "\\exist"  CNAME ";" expr -> exists_expr
             | "\\exist"  CNAME ":" CNAME ";" expr -> exists_typed_expr
             | "\\exist"  CNAME "in" expr ";" expr -> exists_in_expr
             | "\\exist"  CNAME ":" CNAME "in" expr ";" expr -> exists_typed_in_expr
             | "\\exist"  CNAME ("," CNAME)+ ";" expr -> exists_multi_expr

    ?logical_and: equality | logical_and AND_OP and_rhs
    ?and_rhs: equality
            | "\\forall" CNAME ";" expr -> forall_expr
             | "\\forall" CNAME ":" CNAME ";" expr -> forall_typed_expr
             | "\\forall" CNAME "in" expr ";" expr -> forall_in_expr
             | "\\forall" CNAME ":" CNAME "in" expr ";" expr -> forall_typed_in_expr
             | "\\forall" CNAME ("," CNAME)+ ";" expr -> forall_multi_expr
            | "\\exists" CNAME ";" expr -> exists_expr
             | "\\exists" CNAME ":" CNAME ";" expr -> exists_typed_expr
             | "\\exists" CNAME "in" expr ";" expr -> exists_in_expr
             | "\\exists" CNAME ":" CNAME "in" expr ";" expr -> exists_typed_in_expr
             | "\\exists" CNAME ("," CNAME)+ ";" expr -> exists_multi_expr
            | "\\exist"  CNAME ";" expr -> exists_expr
             | "\\exist"  CNAME ":" CNAME ";" expr -> exists_typed_expr
             | "\\exist"  CNAME "in" expr ";" expr -> exists_in_expr
             | "\\exist"  CNAME ":" CNAME "in" expr ";" expr -> exists_typed_in_expr
             | "\\exist"  CNAME ("," CNAME)+ ";" expr -> exists_multi_expr
    ?equality: comparison | equality EQ_OP comparison
    ?comparison: membership | comparison COMP_OP membership
    ?membership: term
              | term "in" term -> in_expr
              | term "not" "in" term -> not_in_expr
    ?term: factor | term ADD_OP factor
    ?factor: unary | factor MUL_OP unary
    
    ?unary: UNARY_OP unary -> unary_op
          | atom

    ?atom: DECIMAL -> decimal
         | NUMBER -> number
         | ESCAPED_STRING -> string_literal
         | "True" -> true_lit
         | "False" -> false_lit
         | "None" -> none_lit
         | "self" "." CNAME "[" expr "]" -> field_subscript
         | "self" "." CNAME -> field_access
         | CNAME "." CNAME -> param_field_access
         | "\\result" "[" expr "]" -> result_subscript
         | "\\result" "." CNAME -> result_field
         | "\\is_sorted" "(" CNAME "," expr "," expr ")" -> is_sorted_expr
         | "\\array_eq" "(" expr "," expr ")" -> array_eq_expr
         | "\\permutation" "(" expr "," expr ")" -> permutation_expr
         | "\\sum" "(" CNAME "," expr "," expr ")" -> sum_expr
         | CNAME "(" expr_list ")" -> call_expr
         | CNAME "(" ")" -> call_expr_noargs
         | CNAME "[" expr ":" expr "]" -> slice_access
         | CNAME "[" expr "]" "[" expr "]" -> chained_subscript
         | CNAME "[" expr "]" -> subscript_access
         | CNAME -> var
         | "\\result" -> result
         | "\\old" "(" expr ")" -> old_var
         | "\\length" "(" CNAME ")" -> array_length
         | "\\length" "(" "self" "." CNAME ")" -> array_length_field
         | "\\length" "(" "\\result" ")" -> array_length_result
         | "\\valid" "(" CNAME "," expr ")" -> valid_pred
         | "\\separated" "(" CNAME "," expr "," CNAME "," expr ")" -> separated_pred
         | "\\at" "(" expr "," CNAME ")" -> at_expr
         | "\\length2d" "(" CNAME "," expr "," expr ")" -> length2d_pred
         | "\\valid2d" "(" CNAME "," expr "," expr ")" -> valid2d_pred
         | atom "^" atom -> str_concat
         | "\\str_length" "(" expr ")" -> str_length_expr
         | "\\str_sub" "(" expr "," expr "," expr ")" -> str_sub_expr
         | "\\mktuple" "(" expr_list ")" -> mktuple_expr
         | "\\fst" "(" expr ")" -> fst_expr
         | "\\snd" "(" expr ")" -> snd_expr
         | "\\proj" "(" expr "," expr ")" -> proj_expr
         | "\\is_ctor" "(" CNAME "," CNAME ")" -> ctor_test
         | "\\payload" "(" CNAME "," CNAME "," NUMBER ")" -> ctor_payload_idx
         | "\\payload" "(" CNAME "," CNAME ")" -> ctor_payload
         | "\\empty_map" -> empty_map_expr
         | "\\map_get" "(" expr "," expr ")" -> map_get_expr
         | "\\map_set" "(" expr "," expr "," expr ")" -> map_set_expr
         | "\\map_eq" "(" expr "," expr ")" -> map_eq_expr
         | "\\has_key" "(" expr "," expr ")" -> has_key_expr
         | "\\map_remove" "(" expr "," expr ")" -> map_remove_expr
         | "\\set_empty" -> set_empty_expr
         | "\\set_add" "(" expr "," expr ")" -> set_add_expr
         | "\\set_remove" "(" expr "," expr ")" -> set_remove_expr
         | "\\set_mem" "(" expr "," expr ")" -> set_mem_expr
         | "\\set_union" "(" expr "," expr ")" -> set_union_expr
         | "\\set_inter" "(" expr "," expr ")" -> set_inter_expr
         | "\\set_diff" "(" expr "," expr ")" -> set_diff_expr
         | "\\set_card" "(" expr "," expr "," expr ")" -> set_card_expr
         | "\\set_subset" "(" expr "," expr ")" -> set_subset_expr
         | "\\set_eq" "(" expr "," expr ")" -> set_eq_expr
         | "\\nil" -> nil_expr
         | "\\cons" "(" expr "," expr ")" -> cons_expr
         | "\\hd" "(" expr ")" -> hd_expr
         | "\\tl" "(" expr ")" -> tl_expr
         | "\\list_length" "(" expr ")" -> list_length_expr
         | "\\nth" "(" expr "," expr ")" -> nth_expr
         | "\\mem" "(" expr "," expr ")" -> mem_expr
         | "\\append" "(" expr "," expr ")" -> append_expr
         | "\\copy" "(" CNAME ")" -> copy_expr
         | "\\copy_range" "(" CNAME "," expr "," expr ")" -> copy_range_expr
         | "\\make" "(" expr "," expr ")" -> make_expr
         | "(" expr ")"

    expr_list: expr ("," expr)*

    // Concurrency annotations
    mutex_expr: CNAME "[" expr "]" -> mutex_subscript
              | CNAME -> mutex_name

    datatype_decl: "datatype" CNAME ("[" CNAME ("," CNAME)* "]")? "=" variant_def ("|" variant_def)*
    inductive_decl: "inductive" CNAME "(" mixin_params? ")" ":" inductive_rule+ inductive_with_member*
    inductive_with_member: "with" CNAME "(" mixin_params? ")" ":" inductive_rule+
    inductive_rule: CNAME ":" expr
    variant_def: CNAME "(" CNAME ("," CNAME)* ")" -> variant_payload
               | CNAME -> variant_nullary

    // Mixin composition directives (mixin.md / mixin-ready.md, Tier 1).
    mixin_decl: "mixin"
    provides_decl: "provides" CNAME
    shared_state_decl: "shared_state" CNAME ":" mixin_type
    touches_field_decl: "touches_field" CNAME ":" mixin_type
    depends_method_decl: "depends_method" CNAME ":" mixin_method_sig
    requires_method_decl: "requires_method" CNAME ":" mixin_method_sig
    compose_from_decl: "compose_from" CNAME ("," CNAME)*
    // A method signature `(self, x: int) -> int`; param annotations optional.
    mixin_method_sig: "(" mixin_params? ")" "->" mixin_type
    mixin_params: mixin_param ("," mixin_param)*
    mixin_param: CNAME (":" mixin_type)?
    // A type reference: a name with optional generic args (`int`, `List[int]`).
    mixin_type: CNAME ("[" mixin_type ("," mixin_type)* "]")?

    shared_decl: "shared" CNAME "protected_by" mutex_expr -> shared_protected
               | "shared" CNAME -> shared_unprotected
    thread_entry_decl: "thread_entry"
    acquires_decl: "acquires" mutex_expr
    releases_decl: "releases" mutex_expr
    critical_decl: "critical" mutex_expr
    mutex_invariant_decl: "mutex_invariant" mutex_expr ":" expr
    lock_order_decl: "lock_order" mutex_expr ("," mutex_expr)*

    // Explicit tokens so Lark doesn't drop the operators
    IMPL_OP: "==>" | "<==>"
    OR_OP: "or"
    AND_OP: "and"
    EQ_OP: "==" | "!="
    COMP_OP: ">" | "<" | ">=" | "<="
    ADD_OP: "+" | "-"
    MUL_OP: "*" | "//" | "/" | "%"
    UNARY_OP: "not" | "-" | "+"
    RANGE_OP: ".."
    GHOST_AUG_OP: "+=" | "-=" | "*="
    GHOST_TYPE: "string" | "array" | "ghost_dict" | "ghost_list" | "ghost_set" | "tuple2" | "tuple3" | "tuple4"

    %import common.CNAME
    %import common.INT -> NUMBER
    DECIMAL.2: /\d+\.\d+/
    %import common.ESCAPED_STRING
    %import common.WS
    %ignore WS
"""

def _csl_to_str(node: CSLNode) -> str:
    """Convert a simple CSL node to string — used for mutex subscript indices."""
    if isinstance(node, Var):
        return node.name
    if isinstance(node, Number):
        return str(int(node.value))
    if isinstance(node, BinOp):
        return f"{_csl_to_str(node.left)}{node.op}{_csl_to_str(node.right)}"
    return "?"


# ---------------------------------------------------------
# 3. The Tree Transformer
# ---------------------------------------------------------

@v_args(inline=True)
class PyCSLTransformer(Transformer):
    """Converts Lark's ParseTree into our Contract AST Nodes."""
    
    def precondition(self, expr) -> Requires: return Requires(expr)
    def postcondition(self, expr) -> Ensures: return Ensures(expr)

    def given_clause(self, expr) -> Given: return Given(expr)
    def act_block(self, name, *clauses) -> Act: return Act(str(name), list(clauses))
    def act_names(self, *names) -> list: return [str(n) for n in names]
    def complete_decl(self, names) -> Complete: return Complete(names)
    def disjoint_decl(self, names) -> Disjoint: return Disjoint(names)
    def happy_decl(self, name, lo, _op, hi, field, *rest) -> HappyProperty:
        # `rest` is the optional except list (act_names → List[str]) or empty.
        except_set = list(rest[0]) if rest else []
        return HappyProperty(str(name), str(field), lo, hi, except_set)

    # 07-1143 R1/R2: subsystem-ownership HAPPY (`protects <dotted paths> except <methods>`).
    def dotted_path(self, *parts) -> str:
        return ".".join(str(p) for p in parts)

    def dotted_path_list(self, *paths) -> list:
        return [str(p) for p in paths]

    def happy_protects_decl(self, name, paths, *rest) -> HappyProperty:
        except_set = list(rest[0]) if rest else []
        return HappyProperty(str(name), "", None, None, except_set, protects=list(paths))

    def assigns(self, target) -> Assigns:
        if isinstance(target, Nothing):
            return Assigns([target])
        elif isinstance(target, list):
            return Assigns(target)
        else:
            return Assigns([target])

    def loop_invariant(self, expr) -> LoopInvariant: return LoopInvariant(expr)
    def loop_variant(self, expr) -> LoopVariant: return LoopVariant(expr)
    def class_invariant(self, expr) -> ClassInvariant: return ClassInvariant(expr)
    def function_variant(self, expr) -> FunctionVariant: return FunctionVariant(expr)
    def function_variant_structural(self, expr, ordering) -> FunctionVariant: return FunctionVariant(expr, str(ordering))
    def diverges_decl(self) -> Diverges: return Diverges()
    def trusted_decl(self, *args) -> Trusted:
        return Trusted(reviewer=str(args[0]) if args else "")
    def abstract_decl(self) -> Abstract:
        return Abstract()
    def lemma_decl(self) -> Lemma:
        return Lemma()
    def uses_decl(self, name) -> Uses:
        return Uses(str(name))
    def preserves_decl(self) -> Preserves:
        return Preserves()
    def ghost_assign_typed(self, name, ghost_type, expr) -> GhostAssignDecl:
        return GhostAssignDecl(str(name), expr, "=", declared_type=str(ghost_type))
    def ghost_assign_untyped(self, name, expr) -> GhostAssignDecl:
        return GhostAssignDecl(str(name), expr, "=")
    def ghost_aug_assign(self, name, op, expr) -> GhostAssignDecl: return GhostAssignDecl(str(name), expr, str(op))
    def ghost_array_set(self, name, index, value) -> GhostArraySetDecl:
        return GhostArraySetDecl(str(name), index, value)
    def raises_decl(self, exc_type, condition) -> RaisesDecl: return RaisesDecl(str(exc_type), condition)

    def exception_name_list(self, *names) -> List[str]:
        return [str(n) for n in names]

    def no_exception_all_decl(self) -> NoExceptionDecl:
        return NoExceptionDecl(exceptions=[], all_form=True)

    def no_exception_list_decl(self, names) -> NoExceptionDecl:
        return NoExceptionDecl(exceptions=list(names), all_form=False)

    def allow_finalizer_decl(self) -> AllowFinalizerDecl:
        return AllowFinalizerDecl()

    def allow_iteration_mutation_decl(self) -> AllowIterationMutationDecl:
        return AllowIterationMutationDecl()

    def bounded_int_decl(self, size) -> BoundedIntDecl: return BoundedIntDecl(int(size))
    def proof_decl(self, prover, qualname) -> ProofDecl:
        return ProofDecl(prover=str(prover), qualname=str(qualname))

    # Concurrency annotations
    def mutex_name(self, name) -> str: return str(name)
    def mutex_subscript(self, name, index) -> str:
        return f"{name}[{_csl_to_str(index)}]"
    def shared_protected(self, name, mutex) -> SharedDecl: return SharedDecl(str(name), str(mutex))
    def shared_unprotected(self, name) -> SharedDecl: return SharedDecl(str(name), None)
    # sum-types: `datatype Name = C1 | C2(int) | …`
    def inductive_decl(self, name, *rest) -> InductiveDecl:
        # `rest` holds, in order: an optional `mixin_params` (a str), the
        # `inductive_rule+` results (each a 2-tuple `(rule_name, clause_expr)`), and
        # any `inductive_with_member` results (each a 3-tuple `(name, sig, rules)` —
        # inductive.md P2 mutual group). Rules are folded INLINE under the header
        # (indentation block — the `#@ rule` keyword was retired).
        params = next((r for r in rest if isinstance(r, str)), None)
        rules = [r for r in rest if isinstance(r, tuple) and len(r) == 2]
        members = [r for r in rest if isinstance(r, tuple) and len(r) == 3]
        sig = f"({params})" if params else "()"
        return InductiveDecl(str(name), sig, rules, members)
    def inductive_with_member(self, name, *rest) -> tuple:
        params = next((r for r in rest if isinstance(r, str)), None)
        rules = [r for r in rest if isinstance(r, tuple) and len(r) == 2]
        sig = f"({params})" if params else "()"
        return (str(name), sig, rules)
    def inductive_rule(self, name, body) -> tuple:
        return (str(name), body)
    def datatype_decl(self, name, *args) -> DatatypeDecl:
        # A5d: type-parameter CNAMEs arrive as bare tokens; variants arrive as
        # (ctor, [types]) tuples — partition by shape.
        type_params = [str(a) for a in args if not isinstance(a, tuple)]
        variants = [a for a in args if isinstance(a, tuple)]
        return DatatypeDecl(str(name), variants, type_params)
    def variant_payload(self, ctor, *types): return (str(ctor), [str(t) for t in types])
    def variant_nullary(self, ctor): return (str(ctor), [])

    # Mixin composition directives (mixin.md / mixin-ready.md, Tier 1).
    def mixin_decl(self) -> MixinDecl: return MixinDecl()
    def provides_decl(self, method) -> ProvidesDecl: return ProvidesDecl(str(method))
    def shared_state_decl(self, name, ty) -> SharedStateDecl:
        return SharedStateDecl(str(name), str(ty))
    def touches_field_decl(self, name, ty) -> TouchesFieldDecl:
        return TouchesFieldDecl(str(name), str(ty))
    def depends_method_decl(self, method, sig) -> MethodDependencyDecl:
        return MethodDependencyDecl(str(method), str(sig), "depends")
    def requires_method_decl(self, method, sig) -> MethodDependencyDecl:
        return MethodDependencyDecl(str(method), str(sig), "requires")
    def compose_from_decl(self, *names) -> ComposeFromDecl:
        return ComposeFromDecl([str(n) for n in names])
    # Render a method signature / type reference back to a canonical string so the
    # S2 composition pass can compare provider vs declared signatures textually.
    def mixin_method_sig(self, *args) -> str:
        # args: (params_str?, return_type_str) — params optional (filter a possible
        # None placeholder from the `?` quantifier).
        vals = [a for a in args if a is not None]
        if len(vals) == 2:
            return f"({vals[0]}) -> {vals[1]}"
        return f"() -> {vals[0]}"
    def mixin_params(self, *params) -> str: return ", ".join(str(p) for p in params)
    def mixin_param(self, name, *ty) -> str:
        return f"{name}: {ty[0]}" if ty else str(name)
    def mixin_type(self, name, *args) -> str:
        return f"{name}[{', '.join(str(a) for a in args)}]" if args else str(name)

    def thread_entry_decl(self) -> ThreadEntry: return ThreadEntry()
    def acquires_decl(self, mutex) -> Acquires: return Acquires(str(mutex))
    def releases_decl(self, mutex) -> Releases: return Releases(str(mutex))
    def critical_decl(self, mutex) -> CriticalSection: return CriticalSection(str(mutex))
    def mutex_invariant_decl(self, mutex, expr) -> MutexInvariant: return MutexInvariant(str(mutex), expr)
    def lock_order_decl(self, *mutexes) -> LockOrder: return LockOrder([str(m) for m in mutexes])

    # Quantifiers
    def forall_expr(self, var, body) -> Forall: return Forall(str(var), body)
    def exists_expr(self, var, body) -> Exists: return Exists(str(var), body)
    def forall_typed_expr(self, var, ty, body) -> Forall:
        return Forall(str(var), body, binder_type=str(ty))
    def exists_typed_expr(self, var, ty, body) -> Exists:
        return Exists(str(var), body, binder_type=str(ty))
    # quantification.md P3 / scc3.md Phase B — bounded quantification `\forall x [: T] in S; P`.
    # Desugared here, reusing the P1 typed binder + the existing `in` membership +
    # implication/conjunction:  \forall x in S; P ≡ \forall x; (x in S) ==> P ;
    # \exists x in S; P ≡ \exists x; (x in S) and P. No new IR/Module 6 emission.
    def forall_in_expr(self, var, domain, body) -> Forall:
        return Forall(str(var), BinOp(CSLIn(Var(str(var)), domain), "==>", body))
    def forall_typed_in_expr(self, var, ty, domain, body) -> Forall:
        return Forall(str(var), BinOp(CSLIn(Var(str(var)), domain), "==>", body),
                      binder_type=str(ty))
    def exists_in_expr(self, var, domain, body) -> Exists:
        return Exists(str(var), BinOp(CSLIn(Var(str(var)), domain), "and", body))
    def exists_typed_in_expr(self, var, ty, domain, body) -> Exists:
        return Exists(str(var), BinOp(CSLIn(Var(str(var)), domain), "and", body),
                      binder_type=str(ty))
    # quantification (remains-2.md C) — multi-binder sugar `\forall x, y, …; P`,
    # desugared to nested single binders (all `int`): \forall x; \forall y; … P.
    def forall_multi_expr(self, *items) -> Forall:
        *names, body = items
        node = body
        for nm in reversed(names):
            node = Forall(str(nm), node)
        return node
    def exists_multi_expr(self, *items) -> Exists:
        *names, body = items
        node = body
        for nm in reversed(names):
            node = Exists(str(nm), node)
        return node
    def array_length(self, var) -> ArrayLength: return ArrayLength(str(var))
    def array_length_field(self, field_name) -> ArrayLength:
        # `\length(self.f)` — length of an `array int` record field.
        # Emitted by Module6 as `Array.length self.f`.
        return ArrayLength("self." + str(field_name))
    def array_length_result(self) -> ArrayLength:
        # `\length(\result)` — length of an `array int` return value.
        # Emitted by Module6 as `Array.length result`.
        return ArrayLength("\\result")
    def subscript_access(self, name, index) -> SubscriptAccess: return SubscriptAccess(str(name), index)
    def chained_subscript(self, name, index1, index2) -> ChainedSubscript: return ChainedSubscript(str(name), index1, index2)
    def slice_access(self, name, low, high) -> CSLSlice: return CSLSlice(str(name), low, high)
    def result_subscript(self, index) -> SubscriptAccess: return SubscriptAccess("\\result", index)
    # 07-0903 W2: `\result.<field>` — field access on a record-returning function's result.
    def result_field(self, field_name) -> FieldAccess: return FieldAccess("\\result", str(field_name))
    def assigns_region(self, name, low, _op, high) -> AssignsRegion: return AssignsRegion(str(name), low, high)
    def assigns_region_list(self, *regions) -> List[AssignsRegion]: return list(regions)
    def valid_pred(self, name, length) -> Valid: return Valid(str(name), length)
    def separated_pred(self, name1, len1, name2, len2) -> Separated: return Separated(str(name1), len1, str(name2), len2)
    def label_decl(self, name) -> Label: return Label(str(name))
    def assert_decl(self, expr) -> CheckPoint: return CheckPoint("assert", expr)
    def check_decl(self, expr) -> CheckPoint: return CheckPoint("check", expr)
    def at_expr(self, expr, label) -> At: return At(expr, str(label))
    def length2d_pred(self, name, rows, cols) -> Length2D: return Length2D(str(name), rows, cols)
    def valid2d_pred(self, name, row, col) -> Valid2D: return Valid2D(str(name), row, col)

    # Operations
    # All binary-operator rules build the same `BinOp(left, op, right)`; one handler,
    # aliased to each rule name (Lark resolves rule → method by name, and the class-level
    # @v_args(inline=True) spreads children as positional args for every alias too).
    def _binop(self, left, op, right) -> BinOp: return BinOp(left, str(op), right)
    implication = logical_or = logical_and = equality = comparison = term = factor = _binop

    def unary_op(self, op, expr) -> UnaryOp: return UnaryOp(str(op), expr)

    # Atoms
    def number(self, n) -> Number: return Number(int(n))
    # no-more-int Stage D: a decimal literal (`0.0`, `1.5`) is a float — kept distinct from
    # an integer NUMBER so Module6 lowers it to a Why3 `real`, not an int.
    def decimal(self, n) -> Number: return Number(float(n))
    def string_literal(self, s) -> StringLiteral: return StringLiteral(str(s)[1:-1])  # strip quotes
    def true_lit(self) -> CSLBool: return CSLBool(True)
    def false_lit(self) -> CSLBool: return CSLBool(False)
    def none_lit(self) -> CSLNone: return CSLNone()
    def var(self, name) -> Var: return Var(str(name))
    def field_access(self, field_name) -> FieldAccess: return FieldAccess("self", str(field_name))
    # no-more-int-2 Track 3: `p.field` on a record-typed param in a contract (object != "self").
    def param_field_access(self, var, field_name) -> FieldAccess:
        return FieldAccess(str(var), str(field_name))
    def field_subscript(self, field_name, index) -> FieldSubscript: return FieldSubscript(str(field_name), index)
    def result(self) -> Result: return Result()
    def old_var(self, expr) -> Old: return Old(expr)
    def nothing(self) -> Nothing: return Nothing()

    # Membership
    def in_expr(self, element, collection) -> CSLIn: return CSLIn(element, collection)
    def not_in_expr(self, element, collection) -> CSLNotIn: return CSLNotIn(element, collection)

    # Function calls and built-in predicates
    def call_expr(self, name, args) -> CallExpr: return CallExpr(str(name), args if isinstance(args, list) else [args])
    def call_expr_noargs(self, name) -> CallExpr: return CallExpr(str(name), [])
    def is_sorted_expr(self, base, lo, hi) -> IsSorted: return IsSorted(str(base), lo, hi)
    def array_eq_expr(self, left, right) -> ArrayEq: return ArrayEq(left, right)
    def permutation_expr(self, left, right) -> Permutation: return Permutation(left, right)
    def sum_expr(self, base, lo, hi) -> Sum: return Sum(str(base), lo, hi)

    # Ghost expression transformers
    def str_concat(self, left, right) -> StrConcatExpr: return StrConcatExpr(left, right)
    def str_length_expr(self, string) -> StrLengthExpr: return StrLengthExpr(string)
    def str_sub_expr(self, string, lo, hi) -> StrSubExpr: return StrSubExpr(string, lo, hi)
    def mktuple_expr(self, elts) -> MkTupleExpr: return MkTupleExpr(elts if isinstance(elts, list) else [elts])
    def fst_expr(self, expr) -> FstExpr: return FstExpr(expr)
    def snd_expr(self, expr) -> SndExpr: return SndExpr(expr)
    def proj_expr(self, expr, index) -> ProjExpr: return ProjExpr(expr, index)
    def ctor_test(self, var, ctor) -> CtorTest: return CtorTest(str(var), str(ctor))
    def ctor_payload(self, var, ctor) -> CtorPayload: return CtorPayload(str(var), str(ctor), 0)
    def ctor_payload_idx(self, var, ctor, idx) -> CtorPayload: return CtorPayload(str(var), str(ctor), int(idx))
    def empty_map_expr(self) -> MapEmptyExpr: return MapEmptyExpr()
    def map_get_expr(self, dict_expr, key) -> MapGetExpr: return MapGetExpr(dict_expr, key)
    def map_set_expr(self, dict_expr, key, value) -> MapSetExpr: return MapSetExpr(dict_expr, key, value)
    def map_eq_expr(self, left, right) -> MapEqExpr: return MapEqExpr(left, right)
    def has_key_expr(self, dict_expr, key) -> HasKeyExpr: return HasKeyExpr(dict_expr, key)
    def map_remove_expr(self, dict_expr, key) -> MapRemoveExpr: return MapRemoveExpr(dict_expr, key)
    def set_empty_expr(self) -> SetEmptyExpr: return SetEmptyExpr()
    def set_add_expr(self, set_expr, elem) -> SetAddExpr: return SetAddExpr(set_expr, elem)
    def set_remove_expr(self, set_expr, elem) -> SetRemoveExpr: return SetRemoveExpr(set_expr, elem)
    def set_mem_expr(self, elem, set_expr) -> SetMemExpr: return SetMemExpr(elem, set_expr)
    def set_union_expr(self, left, right) -> SetUnionExpr: return SetUnionExpr(left, right)
    def set_inter_expr(self, left, right) -> SetInterExpr: return SetInterExpr(left, right)
    def set_diff_expr(self, left, right) -> SetDiffExpr: return SetDiffExpr(left, right)
    def set_card_expr(self, set_expr, lo, hi) -> SetCardExpr: return SetCardExpr(set_expr, lo, hi)
    def set_subset_expr(self, left, right) -> SetSubsetExpr: return SetSubsetExpr(left, right)
    def set_eq_expr(self, left, right) -> SetEqExpr: return SetEqExpr(left, right)
    def nil_expr(self) -> NilExpr: return NilExpr()
    def cons_expr(self, head, tail) -> ConsExpr: return ConsExpr(head, tail)
    def hd_expr(self, list_expr) -> HdExpr: return HdExpr(list_expr)
    def tl_expr(self, list_expr) -> TlExpr: return TlExpr(list_expr)
    def list_length_expr(self, list_expr) -> ListLengthExpr: return ListLengthExpr(list_expr)
    def nth_expr(self, list_expr, index) -> NthExpr: return NthExpr(list_expr, index)
    def mem_expr(self, elem, list_expr) -> MemExpr: return MemExpr(elem, list_expr)
    def append_expr(self, left, right) -> AppendExpr: return AppendExpr(left, right)
    def copy_expr(self, name) -> GhostCopyExpr: return GhostCopyExpr(str(name))
    def copy_range_expr(self, name, lo, hi) -> GhostCopyRangeExpr: return GhostCopyRangeExpr(str(name), lo, hi)
    def make_expr(self, size, default) -> GhostMakeExpr: return GhostMakeExpr(size, default)

    def expr_list(self, *exprs) -> List[CSLNode]: return list(exprs)

# ---------------------------------------------------------
# 4. The Parser Interface
# ---------------------------------------------------------

class Module2_Parser:
    """Parses raw PyCSL string contracts into Contract AST objects."""
    def __init__(self) -> None:
        self.parser = Lark(PYCSL_GRAMMAR, parser='lalr', transformer=PyCSLTransformer())

    def parse_contract(self, contract_str: str, line_number: int) -> CSLNode:
        try:
            return self.parser.parse(contract_str)
        except LarkError as e:
            raise PyCSLParseError(
                f"PyCSL Syntax Error around line {line_number}:\n{contract_str}\n{str(e)}",
                line=line_number, stage="parse"
            ) from e

    def parse_node_contracts(self, raw_contracts: List[str], line_number: int) -> List[CSLNode]:
        parsed_nodes = []
        for contract_str in raw_contracts:
            parsed_nodes.append(self.parse_contract(contract_str, line_number))
        return parsed_nodes
