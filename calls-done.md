# Lib/ Stub Completeness Audit — Done

Audit of `Lib/` PyCSL mock files against actual stdlib usage in `src/`
(as listed in `calls.md`).

## Modules Already Complete (no changes needed)

| Module | Functions in Lib/ | Symbols used by src/ | Status |
|--------|------------------|---------------------|--------|
| `hashlib` | 18 | `sha256` | ✅ Complete |
| `os.path` | 10 | `abspath`, `basename`, `dirname`, `exists`, `expanduser`, `isdir`, `isfile`, `join`, `normpath`, `splitext` | ✅ Complete |
| `shutil` | 22 | `copy2`, `rmtree`, `which` | ✅ Complete |
| `textwrap` | 5 | `dedent`, `indent` | ✅ Complete |
| `time` | 26 | `monotonic` | ✅ Complete |
| `tomllib` | 2 | `load`, `loads` | ✅ Complete |
| `unicodedata` | 20 | `normalize` | ✅ Complete |
| `warnings` | 7 | `warn` | ✅ Complete |

## Modules Updated

### `os.py` — Added 3 constants

- `environ = 0` — environment variables mapping
- `pardir = 0` — parent directory string constant
- `X_OK = 0` — os.access() mode flag for executable check

### `re.py` — Added 3 constants

- `DOTALL = 0` — regex flag: dot matches newline
- `IGNORECASE = 0` — regex flag: case-insensitive matching
- `MULTILINE = 0` — regex flag: `^`/`$` match line boundaries

### `sys.py` — Added 5 attributes

- `executable = 0` — path to the Python interpreter
- `path = 0` — module search path list
- `stderr = 0` — standard error stream
- `stdin = 0` — standard input stream
- `stdout = 0` — standard output stream

### `tempfile.py` — Added 1 function stub

- `TemporaryDirectory(suffix, prefix, dir)` — context manager for temp dirs

### `collections.py` — Added 2 function stubs

- `Counter(iterable)` — counting hashable objects
- `defaultdict(default_factory)` — dict with default factory

### `dataclasses.py` — Added 1 function stub

- `dataclass(cls)` — decorator for generating special methods

### `pathlib.py` — Added 1 function stub (was empty)

- `Path(path)` — concrete filesystem path constructor

### `datetime.py` — Added 1 function stub (was empty)

- `datetime(year, month, day, hour, minute, second)` — date+time constructor

### `argparse.py` — Added 1 function stub (was empty)

- `ArgumentParser(prog, usage, description, epilog)` — argument parser constructor

## Intentionally Skipped

### Exception classes (used only in `except` clauses)

| Module | Symbol | Reason |
|--------|--------|--------|
| `json` | `JSONDecodeError` | Exception class, not callable in contracts |
| `subprocess` | `SubprocessError` | Exception class |
| `subprocess` | `TimeoutExpired` | Exception class |

### Classes used for type-checking only (not called as constructors)

| Module | Symbol | Reason |
|--------|--------|--------|
| `argparse` | `Namespace` | Class, used for type annotations not construction |
| `ast` | 82 AST node classes | Used for `isinstance()` checks and pattern matching |
| `enum` | `Enum` | Base class, not called directly |
| `os` | `PathLike` | Abstract base class |
| `re` | `Match` | Return type class, not constructed |
| `subprocess` | `CompletedProcess` | Return type class, not constructed |

### Type aliases (no runtime behavior)

| Module | Symbols | Reason |
|--------|---------|--------|
| `typing` | `Any`, `Callable`, `Dict`, `Iterable`, `Iterator`, `List`, `Mapping`, `Optional`, `Sequence`, `Set`, `Tuple`, `TypedDict`, `Union` | Type hints only, erased at runtime |

### Submodules (not callable)

| Module | Symbol | Reason |
|--------|--------|--------|
| `importlib` | `util` | Submodule import, not a callable |

## Summary

| Metric | Count |
|--------|-------|
| Modules audited | 23 |
| Already complete | 8 |
| Modules updated | 9 |
| Constants/attributes added | 11 |
| Function stubs added | 6 |
| Symbols intentionally skipped | ~105 |
