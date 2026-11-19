# OPEN ROUTE #400 — S1 ADMITS ast.NodeVisitor / NodeTransformer, BUT `visit` IS AN ABSTRACT CALL WITH NO EFFECT ON self
**Status: OPEN, Severity 1.** Red-team round 31 (2026-10-26, probes around systematic rules S1/GD/TC/SB and the §7.46/§7.47 hash rules); driver-reproduced on 7859e8fb0 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt31/driver-repro.txt`).
Witnesses `witnesses-r400/`: `n32_nodevisitor_assigns_nothing.py`.

```
#400 S1 ADMITS ast.NodeVisitor / NodeTransformer, BUT `visit` IS AN ABSTRACT CALL WITH NO EFFECT ON self  [slips past S1 BASE-MODEL]
  n32  V(ast.NodeVisitor) with a contracted visit_Constant (n += 1); f: v = V(); v.visit(ast.parse("1")); return v.n,
       ensures \result == 0 PROVED                                                                CPython 1
  WhyML: `let _ = (v_visit_1 (ast_parse_1 ..)) in (); v.n` -- the dispatch to visit_* is dropped, v's fields are framed.
  (n14 / n16, the same with an uncontracted visit_* method, FAIL: the auto-frame of visit_Constant itself is false.)
  REPAIR: model `self.visit(x)` / `generic_visit` on a NodeVisitor subclass as a call that may run ANY visit_* method of
  the class (havoc the union of their `assigns`, require their preconditions, propagate their raises), or drop
  NodeVisitor/NodeTransformer from the BASE-MODEL table for code that calls visit.

DOCUMENTED RESIDUALS MEASURED LIVE (PROVED, CPython violation)
  c23  §7.47: `t: tuple` holding a list, {t} no_exception                                       TypeError
  g24  §7.43: base from a USER module (`class Base: k = 5` in gddep.py), getattr(r, "k", 0) == 0    5

CORRECTLY REFUSED / FAILED (selection)
--------------------------------------
- S1 evasions: alias `UL = collections.UserList`, conditional / version-guarded alias, `type([])`, importlib,
  sys.modules, __import__, IfExp, `*BASES`, walrus, `cast(type, ..)`, `base()`, getattr(collections, ..), `__builtins__.list`,
  `[].__class__`, `{}.__class__`, `NS.B`, `UserList.__mro__[0]`, class decorator returning UserList, functional
  namedtuple base, `Generic[T], UD` alias -- all refused (R341 / S1 / name-binding rules) (a01-a48, a64, a69, a70).
  Re-export through a user module / user star import / dependency alias: hashing refused (#381 unknown base); the truthiness
  consequence `if d:` is ill-typed for records (a37-a42). types.new_class / type(..,..) / make_dataclass / functional
  IntEnum: lowered as `int`, goal unprovable (a65-a68). IntEnum/Flag/int-mixin falsiness and StrEnum/IntEnum == int:
  ill-typed (a55-a59). Main-only subclass of a FIELD-LESS base (a49-a51): base lowered to int, goal unprovable.
- Hash (§7.46/§7.47): Starred `{*xs}`, set.update/union/intersection_update (mutation refusals), dict(zip(..)) /
  dict([(k, v)]) / OrderedDict / defaultdict (ill-typed or refused), lru_cache/cache (refused), Counter / fromkeys over
  calls (not modelled), `xs in d.keys()`, {d.keys()}, every annotation spelling of a list (Optional/Union/PEP 604 `int | list[int]`/`list[int]`
  generics/string/`type` alias/TypeAlias/NewType/Annotated/Iterable/Collection/Sized/Container/Reversible/TypeVar/PEP 695/
  Buffer), BoolOp / display-index / sorted / min / setcomp sources (h14-h21), `m[0]` of List[Any], #383 guard rule
  (c21), user __hash__/__eq__ raising at sets of records (ill-typed: sets are of int), `k in d` with a raising user
  __eq__/__hash__ (R252 assert false), eq=False / plain identity-hash dict round-trips (refused as erased or ill-typed).
- GD: __getattr__ / __getattribute__ (own or mixin), type(self).k / cls.k / R.k stores, setattr aliases / builtins.setattr /
  operator.setitem(vars(..)), external instance stores, mangled `_R__k` of R itself, dunder getattr (__module__,
  __class__), getattr on int / class object / module (abstract, unprovable), NamedTuple/Generic/NodeVisitor/Exception
  base attributes (n36-n38) -- refused or unprovable.
- TC: Protocol via asname, typing.Protocol attribute, Protocol[T], PEP 695 class, nested shadow of Protocol/TypedDict,
  structural Protocol call dispatch (t09-t12, t14-t16) -- refused / ill-typed.
- SB: starred / ** into sorted/min/max/round/list/enumerate/range/int via plain names refused; list.sort(**), str/dict
  method stars (ill-typed or mutation refusals).
- Enum/NamedTuple/ABC: E(n) lookup (refused), aliases / auto values / len(E) / IntFlag | (unprovable or refused),
  abstract instantiation (refused), metaclass __call__ (refused, n33).
```

## REPAIR (2026-10-26, e2 executor off 3b2d2e763; code + corpus + docs ffec1ac18 and follow-ups on this branch; inline in `_run_pipeline`, mirror twin `\trusted`, no new def, no emission change, ledger unchanged)
**MEASURED FIRST.** The self-annotation mirror's NodeVisitor users (`Module3_Weaver`, `Module5_IREmitter`, `desugar`, `exec_splice`,
`pure_ast`) all import `frontend.pure_ast as ast` -- a USER module, not the stdlib `ast` -- and the corpus PASS users (0448 / 0450 /
0451 / 0453) call no dispatching `visit`; so neither removing the bases from S1's table nor modelling havoc is needed by any PASS file.
**Design (refusal, the table kept):** when a file class derives (through file classes) from the stdlib `ast.NodeVisitor` /
`NodeTransformer` and it or a file ancestor defines a `visit_*` method (or it is a transformer, which rewrites the tree in place), a
`.visit(..)` / `.generic_visit(..)` call in a verified (non-`\trusted`) function is refused (`PYCSL-R400-NODEVISITOR-DISPATCH`).
Witness 5646 (n32) PROVED at 3b2d2e763 -> REFUSED; controls 5684 (visitor without `visit_*`) and 5685 (`visit_Constant` called
directly, the advice followed; audited FOLLOWABLE) PROVED both. Docs annotations §7.56, translational §T.6.67. Residuals: the havoc
model is not built (a verified caller of a dispatching stdlib visitor is refused); the mirror's own `pure_ast.NodeVisitor` dispatch
(a user-module class) is outside this rule -- `desugar_chained_comparisons` / `splice_constant_exec` declare `assigns \nothing`
around a `NodeTransformer.visit` that rewrites the tree in place, which deserves its own look.
Over-refusal measured (emission sweeps vs a worktree at 3b2d2e763, logs `getting-better/repair-r393-400/gates/`): root corpus 2424 -> 2431 .mlw (7 new controls), 0 MOVED / 0 GONE / 0 APPEARED; python-reference 2186 -> 2186, 0 / 0 / 0; mirror 53 / 53, 0 / 0 / 0 (no OWED proof). The FIRST cut over-refused 3 files, each removed by a justified refinement: mirror `frontend/pure_ast` (`class PyCSLSyntaxError(SyntaxError)` raised `(msg, (file, line, col, text))`: the SyntaxError family is now MODELLED by its constructor shape instead of refused) and corpus 0889 / 0890 (a CONTRACT's `r.n` on a TypedDict is the spec notation for a required key, not a runtime attribute read).
