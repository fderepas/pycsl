STATUS: OPEN — SMT WALL on an inductive loop property; to be closed by a cross-validated Rocq + Lean axiom (skill Step 5b). The exact lemma the next TOOL-AGENT must register in `src/pycsl/module6_whyml/preamble.py` is stated below (§Lemma). os kept GREEN at 1804/0 by REVERTING the syscall ensures + predicate (option (b)); the precise lemma is this doc's deliverable.

# Convergence gap — iteration 9 (`name_present` beachhead: mkdir/access ensures referencing the shared predicate WALL on the `_dir_lookup` scan; the scan-reflects-present lemma is inductive over `range(16)`)

**Loop:** `config/skills/pycsl-stdlib-coverage` — Step 5 / Step 5b.
**Predecessors:**
- `11-0605-convergence-gap-7.md` (§A: os namespace consequences are Unknown through the public API because the syscall contracts are return-code-only; the prescribed fix is a shared `name_present`/`present` view a mutator establishes and an observer reflects).
- `11-0632-convergence-gap-8.md` (the contract-referenced `#@ inductive` predicate was DROPPED across the `from pure_lib.os import …` boundary — a tool gap). **gap-8 is now FIXED** (commit 594e42a; verified end-to-end by corpus driver `test-suite/corpus/pycsl-reference/0703.py` + `multi_file_lib/inductive_fs.py`): a contract-referenced module-level `#@ inductive` predicate now crosses the import boundary as a real `inductive … string = …` logic block. So the predicate-in-contracts approach is viable end-to-end at the *type/emission* level.
**Iteration:** N = 9.

## What was attempted (the beachhead)

Per gap-7's prescription, added to `pure_lib/os/__init__.py`:

1. A module-level inductive LOGIC predicate (the abstract "root dir has a live entry for `name` resolving to a valid inode" — the logic form of `_filesystem._dir_lookup(5, name) >= 0`):
   ```python
   #@ inductive name_present(name: str):
   #@     name_present_intro: \forall n: str; name_present(n) ==> name_present(n)
   ```
2. Post-state `ensures` referencing it on the beachhead syscalls:
   - `mkdir` (`__init__.py`, the `mkdir` wrapper):   `#@ ensures \result == 0 ==> name_present(filepath)`
   - `access` (`__init__.py`, the `access` wrapper): `#@ ensures (\result == 1) <==> name_present(filepath)`

This EMITS cleanly and TYPE-CHECKS (L3-tc ✓): the predicate lowers to a real WhyML logic block
```
inductive name_present string =
  | Name_present_intro : (forall n : string. ((name_present n) -> (name_present n)))
```
and the two `ensures` lower to logic applications `(name_present filepath)` in postcondition position (confirmed in the emitted `pure_lib/os/__init__.mlw`, lines 79–80, 354, 930). gap-8 is genuinely closed: the boundary is no longer the obstacle.

## Where it WALLED (the SMT/inductive wall, precisely pinned)

Running the full os proof with the two new ensures, **exactly 3 goals flip Valid→Timeout** (30 s, Alt-Ergo + Z3); every other VC stays Valid:

| Goal | mlw line | Postcondition | Result |
|------|----------|---------------|--------|
| `access'vc` Postcondition | `__init__.mlw:354` | `(result = 1) <-> (name_present filepath)` | **Timeout** (30 s, ~14.6M steps) |
| `mkdir'vc` Postcondition  | `__init__.mlw:930` | `(result = 0) -> (name_present filepath)`  | **Timeout** (30 s, ~11.6M steps) |
| (companion sub-goal of the same access/mkdir split) | — | same family | **Timeout** (30 s, ~18.8M steps) |

(The baseline without the ensures is `[+] Verification SUCCESS! All contracts formally proven.` — 1804/0.)

### Root cause — two layers, the second is the real (inductive) wall

**Layer 1 (the proximate cause in the `__init__.py` wrappers).** The wrappers delegate:
`access`'s body is `r := _filesystem_sys_access_2 filepath mode; …` and `mkdir`'s body is `_filesystem_sys_mkdir filepath mode`. In the emitted importer view those `_filesystem_sys_*` symbols are **contractless `val`s** — e.g. `val _filesystem_sys_access_2 (x0: string) (x1: int) : int` (`__init__.mlw:47`), no `ensures` at all. So the wrapper's body knows NOTHING about the relationship between the returned code and `name_present`, and `(result = 1) <-> name_present filepath` is unconstrained → Timeout. This layer alone could be narrowed by giving the `sys_*` syscall contracts (in `UnixInodeFileSystem.py`) a `name_present` ensures and letting it propagate. But that just pushes the obligation down to —

