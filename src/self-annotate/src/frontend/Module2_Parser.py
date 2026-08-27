from __future__ import annotations
from dataclasses import dataclass
from typing import List, Union, Any, Optional, NoReturn
from errors import PyCSLParseError
""  # pycsl
@dataclass
class CSLNode:
    pass

class ContractWrapper(CSLNode):
    pass

class QuantifierNode(CSLNode):
    pass

class SingleExprNode(CSLNode):
    pass

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
    "An `act`'s guard clause (`given <expr>`). ACSL `assumes`, pre-state."
    expr: CSLNode

@dataclass
class Act(CSLNode):
    'A named guarded case: `act NAME:` with body clauses (Given/Requires/\n    Ensures/Assigns). Desugared in Module3 to ordinary requires/ensures.'
    name: str
    clauses: List[CSLNode]

@dataclass
class ForExpand(CSLNode):
    '`#@ for VAR in range(lo, hi):` (sugar-for-spec.md) — bounded macro-expansion.\n    Desugared in Module3 to ground requires/ensures: for each integer m in\n    [lo, hi), each body clause with VAR substituted by the literal m. lo/hi are\n    bound exprs (Number for v1); clauses are Requires/Ensures.'
    var: str
    lo: "ExprIR"
    hi: "ExprIR"
    clauses: List["ExprIR"]

@dataclass
class Complete(CSLNode):
    "`complete b1, b2, …` — the acts' guards cover every input."
    names: List[str]

@dataclass
class Disjoint(CSLNode):
    "`disjoint b1, b2, …` — at most one act's guard holds at a time."
    names: List[str]

@dataclass
class Preserves(CSLNode):
    '`#@ \\preserves` on a `\\trusted`/`\\abstract` method — opts the function into\n    the HAPPY trust boundary (meta.md Stage B, option C). The meta-pass synthesizes\n    and attaches the canonical region-preservation `ensures` for every module HAPPY\n    over a field this function does not legitimately write, so callers may assume the\n    region is untouched. A non-exempt trusted/abstract function WITHOUT this marker is\n    a hard error (theorem clause 2 has teeth).'

@dataclass
class HappyProperty(CSLNode):
    "A module-level HAPPY (High-level Assertion-Producing PYthon requirement):\n    `#@ happy NAME: region LO .. HI writes self.FIELD outside region except f, g`.\n    Declares one cross-cutting region-disjointness property; Module3's meta-pass\n    expands it into a per-site `#@ check` (a `CheckPoint`) at every write site of\n    `self.FIELD` in every method other than the exempt set. Desugars entirely to\n    the Stage-A check primitive — no new IR/backend. See `meta.md` Stage B."
    name: str
    field: str
    region_lo: "ExprIR"
    region_hi: "ExprIR"
    except_set: List[str]
    context: str = 'writing'
    protects: Optional[List[str]] = None
    param: Optional[str] = None
    target: Optional[str] = None
    formula: Optional[CSLNode] = None
    secret: Optional[List[str]] = None

@dataclass
class Footprint(CSLNode):
    "07-1143 R3: `#@ footprint NAME(arg)` — binds the parameter of the parametric HAPPY\n    `NAME` to one of the method's own arguments, so the meta-pass injects a per-site\n    region check parameterised by `arg` at each write of the protected path."
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
    # self-tcb-reduction spike (csl-ast-as-emit_ir): retyped left/right from `CSLNode`
    # to the forward-ref `"ExprIR"` so Module5's `_field_type_from_annotation_inst`
    # (via `_irnode_ann_name`) lowers the record fields to `emit_ir` instead of the
    # opaque-tag `int` fallback — the SAME recognized mechanism `_e(self, ir:
    # "ExprIR", ...)` already uses for params (expr_ghost_collections.py). Mirror-only
    # (self-annotate-mirror-check.sh compares signatures by (kind,name,n_params), not
    # annotations — corpus-inert by construction).
    left: "ExprIR"
    op: str
    right: "ExprIR"

@dataclass
class UnaryOp(SingleExprNode):
    op: str
    expr: 'ExprIR'

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
    # isinstance-on-CSL-class recognizer (self-tcb-reduction M5): retyped `expr` from
    # `CSLNode` to the forward-ref `"ExprIR"` so Module5's `_field_type_from_annotation_inst`
    # lowers the record field to `emit_ir` — letting `_csl_old` read `node.expr` as an
    # emit_ir node (the `isinstance(node.expr, CSLFieldAccess)` guard + `.object`/`.field`
    # projections). Mirror-only (self-annotate-mirror-check compares signatures by
    # (kind,name,n_params), not annotations — corpus-inert by construction), the BinOp
    # left/right precedent verbatim.
    expr: "ExprIR"

@dataclass
class Nothing(CSLNode):
    pass

@dataclass
class FieldAccess(CSLNode):
    object: str
    field: str

@dataclass
class FieldSubscript(CSLNode):
    'Represents `self.<field>[i]` — subscript of an instance ARRAY field in a\n    contract. Enables region-preservation postconditions such as\n    `\\forall i; (lo <= i and i < hi) ==> self.disk[i] == \\old(self.disk[i])`\n    on a `\\trusted`/`\\abstract` writer (meta.md Stage B, option C).'
    field: str
    index: 'ExprIR'

@dataclass
class GlobalFieldSubscript(CSLNode):
    "Represents `<global>.<field>[expr]` — subscript of a module-global record's\n    ARRAY field in a contract (spec-15 / gap-15 Wall B), e.g. `_filesystem.fd_inode[fd]`.\n    The sibling of `FieldSubscript` (`self.<field>[i]`) with a module-global instance\n    as the base instead of `self`. Lowers to `Subscript(Attribute(Var(obj), field), index)`,\n    riding the existing gap-10 global-field projection + spec-context `Array.get` machinery."
    obj: str
    field: str
    index: 'ExprIR'

@dataclass
class ClassInvariant(CSLNode):
    expr: CSLNode

@dataclass
class SubscriptAccess(CSLNode):
    array: str
    index: 'ExprIR'

@dataclass
class Forall(QuantifierNode):
    var: str
    # optional-field builder (monomorphic-option ADTs): `body` retyped `CSLNode`
    # -> `"ExprIR"` (record field `emit_ir`); `domain` retyped `Optional[CSLNode]`
    # -> `Optional["ExprIR"]` (record field `option emit_ir`). `binder_type` stays
    # `Optional[str]` -> `option string`. See live Module2_Parser.py.
    body: "ExprIR"
    binder_type: Optional[str] = None
    domain: Optional["ExprIR"] = None

@dataclass
class Exists(QuantifierNode):
    var: str
    body: "ExprIR"
    binder_type: Optional[str] = None
    domain: Optional["ExprIR"] = None

@dataclass
class ArrayLength(CSLNode):
    var: str

@dataclass
class InGlobals(CSLNode):
    '07-1839 P2: `\\in_globals(name)` — is `name` a statically-declared module-level\n    binding? Three-valued (sound lower bound): decided-true for a declared module name\n    (function / class / module global / constant), **unknown** otherwise (the world is\n    open — `import`/`exec` inject names), **never** decided-false. Resolved at emission\n    against the module-binding set.'
    name: str

@dataclass
class InScope(CSLNode):
    '07-1839 P3: `\\in_scope(name)` — is `name` a local/parameter bound at this point?\n    Three-valued via definite-assignment: decided-true if assigned on ALL paths (a formal\n    param, or a top-level assignment before any branching/return); decided-false if `name`\n    is neither a param nor assigned anywhere; **unknown** (conditionally assigned) otherwise.\n    A dynamic `exec`/`eval` havocs the binding set (decision C, P5).'
    name: str

@dataclass
class AssignsRegion(CSLNode):
    'Represents `arr[lo..hi]` inside an assigns clause (frame condition region).'
    base: str
    low: 'ExprIR'
    high: 'ExprIR'

@dataclass
class Valid(CSLNode):
    'Represents `\\valid(arr, n)` — memory region [arr, arr+n) is allocated.'
    base: str
    length: 'ExprIR'

