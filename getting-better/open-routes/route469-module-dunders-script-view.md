# OPEN ROUTE #469 — m1 SYNTHESIZED MODULE DUNDERS: route #461 runs the top level with `__name__` / `__package__` / ... bound to the values of an IMPORTED module, while the file is verified for -- and its __main__ driver runs as -- a script (`__name__ == '__main__'`, `__package__ is None`), so a top level that raises only when run as a script proves
**Status: REPAIRED (executor x2, driver run #3, 2026-10-29), Severity 1.** Red-team round 38 (2026-10-29, on a9eac4a08 after #460-#462: 688 probes / 155 proved / 142 confirmed; rt37's 83 all closed except #463 / #464). Census TSV `scratchpad/rt38/census.tsv`; the family block below is quoted from `scratchpad/rt38/FINDINGS.txt`.
Witnesses `witnesses-r469/` (16): `g6_s600_name_not_main.py`, `g6_s609_package_none.py`, `g6_s641_name_upper_index.py`, `g6_s644_class_module_attr.py`, `g6_s652_repr_class.py`, `g6_s656_package_eq_empty.py`, `g6_s657_package_len.py`, `g6_s661_type_name_main.py`, `g6_s663_name_dict_key.py`, `g6_s664_name_in_set.py`, `g6_s665_name_startswith.py`, `g6_s667_package_split.py`, `g6_s668_name_len.py`, `g6_s682_name_ne_main_alt.py`, `g6_s684_package_partition.py`, `g6_s685_name_eq_file_stem.py`.

Driver repro: 17/17 family exemplars (scratchpad/rt38/verify/, F8 without --import-path) rc=0 Verification SUCCESS on main a9eac4a08 at 2026-10-29T14:55Z, each violating under CPython (scratchpad/rt38/driver-repro.txt).

```
F5 m1 SYNTHESIZED MODULE DUNDERS: route #461 runs the top level with `__name__` / `__package__` / ... bound to the values of an IMPORTED module, while the file is verified for -- and its __main__ driver runs as -- a script (`__name__ == '__main__'`, `__package__ is None`), so a top level that raises only when run as a script proves (16)
  EXEMPLAR: g6/s600_name_not_main.py (`X = 1 // (__name__ != '__main__')` at module level; f claims no_exception \all)
  CPYTHON: ZeroDivisionError at import when the file is run as the script its own `if __name__ == "__main__":` driver is written for; s609 `__package__.upper()` AttributeError ('NoneType'); g6b adds __name__ in class bodies (__module__), repr / str of a class, logging.getLogger(__name__), Enum / namedtuple functional __module__
  WHY IT PROVES: pycsl.py:22580 binds the synthesized module's `__name__` to the FILE BASENAME and `__package__` to '' (the IMPORTED view), while the `if __name__ == "__main__":` arm is skipped as 'not run'; as a script CPython binds `__name__ = '__main__'` and `__package__ = None` (and class `__module__ = '__main__'`).
  PROPOSED SYSTEMATIC REPAIR: RUN m1 UNDER EVERY ENTRY THE FILE ADMITS: when the file has an `if __name__ == "__main__":` block (or is the CLI target), run the top level a second time with the SCRIPT bindings (`__name__ = '__main__'`, `__package__ = None`, `__spec__ = None`, `__file__` as given) and require both runs to succeed; or, allow-list polarity, make `__name__` / `__package__` / `__spec__` / `__loader__` / `__file__` UNKNOWN to m1 except in the canonical `if __name__ == "__main__":` test, so any other read refuses. Witnesses s600 s609 + g6b; control: `X = __name__` unused (PASS).
  PROBES: g6/s600_name_not_main.py g6/s609_package_none.py g6/s641_name_upper_index.py g6/s644_class_module_attr.py g6/s652_repr_class.py g6/s656_package_eq_empty.py g6/s657_package_len.py g6/s661_type_name_main.py g6/s663_name_dict_key.py g6/s664_name_in_set.py g6/s665_name_startswith.py g6/s667_package_split.py g6/s668_name_len.py g6/s682_name_ne_main_alt.py g6/s684_package_partition.py g6/s685_name_eq_file_stem.py
```

## REPAIR (executor x2, driver run #3, 2026-10-29, off daf5c3d1f; annotations §7.291, translational §T.6.301)

Inside m1's #461 block (no new def, no emission change). Allow-list polarity (the route's second option): `__name__`,
`__package__`, `__spec__`, `__loader__` read as names are UNKNOWN to the top-level run (so any statement whose value
depends on one is refused, under every entry the file admits: script, top-level import, package import), except the
canonical `if __name__ == "__main__":` test (either operand order), whose arm is not run at import and is not judged;
its `else` arm is refused (it binds names the script view lacks). A class's `__module__` is unknown, and so is every
string that exposes the private module name the classes are created under (`repr(C)`, `str(type(C()))`, `f"{C}"`);
a factory that records its caller's module (`namedtuple`, the functional `Enum` / `TypedDict`, `NewType`) is given
that private name; `getattr(o, "__module__")` is refused. Refusal code `PYCSL-R461-IMPORT-RAISES` (the
statement names the unknown read).

Witnesses 7342-7349 (s600 s609 s644 s652 s656 s661 s668 s685; all 16 of `witnesses-r469/` measured REFUSED). Control
7370 (`X = __name__`, `P = __package__` unused, `C.__name__` / `C.__qualname__`, the `__main__` driver): PROVED at base
and candidate.

OVER-REFUSAL COST, measured (candidate vs base emission of main daf5c3d1f = 33f7ac681's): byte-diff root 2604 -> 2608 .mlw, 0 MOVED / 0 GONE / 0 APPEARED (4 new controls); pyref 2186 / 2186 0/0/0; mirror 53 / 53 0/0/0 (no OWED proof). Static screens: CPython `compile()` + cookie decode of all 6937 corpus / pyref / mirror / pycsl_lib files: only the 12 new #465 witnesses fail; 1274 claimed files scanned for function-body classes, module-dunder reads and dunder attribute reads -- the one PASS file the first cut refused (5590, `class C(B)` over a class `B` of the same def) is admitted by the narrow row below; 0 corpus PASS file refused.


## GATES (routes #465 / #469 / #470 / #471 together, worktree pycsl-x2 off daf5c3d1f, 2026-10-29)
Fidelity: check-self-annotate-sync rc=0 (938 verbatim), self-annotate-mirror-check rc=0 (53). Byte-diff vs
`scratchpad/v13/ca` (emission of 33f7ac681, docs-only since): root 2604 -> 2608 0 MOVED / 0 GONE / 0 APPEARED (4 new
controls); pyref 2186 / 2186 0/0/0; mirror vs `v13/ma` 53 / 53 0/0/0 (no OWED proof). Soundness planes: first run 1 of 61
RED -- check-dropped-mutation CTXBIND 52 > 51, the compile gate's own `with open(..) as` (DIAGNOSED: a new `with ... as`
binding in the scanned emitter; repaired by `pathlib.Path(..).read_bytes()`, not by moving the ratchet), re-run
run-soundness-planes rc=0, 61 / 61 green. Ledgers: trusted-reasons rc=0 (409 <-> 409), assumed-facts --emit-dir rc=0, refusal-witness-coverage rc=0
(365 demonstrated, census +39 rows via `_census_row`), refusal-advice-audited rc=0 (191 / 254, R465 FOLLOWABLE),
dropped-mutation rc=0 (51 ctxbind), getattr-erasure rc=0, open-route-carriers rc=0, trusted-frame-honesty rc=0,
trusted-raises-honesty rc=0, clause-survival --emit-dir rc=0 (10 ledgered), stdlib-modules-verify rc=0, doc-coherency
rc=0. `\trusted` lines 437 (= base). Candidate: 39 witnesses REFUSED, 4 controls + 4 advice probes Verification
SUCCESS. Base daf5c3d1f: 18 sampled witnesses (7330 7333 7336 7341 7342 7343 7344 7345 7349 7350 7351 7355 7356 7360
7361 7364 7365 7367) and the 4 controls Verification SUCCESS. Compile screen (CPython `compile` + cookie decode) of 6937
corpus / pyref / mirror / pycsl_lib files: 12 failures, all the new #465 witnesses; 99 files carry a SyntaxWarning
(refusing warnings would cost them).

## RESIDUALS
- `__file__` keeps the absolute path of the verified file (as CPython binds it for a script and for a normal import);
  an import through a relative `sys.path` entry is not modelled.
- The `__main__` driver block itself is still not judged (m1's residual).
