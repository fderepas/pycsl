# OPEN ROUTE #464 — PRIVATE NAME MANGLING (`__x`) IGNORED BY THE FIELD / METHOD TABLES
**Status: REPAIRED (executor cc1, driver run #3, 2026-10-29), Severity 1.** Red team 37 family F8; driver re-run on the landed main 33f7ac681
(`scratchpad/rt37/rerun-on-33f7ac681.txt`): both witnesses rc=0 Verification SUCCESS; CPython AttributeError.
Witnesses `witnesses-r464/` (2): `e29_n100_sub_reads_base_private.py` (`self.__x` read in subclass D is `self._D__x`,
which B's `__init__` never set), `e29_n102_outside_reads_private_classattr.py` (`C.__K` read outside class C).

```
#464 `__name` (not dunder) inside class C means `_C__name`; outside any class it means `__name`. PyCSL resolves the
     unmangled name, so a subclass's `self.__x` finds the base's field and an outside `C.__K` finds C's attribute.
  REPAIR (proposed): apply CPython's mangling in the front end before the field / method / class-attribute tables are
  built (and in #445's attribute admission), so the lookups match CPython's.
```

## REPAIR (executor cc1, driver run #3, 2026-10-29, off a9eac4a08; annotations §7.241, translational §T.6.251)

CPython's private-name mangling is applied to the TREE, where every table is built: in `Module3_Weaver.process` right
after `ast.parse` (both the main pipeline and `ir_resolve`'s dependency pipeline) and on `_run_pipeline`'s `_t341`
(routes #347 / #383 / #444 / #445 read it). `__x` (not a dunder, no dot) lexically inside class C -- methods and
anything nested in them, not a nested class (its own name) -- becomes `_C__x` (C stripped of leading underscores; all
underscores: unchanged) in `Name`, `Attribute.attr`, `arg`, `keyword`, def / class names, `global` / `nonlocal`,
`except .. as`, match captures / class-pattern attributes. Strings are not mangled (CPython). Each `#@` claim string is
mangled by the class enclosing its anchor (a class invariant by its own class), so `#@ ensures self.__x == n` on a
method of C reads the field its body writes. Both inline, `\trusted`-twin methods; written without a computed
`setattr`, `sorted(key=)` or a subscript store into an aliased list, which the dependency pipeline refuses in a module
it reads (measured: the first cut made mirrors `frontend/__init__` and `frontend/ir_resolve` GONE).

Witnesses (expected FAIL): 7200 (e29_n100) and 7201 (e29_n102), PROVED at base, now REFUSED by #445 over the mangled
names (`self._D__x` on D; `C.__K` on C, which binds `_C__K`); 7202 (`self.__m()` in a subclass; base refused only
incidentally, now by the method admission: D's MRO has no `_D__m`); 7203 (`c.__x` outside the class; PROVED at base);
7204 (D's claimed `get` returns `self.__x`; PROVED at base, FAILS: no field `_D__x`). Controls: 7205 (private field
claimed in its own class, PROVED base and candidate), 7206 (`self._C__x` in subclass D: FAILED at base, PROVED now),
7207 (private method `self.__m()` in its own class, PROVED base and candidate).

MOVED (M1, all intended -- the tables now carry CPython's names): root `5091_gen37_r374_ctl_slots_mangled_store`
(B's record: base had BOTH `b___x` and `_A__x`; now one `b__A__x` -- A's `self.__x` and B's `self._A__x` are one slot,
as in CPython), `5465_gen37_gd_ctl_mangled_other_name_absent` (`__k` -> `_R__k`), pyref `0133` (`__v` ->
`_Holder__v` in the record, the contracts and the body). APPEARED root `5440_gen37_gd_getattr_mangled_name`
(expected FAIL): `getattr(r, "_R__k", 0)` used to be refused by GD (the field `_R__k` was unknown); now the field IS
`_R__k`, the read lowers to it and the claim `\result == 0` FAILS (CPython 5) -- census row re-measured (VERIFY-FAIL).
Census rows of the slot witnesses 5058 / 5060 / 5062 / 5063 / 5064 / 5065 re-measured: their messages now print the
mangled attribute (`self._B__x`). Over-refusal cost: 0 PASS files.

ORACLE PLANES TAUGHT THE SAME RULE (they evaluate claims in CPython): `check-corpus-contract-truth.py` called
`getattr(C(), "__m")` for control 7207's private method (AttributeError: CPython binds `_C__m`), and
`check-corpus-contract-truth-args.py` evaluated control 7205's `\result == self.__x` outside any class (reads `__x`,
raises on every tuple -> an UNNAMED no-normal-exit). Both now apply CPython's mangling by the method's class (the method
name; the claim text of a method, as annotations §7.241 defines it). Both RED on the first battery, both rc=0 after.

## RESIDUALS
- `import __x` / `from m import __x` inside a class body is not mangled (CPython mangles the bound name); census 0.
- The claim strings are mangled textually (`\b__\w+`): a private-looking token inside a string literal of a claim is
  rewritten too.
- The other source re-parses in `_run_pipeline` (`_t376`, `_t338`, ...) stay unmangled; the checks that read them do
  their own mangling (#374, GD #388 / #396, #370).
