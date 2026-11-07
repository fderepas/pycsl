# OPEN ROUTE #426 — FORMAT SPECS OF AN f-STRING: INT -> FLOAT / %c CONVERSIONS OWE NO OverflowError 
**Status: REPAIRED, Severity 1.** Red-team round 33 (2026-10-27, convergence measurement after the run #3 allow-list repairs; 653 screened / 385 fully proved / 116 confirmed); driver-reproduced on main (see `scratchpad/rt33/driver-repro.txt`).
Witnesses `witnesses-r426/` (13): `e09_fstring_spec_f_int.py`, `e12_fstring_spec_c_big.py`, `f00_c_neg.py`, `f01_c_range.py`, `f10_int_e_big.py`, `f11_int_g_big.py`, `f12_int_pct_big.py`, `m01_fspec_E.py`, `m02_fspec_dote.py`, `m03_fspec_F.py`, `m04_fspec_G.py`, `m05_fspec_dot2f.py`, `m06_fspec_plus_e.py`.

```
#426 FORMAT SPECS OF AN f-STRING: INT -> FLOAT / %c CONVERSIONS OWE NO OverflowError   [slips past §7.71 / §7.82]   (13)
  e09  f"{n:f}" for n = 10**400 under no_exception \all PROVED                                    CPython OverflowError
  f10 {n:e}  f11 {n:g}  f12 {n:%}  m01 {n:E}  m02 {n:.1e}  m03 {n:F}  m04 {n:G}  m05 {n:.2f}  m06 {n:+e}   (int too large to
       convert to float -- the same bound §7.82 imposes on float(n))
  e12  f"{n:c}" n = 10**20 (C long)   f00 f"{n:c}" n = -1   f01 n = 0x110000   (%c arg not in range(0x110000))
  (The ValueError specs -- {n:.3}, {n:s}, {s:=5}, {n:,_}, {s:x}, nested widths, {n:d} past 4300 digits -- all FAIL: the
  ValueError rows are checked; only the OverflowError conversions are missing. format() / str.format are refused.)
  REPAIR: a FormattedValue whose spec has a float presentation type (e E f F g G % or none with a precision) over an
  int-read operand owes §7.82's `-DBL_MAX <= n <= DBL_MAX`; type `c` owes `0 <= n < 0x110000`; any other spec over an int
  operand that is not a literal-checked integer presentation (d x X o b n , _) is refused.
```

## REPAIR (executor g3, driver run #3, 2026-10-27, off ac28806be; annotations §7.115, translational §T.6.126)

In the literal-spec arm of the FormattedValue lowering (expressions.py, mirror twin `\trusted`): an operand SHOWN int with a float presentation type owes `-DBL_MAX <= n <= DBL_MAX` under `\all`; `c` owes `0 <= n < 0x110000` under `\all` (else the `chr` ValueError row); both registered in `r417_obls` and counted by the driver's erased-obligation census (FormattedValue nodes added). Non-int-shown operands keep §7.71's sample test (the false `format_spec` row). Witnesses 6303-6309 (all 13 red-team probes FAIL on the OverflowError goal); control 6335.

Executor g3, driver run #3, 2026-10-27, off ac28806be. Gates (final candidate): root byte-diff 2497 -> 2512 0 MOVED / 0 GONE / 0 APPEARED (15 new sources); pyref 2186 / 2186 0/0/0; mirrors 53/53 0/0/0 (a first candidate GONE 2 mirrors -- frontend/pure_ast `type.__instancecheck__`, module6_whyml/statements a str-row `.get` -- both fixed before landing, so NO mirror refusal); pycsl_lib --no-proof screen identical (104 files, rc0 87); fidelity rc=0; soundness planes 61/61 green; getattr-erasure (control 6337 registered) / clause-survival / assumed-facts --emit-dir / open-route-carriers / refusal-witness-coverage / refusal-advice-audited rc=0. Logs: getting-better/systematic-soundness-r3/g3-r421-429/.

## RESIDUALS (honest)

The PYCSL-R417-ERASED-OBLIGATION message still names only the #417 sites (kept verbatim to keep its audit); MemoryError of huge widths unmodelled (as §7.71).
