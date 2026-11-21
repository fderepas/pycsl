# Run #8 u53 report: route #614 "Path and str conflated" (refusal-only)

Executor u53, driver run #8. Tree `/home/fabrice/git/pycsl-u53`, branch `run8-u53`, base `run8-int68`
(4d753c2f1). Never pushed. Log paths are relative to the tree root.

## Commits

- 1e21fbd7d R614 pass + witnesses 10200-10207
- beab7ee49 constructors / type_decl contracts checked; docs (annotations.md §7.614, translational ref)
- 7fb23afb1 class fields / class attributes are fields, not scope names; IR name candidates
- 044216152 return rule admits a scalar non-str return annotation (recovers 12 pyref fixtures)
- 4a0533fac progress log (WIP)
- f354523ef census rows via `_census_row` (10200-10206, and 2161/2162 now refused)
- (final) report commit

Gates below were measured at f354523ef (src identical to 044216152).

## The rule: PYCSL-R614-PATH-STR-CONFLATED

Where: `src/pycsl/pycsl.py::_run_pipeline`, one inline block right after route #434's `ord`-of-Path pass
(search `ROUTE #614 (red team rt65`). The mirror twin of `_run_pipeline` is `\trusted` (an abbreviated
body), so no mirror emission moves and no re-proof is owed (measured: 0 mirror diff). There is no nested
`def` (mirror-coverage ratchet), no new `\trusted`, no axiom, and no Module 6 change. An admitted file
emits byte-identical WhyML.

Scope: every IR function that is not `\trusted` / `\abstract`, matched by full and method-stripped name,
plus every `__init__` / `__post_init__` when the unit has classes. Constructors are not IR functions;
their contracts sit in `type_decls`. Only sources containing `Path` are parsed.

Path-ish values (AST; a post-order fixpoint over the module; names keyed by outermost `def`; fields,
class attributes and Path-returning functions are module-wide):
- names annotated `Path` / `PurePath` / `PosixPath` / `WindowsPath` / `Pure*Path` / `PathLike`, also
  inside `List[..]` / `Optional[..]` / string annotations;
- names, fields, class attributes or defaults bound from a path-ish value: assign, annassign, augassign,
  walrus, `for` / comprehension targets, tuple unpacking, `append` / `insert` / item store into a fresh
  local container;
- `Path(..)` and the Path classes; a Path-only method (`resolve`, `with_suffix`, `iterdir`, `glob`,
  `cwd`, `home`, ...) on a path-ish receiver or a Path class; a unit function or property returning a
  Path; `x.parent` / `x.parents`; `/` (and `+`) with a path-ish operand;
- a subscript / conditional / boolean / container literal / comprehension / lambda of one;
  `list` / `sorted` / `zip` / `enumerate` / ... of one; `get` / `pop` / `values` of a path-ish container.

REFUSED in the body (AST):
- a `Compare` (`==` `!=` `<` `<=` `>` `>=` `in` `not in` `is` `is not`) with a path-ish operand. There are
  two exemptions:
  - `is None` / `is not None`;
  - `==` / `!=` with BOTH operands a direct one-argument `Path(..)` call. This is the only equality kept.
    The model is deterministic, so it equates two paths only when the arguments are equal, and CPython
    agrees. It has no injectivity law, so it never decides two paths different: 10205 checks that
    `Path("a//b") == Path("a/b")` with `\result == False` does NOT prove.
- an ordering / hashing / equality / type / repr call that involves one: `sorted` `min` `max` `hash` `set`
  `frozenset` `dict` `sort` `index` `count` `remove` `get` `pop` `add` `update`, the dunders, `operator.eq`
  and friends (including an aliased import), `bisect` / `heapq`, `isinstance` `type` `repr` `ascii` `id`;
- a path-ish set element, dict key or subscript key, or a dunder attribute of one;
- a `!r` / `!a` conversion, `%` formatting, or `.format(..)` (unless the receiver is a literal without
  `!r` / `!a`); a `match` on one;
- returning one from a function whose return annotation is missing, or is neither a Path nor a scalar
  non-str type (`int` `float` `bool` `bytes` `complex` `None`);
- passing one to:
  - a unit-function parameter or dataclass field not annotated `Path`;
  - a parameter / lambda / local callable, or an unknown builtin;
  - `map` / `filter` / `partial` / `setattr` / `reduce`;
  - a method of a value that is neither a module nor a Path;
