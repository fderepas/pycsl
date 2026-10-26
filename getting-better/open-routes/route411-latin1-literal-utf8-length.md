# OPEN ROUTE #411 — A NON-ASCII LATIN-1 STRING LITERAL IS EMITTED AS ITS UTF-8 BYTES: "é" HAS LENGTH 2 IN THE MODEL
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
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