**Layer 2 (the irreducible inductive wall — the lemma).** `UnixInodeFileSystem.sys_access` (`UnixInodeFileSystem.py:1426`) is `inode_num = self._dir_lookup(5, pathname); return 0 if inode_num >= 0 else -1`. So `access(d) == 1  ⇔  sys_access(d) == 0  ⇔  _dir_lookup(5, d) >= 0`. To discharge `(\result == 1) <==> name_present(d)` we must prove

> `_dir_lookup(5, d) >= 0   ⇔   name_present(d)`

`_dir_lookup` (`UnixInodeFileSystem.py:713–726`) is a **linear SCAN over `range(16)`** directory slots:
```python
found = -1
#@ loop invariant 0 <= i and i <= 16
#@ loop invariant found == -1 or (found >= 0 and found < 32)
#@ loop variant 16 - i
for i in range(16):
    entry = self.disk[off + i*32 : off + i*32 + 32]
    inode_num, name_bytes = _unpack_direntry(entry)
    name = name_bytes.split(b'\x00')[0].decode('utf-8', errors='ignore')
    if name == pathname and inode_num != 0 and inode_num < 32:
        found = inode_num
return found
```
Proving "the scan returns a value `>= 0` IFF some live slot decodes to `pathname`" is an **inductive property over the loop**: the scan accumulates a disjunction over the 16 slots, and `name_present(d)` is the existential "∃ slot `k < 16` whose decoded name is `d` and whose inode is live". SMT (Alt-Ergo/Z3) cannot synthesize the loop induction that connects the running `found` to that existential — it times out (the 14.6M/11.6M/18.8M-step blowups above). This is the `dirent_scan_reflects_present` lemma flagged in gap-7/gap-8. It is the SAME class of wall as the existing cited bitmap axiom (`UnixFs.Bitmap.bit_and_one_in_zero_one`, Z3 3.4B-step blowup → 0-step axiom citation) and the variable-length name-decode loop wall already documented at `UnixInodeFileSystem.py:247–254`.

Per the user's standing rule (an SMT wall on a loop/inductive property is closed with a cross-validated Rocq + Lean axiom — skill Step 5b), this is closed by registering the lemma below and citing it with `#@ proof rocq|lean <qualname>` on `sys_access` (and the dual on `sys_mkdir`).

## Why option (a) was NOT viable, and os was REVERTED (option (b))

The task offered (a) guard the new ensures behind `#@ proof rocq/lean <qualname>` referencing the lemma the gap names, so os stays green with the axiom assumed. **This is impossible from the model side today**, because the axiom registry lives in `src/pycsl/module6_whyml/preamble.py` (which the stdlib-agent must NOT edit), and an unregistered qualname is a HARD ERROR, not a silently-assumed axiom:

- `src/pycsl/module6_whyml/preamble.py:578–585` — if a cited `#@ proof` qualname is not in `_AXIOM_REGISTRY`, the emitter raises (`#@ proof {qn}: not in Module6 axiom registry`) and HALTS. Verified empirically: a one-function file citing `#@ proof rocq UnixFs.Dir.scan_reflects_present` aborts the pipeline before any proof runs.

So citing the not-yet-registered `UnixFs.Dir.scan_reflects_present` would make `pure_lib/os/__init__.py` fail to EMIT at all — strictly worse than green. Therefore, per the task's fallback (b), the syscall `ensures` and the `name_present` predicate were **REVERTED**. `pure_lib/os/__init__.py` is now byte-identical to HEAD (verified: `git diff --stat` empty), and os re-proves at **1804/0 green**. The formal test `pure_lib_test/formal_os_namespace.py` therefore remains Unknown on its seven consequences — the correct documented convergence outcome (a documented Unknown, not a simulated green) — BLOCKED ON THE LEMMA below.

## §Lemma — the EXACT statement the next tool-agent must register

**Proposed registry qualname:** `UnixFs.Dir.scan_reflects_present`
(registered in `src/pycsl/module6_whyml/preamble.py` `_AXIOM_REGISTRY`, with the supporting declarations in `_AXIOM_FUNCTIONS` under prefix `UnixFs.Dir.`).

