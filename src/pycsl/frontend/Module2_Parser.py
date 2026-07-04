from __future__ import annotations

from dataclasses import dataclass
from typing import List, Union, Any, Optional
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
class ForExpand(CSLNode):
    """`#@ for VAR in range(lo, hi):` (sugar-for-spec.md) — bounded macro-expansion.
    Desugared in Module3 to ground requires/ensures: for each integer m in
    [lo, hi), each body clause with VAR substituted by the literal m. lo/hi are
    bound exprs (Number for v1); clauses are Requires/Ensures."""
    var: str
    lo: CSLNode
    hi: CSLNode
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
    # 07-1143 R3: the PARAMETRIC (per-object) form. `param` is the bound name (e.g. `n`);
    # `protects` holds the single indexed path; `region_lo`/`region_hi` are the bounds in
    # terms of `param`. A method declares `#@ footprint NAME(arg)` to bind `param := arg`;
    # the per-site check then asserts each write index lies in the substituted region.
    param: Optional[str] = None
    # The general `\targets`/`\context` form (coherent with the C sibling macsl): a NAMED
    # security property attached to ONE target function. `context` is "postcond" (the
    # formula becomes an `ensures` on `target`) or "precond" (a `requires`); `formula` is
    # the property expression; `target` is the method name it constrains. Used by H-R
    # (nonrepud, postcond), H-E (priv_monotonic, postcond), H-S (authn, precond).
    target: Optional[str] = None
    formula: Optional[CSLNode] = None
    # H-I2 (noninterference, macsl's \context(\noninterference)): the SECRET parameter names
    # of `target`. The meta-pass synthesizes a self-composition twin `<target>__selfcomp`
    # that calls `target` twice (public params shared, secret params split _a/_b) and asserts
    # the two results are equal — a leak (result depending on a secret) is then unprovable.
    secret: Optional[List[str]] = None


@dataclass
class Footprint(CSLNode):
    """07-1143 R3: `#@ footprint NAME(arg)` — binds the parameter of the parametric HAPPY
    `NAME` to one of the method's own arguments, so the meta-pass injects a per-site
    region check parameterised by `arg` at each write of the protected path."""
    happy_name: str
    arg: CSLNode

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
class GlobalFieldSubscript(CSLNode):
    """Represents `<global>.<field>[expr]` — subscript of a module-global record's
    ARRAY field in a contract (spec-15 / gap-15 Wall B), e.g. `_filesystem.fd_inode[fd]`.
    The sibling of `FieldSubscript` (`self.<field>[i]`) with a module-global instance
    as the base instead of `self`. Lowers to `Subscript(Attribute(Var(obj), field), index)`,
    riding the existing gap-10 global-field projection + spec-context `Array.get` machinery."""
    obj: str         # the module-global instance name, e.g. "_filesystem"
    field: str       # the field name, e.g. "fd_inode"
    index: CSLNode

@dataclass
class ClassInvariant(CSLNode):
    expr: CSLNode

@dataclass
class SubscriptAccess(CSLNode):
    array: str
    index: CSLNode

@dataclass
class SubscriptFieldAccess(CSLNode):
    """cleared-array.md S2: `<array>[<index>].<field>` — a FIELD PROJECTION off a
    subscripted collection element in a contract (e.g. `a[k].x`, `\\result[k].x`).
    Lowers to `Attribute(Subscript(Var(array), index), field)` — the SAME shape
    the body path already produces for `a[i].x`, so the abstract getter
    `get_<field>` matches a content-faithful projection-comprehension law
    (`\\result[k] == a[k].x`). Enables a driver to CONSUME the S2 lift."""
    array: str       # the collection name, or "\\result"
    index: CSLNode
    field: str

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
class InGlobals(CSLNode):
    """07-1839 P2: `\\in_globals(name)` — is `name` a statically-declared module-level
    binding? Three-valued (sound lower bound): decided-true for a declared module name
    (function / class / module global / constant), **unknown** otherwise (the world is
    open — `import`/`exec` inject names), **never** decided-false. Resolved at emission
    against the module-binding set."""
    name: str

@dataclass
class InScope(CSLNode):
    """07-1839 P3: `\\in_scope(name)` — is `name` a local/parameter bound at this point?
    Three-valued via definite-assignment: decided-true if assigned on ALL paths (a formal
    param, or a top-level assignment before any branching/return); decided-false if `name`
    is neither a param nor assigned anywhere; **unknown** (conditionally assigned) otherwise.
    A dynamic `exec`/`eval` havocs the binding set (decision C, P5)."""
    name: str

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
class NoInline(CSLNode):
    """Represents `#@ no_inline` (no-inline.md) — a modular-verification boundary: the method's
    body is verified once against its contract, and callers reuse the contract (a contract-call)
    instead of splicing the inlined body. Avoids re-proving a large body in every caller's
    context (the os `sys_write` inlining blow-up)."""
    pass

@dataclass
class SiblingConcrete(CSLNode):
    """Represents `#@ sibling_concrete` (allocator-frame plan §2.7) — OPT-IN: an intra-class
    `self.<m>()` call to THIS method is lowered to a CONCRETE call `(<class>__<m> self args)`
    (so the caller gets the real method's full contract AND its type/class-invariant guarantee
    on the post-state), instead of the default abstract `val` stub. Use ONLY on cheap-to-
    maintain leaf writers whose guarantee the caller can absorb as an atom (e.g. the os bitmap
    leaves `_set_bitmap`/`_poke`). Decoupled from `no_inline`: it affects sibling-call lowering
    only, NOT whether the body is inlined into wrappers — so it cannot perturb a separate
    importer gate. Default off → every existing self-call keeps its abstract-stub lowering."""
    pass

@dataclass
class VerifyModule(CSLNode):
    """Represents `#@ verify_module <name>` (module-emission.md) — OPT-IN axiom-isolation:
    the method is emitted into its OWN top-level Why3 `module <name>` (re-declaring the shared
    infra — record type, val-functions, predicates, witness/class-invariant axioms, abstract
    stubs) so that ONLY the `#@ proof` axioms cited by the functions in that module are in
    scope for its goals. Functions sharing the same `<name>` are co-emitted into one module.
    Cross-module `self.<m>(...)` calls (a sibling in a DIFFERENT verify_module / the flat
    default module) are lowered to a bodyless `val` carrying the sibling's proven contract,
    discharged by the Track-B narrowing VC in the sibling's owning module — a PROVEN interface,
    never an assumed `val` / new `\\trusted` / new axiom. Resolves the read+write axiom
    co-residence OOM that blocks `_dir_lookup` (read `field_to_str`/`dir_scan_*` axioms out of
    scope for the write helpers' per-byte goals, and vice-versa). Default (untagged) → the
    single flat `module PyCSL_Program` is emitted unchanged → corpus byte-identical."""
    name: str

