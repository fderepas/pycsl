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

## cleared-hash S4 (record fields, FOLLOW-UP) — threaded field κ; str_hash_op retired for annotated string-keyed fields

**Context.** The prior S4 entry deferred record-field dicts/sets as a bounded-blast-radius risk call
(the "future pass" it named). This follow-up (branch `ghost-assign-bc6`) DID it: a record FIELD whose
declared type is `Dict[str, ν]`/`Set[str]`/`FrozenSet[str]` now lowers to `map string (option ν)` with
the native, injective Why3 `String.(=)` key, retiring the opaque `str_hash_op` for that field.
**Options.** (1) Thread field κ end-to-end (a `field_key_types` collection mirroring `field_value_types`,
a `_self_field_dict_kappa` helper mirroring `_self_field_dict_nu`, `map string` field-type emission in
preamble.py, and a RAW-key update at ALL field op sites in lockstep). (2) Keep the documented residual.
**Choice.** (1). Implemented additively and tightly guarded: only a field with an INFERABLE string κ
(from its `Dict[str,ν]`/`Set[str]`/`FrozenSet[str]` annotation) flips; an int-keyed field, and an
un-annotated field initialized from `{}` (κ genuinely unknowable at the field), stay `map int`
byte-identically. NO false injectivity axiom; `proof_axiom_allowlist` unchanged.
**Op sites threaded (read/write in lockstep — a mismatch is a WhyML type error).** Store
`self.d[k]=v` (statements.py `_handle_array_set_stmt`, also picks up the field ν); subscript-read
`self.d[k]` direct (expressions.py) and via a getattr-bound alias; `.get` (`_lower_dict_get_call`);
membership `k in self.d` direct + the `x in getattr(self, "<field>", set())` defensive form; set
`.add`/`.discard` (statements.py `_handle_expr_stmt`, with the polymorphic `map_update_some`/`_none`).
**Rationale / why now safe.** The emission differential over the full pycsl-reference corpus is EXACTLY
{0746, 0750} (the two pre-existing record-field dict tests, both still PROVE, now native) plus the 5
new field drivers — zero leak onto any other program (an int-keyed or un-annotated field is never
flipped). The self-annotate mirror stays green: mirror-sync EXIT 0 after propagating the two verbatim
statements.py edits, `\trusted` count unchanged (statements.py 43=43; mirror total 1262), and the
`_self_field_dict_kappa`/`_nu` calls added to the mirror follow the SAME established
undefined-helper-call pattern the mirror already uses (`_str_operand_to_int`, `_handle_if_stmt`, …).
The residual named by the prior entry (mirror fragility + lockstep op sites) is discharged by the
tight guard + the enumerated op-site list, not by a false axiom.
**Drivers.** 0772 distinct-key non-aliasing on `self.d`, 0773 absent-key, 0774 literal↔variable
consistency, 0775 `set[str]` field, 0776 NEGATIVE (`# pycsl-expected: FAIL`, false
`self.d["a"]==self.d["b"]` stays unprovable). All newly provable (or correctly unprovable) on a
`self.<field>` — impossible under the retired opaque hash.

## cleared-hash residual-close (items 1 & 2) — shrink κ inference to concat keys; LOCK the honest κ-unknown boundary; non-dict-key hashing out-of-scope

**Context.** The last residuals of `cleared-hash.md` §5: (1) genuinely-unknowable-κ dicts/sets on the
`map int`+`str_hash_op` fallback, and (2) non-dict-key hashing (`0485` `hash(s)`, `0425` decode-equality).
Full-corpus emission shows exactly TWO `.mlw` declare `val str_hash_op` — `0485`, `0425` — and NEITHER
has any `Map.get`/`map` (i.e. neither is a dict/set key op). So corpus-wide there are ZERO string-keyed
dict/set hash fallbacks left.
**Options (item 1a — shrink).** (1) Extend κ inference to every SOUND missed string-key signal.
(2) Declare inference already maximal.
**Choice.** (1) for the one signal that is both SOUND and BENEFICIAL: a string CONCATENATION key
`d[a + b]` (both operands `str`). Module5 `_is_str_key` now recognizes a `str + str` BinOp (recurses).
`str_concat_op` is pinned to Why3's left-cancellative `concat`, so tagging κ=string reads the raw native
key and RECOVERS distinct-key non-aliasing (`a != c ⇒ d[a+b]` unaffected by `d[c+b]`) — a real theorem,
NOT a false axiom. Positive driver `0795`. All OTHER un-inferred string-key forms are declared maximal
with evidence: a derived-string key (`s.upper()` → opaque `str_upper_op`, genuinely non-injective) gains
ZERO injectivity from a native key so stays on the hash; an unannotated/`Any` key is already passed RAW
+ polymorphic (native-equal); a dict comprehension is a SEPARATE `map int` comprehension-machinery
opacity (cleared-array).
**Options (item 1b — lock).** XFAIL driver proving the fallback is HONEST.
**Choice.** `0796` (`# pycsl-expected: FAIL`): a `d[s.upper()]` dict stays on `str_hash_op`; its
distinct-key non-aliasing claim is UNPROVABLE and must be — evidence that no false injectivity axiom is
smuggled onto `str_hash_op` (`proof_axiom_allowlist` unchanged).
**Choice (item 2).** CLOSE as a SEPARATE out-of-scope opacity: `0485` `hash(s)` (opaque `int` IS the real
Python semantics) and `0425` decode-equality (string-content comparison, cleared-string territory) are
non-dict-key — documented in `we-are-getting-better.md` §I (39, 40). No faithful model is forced onto a
genuine `hash()`.
**Rationale / gates.** Byte-diff-0 over the entire pre-existing corpus (no program used an untagged
concat key → the extension is inert; emission differential = EXACTLY {0795, 0796}). Full corpus proof
sweep green (identical VCs ⇒ identical results; 0795 PASS, 0796 correct XFAIL). `proof_axiom_allowlist`
UNCHANGED. Mirror-sync EXIT 0 (a Module5 front-end signal, not a mirrored emitter method; `\trusted`
unchanged). 5-surface docs + annotations.md + traceability 12.5.7 updated; doc-coherency green. Item 1
and item 2 CLOSED (`cleared-hash.md` §10).

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

## cleared-array S2 (Round 2) — LIFT projection `[p.x for p in a]`; call + subscript-projection stay opaque (sharpened)

