# OPEN ROUTE #439 — A HASHED VALUE WHOSE CLASS COMES THROUGH A Protocol, A FOREIGN USER MODULE, OR setattr OWES NO TypeError
**Status: REPAIRED (executor g6, driver run #3), Severity 1.** Red-team round 34 (2026-10-28, convergence measurement after #418-#431 + R-gate on 78b519f63; 497 written / 474 fully proved / 63 confirmed; FINDINGS salvaged by the driver from the stalled executor's on-disk outputs); driver-reproduced on main (see `scratchpad/rt34/FINDINGS.txt` and the driver repro line below).
Witnesses `witnesses-r439/` (5): `pp08_protocol.py`, `pp11_callable_obj.py`, `j5_usermod_callee.py`, `j6_usermod_from.py`, `s0_setattr_dyn_name.py`.

Driver repro: 9/9 family samples rc=0 Verification SUCCESS on main 78b519f63 at 2026-10-28T10:12Z, each violating under CPython (scratchpad/rt34/driver-repro.txt).

```
#439 A HASHED VALUE WHOSE CLASS COMES THROUGH A Protocol, A FOREIGN USER MODULE, OR setattr OWES NO TypeError   (5)
  pp08 c: Pr (a Protocol with __len__); {c} PROVED; f([1])                                       CPython TypeError
  pp11 a Protocol with __call__ satisfied by an unhashable class   j5 / j6 an imported user-module function hashes its argument
  (import m / from m import h)   s0 setattr(o, name, [1]) then {o.k}
  REPAIR (proposed, allow-list / refuse by default): A Protocol-typed value is #UNK for hashing (structural typing admits list/dict/set); a call into an imported user module is
  treated as the R-gate treats an un-claimed callee (§7.47 / route #430), its exceptions reaching the caller; a field
  written by setattr with a non-literal name is #UNK.
```

## REPAIR (executor g6, driver run #3, 2026-10-28, off 1c083dcbe; annotations §7.140, translational §T.6.151)

Three admitted-set repairs, inline in `_run_pipeline` (src/pycsl/pycsl.py, `\trusted` in the mirror; no new def, no
emission change, no new refusal code):

1. STRUCTURAL TYPES are `#UNK` (as `Any`, §7.47): a file class listing `Protocol` (typing / typing_extensions, by
   name or `typing.Protocol`, `Protocol[T]` too) among its bases (`_pr439`), and a standard-library class object that is
   a `typing` Protocol (`_is_protocol`) or has its OWN `__subclasshook__` (`Callable`, `Hashable`, `Iterator`,
   `Awaitable`, `os.PathLike`, `SupportsInt` ...; the classes admitting a list were already "U"), get the value verdict
   "?" -- refused in every hashing position (`PYCSL-R349-UNHASHABLE-RECORD`). Nominal ABCs (`UserString`, `Number`,
   `Enum` ...) are unchanged: only an own hook / protocol flag counts, not an inherited one.
2. IMPORTED USER-MODULE CALLEES join the #430 set: the file's imports are closed over `_resolve_module_path` (skipping
   `sys.stdlib_module_names` and `src/pycsl/Lib/` stubs; transitively through the user modules they import), and a
   function / method of such a module without `#@ no_exception \all` whose body MAY hash (syntactic set: set / dict
   display or comprehension, subscript, `in`, `hash`, `add` / `discard` / `remove` / `get` / `setdefault` / `pop` /
   `update` / `__contains__` / `__getitem__` / `set` / `frozenset` / `dict` / `Counter` / `fromkeys`, a call into a user
   module, or of another such function of the module) carries "may raise TypeError": a `\all` caller is refused
   (`PYCSL-R430-CALLEE-UNDERIVABLE-HASH`), as for a same-file un-claimed callee.
3. A COMPUTED-NAME dynamic store (`setattr(o, nm, v)` / `o.__setattr__(nm, v)` with a non-constant name; a computed-key
   store or `.update` on `__dict__` / `vars(o)`) makes every field / class-attribute read of a file class UNDERIVABLE
   (`#UND`): refused when hashed under a TypeError claim (route R-gate), recorded for #430. Not `#UNK`: §7.63 measured
   that counting these stores as UNKNOWN for hashed values GONEs the `frontend/pure_ast.py` mirror. (The computed-key
   `__dict__` / `vars` forms were already refused by the namespace-dict rebinding rule, measured: probes dropped.)

Witnesses 6615-6624 (red-team pp08 / pp11 / j5 / j6 / s0 = 6615 / 6616 / 6620 / 6621 / 6624; NEW latents 6618
`typing.Protocol`, 6622 a transitive user module, PROVED at base; NEW probes 6617 `Hashable`, 6619 `SupportsInt`, FAIL at
base on another goal) all REFUSED; controls 6641 (an un-hashed Protocol / Callable, typed hashed values), 6642 (claimed /
non-hashing user-module callees), 6643 (computed-name `setattr` file: a field hashed un-claimed, an `int` hashed
claimed) PROVED at base and candidate. Helpers: test-suite/corpus/pycsl-reference/multi_file_lib/r439_{hashlib,hashmid,
okhash}.py.
