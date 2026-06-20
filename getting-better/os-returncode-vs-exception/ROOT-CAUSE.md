# Root-cause: the os model returns `-1` on failure instead of raising `OSError`

**Status:** confirmed faithfulness error, module-wide. `src/pycsl_lib/os/` models failure with
C-syscall return codes (`-1`/`0`); Python's `os` module **raises `OSError` (or subclasses)**.
Every fallible function is affected (`open`, `close`, `mkdir`, `rmdir`, `read`, `write`, `stat`,
`unlink`, `chmod`, …). `access` is the one documented exception (it really does return a bool).

## The spec we violated
`test-suite/library_reference/os.rst`, lines 47–49 (module preamble):

> *All functions in this module raise `OSError` (or subclasses thereof) in the case of invalid or
> inaccessible file names and paths, or other arguments that have the correct type, but are not
> accepted by the operating system.*

`os.error` is documented as an **alias for `OSError`** (l.51–53). The model raises **nothing**
(no `raise`, no `OSError`, no `#@ raises` anywhere in `os/__init__.py`); it returns `-1`.

## How it was possible — a chain where each layer hid the next

1. **Tool expressibility gap.** `exception_model.KNOWN_EXCEPTIONS` =
   `{ZeroDivisionError, IndexError, KeyError, ValueError, StopIteration}` — exceptions with a
   *mathematical implicit trigger*. `OSError` is a **condition**-triggered exception (file absent,
   bad fd), which has no such trigger, so it is not auto-modeled. (Explicit `raise`/`#@ raises`
   *does* work for arbitrary names — the `SyntaxError` precedent — but the OSError **subclass
   hierarchy**, `except OSError` catching `FileNotFoundError`, is **not** modeled.) Path of least
   resistance: a sentinel.

2. **Kernel substrate.** `os/__init__.py` is *"backed by UnixInodeFileSystem"* — a Unix **kernel**
   model whose `sys_*` syscalls `return -1` (the syscall ABI). The wrappers pass `-1` through and
   never added the errno→raise translation that the *real* CPython `os` module is.

3. **Spec preamble blind spot.** The "raise OSError" rule is a **single global** statement, not
   repeated per function. The per-function `open` entry says only *"Return the file descriptor."*
   A function-by-function transcription never meets the global rule.

4. **Self-confirming tests.** The formal tests assert the `-1` consequence (`fd == -1 or fd >= 3`,
   `ino == -1 or valid`, the ENOENT `== -1` direction). The methodology (call API → check
   consequence) was applied faithfully **to the wrong spec**, so the tests *locked in* the error
   instead of catching it.

5. **Misdirected verification focus.** The whole campaign (incl. the `\trusted`-retirement work
   and the vacuity gate) asked *"does the body satisfy its contract?"* — never *"is the contract
   faithful to Python?"* Classic **verified-the-wrong-spec-correctly**.

## The meta-lesson
**A self-consistent wrong model is the most dangerous kind.** Proofs green, formal tests green,
`\trusted` → 0, byte-diffs stable — every internal check passed *because all checks derive from
the same wrong assumption (`-1` = failure)*. There was no **external oracle**: nothing compared
the model to real CPython behavior, and nothing checked the contracts against the module's
**global** spec rule. Internal consistency ≠ faithfulness. (Same throughline as the vacuity
finding: "green" meant "internally consistent," not "matches reality.")

---

# Process fix 1 (tool) — make the right semantics expressible: the OSError hierarchy

**What already works:** explicit raises of arbitrary exception names (`raise FileNotFoundError`,
`#@ raises FileNotFoundError`, `except FileNotFoundError`) — the preamble declares any exception
named in a `raises`/handler (the `SyntaxError` precedent). So the os model *can* be rewritten to
`raise` on failure with no tool change for the raise itself.

**The gap to close:** PyCSL treats exception names as **flat, distinct tokens** — there is no
subclass relation, so `except OSError:` does **not** catch a raised `FileNotFoundError`, and
`#@ raises OSError` does not summarize the subclass raises. Real os code relies on this constantly.

**Draft:**
1. Add an **exception hierarchy table** to `exception_model.py`, e.g.
   ```python
   EXCEPTION_BASES: Dict[str, Tuple[str, ...]] = {
       "FileNotFoundError":  ("OSError", "Exception"),
       "FileExistsError":    ("OSError", "Exception"),
       "PermissionError":    ("OSError", "Exception"),
       "NotADirectoryError": ("OSError", "Exception"),
       "IsADirectoryError":  ("OSError", "Exception"),
       "OSError":            ("Exception",),
       # … (errno-mapped OSError subclasses)
   }
   ```
2. In the WhyML emission of `try/except`, a handler `except B` catches a raised exception `E`
   when `E == B or B in bases*(E)` (reflexive-transitive closure of `EXCEPTION_BASES`). Emit the
   handler guard as a disjunction over the matching exception tags.
3. `#@ raises OSError` on a function means "may raise OSError **or any subclass**"; `#@ raises
   FileNotFoundError` is the precise leaf. Validate handler/raises sets against the hierarchy.
4. Keep `OSError` **out** of `KNOWN_EXCEPTIONS` (no implicit math trigger) — it is raised on an
   **explicit failure condition** in the body (`if dir_lookup(...) < 0: raise FileNotFoundError`),
   exactly like the `SyntaxError` model.

**Acceptance:** a driver doing `try: os.open(absent) except OSError:` proves the handler is taken
(the `FileNotFoundError` raised by `open` is caught by `except OSError`); a driver that forgets the
handler is provably non-total (the `raises` escapes).

---

# Process fix 2 (skill) — an external oracle in the stdlib workflow

The `pycsl-stdlib-coverage` workflow validated each module against **itself**. Add two
external-oracle steps so a self-consistent-but-wrong model cannot pass.

**2a — Global-spec-preamble capture (before annotating).** The discipline must read the module's
**module-level** RST preamble (not only per-function entries) and turn each global statement into a
**module-wide contract obligation** before any function is annotated. For `os`, the obligation is:
*every fallible function raises `OSError`/subclass on failure* — so the very first contract written
is a `raises`, not a return code. Checklist item: *"Quote the module's global failure/return
conventions from the spec preamble; if a function can fail, its contract MUST encode the global
failure mode (raise vs sentinel) — sentinels are allowed ONLY where the spec explicitly documents
one (e.g. `os.access` returns bool)."*

**2b — Differential test against real CPython (the oracle).** Each module ships, alongside its
formal test, a **differential** test: run the SAME inputs — *especially failure inputs* (missing
path, bad fd, existing dir for mkdir) — against **real CPython** and against the model, and assert
they **agree on observable behavior** (raises-which-exception vs returns-what). A formal test that
checks only the model's own consequence is self-confirming; the differential test is the external
oracle that would have caught `open(missing) -> -1` immediately (real CPython raises
`FileNotFoundError`). Wire a `--check-cpython-differential` mode (or a `bin/` harness) that fails
when model and CPython disagree.

**Acceptance:** a model whose `open(missing)` returns `-1` (current os) FAILS the differential
oracle against CPython's `FileNotFoundError`; a model that raises the right subclass passes.

---

## Relation to other findings
Same family as the non-vacuity gap ([[vacuity_nonlinear_div]]) and the no-more-int doctrine
([[feedback_no_more_int]] — `-1`-as-failure is itself an int-sentinel leak): the durable fixes are
about adding **external oracles** and **expressible faithful semantics**, not patching one module.
The os correction itself (return-code → exception, every fallible function + every `== -1` test) is
the follow-on, gated on fix 1.