**Informal statement.** The bounded directory scan `_dir_lookup(blk, name)` returns a non-negative inode IFF the directory block `blk` contains a live slot whose decoded name equals `name`. Equivalently, the scan REFLECTS the abstract predicate `name_present`.

**Abstract predicate it reflects.** `name_present(name)` is the existential over the 16 slots of the ROOT directory block (block 5 in this model):
```
name_present(name)  ≜  ∃ k. 0 <= k < 16
                         ∧  let (ino, nm) = decode_slot(disk, 5, k) in
                            ino <> 0  ∧  ino < 32  ∧  nm = name
```
where `decode_slot(disk, blk, k)` is the model's per-slot decode: read the 32 bytes at `blk*512 + k*32`, `_unpack_direntry` → `(inode_num, name_bytes)`, then `name_bytes.split(b'\x00')[0].decode(...)`. (In the FAITHFUL string view this decode is the proven name-codec `_decode_name`/`_encode_name` round-trip, `UnixInodeFileSystem.py:258–292`; only its accumulation OVER the slot loop is inductive.)

**Precise universally-quantified WhyML statement (the axiom body to register).** Let `slot_inode disk blk k : int` and `slot_name disk blk k : string` be the (logic) per-slot decode functions (the `val function` companions emitted for `UnixFs.Dir.`), and `dir_lookup disk blk name : int` the logic model of the scan result. Then:

```
(* UnixFs.Dir.scan_reflects_present — cross-validated Rocq + Lean *)
forall disk : array int. forall blk : int. forall name : string.
  ( dir_lookup disk blk name >= 0 )
  <->
  ( exists k : int. 0 <= k < 16
      /\ slot_inode disk blk k <> 0
      /\ slot_inode disk blk k < 32
      /\ slot_name disk blk k = name )
```

with `name_present name` defined (in the os model, block fixed to the root block 5) as the right-hand existential:
```
name_present name  =  exists k : int. 0 <= k < 16
                        /\ slot_inode disk 5 k <> 0
                        /\ slot_inode disk 5 k < 32
                        /\ slot_name disk 5 k = name
```
so the lemma directly yields `dir_lookup disk 5 name >= 0  <->  name_present name`, hence `access(name) == 1 <-> name_present name` and (after `sys_mkdir` establishes the witness slot) `mkdir(name) == 0 -> name_present name`.

**The loop it abstracts, and the loop invariant the induction needs.** The lemma is the closed form of `_dir_lookup`'s `for i in range(16)` (`UnixInodeFileSystem.py:719–726`). The inductive loop invariant that the proof assistant carries (and that SMT cannot synthesize) is, at iteration `i`:

```
(* found-reflects-prefix invariant *)
( found >= 0 )
  <->
  ( exists k : int. 0 <= k < i
      /\ slot_inode disk blk k <> 0
      /\ slot_inode disk blk k < 32
      /\ slot_name disk blk k = name )
/\ ( found >= 0 -> found < 32 )
```
i.e. after scanning the first `i` slots, `found >= 0` IFF one of those `i` slots is a live match. At `i = 0` the existential is vacuously false and `found = -1` (base case); the step from `i` to `i+1` is the per-slot `if name == pathname and inode_num != 0 and inode_num < 32: found = inode_num` (inductive case). At `i = 16` the invariant IS the lemma. (Note: `_dir_lookup` keeps the LAST match rather than the first; the IFF is unaffected — existence of a match is what `>= 0` reflects.)

