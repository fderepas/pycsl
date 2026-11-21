#!/usr/bin/env python3
"""r1patch.py <expressions.py> -- apply the R1 per-receiver narrowing view to route #567's judge
(`ExpressionEmissionMixin._handle_attribute_expr`). Exact-string edits; aborts if any anchor is not unique."""
import sys

p = sys.argv[1]
s = open(p, encoding="utf-8").read()


def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    if n != cnt:
        sys.exit(f"ANCHOR x{n} (want {cnt}): {old[:120]!r}")
    s = s.replace(old, new)


# E0: the formal parameters of the emitted function (for R1's single-binding test)
rep("""                _body567: Any = []
                for _fn567 in (self.ir.get("functions", []) or []):
                    if (isinstance(_fn567, dict) and _cef567
                            and (_fn567.get("name") == _cef567
                                 or whyml_ident(str(_fn567.get("name", ""))) == _cef567)):
                        _body567 = [_fn567.get("body") or [], _fn567.get("contracts") or {}]
                        break
""", """                _body567: Any = []
                _pp567: Set[str] = set()
                for _fn567 in (self.ir.get("functions", []) or []):
                    if (isinstance(_fn567, dict) and _cef567
                            and (_fn567.get("name") == _cef567
                                 or whyml_ident(str(_fn567.get("name", ""))) == _cef567)):
                        _body567 = [_fn567.get("body") or [], _fn567.get("contracts") or {}]
                        _pp567 = {str(_q) for _q in (_fn567.get("formal_params") or [])}
                        break
""")

# E1: per-test residual accumulator
rep("""                        _bad567 = not _names567
                        _f567: Optional[Set[str]] = set()
""", """                        _bad567 = not _names567
                        _f567: Optional[Set[str]] = set()
                        # (run #6, R1) the attributes a RECEIVER-admitted `ast` class (below) carries
                        # that the emit_ir projectors do NOT read faithfully (the residual narrowing)
                        _u567: Set[str] = set()
""")

