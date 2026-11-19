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

**Second extension (rt62 r19: a SYMLINKED program).** For `link/prog.py -> ../real/prog.py`, CPython's `sys.path[0]` is the realpath directory, `real/`, while pycsl's first root is `link/`. Rule: when the two differ, ANY importable entry for the module in the real directory counts as an artifact, whether source, package or artifact. It is refused at the same raise site. The witness is `witnesses-r611/r19`.

**Witnesses:**
- `10120` (a sourceless `hashlib.pyc` root) and `10122` (an extension-module root), via `--import-path test-suite/corpus/pycsl-reference/multi_file_lib/r611art[/ext]`. Both are REFUSED in hoare / typed / store, and census rows were made by `_census_row`.
- `witnesses-r611/w1` to `w4` hold the rt62 shapes plus a json one. `w4` is the control: a plain `import hashlib` still takes the model.

**Residual (OPEN, not repaired; rt62 r12).** A forged `__pycache__/X.cpython-314.pyc` beside a local copy that is byte-identical to the stdlib source, using an unchecked-hash pyc (PEP 552) or a matching timestamp header. CPython runs the forged bytecode while pycsl reads the identical source:
- For `hashlib`, it is held today only by accident: a rebound-name rule fires on the real stdlib source.
- For an admitted identical package such as the repo-root `json/`, it is open.

This is route #326's admission rule, so it predates run #7. Run #8 should refuse any `__pycache__` entry beside an admitted stdlib copy, or validate the entry.

## r12 REPAIRED (run #8, executor u50, branch run8-u50)

**Rule** (`_resolve_module_path`, mirror twin `\trusted`; refusal-only, fail-closed; code
`PYCSL-SEM-IMPORT-PYCACHE-UNVERIFIED`). For every module the resolver returns -- the hit itself,
each parent package `__init__.py` on its dotted path, and EVERY `.py` of an admitted
stdlib-named local package copy (route #326 / #611) -- every bytecode cache that CPython's
source loader could take instead of the source must be provably the compilation of that source:

- the candidates are every `__pycache__/<m>.<cache_tag>.pyc` and `<m>.<cache_tag>.opt-<N>.pyc`
  for ANY level N >= 1 (`python -OOO` loads `.opt-3`, PYTHONOPTIMIZE=7 loads `.opt-7`; the
  loader compiles at level 2 for every N >= 2), plus pycsl's own `sys.pycache_prefix` location;
- a candidate CPython itself rejects is ignored: shorter than 16 bytes, wrong magic, unknown
  flag bits, or a TIMESTAMP pyc whose header mtime / size do not match the source's stat (CPython
  recompiles from source then);
- every other candidate -- an unchecked hash-based pyc (PEP 552), a checked one (loaded
  unconditionally under `--check-hash-based-pycs never`), a timestamp pyc whose header matches --
  is unmarshalled and compared with `compile(source, path, "exec", dont_inherit=True,
  optimize=min(N, 2))`: every `co_*` attribute, recursively through `co_consts` (exact constant
  types, float / complex bits, frozenset / slice constants), with `co_filename` rewritten exactly
  as `_imp._fix_co_filename` does. Equal: accepted. Anything else (or an unreadable cache): REFUSED.

