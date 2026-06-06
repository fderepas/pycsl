# Library Method Calls — PyCSL Contracts

For every method or constructor from a Python standard-library or third-party
package called inside `src/`, the recommended `#@ requires` and `#@ ensures`
contracts based on the actual return type and semantics.

**Contract patterns by return type:**
- **object/string/void** → `#@ ensures True` (no numeric property expressible)
- **bool** → `#@ ensures \result == 0 or \result == 1`
- **int/float ≥ 0** → `#@ ensures \result >= 0`
- **tuple with fd** → `#@ ensures \result[0] >= 0`

---

## Standard Library

### `argparse`

| Call | Returns | Contract |
|------|---------|----------|
| `argparse.ArgumentParser()` | object | `#@ requires True` / `#@ ensures True` |

### `ast`

| Call | Returns | Contract |
|------|---------|----------|
| `ast.dump()` | string | `#@ requires True` / `#@ ensures True` |
| `ast.iter_child_nodes()` | iterator of objects | `#@ requires True` / `#@ ensures True` |
| `ast.parse()` | object (AST Module) | `#@ requires True` / `#@ ensures True` |
| `ast.walk()` | iterator of objects | `#@ requires True` / `#@ ensures True` |

### `collections`

| Call | Returns | Contract |
|------|---------|----------|
| `collections.Counter()` | object (Counter dict) | `#@ requires True` / `#@ ensures True` |
| `collections.defaultdict()` | object (defaultdict) | `#@ requires True` / `#@ ensures True` |

### `dataclasses`

| Call | Returns | Contract |
|------|---------|----------|
| `dataclasses.asdict()` | object (dict) | `#@ requires True` / `#@ ensures True` |
| `dataclasses.dataclass()` | object (decorated class) | `#@ requires True` / `#@ ensures True` |
| `dataclasses.field()` | object (Field) | `#@ requires True` / `#@ ensures True` |

### `datetime`

| Call | Returns | Contract |
|------|---------|----------|
| `datetime.datetime.fromisoformat()` | object (datetime) | `#@ requires True` / `#@ ensures True` |
| `datetime.datetime.now()` | object (datetime) | `#@ requires True` / `#@ ensures True` |

### `hashlib`

| Call | Returns | Contract |
|------|---------|----------|
| `hashlib.sha256()` | object (hash) | `#@ requires True` / `#@ ensures True` |

### `importlib`

| Call | Returns | Contract |
|------|---------|----------|
| `importlib.util.module_from_spec()` | object (module) | `#@ requires True` / `#@ ensures True` |
| `importlib.util.spec_from_file_location()` | object (ModuleSpec) | `#@ requires True` / `#@ ensures True` |

### `json`

| Call | Returns | Contract |
|------|---------|----------|
| `json.dumps()` | string | `#@ requires True` / `#@ ensures True` |
| `json.load()` | object (parsed JSON) | `#@ requires True` / `#@ ensures True` |
| `json.loads()` | object (parsed JSON) | `#@ requires True` / `#@ ensures True` |

### `os`

| Call | Returns | Contract |
|------|---------|----------|
| `os.access()` | bool | `#@ requires True` / `#@ ensures \result == 0 or \result == 1` |
| `os.close()` | void | `#@ requires True` / `#@ ensures True` |
| `os.environ.get()` | string or None | `#@ requires True` / `#@ ensures True` |
| `os.getcwd()` | string | `#@ requires True` / `#@ ensures True` |
| `os.listdir()` | list of strings | `#@ requires True` / `#@ ensures True` |
| `os.makedirs()` | void | `#@ requires True` / `#@ ensures True` |
| `os.remove()` | void | `#@ requires True` / `#@ ensures True` |
| `os.unlink()` | void | `#@ requires True` / `#@ ensures True` |

### `os.path`