# E2: R1 admission, per receiver, in the `ast.<Node>` branch
rep("""                                _ok567 = _ast579 and (_e567.get("attr")
                                                      in (getattr(self, "_AST_CLASS_TO_IR_KIND", None) or {}))
""", """                                _ok567 = _ast579 and (_e567.get("attr")
                                                      in (getattr(self, "_AST_CLASS_TO_IR_KIND", None) or {}))
                                # (run #6) R1 -- THE RECEIVER-TYPED NARROWING VIEW. A resolved `ast.<X>`
                                # (route #579: `ast` bound only by the import of the standard-library
                                # `ast` / pycsl's `frontend.pure_ast`, so X IS that genuine node class)
                                # tested ALONE (not in a tuple) is an IR class ON THIS RECEIVER exactly
                                # when `_handle_isinstance` lowers this very test to a constructor
                                # discriminant of the receiver's model type (the same gates, in the
                                # same order; the pyval arm precedes them all): a `pyast_stmt` local
                                # with X in `_AST_CLASS_TO_STMT_KIND` (`is_<x>_node`), a `py_tparam_node`
                                # parameter with X = ClassDef (`is_classdef_of`), an emit_ir value with
                                # X = Constant under the const-reflect model (`is_constant`), an emit_ir
                                # value with X = UnaryOp in `_const_int_value` (`is_unaryop`). The value
                                # then IS the modelled node, so the fields it carries are not values of
                                # an unknown class. The attributes X carries that the emit_ir projectors
                                # misread stay refused through the whole alias closure (the RESIDUAL
                                # narrowing, keyed apart): an `ast.Constant`'s `.kind` (its `str | None`
                                # field, not the `kind_of` tag), an `ast.UnaryOp`'s `.op` (an operator
                                # object; `op_of` reads only a BinOp's string). A class decided by the
                                # FILE, by a spelling, or by any other receiver is untouched (#567 / #579).
                                if not _ok567 and _ast579 and _e567 is _cls567:
                                    _a0r1 = _x567["args"][0]
                                    _cr1 = _e567.get("attr")
                                    _ur1: Optional[Set[str]] = None
                                    # the receiver's ROOT name must have ONE binding in this body (a
                                    # parameter never rebound, or the target of exactly one `for`),
                                    # so its model type -- the gate's input -- is the same wherever
                                    # the name is bound: the test is lowered where it is judged
                                    _rr1 = _a0r1
                                    while isinstance(_rr1, dict) and _rr1.get("type") in (
                                            "Attribute", "FieldGet"):
                                        _rr1 = _rr1.get("object")
                                    _rn1 = (_rr1.get("name") if isinstance(_rr1, dict)
                                            and _rr1.get("type") == "Var" else None)
                                    _bf1 = 0
                                    _bo1 = 0
                                    if isinstance(_rn1, str) and _rn1:
                                        _sk1: List[Any] = [_body567[0] if _body567 else []]
                                        while _sk1:
                                            _y1 = _sk1.pop()
                                            if isinstance(_y1, list):
                                                _sk1.extend(_y1)
                                                continue
                                            if not isinstance(_y1, dict):
                                                continue
                                            for _ky1, _vy1 in _y1.items():
                                                if isinstance(_vy1, (dict, list)):
                                                    _sk1.append(_vy1)
                                                if not (_vy1 == _rn1 or (isinstance(_vy1, list)
                                                                         and _rn1 in _vy1)):
                                                    continue
                                                if _y1.get("type") == "Var" and _ky1 == "name":
                                                    continue
                                                if _ky1 == "object" and _y1.get("type") in (
                                                        "Attribute", "FieldGet"):
                                                    continue
                                                # an attribute / field NAME, a literal's text, a
                                                # callee: not a binding of the name
                                                if _ky1 in ("attr", "field") or (
                                                        _ky1 == "value" and _y1.get("type") in (
                                                            "String", "Str", "Bytes", "Number",
                                                            "Constant")) or (
                                                        _ky1 == "func" and _y1.get("type") == "Call"):
                                                    continue
                                                if (_y1.get("stmt") in ("For", "ForStmt")
                                                        and _ky1 == "target"):
                                                    _bf1 += 1
                                                else:
                                                    _bo1 += 1
                                    _pm1 = isinstance(_rn1, str) and _rn1 in _pp567
                                    _one1 = _bo1 == 0 and (_bf1 == 1 if not _pm1 else _bf1 == 0)
                                    if _one1 and not self._expr_is_pyval(_a0r1):
                                        if (_cr1 in (getattr(self, "_AST_CLASS_TO_STMT_KIND", None) or {})
                                                and not _pm1
                                                and self._pyast_stmt_child_var(_a0r1) is not None):
                                            _ur1 = set()
                                        elif (_cr1 == "ClassDef" and _pm1 and isinstance(_a0r1, dict)
                                                and _a0r1.get("type") == "Var"
                                                and _a0r1.get("name") in getattr(
                                                    self, "_current_tparam_node_params", set())):
                                            _ur1 = set()
                                        elif (_cr1 == "Constant" and self._uses_const_reflect()
                                                and self._is_emit_ir_expr(_a0r1)):
                                            _ur1 = {"kind"}
                                        elif (_cr1 == "UnaryOp"
                                                and (_cef567 == "_const_int_value"
                                                     or _cef567.endswith("___const_int_value"))
                                                and self._is_emit_ir_expr(_a0r1)):
                                            _ur1 = {"op"}
                                    if _ur1 is not None:
                                        _ok567 = True
                                        _u567 |= _ur1
""")

