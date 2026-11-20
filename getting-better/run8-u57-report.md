# run #8 executor u57 -- SOUNDNESS BATCH S5: route #429, refusal-only (user decision 2026-11-19 ~16:25Z)

Branch `run8-u57` (worktree `/home/fabrice/git/pycsl-u57`), base `97a4551d8` (main after L16, `\trusted` 366,
proof-axiom ledger 3). Commit only, never pushed.

## Result
`PYCSL-R429-NONLATIN1-STR-LITERAL`: a str VALUE holding a code point > 255 that ENTERS THE MODEL refuses the
program (fail closed). rt68's p15 / p16 / p17 / p18 / p19 / p21 / p22 / p20 are REFUSED in the default, typed and
store models. Corpus root / pyref byte-identical (0 / 0 / 0). Mirror 53 / 53 with 0 GONE and 3 MOVED: pycsl,
Module3_Weaver, and normalize. normalize carries a SOUNDNESS-FORCED RE-TRUST of `normalize_prover_output` (+1 marker,
367 grep / 339 markers). All three re-proved whole-file: 820 / 820, 331 / 331 and 4 / 4 Valid.

## Measurement (before any rule; base 97a4551d8, CPython-checked probes)
See `getting-better/open-routes/route429-latin1-upper-closure.md`, u57 section (table). Summary:

| range | len / index / positive slice / concat len / find | negative slice | `in`, `!=` | ord | verdict |
|---|---|---|---|---|---|
| ASCII 0-127 | faithful (true claims prove, false do not) | unconstrained at base (sound) | faithful | incomplete, sound | keep |
| Latin-1 128-255 (0x80, 0xE9, 0xFF) | no false claim proves; true claims prove as ASCII's (concat `x[0:2]` incomplete) | unconstrained | faithful | incomplete, sound | keep (no doubt left) |
| BMP 256-0xFFFF (U+20AC, combining U+0301) | FALSE CLAIMS PROVE (7 of 12 claims) | unconstrained | not proved | `ord(x[1]) != cp` PROVES | REFUSE |
| astral > 0xFFFF (U+1F600) | FALSE CLAIMS PROVE (7 of 12) | unconstrained | not proved | PROVES | REFUSE |
| surrogates | pipeline crash (UnicodeEncodeError) | - | - | - | REFUSE (now a clean refusal) |
| `chr(300)` | `len != 1`, `chr(300) == chr(301)` NOT provable (one length unit) | - | - | `ord(chr(300)) != 300` proves = declared LATIN1-STR (corpus 3021) | not in scope, unchanged |
| `bytes.decode` | no model (both directions unproved) | - | - | - | nothing to refuse |
| fold `"\xff".upper()` | raw `(pystr_chr 376)`, no law (not provable either way) | - | - | - | REFUSE (value above 255 enters) |

Direct literal forms: `len("a" + "😀") != 2` PROVED, `"a€b"[2] != "b"` PROVED at base; `len("😀") != 1` not proved
(Python-side fold).

## The rule
see annotations.md §7.611 / translational §T.6.101a. Implementation:
* `src/pycsl/module6_whyml/identifiers.py::whyml_string_literal` (no mirror twin): UTF-8 arm writes decimal escapes
  `\ddd` (same bytes for Why3) and takes `surrogatepass`.
* `src/pycsl/pycsl.py::_run_pipeline` (twin `\trusted`): route #411's literal pass reconstructs each literal's Python
  value (`_off429`); before `return _mlw`, values above 255 refuse unless the source holds the value ONLY as text of a
  `raise <Name|Attr>(..)` argument or of a statement `print(..)` argument (closed under f-string constant parts and
  `+` operands), the file does not bind `print`, and no `#@` string token equals it.
* Live + mirror `_why3_typecheck` message: `—` -> `--` (the only other mirror refusal that a text change removes).

