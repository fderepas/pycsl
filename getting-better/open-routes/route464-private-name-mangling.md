# OPEN ROUTE #464 — PRIVATE NAME MANGLING (`__x`) IGNORED BY THE FIELD / METHOD TABLES
**Status: OPEN, Severity 1.** Red team 37 family F8; driver re-run on the landed main 33f7ac681
(`scratchpad/rt37/rerun-on-33f7ac681.txt`): both witnesses rc=0 Verification SUCCESS; CPython AttributeError.
Witnesses `witnesses-r464/` (2): `e29_n100_sub_reads_base_private.py` (`self.__x` read in subclass D is `self._D__x`,
which B's `__init__` never set), `e29_n102_outside_reads_private_classattr.py` (`C.__K` read outside class C).

```
#464 `__name` (not dunder) inside class C means `_C__name`; outside any class it means `__name`. PyCSL resolves the
     unmangled name, so a subclass's `self.__x` finds the base's field and an outside `C.__K` finds C's attribute.
  REPAIR (proposed): apply CPython's mangling in the front end before the field / method / class-attribute tables are
  built (and in #445's attribute admission), so the lookups match CPython's.
```
