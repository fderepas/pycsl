# os-23-strategy.md — proving the 23 os primitives (without the CompCert/seL4 hammer)

**Date:** 2026-06-08
**Status:** Strategy (for review — no code changed)
**Owner:** [STDLIB] (`pure_lib/os/**`) + [TOOL] (`src/pycsl/**`) + [FORMAL] (`src/formal-semantics/**`)
**Origin:** `09-0757-desc.md` (the `--deep` context-bloat); `try.md` §1.1 (the 23 are the disk-mutating
syscalls' body-VCs); `b-p4-spec.md` (the codec field-range requires-bloat); the A/B/C/D tracks +
`08-1537` (`no_inline`).
**The question:** prove the 23. **The framing to refute:** that this needs a CompCert/seL4-style
verified-extraction effort. It does not — and the reason is the whole strategy.

---

## 1. What the 23 actually are (read from the code)

The 23 unproven goals are the postconditions of the disk-mutating syscalls — `sys_mkdir`,
`sys_unlink`, `sys_rmdir`, `sys_link`, `sys_access`, and siblings. Three facts about them, taken
directly from `UnixInodeFileSystem.py`:

- **Their postconditions are return-code disjunctions.** `sys_mkdir`: `ensures \result == 0 or
  \result == -1`. `sys_open`: `\result == -1 or \result >= 3`. Nothing about disk *contents*.
- **Every `return` returns a literal.** `sys_mkdir` returns `-1` at five guards and `0` at the end;
  `sys_unlink` returns `-1`/`0` likewise. The returned value is a constant at every exit.
- **The class invariant is light:** `\length(self.disk) >= 131072`, the four fd-columns are length 64,
  `self.next_fd >= 3`, three non-negativity facts. No quantified-over-index invariant.

The bodies are guard-heavy control flow calling helpers (`_dir_lookup`, `_read_inode`, `_write_inode`,
`_alloc_inode`, `_alloc_block`, `_write_entry`, `_check_perm`) over the 131072-byte `disk` array.

## 2. Why they fail — and what *kind* of failure this is (the crux)

**It is not foundational unprovability. Every sub-goal is individually easy.** Pushing Why3's weakest-
precondition back through `sys_mkdir`:

- **Return code `\result ∈ {0,-1}`** — every exit is a literal `0`/`-1`; trivially true, **with zero
  disk reasoning.**
- **Callee preconditions** — `_write_inode(inode_num, inode)` needs `0 ≤ inode_num < 32` (the guard
  `if inode_num < 0 or inode_num >= 32: return -1` establishes it) and `\length(inode) == 18` (the
  inode is an 18-element literal). `_write_entry(p_block, slot, …)` needs `0 ≤ p_block < 256` (guard)
  and `0 ≤ slot < 16` (`_dir_find_free` ensures `\result < 16`; the guard rules out `-1`). All easy.
- **Bounds on direct disk slices** — `self.disk[2560 + slot*32 : +32]` needs `slot < 16` ∧
  `\length(self.disk) >= 131072` → `3072 ≤ 131072`. Simple arithmetic.
- **Type-invariant preservation** — slice-writes are length-preserving; helpers preserve the invariant.

So each goal is "flies in the room," not "an unprovable theorem." They fail for **three tractability
frictions**, none foundational:

1. **Context bloat (the `09-0757` story).** The codec's contracts quantify over 64 byte-indices
   (`_pack_inode`/`_unpack_inode` carry ~64 range ensures + 18 value ensures *each*). In scope at a
   syscall goal, they become fuel for trigger-based quantifier instantiation, and the solver chases an
   instantiation space that swamps the easy bounds arithmetic. `--deep` makes this **catastrophic** by
   pulling the *entire transitive closure* (clock, world, path) in at once; even without `--deep`, a
   *rich* codec contract in scope is costly.
2. **Body length.** Long guard-heavy bodies generate many sub-goals per syscall; the cumulative
   per-goal budget overruns even when each goal is cheap.
3. **The codec field-range requires-friction (`b-p4-spec`).** `_pack_inode` *requires* 18 field-range
   bounds (`0 ≤ fields[k] ≤ MAX_k`). `_write_inode`'s precondition is only `\length(inode) == 18` —
   it cannot supply those ranges. Today this is papered over by a **cited Rocq/Lean axiom**
   (`#@ proof rocq …i18.round_trip` on `_read_inode`/`_write_inode`) — a **TCB entry**. The sound fix
   (Tier 1) removes the friction without the axiom.

> **Diagnosis:** the 23 are an **SMT-tractability** problem (context + body-length) plus a **requires-
> friction**, not a provability problem. That single fact is why the cure is far lighter than CompCert.

## 3. The heavy anchor — CompCert / seL4: why it would work, and why it is the wrong tool here

You are right that the heaviest approach *would* work, so it is worth saying exactly what it is and why
it does not fit.

| | CompCert | seL4 |
|---|---|---|
| Method | the compiler is written in **Coq/Gallina**, proven semantics-preserving, **extracted** to OCaml | hand-written **C** proven to **refine** an abstract spec, in **Isabelle/HOL** |
| Discharge | the **proof-assistant kernel** (human-guided proofs), not an SMT solver | same |
| TCB | Coq kernel + extraction | Isabelle kernel + the C-to-binary assumptions |
| Effort | a career | ~20 person-years |
| Targets | goals SMT **genuinely cannot reach** (whole-compiler semantic preservation) | full functional correctness of a microkernel |

**Why it would work:** a proof-assistant kernel can discharge *any* true goal given the human proof —
including ones no SMT solver closes.

**Why it is the wrong tool for the 23:** the 23 are **SMT-closable** (§2 — each sub-goal is
individually easy). CompCert/seL4 machinery exists to defeat **foundational unprovability**; pointing
it at goals that are merely *context-crowded* is a sledgehammer for flies. You would re-write the
filesystem in a proof assistant and **abandon the PyCSL/Why3/SMT pipeline** — to solve a problem that
is context engineering, not provability. The existence proof ("it would work") is real and irrelevant
to cost.

**The one legitimate Rocq/Lean use here is already in the code, and it is tiny:** the i18 round-trip is
cited as a Rocq/Lean axiom on `_read_inode`/`_write_inode`. That is **Track D** — kernel-backing a
*single foundational lemma*, not the whole os. Keep that scoped (Tier 5); do not grow it into
extraction.

## 4. The PyCSL-native strategy — a tier ladder, apply only as much as needed

Each tier addresses a friction from §2, cheapest first. Stop when the 23 clear; most will fall to
Tiers 0–3. The tiers *are* the A/B/C/D tracks, sequenced for this specific goal.

| Tier | Move | Fixes | Cost | Track |
|---|---|---|---|---|
| **0** | **Never `--deep`; codec is a *direct* shallow neighbour** carrying only its `#@ interface` (`\length`) | friction 1 (catastrophic flood) | trivial | `09-0757` |
| **1** | **Totalize the codec leaves** — `_pack_inode` requires only `\valid`; value-ensures guarded by the range | friction 3 (requires-bloat) **+ removes the i18 axiom's necessity** (TCB↓) | low | `b-p4-spec` |
| **2** | **Opacity on every helper** — each `_read_inode`/`_write_inode`/`_dir_lookup`/fd-helper gets a narrow `#@ interface` (return-code range + invariant preservation only) | friction 1 (residual) | medium | **B** |
| **3** | **Split + `no_inline`** — prove each `sys_*` standalone in the thinned context; if it proves, `no_inline` it so the `os.*` wrappers reuse its contract | friction 2 (body length) **+ confirms body-VCs discharge** | medium | `08-1537`, soundness-gated |
| **4** | **Scoped abstraction barrier** — only for any syscall still resisting: abstract inode/fd/dir view; prove its return-code over abstract maps, byte-VCs confined to boundary funcs | a genuine residual body-VC | high | **C** (incl. L0″) |
| **5** | **Rocq/Lean for lemma durability only** — a few foundational lemmas (codec round-trip) kernel-checked; **never** the proof engine for the 23, **never** extraction | durability of the one foundational fact | medium | **D** |

### How each tier bites the actual code

- **Tier 0** keeps the os module's logical context at *one slender codec contract* instead of an entire
  closure — the `09-0757` remedy, and the floor everything else assumes.
- **Tier 1** is the **first real unblock**: `_write_inode` calls `_pack_inode(inode)`, whose 18 field-
  range requires `_write_inode`'s `\length==18` cannot supply. Totalizing the leaves makes `_write_inode`
  prove **without** the i18 axiom — and unblocks every `_write_inode`-calling syscall (`mkdir`,
  `unlink`, `rmdir`, `link`). Replaces a **TCB entry** (the cited axiom) with a **sound proof**.
- **Tier 2** ensures a syscall goal sees `_dir_lookup` as "returns `-1` or `0..31`," not its internals —
  so the return-code disjunction (§2) closes against a handful of thin facts.
- **Tier 3** checks `sys_mkdir` *alone* (thin context). Per §2 it should now prove; `no_inline` then lets
  `os.mkdir`/`os.makedirs` reuse its contract instead of re-proving the inlined body (the `08-1537`
  move, now **soundness-gated** because `sys_mkdir` proves standalone — no `readlink`-style false green).
- **Tier 4** is the principled dissolve, reserved for stragglers: the return code depends only on
  control flow, so an abstract inode/fd/dir view makes the resisting syscall's proof a tiny map-level
  argument, with the disk-byte VCs proven once at `_read_inode`/`_write_inode`. Highest cost (needs
  L0″, the logic-view codec) — apply *only* where Tiers 0–3 leave a hard goal, never wholesale.
- **Tier 5** keeps Rocq exactly where it already is — backing the codec round-trip as one kernel-checked
  lemma (prefer **replay** over the current **axiomatize**, to shrink the TCB) — and nowhere else.

## 5. Expected outcome & sequencing

- **Tiers 0–1 (cheap):** likely clear the `_write_inode`-calling syscalls (`mkdir`, `unlink`, `rmdir`,
  `link`) — the friction there is the field-range requires, which Tier 1 removes.
- **Tiers 2–3 (medium):** clear the rest by thinning every syscall's context and proving each `sys_*`
  standalone, then reusing the contracts via `no_inline`.
- **Tier 4 (high, contingent):** only any genuine body-VC straggler — still PyCSL-native, not CompCert.
- **Tier 5:** never for the syscalls; only to harden the codec lemma's durability.

**Realistic path to "23 → 0": Tiers 0–3, with 4 as contingency. No CompCert/seL4.**

## 6. The argument in one place — why simpler-than-CompCert exists

The disease is **SMT-tractability** (a crowded context + long bodies) plus a **requires-friction** —
not foundational unprovability (§2). The cure is **context engineering**: thin the context (opacity,
Tier 0/2), shorten the per-goal work (modular boundaries, Tier 3), and — only if needed — raise the
abstraction so syscalls never touch bytes (Tier 4). That toolkit is *exactly* what PyCSL already has
(the A/B/C tracks). Rocq/Lean stays scoped to the durability of a *single* foundational lemma (Tier 5,
the i18 round-trip — as the code already does), never the proof engine. CompCert/seL4 defeat a
different, harder disease (goals SMT cannot reach) and would be wasted — and pipeline-abandoning — here.

## 7. Risks & honest caveats

- **A syscall may still resist after Tiers 0–2.** If `sys_mkdir` does not prove *standalone* (a genuine
  bounds/array-creation VC the solver cannot get in budget), that one needs **Tier 4** — measure, don't
  assume. It remains PyCSL-native.
- **Tier 1 changes the codec's value guarantee to *conditional*.** The round-trip lemma must be re-
  proven under the totalized leaves (it carries the range hypothesis where it always did — `b-p4-spec`
  S4). Verify it still proves before relying on it.
- **The i18 axiom is a current TCB entry.** Tiers 1/5 should *replace* it with a sound proof (Tier 1)
  or a kernel **replay** (Tier 5), not leave it as an unverified `axiomatize`. Track the TCB in the
  ledger.
- **Measure after each tier** — which syscalls cleared, and at what context size. The probe discipline:
  reason to design the tier, run it to decide the next.
- **`no_inline` (Tier 3) is only sound if the `sys_*` proves its real contract standalone** (the
  `08-1537-rev2` performance-vs-soundness gate). Confirm each before reusing its contract.

## 8. Out of scope

Full os extraction (the Tier-5 extreme — explicitly de-scoped, §3); the direntry codec
(`_pack_direntry`/`_unpack_direntry` — same totalize + interface pattern, fold in after the inode
case); **rich functional postconditions** beyond return codes (e.g. "`mkdir` creates a type-2 inode") —
those genuinely want Track C's abstract view and are a separate, later goal; changing the SMT solvers
or Why3 itself.

> **In one line:** the 23 are not a foundational-unprovability problem (every sub-goal is individually
> easy — the return codes are literal-valued and disk-content-independent), so they do **not** need a
> CompCert/seL4 verified-extraction effort; they are an **SMT-tractability** problem — a context
> crowded by the codec's quantified byte-index contracts (worst under `--deep`), long syscall bodies,
> and the codec's field-range *requires*-friction (today patched by a Rocq axiom). The PyCSL-native
> cure is a tier ladder that thins the context and raises the abstraction using the tracks already
> designed: **Tier 0** never-`--deep` + codec-as-direct-neighbour, **Tier 1** totalize the leaves
> (removing the requires-bloat *and* the axiom), **Tier 2** opacity on every helper, **Tier 3**
> standalone-prove + `no_inline` the syscalls — clearing 23→0 for the realistic path — with **Tier 4**
> (scoped abstraction) only for stragglers and **Tier 5** (Rocq) reserved for the durability of the one
> foundational codec lemma, never extraction.