@dataclass
class Separated(CSLNode):
    "Represents `\\separated(a, na, b, nb)` — regions [a,a+na) and [b,b+nb) don't overlap."
    base1: str
    length1: 'ExprIR'
    base2: str
    length2: 'ExprIR'

@dataclass
class Label(CSLNode):
    'Represents a `#@ label L` program point annotation.'
    name: str

@dataclass
class CheckPoint(CSLNode):
    'A statement-level proof obligation attached to the following statement:\n    `#@ assert P` (prove-and-assume — P becomes a hypothesis afterward) or\n    `#@ check P` (prove-and-discard). Distinct from the Python `assert` statement,\n    which is a runtime check the prover ignores.'
    kind: str
    expr: CSLNode
    origin: str = None

@dataclass
class At(CSLNode):
    'Represents `\\at(expr, L)` — value of expr at program point L.'
    expr: 'ExprIR'
    label: str

@dataclass
class Length2D(CSLNode):
    'Represents `\\length2d(arr, m, n)` — arr has m rows each of length n.'
    base: str
    rows: 'ExprIR'
    cols: 'ExprIR'

@dataclass
class Valid2D(CSLNode):
    'Represents `\\valid2d(arr, i, j)` — (i,j) is a valid 2D index into arr.'
    base: str
    row: 'ExprIR'
    col: 'ExprIR'

@dataclass
class FunctionVariant(CSLNode):
    'Represents `#@ \\variant <expr>` or `#@ \\variant (<expr>, <ordering>)`.'
    expr: 'ExprIR'
    ordering: Optional[str] = None

@dataclass
class Diverges(CSLNode):
    'Represents `#@ \\diverges` — function may not terminate.'

@dataclass
class NoInline(CSLNode):
    "Represents `#@ no_inline` (no-inline.md) — a modular-verification boundary: the method's\n    body is verified once against its contract, and callers reuse the contract (a contract-call)\n    instead of splicing the inlined body. Avoids re-proving a large body in every caller's\n    context (the os `sys_write` inlining blow-up)."

@dataclass
class SiblingConcrete(CSLNode):
    "Represents `#@ sibling_concrete` (allocator-frame plan §2.7) — OPT-IN: an intra-class\n    `self.<m>()` call to THIS method is lowered to a CONCRETE call `(<class>__<m> self args)`\n    (so the caller gets the real method's full contract AND its type/class-invariant guarantee\n    on the post-state), instead of the default abstract `val` stub. Use ONLY on cheap-to-\n    maintain leaf writers whose guarantee the caller can absorb as an atom (e.g. the os bitmap\n    leaves `_set_bitmap`/`_poke`). Decoupled from `no_inline`: it affects sibling-call lowering\n    only, NOT whether the body is inlined into wrappers — so it cannot perturb a separate\n    importer gate. Default off → every existing self-call keeps its abstract-stub lowering."

@dataclass
class VerifyModule(CSLNode):
    "Represents `#@ verify_module <name>` (module-emission.md) — OPT-IN axiom-isolation:\n    the method is emitted into its OWN top-level Why3 `module <name>` (re-declaring the shared\n    infra — record type, val-functions, predicates, witness/class-invariant axioms, abstract\n    stubs) so that ONLY the `#@ proof` axioms cited by the functions in that module are in\n    scope for its goals. Functions sharing the same `<name>` are co-emitted into one module.\n    Cross-module `self.<m>(...)` calls (a sibling in a DIFFERENT verify_module / the flat\n    default module) are lowered to a bodyless `val` carrying the sibling's proven contract,\n    discharged by the Track-B narrowing VC in the sibling's owning module — a PROVEN interface,\n    never an assumed `val` / new `\\trusted` / new axiom. Resolves the read+write axiom\n    co-residence OOM that blocks `_dir_lookup` (read `field_to_str`/`dir_scan_*` axioms out of\n    scope for the write helpers' per-byte goals, and vice-versa). Default (untagged) → the\n    single flat `module PyCSL_Program` is emitted unchanged → corpus byte-identical."
    name: str

@dataclass
class PropagateFrame(CSLNode):
    "Represents `#@ propagate_frame` (os-roadmap M4) — OPT-IN: THIS method's QUANTIFIED\n    self-field FRAME ensures (`\\forall k. … == \\old(…)`) are propagated onto its `#@ no_inline`\n    boundary stub, each pinned with a specific function-application trigger. Use ONLY on a mutator\n    whose callers genuinely need the frame and are NOT term-rich enough to E-match-explode under it\n    (e.g. the os `_zero_entry`, called only by unlink/rmdir/rename). Default off → the quantified\n    frame is dropped at the boundary (the non-quantified write-posts still propagate via the\n    field_param_post map). NOT for broad mutators like `_write_entry` whose frame poisons rich\n    callers (link/symlink) — see 14-string-field-codec-plan.md §2.9."

@dataclass
class FreshGlobals(CSLNode):
    "Represents `#@ fresh_globals` (fresh-globals.md) — OPT-IN, CONFINED: at THIS\n    function's body entry, re-establish each module-global singleton's CONSTRUCTOR\n    POST-STATE (the class `__init__`'s `#@ ensures`, `self` -> the global) as an\n    ASSUMED fact. Models the execution-model convention that a STANDALONE,\n    internals-blind formal-test DRIVER runs on a freshly-imported module global\n    (import ran `__init__`, so the constructor post-state holds at entry) — instead\n    of Why3's default treatment of a shared mutable global as HAVOC'd at every\n    importer-function entry.\n\n    SOUNDNESS (Module4-enforced confinement): sound ONLY on an INDEPENDENT entry\n    point that is never called by another verified function and never composed after\n    a prior driver mutated the shared global — otherwise a callee would falsely\n    assume the all-fresh state against an already-mutated global. Module4 REJECTS it\n    on `self`-methods, library functions, and any function that is a callee of\n    another verified function in the same unit. The assumed fact is NOT an arbitrary\n    literal: it is the constructor's `#@ ensures`, which `_emit_module_globals`\n    re-checks as a GOAL against the global's literal initializer (so the fact is\n    PROVEN of the freshly constructed global). Replaces the FALSE unconditioned\n    fd-resolution-fidelity no-ENFILE body theorem with a sound, confined,\n    constructor-backed entry fact."

@dataclass
class Trusted(CSLNode):
    'Represents `#@ \\trusted` — function body is not verified.\n    Optional `reviewer` identifies who is accountable for the trust assumption.'
    reviewer: str = ''

@dataclass
class Abstract(CSLNode):
    "Represents `#@ \\abstract` — the function is emitted as a bodyless WhyML\n    `val` defined SOLELY by its contract (+ any cited `#@ proof` axioms). Unlike\n    `\\trusted` (a Python body that is present but unchecked), an `\\abstract`\n    declaration asserts there is no meaningful body to check — the contract IS\n    the definition. Sound: an uninterpreted `val` constrains callers only by its\n    spec. Used for irreducibly-opaque operations (e.g. `ast.literal_eval`, which\n    IS Python's parser) where the honest model is `val + ensures/raises + cited\n    axiom`, not an unverified body. Does NOT count as `\\trusted`."

@dataclass
class Lemma(CSLNode):
    "Represents `#@ lemma` (lemma.md) — the function is a PROVED logical fact.\n    It lowers to a WhyML `let [rec] lemma name (params) : unit requires {H}\n    ensures {C} [variant {m}] = <proof body>`: Why3 verifies the body against the\n    contract, then makes `forall params. H -> C` available to later goals. Unlike\n    `\\trusted` (assumed) and `#@ proof` (proved elsewhere, an axiom), a lemma\n    introduces NO axiom that isn't itself checked. A recursive lemma's self-calls\n    are the induction hypotheses; it MUST carry `#@ \\variant` (soundness)."

@dataclass
class Uses(CSLNode):
    "Represents `#@ uses <lemma>` (scc2.md) — a NON-instantiating citation that the\n    function's verification relies on lemma `<lemma>`'s general fact. Its only effect\n    is an ordering edge (the cited lemma is emitted before this function, so its\n    `forall …` fact is in scope to discharge e.g. a `\\forall`-over-a-recursive-\n    datatype goal). It emits no WhyML of its own; it is consumed by the SCC edge\n    collector (`scc.py`)."
    lemma: str