| Call | Returns | Contract |
|------|---------|----------|
| `os.path.abspath()` | string | `#@ requires True` / `#@ ensures True` |
| `os.path.basename()` | string | `#@ requires True` / `#@ ensures True` |
| `os.path.dirname()` | string | `#@ requires True` / `#@ ensures True` |
| `os.path.exists()` | bool | `#@ requires True` / `#@ ensures \result == 0 or \result == 1` |
| `os.path.expanduser()` | string | `#@ requires True` / `#@ ensures True` |
| `os.path.isdir()` | bool | `#@ requires True` / `#@ ensures \result == 0 or \result == 1` |
| `os.path.isfile()` | bool | `#@ requires True` / `#@ ensures \result == 0 or \result == 1` |
| `os.path.join()` | string | `#@ requires True` / `#@ ensures True` |
| `os.path.normpath()` | string | `#@ requires True` / `#@ ensures True` |
| `os.path.splitext()` | tuple of strings | `#@ requires True` / `#@ ensures True` |

### `pathlib`

| Call | Returns | Contract |
|------|---------|----------|
| `pathlib.Path()` | object (Path) | `#@ requires True` / `#@ ensures True` |
| `pathlib.Path.cwd()` | object (Path) | `#@ requires True` / `#@ ensures True` |
| `pathlib.Path.home()` | object (Path) | `#@ requires True` / `#@ ensures True` |

### `re`

| Call | Returns | Contract |
|------|---------|----------|
| `re.compile()` | object (Pattern) | `#@ requires True` / `#@ ensures True` |
| `re.escape()` | string | `#@ requires True` / `#@ ensures True` |
| `re.findall()` | list of strings | `#@ requires True` / `#@ ensures True` |
| `re.finditer()` | iterator of Match | `#@ requires True` / `#@ ensures True` |
| `re.fullmatch()` | Match or None | `#@ requires True` / `#@ ensures True` |
| `re.match()` | Match or None | `#@ requires True` / `#@ ensures True` |
| `re.search()` | Match or None | `#@ requires True` / `#@ ensures True` |
| `re.sub()` | string | `#@ requires True` / `#@ ensures True` |

### `shutil`

| Call | Returns | Contract |
|------|---------|----------|
| `shutil.copy2()` | string (dest path) | `#@ requires True` / `#@ ensures True` |
| `shutil.rmtree()` | void | `#@ requires True` / `#@ ensures True` |
| `shutil.which()` | string or None | `#@ requires True` / `#@ ensures True` |

### `subprocess`

| Call | Returns | Contract |
|------|---------|----------|
| `subprocess.run()` | object (CompletedProcess) | `#@ requires True` / `#@ ensures True` |

### `sys`

| Call | Returns | Contract |
|------|---------|----------|
| `sys.exit()` | void (never returns) | `#@ requires True` / `#@ ensures True` |
| `sys.path.insert()` | void | `#@ requires True` / `#@ ensures True` |
| `sys.stdin.read()` | string | `#@ requires True` / `#@ ensures True` |
| `sys.stdout.write()` | int (bytes written) | `#@ requires True` / `#@ ensures \result >= 0` |

### `tempfile`

| Call | Returns | Contract |
|------|---------|----------|
| `tempfile.mkstemp()` | tuple (fd, path) | `#@ requires True` / `#@ ensures \result[0] >= 0` |
| `tempfile.NamedTemporaryFile()` | object (file) | `#@ requires True` / `#@ ensures True` |
| `tempfile.TemporaryDirectory()` | object (context mgr) | `#@ requires True` / `#@ ensures True` |

### `textwrap`

| Call | Returns | Contract |
|------|---------|----------|
| `textwrap.dedent()` | string | `#@ requires True` / `#@ ensures True` |
| `textwrap.indent()` | string | `#@ requires True` / `#@ ensures True` |

### `time`

| Call | Returns | Contract |
|------|---------|----------|
| `time.monotonic()` | float ≥ 0 | `#@ requires True` / `#@ ensures \result >= 0` |

