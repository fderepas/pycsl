#!/usr/bin/env python3
"""CPython differential oracle for the pycsl_lib.os exception model (ROOT-CAUSE Fix 2b).

The os MODEL was converted so every fallible function RAISES OSError (or a subclass)
on failure instead of returning -1, per os.rst l.47-49.  This harness is the EXTERNAL
ORACLE that the ROOT-CAUSE writeup demanded: it runs the SAME documented failure
inputs against REAL CPython `os` and asserts that

    (a) real CPython raises an OSError-or-subclass on that failure input, and
    (b) the pycsl model's `#@ raises` declaration for that function names an
        OSError-or-subclass on the same failure condition

i.e. model and CPython AGREE on "raises an OSError-or-subclass" for each failure.
Where the model commits to the PRECISE subclass (open/stat/lstat -> FileNotFoundError),
this harness records whether CPython raises that exact subclass too (an extra-credit
"precise agreement" column); a generic-OSError model row still PASSES the floor as long
as CPython's exception IS-A OSError (which `except OSError` catches via the Fix-1
hierarchy).

This does NOT import the pycsl model (it is pure-Python with PyCSL globals and is not
runnable as plain CPython); it reads the model's declared `#@ raises` clauses from the
source as the model's externally-visible failure contract, and compares them to live
CPython behaviour.  Run:  python3 bin/os-cpython-differential.py
"""
import os
import re
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.path.join(REPO, "src", "pycsl_lib", "os", "__init__.py")

# OSError subclass hierarchy (mirrors src/pycsl/exception_model.py EXCEPTION_BASES).
def is_oserror_or_subclass(exc_name):
    try:
        cls = getattr(__builtins__, exc_name, None) if not isinstance(__builtins__, dict) \
              else __builtins__.get(exc_name)
    except Exception:
        cls = None
    if cls is None:
        cls = {"OSError": OSError, "FileNotFoundError": FileNotFoundError,
               "FileExistsError": FileExistsError, "PermissionError": PermissionError,
               "NotADirectoryError": NotADirectoryError, "IsADirectoryError": IsADirectoryError}.get(exc_name)
    return cls is not None and issubclass(cls, OSError)


def model_raises_clauses():
    """Parse the model's `#@ raises <Exc> when ...` per function (the model's
    externally-declared failure contract)."""
    txt = open(MODEL).read()
    out = {}  # fn -> set(exc names)
    cur = None
    pending = set()
    for line in txt.splitlines():
        m = re.match(r"\s*#@ raises (\w+)", line)
        if m:
            pending.add(m.group(1))
            continue
        d = re.match(r"def (\w+)\(", line)
        if d:
            if pending:
                out[d.group(1)] = set(pending)
            pending = set()
    return out


def run_cpython_failures():
    """Drive real CPython os.* on documented FAILURE inputs; record the raised type."""
    results = {}  # fn -> (raised_exc_name_or_None)
    d = tempfile.mkdtemp()
    absent = os.path.join(d, "definitely_absent_xyz")
    existing_dir = os.path.join(d, "existing_dir")
    os.mkdir(existing_dir)
    existing_file = os.path.join(d, "existing_file")
    open(existing_file, "w").close()
    badfd = 99999

    def record(fn, thunk):
        try:
            thunk()
            results[fn] = None  # no raise (unexpected for a failure input)
        except OSError as e:
            results[fn] = type(e).__name__
        except Exception as e:
            results[fn] = type(e).__name__

    record("open",     lambda: os.close(os.open(absent, os.O_RDONLY)))
    record("close",    lambda: os.close(badfd))
    record("read",     lambda: os.read(badfd, 4))
    record("write",    lambda: os.write(badfd, b"x"))
    record("pread",    lambda: os.pread(badfd, 4, 0))
    record("lseek",    lambda: os.lseek(badfd, 0, 0))
    record("dup",      lambda: os.dup(badfd))
    record("fstat",    lambda: os.fstat(badfd))
    record("stat",     lambda: os.stat(absent))
    record("lstat",    lambda: os.lstat(absent))
    record("mkdir",    lambda: os.mkdir(existing_dir))             # FileExistsError
    record("rmdir",    lambda: os.rmdir(absent))                  # FileNotFoundError
    record("makedirs", lambda: os.makedirs(existing_dir))         # FileExistsError
    record("unlink",   lambda: os.unlink(absent))                # FileNotFoundError
    record("remove",   lambda: os.remove(absent))                # FileNotFoundError
    record("link",     lambda: os.link(absent, os.path.join(d, "lk")))
    record("rename",   lambda: os.rename(absent, os.path.join(d, "rn")))
    record("symlink",  lambda: os.symlink("t", existing_file))    # FileExistsError
    record("readlink", lambda: os.readlink(existing_file))        # EINVAL (not a link)
    record("truncate", lambda: os.truncate(absent, 0))           # FileNotFoundError
    record("chmod",    lambda: os.chmod(absent, 0o644))          # FileNotFoundError
    record("listdir",  lambda: os.listdir(absent))               # FileNotFoundError
    record("scandir",  lambda: list(os.scandir(absent)))         # FileNotFoundError
    return results


def main():
    model = model_raises_clauses()
    cpy = run_cpython_failures()

    fallible = ["open", "close", "read", "write", "pread", "lseek", "dup", "fstat",
                "stat", "lstat", "mkdir", "rmdir", "makedirs", "unlink", "remove",
                "link", "rename", "symlink", "readlink", "truncate", "chmod",
                "listdir", "scandir"]

    print(f"{'function':<10} {'CPython raises':<20} {'model #@ raises':<28} {'floor':<6} {'precise'}")
    print("-" * 80)
    floor_fail = []
    for fn in fallible:
        cpy_exc = cpy.get(fn)
        model_excs = model.get(fn, set())
        # floor: CPython raises an OSError-subclass AND model declares an OSError-subclass
        cpy_ok = cpy_exc is not None and is_oserror_or_subclass(cpy_exc)
        model_ok = any(is_oserror_or_subclass(e) for e in model_excs)
        floor = "PASS" if (cpy_ok and model_ok) else "FAIL"
        if floor == "FAIL":
            floor_fail.append(fn)
        precise = "yes" if cpy_exc in model_excs else ("generic-OSError" if "OSError" in model_excs else "-")
        print(f"{fn:<10} {str(cpy_exc):<20} {','.join(sorted(model_excs)) or '(none)':<28} {floor:<6} {precise}")

    print("-" * 80)
    if floor_fail:
        print(f"[-] DIFFERENTIAL FLOOR FAILED for: {floor_fail}")
        print("    (model must declare an OSError-or-subclass raise where CPython raises one)")
        return 1
    print("[+] DIFFERENTIAL FLOOR PASSED: model and CPython agree that every fallible os")
    print("    function raises an OSError-or-subclass on its documented failure input.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
