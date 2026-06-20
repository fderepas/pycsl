# Faithful-name string-type leak — os `__init__` gate restored GREEN (PROPOSAL)

**Date:** 2026-06-20
**Loop:** test-supervise-sl (dedicated worktree, STOP-AT-PROPOSAL)
**Result:** SUCCESS — os `__init__` gate typechecks (L3-tc ✓) and verifies GREEN (SUCCESS, 0 non-Valid) ×2 deterministic; #53–#55 retirements intact; `\trusted` still 1; no new trust/axiom/val.
**Patch:** `getting-better/PROPOSAL-faithful-name-stringtype-fix.patch`

## BOTTOM LINE
The regression on main (846e4fd) is restored. It had TWO layers — only the first was diagnosed in the mission brief; the second was exposed once the first was fixed:

1. **String-type LEAK (L3-tc RED).** The #53 faithful-name emitter recognizer lowers
   `bytes[a:b].split(b'\x00')[0].decode('utf-8',errors='ignore')` to a `field_to_str …`
   STRING, but in wrapper functions the receiving local was emitted as `ref 0` (int) →
   `"type string, but is expected to have type int"`. Fixed in the emitter.
2. **Aggregate-context proof EXPLOSION (14 non-Valid), hidden behind layer 1.** With the
   type leak fixed, `listdir`/`scandir`/`truncate` now typecheck — and the proof then has
   to discharge `_dir_lookup`'s INLINED `dir_scan_prefix`/`slot_name` asserts in each
   wrapper's full-module aggregate context, where they Timeout/OOM (catalog A.7). Closed by
   marking `_dir_lookup` `#@ no_inline` so wrappers consume its cross-validated
   `\result == dir_lookup(...)` ensures instead of inlining the heavy asserts.

This is therefore MORE INVASIVE than the "pure type fix" the brief anticipated: it is
(type fix) + (one modular-boundary `#@ no_inline`) + (4 faithful source param annotations).
All changes are doctrine-clean and add ZERO trust.

## ROOT CAUSE
- `_dir_lookup` (UnixInodeFileSystem.py:1009) annotates `name: str = …` so its local types
  as string. `listdir`/`scandir`/`truncate` call `_filesystem._dir_lookup(5, filepath)`; the
  importer INLINES the body. The inlined `name` local has NO annotation in the wrapper, so it
  defaulted to `ref 0` (int) while the recognizer assigns a `field_to_str` string → type leak.
- Per-retirement #53–#55 verification used `--fun` body gates (which typecheck only the leaf,
  where `name: str` exists) + corpus byte-diff with `--no-typecheck` (emission only). Neither
  runs the full `__init__` typecheck, so BOTH layers slipped through.
- Layer 2: even string-typed, the inlined `dir_scan_prefix`/`field_to_str` asserts explode in
  the wrapper aggregate context (the os axiom web starves the SMT step budget). `_dir_lookup`
  itself proves fine in `--fun` isolation; the explosion is purely the inlined-into-wrapper case.

## THE FIX (file:line)
1. **Emitter — the string-type leak (the type-only part):**
   - `src/pycsl/module6_whyml/expressions.py:1308` — new `_match_field_decode_idiom(expr)`:
     pure STRUCTURAL matcher of the field-decode idiom (factored out of
     `_recognize_field_decode_idiom`, which now delegates to it at :1400). No emission, so it
     is safe to call during pre-declaration classification. The recognizer's behaviour is
     unchanged (refactor only) — proven by the 0-diff corpus byte sweep.
   - `src/pycsl/module6_whyml/statements.py:1007` — new `_collect_field_decode_str_locals`:
     marks any Assign target whose VALUE matches the idiom as a `str` local (symbol-table +
     `string_vars`), so it is excluded from the integer `ref 0` pre-declaration and let-bound
     as a string ref — exactly the path the explicit `name: str` annotation already takes.
   - `src/pycsl/module6_whyml/statements.py:1109` — wires the collector into `string_vars`.
   Why type-only: it changes the DECLARED TYPE of a local to match the STRING value the
   recognizer already assigns it; it touches no contract, VC, axiom, or trust. Corpus byte-diff
   0/604 (no corpus file uses the idiom).
2. **Source param annotations (faithful — these params ARE paths):** `pure_lib/os/__init__.py`
   `listdir(filepath: str = '.')`, `scandir(filepath: str = '.')`, `truncate(filepath: str, …)`,
   `walk(top: str, …)`. Each forwards a path into a `pathname: str` syscall / `listdir(str)`;
   the unannotated default-`int` type was the second leak (`filepath` used as both string in the
   inlined `dir_scan_prefix` and int in `str_hash_op`). Mirrors `stat(filepath: str)` /
   `lstat(filepath: str)`, already annotated.
