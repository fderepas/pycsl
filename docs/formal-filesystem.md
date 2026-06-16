# Formally modelling a Python OS with Hoare logic

**What this is.** A methodology: how a real operating-system subsystem can be re-expressed in pure
Python and then **proved correct by Hoare logic** — annotated Python → WhyML → Why3 → SMT — with the
proof obligations discharged mechanically. The worked example throughout is Python's `os` module,
realised as a Unix inode filesystem in `pure_lib/os/`. The emphasis is on *how it is done now* and *why
each step has the form it does* — the spirit, from the source of truth down to a formal test that proves
an end-to-end property for all inputs.

The chain is a descent and then a return: **English specification → faithful pure-Python model →
concrete tests → leaf-to-API contracts proved by SMT → a formal test that closes the loop back to the
specification.** Each link is faithful to the one above it; the last link states, as a runnable driver,
the property the first link promised, and proves it universally.

[Novel version of this page](filesystem-story.md)

---

## 0. The pipeline, named precisely

So the verbs below are exact: a function and its `#@` contracts are transpiled to **WhyML** (the input
language of the **Why3** platform); Why3 computes **verification conditions (VCs)** by a
**weakest-precondition calculus** — first-order formulas whose validity means *this body satisfies its
postcondition, calls each callee within that callee's precondition, preserves every loop invariant and
class invariant, and accesses every array in bounds*; the VCs are dispatched to **SMT solvers**
(Alt-Ergo 2.6.2, Z3 4.13.3) under a per-goal time limit. A goal is **Valid** when a solver shows its
negation unsatisfiable. "Proved" means *every* VC came back Valid. No proof-assistant kernel runs during
this; Rocq/Lean appear only offline, to justify a small, audited set of cited axioms.

---

## 1. The source of truth — the English specification

The authority is the **POSIX / Unix specification** (`open`, `read`, `write`, `mkdir`, `unlink`,
`link`, `symlink`, … — the Open Group base specifications). Every function in the model is anchored to
its specification text: what it returns, which errors it produces, what it changes on disk. In the
source these anchors are explicit — each syscall carries a `# cite:` line to its POSIX page and a
`# cite:_note:` paraphrase of the contract (e.g. *"`mkdir()` — allocates inode+block, seeds `.` and
`..`, links the dir into the root; `-1` on EEXIST or ENFILE/ENOSPC"*).

**The spirit.** The specification is the ground truth, and it is written in English. Formalisation does
not *replace* it; it makes a faithful, mechanically-checkable shadow of it. Everything downstream is
answerable to this text, and the citations keep the answer auditable — a reader can trace any contract
back to the sentence in POSIX it encodes.

## 2. Re-implement faithfully in pure Python

The subsystem is rebuilt as **ordinary Python** with no C, no real kernel, no actual syscalls
(`pure_lib/os/`). This is a *simulation* the verifier can reason about — but the point is fidelity, not
convenience: the model implements the **real semantics**, not a comfortable abstraction of them. A file
is bytes on a disk; an inode is a packed byte record; a directory is a block of entries; a descriptor
is a row in a table. Where Python's real `os` would trap into the kernel, the model does the work the
kernel would do, in data structures it owns.

**The spirit.** Faithfulness over expedience. If the real thing manipulates bytes, the model
manipulates bytes — because the proof should be about what actually happens, not about a tidied-up
story. The discipline that makes this pay off is refusing shortcuts: a packer that genuinely rejects
out-of-range input keeps that partiality in its contract rather than pretending to be total; a value is
modelled as its real type (a string as a string, a byte buffer as an array of bytes) rather than
coerced to an integer for ease. Every such shortcut declined is a place the proof stays honest.

## 3. The concrete data model — `os/UnixInodeFileSystem.py`

The heart of the model is a real on-disk layout, held in one array:

- a **`disk`** of 131072 bytes (256 × 512-byte blocks);
- the **inode region** `[512, 2560)` — 32 inodes of 64 bytes each;
- a **block bitmap** in the low blocks; the **root directory** in block 5; **data blocks** from block 6;
- the **open-file table** as parallel `array int` columns indexed by descriptor (`fd_open`,
  `fd_inode`, `fd_offset`, `fd_flags`, and an in-core `fd_block` cache — the analogue of the kernel's
  in-core file table).

Bridging the typed world (an inode is 18 integer fields: size, link count, type, mode, uid, gid,
atimes, ten data-block pointers) and the byte world (64 packed bytes on disk) is a **codec**: byte
leaves `_pack_uint16_be` / `_pack_uint32_be` (and their inverses) compose into `_pack_inode` /
`_unpack_inode`, and `_read_inode` / `_write_inode` move an inode between the typed form and the disk
region. A directory entry has the same shape (`_pack_direntry`).

**The spirit.** A filesystem *is* a byte layout under an interpretation. Modelling the bytes — and the
exact codec between bytes and fields — means the eventual theorem is about the genuine representation: a
file's data really lives in a block whose number is really stored, big-endian, in its inode's bytes. The
model earns the right to claim correctness because it does not abstract that representation away.

## 4. Test the Python — concretely — before proving anything

Before a single contract is written, the model is **run**: concrete drivers (e.g. the os round-trip
and siblings) create a file, write known bytes, close, reopen, read, and check the result with ordinary
assertions on concrete values. This is plain Python execution, not verification.

**The spirit.** A model you cannot run is a model you cannot trust. Concrete testing is the cheap filter
that catches *modelling* mistakes — a wrong offset, an off-by-one in the layout, a codec that does not
round-trip — long before the expensive machinery of proof is brought to bear. Proof tells you the model
meets its contracts; testing tells you the model is the right model. You want both, and you want the
cheap one first. (The formal test in §6 is the counterpart of exactly these concrete drivers, with the
concrete inputs replaced by symbolic ones — so the concrete test is also the rehearsal for the proof.)

## 5. Annotate formally — from the leaves up to the API

Now the contracts. PyCSL annotations (`#@ requires` / `ensures` / `assigns`, `#@ class invariant`,
`#@ loop invariant` / `loop variant`) are added **bottom-up**, because a caller's proof should rest on
its callees' *proven contracts*, never on re-deriving their bodies:

1. **Leaves.** The byte codecs get exact value contracts:
   `_pack_uint16_be` *ensures* `\result[0]*256 + \result[1] == v` and each result byte in `[0,255]`;
   `_unpack_uint16_be` *ensures* the inverse. These prove directly against their tiny bodies.
2. **Compose.** `_pack_inode` / `_unpack_inode` carry per-field value contracts that **compose** from
   the leaves' contracts — the inode round-trip `unpack(pack(fields)) == fields` then holds *by
   composition*, no axiom. (The repetitive byte- and field-range clauses are written once with the
   `#@ for i in range(lo, hi):` expansion sugar, which desugars to the same ground clauses — see
   `sugar-for-spec.md`.)
3. **Climb.** `_read_inode` / `_write_inode` (with a read-after-write contract: a persisted inode's
   block and size are recoverable), the disk helpers (`_alloc_block`, `_dir_lookup`, `_write_entry`, …
   each given a *narrow* contract — its return-code range and the invariants it preserves), then the
   syscalls (`sys_open`, `sys_write`, `sys_read`, `sys_mkdir`, …), then the module-level `os.*` API.
4. **The class invariant** — `\length(disk) >= 131072`, the fd-column lengths, a region byte-invariant
   on the inode bytes — is carried by *every* method, so each one both assumes and re-establishes the
   filesystem's structural well-formedness.

Why3 turns all of this into weakest-precondition VCs and Alt-Ergo/Z3 discharge them. The result for
`os`: **every contract Valid — 0 unproven goals** — with a trusted base of a single cross-validated
axiom (a bitwise bound). The large syscalls reuse their helpers' contracts (often via `#@ no_inline`, so
a syscall is verified once and its wrappers reuse the contract rather than re-proving the inlined body),
which is what keeps a fifty-function module tractable.

