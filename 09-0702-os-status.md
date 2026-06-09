# 09-0702-os-status.md — os verification status + the remaining proof + the multi-session grind

**Date:** 2026-06-09
**Scope:** A synthesis of where the `pure_lib/os/` (`UnixInodeFileSystem`) verification stands, exactly
what proof would remain to make it *fully* SMT-proven (axiom-free), and a concrete plan for the dedicated
multi-session grind — including the larger time budget — that case (2) of
[axiom-registry](docs/glossary/axiom-registry.md) calls for.

---

## 1. Current status (committed, stable)

| Dimension | State |
|---|---|
| Functions | **51** (syscalls + helpers), all in one module |
| Verified bodies | **all 51** — **0 `\trusted`, 0 `\abstract`** (no unchecked bodies in the TCB) |
| Proven goals | **~98%** (per the stdlib-coverage skill); **23 goals remain unproven** |
| Modular boundaries | **2 `#@ no_inline`** (`sys_write`, `sys_open` — verified once, callers reuse the contract) |
| TCB additions | **3 cross-validated axiom families** (Rocq **and** Lean, `audit_proof.py`-checked): |
| | • `UnixFs.Bitmap.bit_and_one_in_zero_one` ×1 — the bitwise-bound on the block/inode bitmap |
| | • `UnixFs.Struct.i18.round_trip` ×2 — the **18-field inode** codec round-trip (`_pack/_unpack_inode`, on `_read_inode`/`_write_inode`) |
| | • `UnixFs.Struct.i1a1.round_trip` ×6 — the **directory-entry** codec round-trip (`_pack/_unpack_direntry`) |

**Reading of this:** the os is a strong soundness position — *every function body is SMT-verified*; the
only trust beyond the SMT backend is the **9 axiom citations** drawn from **3 cross-validated families**.
The codec round-trip is **established** (proven in Rocq+Lean), just **cited** rather than re-proven inline
(the 2026-06-09 decision; axiom-registry §"When to axiomatize", case 2).

## 2. The remaining proof — two distinct buckets (do not conflate)

### Bucket A — the 23 unproven goals (reduce the *count*)
These are **body-VC goals on the disk-mutating syscalls** (`mkdir`/`makedirs`/`unlink`/`access` and
kin) — the residue of the 47→23 reduction (`os-bodyvc-spec.md`, memory *os coverage progress*). They are
**structural/return-code and memory-safety obligations over the 131072-byte disk + the 32-inode region**,
NOT the codec round-trip. They failed the `#@ no_inline` soundness gate (their `sys_*` don't prove
standalone — Type-invariant + bounds + array-creation VCs blow up when inlined). Clearing them is the
**leaf-first body-VC effort**: fix the foundational helpers' value contracts, then the mid composers,
then the syscall body-VCs. This is independent of the axioms.

### Bucket B — the 3 axiom families (reduce the *TCB*)
To make the os **axiom-free** (everything inside the SMT perimeter), each cited family must be replaced
by an inline SMT proof:

- **`i18.round_trip`** (inode codec) — the **Track C** effort: a region byte-invariant supplies the
  codec's field ranges so `_unpack_inode`/`_pack_inode`'s *value* contracts prove, and the round-trip
  follows by composition. **Every mechanism is validated** (drivers 0661–0664; `_pack_inode`,
  `_unpack_inode` proved *standalone*); it is **blocked only by in-context proof cost** (§3).
- **`i1a1.round_trip`** (direntry codec, 6 sites) — the *same shape*, smaller struct (`>H30s`). Folds in
  after the inode case.
- **`Bitmap.bit_and_one_in_zero_one`** — genuinely **case-1** (a bitwise identity; SMT models `bit_and`
  uninterpreted). This one *should stay axiomatized* — there is no affordable inline SMT proof of a
  bitwise bound; the cross-validated axiom is the right home permanently.

So "fully proven os" = **Bucket A** (the 23 body-VCs) + **Bucket B minus Bitmap** (the two round-trip
families). The Bitmap axiom is a permanent, correct case-1 citation.

## 3. Why Bucket B is blocked today — the in-context proof-cost wall

The Track C chain proves **per-mechanism** but not **in aggregate** (full analysis: `c-impl.md §3c`):

- **Standalone is cheap, in-module is not.** `_unpack_inode`'s 18 field-range ensures prove in **12 s** in
  a *minimal* file but **> 300 s** inside the full `UnixInodeFileSystem` module. The inflator is the
  module **context/preamble** — 9 axioms, the record type with 10 class invariants, 50 sibling
  functions — which makes each goal far more expensive to solve.
- **Two per-function pitfalls** (found + fixed standalone, must be applied module-wide): unroll the
  block-field loop (else block ranges need a loop invariant); and use **specific** per-byte requires, not
  a quantified `∀i<64` (which times out on instantiation).
- **The cost compounds.** The full chain is: region byte-invariant `[512,2560)` → `_read_inode` feeds the
  64 byte-bounds to `_unpack_inode` → field ranges → `_write_inode`'s 18 requires discharge → per-syscall
  discharge (literal trivial; disk-read from `_unpack`; computed mutations from `new_size ≤ 131072 < 2³²`,
  `_now()`, `_alloc_block`) → full-os framing of the non-inode writers (bitmap `[0,36)`, dir `[2560,3072)`,
  data `[3072,…)` — all outside `[512,2560)`, framed from existing bounds). Each step is a **300 s–1200 s**
  proof, several chained, with a **~20-min full-os gate** between integration steps.

