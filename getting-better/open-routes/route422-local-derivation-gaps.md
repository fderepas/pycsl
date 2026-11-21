# OPEN ROUTE #422 — LOCAL DERIVATION GAPS: three local forms with a known class are #UND, admitted 
**Status: REPAIRED, Severity 1.** Red-team round 33 (2026-10-27, convergence measurement after the run #3 allow-list repairs; 653 screened / 385 fully proved / 116 confirmed); driver-reproduced on main (see `scratchpad/rt33/driver-repro.txt`).
Witnesses `witnesses-r422/` (3): `c27_str_split_unbound.py`, `c31_enum_value.py`, `c35_nested_def.py`.

```
#422 LOCAL DERIVATION GAPS: three local forms with a known class are #UND, admitted   [documented #UND residual]   (3)
  c27  k = str.split('a b')        c31  k = E.A.value (Enum member value [1])        c35  a NESTED def `-> list` called
  CPython TypeError. REPAIR: read `str.<method>(x, ..)` as the str method row, `<Enum member>.value` as the member's
  initializer class, and a nested def's `-> T` like a module function's.
```

## REPAIR (executor g3, driver run #3, 2026-10-27, off ac28806be; annotations §7.111, translational §T.6.122)

In `_ty383`: unbound `str.m(x, ..)` / `bytes.m(x, ..)` read as the method row of `str` / `bytes`; the str / bytes method rows became an allow-list (unlisted method `#UNK`, e.g. `str.maketrans` -- probe q01 REFUSED; a method the type lacks contributes no class); `E.A.value` = union of member-initializer classes (`_ev422`, recorded by the global derivation) under an MRO condition, else `#UNK`; nested undecorated `def g() -> T` (sole binding) answers T (`_nd422`); a module function shadowed by a local no longer reads `_mf383`. Witnesses 6282-6284; control 6331.

Executor g3, driver run #3, 2026-10-27, off ac28806be. Gates (final candidate): root byte-diff 2497 -> 2512 0 MOVED / 0 GONE / 0 APPEARED (15 new sources); pyref 2186 / 2186 0/0/0; mirrors 53/53 0/0/0 (a first candidate GONE 2 mirrors -- frontend/pure_ast `type.__instancecheck__`, module6_whyml/statements a str-row `.get` -- both fixed before landing, so NO mirror refusal); pycsl_lib --no-proof screen identical (104 files, rc0 87); fidelity rc=0; soundness planes 61/61 green; getattr-erasure (control 6337 registered) / clause-survival / assumed-facts --emit-dir / open-route-carriers / refusal-witness-coverage / refusal-advice-audited rc=0. Logs: getting-better/systematic-soundness-r3/g3-r421-429/.

## RESIDUALS (honest)

Un-annotated nested defs, decorated nested defs and file-Enum `auto()` values stay #UND / #UNK respectively.
