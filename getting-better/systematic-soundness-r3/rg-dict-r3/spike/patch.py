# Spike S1 (dict-value-model-r3-impl.md): LOG-ONLY R-gate instrumentation of the #349 hashing pass.
# Never raises; appends one row per UNDERIVABLE hashed leaf to $PYCSL_RG_LOG.
# Columns: file, function, line, kind (UND | NONE | UND-IT), claimed (0/1), guarded (#383g, 0/1),
#          hashed leaf, site.
import sys
p = sys.argv[1]
s = open(p).read()
anchor = "                    # (#381 / #382 / #383) each outside class name by its real class: a\n"
assert s.count(anchor) == 1
log = r'''                    if __import__("os").environ.get("PYCSL_RG_LOG"):
                        _rgl = []
                        _rgq = [_h349] if id(_h349) not in _xe394 else []
                        while _rgq:
                            _rgy = _rgq.pop()
                            if isinstance(_rgy, _ast341.Tuple):
                                _rgq.extend(_rgy.elts)
                            elif isinstance(_rgy, _ast341.NamedExpr):
                                _rgq.append(_rgy.value)
                            elif isinstance(_rgy, _ast341.IfExp):
                                _rgq.extend([_rgy.body, _rgy.orelse])
                            else:
                                _rgc = set(_ex346.get(id(_rgy), set())) | set(_eh372.get(id(_rgy), set()))
                                if isinstance(_rgy, _ast341.Name):
                                    _rgc |= _dt365.get(_rgy.id, set())
                                if isinstance(_rgy, (_ast341.List, _ast341.ListComp, _ast341.Dict,
                                                     _ast341.DictComp, _ast341.Set, _ast341.SetComp)):
                                    _rgc.add("#UB")
                                if "#UND" in _rgc:
                                    _rgl.append(("UND", _rgy))
                                elif not _rgc:
                                    _rgl.append(("NONE", _rgy))
                        if id(_h349) in _xe394 and "#UND" in _hc349:
                            _rgl.append(("UND-IT", _h349))
                        if _rgl:
                            _rgsl = source_code.splitlines()
                            _rgdl = min([_d.lineno for _d in _f346.decorator_list] + [_f346.lineno])
                            _rgi = _rgdl - 2
                            _rgcl = 0
                            while _rgi >= 0 and _rgsl[_rgi].lstrip().startswith("#@"):
                                _rgt = _rgsl[_rgi].strip()
                                if _rgt.startswith("#@ no_exception") and (
                                        "\\all" in _rgt or "TypeError" in _rgt
                                        or "Exception" in _rgt.replace("no_exception", "")):
                                    _rgcl = 1
                                _rgi -= 1
                            with open(__import__("os").environ["PYCSL_RG_LOG"], "a") as _rgf:
                                for _rgk, _rgy in _rgl:
                                    _rgf.write("\t".join([str(args.file), (_ec346 + "." if _ec346 else "") + _f346.name,
                                        str(getattr(_n346, "lineno", 0)), _rgk, str(_rgcl),
                                        "1" if id(_n346) in _gr383g else "0",
                                        _ast341.unparse(_rgy).replace("\t", " ")[:120],
                                        _ast341.unparse(_n346).replace("\t", " ").replace("\n", " ")[:160]]) + "\n")
'''
s = s.replace(anchor, log + anchor)
open(p, "w").write(s)
print("patched")
