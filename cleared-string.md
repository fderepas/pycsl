# cleared-string.md — remove string opacity (content-faithful string transforms)

**Goal.** Make string TRANSFORMS content-faithful so a driver can prove e.g. `s.lower() == "abc"`,
`s.replace("a","b")[i] == …`, `(a + b)[i] == …`. Today every transform is an opaque abstract `val` with
at most a LENGTH law; only equality/ordering/length are native.

**This is the HARDEST of the opacity plans** (strings are pervasive; char-level reasoning is expensive)
and it is a **feature** (emission changes). Strong incremental/YAGNI discipline: prove one high-value
transform tractable FIRST, expand only if the spike holds.

---

## 1. Context / verdict (today, with citations)

- Strings are Why3 `string.String`: `str_eq_op`/`str_lt_op`/`str_length_op` are FAITHFUL native ops.
- Transforms are OPAQUE bodyless `val`s with only length laws: `str_case_op` (lower/upper,
  expressions.py:885, `ensures { length s >= 1 -> length result >= 1 }`), `str_replace_op`
  (877, conditional length law), `str_strip_op` (892, `length result <= length s`), `str_sub_op`
  (slicing), `str_concat_op`, `str_repeat_op`, `str_mod_op`, `str_repr_op`, `str_split_elem_op`,
  `int_to_string`/`chr_op`. Predicates `str_find/contains/startswith/endswith_op` return ARBITRARY
  results.
- **Root cause:** Why3's builtin `string` is itself nearly opaque — it exposes length + equality but no
  usable char-indexing/decomposition, so a transform cannot be *defined* over the receiver's characters.

**Verdict.** Give strings a **character-sequence content model** — a coercion to `seq int` (Unicode
codepoints) with a `String.length s = Seq.length (chars s)` law and per-char access — so transforms lower
to DEFINING functions over `chars s`. Do it OP-BY-OP behind a spike, starting with the highest-value,
lowest-cost transforms.

---

## 2. Gate B — SMT-feasibility spike FIRST (hand-write `.mlw`)

Decide the representation and confirm tractability. LEAD with the make-or-break (a transform's CONTENT,
not its length):

```whyml
module StrSpike
  use int.Int use seq.Seq use string.String
  (* bridge: a string's character sequence (codepoints) *)
  function chars (s: string) : seq int
  axiom chars_len : forall s. Seq.length (chars s) = String.length s
  (* lower() as a per-char map — the make-or-break CONTENT goal *)
  function to_lower_c (c: int) : int
  function s_lower (s: string) : string
  axiom lower_chars : forall s i. 0 <= i < String.length s ->
      Seq.get (chars (s_lower s)) i = to_lower_c (Seq.get (chars s) i)
  goal lower_idempotent : forall s i. 0 <= i < String.length s ->
      to_lower_c (to_lower_c (Seq.get (chars s) i)) = to_lower_c (Seq.get (chars s) i)
  (* concat content: (a++b)[i] = a[i] for i < |a| *)
  function s_concat (a b: string) : string
  axiom concat_chars : forall a b i. 0 <= i < String.length a ->
      Seq.get (chars (s_concat a b)) i = Seq.get (chars a) i
  goal concat_prefix : forall a b i. 0 <= i < String.length a ->
      Seq.get (chars (s_concat a b)) i = Seq.get (chars a) i
end
```
- Record **Valid vs timeout + timing** (Alt-Ergo AND Z3) — a `seq int` content model with per-char
  quantified laws can trigger E-matching blowups; this is the go/no-go.
- **Compare** to the length-only model's timing on the same corpus subset. If content goals prove and the
  op timing stays ≤ ~2× the length-only model, GO. If not, **YAGNI exit**: keep length-only for that op
  and record it as residual opacity.
- The spike also decides: `chars s : seq int` (codepoints) vs a Why3 `string`-native decomposition — pick
  whichever reasons better; the axioms above are the SOUND CORE (each is a definitional law, provable of
  the real Python semantics, never a false claim).

---

## 3. Stages (op-by-op, highest value first)

