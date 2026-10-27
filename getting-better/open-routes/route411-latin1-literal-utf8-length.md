# OPEN ROUTE #411 — A NON-ASCII LATIN-1 STRING LITERAL IS EMITTED AS ITS UTF-8 BYTES: "é" HAS LENGTH 2 IN THE MODEL
**Status: OPEN (repair attempted, held: root cause wider, user decision), Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r411/`: `g03_utf8_index_exc.py`, `j22_utf8_contract_index.py`, `g04_utf8_index_eq.py`, `j26_utf8_contains_byte.py`, `h07_utf8_neq.py`.

```
#411 A NON-ASCII LATIN-1 STRING LITERAL IS EMITTED AS ITS UTF-8 BYTES: "é" HAS LENGTH 2 IN THE MODEL  [not covered by LATIN1-STR]
  g03  t = "é"; t[1] under no_exception PROVED                                             IndexError
  j22  requires s == "é"; s[1]                                                            IndexError
  g04  ensures \result == False over t[0] == "é"                                           True
  j26  requires s == "é"; ensures len(s) > 1                                              False
  h07  ensures len("é" + s) > 2 for s = "a"                                               False
  WhyML: `let t = ref "\xc3\xa9"`, `in_bounds (String.length !t) 1`. identifiers.py::whyml_string_literal encodes
  every non-printable / non-ASCII code point as its UTF-8 bytes. U+00E9 is INSIDE the declared LATIN1-STR domain
  (code points 0..255), so this is not the declared assumption: the literal is not the Latin-1 string the model
  claims every str is. (The >255 forms, emoji / CJK g07 / j24, are covered by LATIN1-STR and not counted.)
  REPAIR: encode a code point < 256 as ONE `\xHH` (Latin-1); a literal with a code point >= 256 is refused (or
  opaque) unless --strict-latin1 machinery models it.
```

## REPAIR ATTEMPT (2026-10-26, g2 executor off 4431ef86f): NOT LANDED -- the root cause is the SMT-LIB string printer, a decision for the user
**The encoder repair the hint asks for is necessary but NOT sufficient, and was measured, then held back.**
`whyml_string_literal` was changed to emit a code point 128..255 as ONE `\xHH` (so `"é"` is the Why3 literal `"\xe9"`,
one `string.Char`, as LATIN1-STR says). The five witnesses STILL PROVED (`scratchpad` screen, rc=0) and the control
`len("é") == 1` (true) FAILED. Reason, measured directly on Why3 1.8.2 + Z3 4.13.3 (`why3 prove -D z3_487.drv -o`):
Why3's SMT-LIB printer writes every string-literal character outside printable ASCII -- and `"` and `\` as well -- as
`\xHH`, but SMT-LIB 2.6 (which Z3 >= 4.8.10 implements) has only `\u{..}` / `\uXXXX` escapes, so Z3 reads `\xE9` as the
FOUR characters `\`, `x`, `E`, `9`:

```
goal String.length "\xe9" = 4      Valid    (Z3)        goal String.length "\xe9" = 1      Unknown
goal String.length "\n"   = 1      Unknown  (printed "\x0A")
goal String.length "a\"b" = 3      Unknown  (printed "a\x22b", 6 chars to Z3)
```

So the defect is WIDER than #411's Latin-1 case: EVERY literal holding a control character (`"\n"`, `"\t"`), a
double quote or a backslash, or any non-ASCII character, has the wrong length and the wrong characters in the Z3
model (each such character is 4 characters). Probe `p411_newline.py` (`requires s == "\n"; ensures \result == 4`
over `len(s)`, and the `a"b` / `é` analogues) is in the gate log. The Python-side fold of `len(<literal>)` hides
it for a literal directly under `len`, which is why `len("\n") == 1` proves.

Census of the emission population a faithful repair would move (base 4431ef86f sweeps, a literal containing
`\x..`, `\n`, `\t`, `\r`, `\b`, `\"` or `\\`): root corpus 122 `.mlw`, pyref 4, mirrors 30 of 54 (including
`expressions`, `statements`, `stmt_control_flow`, `functions`, `Module6_WhyMLTranspiler`, `pycsl` -- the long
whole-file proofs). A literal of code points 128..255 only: 0 root / 0 pyref / 1 mirror.

DESIGN OPTIONS (each moves the population above; none is a new axiom, but each is a model decision):
- (a) FAITHFUL: emit each such character as `(Char.chr n).Char.contents` (Z3 proves `length = 1`, distinctness and
  `Char.code (Char.get s i) = n` from string.Char's own axioms -- measured `t3.mlw`: c1-c4, c6 Valid, the false
  `length = 2` Timeout), joined to the printable runs by `concat`. Program context needs a logic+program symbol
  (`val function` bridges for `chr`/`concat`, the `chr_op` / `str_concat_op` precedent). Keeps every TRUE fact.
- (b) OPAQUE: emit such a literal as an uninterpreted per-literal `val function` constant (no spec, no fact): sound,
  but every content/length fact about it is lost (mirror proofs that read `"\n"`-bearing literals may stop proving).
- (c) ENVIRONMENT: a Why3 whose SMT-LIB printer emits `\u{HH}` (or a patched driver/printer). Outside the repo.
Owed to the user: the choice, and the mirror re-proof budget it implies. The narrow encoder change is kept as a
patch in the executor's report (`r411-narrow-encoder.patch`), not committed: alone it moves 1 mirror and closes
nothing under Z3.
