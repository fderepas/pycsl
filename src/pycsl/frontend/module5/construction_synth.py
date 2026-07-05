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
        for child in node.body:
            if not (isinstance(child, ast.FunctionDef) and child.name == '__init__'):
                continue
            init_params = [a.arg for a in child.args.args if a.arg != 'self']
            pset = set(init_params)
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
