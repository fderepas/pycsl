# OPEN ROUTE #599 — ROUTE #174 ADMITS `except C` WHEN ANY ONE OPERATION OF THE `try` BODY RAISES C IN THE MODEL; A LATER OPERATION THAT RAISES C ONLY IN CPYTHON REACHES THE HANDLER IN A STATE THE PROOF NEVER CONSIDERED
**Status: REPAIRED (driver run #7, executor u44, branch run7-u44 off ghost-assign-bc6 952bf7891; annotations §7.599). Mechanism: route #174's handler census (`functions.py::_reset_function_state`, twin `\trusted`) now checks, for every narrow class admitted by an explicit / declared / ext raiser, that every operation of the `try` body is modelled for it (`PYCSL-R599-HANDLER-UNMODELLED-RAISER`), with a state-insensitive-handler exemption; lvQ's ext lowering of `.mkdir()` / `.write_text()` (`expressions.py::_handle_call_expr`, twin `\trusted`) admits a receiver only when the SOURCE shows it is a `pathlib.Path` (`pycsl.py::_run_pipeline` table, twin `\trusted`; `PYCSL-R7Q-EXT-PATH-RECEIVER`). Inline, no new def, no axiom, no `\trusted`.** Opened as: Status OPEN, Severity 1. INTRODUCED by run #7 (L9, lvQ's external-effect raise rows now count as raisers of AttributeError / the OSError family / UnicodeDecodeError / SystemExit / ...; base 73fd1874f refuses the five introduced exemplars via route #174) + one PRE-EXISTING twin (an explicit `raise OSError` as the coverer, c06b, proves at base too). MANDATORY repair (plan §4: introduced by the run).** Found by red team rt58 (scratchpad/rt58/FINDINGS.txt, families.txt, logs/). Related lvQ defect: the PATH-RECEIVER check accepts a `str` receiver for `.mkdir()` / `.write_text()` (CPython raises AttributeError, not in the declared set).

## Exemplars (witnesses-r599/)
- c01_cover_argparse_mkdir_str.py: `argparse.ArgumentParser()` covers `except AttributeError`, then `s.mkdir(...)` with `s: str`; `ensures \result == 0` PROVES at L9, refused at base; CPython returns 1.
- c05 (`b.decode()`), c09 (`q.read_text()`), c12 (`sys.exit(k)`), c14b (`os.path.getsize`): INTRODUCED.
- c06b: PRE-EXISTING twin (explicit raise covers, then `os.path.getsize`).

## The repair (driver run #7, executor u44)

RULE (annotations §7.599, code `PYCSL-R599-HANDLER-UNMODELLED-RAISER`), inside route #174's census in
`module6_whyml/functions.py::_reset_function_state` (mirror twin `\trusted`), for a claiming function (route
#171/#174's claim test: a non-trivial `ensures`, an assertion, a loop invariant / variant, a class invariant) and
for each narrow handler class C that route #174 ADMITS although no modelled implicit exception (IndexError,
KeyError, ValueError, ZeroDivisionError, StopIteration) lies below it -- i.e. C is admitted only by an explicit
`raise`, a same-file callee's `raises` or an lvQ `ext` registry row:

- every `Call` of the `try` body, at any depth, must be an `ext` registry call (lvQ's row lists every class CPython
  raises there) or the construction of a builtin exception class; any other call -- a same-file function or method
  (it may raise C at an unmodelled operation of its own), a receiver-less facade (`os.path.getsize`, `sys.exit`,
  `q.read_text()`, `b.decode()`), a builtin -- is an UNMODELLED RAISER;
- when C is not below OSError / UnicodeError / SystemExit / EOFError (classes CPython raises only inside a call),
  every expression must also be a name or a literal (an attribute read, an operator, a subscript, a comprehension
  ... raise AttributeError / TypeError / OverflowError / RecursionError too) and every statement an assignment,
  expression statement, `if`, `pass`, `raise`, `return`, `break`, `continue`, ghost or proof statement;
- EXEMPT (H, a handler whose outcome cannot depend on the state it is entered in): the handler is ONE `return <e>`
  over literals and never-assigned int / bool / str / float parameters, the `try` has no `finally`, the function's
  only claims are `ensures` over `\result`, literals and those parameters (no class invariant, assertion or loop
  invariant), and the FIRST statement of the `try` body is a call over plain arguments that may raise a subclass
  of C in EVERY state (an `ext` row, or a same-file `\abstract` function's `raises D when True`): the model then
  proves the handler's value under the path condition at the `try` itself, which every CPython run entering it
  satisfies. Measured necessary: corpus 0449 / 0450 / 0451 / 0453 (PASS: `except SyntaxError: return 0` around an
  `\abstract` parser, then a record constructor / method / an imported `visit`) would otherwise be refused. A
  CONDITIONAL cover is not enough (witness 9959: `if n > 100: raise OSError` under `requires n <= 100` makes the
  constant handler dead in the model).

PATH-RECEIVER (lvQ sub-defect, rt58 c01): the #31 path model erases `Path` to `str`, so lvQ's
`PYCSL-R7Q-EXT-PATH-RECEIVER` (`_is_string_expr` on the receiver) admitted a `str` receiver of `.mkdir()` /
`.write_text()`, where CPython ALWAYS raises AttributeError (not in the row). `pycsl.py::_run_pipeline` (twin
`\trusted`) now computes per function (Module 5's name) the names the SOURCE shows are a `pathlib.Path` -- a
parameter annotated `Path` / `pathlib.Path` / `PosixPath` (not Optional), or a local every binding of which is a
path expression (`Path(..)`, `Path.cwd()` / `.home()`, a path name, `<p>.parent`, a pathlib method returning a
path, `a / b` with a path operand or a str-valued left operand: CPython gives a Path or raises TypeError there),
greatest fixpoint -- and hands the table to the transpiler (`transpiler.path_names_r599`, the route #567
attribute pattern). `expressions.py::_handle_call_expr` (twin `\trusted`), AFTER lvQ's existing check (so 9712
keeps its message), refuses a receiver not in the table (absent table: refused) with the same code.

Advice of the new messages: "Move every operation the handler is not meant for out of the `try` body" (control
9963 = rt58 c14b with `os.path.getsize` moved after the `try`), "Annotate the receiver as `Path`" (control 9966 =
rt58 c01 with `s: Path`).

## Witnesses and measurements (u44)

All logs under the executor tree `/home/fabrice/git/pycsl-u44/scratchpad/u44/` (`logs/<id>.<tag>-<mode>.{emit,prove}`,
tools `tools/{emit,prove,proofs1,sweeps,gates1,gates2}.sh`; oom_kill 0 -> 0 on every proof).
- rt58 exemplars (this directory): c01 REFUSED PYCSL-R7Q-EXT-PATH-RECEIVER, c05 / c06b / c09 / c12 / c14b REFUSED
  PYCSL-R599-HANDLER-UNMODELLED-RAISER, in default / typed / store (`--no-proof --typecheck`, logs `*.k1-*.emit`;
  full proof default `*.head-hoare.prove`). Their L9 SUCCESS: rt58 `logs/<probe>.h.prove`.
- CORPUS expected FAIL (REFUSED x default / typed / store at HEAD; full proof default refused): 9940-9945 (rt58
  c01 / c05 / c06b / c09 / c12 / c14b), 9946 (same-file callee), 9947 (attribute read, hard class), 9948 (operator,
  TypeError), 9949 (explicit UnicodeDecodeError covers decode), 9950 (nested raiser), 9951 / 9952 (str local /
  str parameter receiver of mkdir / write_text), 9959 (constant handler, CONDITIONAL cover). At base 952bf7891,
  full proof default: 9946, 9948, 9950, 9951, 9952, 9959 PROVED (false proofs; CPython drivers print VIOLATION);
  9947, 9949 not proved there either (shape witnesses).
- CONTROLS expected PASS, PROVED at HEAD in default / typed / store: 9960 (explicit raise only), 9961 (Path-derived
  receiver under an argparse-covered handler), 9962 (two ext mkdir), 9963 (advice: move the op out), 9966 (advice:
  annotate `Path`).
- u44 probes: `u44-probes/` (p599b-p599i, c599a-c599c = the corpus files above); advice files `advice/`.
- Over-refusal: corpus byte-diff vs the L9 sweep v57/bd-int: root 3127 / 3127, 0 MOVED, 0 GONE, 0 APPEARED; pyref
  2185 / 2185, 0 / 0 / 0. Mirror sweep vs v57/mir-int: 53 / 53 IDENTICAL. lvQ's 9700-9713 emit byte-identically
  (inside the root sweep).
- RESIDUALS (named, not repaired here): (a) the handler classes route #171 covers through a modelled implicit
  exception (ValueError and its bases, LookupError, ...) are unchanged -- an unmodelled facade raising ValueError
  (e.g. an embedded NUL in `os.path.getsize`) under `except ValueError` relies on route #171's widened
  `no_exception`, not on this rule; (b) the PATH-RECEIVER table trusts a `Path` parameter annotation (a caller
  passing a `str` literal to a `Path` parameter type-checks under the #31 model); (c) implicit dunder calls of user
  classes (`a + b` with a user `__add__`) under a call-only (soft) class are not counted as calls.
