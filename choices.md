# choices.md — autonomous-execution decision log

Decisions made without supervision during the autonomous execution of
`cleared-pack.md` → `cleared-hash.md` → `cleared-array.md` → `cleared-string.md`.
Standing directive: **always favor rigor**; spend the time to do things well.

Each entry: `## <plan> — <decision>` then **Context / Options / Choice / Rationale**.

---

## cleared-pack S0 — scope the faithful path to single-slot standard integer formats; keep legacy abstract family as documented boundary

**Context.** `struct.pack`/`struct.unpack` lower (expressions.py `_handle_struct_call`) to
abstract `val function struct_pack_<slot_id>`/`struct_unpack_<slot_id>` symbols. `slot_id`
(struct_format.py) encodes only WhyML *types* (`iN` for N int slots), NOT the format chars'
ranges — so `'>HH'` (two uint16) and `'<ii'` (two int32) COLLIDE on `struct_pack_i2`. A single
faithful in-range guard per `slot_id` is therefore either unsound (widest range lets a truncating
value through) or useless (narrowest = bool). The existing `UnixFs.Struct.{i1a1,i2,i18}.round_trip`
axioms are UNGUARDED shape-model witnesses (`struct_pack_i2 := [x0;x1]`, proven by `reflexivity`);
they are consumed by the deep, slow, vacuity-prone os corpus (`src/pycsl_lib/os/UnixInodeFileSystem.py`)
and 5 green corpus tests (0420-0425). Separately, **0665** already realises the *superior* body-faithful
route: hand-written byte codecs (`pack16`/`pack32`/`pack_inode`) that prove the guarded round-trip by
SMT COMPOSITION of value contracts with **zero axioms** — explicitly to ELIMINATE the i18 axiom.

**Options.**
1. Re-key ALL pack/unpack emission to a range-aware `slot_id` and re-verify os + rename the witness
   Coq/Lean module. Cleanest in theory; HIGH risk (destabilises the heavy os proof base I cannot cheaply
   re-verify) and large churn (witness rename, os re-key).
2. Attach a single guard per existing `slot_id`. Unsound (collision) or useless.
3. Route ONLY single-slot pure-integer STANDARD formats (`'>H'`,`'>I'`, ...) — which NO existing
   test/os uses (all existing slots are multi-slot/array: i1a1,i2,i18) — through a NEW faithful path
   with a WIDTH-tagged symbol (`struct_pack_fu16` etc.), size law (`length = calcsize`), in-range
   `requires` (faithful: real `struct.pack` RAISES `struct.error` out-of-range for standard sizes), and
   a guarded round-trip axiom anchored by cited Rocq+Lean byte-codec proofs. Leave legacy i1a1/i2/i18
   untouched (documented coarser boundary). Additive, sound (width in the symbol name ⇒ no collision),
   zero os churn, exercises the exact cited-proof mechanism the DoD names.

**Choice.** Option 3.