**S0 — spike (above)** → GO/NO-GO + timing table committed under `test-suite/corpus/conformance/`.

**S1 — the `chars` bridge + val-bridge pattern.** Preamble: declare `function chars (s: string) : seq int`
+ `axiom chars_len`. Add the val-bridge `val chars_op (s: string) : seq int ensures { result = chars s }`
(a logic symbol can't appear in a program context; mirror `str_length_op`). Everything else builds on this.

**S2 — `.lower()` / `.upper()` (S3.2).** Replace `str_case_op` (length law) with `str_lower`/`str_upper`
functions carrying the `lower_chars` per-char law. Char classifier `to_lower_c`/`to_upper_c` are total
definitional functions. Driver: `#@ ensures s.lower() == "abc"` for a literal, and `s.lower()[i]` content.

**S3 — concatenation `+`.** `str_concat_op` → `s_concat` with the prefix/suffix content laws
(`concat_chars` + the symmetric suffix law). This is the highest-frequency transform (every f-string).

**S4 — slicing `s[i:j]`.** `str_sub_op` → content law `Seq.get (chars (sub s lo len)) k = Seq.get (chars s)
(lo+k)` + the length law it already has. Unblocks `_split_tuple_type`-style prefix strips (leaf campaign).

**S5 — `.replace(a,b)`.** Harder (variable-length). Model the char-for-char case content-faithfully (the
`len a = len b` branch it already length-laws), leave the general grow/shrink case length-only (documented
residual). Do NOT over-claim.

**S6 — predicates `startswith`/`contains`/`==literal`.** `str_startswith_op` → definable from the concat
law (`s.startswith(p) <-> chars-prefix`). `s == "lit"` for a literal already works via `str_eq_op`; extend
to derived strings via the content laws.

**S7 — self-annotate mirror re-verify.** The emitter's own `.replace`/`.lower`/slice chains now carry
content — re-run the mirror proof; may unblock `safe_exc_name` / more leaves (leaf-campaign #38 etc.).

---

## 4. Critical files
- `src/pycsl/module6_whyml/expressions.py` — the transform lowering sites (877/885/892/…) + `_handle_string_value_method`.
- `src/pycsl/module6_whyml/preamble.py` — `chars`/`to_lower_c`/… declarations + the `use seq.Seq` presence + the char-classifier axioms.
- `src/pycsl/module6_whyml/statements.py` — string-local content flow.

## 5. Out-of-scope / soundness
- Only add DEFINITIONAL laws (each true of Python semantics); NO false claims (e.g. never claim
  `replace` preserves length in the general case). Residual grow/shrink cases stay length-only, DOCUMENTED.
- Unicode: model codepoints; full Unicode case-folding tables are out of scope — `to_lower_c` may stay
  abstract (a total function) with only the idempotence/ASCII laws, which is still a strict improvement.
- No new AXIOM in `proof_axiom_allowlist` beyond the definitional bridge laws (which are honest).

## 6. Gates (FEATURE — not byte-diff 0)
Full-corpus proof sweep green (budget multiple, per §8.6 high blast radius); emission differential =
exactly the string-using programs; mirror re-verifies (`\trusted` non-increasing); τ-table + string
semantics doc updated; `str_case_op`/`str_concat_op` opaque-`val` count drops as ops migrate; NO new axiom.

## 7. Reference corpus
One driver per migrated op, each `#@ ensures` a CONTENT claim unprovable under the length-only model:
`s.lower() == "abc"`; `(a + b)[:len(a)] == a`; `s[1:3]` content; `s.startswith("pre")`; a NEGATIVE driver
(`# pycsl-expected: FAIL`) asserting a false content claim. Update annotations.md + traceability.

**Expected outcome:** high-value transforms (lower/upper/concat/slice, and char-for-char replace) become
content-faithful; the general grow/shrink replace + full Unicode folding remain the honest residual;
string equality/ordering/length were already faithful.

---

## OUTCOME (landed)

**Representation.** PIVOTED from the plan's `chars : seq int` codepoint model to the NATIVE Why3 1.8.2
`string.String` decomposition (it is a *rich* theory — `s_at`/`substring`/`concat`/`prefixof`/`contains`/
`indexof`/`replace`/`replaceall` with content axioms — so the "nearly opaque" premise in §1 is outdated;
choices.md cleared-string S1). Concat, slice, and the derived-receiver predicates are content-faithful
with **zero new axioms**.

**S3+S4 concat/slice — DONE.** `(a+b)[:len a]==a` (0765), `s[0:2]+s[2:4]==s[0:4]` (0766); native
`prefixof_concat`/`concat_substring`. Negative 0768 (`(a+b)[:len a]==b`) correctly rejected.

**S6 predicates — DONE.** `startswith`/`endswith`/`find` accept DERIVED string receivers via
`_str_method_recv_and_tail` (0767); simple receivers byte-identical.

**Item 1 `.lower()`/`.upper()` — DONE (sound core) + residual documented.** Replaced the shared
non-deterministic `str_case_op` with DETERMINISTIC `val function str_lower_op`/`str_upper_op`, each
carrying the non-emptiness length law + IDEMPOTENCE (Python `str.lower`/`upper` are idempotent for ALL
strings), encoded via a fresh "already-folded" marker predicate (`str_is_lowerf`/`str_is_upperf`: output
is folded ∧ folded input is a fixed point ⇒ `f(f s)=f s`) — **no new `axiom`**, no self-reference. So
`s.lower().lower()==s.lower()` PROVES and `s.lower()==s.upper()` stays UNKNOWN (distinct symbols; no false
collapse). A STRING-LITERAL receiver is CONSTANT-FOLDED by Python's own method → exact, *full-Unicode-
faithful* content (`"Hello World".upper()=="HELLO WORLD"`; `"ß".upper()`→`"SS"`). Drivers 0791 (positive)
/ 0793 (NEGATIVE: false length-preservation claim rejected). **Residual (boundary):** the per-char ASCII
case-MAP on a SYMBOLIC string is NOT modelled — it would need a codepoint bridge (`chars : seq int`), an
`is_ascii` contract predicate, and `ord`-on-derived-subscript (large new contract surface, ZERO corpus
demand, and a codepoint theory that risks slowing the heavy os/self-annotate sweep); full Unicode folding
(`ß→SS`) is inherently not per-char/length-preserving and stays out of scope on symbolic strings.

**Item 2 general `.replace(a,b)` — DONE (sound core) + residual documented.** `str_replace_op` is now a
DETERMINISTIC `val function` keeping the char-for-char length law (`len pat=len rep→len result=len s`) and
gaining a NOT-CONTAINS identity: if `pat` occurs *nowhere* in `s` (stated as the negation of the
substring-existential the `in`/`not in` operator emits, so `requires pat not in s` connects), then
`result=s`. Empty pat auto-excluded (occurs everywhere), matching CPython — whose empty-pat `replace`
DIFFERS from Why3 `replaceall`, so we deliberately do **not** pin to `String.replaceall`. All-literal
calls constant-fold (`"a.b.c".replace(".","_")=="a_b_c"`). Drivers 0792 (positive) / 0794 (NEGATIVE: false
grow-length claim rejected). **Residual (boundary):** the general grow/shrink CONTENT (single/multi-
occurrence decomposition) is NOT soundly reachable — Why3's `replaceall` has no content axiom beyond
empty-pat/not-contains, and CPython's ALL-occurrences semantics ≠ Why3's FIRST-occurrence `replace`
(whose `replace_substring_indexof` decomposition cannot be borrowed without proving single-occurrence).

**Gate B spikes.** `test-suite/corpus/conformance/spikes/cleared-string-{content,native,residuals}.mlw`
— all content goals Valid on Alt-Ergo AND Z3, no E-matching blowup; the `lower s = s` sentinel correctly
stays Unknown (no over-strong model). **No new axiom** anywhere (`proof_axiom_allowlist` unchanged);
the abstract-op ensures + one fresh uninterpreted marker predicate per case op are the whole delta.

**S7 mirror** — `_handle_string_value_method` is mirror-absent (off the verification path), so the mirror
re-verifies unchanged (`\trusted` non-increasing).