**Rocq proof SKETCH (induction on the slot index `i`).**
```coq
(* model: disk : list Z (or Z -> Z); slot_inode, slot_name : decode at blk*512 + k*32 *)
Definition matches disk blk name k : Prop :=
  slot_inode disk blk k <> 0 /\ slot_inode disk blk k < 32 /\ slot_name disk blk k = name.

(* the running scan as a fixpoint over a prefix length i *)
Fixpoint scan disk blk name (i:nat) (found:Z) : Z :=
  match i with
  | 0 => found
  | S j => let f := scan disk blk name j found in
           if (decide (matches disk blk name j)) then slot_inode disk blk (Z.of_nat j) else f
  end.

Lemma scan_reflects_prefix : forall disk blk name i,
  (scan disk blk name i (-1) >= 0)
  <-> (exists k, (0 <= k < Z.of_nat i)%Z /\ matches disk blk name (k)).
Proof.
  induction i as [| j IH]; intro.
  - (* base: prefix empty -> no witness, scan = -1 *)
    simpl. split; [ lia | intros [k [Hk _]]; lia ].
  - (* step: peel slot j; case-split on (matches … j) *)
    simpl. destruct (decide (matches disk blk name j)) as [Hm | Hnm].
    + (* a live match at j -> scan >= 0, witness k=j *) split; eauto; ... 
    + (* no match at j -> reduce to IH on prefix j *) rewrite IH; split; ...
        (* the witness for [0, j+1) is either in [0,j) (IH) or k=j (excluded by Hnm) *)
Qed.

(* the registered axiom is scan_reflects_prefix at i = 16 (the directory width),
   with dir_lookup disk blk name := scan disk blk name 16 (-1). *)
Theorem scan_reflects_present : forall disk blk name,
  (dir_lookup disk blk name >= 0)
  <-> (exists k, (0 <= k < 16)%Z /\ matches disk blk name k).
Proof. intros; apply (scan_reflects_prefix disk blk name 16). Qed.
```

**Lean 4 proof SKETCH (the cross-validation twin — same induction on `i`).**
```lean
def matches (disk : Array Int) (blk name : ...) (k : Nat) : Prop :=
  slotInode disk blk k ≠ 0 ∧ slotInode disk blk k < 32 ∧ slotName disk blk k = name

def scan (disk) (blk name) : Nat → Int → Int
  | 0,     found => found
  | (j+1), found =>
      let f := scan disk blk name j found
      if matchesDec disk blk name j then slotInode disk blk j else f

theorem scan_reflects_prefix (disk blk name) :
    ∀ i, (scan disk blk name i (-1) ≥ 0)
         ↔ (∃ k, k < i ∧ matches disk blk name k) := by
  intro i; induction i with
  | zero      => simp [scan]   -- no witness in the empty prefix
  | succ j ih =>
      simp only [scan]
      by_cases h : matchesDec disk blk name j
      · -- live match at j: ⟨j, …⟩ is the witness
        constructor <;> intro _ <;> exact ⟨j, by omega, …⟩
      · -- no match at j: reduce to ih on prefix j
        rw [ih]; constructor <;> rintro ⟨k, hk, hm⟩ <;> exact ⟨k, by omega, hm⟩

theorem scan_reflects_present (disk blk name) :
    (dirLookup disk blk name ≥ 0) ↔ (∃ k, k < 16 ∧ matches disk blk name k) :=
  scan_reflects_prefix disk blk name 16
```

Both sides prove by induction on the prefix length with a per-slot case split — exactly the step the SMT backend cannot synthesize, which is why it is sourced from the proof assistants and imported as a Why3 preamble axiom (the family discipline: `csl-philosophy`, and the worked precedent `UnixFs.Bitmap.bit_and_one_in_zero_one` at `preamble.py:77`).

## Closing instructions for the next TOOL-AGENT (src/pycsl side)

1. Register `UnixFs.Dir.scan_reflects_present` in `_AXIOM_REGISTRY` (`src/pycsl/module6_whyml/preamble.py`) with the §Lemma body, and add the `slot_inode`/`slot_name`/`dir_lookup` `val function` declarations under `_AXIOM_FUNCTIONS["UnixFs.Dir."]` (mirroring the `UnixFs.Struct.*` precedent at `preamble.py:141–160`). Ship the cross-validated witness `.v` + `.lean` (the §sketches completed) under the os proofs tree and wire the cross-check manifest.
2. Re-apply the model side (this gap's reverted edits): the `#@ inductive name_present` predicate in `pure_lib/os/__init__.py`, the `mkdir`/`access` ensures, AND a `name_present` ensures on `UnixInodeFileSystem.sys_mkdir`/`sys_access` cited with `#@ proof rocq|lean UnixFs.Dir.scan_reflects_present`, so the wrapper ensures propagate from the cited syscalls.
3. Re-prove os (expect 1804+/0 green with the citation discharging the access/mkdir postconditions in 0 steps), then re-prove `pure_lib_test/formal_os_namespace.py` — its `mkdir_then_access_present` (and `file_present_after_mkdir`) consequence should flip **Unknown → Valid THROUGH THE PUBLIC API**, the convergence fixed point for the namespace beachhead. The rmdir/unlink/link/rename consequences follow once the dual "establishes-absence/presence" ensures are added on those syscalls (out of scope here — beachhead is mkdir + access).
