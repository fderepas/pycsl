# OPEN ROUTE #257 — A BARE `with <cm>:` DROPS `__enter__`/`__exit__` WHEN THE CM IS IMPORTED OR A `@contextmanager` METHOD

**Status: REPAIRED (gen #36, 2026-10-17; opened the same day), Severity 1.** Found by the ch18 re-drain census; driver-reproduced at HEAD
88157755 (both rc=0 "All contracts formally proven"; CPython f() = 1, claims `\result == 0`).

## Witnesses (`getting-better/census-ch18/repro/`)
- `xmod/w2524_bare_with_imported_cm.py` (+ `xmod/cmlib.py`, run with `--import-path .../xmod`): an imported
  context-manager class whose `__enter__` mutates the receiver; emitted body `let c = { n = 0 } in (); c.n`.
- `w2526_bare_with_contextmanager_method_framed.py`: an in-file `@contextmanager` method writing `self.n`.
- True twins w2525 / w2527 fail (completeness); controls w2520/w2521 (CM class in the same file) are refused.

## Mechanism
`Module5_IREmitter._py_stmt_with` lowers a bare `with` to its body; the route #38/#39 guard refuses only when the
SAME FILE defines a context-manager class — imported CM classes and `@contextmanager` generator methods escape it.

## Repair direction
Fail-closed: refuse every bare `with <expr>:` whose CM is not a known-inert builtin (e.g. a lock modelled by the
concurrency layer) — imported classes, `@contextmanager` functions/methods, any call result — or model
`__enter__`/`__exit__` effects. Measure blast radius (the mirror's own `with self.block():` sites).

## Repair landed (gen #36, 2026-10-17)

### Step 1: census (base 49f6a35d, before any code)
Modules 1-3 over corpus + mirror + `src/pycsl_lib` (147 `with` items): 49 bare lock NAMES in 32
`pycsl-reference` files, every one bound `lock_X = threading.Lock()` under `import threading`; 41 mirror items
(`self.block/delimit/require_parens/delimit_if`) in NON-`\trusted` `pure_ast._Unparser` methods, whose emitted
record is `type _unparser = {  }`; 11 mirror items (`open`/`NamedTemporaryFile`/`fdopen`/`ThreadPoolExecutor`/
`self.buffered`, all `as`) inside `\trusted` functions; `1031`'s `with blk():` (body `yield`); the rest
(`1030/1033/1035/1047`, pyref `0209` -> R38; `0989/1784`, pyref `0093/0191` -> #20 `as`) already refused.
`pycsl_lib`: no live site.

### Step 2: the rule (`_run_pipeline`, mirror twin `\trusted`; inline, no new def)
After the R38/#39 block, file-independent and fail-closed (`PYCSL-R257-CONTEXT-MANAGER-NOT-INERT`): outside a
`\trusted`/`\abstract` function (any ancestor), every BARE `with` item must be (L) a name bound ONLY by
`threading.Lock()`/`RLock()` (with `import threading` its sole binding), or (G) a call to an in-file producer
resolved PER CLASS (`self.m` in a method of K, defined once in K, overridden by no in-file subclass; or a
module-level def bound once) in the greatest INERT set: `@contextmanager` (resolved via `contextlib`, the import
the sole binding) with exactly one top-level `yield`, or body exactly `return <producer>()`/`return
nullcontext()`; no global/nonlocal/try/with/raise/del/assert/loop/comprehension/nested def/await/import; stores
only to locals or `self.<attr>` of a K whose IR record has NO fields; calls only producers, `len`/`isinstance`,
or in-file defs framed exactly `assigns \nothing` without `raises`. A `\trusted` producer qualifies only as a
`self` method of a field-less K whose `assigns` names only `self` fields (mirror `_Unparser.delimit_if`; its
reviewed frame is trusted to cover the returned manager's protocol). The call's ARGUMENTS obey the same call
rule. `as` items stay with #20; `async with` is refused outright. Also closes §T.5.10b's "known residue" (W1
keyed on a simple method name) for bare items.

### Step 3: gates
- Witnesses 2560-2566 (false claims; helpers `multi_file_lib/r257_{cmlib,boxlib,bumplib}.py`): each PROVED at
  49f6a35d (2560/2561/2562/2563/2564/2565/2566 rc=0, "All contracts formally proven"), each REFUSED after;
  CPython asserts the true value (1, or 2 for 2566). Scope pins 2567 (attribute; FAILED at base, refused after)
  and 2568 (`async with`; refused after). Control 2570 (the mirror `_Unparser` shape) and 1031 PROVE before and
  after; 0268 + a `#@ critical` lock file unchanged. Repro: w2524/w2526 refused, twins w2525/w2527 refused,
  controls w2520/w2521 still R38.
- Corpus byte-diff vs a fresh 49f6a35d worktree: root 1697/1698, 0 MOVED, 0 GONE, 0 APPEARED (1 new source:
  2570); pyref 2197/2197, 0/0/0. Mirror sweep 53/53, 0 MOVED/GONE/APPEARED (no mirror proof owed).
- `run-soundness-planes.sh` 61/61; `check-self-annotate-sync.sh` rc=0; `self-annotate-mirror-check.sh` rc=0.
  Ledgers: 9 own census rows appended (re-measured via the plane's own `_census_row`); advice audit +1
  FOLLOWABLE (repair: ordinary `enter()`/`leave()` methods around the block VERIFIES).

### Residual
The (G) acceptance rests on a field-less record making `self` writes unrepresentable (`check-yield-erasure`'s
ratcheted status quo), and on `\trusted` producers' reviewed frames. Exceptions raised by a quiet callee or
the CM protocol are not modelled (same footing as any call to that callee).
