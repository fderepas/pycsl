# Route #411 spike (u411, driver run #3) — option (a) measured, (c) refuted

Base 77b33f239. Candidate = working tree of `/home/fabrice/git/pycsl-u411` (spike code: a route-#411
literal pass at the end of `pycsl.py::_run_pipeline` + `whyml_string_literal` emitting a code point
128..255 as ONE `\xHH`). Every number below is from a heavy.sh run; logs are in this directory.

## Option (c) — environment: NOT AVAILABLE in the installed toolchain
- Why3 1.8.2 `src/printer/smtv2.ml` hard-codes `let escape c = ... '\000'..'\031' | '\127'..'\255' ->
  "\\x%02X"` and maps `\\` -> `\x5C`, `"` -> `\x22`. It is passed directly to `Constant.print`; no
  driver keyword / meta reaches it (`smtlib-strings.gen` only has `meta "literal:keep"`).
- Z3 4.13.3: `(assert (not (= (str.len "\x0A") 1)))` is `sat` under `encoding=unicode` (default),
  `encoding=ascii` and `encoding=bmp` (`probes/z.smt2`). No Z3 option restores the old `\x` reading.
- So (c) would mean patching/rebuilding Why3: outside the repo. Rejected.

## Option (a) — FAITHFUL encoding: chosen
Why3 probes (`probes/t1.mlw`, `probes/t2.mlw`, Z3, 10 s):
- `val function pystr_chr (n:int) : string ensures { result = (Char.chr n).Char.contents }` and
  `val function pystr_cat (a b: string) : string ensures { result = String.concat a b }` (t2):
  `length (pystr_chr 233) = 1` Valid, `length (pystr_cat "a" (pystr_cat (pystr_chr 10) "b")) = 3` Valid,
  the FALSE `length (pystr_chr 233) = 2` NOT proved (OOM/Unknown), program use `g'vc` Valid.
  t1 adds c3 distinctness `chr 10 <> chr 13`, c4, c5 `code (get .. 1) = 233` — all Valid.
- A `let function .. = any string ensures {..}` (a PROVED definition, t1) is rejected: the
  `pystr_cat'vc` existence goal does not discharge (OOM). Logic `function`s cannot be used in program
  code (`Logical symbol length is used in a non-ghost context`), so the `val function` bridge (the
  `str_concat_op` precedent; its `ensures` is a definition by a total logic term) is the encoding.

## Where: ONE post-pass, not 40 call sites
`whyml_string_literal` has ~40 call sites, and SEVEN quote-shape tests (`startswith('"')`) in
mirrored, VERIFIED methods (`_coerce_str_arg`, `_coerce_to_int`, `_str_operand_to_int`, ...) key
hashing on a literal being `"..."`. Changing the literal's spelling there would move hashes and owe
re-proofs of those methods. Instead the emitter is unchanged and the FINAL text is rewritten in
`_run_pipeline` (`\trusted` in the mirror): lex Why3 literals (comments / `[@..]` / `[#..]` skipped),
decode per `lexlib.mll`, keep a literal that is all printable ASCII except `"`/`\` byte-identical,
otherwise emit runs + `(pystr_chr N)` joined by `pystr_cat`; add module `PyCSL_StrLit` at the head and
`use PyCSL_StrLit` in each module that reads it. This also covers the contract-literal path of route
#417 and hand-written literals in the generic folds with no extra code.

## Movers (byte-diff vs base, both trees + mirror)
| tree | files | MOVED | GONE | APPEARED |
|---|---|---|---|---|
| root corpus | 2497 / 2497 | 10 | 0 | 0 |
| pyref | 2186 / 2186 | 4 | 0 | 0 |
| mirror | 53 / 53 | 18 | 0 | 0 |

The MOVED sets equal EXACTLY the files an independent census (`litcensus.py`) finds holding a
non-safe literal at base (`lit-base-*.tsv`: 10 / 4 / 18), and the census over the candidate trees
finds 0. g2's estimate (122 / 4 / 30) came from a raw grep that counted comments and prose.

## Verdicts
- Corpus movers re-proved at base AND candidate (`mv-base.txt`, `mv-cand.txt`): 14/14 identical
  (10 PROVED, 4 FAIL — 1957/1959 are `_false_claim` XFAILs, 6106/6107 expected FAIL; the
  candidate FAILs are prover Unknown, not type errors).
- Mirror movers: 18/18 type-check (`mir-tc.txt`); whole-file proofs are step 2.
- Witnesses (`witness-controls-base-cand.log`): g03 g04 h07 j22 j26, g2's 6050-6054, p411_newline,
  `w1` (`"\n"` length 4), `w2` (`"\t"[1]`), `w3` (`"a\"b"` length 6): ALL PROVED at base, ALL FAIL at
  candidate. Controls 6055 and `c1_controls` (len("é") == 1, "\n"/"a\"b"/"a\\b" lengths, concat
  length, `s[0]` of "é", `"\n" != "\r"`): FAIL at base, PROVED at candidate.

Refutation exit NOT taken: no verdict regressed.