@dataclass
class InterfaceClause(CSLNode):
    "Represents `#@ interface ensures/requires/assigns <…>` (b-spec Track B) — the NARROW\n    *interface* contract importers/callers see by default, distinct from the rich *definition*\n    contract (the plain `#@ requires/ensures/assigns`) verified against the body. Opacity: the\n    definition's extra facts are hidden, revealed only via `#@ reveal`. Absent ⇒ interface =\n    definition (transparent — all existing code byte-identical). `kind` ∈ {ensures, requires,\n    assigns}; `payload` is the corresponding Ensures/Requires/Assigns node."
    kind: str
    payload: Any

@dataclass
class Reveal(CSLNode):
    "Represents `#@ reveal <fn>` (b-spec Track B) — this caller opts into `<fn>`'s rich\n    DEFINITION contract at this site (the definition facts are otherwise hidden behind the\n    interface). Within the owning unit it is a no-op (the definition is the visible `let`);\n    across modules it cites the exported definition-fact (v2)."
    fn: str

@dataclass
class CSLBool(CSLNode):
    'Represents True/False literals in contract expressions.'
    value: bool

@dataclass
class CSLNone(CSLNode):
    'Represents None literal in contract expressions.'

@dataclass
class CSLIn(CSLNode):
    'Represents `x in arr` membership test in contracts.'
    element: CSLNode
    collection: CSLNode

@dataclass
class CSLNotIn(CSLNode):
    'Represents `x not in arr` negated membership test in contracts.'
    element: 'ExprIR'
    collection: 'ExprIR'

@dataclass
class DictView(CSLNode):
    '07-1311 Q3: a dict view in a quantifier domain — `d.keys()` / `d.values()` /\n    `d.items()`. Only meaningful as the collection of a bounded quantifier\n    (`\\forall v in d.values(); …`); Module5\'s `_csl_in` desugars it onto the map\n    model (`map int (option int)`). `kind` ∈ {"keys","values","items"}.'
    coll: str
    kind: str

@dataclass
class ForallItems(QuantifierNode):
    '07-1311 Q3: two-binder `\\forall k, v in d.items(); P(k, v)` — binds the key and\n    value of every present entry. Lowers to\n    `forall k. match Map.get d k with Some v -> P | None -> true end`.'
    key: str
    val: str
    coll: str
    body: 'ExprIR'

@dataclass
class CSLSlice(CSLNode):
    'Represents `arr[lo:hi]` slice notation in contracts.'
    collection: str
    low: 'ExprIR'
    high: 'ExprIR'

@dataclass
class ChainedSubscript(CSLNode):
    'Represents `arr[i][j]` chained subscript access (2D array element).'
    array: str
    index1: 'ExprIR'
    index2: 'ExprIR'

@dataclass
class CallExpr(CSLNode):
    'Represents a function call in a contract expression.'
    func: str
    # variadic content-law comprehension (FABLE-sanctioned): `args` is a list of
    # already-lowered ExprIR children (the emitter's `_csl_call_expr` maps
    # `self._csl_to_ir` over them). Retyped `List[CSLNode]` -> `List["ExprIR"]` so the
    # imported record field is `array emit_ir` (value_type "emit_ir", the
    # `_m5_get_list_elem_type` forward-ref path — same as `MkTupleExpr.elts`), letting
    # the emit_ir dispatcher comprehension `[self._csl_to_ir(a) for a in node.args]`
    # lower with both a length law and a per-index content law over the shared
    # `emit_ir_disp__csl_to_ir`, then build the `IrCallN string irlist` ctor. Signature-
    # only retype (string forward-ref, no runtime effect); the parser still fills `args`
    # with CSL AST nodes, which the emitter lowers.
    args: List["ExprIR"]

@dataclass
class IsSorted(CSLNode):
    'Represents `\\is_sorted(a, lo, hi)` — array is sorted in range.'
    base: str
    lo: 'ExprIR'
    hi: 'ExprIR'

@dataclass
class ArrayEq(CSLNode):
    'Represents `\\array_eq(a, b)` — two arrays have equal length and\n    equal elements at every index (extensional content equality).'
    left: 'ExprIR'
    right: 'ExprIR'

@dataclass
class Permutation(CSLNode):
    'Represents `\\permutation(a, b)` — `a` is a permutation of `b` (same\n    multiset of elements). Unlike `\\array_eq` it does NOT unfold to a\n    first-order formula; it lowers to an uninterpreted Why3 `predicate permut`\n    that a proof-assistant-imported axiom constrains (no-more-int A2b Gap 1).'
    left: 'ExprIR'
    right: 'ExprIR'

@dataclass
class Sum(CSLNode):
    'Represents `\\sum(a, lo, hi)` — sum of array elements in range.'
    base: str
    lo: 'ExprIR'
    hi: 'ExprIR'

@dataclass
class GhostAssignDecl(CSLNode):
    'Represents `ghost var = expr` or `ghost var += expr` in contracts.'
    target: str
    value: CSLNode
    op: str
    declared_type: str = 'int'

@dataclass
class MkTupleExpr(CSLNode):
    '\\mktuple(a, b[, c[, d]]) — construct a ghost tuple.'
    # variadic content-law comprehension (FABLE-sanctioned): `elts` is a list of
    # already-lowered ExprIR children (the emitter's `_csl_mktuple` maps
    # `self._csl_to_ir` over them). Retyped `List[CSLNode]` -> `List["ExprIR"]` so
    # the imported record field is `array emit_ir` (value_type "emit_ir", the
    # `_m5_get_list_elem_type` forward-ref path), letting the emit_ir dispatcher
    # comprehension `[self._csl_to_ir(e) for e in node.elts]` lower with both a
    # length law and a per-index content law over the shared `emit_ir_disp__csl_to_ir`.
    # Signature-only retype (matches the `_csl_to_ir` param's own `"ExprIR"`); the
    # parser still fills `elts` with CSL AST nodes, which the emitter lowers.
    elts: List["ExprIR"]

@dataclass
class FstExpr(CSLNode):
    '\\fst(t) — first component of a ghost tuple.'
    tuple_expr: 'ExprIR'

@dataclass
class SndExpr(CSLNode):
    '\\snd(t) — second component of a ghost tuple.'
    tuple_expr: 'ExprIR'

@dataclass
class ProjExpr(CSLNode):
    '\\proj(t, i) — ith component of a ghost tuple (i must be a literal).'
    tuple_expr: 'ExprIR'
    index: CSLNode

@dataclass
class CtorTest(CSLNode):
    '\\is_ctor(x, Ctor) — true iff `x` was built with constructor `Ctor`\n    (A5b: a datatype discriminator usable in a contract).'
    var: str
    ctor: str

@dataclass
class CtorPayload(CSLNode):
    '\\payload(x, Ctor[, i]) — the i-th payload of `x` viewed as constructor\n    `Ctor` (A5b: a datatype projector usable in a contract; `i` defaults to 0).'
    var: str
    ctor: str
    index: int = 0

@dataclass
class StrConcatExpr(CSLNode):
    's ^ t — string concatenation in ghost / contract context.'
    left: 'ExprIR'
    right: 'ExprIR'

@dataclass
class StrLengthExpr(CSLNode):
    '\\str_length(s) — length of a ghost string variable.'
    string: 'ExprIR'

@dataclass
class StrSubExpr(CSLNode):
    '\\str_sub(s, lo, hi) — substring of ghost string s from lo to hi.'
    string: 'ExprIR'
    lo: 'ExprIR'
    hi: 'ExprIR'

@dataclass
class GhostCopyExpr(CSLNode):
    '\\copy(arr) — snapshot of an array into a ghost array.'
    arr: str

@dataclass
class GhostCopyRangeExpr(CSLNode):
    '\\copy_range(arr, lo, hi) — bounded snapshot: arr[lo..hi-1] into a new ghost array.'
    arr: str
    lo: 'ExprIR'
    hi: 'ExprIR'

