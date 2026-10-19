# OPEN ROUTE #281 — int -> str OF > 4300 DIGITS RAISES ValueError (sys.int_max_str_digits), UNMODELLED
**Status: OPEN (gen #37, 2026-10-19), Severity 2.** Red-team round 6; driver-reproduced at 78162575 (4 files rc=0; CPython 3.11+ ValueError).
Witnesses `witnesses-r281/`: `str(x)`, `f"{x}"`, `print(x)` under `no_exception \all` / `no_exception ValueError` with
`x = 10**5000`. Repair: an exception trigger (ValueError unless |x| < 10**4300) on every int->decimal-str conversion
(str/f-string/format/print/repr/%d), or a declared model assumption with an opt-in strict mode (#250/#276 precedent).
