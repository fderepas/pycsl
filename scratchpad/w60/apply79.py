import io, sys
P = "src/pycsl/frontend/module5/construction_synth.py"
src = io.open(P, encoding="utf-8").read()

OLD = """            pset = set(init_params) | set(kwonly_params)
            if not pset:
                break
"""

NEW = '''            pset = set(init_params) | set(kwonly_params)
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
            #     C([1,2,3]).n    #@ ensures \\result == 0   <-- PROVED; CPython returns 3
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
'''

assert src.count(OLD) == 1, "anchor not unique: %d" % src.count(OLD)
io.open(P, "w", encoding="utf-8").write(src.replace(OLD, NEW))
print("patched", P)