# E3: record the residual narrowing under its own key space ("\\x00" + path), never widened by a subscript
rep("""                        if _bad567:
                            _p567: List[str] = []
                            _r567 = _x567["args"][0]
""", """                        if _bad567 or _u567:
                            _p567: List[str] = []
                            _r567 = _x567["args"][0]
""")
rep("""                                _k567 = ".".join([_r567["name"]] + _p567[::-1])
                                if _sub567:
                                    # a subscript coarsens the path to its base: the tested value
                                    # is SOME element, whose own fields the key no longer tells
                                    # apart, so every attribute under the key is refused
                                    _f567 = None
                                if _k567 in _nar567 and (_nar567[_k567] is None or _f567 is None):
                                    _nar567[_k567] = None
                                elif _k567 in _nar567:
                                    _nar567[_k567] = (_nar567[_k567] or set()) | (_f567 or set())
                                else:
                                    _nar567[_k567] = _f567
""", """                                _k567 = ".".join([_r567["name"]] + _p567[::-1])
                                if _u567:
                                    # (R1) the residual: the key MAY be (a container of) the admitted
                                    # class; a subscript keeps the set (the element's misread
                                    # attributes are the same)
                                    _zk567 = "\\x00" + _k567
                                    if _zk567 not in _nar567 or _nar567[_zk567] is not None:
                                        _nar567[_zk567] = (_nar567.get(_zk567) or set()) | _u567
                                if _bad567 and _sub567:
                                    # a subscript coarsens the path to its base: the tested value
                                    # is SOME element, whose own fields the key no longer tells
                                    # apart, so every attribute under the key is refused
                                    _f567 = None
                                if not _bad567:
                                    pass
                                elif _k567 in _nar567 and (_nar567[_k567] is None or _f567 is None):
                                    _nar567[_k567] = None
                                elif _k567 in _nar567:
                                    _nar567[_k567] = (_nar567[_k567] or set()) | (_f567 or set())
                                else:
                                    _nar567[_k567] = _f567
""")

# E4: closure -- residual keys propagate under the same edges, keeping their set on the two EXACT-match
# coarse edges (an element of a may-be-X container may be an X); every structure-losing edge widens.
rep("""                        for _vk567, _vc567 in _alts567:
                            for _n567, _nf567 in list(_nar567.items()):
                                # forward: the value is, extends, or is a prefix of a narrowed path
                                if _vk567 == _n567:
                                    _prop567.append((_t567, None if _vc567 else _nf567))
""", """                        for _vk567, _vc567 in _alts567:
                            for _n567, _nf567 in list(_nar567.items()):
                                # (R1) a residual key: same edges, its own key space; the exact-match
                                # coarse edges keep its set
                                _z567 = _n567.startswith("\\x00")
                                _zp567 = "\\x00" if _z567 else ""
                                if _z567:
                                    _n567 = _n567[1:]
                                # forward: the value is, extends, or is a prefix of a narrowed path
                                if _vk567 == _n567:
                                    _prop567.append((_zp567 + _t567,
                                                     None if (_vc567 and not _z567) else _nf567))
""")
rep("""                                    _seg567 = _vk567[len(_n567) + 1:].split(".")[0]
                                    if _nf567 is None or _seg567 in _nf567:
                                        _prop567.append((_t567, None))
                                elif _n567.startswith(_vk567 + "."):
                                    _prop567.append((_t567 if _vc567 else _t567 + _n567[len(_vk567):],
                                                     None if _vc567 else _nf567))
                                # backward: the target is, or is a prefix of, a narrowed path
                                if _t567 == _n567 or _n567.startswith(_t567 + "."):
                                    _prop567.append((_vk567 if _vc567 else _vk567 + _n567[len(_t567):],
                                                     None if _vc567 else _nf567))
                                elif _t567.startswith(_n567 + "."):
                                    # a field store into the narrowed object: the stored value is a
                                    # field value of it (unknown class when the class may carry it)
                                    _seg567 = _t567[len(_n567) + 1:].split(".")[0]
                                    if _nf567 is None or _seg567 in _nf567:
                                        _prop567.append((_vk567, None))
""", """                                    _seg567 = _vk567[len(_n567) + 1:].split(".")[0]
                                    if _nf567 is None or _seg567 in _nf567:
                                        _prop567.append((_zp567 + _t567, None))
                                elif _n567.startswith(_vk567 + "."):
                                    _prop567.append((_zp567 + (_t567 if _vc567
                                                               else _t567 + _n567[len(_vk567):]),
                                                     None if _vc567 else _nf567))
                                # backward: the target is, or is a prefix of, a narrowed path
                                if _t567 == _n567:
                                    _prop567.append((_zp567 + _vk567,
                                                     None if (_vc567 and not _z567) else _nf567))
                                elif _n567.startswith(_t567 + "."):
                                    _prop567.append((_zp567 + (_vk567 if _vc567
                                                               else _vk567 + _n567[len(_t567):]),
                                                     None if _vc567 else _nf567))
                                elif _t567.startswith(_n567 + "."):
                                    # a field store into the narrowed object: the stored value is a
                                    # field value of it (unknown class when the class may carry it)
                                    _seg567 = _t567[len(_n567) + 1:].split(".")[0]
                                    if _nf567 is None or _seg567 in _nf567:
                                        _prop567.append((_zp567 + _vk567, None))
""")
rep("""                    for _new567, _nf567 in _prop567:
                        if len(_new567.split(".")) > 5:
                            _new567 = ".".join(_new567.split(".")[:5])
                            _nf567 = None
""", """                    for _new567, _nf567 in _prop567:
                        if len(_new567.split(".")) > 5:
                            _new567 = ".".join(_new567.split(".")[:5])
                            _nf567 = None
""")