### `tomllib`

| Call | Returns | Contract |
|------|---------|----------|
| `tomllib.load()` | object (dict) | `#@ requires True` / `#@ ensures True` |
| `tomllib.loads()` | object (dict) | `#@ requires True` / `#@ ensures True` |

### `unicodedata`

| Call | Returns | Contract |
|------|---------|----------|
| `unicodedata.normalize()` | string | `#@ requires True` / `#@ ensures True` |

### `urllib`

| Call | Returns | Contract |
|------|---------|----------|
| `urllib.request.Request()` | object (Request) | `#@ requires True` / `#@ ensures True` |
| `urllib.request.urlopen()` | object (HTTPResponse) | `#@ requires True` / `#@ ensures True` |

### `warnings`

| Call | Returns | Contract |
|------|---------|----------|
| `warnings.warn()` | void | `#@ requires True` / `#@ ensures True` |

---

## Third-Party Libraries

### `jsonschema`

| Call | Returns | Contract |
|------|---------|----------|
| `jsonschema.Draft7Validator()` | object (Validator) | `#@ requires True` / `#@ ensures True` |

### `lark`

| Call | Returns | Contract |
|------|---------|----------|
| `lark.Lark()` | object (parser) | `#@ requires True` / `#@ ensures True` |
| `lark.Lark.open()` | object (parser) | `#@ requires True` / `#@ ensures True` |
| `lark.v_args()` | object (decorator) | `#@ requires True` / `#@ ensures True` |

### `libcst`

| Call | Returns | Contract |
|------|---------|----------|
| `libcst.Comment()` | object (CST node) | `#@ requires True` / `#@ ensures True` |
| `libcst.EmptyLine()` | object (CST node) | `#@ requires True` / `#@ ensures True` |
| `libcst.MetadataWrapper()` | object (wrapper) | `#@ requires True` / `#@ ensures True` |
| `libcst.parse_module()` | object (CST Module) | `#@ requires True` / `#@ ensures True` |

### `mcp`

| Call | Returns | Contract |
|------|---------|----------|
| `mcp.server.fastmcp.FastMCP()` | object (MCP server) | `#@ requires True` / `#@ ensures True` |
| `mcp.run()` | void | `#@ requires True` / `#@ ensures True` |
| `mcp.tool()` | object (decorator) | `#@ requires True` / `#@ ensures True` |

### `numpy`

| Call | Returns | Contract |
|------|---------|----------|
| `numpy.argsort()` | object (ndarray) | `#@ requires True` / `#@ ensures True` |
| `numpy.array()` | object (ndarray) | `#@ requires True` / `#@ ensures True` |
| `numpy.linalg.norm()` | float ≥ 0 | `#@ requires True` / `#@ ensures \result >= 0` |

### `pytest`

| Call | Returns | Contract |
|------|---------|----------|
| `pytest.mark.parametrize()` | object (decorator) | `#@ requires True` / `#@ ensures True` |
| `pytest.mark.skipif()` | object (decorator) | `#@ requires True` / `#@ ensures True` |
| `pytest.raises()` | object (context mgr) | `#@ requires True` / `#@ ensures True` |
| `pytest.skip()` | void (raises Skipped) | `#@ requires True` / `#@ ensures True` |

### `tomli_w`

| Call | Returns | Contract |
|------|---------|----------|
| `tomli_w.dumps()` | string | `#@ requires True` / `#@ ensures True` |

---

## Summary

| Return category | Count | Contract pattern |
|----------------|-------|-----------------|
| object | 44 | `#@ ensures True` |
| string | 16 | `#@ ensures True` |
| void | 9 | `#@ ensures True` |
| bool | 4 | `#@ ensures \result == 0 or \result == 1` |
| int/float ≥ 0 | 3 | `#@ ensures \result >= 0` |
| tuple | 1 | `#@ ensures \result[0] >= 0` |
| **Total** | **77** | |