**Context.** Round 1 (dcaf2367) kept projection `[x.f …]` and call `[g(x) …]` opaque, blaming "the
int-heavy model doesn't reliably lower to pure-int logic terms." Round 2 re-examined with a spike-first
diagnosis. **Spike (`proj_call_spike.mlw`, Why3 1.8.2): GO** — the per-index projection law
`result[i] = get_f(src[i])` consumed at a use-site at TWO indices (AE 0.03s/27 steps, Z3 0.01s/7014) and
the call law `result[i] = g(src[i])` with a propagated `ensures` (AE 0.03s/22, Z3 0.01s/7161) BOTH prove
fast, no E-matching blowup. So the SMT law was NEVER the obstacle. The real obstacles were two engineering
gaps, diagnosed empirically:
- `[p.x for p in a]` over `List[Point]` → source is `array int` (records collapse), so `p.x` lowers to
  the abstract getter `get_x`. That getter was a program `val` (non-deterministic, unusable in an
  `ensures`), and the contract grammar could not even PARSE the consumer `a[k].x`.

**Options.** (1) Give up (Round-1 residual). (2) Make `get_x` a `val function` GLOBALLY — rejected:
changes emission for EVERY getattr program (violates the emission-differential-= comprehension-programs
gate). (3) Confine the lift: emit `get_x` as a pure `val function` ONLY in spec context (`self._in_spec`),
add a `SubscriptFieldAccess` contract atom (`a[k].field`), and extend the `_content_comp` whitelist to
`Attribute` elements over the target (+ arithmetic over them).

**Choice.** Option 3. Projection `[p.x for p in a]` / `[p.x + p.y for p in a]` now proves
`\result[k] == a[k].x` (drivers 0769/0770; NEGATIVE 0771 rejects `a[k].y`). **Rationale / soundness:** a
field read IS deterministic, so `val function get_x` is a faithful refinement (removes spurious
non-determinism, never adds a value claim); `result[i] = get_x(src[i])` is exactly the true semantics
`a[i].x` re-expressed with the SAME getter the driver's `a[k].x` lowers to. Confinement is provable: the
`val`→`val function` toggle fires only in spec context, and 0/105 existing getattr-in-contract corpus
files reach the spec-context `get_` fallback → INERT on the corpus; the `SubscriptFieldAccess` atom is a
brand-new grammar form. No global axiom (definitional `ensures` on the abstract val).

**Call `[g(x) …]` — STAYS OPAQUE (sharpened, not "int-heavy hand-wave").** A module function lowers to a
program `let g`; `g` is unusable in a logic term and a driver's own `\result == g(a[i])` does NOT
type-check today (`unbound function or predicate symbol 'g'` — demonstrated). Lifting requires a separate
language capability (purity analysis + spec-callable `let function` emission) with zero existing consumer.
YAGNI exit.

**Subscript projection `[x[k] …]` — STAYS OPAQUE (sharpened).** `List[List[int]]` / `List[Dict[…]]`
collapse to `array int` (empirically verified), so the element `x` is an `int` with no faithfully-typed
collection to index; the `map string` dict model never reaches a *list element*. No faithful law
expressible.

## cleared-array Round 3 — LIFT call `[g(x) …]`, dict `{x:v …}`, set `{f(x) …}`, filter-subset; item 2 stays boundary

**Context.** The four recorded residuals (call comprehensions, subscript projection, dict/set comps,
reversed+filter). Spike-first (`cleared-array-residuals.mlw`, Why3 1.8.2): the call law, dict/set
membership laws, and filter-subset law ALL prove Valid on Alt-Ergo AND Z3 at ≥2 indices/keys, no
E-matching blowup — GO for items 1, 3, 4.

**Item 1 (call) — LIFT. The recorded blocker was mis-diagnosed.** A PURE module function `g` (`assigns
\nothing`, non-diverging) is ALREADY emitted as `let function g` (via `emits_as_logic_symbol`), and a
driver's `\result[k] == g(a[k])` DOES type-check today (demonstrated — Round 2's claim that it doesn't
was for an IMPURE `g`). **Options.** (1) Give up (Round-2 YAGNI). (2) Build a NEW purity/spec-callable
feature — unnecessary, it already exists. (3) Lift `Call(g, pure-int args)` in the whitelist gated on
`g ∈ _emitted_logic_funcs` (populated in callee-before-caller SCC order), and DEFER the content-law val
(`_late_content_ops`) so it is spliced in after `g` — the early abstract-op block precedes all functions,
which would leave `g` unbound. **Choice.** Option 3. **Soundness:** a pure `let function` is a total
deterministic logic symbol, so `result[i]=g(src[i])` is faithful; a non-pure callee never enters the set
(opaque fallback); a mis-anchored deferral fails L3 typecheck loudly, never a false proof. Drivers
0783/0784.

**Item 3 (dict/set) — LIFT where key/value/elt lift.** Dict `{x: v(x) for x in a}` — **identity key**
only (the soundness pin: a non-injective key ⇒ last-write-wins ⇒ the per-source law is unsound; an
identity key makes every collision map to the same key AND deterministic value) + pure-int value →
`Map.get result (src[i]) = Some v`. Set `{f(x) for x in a}` (pure-int elt) → `Map.get result (f(src[i]))
= Some 0` (membership). Both under-approximate (say nothing about absent keys/elts). A set/dict return
type now triggers the map import. Non-identity key / non-pure-int value or elt stay opaque. Drivers
0785-0788. **Rationale.** Overturns the Round-1 S6 YAGNI now that the make-or-break shapes (identity-key
dict, pure-int set) lift soundly and the SMT membership laws are proven tractable; still refuses the
collision-unsound / impure shapes.

**Item 4 (filter) — LIFT the content-subset law; reversed stays opaque.** Identity element + a filter
predicate that lifts to a pure-bool logic term (comparisons + `and`/`or`/`not`, `_comp_cond_pure_bool`) →
each survivor satisfies `cond` ∧ appears in `src` (the source index is lost, so NO per-index content).
Non-identity/non-lifting keep length-only. Drivers 0789/0790. `reversed` unchanged (axiom-block
entanglement, prior entry).

**Item 2 (subscript projection) — CLOSED-AS-BOUNDARY (unchanged, evidence re-verified).** `List[List[int]]`
and `List[Dict[str,int]]` both collapse the param to `array int` (symbol-table `'list'`); the inner
collection type is not threaded, so no faithfully-typed element to index. The fix (nested element-type
threading `array (array int)`) is a pervasive no-more-int type-model change with zero consumer — deferred.

**Gates.** Corpus 735/738 (only 0540/0700/0701; no regressions). Emission byte-diff vs HEAD = exactly
0763 (monotone filter-subset addition) + 8 new drivers; 662 files byte-identical. doc-coherency +
mirror-sync green; NO new axiom (definitional `ensures` on abstract vals).

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

## cleared-string S1 (representation PIVOT) — use the NATIVE Why3 `string.String` decomposition, NOT the plan's `chars : seq int` model