@dataclass
class GhostMakeExpr(CSLNode):
    '\\make(n, v) — create a ghost array of length n filled with v.'
    size: 'ExprIR'
    default: 'ExprIR'

@dataclass
class MapEmptyExpr(CSLNode):
    '\\empty_map — an empty ghost dictionary (total map defaulting to 0).'

@dataclass
class MapGetExpr(CSLNode):
    '\\map_get(d, k) — look up key k in ghost dict d.'
    dict_expr: 'ExprIR'
    key: 'ExprIR'

@dataclass
class MapSetExpr(CSLNode):
    '\\map_set(d, k, v) — return ghost dict d with d[k] := v.'
    dict_expr: 'ExprIR'
    key: 'ExprIR'
    value: 'ExprIR'

@dataclass
class MapEqExpr(CSLNode):
    '\\map_eq(d1, d2) — extensional equality of two ghost dicts.'
    left: 'ExprIR'
    right: 'ExprIR'

@dataclass
class HasKeyExpr(CSLNode):
    '\\has_key(d, k) — true iff ghost dict d has a present (non-None) value at key k.'
    dict_expr: 'ExprIR'
    key: 'ExprIR'

@dataclass
class MapRemoveExpr(CSLNode):
    '\\map_remove(d, k) — return ghost dict d with key k removed (set to None/absent).'
    dict_expr: 'ExprIR'
    key: 'ExprIR'

@dataclass
class SetEmptyExpr(CSLNode):
    '\\set_empty — the empty ghost set.'

@dataclass
class SetAddExpr(CSLNode):
    '\\set_add(s, x) — ghost set with x added.'
    set_expr: 'ExprIR'
    elem: 'ExprIR'

@dataclass
class SetRemoveExpr(CSLNode):
    '\\set_remove(s, x) — ghost set with x removed.'
    set_expr: 'ExprIR'
    elem: 'ExprIR'

@dataclass
class SetMemExpr(CSLNode):
    '\\set_mem(x, s) — x is a member of ghost set s.'
    elem: 'ExprIR'
    set_expr: 'ExprIR'

@dataclass
class SetUnionExpr(CSLNode):
    '\\set_union(s1, s2) — union of two ghost sets.'
    left: 'ExprIR'
    right: 'ExprIR'

@dataclass
class SetInterExpr(CSLNode):
    '\\set_inter(s1, s2) — intersection of two ghost sets.'
    left: 'ExprIR'
    right: 'ExprIR'

@dataclass
class SetDiffExpr(CSLNode):
    '\\set_diff(s1, s2) — set difference s1 \\ s2.'
    left: 'ExprIR'
    right: 'ExprIR'

@dataclass
class SetCardExpr(CSLNode):
    '\\set_card(s, lo, hi) — cardinality of s restricted to [lo, hi).'
    set_expr: 'ExprIR'
    lo: 'ExprIR'
    hi: 'ExprIR'

@dataclass
class SetSubsetExpr(CSLNode):
    '\\set_subset(s1, s2) — s1 is a subset of s2.'
    left: 'ExprIR'
    right: 'ExprIR'

@dataclass
class SetEqExpr(CSLNode):
    '\\set_eq(s1, s2) — extensional equality of two ghost sets.'
    left: 'ExprIR'
    right: 'ExprIR'

@dataclass
class NilExpr(CSLNode):
    '\\nil — the empty ghost list.'

@dataclass
class ConsExpr(CSLNode):
    '\\cons(x, l) — prepend x to ghost list l.'
    head: 'ExprIR'
    tail: 'ExprIR'

@dataclass
class HdExpr(CSLNode):
    '\\hd(l) — head of ghost list l (requires l non-empty).'
    list_expr: 'ExprIR'

@dataclass
class TlExpr(CSLNode):
    '\\tl(l) — tail of ghost list l (requires l non-empty).'
    list_expr: 'ExprIR'

@dataclass
class ListLengthExpr(CSLNode):
    '\\list_length(l) — length of ghost list l.'
    list_expr: 'ExprIR'

@dataclass
class NthExpr(CSLNode):
    '\\nth(l, i) — ith element of ghost list l (requires 0 <= i < length).'
    list_expr: 'ExprIR'
    index: 'ExprIR'

@dataclass
class MemExpr(CSLNode):
    '\\mem(x, l) — x appears in ghost list l.'
    elem: 'ExprIR'
    list_expr: 'ExprIR'

@dataclass
class AppendExpr(CSLNode):
    '\\append(l1, l2) — concatenation of two ghost lists.'
    left: 'ExprIR'
    right: 'ExprIR'

@dataclass
class GhostArraySetDecl(CSLNode):
    'ghost arr[i] = expr — in-place assignment to a ghost array element.'
    target: str
    index: CSLNode
    value: CSLNode

@dataclass
class RaisesDecl(CSLNode):
    'Represents `raises ExcType when condition` in contracts.'
    exc_type: str
    condition: CSLNode

@dataclass
class NoExceptionDecl(CSLNode):
    'Represents `no_exception E1, E2, ...` or `no_exception \\all`.\n\n    Turns implicit Python exceptions into proof obligations: every IR\n    operation that could raise one of `exceptions` must be preceded by an\n    assertion discharging its trigger condition (see exception_model.py).\n\n    `all_form=True` is the wildcard form; `exceptions` is empty in that case\n    and the function context expands to the full Phase 1 exception set at\n    transpilation time.\n    '
    exceptions: List[str]
    all_form: bool = False

@dataclass
class AllowFinalizerDecl(CSLNode):
    "Represents `#@ allow_finalizer` — opts a class with `__del__` out\n    of UB-7.5's hard rejection. Place on the `class` line.\n    "

@dataclass
class AllowIterationMutationDecl(CSLNode):
    "Represents `#@ allow_iteration_mutation` — opts a `for` loop out\n    of UB-7.1's hard rejection. Place on the `for` line.\n    "

@dataclass
class BoundedIntDecl(CSLNode):
    'Represents `assumes bounded_int(N)` in contracts.'
    size: int

@dataclass
class ProofDecl(CSLNode):
    'Represents `#@ proof <prover> <qualname>` — cites a Rocq or\n    Lean theorem as the justification for a Why3 axiom in the WhyML\n    preamble.\n\n    Emits an `axiom <name> : <body>` line in the transpiled WhyML.\n    The body is looked up from a per-test manifest or hand-curated\n    mapping during the MVP phase, and from `proof2why3` extraction\n    once that pipeline exists (see docs/cross-validated-spec-sources.md).\n    '
    prover: str
    qualname: str

@dataclass
class SharedDecl(CSLNode):
    'Represents `shared VAR protected_by MUTEX` or `shared VAR` (unprotected).'
    variable: str
    mutex: Optional[str] = None

@dataclass
class DatatypeDecl(CSLNode):
    'Represents `#@ datatype Name = C1 | C2(int) | C3(int, int)` — an algebraic\n    (sum) type. `variants` is a list of (constructor_name, [payload_type_names]).\n    `type_params` (A5d) holds the declared type parameters of a *parametric*\n    datatype `#@ datatype Option[T] = …`; empty for a monomorphic one.'
    name: str
    variants: list
    type_params: list = None

@dataclass
class InductiveDecl(CSLNode):
    'Represents an `#@ inductive p(params):` least-fixpoint relation (inductive.md).\n    `signature` is the rendered param string `"(n: int)"`; `rules` is a list of\n    `(rule_name, horn_clause_expr)` parsed inline from the indentation block. `members`\n    (inductive.md P2) holds any `with q(params): …` mutually-inductive group members as\n    `(name, signature, rules)` tuples. Lowers to a Why3 `inductive p (params) = | Rule :\n    clause … [with q … = | …]` (no closing `end`).'
    name: str
    signature: str
    rules: list = None
    members: list = None

@dataclass
class MixinDecl(CSLNode):
    'Represents `#@ mixin` — marks a class as a composable mixin (a trait whose\n    provided methods are verified once against its declared dependencies, then\n    flattened into a composer via `#@ compose_from`).'

