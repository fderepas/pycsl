# OPEN ROUTE #411 — A NON-ASCII LATIN-1 STRING LITERAL IS EMITTED AS ITS UTF-8 BYTES: "é" HAS LENGTH 2 IN THE MODEL
**Status: REPAIRED, candidate (u411, driver run #3, 2026-10-27; see REPAIR below; all 18 moved mirrors proved whole-file), Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
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

## REPAIR (executor u411, driver run #3, 2026-10-27, off 77b33f239; annotations §7.90, translational §T.6.101)
Option (a), FAITHFUL, chosen after the spike (`getting-better/systematic-soundness-r3/u411-r411/SPIKE.md`). Option (c) is
not available: Why3 1.8.2's `smtv2.ml` `escape` is hard-coded (no driver keyword reaches it) and Z3 4.13.3 reads
`"\x0A"` as 4 characters under `encoding=unicode|ascii|bmp` alike (`probes/z.smt2`).
- `whyml_string_literal`: a code point 128..255 is ONE `\xHH` (g2's narrow patch). Above 255: UTF-8 bytes (LATIN1-STR).
- `_run_pipeline` (mirror twin `\trusted`), last step: every WhyML string literal of the emitted text (comments and
  `[@..]`/`[#..]` skipped) is decoded by Why3's lexer rules; one made only of printable ASCII other than `"` / `\` is
  untouched, any other becomes `pystr_cat` of its printable runs and `(pystr_chr N)` per other byte. Module
  `PyCSL_StrLit` (head of file, `use`d by each module that reads it): `val function pystr_chr` with
  `0 <= n < 256 -> length = 1 /\ pystr_code result = n` and, for a non-printable / `"` / `\` code, a GROUND
  disequality from each of the 93 printable one-character literals; `val function pystr_cat = concat`. Every clause is
  true of the one-character string of code point n (satisfiable spec, no `axiom`, no `assume`; assumed-facts 88 -> 88).
  One pass covers body literals, contract literals (route #417's decode) and the generic folds' own literals.
- Encodings MEASURED and rejected on the way: `(Char.chr n).Char.contents` (g2's (a)) proves lengths but cannot show
  `"\n" != "-"` (`string.Char` relates no Char to the solver's characters) and its axioms broke the mirror
  `canonical.term__size_pos` lemma; `String.lt` order clauses pull Why3's `lt_*` axioms and `String.contains` pulls
  `concat_substring` into string search: Z3 out of memory on goals needing the fact. A `let function .. = any ..`
  definition does not discharge its existence VC (`pystr_cat'vc` OOM).
- MIRROR FALSE PROOF EXPOSED: `audit_proof._strip_lean_comments` proved at base ONLY because `"\n"` was 4 characters
  (the skip-to-EOL loop then provably ran to the end of the text). Its inner loop invariant `i >= 0` cannot show
  progress; strengthened to `#@ label SKIP_EOL` / `#@ loop invariant i >= \at(i, SKIP_EOL)` (annotation only, body
  verbatim, fidelity green). Whole file proves at the candidate.

MEASUREMENTS (logs in `getting-better/systematic-soundness-r3/u411-r411/`):
- byte-diff vs base: root 2497/2497 + 10 new (6200-6209): 10 MOVED (0742, 0958, 0959, 1956, 1957, 1958, 1959, 5700,
  6106, 6107), 0 GONE, 0 APPEARED; pyref 2186/2186: 4 MOVED (0020, 0023, 0028, 0030); mirror 53/53: 18 MOVED. Each set
  is EXACTLY the files an independent census (`litcensus.py`) finds holding a non-printable literal at base; 0 at the
  candidate. `m1check.py`: every corpus/pyref diff is exactly the literal re-encoding + the module/`use` lines; the 18
  mirror diffs likewise except audit_proof (U+00B7 one char; the invariant above). g2's 122 / 4 / 30 was a raw grep.
- Movers re-proved base AND candidate: 14/14 verdicts kept (10 PROVED; 1957, 1959, 6106, 6107 FAIL as expected; prover
  Unknown, not type errors). All 18 moved mirrors type-check.
- Witnesses 6200-6207 + g03 g04 h07 j22 j26 + p411: PROVED at base, FAIL at candidate. Controls 6208, 6209 (lengths of
  `"é"`, `"\n"`, `"a\"b"`, `"a\\b"`, concat length, `"\n" != "\r"`): FAIL at base, PROVED at candidate.
- fidelity rc=0 (932 verbatim, 53/53 in sync); planes 61/61; doc-coherency rc=0; `\trusted` 442 -> 442.
- Mirror whole-file proofs at the candidate: ALL 18 moved mirrors rc=0 (`mirror-wholefile-proofs.txt`; longest: expressions 20090 s, statements 18334 s, stmt_control_flow 12205 s). None OWED.