**Context.** The plan's premise (§1 root cause) is that "Why3's builtin `string` is nearly opaque —
exposes length + equality but no usable char-indexing/decomposition", and it prescribes adding a
`chars : seq int` codepoint model with new bridge axioms (`chars_len`, per-char content laws, and — as
the spike revealed — an extensionality axiom `chars_ext`). During S1 I inspected the actual Why3 1.8.2
`string.mlw` in use and found this premise is OUTDATED: `string.String` is a RICH theory exposing
`s_at` (char-at-index), `substring`, `concat`, `prefixof`/`suffixof`/`contains`/`indexof`/`replace`/
`replaceall` with full content axioms (`concat_at`, `substring_at`, `substring_length`,
`concat_substring`, `substring_substring`, `prefixof_concat`, `length_concat`, …). Crucially,
PyCSL's abstract vals ALREADY pin their results to these native symbols: `str_concat_op` ⊨
`result = concat a b`, `str_sub_op` ⊨ `result = String.substring s lo len`, `str_startswith_op` ⊨
`result=1 <-> substring s 0 (len p)=p`.
**Options.** (1) Implement the plan literally: add `chars : seq int` + `chars_len`/`chars_ext`/per-char
laws to every string program, and re-express every transform over `chars`. (2) Use the NATIVE
`string.String` decomposition already in scope — add reference drivers + close the small genuine gaps.
The spike explicitly delegates this choice to "whichever reasons better".
**Evidence (Why3 1.8.2, AE 2.6.2, Z3 4.13.3).** Native-only spike (`native.mlw`, NO new axioms):
`substring (concat a b) 0 (length a) = a` — AE Valid 0.04s/16 steps, Z3 0.01s; `prefixof p (concat p r)`
— Valid fast both; per-char `s_at (concat a b) i = s_at a i` — Valid fast; slice `s_at (substring …)`
— AE 0.05s (Z3 OOM, covered by AE under best-of-N). End-to-end the headline drivers ALREADY prove with
today's code: `(a+b)[:len a]==a` (0765) and `s[0:i]+s[i:]==s` prove with zero source change.
**Choice.** Option 2 — the native `string.String` representation. The `chars : seq int` apparatus is
NOT added.
**Rationale.** Native reasons strictly better: (a) ZERO new axioms (the plan's chars model needs 3+
bridge axioms incl. extensionality — a TCB growth the native path avoids entirely); (b) it is ALREADY
imported (`use string.String`), so no `use seq.Seq` + per-program preamble block is injected into every
string program — the emission stays byte-identical on the whole existing corpus (verified: the S6
change diffs 0 on all 5 simple-receiver corpus files); (c) it does not risk slowing the heavy os /
self-annotate proof base with a codepoint theory. This is the plan's own "pick whichever reasons
better / YAGNI exit" applied at the representation level, with the make-or-break goals proven on the
chosen representation.

## cleared-string S3+S4 (concat + slice) — ALREADY content-faithful natively; deliverable is the locking drivers

**Context.** With the native representation, `+` and `[i:j]` already carry exact content via
`str_concat_op`/`str_sub_op`'s pin to `concat`/`substring` and Why3's `prefixof_concat` /
`concat_substring` / `substring_substring` axioms.
**Choice.** No emitter change for concat/slice; ADD reference drivers 0765 (`(a+b)[:len a]==a`) and
0766 (`s[0:2]+s[2:4]==s[0:4]`) that PROVE the content and lock it against regression, plus the negative
0768 (`(a+b)[:len a]==b` — `# pycsl-expected: FAIL`).
**Rationale.** The plan's §7 drivers were MISSING; adding them is the real, honest deliverable for
these ops (the content-faithfulness itself is delivered by the native theory). 0766 proves in 0.79s
(acceptable); the headline 0765 in 0.01s.

## cleared-string S6 (predicates) — extend content-faithful startswith/endswith/find to DERIVED receivers

**Context.** `_content_string_method` already gave startswith/endswith/find a native-`substring`
witness `ensures`, but ONLY for a SIMPLE `str`-typed Var receiver (`self._current_symbol_table.get(recv)
== "str"`); a derived-string receiver (`(a+b).startswith(a)`) fell through to an opaque uninterpreted
0/1 predicate.
**Options.** (1) Leave derived receivers opaque. (2) Route the receiver through the existing
`_str_method_recv_and_tail` (which already supports computed receivers for the value-method path) and
gate on `_is_string_expr(recv_ir)`, lowering the receiver expression.
**Choice.** (2). Driver 0767 (`(pre+rest).startswith(pre)` proves; plus the simple-receiver form).
**Rationale.** Sound (the witness ties result to `substring recv 0 (len p) = p`, and the derived recv
is pinned to its native op) and strictly more faithful. Zero blast radius: `_is_string_expr(Var)` is a
SUPERSET of the old symbol-table check, so simple receivers emit byte-identically (verified diff-0 on
0447/0453/0491/0492/0493); no existing corpus file uses a derived-receiver string predicate, so the
emission differential is EXACTLY the new drivers. Full sweep 717/720 (== the 3 known pre-existing
failures 0540/0700/0701; zero regressions).

## cleared-string S2 (lower/upper) + S5 (general replace) — YAGNI exit; documented residual

**Context.** `.lower()`/`.upper()` lower to `str_case_op` (a `val`, non-emptiness law only); Why3's
`string.String` exposes NO case-folding operation. `.replace` keeps the sound char-for-char length law
(`len pat=len rep -> len result=len s`); the general grow/shrink case is length-free.
**Options.** (1) Model case folding content-faithfully (introduce a deterministic `str_lower`/`str_upper`
logic function + `to_lower_c` codepoint classifier + a literal→codepoint value bridge so
`"ABC".lower()=="abc"` proves). (2) Keep length-only, document as residual.
**Choice.** (2), for both lower/upper CONTENT and general replace.
**Rationale/evidence.** (a) SOUNDNESS: Python's `str.lower()`/`.upper()` use FULL Unicode case folding
which is NOT length-preserving (`"ß".upper()=="SS"`, `"İ".lower()` grows), so NO unconditional per-char
or length law is sound; a faithful model would need an `is_ascii`-guarded content law plus the
literal→codepoint value machinery — high cost. (b) DEMAND: no corpus goal needs lower/upper CONTENT
(the string-ness/length is what programs use); `.lower()` is even rejected in a contract, so content is
only expressible as `\result == "lit"`. (c) NO false claim is reachable today: `str_case_op` is a `val`
(fresh per call), so a body-level `s.lower()==s.upper()` does NOT prove (verified Unknown) — the shared
symbol is NOT a soundness hole. Modelling simple/ASCII folding when Python does full folding would also
DIVERGE from faithful semantics for the ß-class. Recorded as the honest residual (translational
§T.6.15, §T.11.1 G2, annotations.md). General grow/shrink replace likewise stays length-only (never
claims length preservation — the sound char-for-char law is retained).

