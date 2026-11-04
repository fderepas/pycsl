# OPEN ROUTE #551 — ROUTE #519 / #529's DECLARED KINDS ARE TRUSTED AT THE CALL SITE: A CALLER PASSING AN `Any`-ANNOTATED LOCAL (BOUND TO AN int) TO A CONSTRUCTOR PARAMETER DECLARED `str` IS NOT JUDGED, AND THE CONSTRUCTOR's `len(s)` IS ADMITTED AT THE DECLARED KIND (6)
**Status: OPEN, Severity 1.** Red-team round 52 (driver run #4, 2026-11-04, on 2ad6cfd15 = main with routes through #539 incl. #521-#526: 1914 probes g1300-g1341, 1836 CPython-breaching, 263 confirmed (probe, mode) pairs in 10 families; the import families F4 / F9 / F10 prove in typed / store too). Census `scratchpad/rt52/census.tsv`; family block from `scratchpad/rt52/FINDINGS.txt`.
Witnesses `witnesses-r551/` (6; dependency modules rt52dep*.py copied beside the probes that import them): `g1303_bd1246_any_into_str_param.py`, `g1313_bn1259_f_any_local.py`, `g1313_bn1260_f_any_call.py`, `g1313_bn1264_f_any_local_none.py`, `g1313_bn1266_f_any_kw.py`, `g1313_bn1269_f_any_list_param.py`.

Driver repro on int28 (= main 9721f9b0a + u19 / u20's #540-#545, landing), 2026-11-04T01:00Z: 10 rt52 exemplars (bb1201 bb1242 bb1258 bc1332 bd1226 bd1246 be1237 bm1200 bt1200 bv1215) rc=0 Verification SUCCESS while CPython breaks the claim (scratchpad/rt52/driver-repro.txt) — so none of these is closed by the pending #540-#545 landing.

```
F6 ROUTE #519 / #529's DECLARED KINDS ARE TRUSTED AT THE CALL SITE: A CALLER PASSING AN `Any`-ANNOTATED LOCAL (BOUND TO AN int) TO A CONSTRUCTOR PARAMETER DECLARED `str` IS NOT JUDGED, AND THE CONSTRUCTOR's `len(s)` IS ADMITTED AT THE DECLARED KIND (6)
  EXEMPLAR: g1303/bd1246_any_into_str_param.py: `class C: def __init__(self, s: str) -> None: self.n = len(s)`; `#@ no_exception \all` `def f(k: int) -> int: v: Any = k; c = C(v); return c.n`
  CPYTHON: bd1246: f(1) -> TypeError: object of type 'int' has no len()
  PYCSL CMD: cd /home/fabrice/git/pycsl-rt52 && PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0 /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py /home/fabrice/git/pycsl/scratchpad/rt52/g1303/bd1246_any_into_str_param.py --import-path src/pycsl  ->  rc=0 'Verification SUCCESS'
  WHY: mlw/bd1246_any_into_str_param.mlw: `let v = ref 0 in v := k; let c = { n = (any int) } in c.n` -- the `Any` local is an int in the model, the construction is a record literal and the str parameter's kind is the judge's premise. Named residual of §7.519 ('the kinds trust declared annotations'), measured. REPAIR: refuse an erased (`Any` / `object`) argument for a constructor parameter whose declared kind the judge relies on.
  PROBES: g1303/bd1246_any_into_str_param.py g1313/bn1259_f_any_local.py g1313/bn1260_f_any_call.py g1313/bn1264_f_any_local_none.py g1313/bn1266_f_any_kw.py g1313/bn1269_f_any_list_param.py
```
