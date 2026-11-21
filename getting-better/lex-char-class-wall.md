# The `lex` termination wall: string-predicate ops on computed receivers — a state-of-the-art report for independent review

Driver run #4, 2026-11-01. Author: the driver (tainted: it has read the base loop's census). Every claim below is
reproducible with the commands of §8; the reviewer is expected to re-run them, not to trust the prose.

## 1. The system in one paragraph

PyCSL is a deductive verifier for annotated Python: `src/pycsl/pycsl.py` parses `#@` contracts, lowers the program
through Modules 1-6 to WhyML, and discharges the VCs with Why3 (Alt-Ergo, Z3). PyCSL verifies ITSELF through a
*mirror*: `src/self-annotate/src/` holds a copy of every source file whose functions are either verbatim copies of
the live body (verified, whole-file proof required) or `#@ \trusted` stubs (assumed). Reducing the number of
`\trusted` stubs without adding axioms (the proof-axiom ledger is fixed at 3) is the goal of the self-tcb-reduction
loop. A conversion must pass three disjoint planes: fidelity (the mirror body is the live body verbatim), the
whole-file Why3 proof of the mirror file (0 non-Valid, non-vacuous), and corpus inertness (the ~2700-file reference
corpus + 2186 python-reference files emit byte-identical WhyML, or every difference is an intended semantic
correction and every changed program re-proves).

## 2. The wall as first seen

The base loop's census of 2026-11-01 (cv7: all 389 `\trusted` stubs, live body ported verbatim one at a time) found
exactly ONE stub whose ported body type-checks, passes the four screen oracles (untrusted-emitted, yield-erasure,
shadowed-selfcalls, emitted-vacuity) and reads non-vacuously: `proof2why3/parser.py::lex` (live body:
`src/pycsl/proof2why3/parser.py:161-219`, a hand-written tokenizer). Its home file's whole-file proof then fails with
3 non-Valid goals, all TERMINATION goals of `lex'vc` (log: `scratchpad/cv7/proof-parser.log`, lines ~1448-1588: two
Timeouts and one Unknown / out of memory).

The two inner scans:

```python
if c.isdigit():                      # c = s[i]
    j = i
    while j < n and s[j].isdigit():  # digit run
        j += 1
    toks.append(Token("INT", s[i:j])); i = j; continue
if c.isalpha() or c == "_":
    j = i
    while j < n and (s[j].isalnum() or s[j] in "_'"):
        j += 1
    toks.append(Token("IDENT", s[i:j])); i = j; continue
```

The outer `while i < n` terminates because each branch advances `i`: in the two scan branches only because the inner
loop runs at least once (j = i satisfies the guard, since `s[i]` is `c` and `c` passed the outer test).

## 3. Where the proof breaks: the emitter, measured

`src/pycsl/module6_whyml/expressions.py`, the `is*` string-predicate lowering (around line 12256-12350), has three
arms:

1. **named receiver** (`c.isdigit()` with `c` a local / parameter / symbol): emits `(py_isdigit_op c)` with
   `val py_isdigit_op (s: string) : int ensures { result = 0 || result = 1 }` — receiver-carrying, monomorphic in
   `string`, uninterpreted.
2. **dotted name fallback**: a receiver-less `val <name>_isdigit_0 () : int` (refused / avoided elsewhere as a
   faithfulness violation).
3. **computed receiver** (`s[j].isdigit()`, receiver in the IR `receiver` field): emits `(isdigit_1 (recv))` with
   `val isdigit_1 (x0: 'a0) : int ensures { ... }` — a DIFFERENT, polymorphic uninterpreted symbol.

