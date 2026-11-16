# OPEN ROUTE #610 — MODULE-NAME SHADOWING IN THE EXTERNAL-EFFECT MODELS: A PARAMETER / LOCAL NAMED `hashlib` / `os` / `shutil` / `json` / ... MAKES `<name>.<f>(..)` TAKE THE MODULE MODEL, DROPPING THE USER OBJECT'S METHOD, ITS EFFECTS AND ITS NON-DETERMINISM
**Status: REPAIRED (driver run #7, executor u47, branch run7-u47 off run7-int65 d740630ef = L12 + lvU + lvV; annotations §7.610). Mechanism: a per-function source table of bound watched names (`pycsl.py::_run_pipeline`, twin `\trusted`) read by fail-closed guards at the model decision sites in `Module6_WhyMLTranspiler.transpile` (twin `\trusted`): lvQ / lvU's callee-registry walk and lvV's digest walk. A shadowed builtin (`sorted`, `int`) is already refused by the pre-existing rebound-name rule (route #386). Rule: PYCSL-R610-EXT-MODULE-NAME-SHADOWED.** Opened as: OPEN, Severity 1. INTRODUCED by run #7 for `hashlib` (lvV 695b1b71c), `shutil.which` and `os.access` (lvU 54fe15830; rt61's confirmed proofs a15, v07 / v13 / v15, a04 -- on L12 the user method's contract of a04 was used soundly); lvQ's `json.dumps` row (a12) as measured by rt61. Red team rt61 family M1.

## The defect (rt61 M1)

lvQ / lvU / lvV decide their models by the IR CALLEE STRING. Module 5 builds it from the spelling, so
`hashlib.sha256(b)` on a parameter `hashlib: K` is the string `"hashlib.sha256"` with receiver `None`, exactly
the module call. The guards checked only the import list (`_x7_mod`, `_x7v_hl`) and the class names
(`_x7_tnames`), never the function scope:

- M1a (introduced, lvV): `def same(hashlib: K, s): return hashlib.sha256(s.encode()).hexdigest() ==
  hashlib.sha256(s.encode()).hexdigest()` with `#@ ensures \result == True` and a counter-based `K.sha256`
  type-checked (and the deterministic `ext_sha256_hexdigest_op` proves it); CPython returns False. Also a local
  `hashlib = K()` (v15), and the frame claim `hashlib.c == \old(hashlib.c)` (v27). L12 refused these (R325).
- M1b (introduced, lvU): `return shutil.which(cmd)` with `shutil: W` a parameter: the law-free
  `ext_shutil_which_op_*` drops `W.which`'s write (a15).
- M1c (introduced, lvU): `os.access(..)` on an `os` parameter / local (a04 PROVED false per rt61; a13, a14
  type-check at base): lvU's `os.access` arm had neither a class-name nor a scope guard.
- M1d (lvQ): `json.dumps(..)` on a `json` parameter (a12) type-checks at L12 and at the base.

## The repair (driver run #7, executor u47)

- Rule: a modelled family call (`subprocess.run`, `Path.cwd`, `json.dumps` / the import-path `dumps`,
  `argparse.ArgumentParser`, `os.access`, `shutil.which`, lvV's `hashlib.sha256` and `int(.., 16)`) takes the model ONLY when its head names the module import (or the builtin)
  and is bound nowhere in the enclosing function and not rebound at module level; otherwise REFUSED (never the old
  opaque lowering). A function the table does not name, or no table, counts as shadowed (fail-closed). See §7.610.
- rt61 exemplars (`witnesses-r610/rt61-probes/`): v07 v13 v15 v27 a15 a04 a12 a13 a14 TYPE-CHECKED at base
  int65 (rt61's batch logs; re-measured by u47 on a d740630ef base tree), REFUSED with R610 at HEAD in the default /
  typed / store models; a06 a11 (already refused at base by other rules) also R610 at HEAD; a07 (`class os`) is
  refused at base and HEAD by the "imported name bound again" rule.
- u47 probes (`witnesses-r610/u47-probes/`): b01 walrus, b02 for target, b03 comprehension target, b07 a `Path`
  parameter (`Path.cwd()`), b08 a `subprocess` local, b11 an `argparse` parameter (TYPE-CHECKED at base): R610 x3 at
  HEAD. b04 (`global os` in another function), b05 (except target), b06 (`import json as os` in the function),
  b09 (an `int` parameter), b10 (a module-level `def sorted`) are refused at base and HEAD by earlier rules (global
  aliasing, definite assignment, the rebound-name rule, list-parameter append).
- Corpus witnesses (expected FAIL, refused x3 with R610): 10100-10113. Controls (expected PASS): 10115 (genuine
  `os.access`), 10116 (genuine sha-256 determinism), 10117 (an `os` parameter used as a plain object next to a
  genuine `os.access` in another function), 10118 (genuine `sorted` in the join model).
- Advice followed: `witnesses-r610/advice/a610_rename_binding` (10104's parameter renamed `os_obj`; proves).
- Builtins (lvV's `sorted` in `"<sep>".join(sorted(xs))`, `int(.., 16)`): every shadowing spelling tried is already
  refused at base and HEAD before Module 6 by the rebound-name rule ("a name's runtime value is not the one the model
  reads", route #386): u47 probes `s1` (a `sorted` parameter), `s2` walrus, `s3` for target, `s5` local import,
  `s6` module-level assignment, `s8` a nested-class method, `s9` an `if`-nested def, b09 (an `int` parameter); `s4` / `s7`
  (`global sorted` from another function) by the list-append / global-store rules. A Module 6 guard on lvV's `sorted`
  arm was written and REMOVED: it is unreachable from source, so it could only be an unwitnessed raise site. The
  `int(.., 16)` check shares lvV's digest-walk raise (reached by 10100-10102).

## Measurements (u47)

- Base for every comparison: 07f001675 = d740630ef (int65) merged with run7-lvV 26173c368, no R610 change
  (`/home/fabrice/git/pycsl-u47base`); HEAD e6391efdd = 8522a9cb5 (merge of 26173c368) + the R610 commits.
- Mirror: `bin/mirror-emit-sweep.sh` base vs HEAD, 53 / 53 byte-identical (0 MOVED / 0 GONE / 0 APPEARED); no mirror
  file newly refused.
- Corpus (driver decision: targeted, the full HEAD sweep is the L13 battery's): every root / pyref file that spells a
  modelled-family call, imports a watched module (`os json subprocess shutil argparse hashlib pathlib pkl`) or carries
  an `--import-path` / `--deep` flag, and their importers -- 178 root + 156 pyref at base. Root 67 / 71 emitted
  (the 4 new controls added), 0 MOVED / 0 GONE / 0 APPEARED; pyref 156 / 156, 0 / 0 / 0. lvQ 9700-9713 and lvV
  10080-10099 are all in that population; the lvU rows outside it (`x or {}` map) spell none of the guarded calls.
- Controls 10115-10118 and the advice files PROVED in the default model; typed / store fail L3-tc on 10117 / 10118
  / the advice files with byte-identical emission at base (a pre-existing record-in-pure-context / array-typing limit).
