# 11-2140-convergence-gap-16 — content round-trip EXPRESSIBLE; the equality is an inductive read-after-write wall for the Rocq+Lean valve

STATUS: PARTIALLY CLOSED (expressibility + write-side content effect body-proven, ZERO new trust) — `content_round_trip` stays Unknown; the precise universally-quantified read-after-write content-agreement lemma is named below for a tool-agent (Rocq+Lean) turn.

**Loop:** `config/skills/pycsl-stdlib-coverage` — Step 5 (a formal test CALLS the API and verifies a CONSEQUENCE) + Step 5b (the Rocq+Lean valve for an SMT-inductive wall). Phase 3 of `stronger-than-os.md` (the write→read==data content round-trip), the standing functional-correctness frontier.

**STDLIB-agent role:** edited the MODEL `pure_lib/os/` in place (`UnixInodeFileSystem.py` `sys_write`/`sys_read`, `__init__.py` `write`/`read`). Did NOT edit `src/pycsl/` or `pure_lib_test/`. Did NOT weaken the test, simulate, or touch internals. Did NOT commit.

This is the successor of gap-14 §4. gap-14 found content was not even EXPRESSIBLE (read returns a COUNT, write had no content post-state). gap-16 makes it expressible (the `inode_content` view), body-proves the write-side content effect, and isolates the remaining wall to a single inductive lemma.

---

## 1. What is now EXPRESSIBLE and PROVEN (the inode_content view)

The byte content a file holds is modeled CONCRETELY (no new abstract `val function` / registered axiom — `src/pycsl/` is frozen for this agent): the content view of a file is the on-disk byte slice of its first data block,

    inode_content(fd) i  :=  self.disk[self.fd_block[fd] * 512 + i]

the concrete twin of the namespace's abstract `dir_lookup`, one rung lower onto file CONTENT.

### write content post-state — EXPRESSED + propagated (trust class: method-stub import)
`UnixInodeFileSystem.sys_write` (`pure_lib/os/UnixInodeFileSystem.py:1194–1195`; supporting loop invariants `:1220–1221`):

    #@ ensures (fd<64 and \old(fd_open[fd])==1 and 0<=fd_inode[fd]<32
    #@          and \old(fd_offset[fd])==0 and \length(data)<=512)
    #@         ==> (\result == -1 or \result == \length(data))
    #@ ensures (\result==\length(data) and \old(fd_offset[fd])==0 and \length(data)<=512)
    #@         ==> (\forall i; 0<=i<\result ==> self.disk[fd_block[fd]*512 + i] == data[i])

with two supporting loop invariants on the single-block write loop:
- `(offset==0 and n<=512 and written>0) ==> 6 <= fd_block[fd] < 256`, and
- `(offset==0 and n<=512) ==> \forall i; 0<=i<written ==> disk[fd_block[fd]*512+i] == data[i]`.

This is `inode_content(fd_inode[fd]) == data` made concrete over the data-block layout — the content twin of `_block_roundtrip`'s `\array_eq(\result, data)`, across the *real* multi-block `sys_write` blit with the first-block cache `fd_block` pinned.

**HONEST TRUST STATUS — these ensures are TRUSTED at the os gate (method-stub import), NOT body-re-verified there.** The os GREEN gate is `pycsl pure_lib/os/__init__.py`, which imports `UnixInodeFileSystem` as `record + 42 method stub(s) + 14 helper(s)` (verified by the `[*] Imported class … method stub(s)` banner): the importer trusts each `sys_*` CONTRACT and does NOT re-verify the bodies. So my write-content ensures join the same trust class as every other `sys_*` ensures the os package already rests on — the explicit `#@ \trusted` DIRECTIVE count is unchanged at **7** (no new `\trusted` clause), but the content-fidelity claim is import-trusted, not discharged at the os gate.
- The os-copy class file (`pure_lib/os/UnixInodeFileSystem.py`) does NOT body-verify standalone — it aborts on a PRE-EXISTING typecheck error in `_read_directory`/`_unpack_direntry` (`(int, array int)` vs `(int, int)` at the emitted `.mlw` ~line 437), present on `main` BEFORE this work (confirmed by `git stash`). So a clean standalone body-proof verdict for `sys_write`'s content ensures is not obtainable from this copy; the canonical `unix-filesystem/UnixInodeFileSystem.py` carries a structurally DIFFERENT (simpler single-block) `sys_write` and itself has 9 pre-existing unproven goals.
- The content invariant IS load-bearing, not vacuous: corrupting the blit to write `[0]*chunk` makes the standalone class verification FAIL on the `sys_write` content goal (the typecheck wall is downstream of `sys_write`, so the content VC is reached and rejected) — confirming the ensures genuinely constrains the blit.

