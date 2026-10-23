# Independent review of cursor-nest.md

Reviewer: independent (did not see the sub-loop's reasoning). Every judgment below is grounded
in an oracle run I performed myself on branch `ghost-assign-bc6`; commands and verbatim output
excerpts are included. Scratch artifacts live in
`/tmp/claude-1000/-home-fabrice-git-pycsl/8f7f6044-5a3d-4979-a728-07c3eb57e115/scratchpad/review/`.

## VERDICT: PROCEED-AMENDED

The strategic recommendation — convert the whole nest, with the lexicographic measure encoded
and the monotone-cursor interface proved rather than assumed — is sound and my oracles support
it. But two named factual claims are wrong as stated, and the capability list is incomplete in
one way that would stop the conversion dead at L3-tc. Amendments required before execution:

1. **Add the mutual-recursion continuation-keyword fix to the capability list.** The emitter's
   program-mode SCC continuation emits `and`, which is a Why3 SYNTAX ERROR; WhyML requires
   `with`. (`src/pycsl/module6_whyml/functions.py:5146`, `kw = f"and {name}"`; the logic-mode
   path at :5142 correctly uses `with function`.) Without this one-token fix the 11-method nest
   can never emit type-checking WhyML, whatever else is built.
2. **Soften §5 from "exactly two honest options" to "all-or-nothing for the variant-bearing
   members".** I proved a piecewise counter-construction (below).
3. **§5's "FIXED, same window" frame claim is not landed in the tree I tested.** My emission
   oracle shows trusted vals still carry no `writes` clause despite the mirror's
   `#@ assigns self.pos`.

---

## Claim-by-claim results

### §3(a) "`type term` with all 9 constructors is ALREADY EMITTED, immutable, in parser.mlw" — CONFIRMED

Oracle:

    timeout 300 python3 src/pycsl/pycsl.py src/self-annotate/src/proof2why3/parser.py \
        --import-path src/pycsl --no-proof --keep-mlw
    -> [+] Verification SUCCESS (--no-proof: WhyML generated AND type-checks [L3-tc ✓]; proof skipped)

The generated `parser.mlw` (copied to scratch, original deleted) has at line 19:

    type term =
      | App string (list term)
      | BinOp string term term
      | BoolLit bool
      | Exists (list string) string term
      | Forall (list string) string term
      | IntLit int
      | UnaryOp string term
      | Unsupported string string
      | Var string

All 9 constructors, immutable, exactly as claimed. Also confirmed from the same artifact: the
`Term = 0` stub (mirror `ir.py:121`) makes every trusted parse val return `int`
(`val _parser__parse_expr (self: _parser) : int`), confirming §6 item 1.

### §3(b) "recursive-method emission and MUTUAL recursion already work" — first half CONFIRMED, mutual half REFUTED

This was the claim I most wanted to falsify, and the run falsifies it. I wrote a minimal
faithful probe (`mutrec_nest.py`: a `@mutable_state` class with `toks: List[Token]`, `pos`,
class invariant `0 <= self.pos`, and two mutually recursive int-returning methods `a`/`b` with
the integer-encoded lexicographic variants `2*(\length(self.toks)-self.pos)` and `... + 1`):

    timeout 300 python3 src/pycsl/pycsl.py mutrec_nest.py --no-proof --keep-mlw
    -> [level] L1 ✓  L2 ✓  L3-tc ✗
       [!] Emitted WhyML does NOT type-check (L3-tc failed) — NOT a success:
       File ".../mutrec_nest.mlw", line 32, characters 2-3: syntax error

The emitted file shows the SCC machinery working structurally — the calls resolve concretely
and the group is chained:

    let rec p__b (self: p) : int
      ... variant { ((2 * ((Array.length self.toks) - self.pos)) + 1) }
    = (p__a self)
    and p__a (self: p) : int          <- Why3 rejects `and`; WhyML requires `with`
      ...
      raise (Return (p__b self))

Hand-replacing `and` with `with` (`mutrec_nest_with.mlw`) and proving:

    why3 prove -a split_vc -P "Alt-Ergo,2.6.3," -t 8 mutrec_nest_with.mlw
    -> total: 10  valid: 10   (including both Variant decrease goals)

So: the design is right, the resolution and SCC grouping are right, the encoded-integer
lexicographic variant proves through the emitter's own output — but **mutual recursion does NOT
"already work"**: no run can ever have produced valid WhyML through the `and` path. The report
itself flags this claim as "sourced from reading emitter code, NOT from a run"; the reading was
accurate about the code, and the code is broken. A module-level two-function probe
(`mutrec_funcs.py`) fails identically, so this is not method-specific. One-token fix at
`functions.py:5146`.

Two supporting observations from the same probes, for the implementer:

- Concrete resolution of `self.<m>()` to `(<class>__<m> self)` is **gated on
  `_record_array_fields`** (expressions.py ~:5219). A probe class with `toks: List[int]` (not a
  record-element array) got opaque `val self_odd_0 (self: c) : int writes {self.pos}` stubs and
  a vacuous `let rec` (variant never checked), plus `len(self.toks)` degenerating to the
  ill-typed `iter_length self.toks` (L3-tc ✗). The real `_Parser` (`toks: List[Token]`) is on
  the good side of the gate, but the gate's existence is worth knowing when spiking.
- Single (direct) recursion with resolved calls and a checked variant does work in the faithful
  shape — §3(b)'s first half stands.

### §4 spike "41/41 Valid, 0 non-Valid" — CONFIRMED

    export PATH=$HOME/.opam/framac-coq8/bin:$PATH && \
    why3 prove -a split_vc -P "Alt-Ergo,2.6.3," -t 8 getting-better/cursor-nest/cursor-nest-spike.mlw
    -> 41 "Prover result" lines, 41 ": Valid", 0 Timeout/Unknown/Failure, wall time 2.6 s

Exactly as reported.

### §5 all-or-nothing — core mechanism CONFIRMED by oracle; universal "exactly two options" REFUTED by counter-construction; "FIXED" claim NOT LANDED

I wrote `piecewise_counter.mlw` (two modules, both against trusted vals carrying the HONEST
frame `writes { self.pos }` and `ensures { true }` — no assumption growth):

- **BlockedCase** (confirms the report's mechanism): a converted `parse_implication` — trusted
  `parse_disjunction_stub` call, `take` of `->`, then direct self-call, with
  `variant { Array.length self.toks - self.pos }`:

      Sub-goal Variant decrease of goal parse_implication'vc.
      Unknown (unknown) (0.03s, 68 steps)      <- all other goals Valid

  The report's central example is right: an honestly-framed trusted callee makes the direct
  self-caller's variant undischargeable without growing the stub's contract.

- **PiecewiseCounter** (refutes the universal claim): a converted `parse_expr` — peek, branch,
  delegate to trusted `parse_quant_stub` / `parse_implication_stub` — has **no Why3-visible
  recursion once the trusted vals break the cycle**, hence no variant obligation at all:

      all 5 goals Valid (Array creation size, Type invariant, Index in array bounds, 2x Postcondition)

  Its termination is conditional on the vals' termination — exactly the assumption `\trusted`
  already carries, so nothing is added to the TCB. This is a sound piecewise conversion of one
  nest member.

  Reading the live bodies (`src/pycsl/proof2why3/parser.py:274-456`): the same argument covers
  **`parse_quant`** (its two loops consume a token per iteration via `take` BEFORE any nest
  call, so their variants prove locally; its single `parse_expr` call is not a Why3 recursion
  edge while `parse_expr` is trusted) and **`parse_comparison`** (straight-line, no loop, no
  self-call). The genuinely all-or-nothing members are the direct self-callers
  (`parse_implication`, `parse_atom`) and every member whose loop body contains a nest call
  (`parse_disjunction`, `parse_conjunction`, `parse_arith_add`, `parse_arith_mul`,
  `parse_atom_application`, `parse_atom`'s tuple loop). So §5 should read: ~3 of 11 convert
  piecewise; the other 8 land together or not at all. The practical recommendation
  (whole-nest) is unaffected — the piecewise route strands you at the same final step.

- **"the driver separately established (and FIXED, same window)"**: my §3(a) emission — run
  against the live emitter at review time — shows the trusted parse vals with NO `writes`
  clause at all (`val _parser__parse_disjunction (self: _parser) : int  requires {true}
  ensures {true}`), despite the mirror declaring `#@ assigns self.pos` on every one
  (parser.py:92-162). Code inspection agrees: `functions.py:5241` gates the writes emission on
  `not emit_as_val`, and the val path returns at :5270 before any writes clause. The
  driver-progress log says the fix was designed and gated in DETACHED WORKTREES, not the main
  tree. So the defect is real (their `trusted-frame-oracle.mlw` reproduces it decisively — I
  re-ran it: 17/18 Valid with exactly `iface_as_declared` Unknown, as designed), the fix is
  real somewhere, but "FIXED" is not true of the tree the report's other emissions were made
  from. Until it lands, note the flip side: TODAY a partial conversion's variant WOULD prove —
  vacuously, from the false no-write assumption. The all-or-nothing constraint only binds once
  the frame fix lands, which is one more reason to land it first.

### §6 capability list — INCOMPLETE

(The list has since been narrowed to 4 items by the driver's own probes — driver-progress.log
closed items 4, 5, 6, and most of 7 — my probes independently corroborate two of those
closures: the integer-encoded variant emits and proves, and `\old` appears in landed loop
invariants.) Against the live bodies (parser.py:274-456), the surviving 4-item list is missing:

1. **The `and` -> `with` SCC continuation fix** (see §3(b)) — a hard blocker, not on any list.
2. **`" ".join(ty_parts)`** (parse_quant:308): string-join over a list-of-strings accumulator,
   whose result fills the `ty: string` field of `Forall`/`Exists`. Neither the join nor a
   faithful list-of-strings accumulator is named.
3. **Membership in module-level string-set constants**: `t.value not in _LOGICAL_DISJ_OPS`,
   `in _COMPARISON_OPS`, `in _ARITH_ADD_OPS`, `in _ARITH_MUL_OPS`,
   `atom.name in _KNOWN_FN_HEADS`, `t.value in ("forall", "exists")`. Whether these lower
   faithfully (vs. value-blind int-hash membership) is unmeasured and unnamed.
4. **Keyword-argument constructor application**: the live code builds
   `Forall(binders=tuple(binders), ty=ty, body=body)` and `App(head=..., args=...)` — the
   planned `_call_term_constructor` must handle kwargs and field reordering, not just the
   positional `BinOp(op, l, r)` shown in the report.
5. **Strict-progress interfaces**: `parse_atom_application`'s gather loop calls
   `self.parse_atom()` with NO intervening `take` — its loop variant needs parse_atom's
   postcondition to be STRICT (`self.pos > \old(self.pos)`), not the monotone `>=` the spike
   validated. True of the live body (every parse_atom branch consumes >= 1 token), but it is a
   spec-authoring requirement nobody has written down.

Also confirmed from my §3(a) artifact: §6 item 3's degeneracy is real as described (the Token
record emits as `{ kind: int; value: int }` — string fields int-hashed).

### §7 honesty — mostly honest, three overstatements

The report is unusually candid (it names its own unmeasured items and flags §3(b)'s
code-reading provenance). Remaining overstatements, all identified above: (i) "MUTUAL recursion
already works" — refuted by run; (ii) §5's "exactly two options" — refuted by
counter-construction for 3 of 11 members; (iii) §5's "FIXED, same window" — designed and
worktree-gated, not landed in the tree its own emission evidence comes from. Additionally §4's
"lexicographic variant is mandatory" was already self-corrected by the driver's later probes
(integer encoding suffices; the loop-variant half dissolved) — consistent with my probe, where
the encoded form proved through the emitter's own output. The §1 count read 639 at writing; I
measured 638 mid-review with a conversion agent active — a moving count, not an inconsistency.

## Oracle inventory (all runs in this review)

| # | Oracle | Result |
|---|--------|--------|
| 1 | `why3 prove -a split_vc -P "Alt-Ergo,2.6.3," -t 8 cursor-nest-spike.mlw` | 41/41 Valid, 0 non-Valid, 2.6 s |
| 2 | Emit mirror `proof2why3/parser.py` (`--no-proof --keep-mlw`) | L3-tc ✓; `type term` 9 ctors at line 19; trusted vals return `int` and carry NO `writes` |
| 3 | `mutrec_funcs.py` (module-level mutual recursion) emit | L3-tc ✗ syntax error on `and`; hand-fix to `with` -> 8/8 Valid |
| 4 | `mutrec_nest.py` (faithful @mutable_state Token-cursor nest) emit | L3-tc ✗ syntax error on `and`; calls resolved concretely; hand-fix -> 10/10 Valid incl. both variants |
| 5 | `mutrec_probe.py` / `selfrec_method.py` (List[int] variants) emit | opaque `self_*_0` vals + `iter_length` type error — the `_record_array_fields` gate |
| 6 | `piecewise_counter.mlw` | PiecewiseCounter all Valid (piecewise conversion sound for parse_expr); BlockedCase Variant decrease Unknown (report's §5 mechanism confirmed) |
| 7 | `trusted-frame-oracle.mlw` re-run | 17/18 Valid, exactly `iface_as_declared` Postcondition Unknown — the frame defect reproduces |
| 8 | `methodcall_probe.py` (concrete sibling call, List[int]) | L3-tc ✓ but call lowered to opaque `self_step_0` — gate corroboration |

## Recommended amendments to the impl plan

1. Fix `functions.py:5146` `and` -> `with` FIRST and gate it with a corpus byte-diff (the `and`
   path can never have fired on a passing program, so expect byte-diff 0) plus a new
   two-method mutual-recursion reference test — the corpus evidently has none, or this would
   have been caught.
2. Land the frame fix (writes on trusted vals) before any nest member converts, so no interim
   conversion proves vacuously.
3. Extend the capability list with items 2-5 under §6 above; give `parse_atom` a strict
   (`>`) progress postcondition and the other members the monotone (`>=`) one.
4. Optional sequencing relief: `parse_expr`, `parse_quant`, `parse_comparison` can land
   individually ahead of the main group (PiecewiseCounter pattern) if the remaining 8-member
   landing needs de-risking.
