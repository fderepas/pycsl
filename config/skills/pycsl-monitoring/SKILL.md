---
name: pycsl-monitoring
description: >-
  The accumulated, Gate-S-audited knowledge base of the `test-supervise-sl`
  squeeze loop (the monitor that drives `formal-test-sl`). Holds the proven
  patterns for getting PyCSL formal tests to fully prove, the coherent-and-wrong
  catalog for formal tests (the vacuous-test shapes), per-module coverage ledgers,
  and the discipline for adding knowledge (only via Gate S, traceable, carve-outs
  cite the upper bound). Consult and update this whenever supervising or monitoring
  a fleet of formal-test runs, deciding whether a learned heuristic is in-band,
  diagnosing why a formal test will not prove, or recording coverage. Trigger
  phrasings: "monitor the formal-test loop", "what patterns make a formal test
  prove", "is this formal test vacuous", "record formal-test coverage", "audit a
  consolidated formal-test skill", "Gate S on a PyCSL heuristic", "what's the os
  formal-test coverage".
---

# pycsl-monitoring — knowledge store for `test-supervise-sl`

This skill is the **persistent, disjoint knowledge base** that the supervising loop
`test-supervise-sl` (see `test-supervise-sl.md`) accumulates while monitoring the
base loop `formal-test-sl` (see `formal-test-sl.md`). It is written **only by the
disjoint skill-monitor**, never by the base loop about itself (that would be
self-judging). Everything here has passed **Gate S** (`sl-monitoring-sl`).

## BINDING: the extreme-rigor path is the ONLY path

`test-supervise-sl` is the bearer of the extreme-rigor doctrine (full text in
`test-supervise-sl.md` §Doctrine). The operative rule, restated here because every
run reads this store: **a residual is NEVER closed by adding trust.** A raw
`\trusted`, a reviewer-trusted helper, or a "ready trusted swap" (e.g.
`_rename_swap`) is **struck from the option set** — it is a Gate-B/Gate-C REJECT, not
a choice. The only sanctioned closure routes are (a) Rocq+Lean cross-validated +
cited `#@ proof`, (b) a restructured / re-folded proof, (c) a different prover /
tactic. **If none discharges the goal, the target is a LOGGED GAP routed to the
human — never a trusted "done", and never offered as "accept the trusted swap".**
Adopting even a cross-validated axiom (kernel-PROVED, not bare `\trusted`) is a
human-gated TCB decision, not the loop's. Recorded GAPs under this rule (e.g.
`sys_rename`, see §C) stay open until a rigorous route lands.

## Discipline for adding knowledge (non-negotiable)

- **Gate S first.** A heuristic enters this file only after the skill-monitor
  classified it (ignore-signal vs defer-to-oracle), ran the matching check (trigger
  / validity test against the PyCSL oracle), and returned PASS or CARVE-OUT. A
  REJECT is logged, not kept.
- **Grounded & traceable.** Each entry cites the upper-bound clause (spec /
  methodology rule) it serves, and the run/inputs that revealed it.
- **Carve, don't discard.** Narrow an over-general skill with a bound-deferring
  exception; keep the valid core.
- **Safe direction.** An entry may only make a formal test *stronger / more
  faithful*, never license a weaker or vacuous one.
- **Disjoint authorship.** Only the monitor writes here. The base loop may *propose*
  a skill (a returned soft output); it does not *enter* it.

---

## A. Proven patterns (what makes a PyCSL formal test fully prove)

*(Seeded from the os work; each is a PASS/CARVE under Gate S.)*

1. **Test the observable CONSEQUENCE, not the op's return code.** A formal test is
   setup → operate → observe (write→read-back; mkdir→stat-sees-it→rmdir→stat-gone).
   Asserting the op's own `\result` is vacuous. *(Serves: the consequence rule.)*
2. **Call the public API; never simulate.** The driver calls `os.*` / the module
   API; it never re-implements the op on the data structure or inlines internals.
   Enforced physically: the driver author's context has API + spec only, not the
   internals — so it *cannot* simulate. *(Serves: the calls-the-API rule.)*