3. **Modular boundary (closes the aggregate explosion):** `pure_lib/os/UnixInodeFileSystem.py`
   — `#@ no_inline` on `_dir_lookup`. Wrappers now CALL it (consuming the cross-validated
   `\result == dir_lookup(self.dir, blk, pathname)` + range ensures) rather than inline its
   asserts. Catalog A.6 (`#@ no_inline` boundary with a folded atom). Adds/removes NO trust.
4. **Prevention note:** `config/skills/pycsl-monitoring/SKILL.md` item 15 — per-retirement
   verification MUST include the full `pycsl pure_lib/os/__init__.py` typecheck; `--fun`+byte-diff
   (`--no-typecheck`) hide type errors that only manifest at an inline site.

## EVIDENCE
- **`__init__` gate GREEN ×2 (deterministic):** `PYTHONPATH=$PWD/src:$PWD/src/pycsl
  PYTHONHASHSEED=0 pycsl pure_lib/os/__init__.py` →
  - Run 1: `Verification SUCCESS! All contracts formally proven.` EXIT=0, 195 Valid, 0 non-Valid.
  - Run 2: identical — SUCCESS, EXIT=0, 195 Valid, 0 non-Valid.
  - L3-tc typecheck (`--typecheck --no-proof`) GREEN ×2 (the original `string vs int` error gone).
  - SENTINEL confirmed the edited emitter is loaded (`_match_field_decode_idiom` /
    `_collect_field_decode_str_locals` present; module path = worktree `src`).
- **Before the fix (witnessed this run):** L3-tc RED (`line 717: type string, but is expected to
  have type int`); after the type-only fix alone, full proof = 14 non-Valid (Timeout/OOM
  Assertion goals in `listdir`/`scandir`/`truncate` — the A.7 explosions). The `#@ no_inline`
  closes all 14.
- **#53–#55 retirements intact (`--fun`, complete fix in place):**
  `_dir_lookup` ✓, `_dir_find_slot` ✓, `_dir_find_free` ✓, `_write_dir_entry` ✓,
  `_write_entry` ✓ — all SUCCESS. `_zero_entry` is the pre-existing baseline (FAILED/INCOMPLETE,
  unchanged) — and its emission is byte-identical to main, so it is untouched.
- **`\trusted` still 1** (`#@ \trusted reviewer: fd-resolution-fidelity`,
  UnixInodeFileSystem.py:1726). No new `\trusted`/axiom/assumed-val in the diff.
- **Corpus byte-diff scope:**
  - Reference corpus (604 files): edited emitter vs main emitter = **0 content diffs, 0 one-sided**
    — fully byte-identical (no corpus file uses the field-decode idiom; the emitter change is a
    refactor + a new classifier that fires only on the idiom).
  - `UnixInodeFileSystem.mlw`: **byte-identical** to without-`no_inline` (the `#@ no_inline`
    decorator does not change `_dir_lookup`'s own-module emission — no caller in that module
    inlines it).
  - `pure_lib/os/__init__.mlw`: the ONLY `.mlw` that changes — `listdir`/`scandir`/`truncate`
    now emit a `_dir_lookup` CALL (string-typed params) instead of the inlined dirscan asserts.
    Re-typechecks + verifies GREEN (the deliverable).
- **doc-coherency:** GREEN (exit 0).

## SCOPE FLAG (for the parent)
The brief scoped a "pure type fix". The string-type leak portion IS pure-type (emitter +
faithful param annotations, 0 corpus diff, 0 trust). BUT restoring the gate to GREEN additionally
required `#@ no_inline` on `_dir_lookup` to defuse the inlined-dirscan aggregate explosion that the
type fix unmasked. The `no_inline` is doctrine-clean (consumes an existing cross-validated ensures,
adds no trust, leaves UnixInodeFileSystem.mlw byte-identical), but it is a modular-boundary change,
not a type change. Re-run before merge: full `__init__` typecheck ×2, `--fun` re-verify of the 5
retirements, and the corpus byte-diff (all reproduced above).

## STOP-AT-PROPOSAL
Patch saved to `getting-better/PROPOSAL-faithful-name-stringtype-fix.patch`; working tree reverted
clean (only the patch + this writeup remain). No commit.