@dataclass
class PropagateFrame(CSLNode):
    """Represents `#@ propagate_frame` (os-roadmap M4) — OPT-IN: THIS method's QUANTIFIED
    self-field FRAME ensures (`\\forall k. … == \\old(…)`) are propagated onto its `#@ no_inline`
    boundary stub, each pinned with a specific function-application trigger. Use ONLY on a mutator
    whose callers genuinely need the frame and are NOT term-rich enough to E-match-explode under it
    (e.g. the os `_zero_entry`, called only by unlink/rmdir/rename). Default off → the quantified
    frame is dropped at the boundary (the non-quantified write-posts still propagate via the
    field_param_post map). NOT for broad mutators like `_write_entry` whose frame poisons rich
    callers (link/symlink) — see 14-string-field-codec-plan.md §2.9."""
    pass

@dataclass
class FreshGlobals(CSLNode):
    """Represents `#@ fresh_globals` (fresh-globals.md) — OPT-IN, CONFINED: at THIS
    function's body entry, re-establish each module-global singleton's CONSTRUCTOR
    POST-STATE (the class `__init__`'s `#@ ensures`, `self` -> the global) as an
    ASSUMED fact. Models the execution-model convention that a STANDALONE,
    internals-blind formal-test DRIVER runs on a freshly-imported module global
    (import ran `__init__`, so the constructor post-state holds at entry) — instead
    of Why3's default treatment of a shared mutable global as HAVOC'd at every
    importer-function entry.

    SOUNDNESS (Module4-enforced confinement): sound ONLY on an INDEPENDENT entry
    point that is never called by another verified function and never composed after
    a prior driver mutated the shared global — otherwise a callee would falsely
    assume the all-fresh state against an already-mutated global. Module4 REJECTS it
    on `self`-methods, library functions, and any function that is a callee of
    another verified function in the same unit. The assumed fact is NOT an arbitrary
    literal: it is the constructor's `#@ ensures`, which `_emit_module_globals`
    re-checks as a GOAL against the global's literal initializer (so the fact is
    PROVEN of the freshly constructed global). Replaces the FALSE unconditioned
    fd-resolution-fidelity no-ENFILE body theorem with a sound, confined,
    constructor-backed entry fact."""
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
class InterfaceClause(CSLNode):
    """Represents `#@ interface ensures/requires/assigns <…>` (b-spec Track B) — the NARROW
    *interface* contract importers/callers see by default, distinct from the rich *definition*
    contract (the plain `#@ requires/ensures/assigns`) verified against the body. Opacity: the
    definition's extra facts are hidden, revealed only via `#@ reveal`. Absent ⇒ interface =
    definition (transparent — all existing code byte-identical). `kind` ∈ {ensures, requires,
    assigns}; `payload` is the corresponding Ensures/Requires/Assigns node."""
    kind: str
    payload: Any

@dataclass
class Reveal(CSLNode):
    """Represents `#@ reveal <fn>` (b-spec Track B) — this caller opts into `<fn>`'s rich
    DEFINITION contract at this site (the definition facts are otherwise hidden behind the
    interface). Within the owning unit it is a no-op (the definition is the visible `let`);
    across modules it cites the exported definition-fact (v2)."""
    fn: str

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
class DictView(CSLNode):
    """07-1311 Q3: a dict view in a quantifier domain — `d.keys()` / `d.values()` /
    `d.items()`. Only meaningful as the collection of a bounded quantifier
    (`\\forall v in d.values(); …`); Module5's `_csl_in` desugars it onto the map
    model (`map int (option int)`). `kind` ∈ {"keys","values","items"}."""
    coll: str
    kind: str

@dataclass
class ForallItems(QuantifierNode):
    """07-1311 Q3: two-binder `\\forall k, v in d.items(); P(k, v)` — binds the key and
    value of every present entry. Lowers to
    `forall k. match Map.get d k with Some v -> P | None -> true end`."""
    key: str
    val: str
    coll: str
    body: CSLNode

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
class NestedSubscript(CSLNode):
    """nested-list.md §8 EXTENSION: `base[index]` where `base` is itself an
    arbitrary subscript expression — the DEEPER-than-2 chain `arr[i][j][k]`
    (and beyond). Depth ≤2 stays `ChainedSubscript` (byte-identical); this node
    wraps the third and further index levels so `\\result == a[i][j][k]` parses.
    Lowers to `Subscript(<base IR>, <index IR>)`."""
    base: CSLNode
    index: CSLNode

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
class ConformsToDecl(CSLNode):
    """Represents `#@ conforms_to P1, P2, …` (typing-engagement ty2 / PEP 544) — marks a
    class as conforming to the named Protocols. Synthesizes per-method contract-refinement
    `overrides` entries (P2/P4): for each member `m` of each named Protocol `P` that the
    class provides, an `(C__m, P__m)` pair is recorded so `--check-behavioral-subtyping`
    emits the refinement goal `((pre_P -> pre_C) /\\ (post_C -> post_P))`. This is the
    static-plane conformance VC — it must NOT be discharged by any runtime
    `isinstance`/`hasattr` presence check (GT7 no-blend, D1). PEP 544 conformance is
    structural/implicit; PyCSL's TY2 scope requires the explicit directive (divergence-by-
    strictness) so conformance is a discharged per-method VC, not a whole-program search."""
    protocols: list

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
# 3. Hand-written recursive-descent parser (the `pure_ast` style)
# ---------------------------------------------------------
# Replaces the former Lark LALR grammar + PyCSLTransformer. One method per
# grammar rule, each building the SAME `CSLNode` the transformer built. The
# tokenizer is regex-based: Python's `tokenize` rejects the contract language's
# `\result` / `\forall` identifiers (`\` is line-continuation). The differential
# test in `bin/diff_parser.py` proved this engine produces CSLNode trees
# byte-identical to the legacy Lark engine before deletion.

import os as _os
import re as _re


class _ContractSyntaxError(Exception):
    """Internal syntax error raised by `_ContractParser`; converted to
    `PyCSLParseError` at the `Module2_Parser` boundary."""


class _Tok:
    __slots__ = ("type", "string", "start")

    def __init__(self, type_, string, start):
        self.type = type_        # 'NAME' | 'NUMBER' | 'DECIMAL' | 'STRING' | 'BSNAME' | 'OP'
        self.string = string
        self.start = start       # offset into source (for REVIEWER_ID re-scan)

    def __repr__(self):
        return f"_Tok({self.type}, {self.string!r})"


# Longest-match-first operator table (Lark terminal priorities replicated).
_OP_ALTERNATIVES = [
    "==>", "<==>", "//", "..", "+=", "-=", "*=", "->",
    "==", "!=", ">=", "<=",
    "+", "-", "*", "/", "%", "^", ":", ",", ";",
    "(", ")", "[", "]", "=", ".", "<", ">", "|",
]
_TOKEN_RE = _re.compile(_re.escape('|') and r"""(?xs)
    (?P<WS>\s+)
  | (?P<DECIMAL>\d+\.\d+)
  | (?P<NUMBER>\d+)
  | (?P<STRING>"(?:[^"\\]|\\.)*")
  | (?P<BSNAME>\\[A-Za-z_][A-Za-z0-9_]*)
  | (?P<NAME>[A-Za-z_][A-Za-z0-9_]*)
  | (?P<OP>""" + "|".join(_re.escape(o) for o in _OP_ALTERNATIVES) + r""")
""")


