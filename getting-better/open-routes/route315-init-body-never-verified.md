# OPEN ROUTE #315 — `__init__` BODIES ARE NEVER EMITTED OR VERIFIED: CONSTRUCTOR CALLS DROP ARGUMENT MUTATIONS AND CALLEE PRECONDITIONS
**Status: REPAIRED (gen #37, 2026-10-23; opened the same day; sound refusal), Severity 1.** Red-team round 15; driver-reproduced on main 65b22999 (rc=0; CPython violates).
Witnesses `witnesses-r315/`: `k = K(xs)` lowers to a bare record literal `{ n = 0 }`: `a[0] += 1` in __init__ (j01), `self.n = inc(a)` (j02),
effectful field initialisers (j03-j08 incl. print, if-condition call), explicit `#@ assigns a[0]`/`ensures` on __init__ ignored (j09),
callee precondition inside __init__ never checked: `K([])` calls `first(a)` (`requires len(a) >= 1`) — CPython IndexError, pycsl proves
`== 1` (j11); user exception __init__ mutating its argument (b04, #310 residual 4). Route #150 (draft) covers effects on `self` only.
Repair: verify every user `__init__` as a function (its own contract, default `assigns` = its fields only) and lower `K(args)` as a call to
it (pre-check requires, apply assigns/ensures, build the record from its ensures/body) — or refuse any class whose `__init__` is not
provably effect-free on arguments and precondition-free (pure field initialisation from parameters/literals).

## REPAIR (2026-10-23, r315 executor off d4e39ef2; commit 722fbff3 (code + witnesses + census) + docs commit)
**Census first** (AST, `scratch-r315/census.py` + the live rule replayed per file): classes with a user `__init__` /
`__post_init__`: pycsl-reference 742 (709 field initialisers, 33 not; 572 more without one), python-reference 12 (all field
initialisers), mirror 21 (17 / 4: `Module6_WhyMLTranspiler` subscript, `_Inliner` subscript, `_ContractParser` user call,
`pure_ast.AST` `kwargs.items()`), `src/pycsl_lib` 69 (62 / 7). Of the 33 corpus non-initialisers, 7 were constructed in a
non-trusted function of a file that still emitted (the GONE set below); the other 26 are the new witnesses or sit in files
that were already refused (#179, #271, ...) or never construct them in a checked function (byte-diff: nothing else moved). Corpus calls in constructors: `bytearray` 31, `super().__init__` 21, nested ctors 7, `setattr` 4, `len` 3, builtin
exceptions 3, `list` 3, user/method calls 6. Explicit `__init__` contracts: 98 corpus classes (route #15's checking-only
`<class>__init`, unchanged).

**Design (A), sound refusal; (B) not taken.** A faithful model (emit `__init__` as a verified function, lower `K(args)` to a
call, rebuild the record from its result) touches the record-construction lowering in `expressions.py` (the #311-#314 erasure
sites, worked in parallel), the 7 field-capture side channels of routes #79-#154 and the frame of every caller; the refusal
moves 7 expected-FAIL corpus files and nothing else, so (B) is disproportionate. Rule (`_run_pipeline` source scan, inline,
mirror twin `\trusted`; no IR change, no new def): a class's constructor (own `__init__`/`__post_init__`, else the nearest
base's) is a FIELD INITIALISER iff its statements are stores to `self.<f>` / a local, `if`/`for`/`match`/`raise`/`return`/
`pass`/expression statements, an augmented store only `+=`/`-=` of a number, calls only to total builtins, builtin
exceptions, `setattr(self, ...)`, `super().__init__` of a modelled base or a modelled class's constructor; no subscript read
(slices allowed), no subscript / non-`self` attribute store, no `/ // % << >>` by a non-positive-literal, no `while`/`try`/
`with`/`assert`/`global`/`nonlocal`; closed transitively over constructed classes and inherited constructors. A non-trusted
main-file function (or a `#@ fresh_globals` module body) constructing any other class -> `PYCSL-R315-UNMODELLED-CONSTRUCTOR`.

Probe table (`pycsl.py` whole-file; CPython ground truth in each file's `__main__`):

PROBE_TABLE

Blast radius: corpus root 0 MOVED / 7 GONE (declared: 1495, 1496, 1498 (#150), 1517, 1518, 1519 (#154), 2014 (#235) — all
`pycsl-expected: FAIL` witnesses, FAIL -> REFUSED; a constructor that calls `self._setup()` / `init_p(self)` / `xs.items()`,
stores through `me`/`xs` aliases or into `self.xs[0]`) / 0 APPEARED (4 new sources = the controls); pyref 0/0/0 (2186/2186);
mirror 0/0/0 (53/53: the 4 non-initialiser mirror classes are only constructed in `\trusted` code). No previously-PROVED
corpus file moved: no latent false proof, no regression. Census rows: 20 new (4040-4058, 4063) + 6 movers re-measured via
`_census_row` (VERIFY-FAIL -> REFUSAL; 2014 had none).
Gates: witnesses PROVED -> REFUSED (table); controls PASS both sides; byte-diff-compare root rc=0 (with the 7
`--expect-gone`), pyref rc=0 (`--min-files 2000`); mirror-emit-sweep base/after rc=0, compare `--min-files 50` rc=0 (0
movers, nothing OWED); check-self-annotate-sync.sh rc=0 (926 verbatim); self-annotate-mirror-check.sh rc=0;
run-soundness-planes.sh fast rc=0 (61/61); doc-coherency --check rc=0; check-assumed-facts rc=0; trusted-raises-honesty rc=0
(61 silent, ratchet 61); check-refusal-witness-coverage rc=0 (258 demonstrated / 5 undemonstrated, ceiling 5). Ledger 3.
Docs: annotations.md §7.9, static-semantics "Source refusal added by route #315", translational §T.6.20.
OWED: none (no mirror mover).
Residuals: (1) a base class not declared in the parsed sources (unresolved import, `src/pycsl_lib` stubs reached through the
import classifier, dynamically created classes such as `pure_ast`'s node types) is assumed to have a modelled constructor;
(2) constructions not spelled `K(...)` / `m.K(...)` (`cls(...)`, `type(self)(...)`, an alias `C = K`) are not scanned; (3) a
dataclass `field(default_factory=...)` runs at construction and is not scanned; (4) a `#@ requires` on `__init__` is still not
checked at the construction site (route #15; unobservable for a field initialiser body); (5) comparisons / `str()` / `for` over
a user object may call user dunders from a field initialiser (not scanned); (6) #310 residual 4 (effectful user exception
constructor) is closed by this refusal.
