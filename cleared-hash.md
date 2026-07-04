# cleared-hash.md — make hash tables faithful (drop the opaque `str_hash_op`)

**One-line goal.** Model every string-keyed dict/set as `map string (option ν)` with the string key used
DIRECTLY (Why3-native string equality), eliminating the opaque `str_hash_op : string → int` (30 sites)
and the emit-time `stable_hash(...)` constant-key hashing. Hash tables stop being opaque because there is
no hash — keys are compared by the faithful, injective, native `String.(=)`.

This is a **feature** (it changes emitted WhyML), not a refactor — so the gate is *the corpus still
proves under the more-faithful model*, NOT byte-diff 0. High blast radius (the core dict/set path);
sequence carefully.

---

## 1. Context / verdict (what the model does TODAY, with citations)

Two representations coexist:

- **Faithful (recent, partial):** a `dict`-typed *parameter* with κ=string already lowers to
  `map string (option ν)` — `_dict_param_whyml_type` (functions.py:1808), driven by `_dict_key_types`
  (κ) from Module5 (`_m5_get_dict_key_type`, Module5:3057; collected at 3139/3168 for params + AnnAssign).
- **Opaque (legacy, the rest):** dict/set **locals, record fields, literals, and sets** are
  `map int (option _)`, and a **string** key is hashed to int with the abstract op:
  ```python
  # expressions.py:3356 (and 29 sibling sites)
  if not self._in_spec and self._is_string_expr(_kir):
      self._add_abstract_op("val str_hash_op (s: string) : int")   # OPAQUE, bodyless
      k = f"(str_hash_op {args[0]})"
  else:
      k = self._coerce_to_int(args[0])
  ```
  and a **literal** field-name key uses the emit-time constant `stable_hash(field)`
  (statements.py:949/979, expressions.py:4235) — `stable_hash` is a real SHA-256 (identifiers.py),
  and it CANNOT be a verified PyCSL method (it IS the hash primitive; that is why §9 of the leaf
  campaign flagged it "inherently opaque").

**The soundness smell.** `str_hash_op` is a bodyless `val` — Why3 treats it as an ARBITRARY total
function. So for two distinct keys `k1 ≠ k2`, Why3 cannot prove `str_hash_op k1 ≠ str_hash_op k2`: the
model admits a **collision**, under which `set d k1 v` also changes `get d k2`. Consequences:
- a membership/read can **conflate two distinct keys** (an over-approximation of aliasing);
- a faithful post-condition like `d["a"] ≠ d["b"]` or `"a" ∉ d after we only inserted "b"` is
  **unprovable** even when true;
- worse, the emit-time `stable_hash("foo")` (a concrete int) and the runtime `str_hash_op "foo"` (an
  abstract int) are **never related** — the model can't connect a literal-key write to a variable-key read.

`map string (option ν)` fixes all three at once: `String.(=)` is injective by construction, there is no
hash function, and literal and variable keys are the SAME string term.

**Verdict.** Migrate all string-keyed dicts/sets to `map string`, dropping `str_hash_op` and the
`stable_hash`-for-keys path. Int-keyed dicts are unchanged (`map int`, the int is the key).

---

## 2. Gate B — SMT-feasibility spike FIRST (hand-write `.mlw`, no PyCSL)

