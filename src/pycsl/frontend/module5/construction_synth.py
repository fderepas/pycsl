from __future__ import annotations

from frontend import pure_ast as ast
from typing import Any, Dict, List, Tuple


class ConstructionSynthMixin:
    """Record / namedtuple construction synthesis feeding Tier-A parametrized
    construction (base_op.md / collections-plan).

    Extracted verbatim from `Module5_IREmitter.PyCSLToJSONEmitter` as a sibling
    mixin under `module5/` (Part B move 3, mirroring `module6_whyml/`). Composed
    into `PyCSLToJSONEmitter`, which supplies `self.program_ir` and
    `self._py_expr_to_ir`."""

    @staticmethod
    def _namedtuple_fields(arg: ast.expr) -> List[str]:
        """Parse a `namedtuple` fields arg into a list of field names, or [] if it is
        not a compile-time literal (a list/tuple of str constants, or a space/comma
        separated `"x y"` / `"x, y"` string). A non-literal fields arg → [] (no record
        synthesised; the factory stays opaque)."""
        if isinstance(arg, (ast.List, ast.Tuple)):
            names: List[str] = []
            for e in arg.elts:
                if isinstance(e, ast.Constant) and isinstance(e.value, str):
                    names.append(e.value)
                else:
                    return []
            return names
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return arg.value.replace(",", " ").split()
        return []

    def _synthesize_namedtuple_records(self, node: ast.Module) -> None:
        """collections-plan: a module-level `Name = namedtuple('Name', <fields>)` becomes
        a record type_decl (all fields `int`) with an implicit `__init__(self, f1, …)`
        that sets `self.fi = fi`. So `Name(a, b)` reuses the Tier-A parametrized record
        construction (`{f1 = a; f2 = b}`) and `p.fi` is a record-field read. Only literal
        fields are recognised; a dynamic fields arg synthesises nothing."""
        for stmt in node.body:
            if not (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                    and isinstance(stmt.targets[0], ast.Name)
                    and isinstance(stmt.value, ast.Call)):
                continue
            call = stmt.value
            fn = call.func
            is_nt = ((isinstance(fn, ast.Name) and fn.id == "namedtuple")
                     or (isinstance(fn, ast.Attribute) and fn.attr == "namedtuple"))
            if not is_nt or len(call.args) < 2:
                continue
            fields = self._namedtuple_fields(call.args[1])
            if not fields:
                continue
            name = stmt.targets[0].id
            self.program_ir["type_decls"].append({
                "kind": "record", "name": name,
                "fields": [{"name": f, "type": "int", "mutable": True} for f in fields],
                "class_invariants": [], "field_defaults": {f: 0 for f in fields},
                "has_hash": False, "has_eq": False, "is_unhashable": False,
                "constants": {}, "bases": [],
                "init_params": list(fields),
                "init_body": [{"field": f, "value": {"type": "Var", "name": f}}
                              for f in fields],
            })

    def _collect_init_construction(
            self, node: ast.ClassDef) -> Tuple[List[str], List[Dict[str, Any]]]:
        """Capture `__init__`'s formal params and its *param-dependent* field
        initialisers, for parametrized record construction `C(a, b)` (base_op.md
        Tier A). Returns (init_params, init_body):

          init_params : the `__init__` formals minus `self`, in order.
          init_body   : [{"field", "value"}] for each TOP-LEVEL `self.x = <rhs>`
                        whose `<rhs>` references at least one param and ONLY params
                        (free names ⊆ init_params). `value` is the lowered IR.

        Soundness: only flat top-level assignments are captured (no control flow —
        a conditional/looping init can't be reduced to a single record literal), and
        only RHS over params/literals (an RHS touching a local, a method call, or
        another field would not be substitutable at the construction site). Anything
        outside this shape is omitted, and that field falls back to its default
        witness in `_call_record_constructor` (sound, just less precise). Constant
        RHS (e.g. `self.start = 7`) is already handled by `field_defaults`, so it is
        intentionally NOT re-captured here."""
        init_params: List[str] = []
        init_body: List[Dict[str, Any]] = []
        # (#49) ROUTE #82 side-channel, reset per class so a constructor with no
        # keyword-only parameter emits nothing new (additive -> byte-identical).
        self._init_kwonly = ([], {})
        # (#49) ROUTE #149 side-channel: POSITIONAL parameter defaults, and the names of
        # every parameter (either kind) whose default is not an int this model can state.
        self._init_posdef = ({}, [])
        # (#49) ROUTE #83 side-channel — fields whose value at construction time is
        # genuinely UNKNOWN. Reset per class; empty for every constructor whose stores
        # are all top-level, so it is additive and byte-identical there.
        self._init_unknown: List[str] = []
        # (#49) ROUTE #89 — A SEPARATE, NARROWER CHANNEL FOR THE COLLECTION ARMS.
        # `_init_unknown` mixes TWO different reasons a field's value is unknown: route
        # #83's "stored inside control flow" and route #79's "top-level RHS names something
        # outside the parameter set". For a SCALAR both reasons are equally fatal, so one
        # list was enough. FOR A COLLECTION THEY ARE NOT THE SAME: `_array_init_size`
        # captures a COMPUTED RHS's LENGTH faithfully (`self.buf = bytearray(4096)` really
        # does give a 4096-element array), so honouring #79's reason in the list arm would
        # destroy a true capability. MEASURED — the first build of #89's repair consulted
        # `_init_unknown` and moved corpus 0452, whose `self.buf: list = bytearray(4096)` is
        # a SINGLE TOP-LEVEL STORE: its `\length(self.buf) >= 4096` class invariant stopped
        # holding at construction. THE BYTE-DIFF CAUGHT IT AND THE REPAIR WAS NARROWED
        # RATHER THAN THE CORPUS RE-PRICED. This list carries ONLY the reasons that defeat
        # a length capture too — a store nested in control flow (#83) and an augmented
        # store (#88) — because in both of those the straight-line literal is not the
        # field's value AT ALL, length included.
        self._init_unknown_cf: List[str] = []
        # (#49) ROUTE #150 side-channel, reset per class: the constructor can change
        # `self` by some means other than a recognized store, so NO field's value at
        # construction time is known. Consumed by `visit_ClassDef`, which widens the two
        # unknown lists to every field.
        self._init_opaque150: bool = False
        # (#49) ROUTE #150 — the argument IR of a LEADING `super().__init__(<args>)`
        # statement, composed faithfully by `apply_inheritance`; None when absent.
        self._init_super150: Any = None
        # A `@dataclass` whose SYNTHESIZED `__init__` calls `self.__post_init__()`.
        if (self._is_dataclass_decorated(node)
                and not self._dc_decorator_init_false(node)
                and not any(isinstance(_c150, ast.FunctionDef) and _c150.name == "__init__"
                            for _c150 in node.body)
                and any(isinstance(_c150, ast.FunctionDef)
                        and _c150.name == "__post_init__" for _c150 in node.body)):
            self._init_opaque150 = True
        # (#49) ROUTE #144 side-channel, reset per class: True only when the
        # `init_params` below were SYNTHESIZED from a `@dataclass`'s own field
        # declarations (no explicit `__init__`) — the one case in which Python also
        # inherits the BASE dataclasses' fields into the synthesized signature, so
        # `ir_resolve.apply_inheritance` may prepend them. False for every class with
        # an explicit `__init__` (its declared signature is the whole truth) and for
        # every non-dataclass, so the key is absent there and the IR of the corpus,
        # the mirror and all 38 frozen conformance goldens is byte-identical.
        self._init_dc_synth: bool = False
        # (#49) ROUTE #144 — THIS class's own `@dataclass` FIELD list, which is what a
        # DERIVED dataclass inherits. It is computed here, for EVERY `@dataclass`, and
        # not from `init_params` below, because the two differ exactly where it matters:
        # a `@dataclass` that ALSO writes an explicit `__init__` keeps that `__init__`
        # (`dataclasses._set_new_attribute` never overwrites a class attribute) but STILL
        # publishes `__dataclass_fields__`, so a subclass of it inherits these names even
        # though the class's own `init_params` are the explicit signature. `ClassVar`
        # members are excluded here for the same reason as below (PEP 557 pseudo-fields).
        # (#49) ROUTE #146 — A KEYWORD-ONLY `@dataclass` FIELD IS NOT A POSITIONAL ONE,
        # AND KEEPING IT IN THE POSITIONAL LIST SHIFTS EVERY BINDING AFTER IT. Python
        # 3.10 added THREE spellings, and all three change the ORDER of the synthesized
        # `__init__`'s positional parameters:
        #   `@dataclass(kw_only=True)`        every field is keyword-only;
        #   `x: int = field(kw_only=True)`    that one field is (and `kw_only=False`
        #                                     forces a field back to positional);
        #   `_: KW_ONLY`                      a SENTINEL pseudo-field: it is not a field
        #                                     at all and every field AFTER it is kw-only.
        # MEASURED at `2887ba44`, PROVING with CPython contradicting:
        #     @dataclass
        #     class Pee:
        #         xfld: int = field(kw_only=True, default=0)
        #         yfld: int = 0
        #     Pee(5, xfld=1).yfld    #@ ensures \result == 0   <-- PROVED; CPython gives 5
        # because `yfld` is Python's FIRST positional parameter while the model made it
        # the second, bound `xfld` from the 5, and then let the explicit `xfld=1` keyword
        # overwrite it — leaving `yfld` on its default. The keyword-only names go out on
        # route #82's EXISTING channel (`init_kwonly_params`/`init_kwonly_defaults`),
        # which binds BY NAME ONLY and can never take a positional argument.
        # CENSUS of `kw_only` / `KW_ONLY` over the two corpora, the 53 mirrors and
        # `pycsl_lib`: ONE file, `src/pycsl_lib/dc/__init__.py`, and that is the STUB
        # DECLARING `field(...)`, not a use — so this is byte-inert.
        _dcpos: List[str] = []
        _dckw: List[str] = []
        _dckwd: Dict[str, Any] = {}
        if self._is_dataclass_decorated(node):
            _kwall = self._dc_decorator_kw_only(node)
            _sentinel = False
            for stmt in node.body:
                if not (isinstance(stmt, ast.AnnAssign)
                        and isinstance(stmt.target, ast.Name)):
                    continue
                if self._ann_is_classvar(stmt.annotation):
                    continue
                if self._ann_is_kw_only_sentinel(stmt.annotation):
                    _sentinel = True
                    continue
                _fk = self._dc_field_kw_only(stmt.value)
                if _fk if _fk is not None else (_kwall or _sentinel):
                    _dckw.append(stmt.target.id)
                    _dv = self._dc_default_const(stmt.value)
                    if _dv is not None:
                        _dckwd[stmt.target.id] = _dv
                else:
                    _dcpos.append(stmt.target.id)
        # (#49) ROUTE #144 — THIS class's own `@dataclass` FIELD list, which is what a
        # DERIVED dataclass inherits. It is computed here, for EVERY `@dataclass`, and
        # not from `init_params` below, because the two differ exactly where it matters:
        # a `@dataclass` that ALSO writes an explicit `__init__` keeps that `__init__`
        # (`dataclasses._set_new_attribute` never overwrites a class attribute) but STILL
        # publishes `__dataclass_fields__`, so a subclass of it inherits these names even
        # though the class's own `init_params` are the explicit signature. `ClassVar`
        # members are excluded (PEP 557 pseudo-fields) and keyword-only fields travel in
        # their own list so a subclass inherits them as keyword-only too.
        self._init_dc_fields: List[str] = _dcpos
        self._init_dc_kwonly: List[str] = _dckw
        for child in node.body:
            if not (isinstance(child, ast.FunctionDef) and child.name == '__init__'):
                continue
            # (#49) ROUTE #82 — `ast.arguments.args` HOLDS ONLY THE PLAIN
            # POSITIONAL-OR-KEYWORD PARAMETERS. Python keeps the other two kinds in
            # the SIBLING fields `posonlyargs` and `kwonlyargs`, and reading only
            # `args` silently means "this constructor has no parameters" for a
            # keyword-only `__init__`: `pset` came back EMPTY, the `if not pset:
            # break` below fired, `init_params`/`init_body` were empty, and EVERY
            # field fell through to `_field_default`'s literal `0`. MEASURED:
            #     class P:
            #         v: int
            #         def __init__(self, *, v: int = 0) -> None: self.v = v
            #     P(v=7).v     #@ ensures \result == 0   <-- PROVED; CPython gives 7
            # The TRUE twin was refused, a POSITIONAL-ONLY `(v, /)` behaved
            # identically, the stale `0` DISCHARGED a callee's `requires`, and the
            # CONTROL — the same class, field, value and clause with an ORDINARY
            # POSITIONAL parameter — was FAITHFUL IN BOTH DIRECTIONS. Only the
            # parameter KIND changed.
            #
            # THE TWO LISTS ARE KEPT SEPARATE ON PURPOSE. `init_params` is consumed
            # by `_call_record_constructor` as the POSITIONAL binding list
            # (`args[i]` binds `init_params[i]`), so appending the keyword-only
            # names to it would bind them FROM POSITIONAL ARGUMENTS — something
            # Python never does, i.e. a DIFFERENT wrong model in place of the old
            # one. Positional-only and positional-or-keyword parameters DO bind
            # positionally and belong in `init_params`, in Python's own order;
            # keyword-only names go out separately as `init_kwonly_params` for the
            # WL-07 by-name binding. `pset` — which only decides whether an RHS is
            # EXPRESSIBLE from the constructor's parameters — sees all three kinds.
            init_params = [a.arg for a in
                           (child.args.posonlyargs + child.args.args)
                           if a.arg != 'self']
            kwonly_params = [a.arg for a in child.args.kwonlyargs
                             if a.arg != 'self']
            # A keyword-only parameter OMITTED at the call site takes its DEFAULT,
            # and the literal `0` is right only when that default happens to be 0
            # (measured: `*, v: int = 5` with `P()` proved `\result == 0` where
            # CPython returns 5). Capture the CONSTANT defaults so the omitted case
            # is faithful too; a non-constant default stays omitted and is route
            # #79's class, not this one.
            #
            # (#49) ROUTE #149 — AN OMITTED ARGUMENT TAKES ITS PARAMETER'S DEFAULT, OF
            # EITHER KIND, AND ROUTE #82 COVERED ONE KIND AND ONE SPELLING. MEASURED at
            # `acba66f3`, each `Cy().r` read PROVING a false `== 0`:
            #   * a POSITIONAL `def __init__(self, r: int = 5)` — the IR carried no
            #     positional defaults at all, so the record literal took the field's
            #     witness 0 (and a zero-argument call never entered the binding block);
            #   * a keyword-only default that is a MODULE CONSTANT (`*, r: int = K`) —
            #     "a non-constant default stays omitted and is route #79's class": no
            #     route #79 arm reads parameter defaults, so it too took the witness 0;
            #   * a keyword-only `True` — the capture excluded `bool`, and `True` is 1;
            #   * a keyword-only `2.5` — `int()` TRUNCATED it to 2 (route #148).
            # One rule for both kinds: an int, a bool, an integral float or a folded
            # negative literal is CAPTURED; any other default makes the fields that
            # parameter initialises UNKNOWN when the argument is omitted.
            kwonly_defaults = {}
            _posdef149: Dict[str, int] = {}
            _dunk149: List[str] = []
            _pos149 = [a.arg for a in (child.args.posonlyargs + child.args.args)]
            _pairs149 = [(_n, _d, True) for _n, _d in zip(
                _pos149[len(_pos149) - len(child.args.defaults):], child.args.defaults)]
            _pairs149 += [(_a.arg, _d, False) for _a, _d in zip(
                child.args.kwonlyargs, child.args.kw_defaults) if _d is not None]
            for _n149, _d149, _ispos149 in _pairs149:
                _v149 = None
                if isinstance(_d149, ast.Constant) and isinstance(_d149.value, bool):
                    _v149 = int(_d149.value)
                elif isinstance(_d149, ast.Constant) and isinstance(_d149.value, int):
                    _v149 = _d149.value
                elif (isinstance(_d149, ast.Constant) and isinstance(_d149.value, float)
                        and _d149.value.is_integer()):
                    _v149 = int(_d149.value)
                elif self._const_int_value(_d149) is not None:
                    _v149 = self._const_int_value(_d149)
                if _v149 is None:
                    _dunk149.append(_n149)
                elif _ispos149:
                    _posdef149[_n149] = _v149
                else:
                    kwonly_defaults[_n149] = _v149
            self._init_kwonly = (kwonly_params, kwonly_defaults)
            self._init_posdef = (_posdef149, _dunk149)
            # (#49) ROUTE #150 — A CONSTRUCTOR'S EFFECTS OUTSIDE ITS RECOGNIZED STORES ARE
            # NOT IN THE RECORD LITERAL, SO THE LITERAL MAY NOT STATE ANY FIELD AS KNOWN.
            # MEASURED at `acba66f3`, each `== 1` (or `== 0`) PROVED while CPython gives the
            # post-effect value: `self._setup()` storing the field; `me = self; me.x = 7`;
            # `setattr(self, "x", 7)`; `init_p(self)`; `super().__init__(k + 100)`; and a
            # `@dataclass`'s `__post_init__` (flagged above). One rule: a `super()` call,
            # any call whose callee or arguments mention `self` (except a small set of pure
            # builtins over it), or ANY other load of the bare name `self` (an alias, a
            # container element, a return) makes every field UNKNOWN.
            _pure150 = {"len", "abs", "min", "max", "int", "str", "bool", "float",
                        "isinstance", "range", "list", "dict", "set", "frozenset", "tuple",
                        "sorted", "sum", "any", "all", "hash", "repr", "ord", "chr"}
            # A LEADING `super().__init__(<positional args>)` (after an optional docstring)
            # is not opaque: `apply_inheritance` composes the base constructor's binding
            # into this one, which keeps goldens 0442/0443 (`super().__init__()` first)
            # faithful rather than unknown. Any other `super()` use stays opaque.
            _lead150 = [_st for _st in child.body
                        if not (isinstance(_st, ast.Expr)
                                and isinstance(_st.value, ast.Constant)
                                and isinstance(_st.value.value, str))]
            _skip150 = None
            if _lead150 and isinstance(_lead150[0], ast.Expr):
                _sc150 = _lead150[0].value
                if (isinstance(_sc150, ast.Call)
                        and isinstance(_sc150.func, ast.Attribute)
                        and _sc150.func.attr == "__init__"
                        and isinstance(_sc150.func.value, ast.Call)
                        and isinstance(_sc150.func.value.func, ast.Name)
                        and _sc150.func.value.func.id == "super"
                        and not _sc150.func.value.args
                        and not _sc150.keywords
                        and not any(isinstance(_a, ast.Starred) for _a in _sc150.args)):
                    _skip150 = _sc150
                    self._init_super150 = [self._py_expr_to_ir(_a) for _a in _sc150.args]
            _attr_roots150 = set()
            for _n150 in ast.walk(child):
                if isinstance(_n150, ast.Attribute) and isinstance(_n150.value, ast.Name):
                    _attr_roots150.add(id(_n150.value))
            _skipids150 = ({id(_x) for _x in ast.walk(_skip150)} - {id(_a2) for _a in _skip150.args for _a2 in ast.walk(_a)}
                           if _skip150 is not None else set())
            for _n150 in ast.walk(child):
                if id(_n150) in _skipids150:
                    continue
                if isinstance(_n150, ast.Call):
                    _fn150 = _n150.func
                    _root150 = _fn150
                    while isinstance(_root150, (ast.Attribute, ast.Subscript)):
                        _root150 = _root150.value
                    if (isinstance(_root150, ast.Call) and isinstance(_root150.func, ast.Name)
                            and _root150.func.id == "super"):
                        self._init_opaque150 = True
                        break
                    if isinstance(_root150, ast.Name) and _root150.id == "self":
                        self._init_opaque150 = True
                        break
                    _mentions150 = any(
                        isinstance(_m150, ast.Name) and _m150.id == "self"
                        for _a150 in list(_n150.args) + [_k.value for _k in _n150.keywords]
                        for _m150 in ast.walk(_a150))
                    if _mentions150 and not (isinstance(_fn150, ast.Name)
                                             and _fn150.id in _pure150):
                        self._init_opaque150 = True
                        break
                elif (isinstance(_n150, ast.Name) and _n150.id == "self"
                      and isinstance(_n150.ctx, ast.Load)
                      and id(_n150) not in _attr_roots150):
                    # a bare `self` that is not the root of an attribute: an alias, an
                    # argument (already handled above for calls), a container element...
                    self._init_opaque150 = True
                    break
            # (#49) ROUTE #83 — A FIELD STORED INSIDE CONTROL FLOW IS NOT MERELY
            # UNCAPTURED, ITS VALUE IS UNKNOWN, AND EMITTING A LITERAL `0` FOR IT IS A
            # DEFINITE FALSE FACT. The loop below is TOP-LEVEL ONLY (`for stmt in
            # child.body`), by the docstring's own reasoning that "a conditional/looping
            # init can't be reduced to a single record literal". That reasoning is right
            # about the REPRESENTATION and wrong about the CONSEQUENCE: the field then
            # fell through to `_field_default`'s literal `0`. MEASURED:
            #     class C:
            #         v: int
            #         def __init__(self, n: int) -> None:
            #             self.v: int = 0
            #             if n > 0:
            #                 self.v = n
            #     C(7).v      #@ ensures \result == 0   <-- PROVED; CPython returns 7
            # The TRUE twin was refused; an UN-ANNOTATED store behaves identically (so
            # this is NOT the `AnnAssign` hole it was predicted to be); a `while` store
            # is a third carrier; and the stale `0` DISCHARGED a callee's `requires`.
            # Collected here and emitted as an UNCONSTRAINED value at the allocation
            # site — which is what "sound, just less precise" would have meant all along.
            # (#49) ROUTE #88 — AN `AugAssign` TO A FIELD IS INVISIBLE TO EVERY CAPTURE
            # PATH, AND THAT MAKES A **NESTED** ONE A SURVIVOR OF ROUTE #83's REPAIR.
            # The walk below tests `ast.Assign` / `ast.AnnAssign` only, and
            # `Module5_IREmitter._collect_class_fields` does the same, so
            #     self.n = 0
            #     self.n += 5              # or:  if k > 0: self.n += 5
            # left the field at its literal `0` and `C(7).n == 0` PROVED where CPython
            # returns 5 — BOTH spellings measured, both directions, the true twin refused.
            # A carrier that SURVIVES a landed repair is a SECOND ROUTE, not a failed
            # repair (gen #10's generator 2). An augmented store is never reducible to a
            # record literal, so the field's value at construction time is genuinely
            # UNKNOWN and `(any int)` is the faithful answer — the same conclusion #83
            # reached for a conditional store. Census: ZERO `self.<f> op= ...` sites in
            # `__init__` across corpus, mirror, src/pycsl and src/pycsl_lib, so additive.
            for _ag in ast.walk(child):
                if not isinstance(_ag, ast.AugAssign):
                    continue
                _at = _ag.target
                if (isinstance(_at, ast.Attribute)
                        and isinstance(_at.value, ast.Name)
                        and _at.value.id == 'self'):
                    if _at.attr not in self._init_unknown:
                        self._init_unknown.append(_at.attr)
                    if _at.attr not in self._init_unknown_cf:
                        self._init_unknown_cf.append(_at.attr)   # (#49) ROUTE #89
            _top_ids = {id(_st) for _st in child.body}
            for _st in ast.walk(child):
                if id(_st) in _top_ids:
                    continue
                _ut = None
                if isinstance(_st, ast.Assign) and len(_st.targets) == 1:
                    _ut = _st.targets[0]
                elif isinstance(_st, ast.AnnAssign):
                    _ut = _st.target
                if (isinstance(_ut, ast.Attribute)
                        and isinstance(_ut.value, ast.Name)
                        and _ut.value.id == 'self'):
                    if _ut.attr not in self._init_unknown:
                        self._init_unknown.append(_ut.attr)
                    if _ut.attr not in self._init_unknown_cf:
                        self._init_unknown_cf.append(_ut.attr)   # (#49) ROUTE #89
            pset = set(init_params) | set(kwonly_params)
            # (#49) ROUTE #79 — A TOP-LEVEL FIELD INITIALISER WHOSE RHS NAMES ANYTHING
            # OUTSIDE THE PARAMETER SET IS NOT MERELY UNCAPTURED, ITS VALUE IS UNKNOWN,
            # AND THE LITERAL `0` IT USED TO GET IS A DEFINITE FALSE FACT. The capture
            # rule below keeps only an RHS over `pset`; everything else was omitted and
            # `_field_default` supplied `rec_info['defaults'].get(fn, 0)`. The docstring
            # calls that "sound, just less precise". IT IS NOT LESS PRECISE, IT IS WRONG:
            # "less precise" is an unconstrained value, a literal `0` is a definite claim
            # and the emitter proves postconditions from it. MEASURED:
            #     class C:
            #         n: int
            #         def __init__(self, items: List[int]) -> None:
            #             self.n = len(items)
            #     C([1,2,3]).n    #@ ensures \result == 0   <-- PROVED; CPython returns 3
            # Three carriers, all the same erasure site reached by a different RHS: a
            # BUILTIN (`len(items)`), a MODULE CONSTANT (`n + K`), and ANOTHER SELF FIELD
            # (`self.a + 1`). The CONTROL bounds it exactly — an RHS over parameters ONLY
            # (`self.x = n + 1`) is captured and is FAITHFUL IN BOTH DIRECTIONS, and a
            # LITERAL RHS (`self.w = 5`) is faithfully carried by `field_defaults`. So the
            # defect is exactly "the RHS references a free name the record literal cannot
            # substitute", which is the complement of the rule already computed below.
            #
            # THE UNIT IS THE FIELD'S **LAST** TOP-LEVEL STORE, NOT THE STORE. A field
            # written twice must be judged by the write that decides its value; keying on
            # any-store would mark a field unknown because of a line a later line overwrote.
            #
            # SCOPE — WHY THIS IS CHEAPER THAN ITS RECORDED PRICE. The emission site in
            # `module6_whyml/expressions.py` already guards on `field_types not in
            # _NONSCALAR`, so list/dict/set fields CANNOT be reached by this at all.
            # Measured over corpus + mirror + compiler + stdlib: 113 class-(iii) sites, of
            # which only 40 are SCALAR and can move — src/pycsl 18, src/pycsl_lib 14,
            # src/self-annotate 8, and **ZERO in the verified corpus** (every uncaptured
            # corpus field is a literal or an array). The array arm is not an unpaid cost,
            # it is a cost the emitter already fences.
            #
            # This runs BEFORE the `if not pset: break` ON PURPOSE: a constructor with NO
            # parameters never reached the capture loop at all, so EVERY one of its
            # computed fields silently took the literal `0` — the widest form of the
            # defect, and it is invisible to any census that starts from the capture rule.
            _last79: Dict[str, bool] = {}
            for _s79 in child.body:
                _t79 = _r79 = None
                if isinstance(_s79, ast.Assign) and len(_s79.targets) == 1:
                    _t79, _r79 = _s79.targets[0], _s79.value
                elif isinstance(_s79, ast.AnnAssign) and _s79.value is not None:
                    _t79, _r79 = _s79.target, _s79.value
                if not (isinstance(_t79, ast.Attribute)
                        and isinstance(_t79.value, ast.Name)
                        and _t79.value.id == 'self'):
                    continue
                _n79 = {n.id for n in ast.walk(_r79) if isinstance(n, ast.Name)}
                # A LITERAL RHS (no free names) is deliberately NOT marked: it is carried
                # faithfully by `field_defaults`, and marking it would throw away a true
                # value — the #82 lesson that a faithful capture beats an unconstrained
                # one wherever the information exists.
                # (#49) ROUTE #139 — ... AND THE EXEMPTION'S PREMISE IS A CLAIM ABOUT A
                # COLLECTOR NOBODY RE-READ. "A LITERAL RHS is carried faithfully by
                # `field_defaults`" is true only of the shapes `field_defaults` MATCHES:
                # an `ast.Constant` int/float, a `_const_int_value` fold, an
                # `_array_init_size` length — and, through the route #85/#86/gap2a
                # channels, a Dict / Set / List / Tuple / str Constant / collection call.
                # Python's parser does not fold, so `self.start = -7` (UnaryOp) and
                # `self.start = 2 + 3` (BinOp) are name-free, unmatched, unmarked, and
                # fell to the DEFINITE witness 0: `\result == 0` PROVED while CPython
                # returned -7 and 5 (the true twin `== -7` was refused). The unary-minus
                # half is now carried FAITHFULLY by `field_defaults`; a name-free RHS
                # that is still a COMPUTED expression is marked UNKNOWN here, which is
                # the fail-closed half. CENSUS of name-free unmatched RHS over the four
                # trees: 59 — 42 Dict, 14 Constant (str/None), 1 Set, all carried by
                # their own channels, plus 2 UnaryOp (`-1`, in the mirror's own
                # `frontend/__init__.py`) which the `field_defaults` fix now carries.
                # So this arm's live population is 0 and it is a pure ratchet.
                _lit79 = isinstance(_r79, (ast.Constant, ast.Dict, ast.Set, ast.List,
                                           ast.Tuple))
                # (#49) ROUTE #148 — a NON-INTEGRAL float Constant is not carried by
                # `field_defaults` (it used to be, TRUNCATED), so it is not exempt.
                if (isinstance(_r79, ast.Constant) and isinstance(_r79.value, float)
                        and not _r79.value.is_integer()):
                    _lit79 = False
                if not _lit79 and isinstance(_r79, ast.Call) and isinstance(_r79.func, ast.Name):
                    _lit79 = _r79.func.id in ("set", "frozenset", "dict", "list",
                                              "bytearray", "bytes", "tuple")
                if not _lit79:
                    _lit79 = (self._const_int_value(_r79) is not None
                              or self._array_init_size(_r79) is not None)
                _last79[_t79.attr] = ((bool(_n79)
                                       and not ((_n79 & pset) and _n79 <= pset))
                                      or (not _n79 and not _lit79))
            for _f79, _bad79 in _last79.items():
                if _bad79 and _f79 not in self._init_unknown:
                    self._init_unknown.append(_f79)
            if not pset:
                break
            # (#49) ROUTE #88 — THIS LOOP USED TO **APPEND**, SO AN EARLIER
            # PARAM-DEPENDENT STORE SURVIVED A LATER ONE THAT SUPERSEDED IT. MEASURED,
            # and this is the direction that shows the model has no notion of store
            # ORDER at all rather than a preference for literals:
            #     def __init__(self, k: int) -> None:
            #         self.n = k
            #         self.n = 3
            #     C(7).n      #@ ensures \result == 7   <-- PROVED; CPython returns 3
            # The true twin (`== 3`) was refused. Keyed by FIELD and last-wins: a later
            # store that the capture rule cannot express (a literal — which
            # `field_defaults` now carries last-wins too — or anything else) sets the
            # slot back to None rather than popping it, so a field's position in
            # `init_body` stays at its FIRST capture and a single-store constructor
            # emits byte-identically. Census: ZERO fields with two top-level stores in
            # corpus, mirror, src/pycsl or src/pycsl_lib.
            _cap88: Dict[str, Any] = {}
            for stmt in child.body:  # top-level only — no ast.walk
                tgt = rhs = None
                if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
                    tgt, rhs = stmt.targets[0], stmt.value
                elif isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
                    tgt, rhs = stmt.target, stmt.value
                if not (isinstance(tgt, ast.Attribute)
                        and isinstance(tgt.value, ast.Name)
                        and tgt.value.id == 'self'):
                    continue
                names = {n.id for n in ast.walk(rhs) if isinstance(n, ast.Name)}
                # param-dependent AND only over params (no other free names)
                if names and (names & pset) and names <= pset:
                    _cap88[tgt.attr] = self._py_expr_to_ir(rhs)
                elif tgt.attr in _cap88:
                    _cap88[tgt.attr] = None
            for _f88, _v88 in _cap88.items():
                if _v88 is not None:
                    init_body.append({"field": _f88, "value": _v88})
            return init_params, init_body
        # WL-07 (wrong-lowering-to-fix.md §WL-07 @dataclass ctor arg-drop, a
        # severity-1 UNSOUNDNESS): a `@dataclass` with NO explicit `__init__` has
        # its constructor SYNTHESIZED by Python — `__init__(self, f1, …, fn)` binds
        # each declared field from the same-position positional arg, in
        # field-DECLARATION order. Before this fix the loop above found no
        # `__init__`, returned empty init_params/init_body, and
        # `_call_record_constructor` fell EVERY field back to its zero/default —
        # so `Point(1, 2).x` emitted `{ x = 0; y = 0 }` and a driver could PROVE
        # `Point(1, 2).x == 0`, a claim FALSE of real Python (`.x` is `1`). Here we
        # synthesize the same `init_params` (the class-body AnnAssign fields in
        # declaration order) and `init_body` (`self.<field> = <field-param>`) that
        # an explicit positional `__init__` would carry, so `_call_record_constructor`
        # threads the args into the fields EXACTLY like a NamedTuple / recognized
        # `Tuple` / explicit-`__init__` positional class. A field WITHOUT a default
        # bound past the provided arity, or a non-scalar (list/dict/set) field, is
        # handled by `_call_record_constructor` (positional-prefix binding + typed
        # default) — sound. Additive: a non-dataclass class with no `__init__` is
        # untouched (empty init, prior behaviour).
        if (self._is_dataclass_decorated(node)
                and not self._dc_decorator_init_false(node)):
            # (#49) ROUTE #144, SHAPE B — A `ClassVar` MEMBER IS AN `ast.AnnAssign` BUT IS
            # **NOT** AN `__init__` PARAMETER, SO INCLUDING IT SHIFTS THE WHOLE POSITIONAL
            # BINDING BY ONE AND EVERY FIELD TAKES ITS *NEIGHBOUR'S* ARGUMENT. Measured at
            # `2887ba44` on
            #     @dataclass
            #     class P:
            #         k: ClassVar[int] = 10
            #         x: int
            #         y: int
            #     P(1, 2).x     #@ ensures \result == 2   <-- PROVED; CPython gives 1
            # This is strictly worse than shape A below: it is not a lost default, it is a
            # DEFINITE WRONG VALUE silently taken from the neighbouring argument. Python's
            # `@dataclass` skips a `ClassVar`-annotated member when it synthesizes
            # `__init__` (PEP 557: "pseudo-field"), so we skip it here. The member stays a
            # `fields` entry (typed `classvar`) with its `field_defaults` value, so the
            # class-level constant is still readable — only the BINDING LIST loses it.
            init_params = list(self._init_dc_fields)
            init_body = [{"field": fn, "value": {"type": "Var", "name": fn}}
                         for fn in (list(self._init_dc_fields)
                                    + list(self._init_dc_kwonly))]
            # (#49) ROUTE #146 — the keyword-only fields leave on route #82's channel.
            if self._init_dc_kwonly:
                self._init_kwonly = (list(self._init_dc_kwonly), dict(_dckwd))
            # (#49) ROUTE #144, SHAPE A — the side-channel that lets `ir_resolve`'s
            # inheritance merge PREPEND the base dataclasses' parameters. It marks
            # "this class's `init_params` were SYNTHESIZED from its own field
            # declarations", which is exactly the case in which Python's synthesized
            # `__init__` also inherits the bases' fields. A class with an EXPLICIT
            # `__init__` must NOT be merged — its signature is whatever it declares,
            # base fields included or not — and the `return` above leaves the flag at
            # its per-class `False`.
            self._init_dc_synth = True
        return init_params, init_body

    @staticmethod
    def _ann_is_classvar(ann: Optional[ast.expr]) -> bool:
        """(#49) ROUTE #144 — is this annotation a `ClassVar` / `ClassVar[T]`?

        Both the bare name (`from typing import ClassVar`) and the dotted spelling
        (`typing.ClassVar[int]`) are recognized, subscripted or not. A STRING
        annotation (`"ClassVar[int]"`, PEP 563) is deliberately NOT matched: it is
        not parsed anywhere else in this front end either, and answering False keeps
        the member in `init_params`, which is the PRE-EXISTING behaviour — this
        predicate only ever REMOVES a member from the binding list, never adds one.
        """
        if ann is None:
            return False
        base = ann.value if isinstance(ann, ast.Subscript) else ann
        if isinstance(base, ast.Name):
            return base.id == "ClassVar"
        if isinstance(base, ast.Attribute):
            return base.attr == "ClassVar"
        return False

    @staticmethod
    def _ann_is_kw_only_sentinel(ann) -> bool:
        """(#49) ROUTE #146 — is this annotation the bare `KW_ONLY` sentinel?

        `_: KW_ONLY` is a PSEUDO-FIELD: it declares no field of its own and makes every
        member declared AFTER it keyword-only. It is never subscripted, so only the bare
        `Name`/`Attribute` spellings are matched.
        """
        if isinstance(ann, ast.Name):
            return ann.id == "KW_ONLY"
        if isinstance(ann, ast.Attribute):
            return ann.attr == "KW_ONLY"
        return False

    @staticmethod
    def _dc_decorator_kw_only(node) -> bool:
        """(#49) ROUTE #146 — does the `@dataclass(...)` decorator pass `kw_only=True`?"""
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            target = dec.func
            if not ((isinstance(target, ast.Name) and target.id == "dataclass")
                    or (isinstance(target, ast.Attribute)
                        and target.attr == "dataclass")):
                continue
            for kw in dec.keywords:
                if kw.arg == "kw_only" and isinstance(kw.value, ast.Constant):
                    return bool(kw.value.value)
        return False

    @staticmethod
    def _dc_decorator_init_false(node) -> bool:
        """(#49) ROUTE #147, gen #29 carrier — does `@dataclass(...)` pass `init=False`?

        `dataclasses` then generates NO `__init__`, so the class keeps the one it
        declares or INHERITS the first one in its MRO — it is route #147's case, not
        the SYNTHESIZE arm. Measured before this check, `@dataclass(init=False)` over a
        plain base whose `__init__` stores `afld + 100`: `Cee(7).get() == 0` PROVED,
        CPython 107. Only a CONSTANT keyword is read (the `kw_only=` convention above);
        census of `dataclass(... init=` over both corpora, the 53 mirrors, `src/pycsl`
        and `src/pycsl_lib`: ZERO.
        """
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            target = dec.func
            if not ((isinstance(target, ast.Name) and target.id == "dataclass")
                    or (isinstance(target, ast.Attribute)
                        and target.attr == "dataclass")):
                continue
            for kw in dec.keywords:
                if kw.arg == "init" and isinstance(kw.value, ast.Constant):
                    return not bool(kw.value.value)
        return False

    @staticmethod
    def _dc_field_kw_only(value):
        """(#49) ROUTE #146 — a field's OWN `kw_only=` override, or None when it has none.

        `field(kw_only=True)` makes exactly this field keyword-only and
        `field(kw_only=False)` forces it back to positional, overriding BOTH the
        class-level `kw_only=True` and a preceding `KW_ONLY` sentinel — which is why
        this returns a THREE-valued answer and the caller only falls back to the
        class-level rule on None.
        """
        if not isinstance(value, ast.Call):
            return None
        fn = value.func
        if not ((isinstance(fn, ast.Name) and fn.id == "field")
                or (isinstance(fn, ast.Attribute) and fn.attr == "field")):
            return None
        for kw in value.keywords:
            if kw.arg == "kw_only" and isinstance(kw.value, ast.Constant):
                return bool(kw.value.value)
        return None

    @staticmethod
    def _dc_default_const(value):
        """(#49) ROUTE #146 — the INT value of a field's declared default, or None.

        Unwraps `field(default=<x>)` first (the dataclass spelling), then accepts a
        numeric literal or a unary-minus literal. A `default_factory`, a bare `field()`
        and any non-constant default answer None, so the omitted keyword falls to
        `_field_default` rather than to a fabricated witness.
        """
        if isinstance(value, ast.Call):
            fn = value.func
            if ((isinstance(fn, ast.Name) and fn.id == "field")
                    or (isinstance(fn, ast.Attribute) and fn.attr == "field")):
                value = next((k.value for k in value.keywords
                              if k.arg == "default"), None)
        if isinstance(value, ast.Constant) and isinstance(value.value, (int, float)):
            return int(value.value)
        if (isinstance(value, ast.UnaryOp) and isinstance(value.op, ast.USub)
                and isinstance(value.operand, ast.Constant)
                and isinstance(value.operand.value, (int, float))):
            return -int(value.operand.value)
        return None

    def _collect_init_contract_check(self, node: ast.ClassDef) -> Dict[str, Any]:
        """(#43) ROUTE #15 — a constructor's `#@ requires` / `#@ ensures` is never checked.

        `__init__` is not emitted as a function: it is INLINED at each allocation site, so
        its clauses go nowhere. MEASURED: `#@ ensures self.x == 99` over a body `self.x = 0`
        printed *All contracts formally proven*, and `#@ requires 1 == 2` was discarded the
        same way. The inlining itself is FAITHFUL (a caller-side claim that leans on the
        false postcondition correctly FAILS, single-file and cross-file), so this is the
        tool reporting success for work it did not do rather than an unsoundness — #33's
        category for the dangling-block finding.

        Returns the material Module 6 needs to emit a CHECKING-ONLY
        `let <class>__init (<params>) : <class>` beside the inlining, or `{}` when there is
        nothing to check. EMITTED ONLY WHEN A CLAUSE IS NON-TRIVIAL: `#@ requires True` /
        `#@ ensures True` carry no information and are legitimately normalized away, and
        ALL 24 of the mirror's constructor contracts are exactly that — so this field is
        absent for every mirror file and the whole 53-file re-proof battery never arises.
        Census: 34 non-trivial constructor contracts tree-wide, 13 in the reference corpus
        and 21 in `src/pycsl_lib`, ZERO in `src/self-annotate/src`.

        `param_types` is carried because `init_params` is a list of NAMES only and
        `__init__` — never being emitted as a function — is absent from Module 6's
        `_module_method_param_whyml_types`, so the types cannot be recovered downstream.
        """
        for child in node.body:
            if not (isinstance(child, ast.FunctionDef) and child.name == '__init__'):
                continue
            def _nontrivial(clauses):
                out = []
                for c in clauses:
                    ir = self._csl_to_ir(c.expr)
                    if (isinstance(ir, dict) and ir.get("type") in ("Bool", "True")
                            and ir.get("value") in (True, 1, "True")):
                        continue
                    if isinstance(ir, dict) and ir.get("type") == "Var" \
                            and ir.get("name") == "True":
                        continue
                    out.append(ir)
                return out
            reqs = _nontrivial(getattr(child, 'csl_requires', []) or [])
            enss = _nontrivial(getattr(child, 'csl_ensures', []) or [])
            if not reqs and not enss:
                return {}
            def _ann_text(a):
                """The annotation as SOURCE TEXT, for the shapes a constructor parameter
                actually uses. Deliberately NOT `arg_type` from `_scan_function_scope`:
                that derivation is entangled with the symbol table, and Module 6 only needs
                enough to pick a WhyML type. Anything unrecognized yields "", which Module 6
                treats as `int` — the same default `_param_type_str` already uses."""
                if a is None:
                    return ""
                if isinstance(a, ast.Name):
                    return a.id
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    return a.value
                if isinstance(a, ast.Attribute):
                    return a.attr
                if isinstance(a, ast.Subscript):
                    _base = _ann_text(a.value)
                    _sl = getattr(a, "slice", None)
                    if isinstance(_sl, ast.Tuple):
                        return _base + "[" + ", ".join(_ann_text(e) for e in _sl.elts) + "]"
                    return _base + "[" + _ann_text(_sl) + "]"
                return ""
            _pt = {}
            for _a in list(child.args.args)[1:]:          # skip `self`
                _pt[_a.arg] = _ann_text(getattr(_a, "annotation", None))
            return {"requires": reqs, "ensures": enss, "param_types": _pt}
        return {}

    def _collect_init_ensures(self, node: ast.ClassDef) -> List[Dict[str, Any]]:
        """Capture the constructor's `#@ ensures` clauses (fresh_globals.md / the
        `#@ fresh_globals` directive). These are the CONSTRUCTOR POST-STATE facts
        (`\\forall k. (0<=k<64) ==> self.fd_open[k] == 0`) that:

          1. `_emit_module_globals` re-checks as a GOAL against each module-global
             singleton's literal initializer (so the fact is PROVEN of the freshly
             constructed global — never an arbitrary literal), and
          2. `#@ fresh_globals` on a confined standalone driver re-establishes as an
             ASSUMED entry fact (sourced from this PROVEN ensures).

        `self` is left symbolic in the IR; the consumers substitute `self -> <global>`.
        Returns [] for a class with no `__init__` ensures (byte-identical to before)."""
        for child in node.body:
            if isinstance(child, ast.FunctionDef) and child.name == '__init__':
                return [self._csl_to_ir(e.expr)
                        for e in getattr(child, 'csl_ensures', [])]
        return []