So `c.isdigit()` and `s[j].isdigit()` lower to two unrelated symbols: knowing `py_isdigit_op c = 1` says nothing
about `isdigit_1 (s[j])` even when `j = i` and `c = s[i]`. The inner loop may run zero times in the model, `i = j`
does not advance, and the outer variant is unprovable. (Comment at the third arm: "the corpus has no computed-receiver
isX/startswith/endswith, so this is byte-identical there" — a claim to re-check.)

The identifier branch needs more: `c.isalpha()` (arm 1) must imply `s[j].isalnum()` at `j = i`. With two
uninterpreted ops `py_isalpha_op` / `py_isalnum_op` there is no relation; a lemma `isalpha c -> isalnum c` would be a
NEW AXIOM (ledger would exceed 3: forbidden). And the `c == "_"` disjunct needs `s[j] in "_'"` (string membership in a
literal) to be true at `s[j] = "_"`.

## 4. Candidate routes, honestly costed (all unbuilt; the reviewer is asked to spike)

- **R1 — unify the computed-receiver arm with the named arm when the receiver is statically a `string`**: emit
  `(py_<pred>_op <recv>)` instead of `(<pred>_1 (<recv>))`. Pure emitter change; sound (same uninterpreted
  0/1 symbol, applied to the value tested — strictly more faithful: equal values give equal answers). Cost: every
  mirror / corpus file with a computed-receiver string predicate moves (the corpus claim of "none" must be
  re-measured; mirror movers owe whole-file proofs). Unblocks the DIGIT branch only.
- **R2 — a definitional character-class model, no axiom**: make `py_isalnum_op` a DEFINED function over its parts
  instead of an independent `val`, e.g. for Python's single-character semantics
  `isalnum c = isalpha c || isdecimal c || isdigit c || isnumeric c` (CPython docs: `str.isalnum` is True iff every
  char satisfies one of the four). Multi-character strings: `s.isalnum()` is True iff `len(s) >= 1` and every
  character is alnum — so a definition over strings must quantify over characters, or the definitional link is
  restricted to one-character receivers (`s[j]`, `c = s[i]`). Keeping `isalpha` / `isdigit` / `isdecimal` /
  `isnumeric` uninterpreted keeps the model sound (nothing is claimed about which characters are alphabetic).
  Question: can the link be stated as a WhyML `function` definition (not an `axiom`, not a `lemma` that needs a
  proof the ledger cannot carry) for all receivers, or only for receivers known to have length 1?
- **R3 — `s[j] in "_'"`**: how is `<str> in <str literal>` lowered today? If it is a receiver-carrying `contains`
  op, `"_" in "_'"` needs evaluation on two literals (a ground fact the emitter could fold).
- **R4 — loop-annotated mirror**: NOT available: the fidelity plane forbids editing the mirror body (no added
  invariants / variants beyond what the live body carries).

Expected yield: 1 stub (`lex`). Side benefit of R1: computed-receiver predicates become comparable with named ones
everywhere (a completeness gain; soundness unchanged).

## 5. Honest limits

- The termination failure was read from the goal names and the shape of the two loops; the driver has not isolated
  which of the 3 goals belongs to which loop.
- R2's semantic claim about CPython's `isalnum` must be checked against the CPython docs and on the full Unicode range
  (`unicodedata`): a definition that is false for some character is an UNSOUND model, not merely incomplete.
- Whether the outer loop's other branches (`_OP_TOKENS` / `startswith` scan) prove was not re-measured in isolation.

## 6. Questions for the reviewer

1. Is R1 sound and is its blast radius as small as claimed (re-measure the corpus for computed-receiver predicates)?
2. Is there a definitional (axiom-free) statement of the isalpha ⇒ isalnum link that is TRUE for Python on every
   string, and can Why3 accept it as a `function` body? Or must it be restricted to length-1 receivers — and is the
   length-1 fact available at `s[j]` in the emitted model?
3. Is R3 already handled?
4. Is the yield (1 stub) worth an emitter change that moves mirror emissions (whole-file re-proofs)? Is there a
   cheaper path the driver missed?

## 7. Constraints any proposal must respect

No new axiom (ledger 3); no gate loosening; the mirror body stays verbatim; refuse-by-default over silent weakening;
a corpus-affecting change is allowed only if the diff is exactly the intended semantic correction and every changed
program re-proves; every mirror file whose emission moves owes a whole-file proof.

## 8. Reproduction

```bash
cd /home/fabrice/git/pycsl            # main; every heavy job through the wrapper:
H=/home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh; export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
# the live body and the emitter arms
sed -n 161,219p src/pycsl/proof2why3/parser.py
grep -n '_IS_PREDS\|COMPUTED receiver' src/pycsl/module6_whyml/expressions.py
# the census evidence
less scratchpad/cv7/proof-parser.log; grep lex scratchpad/cv7/cls.tsv
# a spike: port lex (bin/port-one-mirror-body.py <tree> proof2why3/parser.py lex --convert) in a SCRATCH tree,
# then:  $H env PYTHONHASHSEED=0 .venv/bin/python3 src/pycsl/pycsl.py src/self-annotate/src/proof2why3/parser.py \
#          --import-path src/pycsl --no-proof --keep-mlw        # read the emitted isdigit / isalnum / `in` terms
# and hand-write a .mlw with the proposed ops; prove with: $H why3 prove -P alt-ergo <file>.mlw
```
