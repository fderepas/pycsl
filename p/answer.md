# Computed answers to the review's open questions

All numbers below are computed from the working tree with `grep`/`wc`/Python
counting (no estimates). Snapshot date: 2026-06-11. Scope of the `os` model:
`pure_lib/os/*.py` (`UnixInodeFileSystem.py`, `__init__.py`, `codec.py`,
`path.py`). The PyCSL tool is `src/pycsl/`.

---

## 1. LOS : LOC ratio for the `os` model

**Definitions used**
- **LOS** (Lines Of Specification) = lines containing a `#@` contract token
  (`grep -c '#@'`).
- **LOC** (Lines Of Code) = executable Python: non-blank, and not a `#`
  comment line (which excludes every `#@` line, since `#@` lines start with
  `#`). Blank lines and prose comments are excluded from both.

### Per-file

| File | LOS (`#@`) | LOC (exec) | LOS:LOC |
|------|-----------:|-----------:|--------:|
| `UnixInodeFileSystem.py` | 473 | 763 | 0.62 |
| `__init__.py` (public API wrappers) | 157 | 245 | 0.64 |
| `codec.py` | 113 | 120 | 0.94 |
| `path.py` (unannotated string helpers) | 0 | 87 | 0.00 |
| **TOTAL** | **743** | **1215** | **0.61** |

**Headline: LOS:LOC = 743 : 1215 ≈ 0.61 : 1, i.e. about 1 line of
specification for every 1.64 lines of executable code (61% annotation
overhead).**

Note: `path.py` is pure string-manipulation glue carrying no contracts; it
dilutes the ratio. Excluding it, the *annotated* core is 743 : 1128 ≈ 0.66 : 1
(≈ 1:1.52). The codec is the most spec-dense (0.94:1) because it is leaf
value-contract heavy; the FS core and the public wrappers sit near 0.62–0.64:1.

### LOS breakdown by clause kind (across all `pure_lib/os/*.py`)

| Clause | Count |
|--------|------:|
| `ensures` | 278 |
| `requires` | 171 |
| `assigns` | 107 |
| `proof` (Rocq/Lean axiom citations) | 62 |
| `loop invariant` | 24 |
| `no_inline` (modularity markers) | 17 |
| `loop variant` | 14 |
| `class invariant` | 13 |
| `for` (indexed-clause expansion sugar) | 12 |
| `interface` (opacity) | 3 |
| `\trusted` (active reviewer-trust clauses) | 7 |
| `raises` | 1 |
| `assert` (in-body ghost asserts) | 34 |

(Clause-kind counts sum to more than 743 in some groupings only because a few
`#@` lines are continuation/comment lines or carry no leading keyword; the
743 total is the authoritative LOS figure.)

---

## 2. PyCSL tool LoC (`src/pycsl/`)

| Measure | Lines |
|---------|------:|
| Python files | 90 |
| Total lines (`wc -l`) | 39,339 |
| Non-blank lines | 35,330 |
| Non-blank, non-comment (code) lines | 31,245 |

**Headline: the PyCSL verifier is ~39.3 K lines of Python (90 files);
~31.2 K are non-blank, non-comment code.**

---

## 3. Other computed technical details

### 3a. Body-level VC count for `os`
The Lark front-end is not installed in this environment, so the live count
could not be re-run here. The documented convergence trail (the project's own
proof logs) gives the authoritative figures: the `os` module body proves at
**0 unproven goals** with a total VC count that grew as consequence work was
added — **1191 VCs** at the gap-12 checkpoint (`11-1404-convergence-gap-12.md`:
"os GREEN: 1191 VCs, Verification SUCCESS"), rising to **1480** after the
remove/absence axiom family landed (`11-1219-convergence-spec-11.md`), with the
"~1202" figure being the in-flight count around the spec-13 frame work. The
stable claim the paper can make is the qualitative one — **every VC Valid, 0
unproven goals** — with the body-VC count in the **~1200–1480** range depending
on which consequence layer is active. The convergence of the *unproven* count
is documented as 47 → 39 → 23 → 0 (`os_coverage_progress` memory; matched by
the narrative trail "Forty. Twenty-three. Eleven. Three." in
`docs/filesystem-story.md`).

### 3b. Consequences proven THROUGH the public API
- **Namespace chain: 7/7 VALID** (`11-1219-convergence-spec-11.md`:
  "7/7 namespace consequences VALID through the STANDARD public API"). The
  driver is `pure_lib_test/formal_os_namespace.py`, covering
  `mkdir`/`access`/`rmdir`/`unlink`/`link`/`rename` (4 presence + 3 absence
  consequences = 7), each discharged through the imported public wrappers, not
  the internal `sys_*`.
- **fd chain: 3/5 fully VALID at the public API** (as of commit `4ea6d3e`, the
  fstat/dup flip via the gap-15 `<global>.<field>[expr]` grammar). The five
  fd-chain consequences in `pure_lib_test/formal_os_fd.py`:
  1. `open_existing_yields_valid_fd` — **VALID** (≤17 K steps)
  2. `open_absent_yields_enoent` — Unknown (Wall A: pristine-global assumption
     not API-expressible without a setup that absents the path)
  3. `fstat_of_opened_fd_is_valid_inode` — **VALID** (flipped — fstat reports
     `_filesystem.fd_inode[fd]`, body-proven, zero new trust)
  4. `content_round_trip` — Unknown (gap-16: needs the Rocq+Lean
     `UnixFs.Content.write_then_read_agree` array-agreement axiom)
  5. `dup_yields_valid_fd` — **VALID** (flipped — duped fd shares the source
     inode; +1 interim `fd-resolution-fidelity` trust)

  So the *public-API* fd chain is **3/5 VALID** (open/fstat/dup); the remaining
  two (`content_round_trip` + `open_absent`) are the open frontier — **5/5 is
  the target**. (This narrows the "one end-to-end gap remains open" the paper
  discloses in §7.4 to the content round-trip + the absence test-structure wall.)