def _lex_contract(source: str):
    """Tokenize a contract string (no `#@` prefix) into a list of `_Tok`.

    Mirrors `pure_ast._lex` in shape (filter trivia, return token list) but is
    regex-based: Python's `tokenize` rejects `\\result`/`\\forall` (`\\` is the
    line-continuation character). A trailing NEWLINE is appended if missing so
    the lexer is uniform whether or not the caller included one.
    """
    if not source.endswith("\n"):
        source = source + "\n"
    toks = []
    pos = 0
    n = len(source)
    while pos < n:
        m = _TOKEN_RE.match(source, pos)
        if m is None:
            raise _ContractSyntaxError(
                f"unexpected character {source[pos]!r} at offset {pos}")
        pos = m.end()
        kind = m.lastgroup
        if kind == "WS":
            continue
        toks.append(_Tok(kind, m.group(), m.start()))
    toks.append(_Tok("EOF", "", n))
    return toks, source


# Operator sets used by the expression precedence ladder (mirror the grammar's
# IMPL_OP / OR_OP / AND_OP / EQ_OP / COMP_OP / ADD_OP / MUL_OP terminals).
_IMPL_OPS = ("==>", "<==>")
_EQ_OPS = ("==", "!=")
_COMP_OPS = (">", "<", ">=", "<=")
_ADD_OPS = ("+", "-")
_MUL_OPS = ("*", "//", "/", "%")


