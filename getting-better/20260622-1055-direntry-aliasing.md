# DirEntry constructor blocks formal-test drivers (aliasing rule)

**Category:** Ergonomics gap (formal-test authoring)
**Filed by:** test-supervise-sl (os module fleet)
**Date:** 2026-06-22

## Problem

`DirEntry.__init__(self, name, inode_num, fs)` takes a filesystem argument `fs`.
PyCSL prohibits passing the module global `_filesystem` as an argument:

```
[!] PIPELINE ERROR:
cannot pass module global '_filesystem' as an argument (inline.md Phase 3):
would alias the global; operate on it via its own methods/fields.
```

Additionally, `scandir()` in this model returns inode **numbers** (a list of
ints), NOT `DirEntry` objects. So there is no public API that yields a
constructible `DirEntry`.

## Consequence

DirEntry methods (`is_dir`, `is_file`, `is_symlink`, `is_junction`) are
**untestable** through the public API. The contracts are body-proven in
`os/__init__.py`, but no caller-side consequence test can fire.

## Suggested fix (ergonomics)

One or more of:
1. Allow passing `_filesystem` to constructors whose parameter is typed as the
   filesystem class (the aliasing concern is about mutation through an alias;
   a constructor storing the reference is safe if the caller does not mutate
   through the local).
2. Have `scandir()` return `DirEntry` objects (matching CPython's API) instead
   of raw inode numbers, so callers obtain DirEntry through the public API.
3. Provide a `DirEntry.from_inode(name, inode_num)` classmethod that implicitly
   binds `_filesystem`, avoiding the explicit global-as-argument.