3. **Leaf-first, compose-don't-re-derive.** When a clause won't discharge, the cause
   is usually a missing **leaf VALUE contract**; fix bottom-up (the codec leaves'
   value contracts compose into the inode round-trip; the syscall reuses proven
   contracts via `#@ no_inline`). Never weaken the test to land.
4. **Cross a `#@ no_inline` boundary with a FOLDED uninterpreted atom, never a bare
   `∀i`.** A `\forall i …` (and `\array_eq`, which lowers to the same `∀i`) does NOT
   propagate across a `no_inline` boundary (Alt-Ergo and Z3 both go Unknown). Fold
   the per-element fact into an uninterpreted predicate (e.g. `block_content_eq`)
   with definitional intro/elim; the atom crosses as one term. *(This is the gap-17
   content-round-trip mechanism.)*
5. **A non-vacuous range/value postcondition needs an early-return guard.** If an
   early path (`if n == 0: return 0`) returns before establishing the claimed field,
   guard the ensures antecedent (e.g. `\result >= 1`) — else the claim is false on
   that input. *(Carve-out from the fd_block empty-write bug this session.)*
6. **Re-run the gate on the COMMITTED artifact; never re-report an intermediate
   count.** A green taken from an intermediate run while the committed file is red is
   the self-declared-done collapse. Run `PYTHONHASHSEED=0` on the file as it stands.
7. **Keep array-heavy reopen/read/write consequence theorems in their OWN file.**
   A light fd-chain / namespace theorem that PROVES in isolation can flip to
   `Unknown` purely by being co-located with a heavy `open→write→close→reopen→read`
   theorem in the same module (shared E-matching context starves the light goal's
   step budget). Byte-identical body + import set, different verdict — the only
   variable is the sibling theorems. Diagnose by re-proving the goal alone; do NOT
   blame a missing contract. *(Carve-out: split `content_round_trip*` out of
   `formal_os_fd`/`formal_os_rwsize` this session; see
   `getting-better/20260616-2050-formal-test-context-pollution.md`.)*
8. **Co-import an array-trigger op (`mkdir`+`access`) with a return-code-only
   filesystem stub.** Importing `chmod`/`truncate` alone yields
   `unbound type symbol 'array'` at L3-tc — the emitter omits `use array.Array`
   when no imported contract carries an explicit array term, even though the
   pulled-in helper `val`s reference `array int`. Co-importing+calling `mkdir`
   (whose `dir_lookup` ensures is an array term) emits the `use`. *(CONFIRMED
   emitter bug: `bugs-to-report/20260616-2050-import-stub-missing-use-array.md`.)*

