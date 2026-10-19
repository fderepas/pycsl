# OPEN ROUTE #282 — DISTINCT PARAMETERS (AND DISTINCT LIST ELEMENTS) ARE ASSUMED NOT TO ALIAS, UNDECLARED
**Status: RESOLVED (declared assumption PARAM-DISJOINT), gen #37, 2026-10-19** — was OPEN (gen #37, 2026-10-19), Severity 2. See "REPAIR" at the end. Red-team round 6 (found by the r279 executor's census); probes rc=0 at 15953960, CPython violates.
Witnesses `witnesses-r282/`: p111 `f(xs, ys)` with `assigns xs[0]` proves `ys[0] == \old(ys[0])`; caller `f(a, a)` breaks it.
p112 the same through two object parameters; p114 `[r, r]` (one object twice in a list). Every caller that BUILDS the alias in
VERIFIED code is refused (route #254, R167 #243/#244); the residue is an alias built in UNVERIFIED code — ownership rule R1,
exactly like FIELD-DISJOINT (#256) for fields, but NOT listed by `--soundness-report`. Repair: declare it (e.g. PARAM-DISJOINT:
relied_on_by = every function that writes one mutable parameter/element while reading another of a compatible type), docs
in README / static-semantics / translational references, FIELD-DISJOINT precedent; or an opt-in strict mode if cheap.

## REPAIR (2026-10-19, worktree pycsl-r282 off 18354f52) — RESOLVED as the declared model assumption PARAM-DISJOINT

Decision: the FIELD-DISJOINT (#256) precedent, not a refusal. A faithful repair would need a separation
precondition PyCSL does not have, or a refusal of every function that writes one mutable handle while
touching another — measured below at 112 pre-existing root corpus files (180 functions) and 33 of the 53
mirror files (2731 entries, every `self`-mutating method that reads an IR-node parameter): disproportionate.
No emission change; no strict mode (every list/dict/set/record parameter frame rests on it).

Probe table (`pycsl.py`, rc; probes under the r282 scratchpad `probes/`; CPython ground truth in each corpus
file's `__main__`). The callee half PROVES at base and after (the assumption, now REPORTED); every verified
caller that builds the alias fails closed at base already — no new false proof found.

| shape | callee (base = after) | `--soundness-report` after | verified caller building the alias (base = after) |
|---|---|---|---|
| two list params `f(xs, ys)` (p111 / 3180) | PROVED | PARAM-DISJOINT `f: writes through xs, also accesses ys` | `f(a, a)`, `b = a; f(a, b)`: ill-typed, Why3 "illegal alias" (3190) |
| two record params `f(a, b)` (p112 / 3181) | PROVED | `f: writes through a, also accesses b` | `f(x, x)`: illegal alias (3191); `y = x; f(x, y)`: ill-typed (probe b02b) |
| one object twice in a `List[List[int]]` (p114 / 3182) | PROVED | `f: writes an element of xss ...` | `f([r, r])`, `m.append(r)` twice: ill-typed array-vs-matrix (3192, probe b03b) |
| two dict / two set params (3183) | PROVED | `f`/`g` reported | `f(d, d)` / `g(s, s)`: REFUSED PYCSL-WHYML-COLLECTION-ALIAS (3193; route #254) |
| `self` and a param of its class (3184) | PROVED | `a__bump: writes through self, also accesses o` | `x.bump(x)`: ill-typed (3194) |
| list param and a list field of `self` (3185) | PROVED | `t__m: writes through xs, also accesses self` | `T(L).m(L)`, `t.m(t.ys)`, param stored then passed: FAIL (constructor field havocked, R167 `assert false`) (3195) |
| list param and an element of a `List[List[int]]` param (3186) | PROVED | `f: writes through xs, also accesses xss` | `f(r, [r])`: ill-typed (3196) |
| forwarding caller `h(p, q)` -> `f(p, q)` (3188) | PROVED | BOTH `f` and `h` reported | — (h's own callers: the rows above) |
| two record values sharing one list field (`T(L)`, `T(L)`; method on another `T`) | Timeout (probe a11) | (FIELD-DISJOINT territory) | `a.m(b)`, `a.m(a)`: ill-typed (probes b11/b11b) |
| `List[A]` element field store `objs[0].v = 9` | REFUSED (pure-record elements) | — | `[x, x]`, `f(x, [x])`: REFUSED (probes b08/b18) |
| param and a module-level list `G` | Timeout (G is an opaque `val constant`; probe a13) | reported (`f: writes through xs, also accesses G`) | — |
| controls: distinct fresh objects to the 3180/3181 callees (3189) | PASS | — | — |

Rule (inline in `pycsl.py::_build_soundness_report`, mirror twin `\trusted` and unchanged; no new def — the
location-root walk is written inline, lesson a4): a function's mutable HANDLES are its parameters (unless the
annotation names only int/float/str/bool/bytes/complex/None, or tuple/frozenset/Optional of those; an
unannotated parameter is a handle), `self` for a method, and every module-level name its body reads (not a
local, parameter, function, type, import or builtin). A WRITE through a handle is a subscript store/slice
store/`del`, a field store or field augmented assignment, an augmented assignment, any method call on it,
passing it (or a location rooted at it) to a non-builtin call, or an `assigns` location rooted at it.
Reported: `f: writes through h, also accesses k, ...` when another handle is read or written anywhere in the
body or the contract; and `f: writes an element of h ...` when the written location passes through an
element (`xss[i][j] = ...`, an element-rooted `assigns`). Types are not matched (over-, never
under-reported). Statement: "two distinct mutable parameters (list/dict/set/record-valued, or a parameter and
the receiver self or one of its fields) hold distinct objects, and distinct elements of a list/dict parameter
hold distinct objects ... (ownership discipline rule R1; FIELD-DISJOINT for parameters and elements)".

Census (the new report over the pre-existing population): root corpus 112 files / 180 entries; mirror 33 of
53 files / 2731 entries. Spot check for UNDER-reporting: of the 18 root files whose signature has two
`List`/`Dict`/`Set` params, 14 are reported and the 4 that are not write nothing (`assigns \nothing`).

Docs: README (declared model assumptions: five), static-semantics App. C.1 (heading, count, table row),
translational §T.10.1 row + §T.10.5 entry, ownership discipline §5 ("Declared residue (routes #256, #282)"),
`bin/check-assumed-facts.py` docstring.

Corpus (block 3180-3199; 3180-3186, 3188-3196 used; 3187 dropped — the module-global probe times out):
3180-3186/3188 `# pycsl-model-assumption: PARAM-DISJOINT`, PASS (rc=0); control 3189 PASS (rc=0);
verified-caller alias controls 3190-3196 `# pycsl-expected: FAIL` (rc=1: 3190/3191/3192/3194/3196 ill-typed,
3193 refused, 3195 Unknown).

Gates (logs under the r282 scratchpad; base = worktree at 18354f52, removed):
- Witnesses (route `witnesses-r282/`): p111/p112/p114 rc=0 at base and after — by design (declared, not
  refused); `--soundness-report` lists PARAM-DISJOINT for each after (absent at base). Corpus 3180-3186/3188
  rc=0, 3189 rc=0, 3190-3196 rc=1 (same verdicts at base: the change touches only the report path).
- byte-diff-sweep base/after rc=0; byte-diff-compare root rc=0 (1812 base / 1827 cand, 0 MOVED / 0 GONE /
  0 APPEARED, 15 new sources ignored — 3193 is refused), pyref rc=0 (2186/2186, 0/0/0); mirror-emit-sweep
  base/after rc=0, compare `--min-files 45` rc=0 (53/53, 0/0/0). No mover, so no whole-file re-proof is OWED.
- Fidelity: check-self-annotate-sync.sh rc=0 (923 verbatim); self-annotate-mirror-check.sh rc=0 (53). The
  mirror twin of `_build_soundness_report` is `\trusted` and untouched.
- doc-coherency rc=0. run-soundness-planes.sh (fast) rc=0, 61/61 green. `--slow` NOT run (heavy slots held
  by other executors' slow planes and mirror proofs for most of the window).
- Ledgers (lesson d5): refusal-witness census +7 rows (3190-3196, via the plane's own `_census_row`, only
  these witnesses); refusal-witness-coverage rc=0 (240 demonstrated, 4 undemonstrated, ceiling 5). No
  refusal message, raise site, `\trusted` marker or axiom added (ledger 3).

Residuals. (1) A module-level mutable global is emitted as an opaque `val constant` (probe a13: `G: List[int]`
read inside `f` is `val constant g : int` with `subscript_get`), so neither its mutation nor its aliasing with a
parameter is modelled; the report counts such names as handles, but the global model itself is outside this
route. (2) Two record values sharing one list field (`T(L)`, `T(L)`) is FIELD-DISJOINT's case; its probe a11
timed out and the verified callers are ill-typed. (3) The verified-caller rows above fail closed partly BY
ACCIDENT (ill-typed emissions: illegal alias, array-vs-matrix, `x.bump(x)`), not by a named refusal; a future
change that makes those emissions well-typed must re-run 3190-3196. (4) No strict mode.