**Rationale.** Maximises rigor achievable without destabilising the os proof base: the faithful family
is byte-honest (size + guarded round-trip + guard-necessity all anchored by cross-validated Rocq+Lean),
the guard is load-bearing at BOTH the pack precondition (matches Python's out-of-range `struct.error`)
and the axiom antecedent, and the width tag makes it collision-sound. The legacy unguarded shape-model
axioms and the full-os re-key (plan S5) are recorded as a documented residual: 0665 already shows the
zero-trust body-faithful elimination path for i18, which supersedes re-keying the abstract family.

## cleared-pack S4 (per-field extraction) — YAGNI exit; documented boundary

**Context.** S4 asks for a per-field content law `unpack(data)[k] == <k-th field decode of data>`.
**Options.** (1) Add a per-field decode axiom over the abstract `struct_unpack_f*`; (2) skip.
**Choice.** Skip (documented boundary).
**Rationale.** The faithful family (S1–S3) targets a SINGLE-slot format, so "the k-th field" is the
whole value — the round-trip already delivers it (`unpack(pack x)==x`). A per-field content law only
adds value for MULTI-slot formats, which are out of the faithful family's scope (choices.md S0 entry).
The zero-trust way to get per-field content for multi-slot codecs already exists — the body-faithful
0665 codec exposes each field's exact byte-decode as an SMT-discharged `ensures` with NO axiom, which
strictly dominates a per-field abstract axiom. Adding an abstract per-field axiom here would be effort
on a hypothesis no corpus goal consumes (cf. the axiom-registry cautionary note on vestigial struct
axioms). Recorded as a residual in the UB catalog §7.4a.

## cleared-hash S0 (SMT spike) — GO; `map string` proves the make-or-break, opaque hash cannot

**Context.** Before any pipeline work, hand-write a `.mlw` LEADING with `distinct_no_alias`
(`k1<>k2 -> get (set d k1 v) k2 = get d k2`) plus present/absent/literal-var, in BOTH the
`map string (option int)` encoding and the int+opaque-`str_hash_op` encoding; record Valid/timeout
+ timing for Alt-Ergo AND Z3.
**Result (Why3 1.8.2, AE 2.6.2, Z3 4.13.3).**
| goal | string AE | string Z3 | int+hash AE | int+hash Z3 |
|---|---|---|---|---|
| distinct_no_alias | Valid 0.03s | Valid 0.01s | **Timeout 10s** | **Timeout 10s** |
| present | Valid 0.04s | Valid 0.01s | Valid 0.04s | Valid 0.00s |
| absent | Timeout 10s | Valid 0.01s | — | — |
| literal_var_consistency | Valid 0.03s | Valid 0.01s | — | — |
**Choice.** GO. Fixtures committed at `test-suite/corpus/conformance/spikes/cleared-hash-{string,int-opaque}.mlw`.
**Rationale.** The string encoding proves the make-or-break `distinct_no_alias` fast on BOTH provers;
the opaque-hash encoding CANNOT (times out on both — the model admits a collision, exactly the
unsoundness smell the migration removes). `absent` (distinct string LITERALS) times out on Alt-Ergo
(weak string-literal disequality) but Z3 discharges it in 0.01s — PyCSL runs both provers best-of, so
this is covered (verified end-to-end by driver 0756). No scaling concern → no YAGNI exit.

## cleared-hash S1 (κ-inference scope) — infer κ=string for Var-receiver LOCALS; fields/sets deferred

**Context.** Today κ=string is inferred only for `Dict[str,_]` params/AnnAssign locals (already
`map string`). Un-annotated string-key locals (`d = {}`, then `d[k]=v`) emit `map int` + `str_hash_op`
— a bodyless `val` ILLEGAL in the resulting VC formula (`unbound symbol`), so they FAIL today.
**Options.** (1) Infer κ from a string-key literal + string-key USAGE (subscript/`in`/`.get`, string
literal or `str`-typed name) for function locals/params. (2) Additionally thread κ through record
FIELDS and sets (S4/S5) in the same pass.
**Choice.** (1) now (Module5 `_build_function_symbol_table`, additive `setdefault` — never overrides
an annotation, only tags on genuine string-key evidence). Fields/sets assessed separately (see the
S4 entry); Python dicts are homogeneously keyed, so any string-key evidence pins κ=string soundly.
**Rationale.** Highest value / lowest risk: currently-FAILING un-annotated locals become faithful;
CANNOT regress a passing test (a passing dict local used with int keys is never tagged). Empirically
confirmed: full corpus 707/710 (== the 3 known pre-existing failures 0540/0700/0701, zero
regressions); emission differential = EXACTLY {0751} (a string→str local dict, `str_hash_op` dropped
for native keys); `str_hash_op` val-decl files 5→4. Also fixed an S3 latent bug: membership on a
κ=string map ran `_coerce_to_int` on a string LITERAL key → `stable_hash` int against a `map string`
map (type error); now passes the raw string.

## cleared-hash S5 (sets) — migrate string SET LOCALS; keep the write/read consistent

**Context.** A runtime set shares the dict `map` model; the element IS the key. S1's membership
inference (`x in s`) tags a set local κ=string, and the S3 membership fix reads the raw string — but
the set `.add`/`.discard` write (statements.py) still hashed the element (`str_hash_op`/`stable_hash`),
so a string set local became INCONSISTENT (write int key, read string key → type error).
**Options.** (1) Complete S5: thread κ=string through the set-add/discard write (raw string element +
polymorphic `map_update_some`/`_none`) AND extend S1 to tag a set from `.add`/`.discard`/`.remove` with
a string element, so write and read always agree. (2) Restrict S1 to NOT tag sets (keep sets fully
hashed & consistent) — leaves sets a residual.
**Choice.** (1). Driver 0759 (string set, distinct-element absence).
**Rationale.** Consistency is mandatory (an inconsistent write/read is a type error, not merely coarse),
so the honest options are "both native" or "both hashed"; native is strictly more faithful and matches
the delivered dict-local path. Empirically inert on the existing corpus (emission differential vs the
S0-S3 commit = ONLY the new drivers 0755-0759; no existing set program was string-keyed-via-inference),
so zero regression risk: full sweep 712/715 (== 710 + 5 new drivers; same 3 known pre-existing
failures). A set tagged κ=string only via string evidence; an int/opaque set is never tagged.

## cleared-hash S4 (record-field dicts/sets) — DOCUMENTED RESIDUAL boundary (not a false axiom)

**Context.** A record-*field* dict/set (`self.TAGS: Dict[str,str]`, `self._nested: Dict[str,List[str]]`)
still lowers to `map int (option ν)` + the opaque `str_hash_op` (corpus 0750, 0746; and the
self-annotate mirror's many string-keyed fields — `_current_symbol_table`, etc.). Its κ IS knowable
from the annotation, so this is κ-known-but-field, not truly κ-unknown.
**Options.** (1) Thread field κ (`field_key_types`, a `_self_field_dict_kappa` helper, `map string`
field-type emission in preamble.py, and a consistent raw-key update at ALL ~5 field-dict op sites:
store, `.get`, subscript read, membership, set-add). (2) Keep fields on the hash as a documented
residual (plan §5/§6.4 explicitly permit it).
**Choice.** (2), for THIS pass. Recorded, never claimed collision-sound; NO false injectivity axiom
added to `str_hash_op` (`proof_axiom_allowlist` unchanged).
**Rationale.** Risk/reward is inverted for fields: the change must flip the field map type for EVERY
string-keyed field of the already-fragile self-annotate mirror (which has a PRE-EXISTING string/int
type error in statements.py, confirmed identical at HEAD~1 — not mine) and update all field-dict op
sites in lockstep; any missed site is a type-error regression on the heavy mirror/os proof base. The
corpus benefit is 2 tests (0750, 0746) whose own docstrings state they need only result TYPES, not tag
values (a deliberately coarse abstract-field model). The SMT spike already proved `map string` scales
(so this is NOT a provability limit — it is a bounded-blast-radius / YAGNI risk call, exactly the
residual the plan blesses). The core soundness win — removing the collision-unsoundness smell for the
common inferable Var-receiver dict/set — is fully delivered by S1-S3/S5. Fields remain the honest,
documented opacity boundary; a future pass can thread field κ behind its own sweep + mirror re-verify.

## cleared-pack S5 (os corpus re-key) — keep os on legacy family; documented boundary

**Context.** S5 asks to re-verify the os inode blit/read-back corpus against the faithful round-trip.
**Options.** (1) Re-key `src/pycsl_lib/os/UnixInodeFileSystem.py` (multi-slot '>IHHHHHII10Ixx' / '>H30s')
to a faithful multi-slot family; (2) leave os as-is.
**Choice.** Leave os on its existing path (documented boundary).
**Rationale.** (a) The faithful family is single-slot by construction (S0 soundness scope); os uses
multi-slot formats, which would require the range-aware multi-slot machinery the S0 entry explicitly
deferred to avoid destabilising the heavy os proof base. (b) More decisively, the body-verified
`src/pycsl_lib/os` ALREADY eliminated the struct round-trip axiom via the 0665-style pure-Python byte
codec (see axiom-registry.md cautionary note: "removing all eight [citations] left the os fully proven,
0 unproven goals"). The os read-back is therefore ALREADY honest — re-keying it to a new faithful
struct axiom would RE-INTRODUCE an axiom the body-verified os no longer needs. The only os path still on
the abstract codec is the separate `struct.pack`-based stub, whose legacy `UnixFs.Struct.*` axioms are
retained and documented. No os regression: 0420–0425 + 0665 verify unchanged.

## cleared-array S0 + S0-bis (SMT spike) — GO; per-index law AND sorted permut+sortedness both tractable

**Context.** Before touching the comprehension lowering, hand-write a `.mlw` LEADING with the make-or-break
per-index defining law `forall i. 0<=i<len src -> result[i] = f(src[i])` consumed at a USE site (a `val`
with the quantified `ensures`, instantiated at two independent indices to probe E-matching blowup), plus
the identity specialization, the filter length bound, and — separately (S0-bis) — the `sorted`
permutation+sortedness law (`permut_all src result /\ forall k1<=k2. result[k1] <= result[k2]`).
**Result (Why3 1.8.2, AE 2.6.2, Z3 4.13.3).**
| VC | Alt-Ergo | Z3 |
|---|---|---|
| test_elt (per-index law, 2-point instantiation) | Valid 0.04s / 27 steps | Valid 0.02s / 32576 steps |
| test_id (identity result[i]=src[i]) | Valid 0.04s / 14 steps | Valid 0.02s / 32002 steps |
| test_filt (length bound) | Valid 0.03s | Valid 0.01s |
| test_sorted (permut_all + sortedness) | Valid 0.04s / 16 steps | Valid 0.02s / 32906 steps |
**Choice.** GO on S1–S4 (content laws) AND S5 (`sorted` permut+sortedness — the S0-bis spike HOLDS, it is
NOT intractable). Fixture: `test-suite/corpus/conformance/spikes/cleared-array-comp.mlw`.
**Rationale.** The quantified per-index law instantiates cleanly at multiple points with no E-matching
blowup on either prover (AE step counts tiny); `permut_all` + the pairwise sortedness predicate are
discharged fast — so `sorted_1` can gain a real permutation+sortedness contract with NO new global axiom
(the ensures is on the abstract `val`, discharged where used). One import gotcha recorded: `use map.Map`
and `use array.Array` both export the `[]` mixfix; a comprehension `.mlw` must NOT import `map.Map` when
it uses array indexing (they collide → "expected 'xi -> 'xi1").

## cleared-array S1–S4 — lift ONLY pure-int (identity + `+ - *`) elements over the target; opaque otherwise

**Context.** After the GO spike, the ListComp lowering must attach a per-index content law
`result[i] = <elt[target:=src[i]]>`. The element `elt` is an arbitrary sub-expression; to appear in a
logic `ensures` on the abstract `val list_content_comp_<n>(src)` it must be (a) a PURE, TOTAL `int` term
and (b) reference no free variable other than the loop target (the val has only `src` as a parameter).
**Options.** (1) Lift EVERY element by textual substitution and let Why3 typecheck reject the bad ones —
fragile (a `val`-call element or a partial `div` would emit ill-typed/unsound `ensures`, and per-instance
typecheck failure is hard to detect additively). (2) Lift a fresh UNINTERPRETED `elt_fn_<n>` so
`result[i] = elt_fn(src[i])` for ANY element — sound but the driver cannot name `elt_fn`, so it proves
nothing a driver actually writes (`result[i] == a[i]+1` won't match). (3) Whitelist a small set of element
node shapes KNOWN to lower to pure-int logic terms — identity `Var(target)`, integer literals, and the
total operators `+ - *` (recursively) — plus a free-variable check `⊆ {target}`; everything else falls
through to the existing opaque length-only path.
**Choice.** Option 3 (`_comp_elt_pure_int` + `_content_comp`). Division/modulo excluded (partiality —
ZeroDivisionError must not leak into a logic `ensures`); calls/subscripts/attributes/comparisons/booleans
excluded (not guaranteed pure-int). Seq-local sources are left to the existing seq comprehension path.
**Rationale.** Maximally rigorous: every emitted content law is a genuine pure-int term the driver can
name and match (verified by 0761/0762), the negative 0764 shows the law is not over-strong, and the
whitelist can only UNDER-approximate (fall through to opaque) — it can never emit a false content claim.
S2 projection `[x.f …]` and S3 call `[g(x) …]` in the int-heavy model do not reliably lower to pure-int
logic terms (they hit opaque `getattr`/`val` ops), so they stay in the opaque residual DOCUMENTED rather
than risk an ill-typed or unsound `ensures`; arithmetic `[x+1 …]` is the landed S3 representative of "the
element is a computed function of the source element". No new global axiom (definitional `ensures` on the
abstract val).

## cleared-array S6 (dict/set comprehensions) — YAGNI exit; documented opaque residual

**Context.** S6 asks for dict/set comprehension content laws (`{k: v for …}` → map-get law; `{f(x) …}` →
membership). **Options.** (1) implement map/set membership laws; (2) keep opaque, document.
**Choice.** Keep opaque (documented in §T.11.1 G6 + §T.14.5a). **Rationale.** No corpus consumes dict/set
comprehension content; the value/key element shapes face the SAME int-model purity wall as ListComp S2/S3
(the only shapes that lift cleanly are already covered for lists), and the set-membership law is a distinct
theory add with no demand. Recording as a residual rather than speculative machinery (cf. the axiom-registry
caution on vestigial abstractions). The list-comprehension content path (S1–S4) + `sorted` (S5) deliver the
plan's headline content-faithfulness; dict/set remain the honest opaque boundary.

## cleared-array (reversed) — keep `array_rev` opaque; do NOT add a content law (axiom entanglement)

**Context.** The plan says "also covers `reversed`". `reversed(xs)` lowers to `val function array_rev
(a: array int)`, which is ALSO an `_AXIOM_FUNCTIONS` symbol (preamble.py:1396): the cited `rev_permutation`
axiom `forall s. permut (array_rev s) s` (corpus 0539) declares it in the axiom block.
**Options.** (1) Add an exact content `ensures { result[i] = a[len-1-i] }` to `array_rev`; (2) leave opaque.
**Choice.** Leave opaque. **Rationale.** A content `ensures` on the abstract-op declaration would be
DROPPED for files that cite `rev_permutation` (the axiom block emits the plain `val function array_rev`,
and `_insert_abstract_val_block` skips the abstract-op twin by name) — so the law would exist for some
files and not others, an inconsistency for zero demand (no corpus needs reversed CONTENT; 0539 needs only
the permutation, already delivered by the cited axiom). `sorted` (S5) is the landed permutation/ordering
win; `reversed` content is a documented future residual, not worth the axiom-block entanglement.

## cleared-string S0 (SMT spike) — GO; `chars : seq int` codepoint model proves all content goals fast, no E-matching blowup

**Context.** Before any pipeline work, hand-write a `.mlw` LEADING with the make-or-break CONTENT
goals (lower idempotence at an index, concat-prefix at two indices, `(a++b)[:len a]==a` reduced to
per-index content, slice content at two indices) under the `chars s : seq int` codepoint model, plus
a length-only baseline of the same shape; record Valid/timeout + timing for Alt-Ergo AND Z3.
**Result (Why3 1.8.2, AE 2.6.2, Z3 4.13.3).**
| goal | Alt-Ergo | Z3 |
|---|---|---|
| g_lower_idem (per-char lower idempotence) | Valid 0.05s / 45 steps | Valid 0.01s / 10274 steps |
| g_concat_prefix2 (prefix at 2 indices) | Valid 0.05s / 36 steps | Valid 0.01s / 10716 steps |
| g_concat_slice ((a++b)[:len a] content) | Valid 0.06s / 132 steps | Valid 0.01s / 10821 steps |
| g_slice2 (slice content at 2 indices) | Valid 0.04s / 41 steps | Valid 0.01s / 11109 steps |
| g_len_concat_slice (length-only baseline) | Valid 0.21s / 2184 steps | Valid 0.01s / 5265 steps |
**Choice.** GO on the `chars : seq int` codepoint representation for S1–S6. Fixture committed at
`test-suite/corpus/conformance/spikes/cleared-string-content.mlw`.
**Rationale.** Every content goal proves fast on BOTH provers with NO E-matching blowup (AE step
counts 36–132, i.e. SMALLER than the length-only baseline's 2184) — the feared `seq int` per-char
quantified-law blowup does not materialise, and content timing is at or below the length-only model,
so the ~2x YAGNI threshold is cleared with large margin. The `chars` bridge + per-char `Seq.get`
laws (`lower_chars`/`concat_prefix`/`concat_suffix`/`sub_chars`) each are definitional laws true of
Python semantics; `to_lower_c` stays an abstract total char-classifier with only the idempotence law
(full Unicode folding out of scope, documented). Representation `chars : seq int` reasons better than
a Why3-string-native decomposition (string.String exposes no usable char indexing), so it is chosen.