@dataclass
class ProvidesDecl(CSLNode):
    "Represents `#@ provides <m>` — the following method is a provided operation\n    of this mixin (a candidate provider for a sibling's `depends_method`)."
    method: str

@dataclass
class SharedStateDecl(CSLNode):
    "Represents `#@ shared_state <name>: <type>` (D1) — a field declared as\n    deliberately-shared facade state. Multiple mixins may read/write it; it is NOT\n    an owned-field conflict. A write must still appear in the method's `assigns`."
    name: str
    type_str: str

@dataclass
class TouchesFieldDecl(CSLNode):
    'Represents `#@ touches_field <name>: <type>` — an OWNED field of this mixin.\n    At most one mixin may own a given name (two owners → conflict → Tier 2).'
    name: str
    type_str: str

@dataclass
class MethodDependencyDecl(CSLNode):
    'Represents `#@ depends_method <m>: <sig>` (D2, a CONCRETE dependency on a\n    sibling/core provider) or `#@ requires_method <m>: <sig>` (an ABSTRACT operation\n    the composing class must supply). Both are modelled as an abstract `val` against\n    which the mixin is verified once; composition discharges provider ⊑ declared.'
    method: str
    sig: str
    kind: str

@dataclass
class ComposeFromDecl(CSLNode):
    'Represents `#@ compose_from M1, M2, …` — marks a class as composing the named\n    mixins. Synthesizes the composition obligations (unique provider per dependency,\n    provider-refines-dependency, init-hook) checked by the Module4 pass (S2).'
    mixins: list

@dataclass
class ConformsToDecl(CSLNode):
    "Represents `#@ conforms_to P1, P2, …` (typing-engagement ty2 / PEP 544) — marks a\n    class as conforming to the named Protocols. Synthesizes per-method contract-refinement\n    `overrides` entries (P2/P4): for each member `m` of each named Protocol `P` that the\n    class provides, an `(C__m, P__m)` pair is recorded so `--check-behavioral-subtyping`\n    emits the refinement goal `((pre_P -> pre_C) /\\ (post_C -> post_P))`. This is the\n    static-plane conformance VC — it must NOT be discharged by any runtime\n    `isinstance`/`hasattr` presence check (GT7 no-blend, D1). PEP 544 conformance is\n    structural/implicit; PyCSL's TY2 scope requires the explicit directive (divergence-by-\n    strictness) so conformance is a discharged per-method VC, not a whole-program search."
    protocols: list

@dataclass
class ThreadEntry(CSLNode):
    'Represents `thread_entry` — marks a function as a concurrent thread entry point.'

@dataclass
class Acquires(CSLNode):
    'Represents `acquires MUTEX` — marks a mutex acquire point.'
    mutex: str

@dataclass
class Releases(CSLNode):
    'Represents `releases MUTEX` — marks a mutex release point.'
    mutex: str

@dataclass
class CriticalSection(CSLNode):
    'Represents `critical MUTEX` — marks a `with` block as a critical section.'
    mutex: str

@dataclass
class MutexInvariant(CSLNode):
    'Represents `mutex_invariant MUTEX: EXPR` — invariant held when mutex is unlocked.'
    mutex: str
    expr: CSLNode

@dataclass
class LockOrder(CSLNode):
    'Represents `lock_order M1, M2, ...` — total order on mutex acquisition to prevent deadlock.'
    order: List[str]

#@ requires True
#@ ensures True
#@ assigns \nothing
def _csl_to_str(node: "ExprIR") -> str:
    if isinstance(node, Var):
        return node.name
    if isinstance(node, Number):
        return str(int(node.value))
    if isinstance(node, BinOp):
        return f"{_csl_to_str(node.left)}{node.op}{_csl_to_str(node.right)}"
    return "?"

import os as _os
import re as _re
class _ContractSyntaxError(Exception):
    'Internal syntax error raised by `_ContractParser`; converted to\n    `PyCSLParseError` at the `Module2_Parser` boundary.'

# Mirror-only infra shim (see bin/self-annotate-mirror-check.sh MIRROR_ONLY): marks the
# token-cursor `_ContractParser` as a stateful record so its `toks`/`i` fields lower to
# `mutable toks: array _tok` / `mutable i: int`.
def mutable_state(cls):
    return cls


class _Tok:
    __slots__ = ('type', 'string', 'start')
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self, type_, string, start):
        self.type: str = type_
        self.string: str = string
        self.start: int = start

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __repr__(self):
        return f"_Tok({self.type}, {self.string!r})"


_OP_ALTERNATIVES = ['==>', '<==>', '//', '..', '+=', '-=', '*=', '->', '==', '!=', '>=', '<=', '+', '-', '*', '/', '%', '^', ':', ',', ';', '(', ')', '[', ']', '=', '.', '<', '>', '|']
_TOKEN_RE = _re.compile(_re.escape('|') and '(?xs)\n    (?P<WS>\\s+)\n  | (?P<DECIMAL>\\d+\\.\\d+)\n  | (?P<NUMBER>\\d+)\n  | (?P<STRING>"(?:[^"\\\\]|\\\\.)*")\n  | (?P<BSNAME>\\\\[A-Za-z_][A-Za-z0-9_]*)\n  | (?P<NAME>[A-Za-z_][A-Za-z0-9_]*)\n  | (?P<OP>' + '|'.join((_re.escape(o) for o in _OP_ALTERNATIVES)) + ')\n')
#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def _lex_contract(source: str):
    pass