class _ContractParser:
    """Recursive-descent parser over `_Tok` producing `CSLNode` trees.

    One method per grammar rule; each builds the SAME `CSLNode` the
    corresponding `PyCSLTransformer` method built. Dispatch is on the leading
    keyword / backslash-name of the contract.
    """

    def __init__(self, source: str):
        toks, raw = _lex_contract(source)
        self.toks = toks
        self.source = raw
        self.i = 0

    # -- token helpers ------------------------------------------------------
    def cur(self):
        return self.toks[self.i]

    def peek(self, k=1):
        j = self.i + k
        return self.toks[j] if j < len(self.toks) else self.toks[-1]

    def advance(self):
        t = self.toks[self.i]
        if self.i < len(self.toks) - 1:
            self.i += 1
        return t

    def at_op(self, *vals):
        t = self.cur()
        return t.type == "OP" and (not vals or t.string in vals)

    def at_name(self, *vals):
        t = self.cur()
        return t.type == "NAME" and (not vals or t.string in vals)

    def at_bs(self, *vals):
        t = self.cur()
        return t.type == "BSNAME" and (not vals or t.string in vals)

    def at_eof(self):
        return self.cur().type == "EOF"

    def accept_op(self, val):
        if self.at_op(val):
            return self.advance()
        return None

    def expect_op(self, val):
        if not self.at_op(val):
            self._err(f"expected {val!r}")
        return self.advance()

    def expect_name(self, val=None):
        if not self.at_name() or (val is not None and not self.at_name(val)):
            self._err(f"expected name {val!r}" if val else "expected name")
        return self.advance().string

    def expect_bs(self, val):
        if not self.at_bs(val):
            self._err(f"expected {val!r}")
        return self.advance().string

    def _err(self, msg):
        t = self.cur()
        raise _ContractSyntaxError(f"{msg} (got {t.type} {t.string!r})")

    def _try(self, fn):
        saved = self.i
        try:
            return fn()
        except _ContractSyntaxError:
            self.i = saved
            return None

    # -- entry --------------------------------------------------------------
    def parse(self):
        node = self._parse_contract()
        if not self.at_eof():
            self._err("unexpected trailing input")
        return node

    # -- top-level dispatch -------------------------------------------------
    def _parse_contract(self):
        t = self.cur()
        if t.type == "NAME":
            kw = t.string
            if kw == "requires": self.advance(); return Requires(self._parse_expr())
            if kw == "ensures":  self.advance(); return Ensures(self._parse_expr())
            if kw == "assigns":  self.advance(); return self._parse_assigns()
            if kw == "loop":     return self._parse_loop()
            if kw == "class":    return self._parse_class_invariant()
            if kw == "label":    self.advance(); return Label(self.expect_name())
            if kw == "assert":   self.advance(); return CheckPoint("assert", self._parse_expr())
            if kw == "check":    self.advance(); return CheckPoint("check", self._parse_expr())
            if kw == "no_inline": self.advance(); return NoInline()
            if kw == "sibling_concrete": self.advance(); return SiblingConcrete()
            if kw == "verify_module": self.advance(); return VerifyModule(self.expect_name())
            if kw == "propagate_frame": self.advance(); return PropagateFrame()
            if kw == "fresh_globals": self.advance(); return FreshGlobals()
            if kw == "lemma": self.advance(); return Lemma()
            if kw == "uses": self.advance(); return Uses(self.expect_name())
            if kw == "interface": return self._parse_interface()
            if kw == "reveal": self.advance(); return Reveal(self.expect_name())
            if kw == "ghost":   return self._parse_ghost()
            if kw == "raises":  return self._parse_raises()
            if kw == "no_exception": return self._parse_no_exception()
            if kw == "allow_finalizer": self.advance(); return AllowFinalizerDecl()
            if kw == "allow_iteration_mutation": self.advance(); return AllowIterationMutationDecl()
            if kw == "assumes": return self._parse_assumes()
            if kw == "proof":   return self._parse_proof()
            if kw == "datatype": return self._parse_datatype()
            if kw == "inductive": return self._parse_inductive()
            if kw == "mixin":   self.advance(); return MixinDecl()
            if kw == "provides": self.advance(); return ProvidesDecl(self.expect_name())
            if kw == "shared_state": return self._parse_shared_state()
            if kw == "touches_field": return self._parse_touches_field()
            if kw == "depends_method": return self._parse_depends_method("depends")
            if kw == "requires_method": return self._parse_depends_method("requires")
            if kw == "compose_from": return self._parse_compose_from()
            if kw == "conforms_to": return self._parse_conforms_to()
            if kw == "shared":   return self._parse_shared()
            if kw == "thread_entry": self.advance(); return ThreadEntry()
            if kw == "acquires": self.advance(); return Acquires(self._parse_mutex_expr_str())
            if kw == "releases": self.advance(); return Releases(self._parse_mutex_expr_str())
            if kw == "critical": self.advance(); return CriticalSection(self._parse_mutex_expr_str())
            if kw == "mutex_invariant": return self._parse_mutex_invariant()
            if kw == "lock_order": return self._parse_lock_order()
            if kw == "act":  return self._parse_act_block()
            if kw == "for":  return self._parse_for_block()
            if kw == "complete": self.advance(); return Complete(self._parse_act_names())
            if kw == "disjoint": self.advance(); return Disjoint(self._parse_act_names())
            if kw == "happy": return self._parse_happy()
            if kw == "footprint": return self._parse_footprint()
        elif t.type == "BSNAME":
            s = t.string
            if s == "\\variant":   return self._parse_function_variant()
            if s == "\\diverges":  self.advance(); return Diverges()
            if s == "\\trusted":   return self._parse_trusted()
            if s == "\\abstract":  self.advance(); return Abstract()
            if s == "\\preserves": self.advance(); return Preserves()
        self._err("unrecognized contract keyword")

    # -- loop / class invariant --------------------------------------------
    def _parse_loop(self):
        self.expect_name("loop")
        if self.at_name("invariant"):
            self.advance(); return LoopInvariant(self._parse_expr())
        if self.at_name("variant"):
            self.advance(); return LoopVariant(self._parse_expr())
        self._err("expected 'invariant' or 'variant' after 'loop'")

    def _parse_class_invariant(self):
        self.expect_name("class")
        self.expect_name("invariant")
        return ClassInvariant(self._parse_expr())

    def _parse_function_variant(self):
        self.expect_bs("\\variant")
        if self.at_op("("):
            self.advance()
            e = self._parse_expr()
            self.expect_op(",")
            ordering = self.expect_name()
            self.expect_op(")")
            return FunctionVariant(e, ordering)
        return FunctionVariant(self._parse_expr())

    # -- trusted / reviewer -------------------------------------------------
    def _parse_trusted(self):
        self.expect_bs("\\trusted")
        reviewer = ""
        if self.at_name("reviewer"):
            self.advance()
            self.expect_op(":")
            reviewer = self._grab_reviewer_id()
        return Trusted(reviewer=reviewer)

    def _grab_reviewer_id(self):
        # REVIEWER_ID: /[A-Za-z0-9._@-]+/ — my tokenizer splits e.g. `c2-probe`
        # into `c2`, `-`, `probe`. Re-scan from the current source position so
        # the matched string is byte-identical to Lark's terminal.
        tok = self.cur()
        pos = tok.start
        m = _re.match(r"[A-Za-z0-9._@-]+", self.source[pos:])
        if m is None:
            self._err("expected reviewer id")
        reviewer = m.group(0)
        end_pos = pos + len(reviewer)
        # advance past every token fully inside the matched span
        while self.i < len(self.toks) and self.toks[self.i].type != "EOF" \
                and self.toks[self.i].start < end_pos:
            self.i += 1
        return reviewer

    # -- ghost --------------------------------------------------------------
    def _parse_ghost(self):
        self.expect_name("ghost")
        name = self.expect_name()
        if self.accept_op(":"):
            gtype = self.expect_name()  # GHOST_TYPE
            self.expect_op("=")
            return GhostAssignDecl(name, self._parse_expr(), "=", declared_type=gtype)
        if self.at_op("+=") or self.at_op("-=") or self.at_op("*="):
            op = self.advance().string
            return GhostAssignDecl(name, self._parse_expr(), op)
        if self.at_op("["):
            self.advance()
            index = self._parse_expr()
            self.expect_op("]")
            self.expect_op("=")
            return GhostArraySetDecl(name, index, self._parse_expr())
        self.expect_op("=")
        return GhostAssignDecl(name, self._parse_expr(), "=")

    # -- raises / no_exception / assumes / proof ----------------------------
    def _parse_raises(self):
        self.expect_name("raises")
        exc = self.expect_name()
        self.expect_name("when")
        return RaisesDecl(exc, self._parse_expr())

    def _parse_no_exception(self):
        self.expect_name("no_exception")
        if self.at_bs("\\all"):
            self.advance()
            return NoExceptionDecl(exceptions=[], all_form=True)
        names = [self.expect_name()]
        while self.accept_op(","):
            names.append(self.expect_name())
        return NoExceptionDecl(exceptions=names, all_form=False)

    def _parse_assumes(self):
        self.expect_name("assumes")
        self.expect_name("bounded_int")
        self.expect_op("(")
        size_tok = self.cur()
        if size_tok.type != "NUMBER":
            self._err("expected NUMBER in bounded_int(...)")
        self.advance()
        self.expect_op(")")
        return BoundedIntDecl(int(size_tok.string))

    def _parse_proof(self):
        self.expect_name("proof")
        prover = self.expect_name()  # PROVER_ID: rocq | lean
        qualname = self._parse_qualname()
        return ProofDecl(prover=prover, qualname=qualname)

    def _parse_qualname(self):
        name = self.expect_name()
        while self.accept_op("."):
            name += "." + self.expect_name()
        return name

    # -- interface / reveal --------------------------------------------------
    def _parse_interface(self):
        self.expect_name("interface")
        if self.at_name("ensures"):
            self.advance(); return InterfaceClause("ensures", Ensures(self._parse_expr()))
        if self.at_name("requires"):
            self.advance(); return InterfaceClause("requires", Requires(self._parse_expr()))
        if self.at_name("assigns"):
            self.advance(); return InterfaceClause("assigns", self._parse_assigns())
        self._err("expected ensures/requires/assigns after 'interface'")

    # -- assigns ------------------------------------------------------------
    def _parse_assigns(self):
        return Assigns(self._parse_assigns_target())

    def _parse_assigns_target(self):
        if self.at_bs("\\nothing"):
            self.advance()
            return [Nothing()]
        region = self._try(self._parse_assigns_region)
        if region is not None:
            regions = [region]
            while self.accept_op(","):
                regions.append(self._parse_assigns_region())
            return regions
        exprs = [self._parse_expr()]
        while self.accept_op(","):
            exprs.append(self._parse_expr())
        return exprs

    def _parse_assigns_region(self):
        name = self.expect_name()
        self.expect_op("[")
        lo = self._parse_expr()
        self.expect_op("..")
        hi = self._parse_expr()
        self.expect_op("]")
        return AssignsRegion(name, lo, hi)

    # -- act / for / complete / disjoint ------------------------------------
    def _parse_act_block(self):
        self.expect_name("act")
        name = self.expect_name()
        self.expect_op(":")
        clauses = []
        while self.at_name("given") or self.at_name("requires") \
                or self.at_name("ensures") or self.at_name("assigns"):
            if self.at_name("given"):
                self.advance(); clauses.append(Given(self._parse_expr()))
            elif self.at_name("requires"):
                self.advance(); clauses.append(Requires(self._parse_expr()))
            elif self.at_name("ensures"):
                self.advance(); clauses.append(Ensures(self._parse_expr()))
            else:
                self.advance(); clauses.append(self._parse_assigns())
        if not clauses:
            self._err("act block requires at least one clause")
        return Act(name, clauses)

    def _parse_for_block(self):
        self.expect_name("for")
        var = self.expect_name()
        self.expect_name("in")
        self.expect_name("range")
        self.expect_op("(")
        e1 = self._parse_expr()
        if self.accept_op(","):
            lo, hi = e1, self._parse_expr()
        else:
            lo, hi = Number(0), e1
        self.expect_op(")")
        self.expect_op(":")
        clauses = []
        while self.at_name("requires") or self.at_name("ensures"):
            if self.at_name("requires"):
                self.advance(); clauses.append(Requires(self._parse_expr()))
            else:
                self.advance(); clauses.append(Ensures(self._parse_expr()))
        if not clauses:
            self._err("for block requires at least one clause")
        return ForExpand(var, lo, hi, clauses)

    def _parse_act_names(self):
        names = [self.expect_name()]
        while self.accept_op(","):
            names.append(self.expect_name())
        return names

    # -- happy / footprint --------------------------------------------------
    def _parse_happy(self):
        self.expect_name("happy")
        name = self.expect_name()
        if self.at_op("("):
            self.advance()
            param = self.expect_name()
            self.expect_op(")")
            self.expect_op(":")
            self.expect_name("protects")
            path = self._parse_dotted_path()
            self.expect_op("[")
            lo = self._parse_expr()
            self.expect_op(":")
            hi = self._parse_expr()
            self.expect_op("]")
            except_set = self._parse_opt_except()
            return HappyProperty(name, "", lo, hi, except_set,
                                 protects=[path], param=param)
        # not parametric: `happy NAME : ...`
        self.expect_op(":")
        if self.at_name("region"):
            return self._parse_happy_region(name)
        if self.at_name("targets"):
            return self._parse_happy_targets(name)
        if self.at_name("protects"):
            self.advance()
            paths = self._parse_dotted_path_list()
            except_set = self._parse_opt_except()
            return HappyProperty(name, "", None, None, except_set, protects=paths)
        self._err("expected 'region'/'targets'/'protects' after 'happy NAME:'")

    def _parse_happy_region(self, name):
        self.expect_name("region")
        lo = self._parse_expr()
        self.expect_op("..")
        hi = self._parse_expr()
        if self.at_name("writes"):
            mode = "writing"
        elif self.at_name("reads"):
            mode = "reading"
        else:
            self._err("expected 'writes' or 'reads' in happy region decl")
        self.advance()
        self.expect_name("self")
        self.expect_op(".")
        field = self.expect_name()
        self.expect_name("outside")
        self.expect_name("region")
        except_set = self._parse_opt_except()
        return HappyProperty(name, field, lo, hi, except_set, context=mode)

    def _parse_happy_targets(self, name):
        self.expect_name("targets")
        target = self.expect_name()
        if self.at_name("postcond"):
            self.advance()
            return HappyProperty(name, "", None, None, [], context="postcond",
                                 target=target, formula=self._parse_expr())
        if self.at_name("precond"):
            self.advance()
            return HappyProperty(name, "", None, None, [], context="precond",
                                 target=target, formula=self._parse_expr())
        if self.at_name("total"):
            self.advance()
            return HappyProperty(name, "", None, None, [], context="total",
                                 target=target)
        if self.at_name("noninterference"):
            self.advance()
            self.expect_name("secret")
            secrets = self._parse_act_names()
            return HappyProperty(name, "", None, None, [], context="noninterference",
                                 target=target, secret=secrets)
        self._err("expected postcond/precond/total/noninterference after targets")

    def _parse_opt_except(self):
        if self.at_name("except"):
            self.advance()
            return self._parse_act_names()
        return []

    def _parse_dotted_path(self):
        path = self.expect_name()
        while self.accept_op("."):
            path += "." + self.expect_name()
        return path

    def _parse_dotted_path_list(self):
        paths = [self._parse_dotted_path()]
        while self.accept_op(","):
            paths.append(self._parse_dotted_path())
        return paths

    def _parse_footprint(self):
        self.expect_name("footprint")
        happy_name = self.expect_name()
        self.expect_op("(")
        arg = self._parse_expr()
        self.expect_op(")")
        return Footprint(happy_name, arg)

    # -- datatype / inductive ----------------------------------------------
    def _parse_datatype(self):
        self.expect_name("datatype")
        name = self.expect_name()
        type_params = []
        if self.at_op("["):
            self.advance()
            type_params.append(self.expect_name())
            while self.accept_op(","):
                type_params.append(self.expect_name())
            self.expect_op("]")
        self.expect_op("=")
        variants = [self._parse_variant_def()]
        while self.accept_op("|"):
            variants.append(self._parse_variant_def())
        return DatatypeDecl(name, variants, type_params)

    def _parse_variant_def(self):
        ctor = self.expect_name()
        if self.at_op("("):
            self.advance()
            types = [self.expect_name()]
            while self.accept_op(","):
                types.append(self.expect_name())
            self.expect_op(")")
            return (ctor, types)
        return (ctor, [])

    def _parse_inductive(self):
        self.expect_name("inductive")
        name = self.expect_name()
        self.expect_op("(")
        params = None
        if not self.at_op(")"):
            params = self._parse_mixin_params()
        self.expect_op(")")
        self.expect_op(":")
        rules = self._parse_inductive_rules()
        members = []
        while self.at_name("with"):
            self.advance()
            wname = self.expect_name()
            self.expect_op("(")
            wparams = None
            if not self.at_op(")"):
                wparams = self._parse_mixin_params()
            self.expect_op(")")
            self.expect_op(":")
            wrules = self._parse_inductive_rules()
            wsig = f"({wparams})" if wparams else "()"
            members.append((wname, wsig, wrules))
        sig = f"({params})" if params else "()"
        return InductiveDecl(name, sig, rules, members)

    def _parse_inductive_rules(self):
        rules = []
        while self.at_name() and not self.at_name("with"):
            rname = self.expect_name()
            self.expect_op(":")
            rules.append((rname, self._parse_expr()))
        if not rules:
            self._err("inductive block requires at least one rule")
        return rules

    # -- mixin composition --------------------------------------------------
    def _parse_shared_state(self):
        self.expect_name("shared_state")
        name = self.expect_name()
        self.expect_op(":")
        ty = self._parse_mixin_type()
        return SharedStateDecl(name, ty)

    def _parse_touches_field(self):
        self.expect_name("touches_field")
        name = self.expect_name()
        self.expect_op(":")
        ty = self._parse_mixin_type()
        return TouchesFieldDecl(name, ty)

    def _parse_depends_method(self, kind):
        self.advance()  # depends_method / requires_method
        method = self.expect_name()
        self.expect_op(":")
        sig = self._parse_mixin_method_sig()
        return MethodDependencyDecl(method, sig, kind)

    def _parse_compose_from(self):
        self.expect_name("compose_from")
        names = [self.expect_name()]
        while self.accept_op(","):
            names.append(self.expect_name())
        return ComposeFromDecl(names)

    def _parse_conforms_to(self):
        self.expect_name("conforms_to")
        names = [self.expect_name()]
        while self.accept_op(","):
            names.append(self.expect_name())
        return ConformsToDecl(names)

    def _parse_mixin_type(self):
        name = self.expect_name()
        if self.at_op("["):
            self.advance()
            args = [self._parse_mixin_type()]
            while self.accept_op(","):
                args.append(self._parse_mixin_type())
            self.expect_op("]")
            return f"{name}[{', '.join(args)}]"
        return str(name)

    def _parse_mixin_param(self):
        name = self.expect_name()
        if self.accept_op(":"):
            return f"{name}: {self._parse_mixin_type()}"
        return str(name)

    def _parse_mixin_params(self):
        params = [self._parse_mixin_param()]
        while self.accept_op(","):
            params.append(self._parse_mixin_param())
        return ", ".join(params)

    def _parse_mixin_method_sig(self):
        self.expect_op("(")
        params = None
        if not self.at_op(")"):
            params = self._parse_mixin_params()
        self.expect_op(")")
        self.expect_op("->")
        ret = self._parse_mixin_type()
        if params is not None:
            return f"({params}) -> {ret}"
        return f"() -> {ret}"

    # -- concurrency --------------------------------------------------------
    def _parse_shared(self):
        self.expect_name("shared")
        name = self.expect_name()
        if self.at_name("protected_by"):
            self.advance()
            mutex = self._parse_mutex_expr_str()
            return SharedDecl(name, mutex)
        return SharedDecl(name, None)

    def _parse_mutex_expr_str(self):
        name = self.expect_name()
        if self.at_op("["):
            self.advance()
            index = self._parse_expr()
            self.expect_op("]")
            return f"{name}[{_csl_to_str(index)}]"
        return name

    def _parse_mutex_invariant(self):
        self.expect_name("mutex_invariant")
        mutex = self._parse_mutex_expr_str()
        self.expect_op(":")
        return MutexInvariant(mutex, self._parse_expr())

    def _parse_lock_order(self):
        self.expect_name("lock_order")
        names = [self._parse_mutex_expr_str()]
        while self.accept_op(","):
            names.append(self._parse_mutex_expr_str())
        return LockOrder(names)

    # ======================================================================
    # Expression grammar (mirror the Lark `expr` hierarchy + quantifier rules)
    # ======================================================================
    def _parse_expr(self):
        if self.at_bs("\\forall") or self.at_bs("\\exists") or self.at_bs("\\exist"):
            return self._parse_quantifier()
        return self._parse_implication()

    def _parse_quantifier(self):
        kw = self.advance().string
        is_exists = kw in ("\\exists", "\\exist")
        cls = Exists if is_exists else Forall
        var = self.expect_name()
        # `: TYPE` (typed binder)
        if self.accept_op(":"):
            ty = self.expect_name()
            if self.at_name("in"):
                self.advance()
                domain = self._parse_expr()
                self.expect_op(";")
                body = self._parse_expr()
                return cls(var, self._mk_in(var, domain, body, is_exists),
                           binder_type=ty)
            self.expect_op(";")
            return cls(var, self._parse_expr(), binder_type=ty)
        # `in DOMAIN` (untyped bounded)
        if self.at_name("in"):
            self.advance()
            domain = self._parse_expr()
            self.expect_op(";")
            body = self._parse_expr()
            return cls(var, self._mk_in(var, domain, body, is_exists))
        # `, NAME ...` (multi-binder or two-in)
        if self.at_op(","):
            names = [var]
            self.advance()
            names.append(self.expect_name())
            while self.accept_op(","):
                names.append(self.expect_name())
            # two-in: exactly 2 binders + `in`
            if len(names) == 2 and self.at_name("in"):
                self.advance()
                domain = self._parse_expr()
                self.expect_op(";")
                body = self._parse_expr()
                if not is_exists:
                    if not (isinstance(domain, DictView) and domain.kind == "items"):
                        raise _ContractSyntaxError(
                            "two-binder `\\forall k, v in …;` requires `d.items()`")
                    return ForallItems(names[0], names[1], domain.coll, body)
                raise _ContractSyntaxError("two-in quantifier is forall-only")
            self.expect_op(";")
            body = self._parse_expr()
            node = body
            for nm in reversed(names):
                node = cls(nm, node)
            return node
        # plain `; body`
        self.expect_op(";")
        return cls(var, self._parse_expr())

    @staticmethod
    def _mk_in(var, domain, body, is_exists):
        # quantification.md P3 desugar: ∀x in S; P ≡ ∀x; (x in S) ==> P ;
        # ∃x in S; P ≡ ∃x; (x in S) and P.
        op = "and" if is_exists else "==>"
        return BinOp(CSLIn(Var(var), domain), op, body)

    def _parse_impl_rhs(self):
        if self.at_bs("\\forall") or self.at_bs("\\exists") or self.at_bs("\\exist"):
            return self._parse_quantifier()
        return self._parse_logical_or()

    def _parse_or_rhs(self):
        if self.at_bs("\\forall") or self.at_bs("\\exists") or self.at_bs("\\exist"):
            return self._parse_quantifier()
        return self._parse_logical_and()

    def _parse_and_rhs(self):
        if self.at_bs("\\forall") or self.at_bs("\\exists") or self.at_bs("\\exist"):
            return self._parse_quantifier()
        return self._parse_equality()

    def _parse_implication(self):
        left = self._parse_logical_or()
        while self.at_op("==>", "<==>"):
            op = self.advance().string
            right = self._parse_impl_rhs()
            left = BinOp(left, op, right)
        return left

    def _parse_logical_or(self):
        left = self._parse_logical_and()
        while self.at_name("or"):
            self.advance()
            right = self._parse_or_rhs()
            left = BinOp(left, "or", right)
        return left

    def _parse_logical_and(self):
        left = self._parse_equality()
        while self.at_name("and"):
            self.advance()
            right = self._parse_and_rhs()
            left = BinOp(left, "and", right)
        return left

    def _parse_equality(self):
        left = self._parse_comparison()
        while self.at_op("==", "!="):
            op = self.advance().string
            left = BinOp(left, op, self._parse_comparison())
        return left

    def _parse_comparison(self):
        left = self._parse_membership()
        while self.at_op(">", "<", ">=", "<="):
            op = self.advance().string
            left = BinOp(left, op, self._parse_membership())
        return left

    def _parse_membership(self):
        left = self._parse_term()
        if self.at_name("in"):
            self.advance()
            return CSLIn(left, self._parse_term())
        if self.at_name("not") and self.peek().type == "NAME" and self.peek().string == "in":
            self.advance(); self.advance()
            return CSLNotIn(left, self._parse_term())
        return left

    def _parse_term(self):
        left = self._parse_factor()
        while self.at_op("+", "-"):
            op = self.advance().string
            left = BinOp(left, op, self._parse_factor())
        return left

    def _parse_factor(self):
        left = self._parse_unary()
        while self.at_op("*", "//", "/", "%"):
            op = self.advance().string
            left = BinOp(left, op, self._parse_unary())
        return left

    def _parse_unary(self):
        if self.at_name("not") or self.at_op("-", "+"):
            op = self.advance().string
            return UnaryOp(op, self._parse_unary())
        return self._parse_atom()

    # -- atom (the long rule list, in grammar order) -----------------------
    def _parse_atom(self):
        node = self._parse_atom_primary()
        if self.at_op("^"):
            self.advance()
            right = self._parse_atom()        # right-assoc (Lark LALR shifts)
            return StrConcatExpr(node, right)
        return node

    def _parse_atom_primary(self):
        t = self.cur()
        if t.type == "DECIMAL":
            self.advance(); return Number(float(t.string))
        if t.type == "NUMBER":
            self.advance(); return Number(int(t.string))
        if t.type == "STRING":
            self.advance(); return StringLiteral(t.string[1:-1])
        if t.type == "BSNAME":
            return self._parse_atom_bs()
        if t.type == "NAME":
            return self._parse_atom_name()
        if t.type == "OP" and t.string == "(":
            self.advance()
            e = self._parse_expr()
            self.expect_op(")")
            return e
        self._err("unexpected token in expression")

    def _parse_atom_name(self):
        name = self.advance().string
        if name == "True":  return CSLBool(True)
        if name == "False": return CSLBool(False)
        if name == "None":  return CSLNone()
        if name == "self":
            self.expect_op(".")
            field = self.expect_name()
            if self.at_op("["):
                self.advance()
                idx = self._parse_expr()
                self.expect_op("]")
                return FieldSubscript(field, idx)
            return FieldAccess("self", field)
        # general CNAME
        if self.at_op("."):
            self.advance()
            field2 = self.expect_name()
            if self.at_op("("):
                self.advance()
                self.expect_op(")")
                if field2 not in ("keys", "values", "items"):
                    raise PyCSLParseError(
                        f"unsupported method '.{field2}()' in a contract; only "
                        f".keys()/.values()/.items() are recognised (07-1311)")
                return DictView(name, field2)
            if self.at_op("["):
                self.advance()
                idx = self._parse_expr()
                self.expect_op("]")
                return GlobalFieldSubscript(name, field2, idx)
            return FieldAccess(name, field2)  # param_field_access
        if self.at_op("("):
            self.advance()
            if self.at_op(")"):
                self.advance()
                return CallExpr(name, [])
            args = self._parse_expr_list()
            self.expect_op(")")
            return CallExpr(name, args)
        if self.at_op("["):
            self.advance()
            e1 = self._parse_expr()
            if self.at_op(":"):
                self.advance()
                e2 = self._parse_expr()
                self.expect_op("]")
                return CSLSlice(name, e1, e2)
            self.expect_op("]")
            if self.at_op("["):
                self.advance()
                e2 = self._parse_expr()
                self.expect_op("]")
                # nested-list.md §8 EXTENSION: a THIRD+ index level (`a[i][j][k]`,
                # up to the type-recursion bound) wraps the depth-2 ChainedSubscript
                # in NestedSubscript nodes. Depth ≤2 stays ChainedSubscript
                # (byte-identical); each further `[eN]` nests one more Subscript.
                node = ChainedSubscript(name, e1, e2)
                while self.at_op("["):
                    self.advance()
                    eN = self._parse_expr()
                    self.expect_op("]")
                    node = NestedSubscript(node, eN)
                return node
            # cleared-array.md S2: `<name>[<idx>].<field>` — projection off a
            # subscripted element (the consumer of a projection-comprehension
            # content law).
            if self.at_op("."):
                self.advance()
                field = self.expect_name()
                return SubscriptFieldAccess(name, e1, field)
            return SubscriptAccess(name, e1)
        return Var(name)

    def _parse_atom_bs(self):
        name = self.advance().string
        if name == "\\result":
            if self.at_op("["):
                self.advance()
                idx = self._parse_expr()
                self.expect_op("]")
                # cleared-array.md S2: `\result[<idx>].<field>` projection.
                if self.at_op("."):
                    self.advance()
                    field = self.expect_name()
                    return SubscriptFieldAccess("\\result", idx, field)
                return SubscriptAccess("\\result", idx)
            if self.at_op("."):
                self.advance()
                field = self.expect_name()
                return FieldAccess("\\result", field)
            return Result()
        if name == "\\old":
            self.expect_op("(")
            e = self._parse_expr()
            self.expect_op(")")
            return Old(e)
        if name == "\\nothing":
            return Nothing()
        if name == "\\in_globals":
            self.expect_op("("); v = self.expect_name(); self.expect_op(")")
            return InGlobals(v)
        if name == "\\in_scope":
            self.expect_op("("); v = self.expect_name(); self.expect_op(")")
            return InScope(v)
        if name == "\\length":
            self.expect_op("(")
            if self.at_name("self"):
                self.advance(); self.expect_op(".")
                f = self.expect_name(); self.expect_op(")")
                return ArrayLength("self." + f)
            if self.at_bs("\\result"):
                self.advance(); self.expect_op(")")
                return ArrayLength("\\result")
            v = self.expect_name(); self.expect_op(")")
            return ArrayLength(v)
        if name == "\\valid":
            self.expect_op("(")
            base = self.expect_name(); self.expect_op(",")
            ln = self._parse_expr(); self.expect_op(")")
            return Valid(base, ln)
        if name == "\\separated":
            self.expect_op("(")
            b1 = self.expect_name(); self.expect_op(","); l1 = self._parse_expr()
            self.expect_op(","); b2 = self.expect_name(); self.expect_op(","); l2 = self._parse_expr()
            self.expect_op(")")
            return Separated(b1, l1, b2, l2)
        if name == "\\at":
            self.expect_op("(")
            e = self._parse_expr(); self.expect_op(","); lbl = self.expect_name()
            self.expect_op(")")
            return At(e, lbl)
        if name == "\\length2d":
            self.expect_op("(")
            b = self.expect_name(); self.expect_op(","); r = self._parse_expr()
            self.expect_op(","); c = self._parse_expr(); self.expect_op(")")
            return Length2D(b, r, c)
        if name == "\\valid2d":
            self.expect_op("(")
            b = self.expect_name(); self.expect_op(","); r = self._parse_expr()
            self.expect_op(","); c = self._parse_expr(); self.expect_op(")")
            return Valid2D(b, r, c)
        if name == "\\is_sorted":
            self.expect_op("(")
            b = self.expect_name(); self.expect_op(","); lo = self._parse_expr()
            self.expect_op(","); hi = self._parse_expr(); self.expect_op(")")
            return IsSorted(b, lo, hi)
        if name == "\\array_eq":
            self.expect_op("(")
            a = self._parse_expr(); self.expect_op(","); b = self._parse_expr()
            self.expect_op(")")
            return ArrayEq(a, b)
        if name == "\\permutation":
            self.expect_op("(")
            a = self._parse_expr(); self.expect_op(","); b = self._parse_expr()
            self.expect_op(")")
            return Permutation(a, b)
        if name == "\\sum":
            self.expect_op("(")
            b = self.expect_name(); self.expect_op(","); lo = self._parse_expr()
            self.expect_op(","); hi = self._parse_expr(); self.expect_op(")")
            return Sum(b, lo, hi)
        if name == "\\str_length":
            self.expect_op("(")
            e = self._parse_expr(); self.expect_op(")")
            return StrLengthExpr(e)
        if name == "\\str_sub":
            self.expect_op("(")
            s = self._parse_expr(); self.expect_op(","); lo = self._parse_expr()
            self.expect_op(","); hi = self._parse_expr(); self.expect_op(")")
            return StrSubExpr(s, lo, hi)
        if name == "\\mktuple":
            self.expect_op("(")
            elts = self._parse_expr_list(); self.expect_op(")")
            return MkTupleExpr(elts)
        if name == "\\fst":
            self.expect_op("("); e = self._parse_expr(); self.expect_op(")")
            return FstExpr(e)
        if name == "\\snd":
            self.expect_op("("); e = self._parse_expr(); self.expect_op(")")
            return SndExpr(e)
        if name == "\\proj":
            self.expect_op("(")
            e = self._parse_expr(); self.expect_op(","); idx = self._parse_expr()
            self.expect_op(")")
            return ProjExpr(e, idx)
        if name == "\\is_ctor":
            self.expect_op("(")
            v = self.expect_name(); self.expect_op(","); ctor = self.expect_name()
            self.expect_op(")")
            return CtorTest(v, ctor)
        if name == "\\payload":
            self.expect_op("(")
            v = self.expect_name(); self.expect_op(","); ctor = self.expect_name()
            if self.accept_op(","):
                idx_tok = self.cur()
                if idx_tok.type != "NUMBER":
                    self._err("expected NUMBER payload index")
                self.advance()
                self.expect_op(")")
                return CtorPayload(v, ctor, int(idx_tok.string))
            self.expect_op(")")
            return CtorPayload(v, ctor, 0)
        if name == "\\empty_map":
            return MapEmptyExpr()
        if name == "\\map_get":
            self.expect_op("(")
            d = self._parse_expr(); self.expect_op(","); k = self._parse_expr()
            self.expect_op(")")
            return MapGetExpr(d, k)
        if name == "\\map_set":
            self.expect_op("(")
            d = self._parse_expr(); self.expect_op(","); k = self._parse_expr()
            self.expect_op(","); v = self._parse_expr(); self.expect_op(")")
            return MapSetExpr(d, k, v)
        if name == "\\map_eq":
            self.expect_op("(")
            a = self._parse_expr(); self.expect_op(","); b = self._parse_expr()
            self.expect_op(")")
            return MapEqExpr(a, b)
        if name == "\\has_key":
            self.expect_op("(")
            d = self._parse_expr(); self.expect_op(","); k = self._parse_expr()
            self.expect_op(")")
            return HasKeyExpr(d, k)
        if name == "\\map_remove":
            self.expect_op("(")
            d = self._parse_expr(); self.expect_op(","); k = self._parse_expr()
            self.expect_op(")")
            return MapRemoveExpr(d, k)
        if name == "\\set_empty":
            return SetEmptyExpr()
        if name == "\\set_add":
            self.expect_op("(")
            s = self._parse_expr(); self.expect_op(","); e = self._parse_expr()
            self.expect_op(")")
            return SetAddExpr(s, e)
        if name == "\\set_remove":
            self.expect_op("(")
            s = self._parse_expr(); self.expect_op(","); e = self._parse_expr()
            self.expect_op(")")
            return SetRemoveExpr(s, e)
        if name == "\\set_mem":
            self.expect_op("(")
            e = self._parse_expr(); self.expect_op(","); s = self._parse_expr()
            self.expect_op(")")
            return SetMemExpr(e, s)
        if name == "\\set_union":
            self.expect_op("(")
            a = self._parse_expr(); self.expect_op(","); b = self._parse_expr()
            self.expect_op(")")
            return SetUnionExpr(a, b)
        if name == "\\set_inter":
            self.expect_op("(")
            a = self._parse_expr(); self.expect_op(","); b = self._parse_expr()
            self.expect_op(")")
            return SetInterExpr(a, b)
        if name == "\\set_diff":
            self.expect_op("(")
            a = self._parse_expr(); self.expect_op(","); b = self._parse_expr()
            self.expect_op(")")
            return SetDiffExpr(a, b)
        if name == "\\set_card":
            self.expect_op("(")
            s = self._parse_expr(); self.expect_op(","); lo = self._parse_expr()
            self.expect_op(","); hi = self._parse_expr(); self.expect_op(")")
            return SetCardExpr(s, lo, hi)
        if name == "\\set_subset":
            self.expect_op("(")
            a = self._parse_expr(); self.expect_op(","); b = self._parse_expr()
            self.expect_op(")")
            return SetSubsetExpr(a, b)
        if name == "\\set_eq":
            self.expect_op("(")
            a = self._parse_expr(); self.expect_op(","); b = self._parse_expr()
            self.expect_op(")")
            return SetEqExpr(a, b)
        if name == "\\nil":
            return NilExpr()
        if name == "\\cons":
            self.expect_op("(")
            h = self._parse_expr(); self.expect_op(","); tl = self._parse_expr()
            self.expect_op(")")
            return ConsExpr(h, tl)
        if name == "\\hd":
            self.expect_op("("); e = self._parse_expr(); self.expect_op(")")
            return HdExpr(e)
        if name == "\\tl":
            self.expect_op("("); e = self._parse_expr(); self.expect_op(")")
            return TlExpr(e)
        if name == "\\list_length":
            self.expect_op("("); e = self._parse_expr(); self.expect_op(")")
            return ListLengthExpr(e)
        if name == "\\nth":
            self.expect_op("(")
            l = self._parse_expr(); self.expect_op(","); i = self._parse_expr()
            self.expect_op(")")
            return NthExpr(l, i)
        if name == "\\mem":
            self.expect_op("(")
            e = self._parse_expr(); self.expect_op(","); l = self._parse_expr()
            self.expect_op(")")
            return MemExpr(e, l)
        if name == "\\append":
            self.expect_op("(")
            a = self._parse_expr(); self.expect_op(","); b = self._parse_expr()
            self.expect_op(")")
            return AppendExpr(a, b)
        if name == "\\copy":
            self.expect_op("(")
            v = self.expect_name(); self.expect_op(")")
            return GhostCopyExpr(v)
        if name == "\\copy_range":
            self.expect_op("(")
            v = self.expect_name(); self.expect_op(","); lo = self._parse_expr()
            self.expect_op(","); hi = self._parse_expr(); self.expect_op(")")
            return GhostCopyRangeExpr(v, lo, hi)
        if name == "\\make":
            self.expect_op("(")
            sz = self._parse_expr(); self.expect_op(","); d = self._parse_expr()
            self.expect_op(")")
            return GhostMakeExpr(sz, d)
        self._err(f"unrecognised backslash atom {name!r}")

    def _parse_expr_list(self):
        exprs = [self._parse_expr()]
        while self.accept_op(","):
            exprs.append(self._parse_expr())
        return exprs


# ---------------------------------------------------------
# 4. The Parser Interface
# ---------------------------------------------------------

class Module2_Parser:
    """Parses raw PyCSL string contracts into Contract AST objects.

    A pure-Python recursive-descent parser (`_ContractParser`) — no 3rd-party
    deps. Replaces the former Lark LALR engine; the 1:1 grammar→CSLNode map is
    preserved (differential-tested against the legacy engine in
    `bin/diff_parser.py`).
    """
    def __init__(self, use_rdp=None) -> None:
        # `use_rdp` is accepted (and ignored) for backward compatibility with
        # callers that passed it during the migration; the rdp engine is now
        # the only engine.
        pass

    def parse_contract(self, contract_str: str, line_number: int) -> CSLNode:
        try:
            return _ContractParser(contract_str).parse()
        except _ContractSyntaxError as e:
            raise PyCSLParseError(
                f"PyCSL Syntax Error around line {line_number}:\n{contract_str}\n{e}",
                line=line_number, stage="parse") from e

    def parse_node_contracts(self, raw_contracts: List[str], line_number: int) -> List[CSLNode]:
        parsed_nodes = []
        for contract_str in raw_contracts:
            parsed_nodes.append(self.parse_contract(contract_str, line_number))
        return parsed_nodes
