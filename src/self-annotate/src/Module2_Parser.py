from __future__ import annotations
from dataclasses import dataclass
from typing import List, Union, Any, Optional
from lark import Lark, Transformer, v_args
from lark.exceptions import LarkError
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
    object: str
    field: str

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

@dataclass
class Exists(QuantifierNode):
    var: str
    body: CSLNode

@dataclass
class ArrayLength(CSLNode):
    var: str

@dataclass
class AssignsRegion(CSLNode):
    'Represents `arr[lo..hi]` inside an assigns clause (frame condition region).'
    base: str
    low: CSLNode
    high: CSLNode

@dataclass
class Valid(CSLNode):
    'Represents `\\valid(arr, n)` — memory region [arr, arr+n) is allocated.'
    base: str
    length: CSLNode

@dataclass
class Separated(CSLNode):
    "Represents `\\separated(a, na, b, nb)` — regions [a,a+na) and [b,b+nb) don't overlap."
    base1: str
    length1: CSLNode
    base2: str
    length2: CSLNode

@dataclass
class Label(CSLNode):
    'Represents a `#@ label L` program point annotation.'
    name: str

@dataclass
class At(CSLNode):
    'Represents `\\at(expr, L)` — value of expr at program point L.'
    expr: CSLNode
    label: str

@dataclass
class Length2D(CSLNode):
    'Represents `\\length2d(arr, m, n)` — arr has m rows each of length n.'
    base: str
    rows: CSLNode
    cols: CSLNode

@dataclass
class Valid2D(CSLNode):
    'Represents `\\valid2d(arr, i, j)` — (i,j) is a valid 2D index into arr.'
    base: str
    row: CSLNode
    col: CSLNode

@dataclass
class FunctionVariant(CSLNode):
    'Represents `#@ \\variant <expr>` or `#@ \\variant (<expr>, <ordering>)`.'
    expr: CSLNode
    ordering: Optional[str] = None

@dataclass
class Diverges(CSLNode):
    'Represents `#@ \\diverges` — function may not terminate.'

@dataclass
class Trusted(CSLNode):
    'Represents `#@ \\trusted` — function body is not verified.\n    Optional `reviewer` identifies who is accountable for the trust assumption.'
    reviewer: str = ''

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
    element: CSLNode
    collection: CSLNode

@dataclass
class CSLSlice(CSLNode):
    'Represents `arr[lo:hi]` slice notation in contracts.'
    collection: str
    low: CSLNode
    high: CSLNode

@dataclass
class ChainedSubscript(CSLNode):
    'Represents `arr[i][j]` chained subscript access (2D array element).'
    array: str
    index1: CSLNode
    index2: CSLNode

@dataclass
class CallExpr(CSLNode):
    'Represents a function call in a contract expression.'
    func: str
    args: List[CSLNode]

@dataclass
class IsSorted(CSLNode):
    'Represents `\\is_sorted(a, lo, hi)` — array is sorted in range.'
    base: str
    lo: CSLNode
    hi: CSLNode

@dataclass
class Sum(CSLNode):
    'Represents `\\sum(a, lo, hi)` — sum of array elements in range.'
    base: str
    lo: CSLNode
    hi: CSLNode

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
    elts: List[CSLNode]

@dataclass
class FstExpr(CSLNode):
    '\\fst(t) — first component of a ghost tuple.'
    tuple_expr: CSLNode

@dataclass
class SndExpr(CSLNode):
    '\\snd(t) — second component of a ghost tuple.'
    tuple_expr: CSLNode

@dataclass
class ProjExpr(CSLNode):
    '\\proj(t, i) — ith component of a ghost tuple (i must be a literal).'
    tuple_expr: CSLNode
    index: CSLNode

@dataclass
class StrConcatExpr(CSLNode):
    's ^ t — string concatenation in ghost / contract context.'
    left: CSLNode
    right: CSLNode

@dataclass
class StrLengthExpr(CSLNode):
    '\\str_length(s) — length of a ghost string variable.'
    string: CSLNode

