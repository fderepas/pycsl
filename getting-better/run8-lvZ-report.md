# Run #8 lvZ report: routes #614 + #617, a pathlib Path value is identified with its string

Executor lvZ, driver run #8. Tree `/home/fabrice/git/pycsl-lvZ`, branch `run8-lvZ` (base `run8-int70`
ff01853ec). Spike branch `run8-lvZ-spikeT` (fdb9e6419). Never pushed. Log paths are relative to
`scratchpad/lvZ/` in the tree unless absolute.

## 1. Spike (T): Path as its own abstract WhyML type `py_path`

Branch `run8-lvZ-spikeT`, commit fdb9e6419 (measurement only, not for landing).

What the spike does:
- Module5 `_m5_path_ann_tag` tags `Path` / `PurePath` / `PosixPath` / `PurePosixPath` annotations (also
  through #31's alias resolution and `Optional[..]`) `py_path` instead of `str`. The Windows flavours are
  excluded: `PureWindowsPath("A") == PureWindowsPath("a")` while their `str`s differ.
- Module6: a `py_path` parameter / `-> Path` return is `py_path`; `type py_path` is declared once in the
  abstract block. `Path(<str>)` is `ext_path_of_str_op : string -> py_path`. `str(p)` / `os.fspath(p)` /
  `f"{p}"` is the law-free `path_str_op : py_path -> string`. `p / s` is `ppath_div_op`, `.parent`,
  `.stem` / `.name` / `.suffix`, `.resolve()`, `.is_file()` / `.is_dir()` / `.exists()`, `Path.cwd()`,
  `mkdir` / `write_text` / `read_bytes` take or return `py_path`. `os.path.*` of a `py_path` argument
  wraps it in `path_str_op`. `Path == Path` is `path_eq_op` (equality on the abstract type).
- Everything else that mixes a `py_path` with a `str`, or orders two of them, falls through to the
  existing lowerings and is a Why3 type error (fail-closed).

### Measurement (battery `bat1`, step S1; one NORMAL heavy job, cwd = snapshot tree root, oom_kill 15 -> 15)

| plane | result | log |
|---|---|---|
| corpus root vs `scratchpad/run8/v69/bd-int` | 3295 / 3295; **24 MOVED**, 0 GONE, 0 APPEARED | `bat1/spike-cmp-root.txt`, `bat1/spike-moved-root.txt` |
| pyref | 2185 / 2185; 0 / 0 / 0 | `bat1/spike-cmp-pyref.txt` |
| mirror vs `scratchpad/run8/v69/mir-int` | 53 / 53; **9 MOVED** | `bat1/spike-cmp-mir.txt`, `bat1/spike-mir-diff.txt` |

- The 24 moved corpus files are exactly the Path-lowering files (lvQ / lvV / lvX / u44 / u53 / gen36 ch14
  witnesses). About 12 of them are expected-PASS, and each would owe a re-proof.
- At the L3-tc level, none of the 66 corpus files that mention Path changed category
  (`logs/emit-spkcorp` vs `logs/emit-rcorp`).
- The 9 mirror movers are `pycsl`, `audit_proof` and `audit_proof_reverify`, plus 6 others:
  `frontend/import_classifier` and `proof2why3/{crosscheck, crosscheck_ir, extract, extract_lean_meta,
  sertop}`.
- Two of those 6 have VERIFIED bodies that move:
  - `proof2why3.crosscheck._module_namespace_of` (`let function ... (rocq_file: py_path)`);
  - `proof2why3.extract_lean_meta.lean_meta_available` (`let ... (proofs_dir: py_path)`, now with
    `ppath_div_op` / `ppath_isfile_op`).
- The landing would also have to inline the spike's classifier method `_lvz_is_path_expr`. It is a new
  method in a mirrored file, so it is counted by the mirror-coverage ratchet.

Probes (QUICK `--no-proof`, `logs/emit-spk1` vs `logs/emit-before`):
- All 16 rt67 shapes that emitted string lowerings at base became L3-tc type errors: m01 m02 m05 n02 n17
  n18 n19 n24 n27-n31.
- One sound control was over-refused: o03 (`f"{p}" == str(p)`). Route #307 rebinds the f-string operand
  to a fresh name that the classifier cannot see.
- o04 and o08 (`os.path` of a Path) were over-refused in that run. The `os.path` wrap fixed them before
  fdb9e6419, but they were not re-measured.

**Recommendation: (R).** By the driver's rule, (T) fails on both counts:
- it moves verified mirror bodies beyond `pycsl.py` / `audit_proof*`;
- it costs 24 corpus re-proofs.

(T) remains the principled direction. It needs a run that owns `proof2why3` and `import_classifier`
mirror re-proofs and can inline the classifier.
