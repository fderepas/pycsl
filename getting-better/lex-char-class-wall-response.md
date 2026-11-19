# Review of `lex-char-class-wall.md` — independent, oracle-backed

Reviewer: fable (never saw the base loop's census contents; only the report + the trees). 2026-11-01.
Scratch: `/home/fabrice/git/pycsl/scratchpad/fr1/` (every `.mlw`, log and script cited below lives there).
Every heavy run went through `scratchpad/heavy/heavy.sh`; Why3 1.8.2, Alt-Ergo 2.6.3, Z3 4.13.3.

## 0. Verdict in four lines

1. The report's root-cause diagnosis is WRONG as stated: the 3 failing goals are the literal formula `false`,
   emitted by Why3 1.8.2 for every `while` loop that carries no `variant`. No emitter symbol change can prove
   `false`. The first blocker is "the ported `lex` body has no `#@ loop variant`" — and the report's R4
   ("fidelity forbids adding one") is refuted by the project's own policy and by 298 such lines already in the mirror.
2. AFTER variants are added, the report's symbol-relation problem is real — but R1 as written does not fix it:
   `py_isdigit_op` is a `val`, so two calls on the same value are NOT related. Determinism needs a logic symbol.
3. R2 is sound and axiom-free for ALL strings (CPython checked on all 1,114,112 code points), and both provers
   prove the link as a `lemma` in < 0.1 s. R3's lowering is already semantically exact but needs a literal fold.
4. The hand model of the two scans proves completely with the Alt-Ergo→Z3 chain (§2). But the FULL emitted
   `lex` does NOT (§4a): 10 of 43 `lex'vc` goals time out in both provers — including `0 <= i` preservation,
   which is trivially true — and they stay red even with the `_OP_TOKENS` branch defused. The remaining wall is
   prover capacity in the context the `for op in _OP_TOKENS` lowering creates (a 14-`Seq.cons` literal with
   `pystr_cat`/`pystr_chr` terms), plus `len(op) >= 1` being unprovable for Alt-Ergo. The report never measured
   this branch (§5 of the report admits it); it is the actual make-or-break, and it is NOT a char-class problem.

## 1. Claims checked, one by one

### C1 — the three emitter arms and their symbols: CONFIRMED
`src/pycsl/module6_whyml/expressions.py:12256-12345` (read): arm 1 `py_<pred>_op (s: string)` for a named
receiver; arm 2 receiver-less `<name>_<pred>_0 ()` (dotted fallback); arm 3 `<pred>_1 (x0: 'a0)` for a
computed receiver. The emitted WhyML of the ported mirror (`lex-ported.mlw`, produced by
`$H ... pycsl.py src/self-annotate/src/proof2why3/parser.py --import-path .../src/pycsl --no-proof --keep-mlw`,
L3-tc ✓) confirms both symbols side by side:
```
91:  val isalnum_1 (x0: 'a0) : int ensures { ((result = 0) || (result = 1)) }
92:  val isdigit_1 (x0: 'a0) : int ensures { ((result = 0) || (result = 1)) }
106: val py_isdigit_op (s: string) : int  ensures { ((result = 0) || (result = 1)) }
736: if ((py_isdigit_op !c) <> 0) then begin
738:   while (... (isdigit_1 ((str_sub_op s !j 1))) ...) do
745: if ((let __or_l = (py_isalpha_op !c) in ... (str_eq_op !c "_") ...
747:   while (... (isalnum_1 ((str_sub_op s !j 1))) ... (str_contains_op "_'" (str_sub_op s !j 1)) ...) do
```
Note `c` is `ref (str_sub_op s !i 1)` and the inner receiver is `str_sub_op s !j 1` — same program call, so at
`j = i` the two VALUES are provably equal (given `0 <= i`); only the predicate symbols differ.

### C2 — "3 TERMINATION goals; caused by the unrelated symbols": goal count CONFIRMED, cause REFUTED
The emitted `lex` carries NO `invariant`/`variant` on its three `while` loops (lines 689, 738, 747 of the
census mlw = the same lines in `lex-ported.mlw`; only the `for op in _OP_TOKENS` loop gets an auto-variant).
Oracle 1 — `spikeA_novariant.mlw`, two variant-less loops, `why3 prove -a split_vc -D why3`:
```
goal fqtvc [@expl:VC for f] : [@vc:annotation] [@expl:termination] false      (one per loop)
Sub-goal Termination of goal f'vc.  Prover result is: Unknown (unknown) (0.01s, 2 steps).
```
Oracle 2 — same print on the real emission: `why3 prove -a split_vc -D why3 lex-ported.mlw | grep -c "expl:termination\] false"` → `5`
(5 literal-`false` termination goals in `lex'vc`; the census log's 2 "Valid" ones sit in contradictory contexts,
the 3 reachable ones are the 2 Timeouts + 1 OOM). Conclusion: the census failure is "no variant", full stop.
The symbol problem only becomes visible once a variant exists (§1 C5).

### C3 — R4 "fidelity forbids in-body `#@ loop` lines": REFUTED
`bin/check-self-annotate-mirror-sync.py:8,16`: "only `#@` contract/loop-invariant annotations are added";
body "byte-IDENTICAL (modulo `#@` lines and blank ...)". `bin/check-mirror-loop-annotations.py` is a RATCHET
whose whole purpose is to keep in-body `#@ loop invariant/variant` lines from being lost.
`grep -rn '#@ loop' src/self-annotate/src/ | wc -l` → `298`; the mirror's own `proof2why3/parser.py:166-168`
already carries `#@ loop variant \length(self.toks) - self.pos`. Adding variants to `lex` is standard practice.

### C4 — "the corpus has no computed-receiver is* predicate": REFUTED
`grep -rnE '(\]|\))\.(isalpha|isdigit|...)\(' test-suite/ src/`:
- corpus: `pycsl-reference/0605.py:15 if s[i].isdigit():` (the reference driver FOR arm 3, contract
  `\result == 1 or \result == 0`) and `6820_re_split_literal_for_join.py:29 if tok and tok[0].isalpha():` — 2 files.
- mirror, in CONVERTED (un-trusted) functions: `proof2why3/canonical.py:342 token[0].isalpha()`
  (`_normalize_type_string`), `frontend/Module5_IREmitter.py:2916 elt.id[:1].isupper()` (`_union_arm_tag`);
  `audit_proof.py:225/337` is `\trusted` (inert). Live tree also: `sertop.py:124`, `pure_ast.py:3825`, etc.
So any change to arm 3 owes: 2 corpus re-proofs (0/1 contracts — will re-prove) + whole-file re-proofs of
`canonical.py` and `Module5_IREmitter.py`. The report's "pure emitter change, blast radius none" is false.

### C5 — R1 "same uninterpreted symbol ⇒ equal values give equal answers": REFUTED for a `val`
`val py_isdigit_op (s: string) : int ensures {result = 0 || result = 1}` is a NON-DETERMINISTIC program
function: `py_isdigit_op c` and `py_isdigit_op (str_sub_op s j 1)` are two fresh results each only known to be
0/1. Unifying arm 3 onto arm 1 changes nothing for the proof. The fix is a logic symbol behind the val
(`function isdigit_f (s: string) : int` + `ensures { result = isdigit_f s }`, or `val function`). Still axiom-free.

### C6 — R2: is `isalnum = isalpha ∨ isdecimal ∨ isdigit ∨ isnumeric` TRUE in CPython? CONFIRMED (char level)
`unicode_check.py` (CPython 3.14.4, all code points incl. surrogates):
```
python 3.14.4 codepoints 1114112 isalnum!=disj 0 isalpha&!isalnum 0
'a1' isalnum True disj-of-string-preds False allchars True      <- string level: the disjunction is WRONG
'_'  isalnum False ...   '½' isalnum True (isnumeric)   "_" in "_'" True | "" in "_'" True | "_'" in "_'" True
```
Char level: exact (it is literally `Py_UNICODE_ISALNUM` in `Include/cpython/unicodeobject.h`). String level: the
disjunction of STRING predicates is false (`"a1"`), so the definition must quantify over characters:
`isX_f s = if len s >= 1 /\ forall k. 0<=k<len s -> isX_c (substring s k 1) = 1 then 1 else 0`, with
`isalpha_c/isdecimal_c/isdigit_c/isnumeric_c` uninterpreted `function`s and `isalnum_c` DEFINED as the disjunction.
This is a sound model of Python for every receiver (no length-1 restriction needed), and the length-1 fact is
never needed: at `c = substring s i 1`, the `forall k` instantiates at `k = 0` on syntactically equal terms.
Oracle (`spikeB_lex.mlw`): `lemma alpha_implies_alnum: forall s. isalpha_f s = 1 -> isalnum_f s = 1` —
Alt-Ergo `Valid (0.02s, 78 steps)`, Z3 `Valid (0.00s, 5372 steps)`. A proved `lemma`, zero `axiom`.

### C7 — R3 "how is `s[j] in "_'"` lowered?": handled semantically, NOT provable by Alt-Ergo
Lowered to `str_contains_op "_'" (str_sub_op s !j 1)` with the exact substring `exists` ensures (lines 114-118
of the emission). Ground fact `"_" in "_'"` (`ground_underscore'vc` in spike B): Z3 `Valid (0.05s)`,
Alt-Ergo `Timeout (30s/60s)` (no string theory). Inside the real variant goal even Z3 fails (§2).

## 2. The make-or-break spike, measured (`spikeB*_*.mlw`, `spikeB-split-clean.log`, `spikeB23.log`, `runC.log`)
Hand-written model of the three loops exactly as emitted, plus: logic symbols behind the three predicate vals,
the C6 definitions, `invariant {0 <= !i} variant {!n - !i}` outer, `invariant {!i <= !j} variant {!n - !j}` inner.
Per sub-goal (`-a split_vc -t 30`):

| variant goal | B (as-is) | B2 (no `c=="_"` disjunct) | B3 (+ literal hint lemmas) | B4 (literal fold, §3) |
|---|---|---|---|---|
| outer, DIGIT exit | AE Valid 50 st / Z3 Valid 0.43s | Valid/Valid | Valid/Valid | Valid/Valid |
| outer, IDENT exit | AE Timeout / Z3 Timeout | AE Valid / Z3 Valid | AE Timeout (hint lemmas themselves time out) / Z3 Timeout 60s | **AE Valid** / Z3 Timeout |
| all other 15-16 goals | Valid both | Valid both | Valid both | Valid both |

Reading: (i) the DIGIT branch is solved by determinism alone (C5) — no definition needed; (ii) the IDENT branch's
`isalpha ⇒ isalnum` half is solved by the definitional model (B2: Valid in both provers); (iii) the `c == "_"`
half is a string-literal ground fact that Alt-Ergo cannot do at all and that Z3 can do only in isolation
(not under the loop VC: B, B3). B4 folds the literal membership (§3) and Alt-Ergo then proves every `lex_core`
goal; PyCSL's chain is Alt-Ergo then Z3, accept first Valid — so B4 passes the chain.

## 3. The literal-membership fold (R3, made exact)
For `<expr> in "<lit>"` with a LITERAL haystack of length L, the set of needles is finite: all substrings of the
literal (L(L+1)/2 + 1 strings). Emit a per-literal val whose ensures is that enumeration —
`val str_in_lit_us_op (needle: string) : bool ensures { result <-> (needle = "" \/ needle = "_" \/ needle = "'" \/ needle = "_'") }`.
This is byte-for-byte Python's semantics (checked above: `""`, `"_"`, `"'"`, `"_'"` all `in "_'"`), needs no
string theory, and is strictly MORE complete than `str_contains_op` for Alt-Ergo. Guard it: only when the
literal is short (say L <= 8) and the needle expression is not itself a literal (that case can be folded to a
constant). Blast radius must be measured (`grep -rn ' in "' corpus/mirror`) before landing; every mover re-proves.

## 4a. Full-file spike — the honest gate — FAILS, and not on the char classes
`mkC.py` patches the real emission `lex-ported.mlw` (nothing else in the 400-goal file touched) with exactly the
§5 model: arms unified onto `py_isdigit_op`/`py_isalnum_op` with logic symbols, the C6 definitions, the §3 fold
(`spikeC2_fold.mlw`), and the 5 loop annotations at lines 706-707 / 757-758 / 768-769. Whole file, `-a split_vc -t 30`
(`runC3.log`, `C2-alt-ergo.txt`, `C2-z3.txt`):
```
== spikeC2_fold WHOLE FILE alt-ergo   total 406 goals; lex'vc goals 43; non-Valid: 10
line 707 | Loop variant decrease of goal lex'vc.        | Timeout (30.00s, 486327 steps)   x5
line 706 | Loop invariant preservation of goal lex'vc.  | Timeout (30.00s, 485017 steps)   x5
== spikeC2_fold WHOLE FILE z3         total 406; lex'vc 43; non-Valid: 10 (same ten) + alpha_implies_alnum Timeout
```
Both inner loops (757/758, 768/769) prove in both provers; the `for` loop (739/740) proves; the two definitional
pieces work in situ. What fails is the OUTER loop on 5 of its ~11 paths — and `invariant { 0 <= !i }` preservation
is among the failures, a goal no model can make harder. That is a context-size symptom, not a semantic gap.
Diagnostics (`runC4.log`):
- C3 = C2 + `assert { String.length !op >= 1 }` after `let op = ref (Seq.get _seqlit_idx_op !_idx_op)`:
  `line 742 | Assertion | Timeout (30s)` in Alt-Ergo — so `i += len(op)` can never decrease the variant for
  Alt-Ergo (no string-literal lengths; and the element is reached through 14 nested `Seq.cons` with
  `pystr_cat (pystr_chr 92) "/"` elements whose `pystr_chr` ensures carries 95 disequalities).
- C4 = C2 with that branch defused (`i := !i + 1 + len op`, diagnostic only): STILL the same 10 timeouts in
  both provers. So the op branch's VARIANT is not the only problem: every path that passes through the
  `_OP_TOKENS` loop inherits its context and drowns. (Z3 also loses `alpha_implies_alnum` in the big file —
  emit that lemma in a tiny separate module, or not at all: B2 shows the provers do not need it.)
Conclusion: after all four model fixes, `lex` is still red because of the `for op in <list-literal>` lowering.

## 5. Recommendation: route R5 = (variants) + (determinism) + (definitional isalnum) + (literal fold) — GATED on step 0
0. **Make-or-break first spike (1-2 h, zero emitter change): the `_OP_TOKENS` branch alone.** In the mirror,
   add the 5 `#@ loop` lines and prove the ported `lex` with the DIGIT/IDENT scans still red; count the outer-loop
   goals on the op path. Then try, in a hand `.mlw` copy, the only levers that need no new axiom: (a) `-a split_vc`
   plus `introduce_premises`/`remove_unused`-style pruning (Why3 CLI: `-a split_vc -a remove_triggers` etc.)
   on the 10 goals; (b) replace the inline 14-cons `Seq` literal by a `val constant _OP_TOKENS : seq string
   ensures { Seq.length result = 14 /\ Seq.get result 0 = "->" /\ ... }` (a module-level list literal lowered
   ONCE with per-element facts, no axiom), so the loop context no longer carries the cons chain and
   `pystr_chr` terms; (c) a `#@ loop invariant` on the op loop stating `\forall k. \length(_OP_TOKENS[k]) >= 1`
   (provable by Z3 only, 14 ground string lengths). REFUTATION EXIT: if (a)+(b)+(c) do not make the 10 goals
   Valid in the full file, `lex` is a prover-capacity wall tied to list-literal iteration, NOT a char-class wall;
   record it as such, keep the 5 variant lines (ratchet +5, `bin/check-mirror-loop-annotations.py --update`),
   and spend no emitter effort on R1/R2/R3 for this stub.
1. **Variants** (`#@ loop invariant 0 <= i`, `#@ loop variant n - i`; `#@ loop invariant i <= j`,
   `#@ loop variant n - j` twice). Legal per C3; mandatory for every route; 30 min.
2. **Determinism** (emitter, arms 1 and 3): declare `function py_<pred>_f (s: string) : int` and emit
   `ensures { result = py_<pred>_f s /\ (result = 0 || result = 1) }` (keep the 0/1 clause textually so 0447/0605's
   contracts still prove); arm 3 calls the same `py_<pred>_op` when the receiver is a string expression. Movers:
   0447, 0605, 6820, `statements.py` mirror, `canonical.py` mirror, `Module5_IREmitter.py` mirror — all owe proofs.
   This alone closes the DIGIT branch (B: Valid/Valid).
3. **Definitional `isalnum`** (emitter preamble): the C6 block, emitted only when `isalnum` appears together with
   one of its four parts (keeps every other file byte-identical). No axiom; the `lemma` is optional (provers find
   it without, B2). Closes the `isalpha` half of IDENT.
4. **Literal fold** (§3) for `<expr> in "<short literal>"`. Closes the `c == "_"` half; Alt-Ergo proves it.
Steps 2-4 are only worth doing for `lex` if step 0 goes green; they are measured-good in the small (spike B4:
every scan goal Valid under the chain) and in situ for the inner loops (§4a), so the risk they carry is blast
radius, not soundness. Final gate: 0 non-Valid in the ported mirror `parser.py` whole-file proof with the default
chain, byte-diff of both corpora = exactly the intended movers, every mover re-proved.

Costs, honest: step 0 is 1-2 h of hand-`.mlw` work (the C2/C3/C4 files are a ready starting point); step 1 is
30 min; steps 2-4 are each a half-day emitter change + byte-diff + 3-6 re-proofs (Module5_IREmitter.py's
whole-file proof is the expensive one — budget it before step 2). Yield: 1 stub; steps 2-4 are permanent
completeness gains for every `s[i].isX()` / `isalnum` / `in "lit"` site (>= 10 in the live tree, C4 grep), and
step 0(b) — if it is what unblocks — is a completeness gain for every `for x in [literal list]` loop in the mirror.
If the budget is one increment: do step 0 + step 1 only. They convert the report's misdiagnosis into a
measured wall with the right name.

## 6. Answers to the report's §6 questions
1. R1 sound: yes, but useless alone (C5: `val` is non-deterministic); blast radius: 2 corpus + 2 converted mirror
   files + `statements.py` mirror (C4) — not "none".
2. Yes: the char-quantified definitions of C6 are TRUE for every Python string, Why3 takes them as `function`
   bodies, no `axiom`, no length-1 restriction, and the length-1 fact is never needed (`k = 0` instantiation).
3. R3 is lowered with exact substring semantics; provable by Z3 in isolation, by neither prover inside the loop
   VC; the §3 finite-enumeration fold makes it Alt-Ergo-provable and is still exact Python.
4. Not as a char-class change: the wall is the `_OP_TOKENS` loop context (§4a). Cheaper path missed by the
   driver: variants are allowed in the mirror (C3), and that alone is the honest first increment.

## 7. What I did not do
No edit to any file outside this response and `scratchpad/fr1/`. I did not run the whole-file proof of the
unmodified mirror parser.py (census already did); the C-spikes are the ported emission patched by `mkC.py` /
small Python replacements, not an emitter change. I did not measure the `in "lit"` blast radius, did not try
step 0's levers (a)-(c) — time box — and did not isolate WHICH 5 outer-loop paths time out beyond the C3/C4 evidence.

## 8. Reproduction (all under `$H = scratchpad/heavy/heavy.sh`, `PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH`)
```
cd /home/fabrice/git/pycsl/scratchpad/fr1
.venv/bin/python3 -I unicode_check.py                                  # C6
$H why3 prove -a split_vc -D why3 lex-ported.mlw | grep -c 'termination\] false'   # C2 -> 5
$H why3 prove -P alt-ergo -t 30 -a split_vc spikeB4_fold.mlw           # all lex_core goals Valid
$H why3 prove -P z3 -t 30 -a split_vc spikeB2_noUnderscore.mlw         # all 18 Valid
$H sh runC3.sh; $H sh runC4.sh                                        # whole-file C2, then C3/C4 diagnostics
```