### 3c. Cross-validated dual-kernel axiom registry (`_AXIOM_REGISTRY`)
Source: `src/pycsl/module6_whyml/preamble.py` (theorem-statement keys, excluding
the separate signature-declaration dictionary), corroborated by
`docs/glossary/axiom-registry.md`. **20 cross-validated axioms total**, each
proved in BOTH Rocq and Lean and cross-checked:

| Family | Axioms | Members |
|--------|------:|---------|
| `UnixFs.Dir` | **6** | `scan_reflects_present`, `slot_inode_nonneg`, `remove_reflects_absent`, `insert_preserves_unique`, `empty_disk_slots_dead`, `block5_decode_frame` |
| `Pycsl.Reference.Gcd` | 7 | `gcd_result_nonneg`, `gcd_result_positive`, `gcd_divides_a`, `gcd_divides_b`, `gcd_0`, `gcd_step`, `gcd_greatest` |
| `UnixFs.Struct` | 3 | `i1a1.round_trip`, `i2.round_trip`, `i18.round_trip` |
| `Pycsl.Reference.Perm` | 2 | `permut_refl`, `rev_permutation` |
| `Pycsl.Reference.Json` | 1 | `mirror_involution` |
| `UnixFs.Bitmap` | 1 | `bit_and_one_in_zero_one` |
| **TOTAL** | **20** | |

The `os` proof's TCB uses the `UnixFs.Dir` (6), `UnixFs.Struct` (codec
round-trip) and `UnixFs.Bitmap` (bitwise) families; `Gcd`/`Perm`/`Json` back
other reference demos. Dual-kernel proof artifacts for the directory family
live in `unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/` — **6 Rocq
`.v` + 6 Lean `.lean`** files, with `.vok`/`.vos` confirming the Rocq kernel
accepted them. Audit tooling: `src/pycsl/audit_proof.py`
(`audit_proof_reverify.py`) checks the closed-Rocq-context condition, the
Lean kernel-axiom budget (⊆ `{propext, Quot.sound}`), and the statement
pairing.

### 3d. Remaining TCB (`\trusted` clauses) in `pure_lib/os/`
**7 active `#@ \trusted` clauses**, all in `UnixInodeFileSystem.py`, in two
human-reviewed trust classes:
- **5 × `dirscan-fidelity`** (lines 827, 879, 909, 961, 998) — the
  decode↔bytes faithfulness of the directory-slot scan/write helpers.
- **2 × `fd-resolution-fidelity`** (lines 1124, 1786) — the fd-table resolution
  helpers.

This is a material correction to the paper's §5.3/§5 claim that "No `\trusted`
escape ... appears anywhere in the verified module." See `p/review2.md`.

### 3e. Conformance / reference corpus size
- `test-suite/corpus/pycsl-reference/`: **661 `.py` drivers** (679 entries
  including proof subdirs). The byte-diff/determinism gates run over the full
  corpus (the convergence logs cite "595/595 byte-diff IDENTICAL",
  "conformance 38 OK / 0 MISMATCH", "determinism 10/10" for the active
  conformance subset).
- `os` formal-test drivers in `pure_lib_test/`: 7 (`formal_os.py`,
  `formal_os_dir.py`, `formal_os_fd.py`, `formal_os_io.py`,
  `formal_os_namecodec.py`, `formal_os_namespace.py`, `formal_os_query.py`),
  plus the broader `formal_*.py` suite of ~110 stdlib formal tests.

### 3f. `os` model size in functions
**118 `def`s** across `pure_lib/os/*.py` (UnixInodeFileSystem 57, `__init__`
public wrappers 43, codec 7, path 11). The paper's "~50 functions" is a fair
characterization of the *core* FS + codec + syscall layer (the verified
nucleus); counting every public wrapper and `path` helper it is ~118.

### 3g. Proof backend (verified versions)
- **SMT**: Alt-Ergo **2.6.2** + Z3 **4.13.3** (defaults in `src/pycsl/pycsl.py`
  `_DEFAULT_PROVERS`; corroborated across `docs/`).
- **WP / VC engine**: Why3 (WhyML, weakest-precondition calculus).
- **Offline cross-validation**: Rocq/Coq **8.20.1** (`pycsl.py` `-P Coq,8.20.1`;
  SerAPI 8.20.0+0.20.0) + Lean **4.30.0** (`preamble.py` audit comments). Neither
  kernel runs at verification time.

---

## Bottom line for the paper

- **LOS:LOC ≈ 0.61:1 (743:1215)** — i.e. about 61% annotation overhead, or
  ~1 spec line per 1.6 code lines. This is the descriptive metric the review
  (final question) asked for and can be dropped straight into §10.
- **PyCSL tool: ~39.3 K LoC Python (31.2 K non-comment), 90 files.**
- The dual-prover registry is **20 cross-validated axioms** (the `UnixFs.Dir`
  family being 6); the `os` public-API consequence status is **namespace 7/7,
  fd chain 3/5 (open/fstat/dup) VALID today, 5/5 targeted** (content-round-trip +
  open-absent remain); the residual TCB is **7 `\trusted` clauses + the cited
  axiom families**.