Before any pipeline work, prove the representation reasons at least as fast as the int model, LEADING
with the make-or-break goal (distinct keys don't alias — the property `str_hash_op` cannot give):

```whyml
module HashSpike
  use int.Int  use option.Option  use string.String  use map.Map
  (* the make-or-break: distinct string keys are independent *)
  goal distinct_no_alias :
    forall d: map string (option int), k1 k2: string, v: int.
      k1 <> k2 -> (get (set d k1 (Some v)) k2) = get d k2
  goal present : forall d: map string (option int), v: int.
      get (set d "a" (Some v)) "a" = Some v
  goal absent  : forall d: map string (option int).
      get (set (set (const None) "a" (Some 1)) "b" (Some 2)) "c" = None
end
```
- Record **Valid vs timeout + timing** for Alt-Ergo AND Z3 (string theory can be slower than linear int).
- **Compare** the same three goals in the int+opaque-hash encoding — `distinct_no_alias` is EXPECTED to
  FAIL there (the point of the migration). If the string version proves `distinct_no_alias` fast and the
  other two ≤ int-model time, GO. If string-key `get`/`set` times out at corpus scale, **YAGNI exit**:
  keep the hash but add the honest boundary note (§6) and stop.
- The spike also **decides the empty-map literal**: `(const (None: option _))` keyed by string — confirm
  it type-checks + the polymorphic `map_update_some` unifies at `map string`.

---

## 3. Stages (each with its own driver + gate)

**S0 — spike (above).** Deliverable: a committed `.mlw` under `test-suite/corpus/conformance/` (force-add
the `.expected.mlw` per the `.mlw git add -f` convention) + the timing table. GO/NO-GO recorded here.

**S1 — κ inference: tag every string-keyed dict/set as κ=string.** Today only params/AnnAssign get κ.
Extend the collectors so a dict is κ=string when: (a) its literal has string keys (`{"a": …}`); (b) a
`.get`/subscript/`in`/`[k]=` uses a string key (`_is_string_expr(key)`); (c) a set's elements are strings.
Files: Module5 `_dict_key_types` collection + a Module-6 body-local κ pass mirroring `_dict_value_types`
(local-dict-value-type, already built). Driver: a corpus program with a string-keyed dict LITERAL that
today lowers `map int` + `str_hash_op`.

**S2 — the map TYPE for κ=string, everywhere (not just params).** Route local/field/literal dict + set
type emission through `_dict_param_whyml_type` (or a shared helper) so κ=string ⇒ `map string (option ν)`.
Files: functions.py (`_dict_param_whyml_type`, `_param_type_str`), the first-assign/field/literal dict-type
sites in statements.py/expressions.py. The empty-map literal for a κ=string local emits
`(const (None: option ν)) : map string (option ν)`.

**S3 — the KEY at operations: `str_hash_op k` → `k` for string-keyed maps.** Replace all 30
`(str_hash_op {k})` emissions with the raw string `{k}` WHEN the receiver map is κ=string; keep
`str_hash_op` ONLY for a κ-unknown fallback (see §6). Sites: the 6+ `_add_abstract_op("val str_hash_op…")`
+ `k = f"(str_hash_op …)"` blocks in expressions.py (3356, 3901, 3972, 1474, 551, 3016, 3742) and
statements.py (702). Membership, subscript-read, `.get`, and store all read the same key term.

**S4 — literal/field keys: `stable_hash(field)` → the string literal.** For a κ=string record dict field
(`self.<field>[k]`, `field in self.<field>`), the field-name/element key is the STRING literal, not
`stable_hash(field)`. Sites: statements.py:949/979 (`hash_field = stable_hash(field)`), expressions.py:4235.
`stable_hash` stays ONLY for the non-dict opaque-string→int fallback (expressions.py:277/357/375/1207) —
out of scope (§6).

**S5 — sets.** A set of strings is `map string (option _)` (present ≡ `Some 0`); `x in s` /
`s.add(x)` / `s.discard(x)` use the string `x`. The getattr-set-membership recognizer
(we-are-getting-better #20) switches its key from `str_hash_op x` to `x`.

**S6 — self-annotate mirror re-verify.** The emitter's OWN dicts (`_current_symbol_table`,
`_todict_aliases`, `_METATYPE_TAGS`, …) are string-keyed → the mirror now emits `map string`. Re-run the
full self-annotate proof; fix any leak (this is a real re-verification, not byte-diff 0). This also
*retires* the `stable_hash`-for-keys reason inside the mirror, and may let a previously-blocked leaf
convert.

---

## 4. Critical files

- `src/pycsl/frontend/Module5_IREmitter.py` — κ inference (`_dict_key_types`, `_m5_get_dict_key_type`,
  the literal-key + set-element cases) — S1.
- `src/pycsl/module6_whyml/functions.py` — `_dict_param_whyml_type` (already κ-aware), `_param_type_str` — S2.
- `src/pycsl/module6_whyml/expressions.py` — the 8 `str_hash_op` sites + the DictLit/get/subscript/`in`
  lowering + the `map int` type strings — S2/S3/S4.
- `src/pycsl/module6_whyml/statements.py` — dict store (`d[k]=v`), `hash_field`, set ops — S3/S4/S5.
- `src/pycsl/module6_whyml/preamble.py` — the `str_hash_op` `val` decl (emit only when the κ-unknown
  fallback is actually used) + `use string.String` presence for string-keyed maps.

---

## 5. Out-of-scope / soundness boundaries

- **int-keyed dicts unchanged** — `map int`, the int IS the key; no hash was ever involved.
- **κ-UNKNOWN dicts** (key type not inferable) — keep the `map int` + `str_hash_op` fallback, and emit a
  boundary note. Better κ inference (S1) should shrink this to ≈0; whatever remains is the honest
  residual opacity (documented, never claimed sound). Do NOT add a false injectivity axiom to
  `str_hash_op` — that would be an unsound `#@ proof` (the hash is not a perfect hash).
- **`stable_hash` for non-dict opaque-string→int** (expressions.py:277 etc. — a bare `str→int` coercion,
  not a map key) — out of scope; a separate opacity, tracked in `we-are-getting-better.md` if pursued.
- **String-value dicts** (ν=string) already work (no-more-int-3); this plan only touches the KEY (κ).

---

## 6. Gates (this is a FEATURE — byte-diff is NOT the gate)

Because emission CHANGES for string-keyed dicts, the standard byte-diff-0 gate does not apply. Instead:

1. **Full-corpus proof sweep still green** — `bin/run-reference-tests.sh --pycsl`, PYTHONHASHSEED=0,
   parallel; classify regressions vs now-pass. The new model must PROVE what the old one proved (plus the
   new distinctness properties). Budget MULTIPLE sweeps (core-path change, high blast radius §8.6).
2. **Emission differential as a CHANGE-ENUMERATOR** (not a gate): the set of changed `.mlw` files must
   equal exactly the set of programs using a string-keyed dict/set — anything else is an unintended leak.
3. **Self-annotate mirror re-verifies** (S6) — `\trusted` count non-increasing; sync green.
4. **`str_hash_op` `val` count DROPS** (ideally to 0 across the corpus; residual only for κ-unknown).
5. **5-surface doc-coherency** — update the τ-table (`dict[str,_] ~ map string (option ν)`) in
   static-semantics §1.4 + translational §T.2.2, and the UB/opacity note for the κ-unknown residual.
6. **`proof_axiom_allowlist` unchanged** — NO new axiom (esp. no hash-injectivity axiom).

---

## 7. Reference corpus (per the reference-corpus requirement)

Add to `test-suite/corpus/pycsl-reference/` — one driver per property the faithful model newly proves,
each `#@ ensures` a claim that is UNPROVABLE under the opaque hash and PROVABLE under `map string`:

- **distinct-key non-aliasing** — insert `d["a"]=1`, `d["b"]=2`; `#@ ensures d["a"] == 1` after the second
  write (the opaque hash can't guarantee "b" didn't clobber "a").
- **absent key** — `#@ ensures "c" not in d` after inserting only "a","b".
- **literal↔variable key consistency** — write `d["k"]=v`; read `d[key]` with `key = "k"`; `#@ ensures ==`.
- **negative driver** (`# pycsl-expected: FAIL`) — a genuinely-false claim (`d["a"] == d["b"]`) stays
  unprovable, proving the check can fail.
- update `test-suite/annotations.md` + `traceability-pycsl.md`.

---

## 8. Sequencing & risk

Blast radius is HIGH (touches the dict/set core). Order: **S0 spike (go/no-go)** → S1 κ inference
(additive, low risk) → S2 type emission → S3 key emission (the 30 sites, per-site with a sweep) → S4/S5
literal + set keys → S6 mirror re-verify. Sweep after S2, S3, S5, S6. If S0 shows string-key `map`
operations don't scale under Alt-Ergo/Z3, **stop at YAGNI** and keep the documented opaque fallback — the
plan's value is then the *honest boundary* (κ-unknown residual + no false axiom), not the full migration.

**Expected outcome if it lands:** `str_hash_op` retired for all inferable string-keyed dicts/sets,
`stable_hash`-for-keys retired, the dict/set model faithfully injective, the corpus proving strictly more
(the distinct-key properties), and `stable_hash` reduced to (at most) the non-dict opaque-string→int
fallback — hash tables no longer opaque.

---

## 9. Outcome (executed on branch `ghost-assign-bc6`)

**Verdict: LANDED for the inferable common case (Var-receiver dict/set locals);
record-field dicts/sets kept as the documented κ-known-but-field residual.**

- **S0 spike — GO.** `map string` proves `distinct_no_alias` on both Alt-Ergo (0.03s) and Z3
  (0.01s); the int+opaque-hash encoding times out on both. Fixtures:
  `test-suite/corpus/conformance/spikes/cleared-hash-{string,int-opaque}.mlw`. No scaling concern
  ⇒ no YAGNI exit on provability grounds.
- **S1 (κ inference) — DONE.** Module5 `_build_function_symbol_table` now tags a Var-receiver dict/set
  local κ=string from (a) a string-key literal, (b) string-key usage (`d[k]`/`k in d`/`d.get(k)`),
  (c) set-element methods (`.add`/`.discard`/`.remove`). Additive `setdefault` (never overrides an
  annotation).
- **S2/S3 — DONE.** κ=string locals emit `map string (option ν)` (empty-literal key type inferred
  polymorphically by Why3 from the first native-string update) and every Var-receiver op site
  (subscript r/w, membership, `.get`) reads the raw string key. Fixed a latent membership bug
  (`_coerce_to_int` hashed a string LITERAL key against a `map string` map).
- **S5 (sets) — DONE.** String set locals: `.add`/`.discard` write the raw native element with a
  polymorphic `map_update_some`/`map_update_none`, matching the raw-key membership read.
- **S4 (record fields) — DOCUMENTED RESIDUAL** (choices.md): field κ is knowable but threading it
  would flip the field map type for every string-keyed field of the fragile self-annotate mirror and
  touch ~5 op sites in lockstep, for a 2-test corpus benefit; the plan (§5/§6.4) blesses the residual.
  NO false injectivity axiom; `proof_axiom_allowlist` unchanged.
- **S6 (mirror) — re-verified.** Mirror-sync green after propagating the S5 body; no new mirror
  failure, no new `\trusted` (the pre-existing statements.py "string vs int" proof failure is
  independent — identical at HEAD~2).

**Gates.** Corpus 712/715 (== 710 + 5 new drivers; the 3 known pre-existing failures
0540/0700/0701, ZERO regressions). Emission differential = EXACTLY the string-keyed programs (S1:
only `0751`; S5: only the new drivers — inert on the existing corpus). `str_hash_op` val-decl files
5→4 (residual: `0485` genuine `hash(s)`, `0425` decode-string equality, `0750`/`0746` record fields —
all documented boundaries). 5-surface docs + annotations.md + traceability updated; doc-coherency
green. NO new axiom.

**Reference drivers.** `0755` distinct-key non-aliasing (un-annotated local), `0756` absent key,
`0757` literal↔variable key consistency, `0758` NEGATIVE (`# pycsl-expected: FAIL`, false
`d["a"]==d["b"]`), `0759` string set. All newly provable (or, for `0758`, correctly unprovable) under
`map string`, and unprovable under the retired opaque hash.