A genuine CPython-written cache validates, so verdicts do not depend on whether CPython once ran
in a directory: the `__pycache__` caches of all 241 main-tree source modules that have one
(test-suite, json/, src/), plus the repo-root `json/` package walked as an admitted stdlib copy,
are ACCEPTED by the exact rule code (`witnesses-r611r12/blk.py`, `maintree-scan.txt`, measured
2026-11-17 on the main tree's live caches).

**Measured (real CPython 3.14.4 vs pycsl, `witnesses-r611r12/`):** 22 probes, each run under
CPython default / -O / -OO / -OOO / `--check-hash-based-pycs never|always`. The set pycsl refuses
is EXACTLY the set where some CPython configuration runs the forged bytecode (A1 A2 A3 A6 A7 A9
J1 N1 T1); every genuine / stale / other-version cache is accepted (A4 A5 A5o A5r A5u A8 J2 N2 T2).

**Not only held by accident:** at base 0057c8b94, N1 (a plain local dependency with a forged
unchecked pyc) and T1 (a stdlib-identical `tomllib/` copy with a forged submodule cache) PROVE
while CPython violates the contract -- live pre-existing false proofs (the hashlib and json shapes
were held by the rebound-name rule and route #305). Corpus witnesses 10124-10127 (FAIL, refused
x3 models), controls 10128 (dependency + genuine `.pyc` / `.opt-1.pyc`) and 10129 (tomllib copy +
genuine caches), which prove in hoare exactly as at base.

**Residuals (not closable in pycsl):** the program's runtime environment is not visible to
pycsl: `PYTHONPYCACHEPREFIX` / `-X pycache_prefix` of the user's interpreter (only pycsl's own
prefix is checked), another interpreter version with another cache tag (`cpython-313`), and a
program run as `python -m prog` (its own cache is then used; only imported modules are checked).
A future CPython patch release that compiles the same source differently under the same magic
number would make a genuine cache refuse (fail-closed, environment-dependent over-refusal).

### r12 follow-up (driver review cr63, `scratchpad/run8/evidence/u50/cr63-review.md`)

- **R1 fixed:** `co_code` is CPython's DEOPTIMISED view (specialised opcodes mapped back, inline
  caches zeroed); every code-object pair must now also have equal `_co_code_adaptive` (the bytes
  the interpreter runs). Both sides are fresh, never-executed objects: on the main tree this
  costs no genuine cache (`maintree-scan.txt`: 0 of 242 main-tree caches refused).
- **Q3 fixed:** an unlistable `__pycache__` (`os.listdir` OSError, mode `-wx`) refuses with the
  same code instead of crashing the resolver (CPython can still open a pyc in it by name).
- **Residual 3 (stale / latent timestamp pyc): DRIVER DECISION, kept as a TOCTOU residual.** A first
  version (69529e2de) validated a timestamp pyc even when its header does not match the source's
  current stat. Measured cost: 25 of the 242 main-tree caches (all honestly stale) refused, and with
  those caches present 3 of 53 mirror files (`Module6_WhyMLTranspiler`, `proof2why3__crosscheck_ir`,
  `pycsl`) unemittable -- verdicts depending on cache state the other way round. CPython does not
  load such a pyc at that moment (it recompiles from source); it only goes live after a later
  metadata change (`touch -d`, `cp -p`, `rsync -t`, an mtime-restoring extraction), and a new pycsl
  run then sees a header-matching cache and validates it. So non-matching timestamp headers are
  ignored again, exactly as CPython ignores them, and the metadata-later case is documented with
  time-of-check vs time-of-use. Main-tree scan after the revert: 0 of 242 refused.
- **Documented residuals (not compared / out of reach):** R2 `localspluskinds` (no `co_*` view;
  a forged CO_FAST_HIDDEN / argument-kind bit changes only `locals()` / frame introspection);
  R3 constant identity / sharing (`f() is g()` over equal constant tuples, de-shared via marshal
  back-references); time-of-check vs time-of-use (a cache created or modified after verification,
  honestly by CPython or by an attacker, or a stale timestamp pyc made header-matching by a later
  metadata change); the program's runtime PYTHONPYCACHEPREFIX; another
  interpreter's cache tag; under `python -m pkg.prog` the program's own cache AND the package
  `__init__` chain above the main file (the parent loop starts below the import's base).
- **Over-refusals (fail-closed, documented):** a stale CHECKED-hash pyc (CPython's default mode
  rejects and rewrites it; refused because `--check-hash-based-pycs never` would run it; common
  when `SOURCE_DATE_EPOCH` is set); caches written with `-X no_debug_ranges` /
  PYTHONNODEBUGRANGES, or pycsl run that way (different `co_linetable`); an unreadable cache file
  (EACCES; CPython ignores it); a patch release that compiles differently under the same magic.