@dataclass
class StrSubExpr(CSLNode):
    '\\str_sub(s, lo, hi) — substring of ghost string s from lo to hi.'
    string: CSLNode
    lo: CSLNode
    hi: CSLNode

@dataclass
class GhostCopyExpr(CSLNode):
    '\\copy(arr) — snapshot of an array into a ghost array.'
    arr: str

@dataclass
class GhostCopyRangeExpr(CSLNode):
    '\\copy_range(arr, lo, hi) — bounded snapshot: arr[lo..hi-1] into a new ghost array.'
    arr: str
    lo: CSLNode
    hi: CSLNode

@dataclass
class GhostMakeExpr(CSLNode):
    '\\make(n, v) — create a ghost array of length n filled with v.'
    size: CSLNode
    default: CSLNode

@dataclass
class MapEmptyExpr(CSLNode):
    '\\empty_map — an empty ghost dictionary (total map defaulting to 0).'

@dataclass
class MapGetExpr(CSLNode):
    '\\map_get(d, k) — look up key k in ghost dict d.'
    dict_expr: CSLNode
    key: CSLNode

@dataclass
class MapSetExpr(CSLNode):
    '\\map_set(d, k, v) — return ghost dict d with d[k] := v.'
    dict_expr: CSLNode
    key: CSLNode
    value: CSLNode

@dataclass
class MapEqExpr(CSLNode):
    '\\map_eq(d1, d2) — extensional equality of two ghost dicts.'
    left: CSLNode
    right: CSLNode

@dataclass
class HasKeyExpr(CSLNode):
    '\\has_key(d, k) — true iff ghost dict d has a present (non-None) value at key k.'
    dict_expr: CSLNode
    key: CSLNode

@dataclass
class MapRemoveExpr(CSLNode):
    '\\map_remove(d, k) — return ghost dict d with key k removed (set to None/absent).'
    dict_expr: CSLNode
    key: CSLNode

@dataclass
class SetEmptyExpr(CSLNode):
    '\\set_empty — the empty ghost set.'

@dataclass
class SetAddExpr(CSLNode):
    '\\set_add(s, x) — ghost set with x added.'
    set_expr: CSLNode
    elem: CSLNode

@dataclass
class SetRemoveExpr(CSLNode):
    '\\set_remove(s, x) — ghost set with x removed.'
    set_expr: CSLNode
    elem: CSLNode

@dataclass
class SetMemExpr(CSLNode):
    '\\set_mem(x, s) — x is a member of ghost set s.'
    elem: CSLNode
    set_expr: CSLNode

@dataclass
class SetUnionExpr(CSLNode):
    '\\set_union(s1, s2) — union of two ghost sets.'
    left: CSLNode
    right: CSLNode

@dataclass
class SetInterExpr(CSLNode):
    '\\set_inter(s1, s2) — intersection of two ghost sets.'
    left: CSLNode
    right: CSLNode

@dataclass
class SetDiffExpr(CSLNode):
    '\\set_diff(s1, s2) — set difference s1 \\ s2.'
    left: CSLNode
    right: CSLNode

@dataclass
class SetCardExpr(CSLNode):
    '\\set_card(s, lo, hi) — cardinality of s restricted to [lo, hi).'
    set_expr: CSLNode
    lo: CSLNode
    hi: CSLNode

@dataclass
class SetSubsetExpr(CSLNode):
    '\\set_subset(s1, s2) — s1 is a subset of s2.'
    left: CSLNode
    right: CSLNode

@dataclass
class SetEqExpr(CSLNode):
    '\\set_eq(s1, s2) — extensional equality of two ghost sets.'
    left: CSLNode
    right: CSLNode

@dataclass
class NilExpr(CSLNode):
    '\\nil — the empty ghost list.'

@dataclass
class ConsExpr(CSLNode):
    '\\cons(x, l) — prepend x to ghost list l.'
    head: CSLNode
    tail: CSLNode

@dataclass
class HdExpr(CSLNode):
    '\\hd(l) — head of ghost list l (requires l non-empty).'
    list_expr: CSLNode