## Over-refusal (measured before narrowing; every list in the route file)
1. broad (source scan + emission): corpus 14 (7 expected-PASS / unheadered: 1031, 3020, 3022, 3023, 3028, 3029,
   8030), pyref 0, mirror 14.
2. emission only: corpus 0, pyref 0, mirror 7 (audit_proof, desugar, Module5_IREmitter, expressions,
   stmt_control_flow, normalize, pycsl).
3. + raise / print text excused: mirror 2 (normalize, pycsl); pycsl repaired by the message rewrite.
4. normalize: a true refusal (its verified body `str.replace`s '∀'-style 3-byte patterns). Per the driver
   (01:30Z) `normalize_prover_output` is RE-TRUSTED (soundness-forced, +1, NOT progress); the file emits again and the
   rest of it re-proves (4 / 4).
5. stricter narrowing 2 (no raw-written value excused; no excusal in a file with another non-statement constant /
   `#@` token above Latin-1): final over-refusal corpus 0, pyref 0, mirror 0 (after 4).

## Witnesses (corpus 10260-10279)
REFUSED (PYCSL-R429-NONLATIN1-STR-LITERAL) in default / typed / store, candidate 50ffa6804 (logs
`scratchpad/u57/wprove2/{hoare,typed,store}/`): 10260 p15, 10261 p16, 10262 p17, 10263 p19, 10264 p18, 10265 p21, 10266
p22, 10267 contract-only literal, 10268 fold "\xff".upper(), 10271 `\N{..}`, 10272 module constant, 10274 imported
constant, 10275 lone surrogate (p20) = 13 x 3. Expected FAIL, not refused (literal never reaches the model), FAIL by
proof x3: 10269 f-string part, 10270 format spec, 10273 default. Controls: 10276 ASCII and 10277 Latin-1 PROVE x3;
10278 (comment emoji) and 10279 (docstring emoji) PROVE in default and are NOT refused in typed / store. There they
fail Why3 typing ("This function depends on external variables"), which is pre-existing: no literal of theirs is
touched by the rule.
At base 97a4551d8 (hoare, `scratchpad/u57/wprove/base-hoare/`): 10262 / 10263 PROVED (the false proofs); 10260 / 10261 /
10264-10266 not proved (negative bounds unconstrained before batch D's R3); 10269 / 10270 / 10273 FAIL.

## Narrowing 2 probes (`scratchpad/u57/nar/`, candidate; `scratchpad/u57/wprove2/nar/`)
n1 raise payload `"😀"[3]` -> refused (R506 before R429); n2 `print` shadowed by a user def -> R429; n3 the message
value also compared -> R429; n4 `raise ValueError("negative — ..." + str(n))` -> PROVES; n5 `print(f"  ✓ {n}")` ->
PROVES; n6 a docstring read through `g.__doc__` -> not refused, FAIL (no literal emitted, `__doc__` opaque); n7 message
value also in a `#@ requires` -> R429; n8 `raise ValueError("Ÿ")` + fold `"\xff".upper()` -> R429 (raw); n9 message
"a—b" + comparison with `"a" + "—b"` -> R429 (another constant above Latin-1 cancels excusal); n10 print text also
returned by another def -> R429.
GUARANTEE (also in the `_run_pipeline` comment): an excused value occurs in the source ONLY as a raise-constructor
argument / statement-print argument (constant, f-string constant part, `+` operand); Module 5 lowers `raise N(a0, ..)`
to tag N + payload a0 (later args dropped), payload arms are wildcards and route #233 refuses `except .. as e` reads;
builtin tags carry no payload; `print(..)` is `let _ = print_1 (str_hash_op ..)`. The closure holds no call,
subscript or comparison. So no obligation, return value, comparison or contract is computed from the text. No
excusal in a file where another non-statement constant or a `#@` token is above Latin-1, and never for raw-written
values.

## Gates (candidate 50ffa6804 + 436cbd63b census/message-format commit; logs `scratchpad/u57/sw2/`, `scratchpad/u57/gates4/`)
* byte-diff vs `scratchpad/run8/v70/bd-int`: root 3291 / 3298, 0 MOVED / 0 GONE / 0 APPEARED, 7 new sources (rc 0,
  compared twice: `sw2/C-root-{1,2}.txt`); pyref 2185 / 2185 0/0/0 (rc 0 twice: `sw2/C-pyref-{1,2}.txt`).
* mirror vs `v70/mir-int`: 53 / 53, 3 MOVED (pycsl, frontend__Module3_Weaver, proof2why3__normalize), 0 GONE
  (`sw2/D-mir.txt`; `--expect-moved` of the 3: rc 0, `sw2/D-mir-expect.txt`). Movers re-proved whole-file:
  `mproof/pycsl.py.log` 820 / 820 SUCCESS (5526 s), `mproof/frontend_Module3_Weaver.py.log` 331 / 331 (873 s) -- both on
  45ea80fd3, whose emission of the two files is byte-identical to the final sweep's (cmp) --
  `mproof/proof2why3_normalize.py.log` 4 / 4 (120 s, 50ffa6804). oom_kill 15 throughout.
* fidelity: check-self-annotate-sync rc 0, self-annotate-mirror-check rc 0, doc-coherency rc 0 (`gates4/E-*.log`).
* fast planes (snap2 50ffa6804, `gates4/planes-fast.log`): 61 / 62 green. The 1 red was check-refusal-witness-coverage
  (no census rows yet). After 436cbd63b (16 rows via `_census_row`; the fragment fix) it is OK: 480 demonstrated,
  5 undemonstrated = ceiling 5 (`gates4/ind3-refusal-witness-coverage.log`). `--append-new` was STOPPED: 520
  pre-existing rowless expected-FAIL witnesses would have taken hours.
* individually: core-only-conformance 38 / 0 rc 0, frontend-only-conformance rc 0, check-trusted-reasons OK (339 <->
  339, unclassified 213 / ratchet 225), count-trusted-directives OK (339 markers, 367 grep).
* ledger planes: check-assigns-writes-survival OK (HOLE 0, TRAP 1398 / NMS 1501), check-trusted-frame-honesty OK
  (both on a single-underscore-named copy of the final mirror emission, `mir_emit3`; a first run on the
  double-underscore sweep names gave the documented FALSE RED 48 > 0 and is void), check-getattr-erasure OK.
* \trusted 366 -> 367 grep (338 -> 339 markers): the one soundness-forced re-trust. Proof-axiom ledger 3 (allowlist
  unchanged).

## Residuals
* LATIN1-STR for SYMBOLIC str values stays declared: `ord(s) < 256`, `s.upper()` of a Latin-1 input (p03 / p04),
  `ord(chr(300)) != 300` (corpus 3021).
* The excusal is a syntactic allow-list over the main file's source. Red team target: anything that renders an excused
  value outside its raise / print position (e.g. an emitter copying a payload elsewhere).
* `normalize_prover_output` re-trust: re-convertible only with a code-point str model.
* Module3_Weaver's move is a hash of an escaped rendering (the `\ddd` marker changes `stable_hash`), not a semantic
  change. Any other emitter that hashes rendered literals moves the same way on non-Latin-1 text.
* typed / store: 10278 / 10279 Why3 typing failure (pre-existing).
* batch D re-evaluation: p15 / p16 (D's introduced consequences) are now refused at this branch.
* Scratch worktrees left (mine, clean or measurement-only): /home/fabrice/git/pycsl-u57base (base 97a4551d8),
  /home/fabrice/git/pycsl-u57snap (45ea80fd3), /home/fabrice/git/pycsl-u57snap2 (50ffa6804), /home/fabrice/git/pycsl-u57nn
  (2e7832969 + a measurement-only patch disabling the narrowing).