- storing one into a container that is not a fresh local one (a parameter's, a field's, an alias's), or
  binding one to a `global` / `nonlocal`.

REFUSED on the IR, for the same functions and for the constructors' `init_ensures` /
`init_contract_check` / `class_invariants`:
- a `BinOp` comparison with a path-ish operand, with the same two exemptions. Path-ish here means a `Var`
  in the set, `Result` of a `-> Path` function, `Old(..)`, a Path call, `.parent`, a `FieldGet` of a Path
  field, or `/`;
- a path-ish subscript key;
- in the contract part (clauses, `ProofAssert`, loop invariants / variants), a call with a path-ish
  argument to anything except: `str` / `len`, the Path classes and methods, a module function, or a unit
  function whose parameter is annotated `Path`.

Admitted on purpose: `str(p)`, `f"{p}"` and `"{}".format(p)` are `str` values in CPython too, so
comparing them with a `str` or with each other is decided as CPython does. Control 10207 proves
`q = str(p); q == str(p)` in all three models.

Docs: `test-suite/annotations.md` §7.614; `docs/pycsl-translational-reference.md`, the paragraph "PATH /
STR CONFLATION" after route #434's PATH VALUES.

## rt65 probes, before (rt65, at a5303269e / 4d753c2f1) and after (f354523ef)

Full proofs: `scratchpad/u53/L/b1/summary.txt` (logs `scratchpad/u53/L/b1/<id>.<model>.log`;
PYTHON_CPU_COUNT=4; oom_kill 5->5 for every run). The value had risen from 0 to 5 during other
executors' jobs before my batch started.

| probe | before | after |
|---|---|---|
| a01 `p == str(p)` | SUCCESS 2/2 | REFUSED R614 |
| a07 `p: Path`, `p == str(p)` (pre-existing) | SUCCESS (head and base) | REFUSED R614 |
| a19 `!=` | SUCCESS | REFUSED R614 |
| a20 literal | SUCCESS | REFUSED R614 |
| b03 `p in [str(p)]` | SUCCESS | REFUSED R614 |
| b09 `f"{p}" == p` | SUCCESS | REFUSED R614 |
| b10 branch `q == p` | SUCCESS | REFUSED R614 |
| g03 branch `p != t` | SUCCESS | REFUSED R614 |
| g01 ordering | SUCCESS | REFUSED R614 |
| d06 method | SUCCESS | REFUSED R614 |
| g02 `[p] == [str(p)]` | L3-tc fail | REFUSED R614 |
| w10140 `Path(s) == Path(s)` | SUCCESS | SUCCESS 2/2 (kept; CPython True) |
| c01 / c04 `_sha256_file` non-vacuity | FAILED | FAILED (0/2, 1/3) |

Emission-level spot check of the axes that held (`scratchpad/u53/e4/*.log`, QUICK `--no-proof`):
- still refused: d01 d02 d03 d04 d09 d12 a05 a11 a14 a15 b27 e01 e05 e07 c03 a12 b19 d11. Some now hit
  R614 first; at head they were refused by R325 / #610 / #174 / #498.
- still emitted as before: b11 (sound control), b33, b34, c01, c04.

Also refused, rt65's b01 `repr`, b02 `isinstance(Path(s), str)`, b04 `d.get(p)`, b05, b07 `type(..)`
(`scratchpad/u53/e1`).

Own adversarial probes x01-x34 (`scratchpad/u53/adv/`, emissions in `scratchpad/u53/e3`, `e6`, `e7`):
- every conflating shape is refused. Covered: callable parameter, str-parameter helper, return as str,
  contract `requires p == "a"` / `ensures \result == str(p)` / `\old(p)` / loop invariant / `#@ assert`,
  sorted, set literal, `.parent`, lambda, tuple unpack, `for` over `List[Path]`, IfExp, `Path.cwd()`,
  `<`, `d.get(p)`, ctor parameter, dict key store, `from operator import eq as E`, default `p=Path("a")`,
  a contract predicate call, `@property -> Path`, a constructor body, a class attribute;
- admitted: x10 / x11 (`Path()==Path()`), x12 / x13 (`str(q) == str(q)`), x19 (`Optional[Path] is None`),
  x30 (fresh list append).

## Witnesses (corpus 10200-10207)

`scratchpad/u53/L/b1/summary.txt`; CPython (ulimit'd) agrees with each expectation.

| id | claim | hoare | typed | store |
|---|---|---|---|---|
| 10200 a01 shape | FAIL | REFUSED R614 | REFUSED | REFUSED |
| 10201 `p: Path` param (pre-existing a07) | FAIL | REFUSED | REFUSED | REFUSED |
| 10202 ordering by parts | FAIL | REFUSED | REFUSED | REFUSED |
| 10203 `p in [str(p)]` | FAIL | REFUSED | REFUSED | REFUSED |
| 10204 contract `\result == str(p)` (IR clause site) | FAIL | REFUSED | REFUSED | REFUSED |
| 10205 `Path("a//b") == Path("a/b")`, ensures False | FAIL | FAILED 1/3 | FAILED (L3-tc, lvX's pure-`let function` limit, as 10140) | FAILED (same) |
| 10206 `f"{p}" == p` | FAIL | REFUSED | REFUSED | REFUSED |
| 10207 control `q = str(p); q == str(p)` | PASS | SUCCESS 2/2 | SUCCESS 2/2 | SUCCESS 2/2 |

Census rows: `scratchpad/u53/tools/census.py` (`_census_row`), appended to `bin/refusal-witness-census.tsv`.

lvX witnesses (hoare):
- 10140 SUCCESS 2/2;
- 10141 FAILED 1/3, 10142 FAILED 1/3, 10144 FAILED 1/3;
- 10143 REFUSED (shadowing, as before);
- 10145 SUCCESS 17/17.

## Byte-diff (corpus root + pyref vs `scratchpad/run8/v67/bd-int`, one comparator per tree, cwd = tree root)

Sweep s2 at f354523ef: `scratchpad/u53/L/s2.status`, `s2.cmp-root.txt`, `s2.cmp-pyref.txt`.

- root: 3296 baseline / 3295 candidate; 0 MOVED, 3 GONE, 0 APPEARED, 2 new sources (10205 and 10207 emit;
  the other six new witnesses are refused).
  - The comparator with the 3 declared refusals and the new sources is OK rc 0
    (`scratchpad/u53/L/s2.cmp-root-expected.txt`).
- pyref: 2185 / 2185, 0 / 0 / 0, rc 0.

GONE (newly refused):
- `2160_gen36_ch13_path_resolve_is_path`, expected PASS. **OVER-REFUSAL.** Its `keep_other(p: Path,
  q: Path) -> Path` compares `r == q` (two Path values, `r = p.resolve()`) and claims `ensures \result ==
  q`. Path == Path between two non-`Path(..)`-call operands is refused, per the brief (only `Path(<str>)
  == Path(<str>)` is kept). The claim itself is sound in CPython for PosixPath; `bump_after_resolve` in
  the same file is collateral.
- `2161_gen36_ch13_path_resolve_not_identity_false_claim`, expected FAIL. It was VERIFY-FAIL and is now
  REFUSED (its `ensures \result == p` compares two Paths). Census row added.
- `2162_gen36_ch13_path_resolve_not_injective_false_claim`, expected FAIL. It was VERIFY-FAIL and is now
  REFUSED (`p.resolve() != q.resolve()`). Census row added.

A first sweep s1 (at 7fb23afb1) also lost 12 pyref fixtures
`stdlib/pathlib/{Path,PosixPath,PurePath,PurePosixPath,PureWindowsPath,WindowsPath}_call_{proves,fails}`
(`return pathlib.Path(x)` from `-> int`). 044216152 narrowed the return rule and recovered all 12 (s2 0 GONE).

## Mirror

Mirror sweep vs `scratchpad/run8/int68/mir`: 53 emitted, 0 diff lines, comparator 53/53 0/0/0 rc 0
(`scratchpad/u53/L/p1.status`, `p1.mir.diff`, `p1.mir.cmp`). No mirror file moved.

## Planes

- Fast planes (`bin/run-soundness-planes.sh`, teed, PRIO): rc 0, 62 ok, 23 slow planes not run (`--slow`
  not run, as the brief says). Log: `scratchpad/u53/L/f1.planes.log`, `f1.status`; oom 5->5.
- Individual planes (NORMAL job q1 at 1f0aaad46, src identical to f354523ef; oom 15->15, the rise from 5
  to 15 came from other executors' jobs between my runs): all rc 0 (`scratchpad/u53/L/q1.status`,
  `q1.<plane>.log`):
  - check-refusal-witness-coverage rc 0 (OK);
  - check-getattr-erasure rc 0 (DECLARED 0, ABSENT 27, UNKNOWN 75);
  - check-claim-vacuity rc 0 (1791 at the ceiling 1791);
  - check-mirror-coverage rc 0 (549 / 41, at the ratchets);
  - check-assigns-writes-survival rc 0 and check-trusted-frame-honesty rc 0, both on the
    single-underscore emit dir `scratchpad/u53/L/p1_emit1`;
  - count-trusted-directives rc 0.
- frontend-only conformance rc 0 (10/10 determinism); core-only conformance rc 0 (38 OK / 0 MISMATCH).
- Fidelity: covered by the fast planes run. The mirror-sync check is unaffected because `_run_pipeline`'s
  twin is `\trusted`.

## Counts

- Proof-axiom ledger: 3, unchanged. `src/pycsl/proof_axiom_allowlist.py` has no diff vs 4d753c2f1.
- `\trusted`: 365 (grep-substring), markers 337, unchanged (`scratchpad/u53/L/q1.count-trusted-bare.log`) (no `#@ \trusted` added; no mirror file touched).

## Residuals

- The equality of two Path-typed non-`Path(..)` operands (2160) is refused although it is sound for PosixPath
  when annotations hold. Re-admitting it needs an argument about annotation honesty.
- Annotations are trusted. A `str` passed to a `p: Path` parameter, or returned from a `-> Path` function,
  is not seen; this is the same trust as for every other annotation.
- Functions injected from IMPORTED modules (`resolve_imports`) have no source AST in this pass. Their
  bodies and contracts are checked only when their own file is verified.
- Path values that enter through an untracked channel are not followed: an external module call that
  returns a Path under a non-Path name, `getattr`, or a field of a class from another module.
- `p.name` / `p.suffix` (str attributes) are admitted. Their model is opaque and not the identity.