It is **not a missing mechanism** — it is that the faithful, richly-contracted os is **proof-cost-bound in
aggregate**.

## 4. The dedicated multi-session grind (larger time budget)

### 4.1 The time budget — two levers, used together
1. **Raise the per-goal solver budget.** Today the runner uses `--timelimit 30` (30 s/goal). The codec
   functions need **120–300 s/goal** in-context. Raise it for the codec-bearing module (and add Z3/CVC5
   alongside Alt-Ergo; try more cores so split-VC goals run in parallel).
2. **Cut the per-goal context cost — the real lever.** Brute time alone is expensive (a full os at
   300 s/goal × ~1150 goals is many hours). The structural fix is **modular verification**: verify each
   codec function in a **minimal context** (where it is 12 s) and have the os module **import its
   contract**, not re-verify its body. PyCSL's `#@ no_inline` already does this for *methods*; the codec
   functions (`_pack/_unpack_inode`, `_pack/_unpack_direntry`) are *free functions*, so this needs either
   (a) extending `no_inline`/`#@ \abstract`-with-separate-proof to free functions, or (b) **true separate
   compilation** (verify the codec as its own unit; the os imports the narrowed contract — exactly Track
   B's interface + `try.md §7`). **(b) is the highest-leverage tool investment** — it converts the
   aggregate wall into N cheap standalone proofs.

### 4.2 Session plan (each session lands a gated piece; os stays green between sessions)

| Session | Deliverable | Gate (budget) |
|---|---|---|
| **G0** | **Tooling** — raise `--timelimit` for the os module; add a second prover; (ideally) land modular verification / separate-compilation for free functions (§4.1 lever 2). Without it, G1–G4 pay full in-context cost. | tool change; corpus byte-clean |
| **G1** | **Codec value contracts** — `_pack_inode` rich def (length + 18 values + `∀i<64` bytes) + interface; `_unpack_inode` 18 field-range ensures (unrolled loop, specific per-byte requires). Both already proved **standalone**; land them in-module under the raised budget (or via G0's modular boundary). | each proves in-module |
| **G2** | **Region byte-invariant** `[512,2560)` + `_read_inode` supplies the 64 byte-bounds to `_unpack_inode` (instantiating the quantified disk invariant at the call — likely needs specific extraction or a small bridging lemma). | `_read_inode`/`_unpack` chain proves |
| **G3** | **C1 + syscalls** — `_write_inode` + 18 range requires; `__format_disk` byte sources; per-syscall discharge (literal/disk-read/computed). | each syscall `--fun` proves |
| **G4** | **Full-os integration** — the non-inode writers frame from their bounds; **drop the `i18.round_trip` citation**; full os run. | **os holds at 23, axiom-free for i18** (~20-min gate) |
| **G5** | **`i1a1.round_trip`** (direntry) — same chain, smaller struct; drop its 6 citations. | os holds at 23, i1a1 axiom-free |
| **G6 (parallel track)** | **Bucket A** — the 23 body-VCs via leaf-first (`os-bodyvc-spec`). Independent of B; can interleave. | unproven count < 23 → 0 |

**End state:** os fully SMT-proven except the **`Bitmap` bitwise axiom** (a permanent, correct case-1
citation). TCB shrinks from 3 axiom families to 1.

### 4.3 Cost model & risk
- **Per-session cost:** G1–G3 iterate with fast `--fun`/standalone proofs (seconds–minutes each); G4/G5
  each cost one or more **~20-min full-os runs** (the integration gate). Budget several full-os runs per
  integration session.
- **Without G0 (modular verification):** every codec function pays the in-context inflation (300 s–1200 s
  each), and the full-os gate is the dominant cost — feasible but slow; **G0 is what makes the grind
  affordable**.
- **Risk management:** each session must leave os **green** (≥ its current proven count) or revert — the
  invariant breaks all inode-region writers at once, so a session that adds the region invariant must
  also land G3's writers before the full-os gate, or hold the change on a branch. Never commit a state
  where os regresses below 23.
- **Realistic estimate:** **G0 (tool) + 4–5 implementation sessions** for Bucket B (i18 then i1a1), plus
  the separate Bucket A leaf-first track. The single biggest determinant is whether G0 (modular
  verification of free functions) lands — with it, the grind is bounded standalone proofs; without it, it
  is a long brute-force against the aggregate wall.

## 5. One-paragraph synthesis

The os is **~98% SMT-proven with every body verified and only 9 cross-validated axiom citations from 3
families** in its TCB. Two independent bodies of proof remain: **(A)** the **23 disk-mutating-syscall
body-VCs** (leaf-first body-VC work, reduces the unproven *count*), and **(B)** the **codec round-trip
axioms** (`i18` + `i1a1`), whose inline SMT proof (Track C) is **mechanism-complete but proof-cost-bound
in aggregate** — each codec function proves standalone (12 s) but is slow in-module (> 300 s) and the cost
compounds across the chain. The dedicated grind is a **tool session (G0: raise the budget + modular
verification of free functions / separate compilation — the decisive lever) followed by 4–5 gated
implementation sessions** (codec contracts → region byte-invariant → `_write_inode`/syscalls → full-os
integration dropping the citation, then the direntry repeat), each kept os-green, with the `Bitmap`
bitwise axiom remaining a permanent, correct case-1 citation. Until that grind is funded, the
cross-validated `round_trip` axioms are the **pragmatic, sound** resting point.