## cleared-pack RESIDUALS (items 1-5) — widen the faithful family to a per-field width/signedness tag; reject native alignment; supersede os re-key

**Context.** The single-slot faithful `Pycsl.Struct.Std` family (S1-S3) left five residuals: (1)
multi-slot standard-int, (2) signed integers, (3) floats + `s`/`p`, (4) native `@` alignment, (5)
S4 per-field / S5 os re-key. The S0 decision (above) had scoped faithful to single-slot to avoid the
`slot_id` collision (`'>HH'` and `'<ii'` both `struct_pack_i2`) and to leave the heavy os proof base
untouched.

**Options for the collision (the item-1 blocker).**
1. Re-key ALL pack/unpack to a range-aware `slot_id` and re-verify os. HIGH risk (destabilises os),
   large churn.
2. A single guard per existing `slot_id`. Unsound (collision) or useless.
3. Extend the width-tagged single-slot scheme to a PER-FIELD width/signedness tag
   (`faithful_slots()` → tag-join; symbol `struct_{pack,unpack}_f<tag>`), gated by a WHITELIST of
   shapes that carry a cited Rocq+Lean byte-codec proof (`_FAITHFUL_SHAPES`). Whitelisted shapes route
   faithful; everything else (incl. the legacy os `i2`/`i18`/`i1a1`) stays on the opaque/legacy path.

