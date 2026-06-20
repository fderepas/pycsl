# formal_os_pure.py — os PURE-HELPER totality/value theorems, PUBLIC API ONLY.
#
# The pure helpers have no filesystem consequence; the right theorem is a
# totality / modeled-value theorem: the helper is total (no precondition needed)
# and returns the value its contract promises.
#
# TWO CLASSES:
#  (A) CONSTANT-returning helpers (getcwd, getpid, get_exec_path, chflags,
#      confstr, copy_file_range, getxattr, listxattr, islink) — their contract
#      pins \result to the modeled constant, so the value theorem PROVES.
#  (B) IDENTITY helpers (fsdecode, fsencode, fspath) and getenv — their contract
#      is `#@ ensures True` only. The identity CONSEQUENCE `fsdecode(x) == x` is
#      therefore NOT entailed (the body is identity but, as a trusted stub, the
#      body is invisible to callers; the contract promises nothing). Documented
#      Unknown below — the model gap is `ensures \result == filename`.
#
# INTERNALS-BLIND. Public names only. Each theorem returns int, asserts == 1.

from pycsl_lib.os import (
    getcwd, getpid, get_exec_path,
    chflags, confstr, copy_file_range, getxattr, listxattr, islink,
    fsdecode, fsencode, fspath, getenv,
)


# (A) CONSTANT-returning helpers — value theorems (PROVE).

#@ requires True
#@ ensures \result == 1
def getcwd_is_root() -> int:
    if getcwd() == 0:               # modeled cwd: root inode 0
        return 1
    return 0


#@ requires True
#@ ensures \result == 1
def getpid_is_one() -> int:
    if getpid() == 1:               # modeled pid: 1
        return 1
    return 0


#@ requires True
#@ ensures \result == 1
def get_exec_path_is_zero() -> int:
    if get_exec_path() == 0:
        return 1
    return 0


#@ requires True
#@ ensures \result == 1
def chflags_total_zero(p: int, flags: int) -> int:
    if chflags(p, flags) == 0:
        return 1
    return 0


#@ requires True
#@ ensures \result == 1
def confstr_total_zero(name: int) -> int:
    if confstr(name) == 0:
        return 1
    return 0


#@ requires n >= 0
#@ ensures \result == 1
def copy_file_range_total_zero(src: int, dst: int, n: int) -> int:
    if copy_file_range(src, dst, n) == 0:
        return 1
    return 0


#@ requires True
#@ ensures \result == 1
def getxattr_total_zero(p: int, attr: int) -> int:
    if getxattr(p, attr) == 0:
        return 1
    return 0


#@ requires True
#@ ensures \result == 1
def listxattr_total_zero(p: int) -> int:
    if listxattr(p) == 0:
        return 1
    return 0


#@ requires True
#@ ensures \result == 1
def islink_total_zero(p: int) -> int:
    if islink(p) == 0:              # stub: never a symlink in this model
        return 1
    return 0


# (B) IDENTITY helpers — the identity CONSEQUENCE. HONEST STATUS: Unknown.
# fsdecode/fsencode/fspath ensure only `True`; the identity is not entailed.
# getenv ensures only `True`; getenv(k, d) == d is not entailed. The model gap
# is a value post-state (`\result == filename` / `\result == default`).
# NOTE: fsdecode/fsencode/fspath leave their param UN-ANNOTATED, so the emitted
# stub types it `int`; the driver params are `int` to match (a `str` arg trips a
# WhyML int-vs-string emission type error at the `== x` compare — itself a facet
# of the model gap: no str-coherent identity contract).

#@ requires True
#@ ensures \result == 1
def fsdecode_is_identity(x: int) -> int:
    if fsdecode(x) == x:            # want: identity — NOT entailed (ensures True)
        return 1
    return 0


#@ requires True
#@ ensures \result == 1
def fsencode_is_identity(x: int) -> int:
    if fsencode(x) == x:           # want: identity — NOT entailed
        return 1
    return 0


#@ requires True
#@ ensures \result == 1
def fspath_is_identity(x: int) -> int:
    if fspath(x) == x:             # want: identity — NOT entailed
        return 1
    return 0


#@ requires True
#@ ensures \result == 1
def getenv_returns_default(key: int, default: int) -> int:
    if getenv(key, default) == default:   # want: returns default — NOT entailed
        return 1
    return 0
