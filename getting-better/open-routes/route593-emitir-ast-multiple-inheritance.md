# OPEN ROUTE #593 — A USER CLASS INHERITING TWO ast NODE CLASSES (class B(ast.Name, ast.Call)) MAKES isinstance(x, ast.Name) and isinstance(x, ast.Call) BOTH TRUE, BUT THE emit_ir MODEL TREATS THE CONSTRUCTORS AS DISJOINT
**Status: REPAIRED (driver run #6, executor u41, branch run6-u41 off ghost-assign-bc6 4e6004f3b after L6; annotations §7.593). Mechanism (front end, `pycsl.py::_run_pipeline` on the standard-library AST, twin `\trusted`; inline, no new def, no axiom): where some name of the source RESOLVES as an IR class / namespace (route #579's table), a class statement may not inherit an IR node class (directly, through an alias, a user-module re-export or a metaclass), and no class may be built another way (`type(name, bases, ns)`, `__new__`, `new_class`, `__class__` / `__bases__` stores, `__mro_entries__`); new `PYCSL-R593-IR-NODE-SUBCLASS`.** Opened as: Status OPEN, Severity 1, pre-existing (red team rt56; Verification SUCCESS on the run #6 base 822621340 and on int55; CPython breaks the claim). Witnesses witnesses-r593/.

## The defect

The emit_ir model lowers `isinstance(<emit_ir>, ast.Name)` to the IR discriminant (`is_var x`), `isinstance(x,
ast.Call)` to another one: the node classes are DISJOINT constructors of one algebraic type there. In CPython a class
may inherit two of them:

    class B(ast.Name, ast.Call): pass
    #@ ensures \result == 0
    def f(self, x: "ExprIR") -> int:
        if isinstance(x, ast.Name) and isinstance(x, ast.Call): return 1
        return 0                               # PROVED; Em().f(B(...)) returns 1

(rt56 hd1767; hd1768 the same with `ast.Attribute`). A one-base subclass is the same hazard in a weaker form: it
keeps the disjointness but may override a node field with a property (rt56 hd1769, refused at base by another rule).

## The repair

RULE (annotations §7.593), in `_run_pipeline` right after route #579's resolution table is built, and only when that
table is non-empty (otherwise no isinstance test is lowered to a discriminant, so a subclass decides nothing):

- (a) BASES. Every class statement's bases and keywords are walked (a `[...]` type argument is skipped). A base name
  is admitted when it is unbound in the file (a builtin: `Exception`, `object`), bound only by class statements of
  this file, or bound only by imports of modules that are not IR modules. A name of an import whose dotted path has a
  component `ast` / `_ast` / `pure_ast` / `ir_schema` / `Module2_Parser` (any alias, `from ast import Name`, a relative
  `from .pure_ast import ...`) is admitted only as the visitors `NodeVisitor` / `NodeTransformer`. A dotted base
  `<root>.<C>` needs an import root (the module's `NodeVisitor` / `NodeTransformer` admitted) or a file class whose
  attribute chain names nested class statements (`class m: X = ast.Name` makes `m.X` an alias). Refused: a base bound
  by any other binding (an assignment alias, a parameter, an `importlib.import_module` result), a name imported from a
  module of the program found OUTSIDE pycsl's own `src/` (it may re-export an IR class or a subclass of one), and a
  `metaclass=` / `**` keyword (a metaclass `__new__` may rewrite the bases).
- (b) NO OTHER CLASS CONSTRUCTION: a Load of `type` (or `builtins.type`) other than as the callee of `type(x)`, inside
  an annotation / a `[...]` type argument, or as the class argument of `isinstance` / `issubclass` (a callee with
  other arity and an attribute receiver `type.__new__` are refused even there); a call through `__new__` /
  `__class__` / `new_class`; a store to `.__class__` / `.__bases__`; a `__mro_entries__` definition.

Message: names the class and the base (or the construct) and the reason; advice "wrap the node in a class of your own
instead of subclassing it, and name base classes directly" (audited FOLLOWABLE, below).

MIRROR: the first spelling collected every Name `type`, including the STORE of a TypedDict field `type: str`
(`module6_whyml/statements.py` `ValIRBoolView`, `stmt_control_flow.py`): both mirrors went GONE in the first head
mirror sweep. Made exact (only a Load of `type` is a use of the builtin), not exempted; then 53/53 identical.

RESIDUAL (named): a subclass defined in ANOTHER module and handed to `f` by a caller there (this file imports
nothing of it) is outside the per-file view; the model's premise "an `ExprIR` value is a genuine node" is the
self-annotation's, stated in route #579's table.

## Witnesses and measurements

- rt56 witnesses (`--no-proof` front end, default / typed / store): hd1767, hd1768 6/6 REFUSED R593 (at base 4e6004f3b
  EMITTED; the driver measured both PROVED on pycsl-base6, `scratchpad/run6/rt56-base6b.tsv`).
- u41 probes `witnesses-r593/u41-probes/` (all CPython-breaching except p593j): `from ast import Name, Call` (p593e)
  and a second module alias `import ast as A` (p593f) REFUSED R593 x 3 models; the one-base `class B(ast.Name)`
  (p593j, CPython honest for that claim) REFUSED R593 x 3 (by design, fail-closed). The alias / `type(...)` /
  metaclass / nested-attribute / `importlib` / starred-tuple / `T = type` / `__mro_entries__` / `types.new_class`
  shapes (p593a-d, g-i, k, l) are REFUSED x 3 by PRE-EXISTING rules (route #341's base-by-name rule, the
  class-construction rules) before R593 runs; R593 (b) is their second line.
- CORPUS (expected FAIL): 9650 (hd1767), 9651 (hd1768), 9652 (p593e), 9653 (p593f): PROVED at base 4e6004f3b in the
  default model (full proof, measured), REFUSED R593 x 3 models at HEAD. CONTROLS (expected PASS, the disjoint claim
  proved through the IR model): 9663 (bases `ast.NodeVisitor`, `Exception`, a file class) and 9664 (R593's advice:
  the node wrapped in a file class, = `witnesses-r593/advice/a593_wrap_node.py`) PROVED at base and HEAD.
- rt56 families g1730 / g1740 (277 probes, `--no-proof`, default model): the only verdict changes are R593 refusals
  of probes that define a two-node-class subclass: hd1767 / hd1768 / hf1734 / hf1737 (CPython-breaching, EMIT-OK at
  triage), hf1736 (was a Why3 type error) and hf1735 (CPython-honest for its one input; its file defines `class
  B2(ast.Name, ast.Call)`, exactly the refused shape, and its claim `\result == 1` is false for an `ast.Call` input
  anyway).
- INERTNESS: see the route #595 doc (one landing; same sweeps).