**Choice.** Option 3, with these sub-decisions:
- **Whitelist gate (`_FAITHFUL_SHAPES`).** Faithful ⟺ std prefix + all scalar-int fields + tag-tuple
  IN the whitelist. This is the honest "claim only what we have proven" boundary AND it keeps the os
  shapes untouched by construction. Deliberately EXCLUDES `u16u16` (`'>HH'` = 0420's legacy `i2`) and
  the wide `i18` — so 0420-0425/0665 emit BYTE-IDENTICALLY (zero churn to the os proof base). The
  multi-slot demo therefore uses `u16u32` (`'>HI'`) and signed `i32i32` (`'<ii'`), which no legacy
  test uses.
- **Exact-match fix for sibling axiom keys.** `round_trip_u16` is a textual prefix of
  `round_trip_u16u32` (and `i32` of `i32i32`); the `_AXIOM_FUNCTIONS` `startswith` match would drag the
  single-slot val decls into a multi-slot citation. Added `_axiom_fn_prefix_match`: namespace keys
  (trailing `.`) prefix-match; full-lemma keys match EXACTLY. Correct for every pre-existing entry
  (verified: only my two new sibling pairs were affected).
- **Signed = two's complement, derived from unsigned.** `pk_iN x = pkU_N (x mod 2^8N)`;
  `up_iN d = let u = upU_N d in if u >= 2^(8N-1) then u - 2^8N else u`. Round-trip proven for the whole
  signed range from the unsigned round-trip + a modular argument. i64 needed the 8-digit base-256
  telescoping (`urt64`) — provable with `lia`/`omega`; NO width was intractable.
- **Multi-slot = disjoint-byte concatenation.** `pk_u16u32 x0 x1 = pk16 x0 ++ pk32 x1`; unpack projects
  each field's byte range. Round-trip = f_equal on the two single-field round-trips.
- **`s` fixed-bytes = truncate codec (`firstn N`).** Under the length guard `len d = N`, `firstn N d = d`
  → array identity. Faithful (struct truncates >N, pads <N; the guard pins =N).
- **Float `f`/`d` = DOCUMENTED YAGNI (UB §7.4c), NOT a faked axiom.** The IEEE-754 bit-extraction does
  not lower to the int/real model (no `real → bits` total function in scope). Size law kept; round-trip
  opacity note. This is a modelling gap, not an SMT timeout — so it is honest opacity, per the plan.
- **Native `@` = REJECTED (UB §7.4b), NOT silently opaque.** `expressions.py:_handle_struct_call` raises
  a clear diagnostic for a `'@'` prefix; `calcsize()` returns `None` for `'@'` defensively. Rejection is
  the SOUND choice (native size/padding is platform-dependent; an opaque model could carry a wrongly-
  sized `len(...)` claim). No existing `.py` corpus program uses `'@'` → zero regression. Negative driver
  0782.
- **S4/S5 = SUPERSEDED, definitively.** 0665's zero-trust body codec already gives the os an axiom-free
  round-trip; re-keying os to a struct axiom would RE-INTRODUCE an axiom. Multi-slot per-field content is
  delivered by the tuple round-trip (0777/0778 prove `\result == field_k`); a separate per-field axiom is
  subsumed and, for wide/legacy shapes, dominated by the 0665 body codec.

**Rationale.** Maximises rigor without destabilising os: every faithful shape is byte-honest (size +
per-field-guarded round-trip + guard-necessity, all cross-validated Rocq+Lean, `coqc`/`lean` exit 0, no
Admitted/sorry, axioms ⊆ core set), the collision is closed by the per-field tag, native alignment is
soundly rejected, and float/wide-multi-slot stay honest documented residuals. `proof_axiom_allowlist`
UNCHANGED (all faithful axioms flow through the registry + `--audit-proof`). Drivers 0777-0782;
proofs 0777-0781.proofs/{rocq,lean}/StructResiduals.{v,lean}.

## cleared-string RESIDUALS (items 1-2) — lower/upper determinism+idempotence+literal-fold; replace not-contains identity+literal-fold; NO new axiom

**Context.** After cleared-string landed concat/slice/predicate content natively, two residuals
remained YAGNI-exited: (1) `.lower()`/`.upper()` were a shared NON-deterministic `val str_case_op`
with only a non-emptiness length law (no content, not even `s.lower()==s.lower()`); (2) general
`.replace(a,b)` kept only the char-for-char length law. The residuals-closing pass RE-ATTEMPTED both
with a Gate-B spike leading on the make-or-break CONTENT goals.

**Spike (`test-suite/corpus/conformance/spikes/cleared-string-residuals.mlw`, Why3 1.8.2 / AE 2.6.2 /
Z3 4.13.3).** All content goals Valid on BOTH provers, no E-matching blowup:
| goal | Alt-Ergo | Z3 |
|---|---|---|
| g_lower_idem / g_upper_idem (idempotence via fold-marker) | Valid 0.04s / 12 steps | Valid 0.01s / 4728 steps |
| g_lower_det (determinism) | Valid 0.03s / 6 steps | Valid 0.01s / 479 steps |
| g_replace_absent (not-contains ⇒ identity) | Valid 0.03s / 37 steps | Valid 0.01s / 5731 steps |
| g_replace_len (char-for-char length) | Valid 0.03s / 16 steps | Valid 0.01s / 613 steps |
| g_lower_not_id (`lower s = s` SENTINEL) | Timeout (unprovable ✓) | Timeout (unprovable ✓) |

**Choice.** GO on a NATIVE + DETERMINISTIC model, NO codepoint apparatus, NO new `axiom` keyword:

- **Item 1 (case).** `str_case_op` → two DETERMINISTIC `val function str_lower_op`/`str_upper_op`,
  each: non-emptiness length law + IDEMPOTENCE. Idempotence is encoded WITHOUT an `axiom` keyword and
  WITHOUT self-reference (illegal in Why3), via a fresh uninterpreted "already-folded" marker
  predicate: `ensures { marker result }` (output is folded) + `ensures { marker s -> result = s }`
  (a folded input is a fixed point) ⇒ `f(f s)=f s`. Distinct symbols keep `s.lower()==s.upper()`
  UNKNOWN. A STRING-LITERAL receiver is CONSTANT-FOLDED by Python's own `str.lower`/`upper` → exact
  FULL-Unicode content. Drivers 0791 / 0793 (NEG).
- **Item 2 (replace).** `str_replace_op` → DETERMINISTIC `val function` + a NOT-CONTAINS identity law
  phrased as the negation of the substring-existential the `in`/`not in` operator emits (so
  `requires pat not in s` connects); empty pat auto-excluded (matches CPython). All-literal calls
  constant-fold. Drivers 0792 / 0794 (NEG).

**Rationale / soundness.** (a) Determinism is FAITHFUL (lower/upper/replace ARE deterministic
functions) and does NOT create the collapse hole the prior YAGNI note feared — only a SHARED symbol
or an over-strong axiom would, and distinct `val function`s with distinct marker predicates relate to
nothing. The `lower s = s` sentinel stays Unknown, confirming the model is not over-strong. (b)
Idempotence is a UNIVERSAL sound law (Python folds are idempotent for ALL strings, Unicode incl.), a
strict content gain over the old opaque fresh-`val`. (c) Constant-folding literals via Python's OWN
method is unconditionally sound and Unicode-faithful (`"ß".upper()`→`"SS"`), the honest way to give
real content on the literal case. (d) NO new global axiom: the whole delta is abstract-op `ensures` +
one fresh marker predicate per case op; `proof_axiom_allowlist` UNCHANGED — no `#@ proof` lemma was
needed (the properties are definitional abstract-op ensures, the same trust class as the length laws).

**Residuals (evidence-backed boundaries, kept honest).**
- The per-char ASCII case-MAP on a SYMBOLIC string is NOT modelled: it needs a codepoint bridge
  (`chars : seq int`), an `is_ascii` contract predicate, and `ord`-on-derived-subscript — a large new
  contract surface with ZERO corpus demand, plus a codepoint theory that risks slowing the heavy
  os/self-annotate sweep. Full Unicode folding (`ß→SS`) is inherently not per-char/length-preserving.
- The general grow/shrink `.replace` CONTENT is NOT soundly reachable: Why3's `replaceall` carries no
  content axiom beyond empty-pat/not-contains, and CPython's ALL-occurrences replace ≠ Why3's
  FIRST-occurrence `replace` (whose `replace_substring_indexof` decomposition cannot be borrowed
  without a single-occurrence proof). No length law is claimed for grow/shrink (0794 rejects it).

Mirror: `_handle_string_value_method` is mirror-absent (off the verification path) → mirror-sync green,
`\trusted` non-increasing. Emission differential = the new drivers + `0751` (the only prior lower user).

## nested-list S0 (Gate-B spike) — representation DECISION

**Decision.** `List[List[τ]]` lowers to **`array (seq τ)`**; `List[Dict[str,int]]` to
`array (map string (option int))`; recursively. The OUTER list stays `array` (byte-identical to a flat
`List[τ] = array τ`, and its `length` / `a[i]` / outer row-replacement `a[i]=row` machinery is
unchanged). The INNER collection is a PURE Why3 type (`seq τ` / `map κ (option ν)`).

**Why not `array (array τ)`.** Why3 REJECTS it at typecheck: `Array.get` cannot return a mutable
element — "This application instantiates pure type variable 'a with a mutable type array int". A pure
inner type is MANDATORY, so the inner collection is `seq`/`map`, never `array`.

**Why not `seq (seq τ)` (fully immutable).** Provable (AE 0.03s / Z3 <0.01s) but would flip the OUTER
list to immutable too, perturbing every flat-list emission (length/subscript machinery is array-based).
`array (seq τ)` keeps the outer array intact → flat lists byte-identical.

**Spike evidence** (`test-suite/corpus/conformance/spikes/nested-list.mlw`, Alt-Ergo 2.6.2 / Z3 4.13.3, -t 10):
- `array (array int)` — REJECTED (typecheck, mutable element). NOT VIABLE.
- `seq (seq int)` — all Valid, AE 0.03s / Z3 <0.01s.
- `array (seq int)` — WINNER. read2/innerlen/setrow/subscript-projection all Valid, AE 0.03s / Z3 <0.02s.
- `array (map string (option int))` — Valid, AE 0.03s / Z3 <0.01s (List[Dict[str,int]]).

**Recursion shape.** One `_rec(T)` = the pure element-position WhyML type: `int/bool→int`, `str→string`,
`float→real`, `List[U]→seq (_rec U)`, `Dict[K,V]→map κ(K) (option (_rec V))`, `Set[U]→map (_rec U) (option int)`.
A top-level `List[T]` param = `array (_rec T)`. Flat `List[int]`: `_rec(int)=int → array int` (byte-identical).
This subsumes the existing `_m5_get_dict_value_type` (which already returns `seq int` for `Dict[str,List[T]]`).

**Boundary (YAGNI read-only for inner).** In-place inner mutation `a[i][j]=v` / `a[i].append(..)` is NOT
expressible on `seq` (immutable) → documented residual: reject or keep opaque, never an unsound update.
Outer whole-row replacement `a[i]=newrow` IS sound and stays expressible. No new axiom (nested read/index
laws are Why3 stdlib `seq.Seq` / `map.Map`).

## nested-list-mutable (Gate-B spike) — in-place inner mutation `a[i][j]=v` via `matrix int`

**Decision.** A `List[List[int]]` param that is IN-PLACE INNER-MUTATED (`a[i][j] = v` in the body)
routes to the MUTABLE built-in Why3 **`matrix int`** model. A read-only nested list stays on the landed
`array (seq τ)` read model. This is a **usage/mutation analysis** (option (a) — coexistence): the two
representations coexist, selected per-param by whether the body inner-mutates it.

**Why not unify all rectangular-int nested lists onto `matrix` (option (b)).** The landed read drivers
0797/0798 use RAGGED inputs (`[[1,2],[3,4,5]]`) and prove per-row `len(a[i])` — a `matrix` has a single
uniform `columns`, so it cannot express ragged per-row length. Unifying would BREAK 0797/0798. The
mutation analysis keeps read-only nested lists ragged-capable on `array (seq τ)` (0797-0800 byte-identical)
and only inner-mutated int-leaf params on `matrix int`.

**Why `matrix int` (over flattened `array int` + offsets).** Both are tractable (spike below), but `matrix`
is the BUILT-IN Why3 mutable 2-D structure — `Matrix.get`/`Matrix.set`/`rows`/`columns` with a proven
frame — needing zero custom machinery. Flattening needs an offset array + injective-layout reasoning for
non-aliasing. `matrix` is rectangular int; the natural target.

**Coexistence lowering.** Inner-mutated int-leaf param → dropped from `param_list_nested_elem`, kept in
`array2d_params` (Module5 `_collect_inner_mutated_params`). Module6: `a[i][j]=v`→`Matrix.set a i j v`,
`a[i][j]`→`Matrix.get a i j` (both pre-existing array2d paths), `len(a)`→`a.rows`, `len(a[i])`→`a.columns`
(new, `_handle_len_call`). The `matrix` model is RECTANGULAR (uniform `columns`) — the rectangular
assumption is structural (same stance as the existing `\length2d` matrix path 0018/0019).

**Spike evidence** (`test-suite/corpus/conformance/spikes/nested-list-mutable.mlw`, Alt-Ergo 2.6.2 / Z3 4.13.3, -t 10):
- `matrix int` — the emitted imperative `let` VCs (`m_read`, `m_update_readback`, `m_update_noalias`,
  `m_dims_preserved`, `m_innerlen`) all Valid in BOTH Alt-Ergo (≤0.05s) AND Z3 (≤0.01s). Read-back
  `(set a i j v; get a i j)=v` and non-aliasing `(i2,j2)≠(i,j) → get unchanged` both Valid.
  (The pure ghost-`update` goal forms time out in Z3 on map-update E-matching but Alt-Ergo proves them;
  they are NOT what is emitted — emission uses imperative `set`/`get`, which BOTH provers discharge fast.
  Per [[smt_timeout_not_unprovable]], an SMT timeout on a non-emitted goal is not a boundary.)
- flattened `array int` + offset — also all Valid (AE ≤0.05s / Z3 ≤0.02s) but needs custom offset
  machinery; NOT chosen.
- `array (array int)` — already Why3 TYPE-REJECTED (mutable element inside `array`); not re-pursued.

**Boundary (honest residual).** In-place inner mutation is int-leaf + rectangular ONLY. A NON-int leaf
(`List[List[str]]` = `array (seq string)`) inner mutation is REJECTED (hard type failure — immutable `seq`;
driver 0804). `a[i].append(...)` (shape-change) stays OPAQUE (`append_1` no-op — makes no false post-state
claim). Ragged in-place mutation is out of the rectangular `matrix` model (UB-catalog: rectangular
assumption). No new axiom (Matrix get/set/frame laws are Why3 stdlib `matrix.Matrix`).

## nested-list §8/§9 EXTENSION (Gate-B spike) — deeper nesting a[i][j][k] + target-dependent comp index

**Decision.** Both residuals LIFT — no cap below the existing type-recursion bound (`_M5_MAX_NEST_DEPTH=4`).
(1) A DEEPER nested read `a[i][j][k]` (List[List[List[τ]]] ~ `array (seq (seq τ))`, up to depth 4)
composes `Seq.get` on the pure inner seqs; the subscript-lowering (S3) is generalized from the fixed
2-level unfold to a recursive one driven by the element-type string (peel one container per index level).
(2) A TARGET-DEPENDENT comprehension index `[x[f(x)] for x in a]` where the index lifts to a pure int
logic term over the loop target `x` (a `seq τ`) — specifically `len(x)` + integer literals + captured
int params under `+ - *` (e.g. `x[len(x)-1]`) — proves via the content law
`result[i] = Seq.get (src[i]) (Seq.length (src[i]) - 1)`. An index that does NOT lift to this grammar
(a call `g(x)` over the seq, a non-`len` seq operation) stays OPAQUE (documented residual).

**Spike evidence** (`test-suite/corpus/conformance/spikes/nested-list-deep.mlw`, Alt-Ergo 2.6.2 / Z3 4.13.3, -t 10):
- DeepRead: `test_read3` / `test_use3` (depth-3 read consumed at a use-site) / `test_innerlen3`
  (`len(a[i][j])` = `Seq.length (Seq.get (a[i]) j)`) / `test_read4` (depth-4) — ALL Valid,
  AE ≤0.03s (≤5 steps) / Z3 ≤0.01s. NO E-matching blowup as nesting deepens (the real risk — cleared).
- TargetDependentComp: `test_target_idx` (law `result[i] = Seq.get (src[i]) (Seq.length (src[i]) - 1)`
  consumed at TWO indices) / `test_target_offset` (captured-offset `len(x)-c`) — Valid, AE ≤0.04s
  (≤29 steps) / Z3 ≤0.02s. The quantified `Seq.length` under `Seq.get` did NOT blow up.

**Why no cap below 4.** Depth 4 (the type-recursion ceiling) is already fast in both provers; deeper
than 4 the type recursion returns None → the param is not nested-elem → the read stays the opaque
`subscript_get` fallback (unchanged). So the cap is inherited from the type bound, not a new SMT limit.

**Boundary (honest residual).** (a) A read deeper than depth 4 stays opaque (`subscript_get`) — the
type-recursion bound. (b) A target-dependent comprehension index that is NOT a `len(x)`-arithmetic term
(a `g(x)` call over the seq, or any non-`len` seq op) stays OPAQUE (length-only comprehension) — never a
false content claim. (c) A target-dependent index over a MAP source (`List[Dict[..]]`) stays opaque
(only seq sources get the target-dependent int index). No new axiom (Seq read/length laws are Why3 stdlib).

## WL-01 — Python `//`/`%` floored division/modulo (SOUNDNESS FIX)

**Decision.** Lower Python floor-division `//` and modulo `%` to Python-faithful **floored**
semantics, not Why3's Euclidean `div`/`mod`. Python `//` rounds toward −∞ and `%` takes the sign of
the **divisor**; Euclidean uses a non-negative remainder. The two AGREE when the divisor is positive
and DIVERGE when it is negative — and PyCSL was PROVING FALSE arithmetic there: `(-7)//(-2)` proved
`==4` (CPython `3`), `7%(-2)` proved `==1` (CPython `-1`).

**Mechanism (no new axiom).** `pycsl_div`/`pycsl_mod` (body helpers, `src/pycsl/module6_whyml/preamble.py`)
and the contract-side lowering (`src/pycsl/module6_whyml/expressions.py`, `op in {div,mod}` spec branch)
correct Euclidean `div`/`mod` by a sign-of-divisor adjustment over the always-in-scope
`int.EuclideanDivision`:
`floordiv x y = if mod x y <> 0 && y < 0 then div x y - 1 else div x y`;
`floormod x y = if mod x y <> 0 && y < 0 then mod x y + y else mod x y`.
The `ensures` is definitional (`result = <floored term>`), discharged trivially. The spec side inlines
the same correction with the operands `let`-bound once (no dependency on the divmod helper block being
emitted, so contract-only usage stays sound).

**Why not a stdlib primitive.** Why3 ships `int.EuclideanDivision` (non-negative remainder) and
`int.ComputerDivision` (truncated, remainder sign = dividend). Neither IS Python floored. The
sign-of-divisor correction over the already-`use`d Euclidean theory is the minimal, name-clash-free
derivation (adding `ComputerDivision` would clash `div`/`mod` unqualified).

**SMT feasibility (spike).** `test-suite/corpus/conformance/spikes/wl01_floored_divmod_spike.mlw`:
all concrete goals (`(-7)//(-2)=3`, `7%(-2)=-1`, `(-7)//2=-4`, `7//2=3`, the `<> 4`/`<> 1` guards, and
the sign/bound law for `%`) are **Valid on both Alt-Ergo 2.6.2 and Z3 4.13.3**. The general nonlinear
identity `x = (x//y)*y + (x%y)` is Valid on Alt-Ergo (0.04s) and times out only on Z3 (documented
nonlinear-multiplication instability) — irrelevant, since the drivers are concrete. No cited Rocq/Lean
lemma needed.

**Positive-divisor byte-identity.** For `y > 0` the correction condition `y < 0` is false, so the
emitted body reduces to the old `div x y`/`mod x y`. The emission differs only for programs that use
`//`/`%` (33 reference files: the helper block + contract-side term); positive-divisor arithmetic
proves exactly as before.

**Regression locks.** `test-suite/corpus/pycsl-reference/0811.py` (POSITIVE: faithful floored values
incl. symbolic-divisor `\result == a//b`), `0812.py` (NEGATIVE `# pycsl-expected: FAIL`: the old false
`==4`). Repro drivers `getting-better/wrong-lowering/wl01_*`. Translational-reference §T.11 G1 marked
RESOLVED (its `(-7)//2` example was itself wrong — Euclidean agrees for a negative *dividend*; the
divergence is a negative *divisor*).

**Note for WL-02 (true `/`).** Untouched by WL-01: `/` shared the `pycsl_div` mechanism (int operands →
floored int div). The real fix — `/` returns a `real` — is now landed as a separate concern (see the
WL-02 decision below); this WL-01 change kept the mechanism clean for it.

---

## WL-02 — Python `/` (TRUE division) lowers to REAL, not integer `div` (SOUNDNESS)

**Date:** 2026-07-05. **Branch:** `ghost-assign-bc6`.

**Decision.** Python `/` is TRUE division and ALWAYS returns a `float` (`5 / 2 == 2.5`, even for int
operands). PyCSL previously lowered a body/contract `/` to the integer Euclidean `pycsl_div`, dropping
the fractional part and UNSOUNDLY proving the false `5 / 2 == 2`. `/` now lowers — in a body **and** in
a contract — to a **real** division: both int operands are lifted to `real` via `real.FromInt`
(`from_int`) and divided over the reals with `real.RealInfix` (`/.`). Contract: `from_int a /. from_int
b`. Body: one abstract `val float_truediv_op (a b: int) : real ensures { result = from_int a /. from_int
b }` (`from_int` is a logic symbol, unusable in a program term). FLOOR division `//` (IR op `"div"`) is
UNCHANGED — it stays integer floored (WL-01 intact). Only `/` (IR op `"/"`) is affected.

**Fail-close, not truncate.** Because a `/` result is a `real`, using it at `int` type (`-> int`,
`#@ ensures \result == 2`) is a real-vs-int **type error** (fail-closed) — never a silent integer
truncation. This is the documented int/float-mixing boundary. To assert an integer quotient, use `//`.

**No smuggled axiom.** Real division is SMT-direct on Alt-Ergo AND Z3 — no cited lemma, `proof_axiom_
allowlist` unchanged. Spike: `test-suite/corpus/conformance/spikes/wl02_truediv_real_spike.mlw`.

**Import gating (byte-identity).** `use real.RealInfix`/`use real.FromInt` are emitted only when
`IRScanner.uses_true_division` finds a BinOp op `"/"`. A program with no `/` is byte-identical. Corpus
byte-diff: only the 13 programs that used a contract `/` to mean integer division changed.

**Corpus reclassification.** 13 reference programs used `/` in a CONTRACT to mean integer division
while the body used `//` (e.g. `0353` `\result == 256 / n`, body `256 // n`; `0004`/`0203`/`0209`
Gauss-sum `n*(n±1)/2`). They RELIED on the old unsound `/`→int. Reclassified by spelling the contract
with `//` (the sound integer division matching the body): all 13 still PROVE; emission byte-identical
(10) or differs only by dropping a dead unused `pycsl_div` helper (3, contract-only division).

**Regression locks.** `0813.py` (POSITIVE: `5/2==2.5`, `1/2==0.5`, `7/2==3.5`, exact `4/2==2.0` at
`float`, plus a `5//2==2` integer guard), `0814.py` (NEGATIVE `# pycsl-expected: FAIL`: the old
int-truncation `5/2==2`). Repro drivers `getting-better/wrong-lowering/wl02_truediv_{UNSOUND,TRUE}.py`.
Concrete-syntax §3.2.8 and translational-reference "True Division (`/`)" corrected (they previously
documented `/`→Euclidean `div` for contracts — that was the bug).

---

## wrong-lowering WL-03 — realize a recognized `Tuple[T1,…,Tn]` param/field as a synthesized per-slot NamedTuple record (reuse, not a new tuple type)

**Context.** A `Tuple[...]`-annotated PARAMETER (and record FIELD) collapsed to bare `int` with an
opaque `subscript_get (x:int)(i:int):int`: a `Tuple[int,str]` param `t[1]` read an int at a `string`
use site (TYPEERR), and an all-int `Tuple[int,int]` param's `t[0]` was content-opaque. The faithful
per-slot model existed ONLY for locally-constructed / returned tuples (the LOCAL baseline is actually
literal-folded — `t[1]`→`20` — not a real record). The τ-table row `τ(Tuple[T1,…]) = tuple` was
UNQUALIFIED but the param/field realization silently diverged to `int`.

**Options.** (1) A native WhyML anonymous tuple type `(int, string)` for the param — REJECTED: Why3 has
no field/`.1` projection on anonymous tuples, so a subscript-expression `t[i]` cannot be lowered
cleanly (needs a `match ... with (a,b) ->` destructure, awkward in a contract term). (2) A brand-new
bespoke tuple record family with its own subscript lowering — REJECTED: duplicates the NamedTuple
positional-access machinery that already lowers `p[i]` to a record-field-by-index read. (3) **CHOSEN:**
synthesize ONE dedup'd per-slot record `type pytuple_<tags> = { field0: τ(T1); … }` marked
`is_namedtuple: True`, and resolve a recognized `Tuple[…]` param/field annotation to it — reusing
`_param_type_str` (record param), `_namedtuple_positional_access` (`t[i]`→`t.field{i}`), and the
record-field emitter verbatim.

**Choice.** Option 3. Module5 `_synthesize_tuple_records(node)` walks the module for recognized
fixed-length `Tuple[T1,…,Tn]` annotations (int/bool→int, str→string slots; NO Ellipsis) and appends a
dedup'd namedtuple record type_decl BEFORE functions/classes are visited; `_m5_get_type_name` (param)
and `_field_type_from_annotation_inst` (field) return the synthesized record name for a recognized
Tuple. A record-PARAM field read (`b.p[1]`) is enabled by teaching `_field_type_of` to consult
`_record_param_classes`; the preamble record emitter emits a nested-record field type.

**Rationale.** Maximal reuse of the already-proven NamedTuple seam; **byte-identical** across the whole
695-file corpus (no corpus program uses a recognized `Tuple[…]` param/field → fully additive); the fix
is exactly the recognized-`Tuple[T1,…]` param/field surface. Bare `tuple` and variable-length
`Tuple[T, …]` (Ellipsis) stay the τ-blessed `int †` collapse. **Scope limit:** a float/container/class
slot is NOT recognized (record-field `float` is not modeled as `real`) → those fall back to the current
collapse rather than emit an unfaithful `real`→int field; that is a fail-safe (documented in the
τ-table `record` row and `wrong-lowering-to-fix.md` §WL-03).

**No smuggled axiom.** The per-slot record read is SMT-direct on Alt-Ergo AND Z3 — no cited lemma,
`proof_axiom_allowlist` unchanged. Spike:
`test-suite/corpus/conformance/spikes/wl03_tuple_param_slot_spike.mlw` (all goals Valid on both provers).

**Regression locks.** `0815.py` (POSITIVE: mixed `Tuple[int,str]` `t[1]==<str>` / `t[0]==<int>` and
homogeneous `Tuple[int,int]` `t[0]`/`t[1]` param slot reads), `0816.py` (NEGATIVE `# pycsl-expected:
FAIL`: a false slot-content conflation `\result==t[1]` while returning `t[0]`). Repro drivers
`getting-better/wrong-lowering/wl03_tuple_{param_COLLAPSED,local_FAITHFUL}.py` (param → PROVEN, local
baseline stays PROVEN). τ-table (`τ(Tuple[T1,…,Tn]) = record`) and `wrong-lowering-to-fix.md` §WL-03
(→ FIXED) updated.

## wrong-lowering WL-04 — realize a FLAT `List[str]`/`List[float]` param element as `array string`/`array real` (one-level-up analog of the nested `array (seq τ)` model)

**Context.** WL-04 (COLLAPSED-with-consumer, severity 3): a FLAT `List[str]`/`List[float]` PARAMETER
collapsed its element to `int` (`let f (a: array int) … : string = a[i]` — `a[i] : int` vs a `string`
return), so a legitimate faithful-typed function was REJECTED as ill-typed WhyML (TYPEERR), not
verified nor cleanly diagnosed. The nested campaign (0797–0810) already proved the faithful element
model (`List[List[τ]] ~ array (seq τ)`); WL-04 is the flat leaf case it skipped.

**Choice.** Realize a flat `List[τ]` PARAMETER's element as the faithful `τ` when `τ ∈ {str→string,
float→real}`. Module5 `_m5_get_list_flat_elem_whyml(annotation)` maps `List[str]`→`"string"` /
`List[float]`→`"real"` (and returns None for `List[int]`/`List[bool]` and any nested
`List[<container>]`, whose slice is a Subscript), captured at the param site into a NEW IR field
`param_list_flat_elem`. Module6 `_reset_function_state` loads it as `self._param_list_flat_elem`, and
`_param_type_str` consumes it (emitting `array {τ}`) in the flat-list arm, RIGHT AFTER the nested
`_list_nested_elem` branch. The subscript READ path is UNCHANGED — the `is_array` branch's `Array.get`
is element-polymorphic, so `a[i] : string`/`: real` matches the str/float use site.

**Rationale.** Maximal reuse of the nested-list threading pattern (a dedicated per-param map + one
`_param_type_str` branch); a NEW dedicated map (not the pre-existing `param_list_elem_types`, whose
"string"/"emit_ir" tags carry @mutable_state semantics) keeps the @mutable_state builder and the
field paths BYTE-IDENTICAL. **Byte-identical** across the whole 697-file corpus (verified via
`bin/byte-diff-sweep.sh`): no corpus program has a flat `List[str]`/`List[float]` PARAM (0746 is a
`Dict[str, List[str]]` FIELD; 0804 is a nested `List[List[str]]` param → the nested path) → fully
additive. `List[int]`/bare-`list` stay `array int`; the nested-list work (0797–0810) and WL-03
tuples (0815/0816) are untouched.

**Scope limit / fail-safe.** A `List[str]`/`List[float]` LOCAL or `-> List[str]` RETURN built by a
LIST LITERAL (`a = ["x","y"]`) still collapses its string/float ELEMENTS through the pre-existing
list-literal construction (a DISTINCT surface, not the parameter-element collapse of §WL-04); the
param-only change does not touch it. `List[<record>]` flat element is a documented follow-on (would
need the WL-03 record-synthesis seam threaded to the flat list param). Both noted in
`wrong-lowering-to-fix.md` §WL-04 and the τ-table row.

**No smuggled axiom.** The `array string`/`array real` element read is SMT-direct on Alt-Ergo AND Z3
— a native `array` read, no cited lemma, `proof_axiom_allowlist` unchanged. Spike:
`test-suite/corpus/conformance/spikes/wl04_list_flat_elem_spike.mlw` (all goals Valid on both provers).

**Regression locks.** `0817.py` (POSITIVE: `List[str]` element reads, `\result == a[i]` at `string`),
`0818.py` (POSITIVE: `List[float]` element reads, fractional value preserved at `real`), `0819.py`
(NEGATIVE `# pycsl-expected: FAIL`: a false element-content conflation `\result == a[1]` while
returning `a[0]`). Repro drivers `getting-better/wrong-lowering/wl04_list_{str,float}_elem_COLLAPSED.py`
(both → PROVEN, was TYPEERR). τ-table rows (`τ(List[str]) = array string`, `τ(List[float]) = array
real`) and `wrong-lowering-to-fix.md` §WL-04 (→ FIXED) updated.
