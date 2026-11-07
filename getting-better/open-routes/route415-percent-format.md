# OPEN ROUTE #415 — `%` STRING FORMATTING IS AN UNCHECKED str_mod_op
**Status: REPAIRED (candidate, g2 run #3), Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r415/`: `l16_percent_format.py`, `n15_percent_mapping.py`.

```
#415 `%` STRING FORMATTING IS AN UNCHECKED str_mod_op  [old family]
  l16  "%d" % s (s: str)                                                                        TypeError
  n15  "%(k)s" % {"j": a}                                                                      KeyError
  (n07 "%s %s" % (a,) fails Unknown.) REPAIR: refuse `%` with a str left operand unless the format literal's
  directives are matched against the operand count / types / keys at emission time.
```

## REPAIR (2026-10-26, g2 executor off 4431ef86f; docs annotations §7.73 / translational §T.6.84)
**Allow-list refusal (no emission change for an admitted site).** Under `no_exception \all` -- and under a named set holding
KeyError when the format has a `%(` key or is not a literal -- `s % x` with a str left operand is REFUSED
(`PYCSL-R415-UNCHECKED-PERCENT-FORMAT`, `_handle_binop`, mirror twin `\trusted`) unless the format is a string LITERAL whose
conversions are only `%s` / `%d` / `%i` / `%r` (and `%%`), with optional flags and a literal width / precision (their size
stays route #284's `format_spec` row) but no mapping key and no `*`; the right side is a tuple display with exactly one
operand per conversion (or a single operand for one conversion); every `%d` / `%i` operand is int-read (an int / bool
literal, a parameter / local typed `int` / `bool`, `len` / `int` / `abs` / `ord` / `hash` / `sum`) and every `%s` / `%r`
operand int-, str- or float-read. Over-refusal measured BEFORE landing: the first allow-list (no flags / width) refused the
PASS control `3271` (`"%5d|%s|%%" % (x, x)`); widened to literal flags / width / precision, which are value-independent
for int and str: 3271 emits byte-identically and PROVES at base and candidate.
Measured together on the final candidate (g2 worktree off 4431ef86f; base = the official `bin/byte-diff-sweep.sh` at 4431ef86f
from the clean g1-base tree, cwd = tree root; candidate the same script from the g2 tree): root 2441 -> 2455 .mlw, 2 MOVED
(`1163`, `1164`: #414's shift obligation), 1 GONE (`3269`, #415), 0 APPEARED, 15 new emitting sources (the 20 new witnesses /
controls minus the 5 refused); pyref 2186 -> 2186, 1 MOVED (`0110`: #412's `no_div_zero (0)` inside a `try/except
ZeroDivisionError`, exactly the assert `//` already gets there), 0 GONE, 0 APPEARED; mirrors 53/53, 0 MOVED / 0 GONE / 0
APPEARED. M1 re-proofs base -> candidate: `1163` FAIL -> FAIL (expected FAIL), `1164` PROVED -> PROVED, `3269` FAIL -> REFUSED
(expected FAIL), pyref `0110` FAIL -> FAIL (a pre-existing real/int type error at both).
Movers of this route alone: `3269` GONE (expected-FAIL `"%q" % x`: FAIL -> REFUSED). PASS files refused: 0 (root, pyref,
mirrors, `pycsl_lib`).
Witnesses PROVED rc=0 at base -> REFUSED rc=1: 6069 (l16), 6070 (n15). Control 6072 (`"%d-%s-%r %% %s" % (a, s, x, a)`,
`"<%s>" % s`): PROVED at base and candidate. Advice audit: FOLLOWABLE (6069 rewritten `"%s" % s` admitted and VERIFIES,
probe `p415_follow`).
Residual: a `%` whose operand is a user object (`%s` calls `__str__`) or a tuple-typed variable is refused, not modelled.