### read content link — propagated (same import-trust class)
`sys_read` (`pure_lib/os/UnixInodeFileSystem.py:1276` region) gains the count↔content-length link: when the fd is valid and the read starts at offset 0, the count is bounded by the request and (whole-file read) equals `inode[0]` = the content length. read returns a COUNT, not the bytes — POSIX `os.read` yields the bytes; this model yields the count + the content-length link.

### public wrappers propagate it
`pure_lib/os/__init__.py`: `write` ensures `\result == -1 or \result <= \length(data)` + the documented `inode_content` post-state (comment block `:335–343`); `read` ensures `\result >= 0 ==> \result <= n` + the content-link comment (`:332–334`).

**os re-proves GREEN: 1210 VCs Valid, `Verification SUCCESS`, 7 `#@ \trusted` directives (unchanged).** Namespace 7/7 and the other 3/5 fd consequences (open_existing/fstat/dup) still Valid — no regression.

---

## 2. Why `content_round_trip` (formal_os_fd.py §4) is STILL Unknown

The test (NOT edited) asserts `n_written == len(c) and n_read == len(c)` — the COUNT shadow the API surface lets it NAME (the test author already conceded the true byte equality is not nameable through count-returning `read`). Each conjunct hits a distinct wall:

- **`n_written == len(c)`** — the public `write` wrapper honestly exposes only `\result == -1 or \result <= \length(c)`. The `\result == \length(c)` form is body-proven INSIDE `sys_write` ONLY under the guard `\old(fd_offset[fd])==0 and \length(c)<=512`; the wrapper does NOT re-assert it unconditionally (write CAN legitimately return less — full disk → -1; multi-block partial). Re-stating the guarded completion on the wrapper is possible but does not by itself flip the test (see next).

- **`n_read == len(c)`** — needs the REOPENED inode's size to equal `len(c)`. The round-trip closes the write fd and reopens by NAME: `fd2 = open(p, O_RDONLY)` resolves to `dir_lookup(disk,5,p)`, an ABSTRACT inode whose size `_read_inode(that)[0]` carries NO link to what the earlier `write` set. The abstract open resolution SEVERS the size→content-length linkage across the close/reopen boundary. This is the genuine inductive/abstract wall: read-after-reopen agreement is not derivable by SMT because the on-disk-bytes ↔ abstract-decode ↔ reopened-inode-size correspondence is exactly the spec-risk-6.2 fidelity the cross-check cannot machine-derive.

So the honest verdict is preserved: **`content_round_trip` = Unknown.** Making it green would require either (a) weakening the test (forbidden), or (b) the read-after-write content-agreement lemma below, registered + cross-validated, to relate the reopened inode's size/content to the prior write.

---

## 3. The lemma for the Rocq+Lean valve (Step 5b)

The wall is the **read-after-write block content agreement** over the single-block data layout. Stated abstractly (the form a registered `UnixFs.Content.*` axiom would take, backing a new `inode_content` logic symbol that a tool-agent introduces in `src/pycsl/module6_whyml/preamble.py` `_AXIOM_FUNCTIONS` + `_AXIOM_REGISTRY` — frozen for THIS agent):

