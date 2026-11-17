# OPEN ROUTE #611: an importable NON-SOURCE module artifact (sourceless `.pyc`, extension module) beside the program

**Status: REPAIRED** on run #7, branch run7-u49, by the driver. Found by red team rt62:
- r10: a sourceless `hashlib.pyc`;
- r13: a `hashlib.cpython-314-x86_64-linux-gnu.so` built from C.

Both PROVED `ensures \result == True` over two sha-256 digests on the L13 tip, and CPython returns False for both. The L12 tip c37d50422 refused both (R325). The breach is therefore **INTRODUCED** by run #7's lvV digest model. The same layout also reaches lvQ's (L9) `json.dumps` model, with a sourceless `json.pyc` in the script directory; CPython returns False.

**Mechanism.** `_resolve_module_path` (`frontend/ir_resolve.py`, mirror twin `\trusted`) looked only for `X/__init__.py` and `X.py`. CPython's FileFinder also imports from the same path entry:
- an extension module (`X.so`, `X.abi3.so`, `X.cpython-*.so`, `X.pyd`), tried before `X.py`;
- a sourceless `X.pyc`, when there is no source.

pycsl found no local source, treated the name as the stdlib module, and its external-effect model fired.

**Rule (fail-closed, every resolution root, every module name; code `PYCSL-SEM-IMPORT-NONSOURCE-ARTIFACT`).** An absolute import is refused if any resolution root holds an importable non-source artifact for it. The root search order is script dir, cwd, `src/`, `Lib/`, then `--import-path`. The artifact is checked for both the top-level name and the full dotted stem.

`__pycache__/X.*.pyc` is not an artifact on its own, since CPython uses it only for an existing `X.py`.

**Extension (rt62 bypasses of the first version).** The first version (5dbaf401d) was bypassed three ways:
- r16: a package `hashlib/` whose only init is `__init__.pyc`;
- r17: a package `hashlib/` whose only init is an `__init__` extension module;
- j04: a stdlib-identical `json/` with `encoder.py` replaced by `encoder.pyc`. Route #326's walk compared only the `.py` files present.

Two rules were added:
- (i) Every non-source loader file anywhere under the top-level directory `X/` in a root (outside `__pycache__`) is an artifact.
- (ii) A local copy is admitted as the stdlib module only if its `.py` set EQUALS the stdlib's `.py` set. A missing file now counts against it, not only an extra or differing one. The repo-root `json/` has the same set, checked.

Witness `10123` covers r16 (`--import-path …/r611art/pkg`). `witnesses-r611/r16`, `r17` and `j04` hold rt62's probes. All are refused, and the controls `w4` and `10116` still take the model.

**Witnesses:**
- `10120` (a sourceless `hashlib.pyc` root) and `10122` (an extension-module root), via `--import-path test-suite/corpus/pycsl-reference/multi_file_lib/r611art[/ext]`. Both are REFUSED in hoare / typed / store, and census rows were made by `_census_row`.
- `witnesses-r611/w1` to `w4` hold the rt62 shapes plus a json one. `w4` is the control: a plain `import hashlib` still takes the model.

**Residual (OPEN, not repaired; rt62 r12).** A forged `__pycache__/X.cpython-314.pyc` beside a local copy that is byte-identical to the stdlib source, using an unchecked-hash pyc (PEP 552) or a matching timestamp header. CPython runs the forged bytecode while pycsl reads the identical source:
- For `hashlib`, it is held today only by accident: a rebound-name rule fires on the real stdlib source.
- For an admitted identical package such as the repo-root `json/`, it is open.

This is route #326's admission rule, so it predates run #7. Run #8 should refuse any `__pycache__` entry beside an admitted stdlib copy, or validate the entry.
