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
