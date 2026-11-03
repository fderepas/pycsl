# OPEN ROUTE #538 — (D) TUPLE ORDERING `t < u` OF TWO Tuple[int, Any] PARAMETERS IS PROVED TOTAL: EQUAL HEADS FALL THROUGH TO COMPARING THE Any SLOTS (str vs int) AND RAISE TypeError WHILE `no_exception \all` PROVES (a plain function body, no constructor) (1)
**Status: OPEN, Severity 1.** Red-team round 50 (driver run #4, 2026-11-03, on 9bdb8cf32 = main with routes through #520 landed: 1113 probes g1100-g1109, 1067 CPython-breaching, 342 confirmed in 11 families, default mode; typed / store fail closed 684/684). Census `scratchpad/rt50/census.tsv`; family block from `scratchpad/rt50/FINDINGS.txt`.
Witnesses `witnesses-r538/` (1): `g1105_bf1047_tuple_lt_any.py`.

Driver repro on main ec80c1dbb..437bd08ae (2026-11-03T04:50Z): 11 rt50 exemplars (ba1068 ba1112 ba1047 ba1136 bc1097 bc1119 bc1050 bj1000 bj1041 bf1047 bg1002) rc=0 Verification SUCCESS while CPython breaks the claim (scratchpad/rt50/driver-repro.txt).

```
F10 (D) TUPLE ORDERING `t < u` OF TWO Tuple[int, Any] PARAMETERS IS PROVED TOTAL: EQUAL HEADS FALL THROUGH TO COMPARING THE Any SLOTS (str vs int) AND RAISE TypeError WHILE `no_exception \all` PROVES (a plain function body, no constructor) (1)
  EXEMPLAR: g1105/bf1047_tuple_lt_any.py: `#@ no_exception \all` f(t: Tuple[int, Any], u: Tuple[int, Any]): `return 1 if t < u else 0`
  CPYTHON: bf1047: f((1, "a"), (1, 2)) -> TypeError: '<' not supported between instances of 'str' and 'int'. Controls: sorted / max of List[Tuple[int, Any]] (bf1048 / bf1049) are not proved
  PYCSL CMD: cd /home/fabrice/git/pycsl-rt50 && PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0 /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py /home/fabrice/git/pycsl/scratchpad/rt50/g1105/bf1047_tuple_lt_any.py --import-path src/pycsl  ->  rc=0 'Verification SUCCESS'
  PROBES: g1105/bf1047_tuple_lt_any.py
```