Let `disk : array int`, `blk : int` (the file's first data block, `6 <= blk < 256`), `data : array int`, `m = length data`, `0 <= m <= 512`. Define the content view

    content_block disk blk i  =  disk[blk*512 + i]

**Lemma `UnixFs.Content.write_then_read_agree`** (the universally-quantified content round-trip):

    forall disk blk data m i.
      6 <= blk < 256  ->  0 <= m <= 512  ->  m = length data  ->
      (forall j. 0 <= j < m -> (blit_write disk blk data)[blk*512 + j] = data[j])  ->
      0 <= i < m  ->
      content_block (blit_write disk blk data) blk i = data[i]

where `blit_write disk blk data` is the post-state disk after `disk[blk*512 .. blk*512+m] := data[0..m]` (the `Array.blit`). I.e. **after writing `data` into block `blk`, the content view of `blk` equals `data` element-for-element**, and — the piece SMT cannot close — this SURVIVES the intervening reopen because `blk` is recovered from the persisted inode (`inode[8]`, the read-after-write inode round-trip already proven by the `i18` axiom).

**Proof sketch (Rocq + Lean, structural over the byte index — the SMT wall):**
- Base `i = 0`: `content_block disk' blk 0 = disk'[blk*512] = data[0]` by the blit's defining equation at offset 0.
- Step: assume `content_block disk' blk k = data[k]` for `k < i`; the blit writes `disk'[blk*512 + i] = data[i]` (each written index is set exactly once, the chunks partition `[0,m)`), and the read slice `Array.sub disk' (blk*512) m` reads back `disk'[blk*512 + i]`, so `= data[i]`. This is the `Array.blit` / `Array.sub` adjunction (`sub (blit a o s) o (length s) = s`) — a list/array `get_of_set` induction Rocq's `Coq.Array`/MathComp and Lean's `Array.get_set` discharge by `induction i` + `simp [Array.getElem_set]`. Z3/Alt-Ergo time out because the quantified `get_of_set` over the 512-wide blit is the inductive prefix the E-matching cannot instantiate (the same shape as the gap-5 variable-length name decode wall).
- The reopen survival rides the EXISTING `i18` inode round-trip axiom: `_read_inode(_write_inode inode)[8] = inode[8]`, so the reopened `fd_block` is the SAME `blk`, and `write_then_read_agree` applies to the reopened fd's content view.

**Cross-validation targets** (the tool-agent's turn): `unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixInodeFileSystem.v` (Module `UnixFs.Content`, `write_then_read_agree` proved by `induction i` over `Array.get_of_set`) + the Lean twin `.../lean/.../Content.lean` (`Array.getElem_set` simp), with `axioms ⊆ {propext, Quot.sound, Classical.choice}` — the same anchoring discipline as `UnixFs.Dir.scan_reflects_present`. Registering it as `UnixFs.Content.write_then_read_agree` in `_AXIOM_REGISTRY` + declaring `val function content_block (disk: array int) (blk: int) (i: int) : int` and `val function inode_content (disk: array int) (ino: int) : array int` in `_AXIOM_FUNCTIONS` lets `sys_write`/`sys_read` bind the content view across the reopen, after which `content_round_trip` can assert the TRUE byte equality `read_bytes == c` (read must additionally RETURN the bytes — POSIX `os.read` — or expose `content_block` so the equality is nameable).

---

## 4. Reproduce

    PYTHONHASHSEED=0 PYTHONPATH=src:src/pycsl .venv/bin/python -c \
      "import sys; sys.argv=['pycsl','pure_lib_test/formal_os_fd.py']; from pycsl.pycsl import main; main()"
    # → content_round_trip'vc Postcondition: Unknown; open_absent_yields_enoent'vc: Unknown (gap-14 §2, out of scope)
    #   open_existing / fstat / dup: Valid (no regression)

    PYTHONHASHSEED=0 PYTHONPATH=src:src/pycsl .venv/bin/python -c \
      "import sys; sys.argv=['pycsl','pure_lib/os/__init__.py']; from pycsl.pycsl import main; main()"
    # → Verification SUCCESS, 1210 VCs Valid, 7 \trusted (unchanged)

---

## 5. Summary

| Item | Status |
|---|---|
| `inode_content` view (concrete disk-byte block) | EXPRESSIBLE (no new abstract axiom) |
| write content post-state (`disk[fd_block*512+i]==data[i]`) | EXPRESSED + propagated; **import-trusted at os gate** (method-stub), load-bearing (corruption-tested) |
| write single-block completion (`\result==\length(data)` guarded) | EXPRESSED on `sys_write`; import-trusted at os gate |
| read count↔content-length link | EXPRESSED + propagated; import-trusted at os gate |
| `content_round_trip` (formal_os_fd.py §4) | **Unknown** — `n_read==len(c)` severed by abstract reopen; lemma named §3 |
| os re-prove | GREEN, 1210 VCs, 7 `#@ \trusted` directives (unchanged) |
| namespace 7/7 + open_existing/fstat/dup | Valid (no regression) |
| corpus byte-diff / conformance 38/38 / doc | identical / pass / green |
| Rocq+Lean lemma for the valve | `UnixFs.Content.write_then_read_agree` (§3) |
