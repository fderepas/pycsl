# DirEntry class import emits ill-typed module stubs (`_filesystem : int`)

**Date:** 2026-06-23 16:00
**Status:** UNCONFIRMED
**Filed by:** test-supervise-sl (os DirEntry fleet run, gap-4)

## Summary

When a formal-test driver imports a CLASS from `pycsl_lib.os` (e.g.
`from pycsl_lib.os import DirEntry`), the importer emits WhyML stubs for
the WHOLE module's functions (access, chmod, close, …) whose contracts
reference the module global `_filesystem` (e.g. `writes { _filesystem.disk }`),
BUT declares `_filesystem` as `val constant _filesystem : int` — NOT as the
`unixinodefilesystem` record. The stubs are therefore ill-typed
("unbound function or predicate symbol 'disk'"), and the file fails to
verify regardless of the driver body.

By contrast, importing FUNCTIONS from `pycsl_lib.os` (e.g.
`from pycsl_lib.os import listdir, mkdir`) materializes `_filesystem` as a
`let _filesystem : unixinodefilesystem = {…}` record (and declares the
`unixinodefilesystem` type), so the same stubs type-check.

## Reproduction

```python
# formal_os_direntry.py — class import
from pycsl_lib.os import DirEntry

#@ requires True
#@ assigns \nothing
#@ ensures \result == 1
def t() -> int:
    d = DirEntry("x", -1)
    return 1
```

```
$ .venv/bin/python src/pycsl/pycsl.py src/pycsl_lib_test/formal_os_direntry.py
…
File "…mlw", line 56, characters 27-31:
unbound function or predicate symbol 'disk'
[-] Verification FAILED or INCOMPLETE.
```

The generated mlw contains:
```whyml
type direntry = { mutable name: int; mutable path: int; mutable _inode_num: int }
…
val constant _filesystem : int          (* <-- WRONG: should be unixinodefilesystem *)
val access (filepath: string) (mode: int) : int
    ensures  { ((result = 1) <-> ((dir_lookup (get_dir _filesystem) 5 filepath) >= 0)) }
    writes   { _filesystem.disk }        (* <-- ill-typed: int has no .disk *)
```

## Expected behaviour

Importing a class should materialize the module's object globals
(`_filesystem : unixinodefilesystem`) and declare the record type, exactly
as a function import does, so the emitted module stubs type-check.

## Workaround applied

Strategy D: free-function wrappers (`dirent_is_dir` / `dirent_is_file` /
`dirent_is_symlink` / `dirent_is_junction`) added to `os/__init__.py` that
construct a `DirEntry` and delegate. The formal-test driver imports THESE
(function import → correct materialization) instead of the `DirEntry` class.
`os/__init__.py` still SUCCESS; the wrappers are body-verified, zero-TCB.

## Impact

Any formal-test driver that imports a class from a module that ALSO defines
module-global object instances (`_filesystem = UnixInodeFileSystem()`)
hits this. The class-import path's global materialization is incomplete
relative to the function-import path.