9. **Adding a leaf precondition can RELOCATE a residual, not close it — re-prove the
   CALLER in isolation before claiming the win.** A failing callee Precondition
   sub-goal (e.g. `_unpack_direntry` calling `_unpack_uint16_be` with `0<=data[..]<=255`
   it can't establish) is "fixed" by requiring the byte-range at the callee — but that
   only makes the callee prove; the obligation moves to EVERY caller, which may equally
   lack the fact. Verdict rule: a fix that keeps the total non-Valid COUNT the same (or
   adds an unmet caller obligation) is NOT a win, it is a relocation → REVERT. Diagnose
   by `--fun <caller>` after the edit: if the same Unknown fingerprint reappears at the
   caller, the real missing fact is upstream (here: a directory-region disk byte-range
   predicate the model doesn't have). Route bottom-up to the genuine source fact;
   if that needs a model extension, it's a GAP, not a cheap win. *(Carve-out from the
   2026-06-17 `_unpack_direntry` WIN-1 probe;
   `getting-better/20260617-0909-direntry-byte-range-gap.md`.)*

## B. Coherent-and-wrong catalog for formal tests (what the monitor hunts)

| Shape | Tell | How the monitor catches it |
|---|---|---|
| **Self-return assertion** | `#@ ensures \result == 0 or 1` — holds even if the op fails | Gate C non-vacuity seed: break the op, the test must FAIL |
| **Simulation** | the driver mutates the data structure / inlines internals instead of calling the API | API-only audit; the physical barrier prevents it at source |
| **Adjacent-weaker** | proves the byte-COUNT round-trip while claiming the byte-VALUE round-trip (`formal_0008` `back == c` int-vs-array) | clause map: the `ensures` must be the *intended* property, not a weaker cousin |
| **Plane blend** | a `--no-proof` (emission) green reported as "proven" | no-blend: emission ≠ proof |
| **Honorary green** | "the gate is green" from a stale/partial run | re-run on the committed file; scan EVERY status incl. `Out of memory` |
| **Aggregate noise mistaken for a residual** | a goal fails in the full-file gate but proves in `--fun` isolation | re-check residuals per-method before recording them as real |
| **Empty-disk artifact mistaken for a no-trust retirement** | a de-trusted helper's fidelity ensures appears `Valid` in `--fun` isolation, but the property has no logical path from the body (binds an uninterpreted symbol with no defining axiom) | the isolated pass rides the canonical zeroed `by{}` witness, not the body. Triangulate constants (`==0` ✓, `==1` ✓, `==7` ✗ = perf artifact, not logic) AND run the SOUNDNESS PROBE: add a `#@ requires` that forces a non-canonical disk (e.g. `slot_inode(self.dir,5,0)==3`); if the ensures then fails, the isolated pass was the empty-disk artifact. Decisive test is the FULL body gate (real non-canonical `self`) — there it OOMs/reds. NOT a retirement. *(dirscan-fidelity pilot, 2026-06-17.)* |
| **Stale test after a model upgrade** | a committed `formal_*` file FAILS at L3-tc with `int`-vs-`string` type errors, or its header claims a consequence is "UNPROVABLE/Unknown" that now proves | the model gained str-typed path params / `dir_lookup` consequence ensures since the test was written; RUN it, fix the param types, and rewrite the stale header to the now-passing reality (don't trust the comment) |
| **Context pollution mis-blamed on a missing contract** | a theorem is `Unknown` in-module but the author "fixes" it by weakening or adding a contract | re-prove the goal ALONE; if it passes in isolation the contract is fine — split the file instead (pattern A.7) |
| **Partial-codec-rung mistaken for a trust retirement** | a new (even cross-validated) byte/string codec axiom makes ONE sub-ensures of a `\trusted` method prove in `--fun`, reported as "the trust is retired" | a `\trusted reviewer` covers the WHOLE method — enumerate every clause: a VALUE ensures may now prove while the `\forall k!=slot` FRAME + `uniq`/`slots_lt32` class-invariant ensures still EXPLODE (Type-invariant Timeout, millions of steps) the moment the body materializes concrete byte terms. A trust is all-or-nothing per method; retirement requires EVERY clause body-proven AND both gates green. Run the FULL method gate, not just the rung. *(slot_inode byte-codec keystone, 2026-06-17.)* |
| **Banked keystone whose narrow trigger never fires on the real body** | a byte-decode axiom keyed `[disk[blk*512+32*k]]` is merged + cross-validated and assumed "ready", but the mutator body indexes through a let-bound ref (`self.dir[!entry_offset]`) so the trigger never E-matches and the ensures still Times-out (8.5M steps) even with the byte VALUES available | a deliberately-narrow byte-keyed trigger (the safety that prevents the GLOBAL `slot_inode`-atom explosion) is exactly what stops it firing at a mutator that abstracts the index behind a variable. Verify firing by inspecting the emitted `.mlw` (does the literal `disk[blk*512+32*k]` term appear at the assert?), not by assuming "the keystone is banked, so it applies". Closing it requires literal-index restructuring OR a `slot_inode`-keyed bridge (a human-gated TCB axiom) OR Why3 normalization — NOT autonomous. *(dirscan write-side pilot `_write_dir_entry`, 2026-06-17.)* |

## C. Per-module coverage ledger

### os (`pure_lib/os/`) — as of 2026-06-17 (re-measured ground truth)
- **Body gate (authoritative, full file):** **2016 Valid / 8 residual** (grep count;
  the 8 = 5 UNIQUE non-Valid + 3 summary echoes). Unique residuals re-confirmed
  2026-06-17 (PYTHONHASHSEED=0, Alt-Ergo 2.6.2 / Z3 4.13.3, load ~2-5): `_unpack_direntry`
  ×2 (Unknown 320459/337358), `_now` ×1 (Out of memory), `sys_rename` ×2 (Timeout
  4621194 + Out of memory). `sys_write` proved this run (the historical "×3 aggregate
  noise" was absent — aggregate noise is non-deterministic; re-measure, don't trust a
  stale count). **0 `\trusted`.**
- **`__init__` gate:** **1159/0 GREEN, SUCCESS, exit 0** — WITNESSED clean 2026-06-17
  on the committed working tree (no edits to `__init__.py` or `UnixInodeFileSystem.py`
  survived; the WIN-1 experiment was reverted before this run).
- **`_unpack_direntry` residual — diagnosed CONFIRMED, the prescribed cheap fix does
  NOT close it (it RELOCATES).** Root cause: `_unpack_uint16_be` is emitted as a `let
  function` (NOT inlined) carrying `requires 0<=data[offset..+1]<=255`; `_unpack_direntry`
  calls it with only `\valid(data,32)`, so the 2 byte-range preconditions can't
  discharge. Adding the minimal 2-clause `#@ requires 0<=data[0..1]<=255` to
  `_unpack_direntry` makes the LEAF prove (Valid 2016→2018) but moves the SAME Unknown
  (fingerprints 381631/304712) to its sole caller `_read_directory`, which reads
  `self.disk[entry_offset:+32]` (block 5, offset≥2560) and has NO byte-range fact:
  the only disk byte-range predicate `inode_bytes_valid` covers ONLY `[512,2560)` (the
  inode table), per `src/pycsl/module6_whyml/preamble.py:551-557`. The directory region
  `[2560,3072)` is unconstrained. Net residual stays 8 + an unmet caller obligation →
  strictly worse → REVERTED. **This is a LOGGED GAP**, not "fix found / deferred": the
  faithful close needs a directory-region (or whole-disk) byte-range predicate
  established in the constructor and maintained by every disk mutator — a substantial,
  `__init__`-gate-risky model extension, NOT a cheap win. See
  `getting-better/20260617-0909-direntry-byte-range-gap.md`. The prior
  `bugs-to-report/20260616-1929-noinline-leaf-not-val-in-importer.md` is SUPERSEDED
  (the blocker is byte-range, not `no_inline` re-verification; the 2-clause version
  fails at the BODY gate before reaching `__init__`).
- **Proven formal tests:** `formal_os_roundtrip` (18/18, totality), `formal_os_content`
  (48/0, on-fd write→pread==data content round-trip), plus the topical
  `formal_os_*` family. As of 2026-06-16 (test-supervise-sl os mission) ALL 19
  `formal_os_*.py` files prove SUCCESS / 0 non-Valid / 0 `\trusted`, each
  re-confirmed non-vacuous from the supervisor's disjoint base (seeded
  falsification flips to FAILED). Every public `os.*` symbol in `__init__.py` has
  a proven consequence (not return-code-only) EXCEPT `walk` (yields, geometry
  only) and the pure stubs (chflags/confstr/copy_file_range/getxattr/listxattr/
  kill/islink — total constants by spec) and chmod/truncate (return-code only;
  no mode/size accessor — model gap, below).
- **Leaf-first extensions this session (zero new trust, body-faithful):**
  `sys_close` gained `\result==0 ⇒ fd_open[fd]==0` (close post-state); `sys_fstat`
  gained the EBADF twin `fd_open[fd]==0 ⇒ \result==-1`; `sys_lseek` gained the
  SEEK_SET consequence `whence==0 ∧ offset≥0 ∧ open ⇒ \result==offset ∧
  fd_offset[fd]==offset`. Propagated to the public `close`/`fstat`/`lseek`
  wrappers. New tests: `formal_os_close` (close→fstat==EBADF) and `formal_os_lseek`
  (lseek SET returns pos). Body gate failing-goal set UNCHANGED by these edits
  (same step-count fingerprints: 320459/337358/4621194) → no regression.
- **Barrier-integrity cleanup (2026-06-17):** `formal_os_io.py` was a barrier
  violation AND a bundle of vacuous self-return assertions — it constructed
  `UnixInodeFileSystem` directly and called `sys_dup2/getdents/fsync/ftruncate/creat/
  chown/utimensat` (NONE of which are public `os.*` symbols — only `dup` is), asserting
  only each op's return code. RECLASSIFIED + renamed to `pure_lib_test/internal_os_io.py`
  (functions `internal_os_*`), with a docstring that loudly states (a) it reaches
  internals BY NECESSITY (no public API exists for these ops) and (b) the assertions
  are return-code SAFETY bounds, NOT consequences — so it is explicitly NOT in the
  public `formal_os_*` family. Still SUCCESS / 0 non-Valid / 0 `\trusted`. LESSON:
  when an op has no public API, an honestly-labeled internal smoke test is the
  doctrine-compliant home — never a `formal_os_*`-named return-code-only "consequence"
  test (that is the self-return vacuity shape masquerading as coverage).
- **Open frontiers (logged gaps, not failures):** reopen-by-name content/size
  round-trip (write count is `<=` not `==`; reopened size unpinned through
  reopen-by-name) — the on-FD round-trip IS proven (`formal_os_content`);
  open(absent,O_RDONLY)==-1 with absence NOT pre-established (a never-created
  name's `dir_lookup` is havoc'd — provable only WITH an established absence, as
  in `formal_os_enoent` after mkdir→rmdir); **chmod mode-reflected / truncate
  size==length — LOGGED GAP, NOT a cheap win** (probed 2026-06-17): no public
  mode/size accessor (`sys_stat` returns only the inode NUMBER), no `inode_mode`
  logic accessor, no MODE-field round-trip ensures on `_read_inode`/`_write_inode`
  (only field 0=size and field 8=block have read-back ensures); closing it is a
  multi-rung extension (accessor + codec round-trip rung + sys_* consequence ensures
  across `no_inline` + NEW public observer API + `__init__` wrapper plumbing + the
  formal test). See `getting-better/20260617-0914-chmod-truncate-consequence-gap.md`;
  multi-block content; `sys_rename` no-trust closure — **a LOGGED GAP, not a trust
  candidate**: the only doctrine-compliant routes are a different prover / a
  restructured proof / composing its already-cross-validated lemmas in-context; the
  ready reviewer-trusted `_rename_swap` is OFF THE MENU (see the BINDING rule above).
- **`dirscan-fidelity` ×6 TCB debt — RETIREMENT IS SMT-INFEASIBLE, a structural wall
  (probed 2026-06-17; net TCB delta 0, 6→6, nothing retired/weakened).** The 6
  `#@ \trusted reviewer: dirscan-fidelity` directives (`_dir_lookup`, `_dir_find_slot`,
  `_dir_find_free`, `_write_dir_entry`, `_write_entry`, `_zero_entry`) bind their byte-
  scan body to the abstract symbols `slot_inode`/`slot_name`/`dir_lookup`, declared as
  **uninterpreted `val function`** (`preamble.py:771-774`). NO axiom DEFINES them over
  the concrete bytes (`preamble.py` slot_inode axioms 123-575 are all RELATIONAL:
  presence⇔existential, frame, uniqueness, nonneg, all-dead-on-zeroed). So the bodies
  have no logical path to the fidelity ensures. **Route (a) blocked:** the
  `UnixDirScan{,Absent}` Rocq/Lean lemmas prove the scan STRUCTURE for an ABSTRACT
  decode (`UnixDirScan.v:27-33` `Variable slot_inode`) — they deliberately abstract the
  byte↔slot bridge away; the bridge itself is unprovable even in a kernel because the
  name byte-CONTENT is opaque (Gap 5, unmodeled). **Route (b) blocked:** de-trusting
  `_dir_find_free` → its postcondition OOMs in the FULL body gate (the `--fun` "Valid"
  was an empty-disk artifact — see the catalog row; soundness probe
  `requires slot_inode(self.dir,5,0)==3` flips it to FAIL); de-trusting `_write_entry`
  → Unknown/Timeout/OOM even in `--fun`. All six share the identical wall (same three
  symbols, same missing bridge). Per the HARD CONSTRAINT, removing a `\trusted` that
  reds a gate is a REGRESSION, not a retirement → directives STAY, logged GAP routed to
  the human. The real close = a concrete byte-decode definitional axiom for the three
  symbols, cross-validated Rocq+Lean — blocked TODAY by Gap 5 (name bytes unmodeled);
  a substantial model extension, human-gated. See
  `getting-better/20260617-1001-dirscan-fidelity-structural-wall.md`.
  - **KEYSTONE UPDATE 2026-06-17 (Gap-5 byte codec LANDED as a primitive; still net TCB 0,
    8→8 on the os).** The inode-FIELD byte→decode is now a cross-validated axiom
    `UnixFs.Dir.slot_inode_byte_decode` (preamble `_AXIOM_REGISTRY`; proofs
    `0711.proofs/{rocq,lean}/SlotInodeByteDecode.{v,lean}` — Rocq Closed under global
    context, Lean depends on NO axioms; exhibited+proven SUCCESS in corpus `0711.py`,
    ≤33k steps; byte-keyed trigger `[disk[blk*512+32*k]]` so it NEVER fires on the
    abstract `slot_inode` atoms; corpus byte-diff 0/601, both gates green). It is
    NECESSARY but NOT SUFFICIENT to retire a write-side trust: a `\trusted reviewer:
    dirscan-fidelity` bundles THREE obligations — (i) inode-VALUE `slot_inode==inode_num`
    (now byte-codec PROVABLE, Valid in `--fun`); (ii) name-VALUE `slot_name==name` (needs
    the `field_to_str` STRING codec, the ~23M-step E-match wall); (iii) the `\forall k!=slot`
    FRAME + `uniq`/`slots_lt32` class-invariant maintenance over the ABSTRACT symbol — and
    (iii) **EXPLODES** the moment the body materializes concrete `disk[...]` byte terms
    (Type-invariant Timeout 9.05M steps, measured), because the byte-keyed decode axiom and
    the `slot_inode`-keyed uniq/slots_lt32 axioms then coexist over the same disk. A
    `\trusted` is all-or-nothing per method, so the value half proving while the
    invariant half explodes ⇒ trust STAYS. The real remaining wall is therefore NOT
    "no byte decode" (it now exists) but **invariant-maintenance E-matching surviving
    byte materialization** + the string codec. See
    `getting-better/20260617-1039-slot-inode-byte-codec-keystone.md`.
  - **KEYSTONE UPDATE 2026-06-17 (Gap-5 STRING half LANDED as a primitive; net TCB still 0
    new on the os).** The name-FIELD byte→decode now exists too, as a cross-validated BRIDGE
    axiom `UnixFs.Dir.slot_name_byte_decode` (preamble `_AXIOM_REGISTRY`; proofs
    `0712.proofs/{rocq,lean}/SlotNameByteDecode.{v,lean}` — Rocq Closed under the global
    context, Lean depends ONLY on {propext, Quot.sound}; exhibited+proven SUCCESS in corpus
    `0712.py`, 24 Valid / 0 non-Valid; corpus byte-diff 0/shared, both gates byte-identical).
    The bridge states `slot_name disk blk k = field_to_str disk (blk*512+32*k+2) 30` (a
    32-byte `'>H30s'` slot = 2-byte inode + 30-byte name, so the name field starts at +2),
    byte-keyed on `[disk[blk*512+32*k+2]]` (the FIRST name-field byte) so it NEVER fires on
    abstract `slot_name` atoms; composing it with the already-merged `field_to_str_round_trip`
    gives the write-side `slot_name == name`. This RESOLVES obligation (ii) of the
    dirscan-fidelity bundle as a *banked primitive* — but it is STILL NOT a trust retirement:
    obligation (iii) (invariant-maintenance E-matching over the abstract symbol surviving
    byte materialization) remains the wall, exactly as for the inode half. Net: both VALUE
    halves (inode + name) are now byte-codec PROVABLE; the FRAME/invariant half is the open
    keystone for Step 2.
  - **STRUCTURAL LESSON (Gate-S PASS, slot_name string keystone, 2026-06-17): keep the
    string axiom OUT of the byte-blit loop.** The string round-trip itself crosses SMT in
    O(1) when its byte hypotheses are *given* (a probe with the per-byte facts as `requires`
    proved `slot_name == name` in ~20k steps — the round-trip + bridge APPLY fast). The
    ~23M-step E-match explosion is NOT the decode; it is the byte-keyed decode trigger firing
    *per loop iteration* inside the encode loop (the loop writes `disk[off+i]` where
    `off = blk*512+32*k+2`, so the trigger term `disk[blk*512+32*k+2]` materializes every
    iteration and drags `field_to_str`/string reasoning into pure-byte loop-invariant goals).
    FIX: factor the blit into a byte-ONLY helper whose contract names no `slot_name`/
    `field_to_str` and whose field offset is an OPAQUE parameter `off` (so the trigger pattern
    cannot syntactically match per-iteration); let the string axioms fire EXACTLY ONCE at the
    decode site in the caller, with the byte facts already in hand. This is the general
    discipline for any byte-keyed codec axiom used by a write helper: opaque-offset blit
    helper + single decode-site application. Trigger-tested: with the inline loop both the
    null-tail invariant and the postcondition Timeout at 5–9M steps; after factoring, the
    whole exhibit is 24/24 Valid.
  - **WRITE-SIDE PILOT 2026-06-17 (`_write_dir_entry`, net TCB 0, 8→8, working tree
    byte-identical to HEAD after revert).** De-trusting the simplest dir mutator and
    running `--fun unixinodefilesystem___write_dir_entry` pins obligation (iii) to a
    SHARPER root than "byte-materialization E-matching": **(1)** the leaf pack helpers
    DISCARD byte VALUES — `_pack_uint16_be` had NO contract; `_pack_direntry` ensured only
    `\length==32`. With value ensures added (`_pack_uint16_be`: `\result[0]*256+\result[1]==v`;
    `_pack_direntry`: `\result[0]*256+\result[1]==inode_num`, `\forall i<30. \result[i+2]==name_bytes[i]`)
    — both `--fun` SUCCESS — the slot_name Postcondition explosion drops **68M → 1.5M steps**.
    This is the genuinely-missing FOUNDATION (pattern A.3, leaf-first), proven and bankable.
    **(2)** Even then the keystone STILL does not fire: the body indexes via a let-bound ref
    `self.dir[!entry_offset]` (`entry_offset := block_num*512 + slot*32`), and the keystone
    trigger `[disk[blk*512+32*k]]` does not E-match the deref (and `slot*32` ≠ `32*k`
    syntactically). The `slot_inode==inode_num` assert Times-out at 8.5M with the keystone
    never applied (confirmed by reading the emitted `.mlw`). This is the DUAL of the
    opaque-offset discipline above: an opaque/let-bound offset that keeps the trigger from
    firing *per-iteration in the loop* ALSO keeps it from firing *at the decode site where
    you WANT it*. Closing it needs literal-index restructuring of the blit (`block_num*512 +
    32*slot`, no ref) OR a `slot_inode`-keyed bridge (human-gated TCB) OR Why3 trigger
    normalization. Per doctrine the de-trust reds the gate (5→7 goals) → REGRESSION →
    reverted → logged GAP. See
    `getting-better/20260617-1240-dirscan-write-keystone-trigger-gap.md`. New catalog
    row B: "Banked keystone whose narrow trigger never fires on the real body".

*(Other modules: `re` 16/16 stub-level; `warnings` 18/18 body + 3/3 formal;
`json` 6/6 thin-API. Add ledgers here as missions cover them.)*

---

## D. Outputs the loop files elsewhere

- **`getting-better/`** — ergonomic feature ideas (PyCSL/tooling improvements that
  would make formal tests easier). One concern per `YYYYMMDD-hhmm-name.md`.
- **`bugs-to-report/`** — candidate PyCSL bugs with minimal repro and
  `STATUS: CONFIRMED|UNCONFIRMED`. One per `YYYYMMDD-hhmm-name.md`.

These are *proposals*, not knowledge — they live outside this skill until acted on.
When a bug is fixed or a feature lands, fold the resulting durable lesson back here
(under A/B) via Gate S.
