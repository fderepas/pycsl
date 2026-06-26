# formal_os_path.py — os.path CONSEQUENCE tests — PUBLIC API ONLY.
#
# Tests the os.path string functions that PyCSL can body-verify (exists,
# expanduser, isabs, isdir, isfile, basename, dirname, join). Each theorem
# CALLS THE PUBLIC API and asserts an OBSERVED CONSEQUENCE of the function's
# semantics — never the call's own return code in isolation.
#
# gap-1 (os.path string ops) — Strategy A LANDED for basename, dirname, join:
# pure-Python reimplementations using PyCSL-supported string primitives (len,
# indexing, slicing, +), replacing the rfind/split/variadic lowers that
# blocked body verification. Body-verified, zero-TCB. The consequence tests
# below forward the body-proven length-bound contracts (the analog of
# path_expanduser_identity). The importer stub exposes only the contract, so
# specific-input consequences (e.g. basename("/foo") == "foo") are NOT
# entailed through the public API — only the contract-entailed bounds are.
#
# REMAINING GAP (3 functions): splitext (string-tuple return type not
# inferred — component type defaults to int), normpath (split/join/..-
# resolution loop too complex for SMT), abspath (transitively depends on
# normpath). Kept `#@ \abstract` (zero-TCB bodyless val, no ensures). See
# bugs-to-report/20260623-1500-os-path-tool-gaps.md.

from pycsl_lib.os.path import (
    exists, expanduser, isabs, isdir, isfile, basename, dirname, join,
)


# (1) exists — CONSEQUENCE: no filesystem binding => always absent (0).
# Non-vacuous: a real binding would return 1 for an existing path.
#@ assigns \nothing
#@ ensures \result == 1
def path_exists_never_bound(p: str) -> int:
    r = exists(p)
    if r == 0:
        return 1
    return 0


# (2) isdir — CONSEQUENCE: no filesystem binding => never a directory (0).
# Non-vacuous: a real binding would return 1 for a directory path.
#@ assigns \nothing
#@ ensures \result == 1
def path_isdir_never_bound(p: str) -> int:
    r = isdir(p)
    if r == 0:
        return 1
    return 0


# (3) isfile — CONSEQUENCE: no filesystem binding => never a regular file (0).
# Non-vacuous: a real binding would return 1 for a file path.
#@ assigns \nothing
#@ ensures \result == 1
def path_isfile_never_bound(p: str) -> int:
    r = isfile(p)
    if r == 0:
        return 1
    return 0


# (4) expanduser — CONSEQUENCE: no home binding => identity (returns the
# path unchanged). Non-vacuous: a real expansion would rewrite "~...".
# Returns the result directly; the contract asserts the identity consequence
# (avoids body-level string comparison, which PyCSL lowers to a hash op).
#@ assigns \nothing
#@ ensures \result == p
def path_expanduser_identity(p: str) -> str:
    return expanduser(p)


# (5) isabs — CONSEQUENCE: the root path "/" is absolute (returns 1).
# Non-vacuous: if isabs did not check the leading "/", it would not pin "/"
# to 1. Constant input, genuine semantic consequence.
#@ assigns \nothing
#@ ensures \result == 1
def path_isabs_root() -> int:
    r = isabs("/")
    if r == 1:
        return 1
    return 0


# (6) isabs — CONSEQUENCE: the empty path is NOT absolute (returns 0).
# Non-vacuous: if isabs ignored the length guard, "" might return 1.
#@ assigns \nothing
#@ ensures \result == 1
def path_isabs_empty() -> int:
    r = isabs("")
    if r == 0:
        return 1
    return 0


# (7) isabs — CONSEQUENCE: a leading-slash path is absolute. Symbolic in
# the bound that any path whose first char is "/" yields 1.
#@ assigns \nothing
#@ requires \str_length(p) > 0
#@ requires \str_sub(p, 0, 1) == "/"
#@ ensures \result == 1
def path_isabs_leading_slash(p: str) -> int:
    r = isabs(p)
    if r == 1:
        return 1
    return 0


# (8) isabs — CONSEQUENCE: a non-empty path with no leading slash may be
# relative; the contract pins the RANGE (0 or 1) for any path. Symbolic.
# Non-vacuous: a function returning 2 would fail the bound.
#@ assigns \nothing
#@ ensures \result == 1
def path_isabs_range(p: str) -> int:
    r = isabs(p)
    if r == 0 or r == 1:
        return 1
    return 0


# (9) basename — CONSEQUENCE: the result is never longer than the input
# (a suffix-or-whole bound). Non-vacuous as an IMPORT check: a broken import
# that lost basename's length-bound contract would fail this. Symbolic in the
# input. Body-verified (Strategy A: pure-Python tail-scan loop, zero-TCB —
# no \abstract, no \trusted). Returned directly to avoid the int-hash local
# fallback for string comparison (same pattern as path_expanduser_identity).
#@ assigns \nothing
#@ ensures \str_length(\result) <= \str_length(p)
def path_basename_no_longer(p: str) -> str:
    return basename(p)


# (10) dirname — CONSEQUENCE: the result is never longer than the input
# (a prefix-or-empty bound). Non-vacuous as an IMPORT check. Body-verified
# (Strategy A: pure-Python tail-scan loop, zero-TCB).
#@ assigns \nothing
#@ ensures \str_length(\result) <= \str_length(p)
def path_dirname_no_longer(p: str) -> str:
    return dirname(p)


# (11) join — CONSEQUENCE: the joined result is at least as long as `b` (the
# second component is always preserved, possibly with a '/' separator and
# `a` prepended). Non-vacuous as an IMPORT check. Body-verified (Strategy A:
# binary join, zero-TCB — replaces the variadic *parts that lowered to an
# opaque int iterator).
#@ assigns \nothing
#@ ensures \str_length(\result) >= \str_length(b)
def path_join_keeps_b(a: str, b: str) -> str:
    return join(a, b)