# E5: the hit check reads both key spaces; a residual hit gets its own message (same code)
rep("""                _hit567 = False
                for _n567, _nf567 in _nar567.items():
                    if _k567 == _n567 and (_nf567 is None or attr in _nf567):
                        _hit567 = True
                    elif _k567 is not None and _k567.startswith(_n567 + ".") and (
                            _nf567 is None
                            or _k567[len(_n567) + 1:].split(".")[0] in _nf567):
                        _hit567 = True
""", """                _hit567 = False
                _rhit567 = False
                for _n567, _nf567 in _nar567.items():
                    _z567 = _n567.startswith("\\x00")
                    if _z567:
                        _n567 = _n567[1:]
                    if (_k567 == _n567 and (_nf567 is None or attr in _nf567)) or (
                            _k567 is not None and _k567.startswith(_n567 + ".") and (
                                _nf567 is None
                                or _k567[len(_n567) + 1:].split(".")[0] in _nf567)):
                        if _z567:
                            _rhit567 = True
                        else:
                            _hit567 = True
                # (R1) a residual-only hit is NOT a projector read when it is `<x>.op` and every
                # occurrence of `<x>.op` in this body is the SUBJECT of `isinstance(<x>.op, ast.USub)`
                # that `_handle_isinstance` lowers over the OBJECT (`str_eq_op (unaryop_op_of x)
                # "-"`, its `_const_int_value` arm, `ast` resolved): the projector's lowering of the
                # subject is computed with the call's arguments and discarded, never read.
                if (_rhit567 and not _hit567 and attr == "op" and _k567 is not None
                        and (_cef567 == "_const_int_value" or _cef567.endswith("___const_int_value"))
                        and ((getattr(self, "ir_class_targets_r579", None) or {}).get("ast")
                             in ("ast", "frontend.pure_ast"))):
                    _occ567 = 0
                    _sbj567 = 0
                    _stk567 = [_body567]
                    while _stk567:
                        _x567 = _stk567.pop()
                        if isinstance(_x567, list):
                            _stk567.extend(_x567)
                            continue
                        if not isinstance(_x567, dict):
                            continue
                        _stk567.extend(_x567.values())
                        _ss567: List[Any] = []
                        if (_x567.get("type") == "Call" and _x567.get("func") == "isinstance"
                                and len(_x567.get("args") or []) == 2
                                and isinstance(_x567["args"][1], dict)
                                and _x567["args"][1].get("type") == "Attribute"
                                and _x567["args"][1].get("attr") == "USub"
                                and isinstance(_x567["args"][1].get("object"), dict)
                                and _x567["args"][1]["object"].get("type") == "Var"
                                and _x567["args"][1]["object"].get("name") == "ast"):
                            _ss567 = [_x567["args"][0]]
                        if _x567.get("type") == "Attribute" and _x567.get("attr") == "op":
                            _ss567.append(None)
                        for _s567 in _ss567:
                            _q567 = _x567 if _s567 is None else _s567
                            if not (isinstance(_q567, dict) and _q567.get("type") == "Attribute"
                                    and _q567.get("attr") == "op"):
                                continue
                            # the receiver path, collapsed at a subscript exactly as the judged
                            # read's; a subject must be a plain field path
                            _p567 = []
                            _pure567 = True
                            _r567 = _q567.get("object")
                            while isinstance(_r567, dict) and _r567.get("type") in (
                                    "Attribute", "FieldGet", "Subscript", "SliceAccess"):
                                if _r567.get("type") in ("Attribute", "FieldGet"):
                                    _p567.append(str(_r567.get("attr") or _r567.get("field")))
                                else:
                                    _p567 = []
                                    _pure567 = False
                                _r567 = _r567.get("object") or _r567.get("value")
                            if isinstance(_r567, str) and _r567:
                                _r567 = {"type": "Var", "name": _r567}
                            _kq567 = (".".join([str(_r567.get("name"))] + _p567[::-1])
                                      if isinstance(_r567, dict) and _r567.get("type") == "Var"
                                      else None)
                            if _kq567 != _k567:
                                continue
                            if _s567 is None:
                                _occ567 += 1
                            elif _pure567:
                                _sbj567 += 1
                    # the judged read itself must be a plain field path
                    _r567 = obj_ir
                    while isinstance(_r567, dict) and _r567.get("type") in ("Attribute", "FieldGet"):
                        _r567 = _r567.get("object")
                    if (_occ567 > 0 and _occ567 == _sbj567
                            and ((isinstance(_r567, dict) and _r567.get("type") == "Var")
                                 or (isinstance(_r567, str) and _r567))):
                        _rhit567 = False
""")
rep("""                if _hit567:
                    from errors import PyCSLSemanticError as _R567
                    raise _R567(
                        "PYCSL-R567-EMITIR-ATTR-ON-NONIR: `" + str(_k567)
""", """                if _rhit567 and not _hit567:
                    from errors import PyCSLSemanticError as _R567
                    raise _R567(
                        "PYCSL-R567-EMITIR-ATTR-ON-NONIR: `" + str(_k567) + "." + str(attr)
                        + "` (in `" + str(getattr(self, "_current_emitting_func", None) or "?")
                        + "`) reads a field of a value this function tests with `isinstance` "
                        "against an `ast` node class the model represents as an IR node, but this "
                        "field is not one the IR projectors read faithfully (an `ast.Constant`'s "
                        "`.kind` is its own `str | None` field, not the constructor tag; an "
                        "`ast.UnaryOp`'s `.op` is an operator object) (route #567, the receiver-"
                        "typed view R1). Test the field's value directly (`isinstance(x.op, "
                        "ast.USub)`), or keep the value in a local of the class it really has.",
                        stage="module6-whyml", code="PYCSL-R567-EMITIR-ATTR-ON-NONIR")
                if _hit567:
                    from errors import PyCSLSemanticError as _R567
                    raise _R567(
                        "PYCSL-R567-EMITIR-ATTR-ON-NONIR: `" + str(_k567)
""")

open(p, "w", encoding="utf-8").write(s)
print("patched", p)