_IMPL_OPS = ('==>', '<==>')
_EQ_OPS = ('==', '!=')
_COMP_OPS = ('>', '<', '>=', '<=')
_ADD_OPS = ('+', '-')
_MUL_OPS = ('*', '//', '/', '%')
#@ class invariant 0 <= self.i
#@ class invariant self.i < \length(self.toks)
#@ class invariant \length(self.toks) >= 1
# The lexer's EOF SENTINEL, read straight off `_lex_contract`: its last act is
# `toks.append(_Tok("EOF", "", n))`, so the final token is ALWAYS EOF. It is the
# property that makes the cursor's `while self.at_op(...)` loops TERMINATE — the
# sentinel is not an OP and not a NAME, so a true loop guard forces
# `self.i < \length(self.toks) - 1`, hence `advance` really increments and the
# variant `\length(self.toks) - self.i` strictly decreases. Not a narrowing: the
# live lexer establishes it unconditionally on every path that returns.
#@ class invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
@mutable_state
class _ContractParser:
    'Recursive-descent parser over `_Tok` producing `CSLNode` trees.\n\n    One method per grammar rule; each builds the SAME `CSLNode` the\n    corresponding `PyCSLTransformer` method built. Dispatch is on the leading\n    keyword / backslash-name of the contract.\n    '
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self, source: str):
        toks, raw = _lex_contract(source)
        self.toks: List[_Tok] = toks
        self.i: int = 0

    #@ requires True
    #@ ensures \result == self.toks[self.i]
    #@ assigns \nothing
    def cur(self) -> _Tok:
        return self.toks[self.i]

    # `k >= 0` is a genuine PARTIALITY boundary, read off the live body: the in-range
    # read `self.toks[j]` is guarded ONLY from above (`j < len(self.toks)`), so a
    # negative `k` makes `j` negative and Python silently reads from the END of the
    # list — a different token than "the one `k` ahead". The live call site passes the
    # default `1`. Not a convenience narrowing.
    #@ requires k >= 0
    #@ ensures True
    #@ assigns \nothing
    def peek(self, k=1) -> _Tok:
        j = self.i + k
        return self.toks[j] if j < len(self.toks) else self.toks[-1]

    #@ requires True
    #@ ensures \old(self.i) < \length(self.toks) - 1 ==> self.i == \old(self.i) + 1
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def advance(self) -> _Tok:
        t = self.toks[self.i]
        if self.i < len(self.toks) - 1:
            self.i += 1
        return t

    #@ requires True
    #@ ensures \result != False ==> self.toks[self.i].py_type == "OP"
    #@ assigns \nothing
    def at_op(self, *vals: str) -> bool:
        t = self.cur()
        return t.type == 'OP' and (not vals or t.string in vals)

    #@ requires True
    #@ ensures \result != False ==> self.toks[self.i].py_type == "NAME"
    #@ assigns \nothing
    def at_name(self, *vals: str) -> bool:
        t = self.cur()
        return t.type == 'NAME' and (not vals or t.string in vals)

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def at_bs(self, *vals: str) -> bool:
        t = self.cur()
        return t.type == 'BSNAME' and (not vals or t.string in vals)

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def at_eof(self) -> bool:
        return self.cur().type == 'EOF'

    #@ requires True
    #@ ensures \result != None ==> self.i > \old(self.i)
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def accept_op(self, val: str) -> Optional[_Tok]:
        if self.at_op(val):
            return self.advance()
        return None

    #@ requires True
    # FAITHFUL MONOTONICITY (was `ensures True`): `expect_op` moves `self.i` only
    # through `advance` (`self.i >= \old(self.i)`) on the success path; the failure
    # path is `self._err(...)` which is `-> NoReturn` (diverges, never returns
    # normally). So `self.i >= \old(self.i)` is a REAL property of the live body —
    # the same monotonicity `expect_name`/`accept_op`/`advance` already export. It
    # lets a converted caller whose live body ends in `self.expect_op(...)` (e.g.
    # `_parse_mixin_type`'s `expect_op("]")` tail) discharge its own monotonicity
    # postcondition across this sibling call.
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def expect_op(self, val: str) -> _Tok:
        if not self.at_op(val):
            self._err(f"expected {val!r}")
        return self.advance()

    #@ requires True
    # Monotonicity is a REAL property of the token cursor: `expect_name` moves
    # `self.i` only through `advance` (`self.i >= \old(self.i)`); `_err` is
    # `assigns \nothing`, `at_name` is `assigns \nothing`. This is what lets the
    # `while self.accept_op("."): … self.expect_name()` loops (`_parse_qualname`,
    # `_parse_dotted_path`) discharge their `\length(self.toks) - self.i` variant,
    # exactly as the expression-chain RHS helpers (`_parse_impl_rhs`, …) do.
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def expect_name(self, val: str = None) -> str:
        if not self.at_name() or (val is not None and not self.at_name(val)):
            self._err(f"expected name {val!r}" if val else "expected name")
        return self.advance().string

    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def expect_bs(self, val: str) -> str:
        if not self.at_bs(val):
            self._err(f"expected {val!r}")
        return self.advance().string

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    # DIVERGENCE MODEL (_err-divergence run): the LIVE `_err` body is
    # `t = self.cur(); raise _ContractSyntaxError(...)` — an UNCONDITIONAL raise, so it
    # NEVER returns normally. The `-> NoReturn` annotation records that faithfully: Module5
    # sets is_noreturn (NR1), Module6 gives the abstract op `ensures { false }` and lowers a
    # `self._err(...)` call to `(let _ = <call> in absurd)` (continuation UNREACHABLE). This
    # is what lets a clause parser whose live body ends in a trailing `self._err(...)` with
    # no following return (e.g. `_parse_loop`) type-check as `-> ExprIR` — the raising path
    # yields the branch's emit_ir type via the divergence, not a spurious `unit`. Stays
    # `\trusted` (raise + f-string + `self.cur()` char boundary); the annotation only makes
    # the trusted interface precise, backed by the live unconditional raise.
    def _err(self, msg: str) -> NoReturn:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    # FAITHFUL FRAME (was `assigns \nothing`, which the live body contradicts — the
    # `except _ContractSyntaxError` path does `self.i = saved`).
    # HIGHER-ORDER LIMITATION: `_try(fn)` calls `fn()`, so its true frame is
    # `self.i` UNION whatever `fn` writes. The frame below is exact only because the
    # live class has a SINGLE `_try` call site — `self._try(self._parse_assigns_region)`
    # — and `_parse_assigns_region`'s transitive frame is itself `{self.i}` (in the
    # live `_ContractParser`, only `__init__`, `advance`, `_try` and `_grab_reviewer_id`
    # write a self field, and all four write only `self.i`; `self.toks` is written
    # exclusively by `__init__`). It is NOT a frame valid for an arbitrary `fn`; a new
    # `_try` call site with a wider callee INVALIDATES it.
    # NO monotonicity `ensures` here: `self.i = saved` can DECREASE `self.i`. `_try` is
    # precisely the backtracking site the expression chain's monotonicity relies on
    # being unreachable.
    #@ ensures True
    #@ assigns self.i
    def _try(self, fn):
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def parse(self):
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_contract(self):
        pass

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_loop(self) -> "ExprIR":
        self.expect_name("loop")
        if self.at_name("invariant"):
            self.advance(); return LoopInvariant(self._parse_expr())
        if self.at_name("variant"):
            self.advance(); return LoopVariant(self._parse_expr())
        self._err("expected 'invariant' or 'variant' after 'loop'")

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_class_invariant(self) -> "ExprIR":
        self.expect_name("class")
        self.expect_name("invariant")
        return ClassInvariant(self._parse_expr())

    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_function_variant(self) -> "ExprIR":
        self.expect_bs("\\variant")
        if self.at_op("("):
            self.advance()
            e = self._parse_expr()
            self.expect_op(",")
            ordering = self.expect_name()
            self.expect_op(")")
            return FunctionVariant(e, ordering)
        return FunctionVariant(self._parse_expr())

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_trusted(self):
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _grab_reviewer_id(self):
        pass

    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_ghost(self) -> "ExprIR":
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

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_raises(self) -> "ExprIR":
        self.expect_name("raises")
        exc = self.expect_name()
        self.expect_name("when")
        return RaisesDecl(exc, self._parse_expr())

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_no_exception(self):
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_assumes(self):
        pass

    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_proof(self) -> "ExprIR":
        self.expect_name("proof")
        prover = self.expect_name()  # PROVER_ID: rocq | lean
        qualname = self._parse_qualname()
        return ProofDecl(prover=prover, qualname=qualname)

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_qualname(self) -> str:
        name = self.expect_name()
        #@ loop invariant self.i >= \old(self.i)
        #@ loop invariant 0 <= self.i and self.i < \length(self.toks)
        #@ loop invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
        #@ loop variant \length(self.toks) - self.i
        while self.accept_op("."):
            name += "." + self.expect_name()
        return name

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_interface(self) -> "ExprIR":
        self.expect_name("interface")
        if self.at_name("ensures"):
            self.advance(); return InterfaceClause("ensures", Ensures(self._parse_expr()))
        if self.at_name("requires"):
            self.advance(); return InterfaceClause("requires", Requires(self._parse_expr()))
        if self.at_name("assigns"):
            self.advance(); return InterfaceClause("assigns", self._parse_assigns())
        self._err("expected ensures/requires/assigns after 'interface'")

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    # Returns an `Assigns` contract-AST node; the `-> "ExprIR"` return annotation lets a
    # converted caller (`_parse_interface`) bind it as an emit_ir payload (GAP #2 typed
    # trusted-return, the `_parse_expr` precedent). Stays `\trusted` (builds an assigns
    # target list — family-B list boundary); the annotation only makes the interface precise.
    def _parse_assigns(self) -> "ExprIR":
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_assigns_target(self):
        pass

    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_assigns_region(self) -> "ExprIR":
        name = self.expect_name()
        self.expect_op("[")
        lo = self._parse_expr()
        self.expect_op("..")
        hi = self._parse_expr()
        self.expect_op("]")
        return AssignsRegion(name, lo, hi)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_act_block(self):
        pass

    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_for_block(self) -> ForExpand:
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
        #@ loop invariant self.i >= \old(self.i)
        #@ loop invariant 0 <= self.i and self.i < \length(self.toks)
        #@ loop invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
        #@ loop variant \length(self.toks) - self.i
        while self.at_name("requires") or self.at_name("ensures"):
            if self.at_name("requires"):
                self.advance(); clauses.append(Requires(self._parse_expr()))
            else:
                self.advance(); clauses.append(Ensures(self._parse_expr()))
        if not clauses:
            self._err("for block requires at least one clause")
        return ForExpand(var, lo, hi, clauses)

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_act_names(self) -> List[str]:
        names = [self.expect_name()]
        #@ loop invariant self.i >= \old(self.i)
        #@ loop invariant 0 <= self.i and self.i < \length(self.toks)
        #@ loop invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
        #@ loop variant \length(self.toks) - self.i
        while self.accept_op(","):
            names.append(self.expect_name())
        return names

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_happy(self):
        pass

    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_happy_region(self, name: str) -> HappyProperty:
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_happy_targets(self, name):
        pass

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_opt_except(self) -> List[str]:
        if self.at_name("except"):
            self.advance()
            return self._parse_act_names()
        return []

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_dotted_path(self) -> str:
        path = self.expect_name()
        #@ loop invariant self.i >= \old(self.i)
        #@ loop invariant 0 <= self.i and self.i < \length(self.toks)
        #@ loop invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
        #@ loop variant \length(self.toks) - self.i
        while self.accept_op("."):
            path += "." + self.expect_name()
        return path

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_dotted_path_list(self) -> List[str]:
        paths = [self._parse_dotted_path()]
        #@ loop invariant self.i >= \old(self.i)
        #@ loop invariant 0 <= self.i and self.i < \length(self.toks)
        #@ loop invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
        #@ loop variant \length(self.toks) - self.i
        while self.accept_op(","):
            paths.append(self._parse_dotted_path())
        return paths

    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_footprint(self) -> "ExprIR":
        self.expect_name("footprint")
        happy_name = self.expect_name()
        self.expect_op("(")
        arg = self._parse_expr()
        self.expect_op(")")
        return Footprint(happy_name, arg)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_datatype(self):
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_variant_def(self):
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_inductive(self):
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_inductive_rules(self):
        pass

    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_shared_state(self) -> "ExprIR":
        self.expect_name("shared_state")
        name = self.expect_name()
        self.expect_op(":")
        ty = self._parse_mixin_type()
        return SharedStateDecl(name, ty)

    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_touches_field(self) -> "ExprIR":
        self.expect_name("touches_field")
        name = self.expect_name()
        self.expect_op(":")
        ty = self._parse_mixin_type()
        return TouchesFieldDecl(name, ty)

    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_depends_method(self, kind: str) -> "ExprIR":
        self.advance()  # depends_method / requires_method
        method = self.expect_name()
        self.expect_op(":")
        sig = self._parse_mixin_method_sig()
        return MethodDependencyDecl(method, sig, kind)

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_compose_from(self) -> "ExprIR":
        self.expect_name("compose_from")
        names = [self.expect_name()]
        #@ loop invariant self.i >= \old(self.i)
        #@ loop invariant 0 <= self.i and self.i < \length(self.toks)
        #@ loop invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
        #@ loop variant \length(self.toks) - self.i
        while self.accept_op(","):
            names.append(self.expect_name())
        return ComposeFromDecl(names)

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_conforms_to(self) -> "ExprIR":
        self.expect_name("conforms_to")
        names = [self.expect_name()]
        #@ loop invariant self.i >= \old(self.i)
        #@ loop invariant 0 <= self.i and self.i < \length(self.toks)
        #@ loop invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
        #@ loop variant \length(self.toks) - self.i
        while self.accept_op(","):
            names.append(self.expect_name())
        return ConformsToDecl(names)

    #@ requires True
    # FAITHFUL MONOTONICITY: `_parse_mixin_type` is a recursive-descent rule over
    # the token stream whose only cursor effect is `expect_name`/`advance`/
    # `accept_op`/`expect_op` — all monotone (never backtrack; `_try` is not
    # reachable from a mixin-type rule). So `self.i >= \old(self.i)` is a REAL
    # structural property of the live body (what lets the converted
    # `_parse_mixin_params`/`_parse_mixin_param` callers discharge their loop
    # variant across this sibling call). CONVERTED via the banked `#@ \variant`
    # recursive-descent key: the mandatory `expect_name` + `advance` under the
    # `at_op("[")` guard strictly increments `self.i` before the FIRST recursive
    # call (the token at `self.i` is an OP, the EOF sentinel is the last token, so
    # `self.i < \length - 1` and `advance` gives `+1`), so the variant is
    # well-founded; the string result is built by the banked `', '.join`
    # (str_join_seq) over a `list string`.
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    #@ \variant \length(self.toks) - self.i
    def _parse_mixin_type(self) -> str:
        name = self.expect_name()
        if self.at_op("["):
            self.advance()
            args = [self._parse_mixin_type()]
            #@ loop invariant self.i > \old(self.i)
            #@ loop invariant 0 <= self.i and self.i < \length(self.toks)
            #@ loop invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
            #@ loop variant \length(self.toks) - self.i
            while self.accept_op(","):
                args.append(self._parse_mixin_type())
            self.expect_op("]")
            return f"{name}[{', '.join(args)}]"
        return str(name)

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_mixin_param(self) -> str:
        name = self.expect_name()
        if self.accept_op(":"):
            return f"{name}: {self._parse_mixin_type()}"
        return str(name)

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_mixin_params(self) -> str:
        params = [self._parse_mixin_param()]
        #@ loop invariant self.i >= \old(self.i)
        #@ loop invariant 0 <= self.i and self.i < \length(self.toks)
        #@ loop invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
        #@ loop variant \length(self.toks) - self.i
        while self.accept_op(","):
            params.append(self._parse_mixin_param())
        return ", ".join(params)

    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_mixin_method_sig(self) -> str:
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

    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_shared(self) -> "ExprIR":
        self.expect_name("shared")
        name = self.expect_name()
        if self.at_name("protected_by"):
            self.advance()
            mutex = self._parse_mutex_expr_str()
            return SharedDecl(name, mutex)
        return SharedDecl(name, None)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ ensures self.i >= \old(self.i)
    #@ ensures self.i < \length(self.toks)
    #@ assigns self.i
    # Returns the mutex-expression STRING (`NAME` or `NAME[<idx>]`); the `-> str` return
    # annotation lets a converted caller (`_parse_mutex_invariant`) bind it as the leaf
    # `mutex` field. Stays `\trusted` — its `f"{name}[{_csl_to_str(index)}]"` body threads
    # a value through the two-trusted-stub `_parse_expr`/`_csl_to_str` type mismatch
    # (CERTIFIED BOUNDARY, parser-tokenstream-impl.md GAP #2 run); the annotation only
    # makes the trusted interface precise (the `_parse_assigns`/`_parse_expr` precedent).
    def _parse_mutex_expr_str(self) -> str:
        pass

    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_mutex_invariant(self) -> "ExprIR":
        self.expect_name("mutex_invariant")
        mutex = self._parse_mutex_expr_str()
        self.expect_op(":")
        return MutexInvariant(mutex, self._parse_expr())

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_lock_order(self) -> "ExprIR":
        self.expect_name("lock_order")
        names = [self._parse_mutex_expr_str()]
        #@ loop invariant self.i >= \old(self.i)
        #@ loop invariant 0 <= self.i and self.i < \length(self.toks)
        #@ loop invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
        #@ loop variant \length(self.toks) - self.i
        while self.accept_op(","):
            names.append(self._parse_mutex_expr_str())
        return LockOrder(names)

    #@ requires True
    # FAITHFUL MONOTONICITY (the `_parse_impl_rhs`/`advance`/`accept_op` precedent):
    # `self.i` is only ever incremented (via `advance`); the sole backtracking site,
    # `_try`, is used exclusively by `_parse_assigns_region` and is UNREACHABLE from any
    # expression rule (`_parse_expr` -> `_parse_quantifier`/`_parse_implication` -> the
    # precedence chain, none of which call `_try`). This is what lets the already-converted
    # clause callers (`_parse_class_invariant`/`_parse_raises`/`_parse_loop`/`_parse_interface`)
    # prove their own `self.i >= \old(self.i)` compositionally from this contract.
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_expr(self) -> "ExprIR":
        if self.at_bs("\\forall") or self.at_bs("\\exists") or self.at_bs("\\exist"):
            return self._parse_quantifier()
        return self._parse_implication()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    # FAITHFUL MONOTONICITY (the `_parse_impl_rhs` precedent): the quantifier rule only
    # advances the cursor (`advance`); it never calls the backtracking `_try`. Stays
    # `\trusted` (builds Forall/Exists/ForallItems nodes = family-B); the monotonicity
    # ensures makes the trusted interface precise so `_parse_expr` proves its own frame.
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_quantifier(self) -> "ExprIR":
        pass

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _mk_in(var: str, domain: "ExprIR", body: "ExprIR", is_exists: bool) -> "ExprIR":
        # quantification.md P3 desugar: ∀x in S; P ≡ ∀x; (x in S) ==> P ;
        # ∃x in S; P ≡ ∃x; (x in S) and P.
        op = "and" if is_exists else "==>"
        return BinOp(CSLIn(Var(var), domain), op, body)

    #@ requires True
    # FAITHFUL FRAME: monotonicity is a real property of the expression chain —
    # `self.i` is only ever incremented (`advance`); the sole backtracking site,
    # `_try`, is used exclusively by `_parse_assigns_region` and is not reachable
    # from any expression rule. Pure dispatch: both branches return an emit_ir node
    # via a callee (`_parse_quantifier` / `_parse_logical_or`) that itself carries
    # `ensures self.i >= \old(self.i)`, so the frame + monotonicity discharge.
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_impl_rhs(self) -> "ExprIR":
        if self.at_bs("\\forall") or self.at_bs("\\exists") or self.at_bs("\\exist"):
            return self._parse_quantifier()
        return self._parse_logical_or()

    #@ requires True
    # FAITHFUL FRAME: `self.i` is only ever incremented in the expression chain; the
    # sole backtracking site `_try` is unreachable from any expression rule. Pure
    # dispatch — both branches return an emit_ir node via a monotone callee.
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_or_rhs(self) -> "ExprIR":
        if self.at_bs("\\forall") or self.at_bs("\\exists") or self.at_bs("\\exist"):
            return self._parse_quantifier()
        return self._parse_logical_and()

    #@ requires True
    # FAITHFUL FRAME: `self.i` is only ever incremented in the expression chain; the
    # sole backtracking site `_try` is unreachable from any expression rule. Pure
    # dispatch — both branches return an emit_ir node via a monotone callee.
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_and_rhs(self) -> "ExprIR":
        if self.at_bs("\\forall") or self.at_bs("\\exists") or self.at_bs("\\exist"):
            return self._parse_quantifier()
        return self._parse_equality()

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_implication(self) -> "ExprIR":
        left = self._parse_logical_or()
        #@ loop invariant self.i >= \old(self.i)
        #@ loop invariant 0 <= self.i and self.i < \length(self.toks)
        #@ loop invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
        #@ loop variant \length(self.toks) - self.i
        while self.at_op('==>', '<==>'):
            op = self.advance().string
            right = self._parse_impl_rhs()
            left = BinOp(left, op, right)
        return left

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_logical_or(self) -> "ExprIR":
        left = self._parse_logical_and()
        #@ loop invariant self.i >= \old(self.i)
        #@ loop invariant 0 <= self.i and self.i < \length(self.toks)
        #@ loop invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
        #@ loop variant \length(self.toks) - self.i
        while self.at_name('or'):
            self.advance()
            right = self._parse_or_rhs()
            left = BinOp(left, 'or', right)
        return left

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_logical_and(self) -> "ExprIR":
        left = self._parse_equality()
        #@ loop invariant self.i >= \old(self.i)
        #@ loop invariant 0 <= self.i and self.i < \length(self.toks)
        #@ loop invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
        #@ loop variant \length(self.toks) - self.i
        while self.at_name('and'):
            self.advance()
            right = self._parse_and_rhs()
            left = BinOp(left, 'and', right)
        return left

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_equality(self) -> "ExprIR":
        left = self._parse_comparison()
        #@ loop invariant self.i >= \old(self.i)
        #@ loop invariant 0 <= self.i and self.i < \length(self.toks)
        #@ loop invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
        #@ loop variant \length(self.toks) - self.i
        while self.at_op('==', '!='):
            op = self.advance().string
            left = BinOp(left, op, self._parse_comparison())
        return left

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_comparison(self) -> "ExprIR":
        left = self._parse_membership()
        #@ loop invariant self.i >= \old(self.i)
        #@ loop invariant 0 <= self.i and self.i < \length(self.toks)
        #@ loop invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
        #@ loop variant \length(self.toks) - self.i
        while self.at_op('>', '<', '>=', '<='):
            op = self.advance().string
            left = BinOp(left, op, self._parse_membership())
        return left

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_membership(self) -> "ExprIR":
        left = self._parse_term()
        if self.at_name("in"):
            self.advance()
            return CSLIn(left, self._parse_term())
        if self.at_name("not") and self.peek().type == "NAME" and self.peek().string == "in":
            self.advance(); self.advance()
            return CSLNotIn(left, self._parse_term())
        return left

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_term(self) -> "ExprIR":
        left = self._parse_factor()
        #@ loop invariant self.i >= \old(self.i)
        #@ loop invariant 0 <= self.i and self.i < \length(self.toks)
        #@ loop invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
        #@ loop variant \length(self.toks) - self.i
        while self.at_op('+', '-'):
            op = self.advance().string
            left = BinOp(left, op, self._parse_factor())
        return left

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_factor(self) -> "ExprIR":
        left = self._parse_unary()
        #@ loop invariant self.i >= \old(self.i)
        #@ loop invariant 0 <= self.i and self.i < \length(self.toks)
        #@ loop invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
        #@ loop variant \length(self.toks) - self.i
        while self.at_op('*', '//', '/', '%'):
            op = self.advance().string
            left = BinOp(left, op, self._parse_unary())
        return left

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    #@ \variant \length(self.toks) - self.i
    def _parse_unary(self) -> "ExprIR":
        if self.at_name("not") or self.at_op("-", "+"):
            op = self.advance().string
            return UnaryOp(op, self._parse_unary())
        return self._parse_atom()

    #@ requires True
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    #@ \variant \length(self.toks) - self.i
    def _parse_atom(self) -> "ExprIR":
        node = self._parse_atom_primary()
        if self.at_op("^"):
            self.advance()
            right = self._parse_atom()        # right-assoc (Lark LALR shifts)
            return StrConcatExpr(node, right)
        return node

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    # FAITHFUL MONOTONICITY (was `ensures True`): the atom-primary rule only ADVANCES
    # the cursor. Its live body calls `cur`/`advance`/`_parse_atom_bs`/`_parse_atom_name`/
    # `_parse_expr`/`expect_op`/`_err` — every one monotone (or diverging); it NEVER
    # calls `_try` (sole backtracking site is `_parse_assigns_region`, line 1481 live)
    # and NEVER assigns `self.i` directly. Verified against the live body — the
    # `_parse_atom` monotonicity precedent (its converted caller discharges its frame).
    #@ ensures self.i >= \old(self.i)
    #@ assigns self.i
    def _parse_atom_primary(self) -> "ExprIR":
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_atom_name(self):
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_atom_bs(self):
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def _parse_expr_list(self):
        pass


class Module2_Parser:
    'Parses raw PyCSL string contracts into Contract AST objects.\n\n    A pure-Python recursive-descent parser (`_ContractParser`) — no 3rd-party\n    deps. Replaces the former Lark LALR engine; the 1:1 grammar→CSLNode map is\n    preserved (differential-tested against the legacy engine in\n    `bin/diff_parser.py`).\n    '
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self, use_rdp=None) -> None:
        # `use_rdp` is accepted (and ignored) for backward compatibility with
        # callers that passed it during the migration; the rdp engine is now
        # the only engine.
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def parse_contract(self, contract_str: str, line_number: int) -> CSLNode:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def parse_node_contracts(self, raw_contracts: List[str], line_number: int) -> List[CSLNode]:
        return []


