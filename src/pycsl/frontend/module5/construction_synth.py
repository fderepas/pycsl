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
        # (#49) ROUTE #83 side-channel — fields whose value at construction time is
        # genuinely UNKNOWN. Reset per class; empty for every constructor whose stores
        # are all top-level, so it is additive and byte-identical there.
        self._init_unknown: List[str] = []
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
            kwonly_defaults = {}
            for _a, _d in zip(child.args.kwonlyargs, child.args.kw_defaults):
                if (isinstance(_d, ast.Constant)
                        and isinstance(_d.value, (int, float))
                        and not isinstance(_d.value, bool)):
                    kwonly_defaults[_a.arg] = int(_d.value)
            self._init_kwonly = (kwonly_params, kwonly_defaults)
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
                        and _ut.value.id == 'self'
                        and _ut.attr not in self._init_unknown):
                    self._init_unknown.append(_ut.attr)
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
                _last79[_t79.attr] = bool(_n79) and not ((_n79 & pset) and _n79 <= pset)
            for _f79, _bad79 in _last79.items():
                if _bad79 and _f79 not in self._init_unknown:
                    self._init_unknown.append(_f79)
            if not pset:
                break
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
                    init_body.append({"field": tgt.attr,
                                      "value": self._py_expr_to_ir(rhs)})
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
        if self._is_dataclass_decorated(node):
            fnames = [stmt.target.id for stmt in node.body
                      if isinstance(stmt, ast.AnnAssign)
                      and isinstance(stmt.target, ast.Name)]
            init_params = list(fnames)
            init_body = [{"field": fn, "value": {"type": "Var", "name": fn}}
                         for fn in fnames]
        return init_params, init_body

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