**The spirit.** *Leaf-first, compose-don't-re-derive.* You prove the bottom of the tower and let each
higher layer stand on the proven contracts beneath it. This is also where faithfulness is paid for: the
contracts say what the code really does (a write changes exactly these bytes; an `open` returns a
well-formed descriptor or `-1`), and the SMT solver refuses anything weaker. The output is a precise
trust boundary — what is proved (almost everything) and what is assumed (one audited axiom) is explicit.

## 6. The capstone — a formal test that exercises the whole API

The final, decisive artifact is a **formal test**: a Python function that drives the public API through
a complete scenario and states the end-to-end property as its **postcondition** — but over **symbolic**
inputs. Where the concrete test of §4 used `"testfile"` and `[72, 101, …]`, the formal test takes an
arbitrary filename `f` and an arbitrary buffer, bounded only by `#@ requires`, and asserts the property
with `#@ ensures`. Because Why3/SMT discharges that postcondition, a *Valid* verdict means the property
holds for **every** input in range — not for the handful a concrete test could sample.

The existing example is `pure_lib_test/formal_os_roundtrip.py`: open-create, write a symbolic buffer, close,
reopen, read it back, over all filenames and buffers up to the modelled sizes (`\length(data)` in
`[1, 512]`) — proved end-to-end with no `\trusted`. Its postcondition is `\result == 0 or \result == 1`:
the scenario runs to a *well-formed* result on every symbolic input — a **totality / safety** property
(no out-of-bounds access, no contract violation, no stuck state, for all filenames and buffers). The
*deepest* form of this test is the **content round-trip** — *write `c`, read it back, **value == `c`***
(`formal_os_content.py`, `#@ ensures \result == True`, the on-fd `write→pread == c` form — PROVEN via
the folded `block_content_eq` atom; the full create→close→reopen-by-name form remains the frontier):
a single theorem that the filesystem genuinely stores and returns a file's content by name. Reaching it
requires exactly the foundation built in §3–§5 (the inode round-trip available as a proven contract, the
block recoverable across a reopen); it is the functional-correctness frontier the same methodology
targets, distinct from the safety/structural correctness already established.

**The spirit.** The formal test is the **return to the source of truth.** The POSIX specification
promises, in English, that a file round-trips; the formal test writes that promise as a runnable driver
and the verifier proves it for all inputs at once. The concrete test (§4) and the formal test (§6) are
the same scenario — that is deliberate: the thing you ran to convince yourself the model is right is the
thing you now prove holds universally. A proved formal test is the strongest statement the whole edifice
can make: *not "it worked on these examples" but "it works on every input the contract admits."*

---

## What this establishes

For `os`: a pure-Python Unix inode filesystem whose every contract is mechanically proved (0 unproven
goals) — array accesses in bounds, the on-disk layout invariant preserved, every syscall returning a
well-formed result faithful to POSIX — resting on a single cross-validated axiom, with formal tests
exercising the API over symbolic inputs. Safety and structural correctness are done; functional content
correctness is the active frontier, reachable on the same foundation.

The method is not specific to filesystems or to Python: any subsystem with an English specification can
be re-expressed faithfully in a host language, tested concretely, annotated leaf-to-API, and crowned
with a formal test that proves its end-to-end property universally. That is the claim — and `os` is the
demonstration that it is now practical.

## The spirit, in one line

**Start from the English truth; model it faithfully; run it to know it is right; prove it leaf-to-API to
know it is safe; then write a formal test that re-states the English promise and proves it for every
input — closing the loop from specification to mechanically-checked theorem.**