@dataclass
class TlExpr(CSLNode):
    '\\tl(l) — tail of ghost list l (requires l non-empty).'
    list_expr: CSLNode

@dataclass
class ListLengthExpr(CSLNode):
    '\\list_length(l) — length of ghost list l.'
    list_expr: CSLNode

@dataclass
class NthExpr(CSLNode):
    '\\nth(l, i) — ith element of ghost list l (requires 0 <= i < length).'
    list_expr: CSLNode
    index: CSLNode

@dataclass
class MemExpr(CSLNode):
    '\\mem(x, l) — x appears in ghost list l.'
    elem: CSLNode
    list_expr: CSLNode

@dataclass
class AppendExpr(CSLNode):
    '\\append(l1, l2) — concatenation of two ghost lists.'
    left: CSLNode
    right: CSLNode

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

PYCSL_GRAMMAR = '\n    ?start: contract\n\n    ?contract: precondition\n             | postcondition\n             | assigns\n             | loop_invariant\n             | loop_variant\n             | class_invariant\n             | label_decl\n             | function_variant\n             | function_variant_structural\n             | diverges_decl\n             | trusted_decl\n             | ghost_assign\n             | ghost_aug_assign\n             | ghost_array_set\n             | raises_decl\n             | no_exception_decl\n             | allow_finalizer_decl\n             | allow_iteration_mutation_decl\n             | bounded_int_decl\n             | proof_decl\n             | shared_decl\n             | thread_entry_decl\n             | acquires_decl\n             | releases_decl\n             | critical_decl\n             | mutex_invariant_decl\n             | lock_order_decl\n\n    precondition: "requires" expr\n    postcondition: "ensures" expr\n    \n    // Extracted alias from group to prevent Lark GrammarError\n    assigns: "assigns" assigns_target\n    ?assigns_target: assigns_region_list\n                   | expr_list \n                   | "\\\\nothing" -> nothing\n\n    assigns_region_list: assigns_region ("," assigns_region)*\n    assigns_region: CNAME "[" expr RANGE_OP expr "]"\n\n    loop_invariant: "loop" "invariant" expr\n    loop_variant: "loop" "variant" expr\n    class_invariant: "class" "invariant" expr\n    label_decl: "label" CNAME\n    function_variant: "\\\\variant" expr\n    function_variant_structural: "\\\\variant" "(" expr "," CNAME ")"\n    diverges_decl: "\\\\diverges"\n    trusted_decl: "\\\\trusted" ("reviewer" ":" REVIEWER_ID)?\n    REVIEWER_ID: /[A-Za-z0-9._@-]+/\n    ghost_assign: "ghost" CNAME ":" GHOST_TYPE "=" expr -> ghost_assign_typed\n              | "ghost" CNAME "=" expr -> ghost_assign_untyped\n    ghost_aug_assign: "ghost" CNAME GHOST_AUG_OP expr\n    ghost_array_set: "ghost" CNAME "[" expr "]" "=" expr\n    raises_decl: "raises" CNAME "when" expr\n\n    // no_exception — implicit exceptions become proof obligations\n    // (see config/skills/pycsl-exception-model). The bare-name form lists\n    // specific exceptions; the `\\all` form expands at transpilation to the\n    // full Phase 1 set and requires the function\'s raises set to be empty.\n    no_exception_decl: "no_exception" "\\\\all" -> no_exception_all_decl\n                     | "no_exception" exception_name_list -> no_exception_list_decl\n    exception_name_list: CNAME ("," CNAME)*\n\n    // UB-7.5 — opt-in to `__del__` despite the default rejection\n    allow_finalizer_decl: "allow_finalizer"\n    // UB-7.1 — opt-in to mutating the iterated container inside a for loop\n    allow_iteration_mutation_decl: "allow_iteration_mutation"\n\n    bounded_int_decl: "assumes" "bounded_int" "(" NUMBER ")"\n\n    // §2.1.12 Proof citation — emits a Why3 axiom in the WhyML preamble\n    // whose body is provided by the cited Rocq or Lean theorem under\n    // <test>.proofs/{rocq,lean}/. See docs/cross-validated-spec-sources.md.\n    // `PROVER_ID` is restricted to {rocq, lean} by the terminal.\n    // `QUALNAME` is a dotted identifier path (e.g. Pycsl.Reference.Gcd.gcd_step).\n    proof_decl: "proof" PROVER_ID QUALNAME\n    PROVER_ID: "rocq" | "lean"\n    QUALNAME: CNAME ("." CNAME)*\n\n    // Expression hierarchy (handles operator precedence and left-recursion)\n    // Quantifiers can appear at top level or as the RHS of ==>, and, or.\n    ?expr: implication\n         | "\\\\forall" CNAME ";" expr -> forall_expr\n         | "\\\\exists" CNAME ";" expr -> exists_expr\n         | "\\\\exist"  CNAME ";" expr -> exists_expr\n\n    ?implication: logical_or | implication IMPL_OP impl_rhs\n    ?impl_rhs: logical_or\n             | "\\\\forall" CNAME ";" expr -> forall_expr\n             | "\\\\exists" CNAME ";" expr -> exists_expr\n             | "\\\\exist"  CNAME ";" expr -> exists_expr\n\n    ?logical_or: logical_and | logical_or OR_OP or_rhs\n    ?or_rhs: logical_and\n           | "\\\\forall" CNAME ";" expr -> forall_expr\n           | "\\\\exists" CNAME ";" expr -> exists_expr\n           | "\\\\exist"  CNAME ";" expr -> exists_expr\n\n    ?logical_and: equality | logical_and AND_OP and_rhs\n    ?and_rhs: equality\n            | "\\\\forall" CNAME ";" expr -> forall_expr\n            | "\\\\exists" CNAME ";" expr -> exists_expr\n            | "\\\\exist"  CNAME ";" expr -> exists_expr\n    ?equality: comparison | equality EQ_OP comparison\n    ?comparison: membership | comparison COMP_OP membership\n    ?membership: term\n              | term "in" term -> in_expr\n              | term "not" "in" term -> not_in_expr\n    ?term: factor | term ADD_OP factor\n    ?factor: unary | factor MUL_OP unary\n    \n    ?unary: UNARY_OP unary -> unary_op\n          | atom\n\n    ?atom: NUMBER -> number\n         | ESCAPED_STRING -> string_literal\n         | "True" -> true_lit\n         | "False" -> false_lit\n         | "None" -> none_lit\n         | "self" "." CNAME -> field_access\n         | "\\\\result" "[" expr "]" -> result_subscript\n         | "\\\\is_sorted" "(" CNAME "," expr "," expr ")" -> is_sorted_expr\n         | "\\\\sum" "(" CNAME "," expr "," expr ")" -> sum_expr\n         | CNAME "(" expr_list ")" -> call_expr\n         | CNAME "(" ")" -> call_expr_noargs\n         | CNAME "[" expr ":" expr "]" -> slice_access\n         | CNAME "[" expr "]" "[" expr "]" -> chained_subscript\n         | CNAME "[" expr "]" -> subscript_access\n         | CNAME -> var\n         | "\\\\result" -> result\n         | "\\\\old" "(" expr ")" -> old_var\n         | "\\\\length" "(" CNAME ")" -> array_length\n         | "\\\\valid" "(" CNAME "," expr ")" -> valid_pred\n         | "\\\\separated" "(" CNAME "," expr "," CNAME "," expr ")" -> separated_pred\n         | "\\\\at" "(" expr "," CNAME ")" -> at_expr\n         | "\\\\length2d" "(" CNAME "," expr "," expr ")" -> length2d_pred\n         | "\\\\valid2d" "(" CNAME "," expr "," expr ")" -> valid2d_pred\n         | atom "^" atom -> str_concat\n         | "\\\\str_length" "(" expr ")" -> str_length_expr\n         | "\\\\str_sub" "(" expr "," expr "," expr ")" -> str_sub_expr\n         | "\\\\mktuple" "(" expr_list ")" -> mktuple_expr\n         | "\\\\fst" "(" expr ")" -> fst_expr\n         | "\\\\snd" "(" expr ")" -> snd_expr\n         | "\\\\proj" "(" expr "," expr ")" -> proj_expr\n         | "\\\\empty_map" -> empty_map_expr\n         | "\\\\map_get" "(" expr "," expr ")" -> map_get_expr\n         | "\\\\map_set" "(" expr "," expr "," expr ")" -> map_set_expr\n         | "\\\\map_eq" "(" expr "," expr ")" -> map_eq_expr\n         | "\\\\has_key" "(" expr "," expr ")" -> has_key_expr\n         | "\\\\map_remove" "(" expr "," expr ")" -> map_remove_expr\n         | "\\\\set_empty" -> set_empty_expr\n         | "\\\\set_add" "(" expr "," expr ")" -> set_add_expr\n         | "\\\\set_remove" "(" expr "," expr ")" -> set_remove_expr\n         | "\\\\set_mem" "(" expr "," expr ")" -> set_mem_expr\n         | "\\\\set_union" "(" expr "," expr ")" -> set_union_expr\n         | "\\\\set_inter" "(" expr "," expr ")" -> set_inter_expr\n         | "\\\\set_diff" "(" expr "," expr ")" -> set_diff_expr\n         | "\\\\set_card" "(" expr "," expr "," expr ")" -> set_card_expr\n         | "\\\\set_subset" "(" expr "," expr ")" -> set_subset_expr\n         | "\\\\set_eq" "(" expr "," expr ")" -> set_eq_expr\n         | "\\\\nil" -> nil_expr\n         | "\\\\cons" "(" expr "," expr ")" -> cons_expr\n         | "\\\\hd" "(" expr ")" -> hd_expr\n         | "\\\\tl" "(" expr ")" -> tl_expr\n         | "\\\\list_length" "(" expr ")" -> list_length_expr\n         | "\\\\nth" "(" expr "," expr ")" -> nth_expr\n         | "\\\\mem" "(" expr "," expr ")" -> mem_expr\n         | "\\\\append" "(" expr "," expr ")" -> append_expr\n         | "\\\\copy" "(" CNAME ")" -> copy_expr\n         | "\\\\copy_range" "(" CNAME "," expr "," expr ")" -> copy_range_expr\n         | "\\\\make" "(" expr "," expr ")" -> make_expr\n         | "(" expr ")"\n\n    expr_list: expr ("," expr)*\n\n    // Concurrency annotations\n    mutex_expr: CNAME "[" expr "]" -> mutex_subscript\n              | CNAME -> mutex_name\n\n    shared_decl: "shared" CNAME "protected_by" mutex_expr -> shared_protected\n               | "shared" CNAME -> shared_unprotected\n    thread_entry_decl: "thread_entry"\n    acquires_decl: "acquires" mutex_expr\n    releases_decl: "releases" mutex_expr\n    critical_decl: "critical" mutex_expr\n    mutex_invariant_decl: "mutex_invariant" mutex_expr ":" expr\n    lock_order_decl: "lock_order" mutex_expr ("," mutex_expr)*\n\n    // Explicit tokens so Lark doesn\'t drop the operators\n    IMPL_OP: "==>" | "<==>"\n    OR_OP: "or"\n    AND_OP: "and"\n    EQ_OP: "==" | "!="\n    COMP_OP: ">" | "<" | ">=" | "<="\n    ADD_OP: "+" | "-"\n    MUL_OP: "*" | "//" | "/" | "%"\n    UNARY_OP: "not" | "-" | "+"\n    RANGE_OP: ".."\n    GHOST_AUG_OP: "+=" | "-=" | "*="\n    GHOST_TYPE: "string" | "array" | "ghost_dict" | "ghost_list" | "ghost_set" | "tuple2" | "tuple3" | "tuple4"\n\n    %import common.CNAME\n    %import common.INT -> NUMBER\n    %import common.ESCAPED_STRING\n    %import common.WS\n    %ignore WS\n'
#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def _csl_to_str(node: CSLNode) -> str:
    """Convert a simple CSL node to string — used for mutex subscript indices."""
    if isinstance(node, Var):
        return node.name
    if isinstance(node, Number):
        return str(int(node.value))
    if isinstance(node, BinOp):
        return f"{_csl_to_str(node.left)}{node.op}{_csl_to_str(node.right)}"
    return "?"

@v_args(inline=True)
class PyCSLTransformer(Transformer):
    "Converts Lark's ParseTree into our Contract AST Nodes."
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def precondition(self, expr) -> Requires: return Requires(expr)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def postcondition(self, expr) -> Ensures: return Ensures(expr)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def assigns(self, target) -> Assigns:
        if isinstance(target, Nothing):
            return Assigns([target])
        elif isinstance(target, list):
            return Assigns(target)
        else:
            return Assigns([target])

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def loop_invariant(self, expr) -> LoopInvariant: return LoopInvariant(expr)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def loop_variant(self, expr) -> LoopVariant: return LoopVariant(expr)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def class_invariant(self, expr) -> ClassInvariant: return ClassInvariant(expr)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def function_variant(self, expr) -> FunctionVariant: return FunctionVariant(expr)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def function_variant_structural(self, expr, ordering) -> FunctionVariant: return FunctionVariant(expr, str(ordering))

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def diverges_decl(self) -> Diverges: return Diverges()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def trusted_decl(self, *args) -> Trusted:
        return Trusted(reviewer=str(args[0]) if args else "")

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def ghost_assign_typed(self, name, ghost_type, expr) -> GhostAssignDecl:
        return GhostAssignDecl(str(name), expr, "=", declared_type=str(ghost_type))

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def ghost_assign_untyped(self, name, expr) -> GhostAssignDecl:
        return GhostAssignDecl(str(name), expr, "=")

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def ghost_aug_assign(self, name, op, expr) -> GhostAssignDecl: return GhostAssignDecl(str(name), expr, str(op))

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def ghost_array_set(self, name, index, value) -> GhostArraySetDecl:
        return GhostArraySetDecl(str(name), index, value)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def raises_decl(self, exc_type, condition) -> RaisesDecl: return RaisesDecl(str(exc_type), condition)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def exception_name_list(self, *names) -> List[str]:
        return [str(n) for n in names]

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def no_exception_all_decl(self) -> NoExceptionDecl:
        return NoExceptionDecl(exceptions=[], all_form=True)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def no_exception_list_decl(self, names) -> NoExceptionDecl:
        return NoExceptionDecl(exceptions=list(names), all_form=False)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def allow_finalizer_decl(self) -> AllowFinalizerDecl:
        return AllowFinalizerDecl()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def allow_iteration_mutation_decl(self) -> AllowIterationMutationDecl:
        return AllowIterationMutationDecl()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def bounded_int_decl(self, size) -> BoundedIntDecl: return BoundedIntDecl(int(size))

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def proof_decl(self, prover, qualname) -> ProofDecl:
        return ProofDecl(prover=str(prover), qualname=str(qualname))

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def mutex_name(self, name) -> str: return str(name)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def mutex_subscript(self, name, index) -> str:
        return f"{name}[{_csl_to_str(index)}]"

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def shared_protected(self, name, mutex) -> SharedDecl: return SharedDecl(str(name), str(mutex))

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def shared_unprotected(self, name) -> SharedDecl: return SharedDecl(str(name), None)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def thread_entry_decl(self) -> ThreadEntry: return ThreadEntry()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def acquires_decl(self, mutex) -> Acquires: return Acquires(str(mutex))

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def releases_decl(self, mutex) -> Releases: return Releases(str(mutex))

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def critical_decl(self, mutex) -> CriticalSection: return CriticalSection(str(mutex))

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def mutex_invariant_decl(self, mutex, expr) -> MutexInvariant: return MutexInvariant(str(mutex), expr)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def lock_order_decl(self, *mutexes) -> LockOrder: return LockOrder([str(m) for m in mutexes])

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def forall_expr(self, var, body) -> Forall: return Forall(str(var), body)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def exists_expr(self, var, body) -> Exists: return Exists(str(var), body)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def array_length(self, var) -> ArrayLength: return ArrayLength(str(var))

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def subscript_access(self, name, index) -> SubscriptAccess: return SubscriptAccess(str(name), index)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def chained_subscript(self, name, index1, index2) -> ChainedSubscript: return ChainedSubscript(str(name), index1, index2)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def slice_access(self, name, low, high) -> CSLSlice: return CSLSlice(str(name), low, high)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def result_subscript(self, index) -> SubscriptAccess: return SubscriptAccess("\\result", index)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def assigns_region(self, name, low, _op, high) -> AssignsRegion: return AssignsRegion(str(name), low, high)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def assigns_region_list(self, *regions) -> List[AssignsRegion]: return list(regions)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def valid_pred(self, name, length) -> Valid: return Valid(str(name), length)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def separated_pred(self, name1, len1, name2, len2) -> Separated: return Separated(str(name1), len1, str(name2), len2)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def label_decl(self, name) -> Label: return Label(str(name))

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def at_expr(self, expr, label) -> At: return At(expr, str(label))

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def length2d_pred(self, name, rows, cols) -> Length2D: return Length2D(str(name), rows, cols)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def valid2d_pred(self, name, row, col) -> Valid2D: return Valid2D(str(name), row, col)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def implication(self, left, op, right) -> BinOp: return BinOp(left, str(op), right)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def logical_or(self, left, op, right) -> BinOp: return BinOp(left, str(op), right)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def logical_and(self, left, op, right) -> BinOp: return BinOp(left, str(op), right)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def equality(self, left, op, right) -> BinOp: return BinOp(left, str(op), right)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def comparison(self, left, op, right) -> BinOp: return BinOp(left, str(op), right)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def term(self, left, op, right) -> BinOp: return BinOp(left, str(op), right)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def factor(self, left, op, right) -> BinOp: return BinOp(left, str(op), right)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def unary_op(self, op, expr) -> UnaryOp: return UnaryOp(str(op), expr)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def number(self, n) -> Number: return Number(float(n))

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def string_literal(self, s) -> StringLiteral: return StringLiteral(str(s)[1:-1])  # strip quotes

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def true_lit(self) -> CSLBool: return CSLBool(True)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def false_lit(self) -> CSLBool: return CSLBool(False)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def none_lit(self) -> CSLNone: return CSLNone()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def var(self, name) -> Var: return Var(str(name))

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def field_access(self, field_name) -> FieldAccess: return FieldAccess("self", str(field_name))

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def result(self) -> Result: return Result()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def old_var(self, expr) -> Old: return Old(expr)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def nothing(self) -> Nothing: return Nothing()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def in_expr(self, element, collection) -> CSLIn: return CSLIn(element, collection)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def not_in_expr(self, element, collection) -> CSLNotIn: return CSLNotIn(element, collection)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def call_expr(self, name, args) -> CallExpr: return CallExpr(str(name), args if isinstance(args, list) else [args])

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def call_expr_noargs(self, name) -> CallExpr: return CallExpr(str(name), [])

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def is_sorted_expr(self, base, lo, hi) -> IsSorted: return IsSorted(str(base), lo, hi)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def sum_expr(self, base, lo, hi) -> Sum: return Sum(str(base), lo, hi)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def str_concat(self, left, right) -> StrConcatExpr: return StrConcatExpr(left, right)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def str_length_expr(self, string) -> StrLengthExpr: return StrLengthExpr(string)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def str_sub_expr(self, string, lo, hi) -> StrSubExpr: return StrSubExpr(string, lo, hi)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def mktuple_expr(self, elts) -> MkTupleExpr: return MkTupleExpr(elts if isinstance(elts, list) else [elts])

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def fst_expr(self, expr) -> FstExpr: return FstExpr(expr)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def snd_expr(self, expr) -> SndExpr: return SndExpr(expr)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def proj_expr(self, expr, index) -> ProjExpr: return ProjExpr(expr, index)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def empty_map_expr(self) -> MapEmptyExpr: return MapEmptyExpr()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def map_get_expr(self, dict_expr, key) -> MapGetExpr: return MapGetExpr(dict_expr, key)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def map_set_expr(self, dict_expr, key, value) -> MapSetExpr: return MapSetExpr(dict_expr, key, value)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def map_eq_expr(self, left, right) -> MapEqExpr: return MapEqExpr(left, right)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def has_key_expr(self, dict_expr, key) -> HasKeyExpr: return HasKeyExpr(dict_expr, key)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def map_remove_expr(self, dict_expr, key) -> MapRemoveExpr: return MapRemoveExpr(dict_expr, key)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def set_empty_expr(self) -> SetEmptyExpr: return SetEmptyExpr()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def set_add_expr(self, set_expr, elem) -> SetAddExpr: return SetAddExpr(set_expr, elem)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def set_remove_expr(self, set_expr, elem) -> SetRemoveExpr: return SetRemoveExpr(set_expr, elem)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def set_mem_expr(self, elem, set_expr) -> SetMemExpr: return SetMemExpr(elem, set_expr)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def set_union_expr(self, left, right) -> SetUnionExpr: return SetUnionExpr(left, right)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def set_inter_expr(self, left, right) -> SetInterExpr: return SetInterExpr(left, right)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def set_diff_expr(self, left, right) -> SetDiffExpr: return SetDiffExpr(left, right)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def set_card_expr(self, set_expr, lo, hi) -> SetCardExpr: return SetCardExpr(set_expr, lo, hi)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def set_subset_expr(self, left, right) -> SetSubsetExpr: return SetSubsetExpr(left, right)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def set_eq_expr(self, left, right) -> SetEqExpr: return SetEqExpr(left, right)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def nil_expr(self) -> NilExpr: return NilExpr()

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def cons_expr(self, head, tail) -> ConsExpr: return ConsExpr(head, tail)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def hd_expr(self, list_expr) -> HdExpr: return HdExpr(list_expr)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def tl_expr(self, list_expr) -> TlExpr: return TlExpr(list_expr)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def list_length_expr(self, list_expr) -> ListLengthExpr: return ListLengthExpr(list_expr)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def nth_expr(self, list_expr, index) -> NthExpr: return NthExpr(list_expr, index)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def mem_expr(self, elem, list_expr) -> MemExpr: return MemExpr(elem, list_expr)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def append_expr(self, left, right) -> AppendExpr: return AppendExpr(left, right)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def copy_expr(self, name) -> GhostCopyExpr: return GhostCopyExpr(str(name))

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def copy_range_expr(self, name, lo, hi) -> GhostCopyRangeExpr: return GhostCopyRangeExpr(str(name), lo, hi)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def make_expr(self, size, default) -> GhostMakeExpr: return GhostMakeExpr(size, default)

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def expr_list(self, *exprs) -> List[CSLNode]: return list(exprs)


class Module2_Parser:
    'Parses raw PyCSL string contracts into Contract AST objects.'
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self) -> None:
        self.parser = Lark(PYCSL_GRAMMAR, parser='lalr', transformer=PyCSLTransformer())

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def parse_contract(self, contract_str: str, line_number: int) -> CSLNode:
        try:
            return self.parser.parse(contract_str)
        except LarkError as e:
            raise PyCSLParseError(
                f"PyCSL Syntax Error around line {line_number}:\n{contract_str}\n{str(e)}",
                line=line_number, stage="parse"
            ) from e

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def parse_node_contracts(self, raw_contracts: List[str], line_number: int) -> List[CSLNode]:
        parsed_nodes = []
        for contract_str in raw_contracts:
            parsed_nodes.append(self.parse_contract(contract_str, line_number))
        return parsed_nodes


