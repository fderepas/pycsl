# Library Method Calls — English Descriptions

Every method or constructor from a Python standard-library or third-party
package that is called inside `src/`.

---

## Standard Library

### `argparse`

| Call | Description |
|------|-------------|
| `argparse.ArgumentParser()` | Create a command-line argument parser that defines expected flags, positional arguments, and help text. |

### `ast`

| Call | Description |
|------|-------------|
| `ast.dump()` | Return a formatted string representation of an AST node tree, useful for debugging. |
| `ast.iter_child_nodes()` | Yield all direct child nodes of a given AST node. |
| `ast.parse()` | Parse a Python source string into an abstract syntax tree (AST). |
| `ast.walk()` | Recursively yield every node in an AST tree in breadth-first order. |

### `collections`

| Call | Description |
|------|-------------|
| `collections.Counter()` | Create a dictionary-like object that counts hashable elements from an iterable. |
| `collections.defaultdict()` | Create a dictionary that returns a default value for missing keys, using a supplied factory function. |

### `dataclasses`

| Call | Description |
|------|-------------|
| `dataclasses.asdict()` | Recursively convert a dataclass instance into a plain dictionary. |
| `dataclasses.dataclass()` | Class decorator that auto-generates `__init__`, `__repr__`, `__eq__`, and other special methods from annotated fields. |
| `dataclasses.field()` | Specify per-field metadata such as default values, default factories, or repr inclusion for a dataclass. |

### `datetime`

| Call | Description |
|------|-------------|
| `datetime.datetime.fromisoformat()` | Parse an ISO-8601 date-time string (e.g. `"2025-01-15T10:30:00"`) into a `datetime` object. |
| `datetime.datetime.now()` | Return the current local date and time as a `datetime` object. |

### `hashlib`

| Call | Description |
|------|-------------|
| `hashlib.sha256()` | Create a SHA-256 hash object for computing a cryptographic digest of data. |

### `importlib`

| Call | Description |
|------|-------------|
| `importlib.util.module_from_spec()` | Create a new module object from a previously obtained module spec. |
| `importlib.util.spec_from_file_location()` | Build a module spec that locates a module by its file-system path rather than by package name. |

### `json`

| Call | Description |
|------|-------------|
| `json.dumps()` | Serialize a Python object (dict, list, etc.) into a JSON-formatted string. |
| `json.load()` | Read a JSON document from an open file object and deserialize it into a Python object. |
| `json.loads()` | Deserialize a JSON string into a Python object. |

### `os`

| Call | Description |
|------|-------------|
| `os.access()` | Test whether the current process has the specified access permission (read, write, execute) on a path. |
| `os.close()` | Close a file descriptor obtained from a low-level open call (e.g. `os.open` or `tempfile.mkstemp`). |
| `os.environ.get()` | Return the value of an environment variable, or a default if the variable is not set. |
| `os.getcwd()` | Return the absolute path of the current working directory. |
| `os.listdir()` | Return a list of names of entries in a given directory. |
| `os.makedirs()` | Create a directory and all necessary intermediate parent directories. |
| `os.remove()` | Delete a single file from the file system. |
| `os.unlink()` | Delete a single file from the file system (synonym of `os.remove`). |

### `os.path`

| Call | Description |
|------|-------------|
| `os.path.abspath()` | Return the absolute version of a path by prepending the current working directory if needed. |
| `os.path.basename()` | Return the final component (file name) of a path string. |
| `os.path.dirname()` | Return the directory component of a path string, stripping the final file name. |
| `os.path.exists()` | Return `True` if the given path exists on the file system. |
| `os.path.expanduser()` | Replace a leading `~` or `~user` in a path with the user's home directory. |
| `os.path.isdir()` | Return `True` if the path points to an existing directory. |
| `os.path.isfile()` | Return `True` if the path points to an existing regular file. |
| `os.path.join()` | Join one or more path components with the OS-appropriate separator (`/` or `\`). |
| `os.path.normpath()` | Normalize a path by collapsing redundant separators and up-level `..` references. |
| `os.path.splitext()` | Split a path into a root and an extension (e.g. `("script", ".py")`). |

### `pathlib`

| Call | Description |
|------|-------------|
| `pathlib.Path()` | Construct an object-oriented filesystem path that supports cross-platform path operations. |
| `pathlib.Path.cwd()` | Return a new `Path` pointing to the current working directory. |
| `pathlib.Path.home()` | Return a new `Path` pointing to the current user's home directory. |

### `re`

| Call | Description |
|------|-------------|
| `re.compile()` | Compile a regular-expression pattern string into a reusable pattern object for faster repeated matching. |
| `re.escape()` | Escape all special regex metacharacters in a string so it can be used as a literal pattern. |
| `re.findall()` | Return a list of all non-overlapping matches of a pattern in a string. |
| `re.finditer()` | Return an iterator of `Match` objects for every non-overlapping match of a pattern in a string. |
| `re.fullmatch()` | Return a `Match` object only if the entire string matches the pattern, otherwise `None`. |
| `re.match()` | Try to match a pattern at the beginning of a string; return a `Match` object or `None`. |
| `re.search()` | Scan through a string looking for the first location where the pattern matches; return a `Match` or `None`. |
| `re.sub()` | Return a string with all occurrences of a pattern replaced by a replacement string or function result. |

### `shutil`

| Call | Description |
|------|-------------|
| `shutil.copy2()` | Copy a file to a destination, preserving both content and file metadata (timestamps, permissions). |
| `shutil.rmtree()` | Recursively delete an entire directory tree. |
| `shutil.which()` | Search the system `PATH` for an executable and return its full path, or `None` if not found. |

### `subprocess`

| Call | Description |
|------|-------------|
| `subprocess.run()` | Run a command as a child process, wait for it to complete, and return a `CompletedProcess` with stdout/stderr/returncode. |

### `sys`

| Call | Description |
|------|-------------|
| `sys.exit()` | Exit the Python interpreter with an optional exit code (0 = success, non-zero = error). |
| `sys.path.insert()` | Insert a directory into the module search path at a given index so that `import` can find modules there. |
| `sys.stdin.read()` | Read all remaining data from standard input as a string. |
| `sys.stdout.write()` | Write a string to standard output without appending a newline. |

### `tempfile`

| Call | Description |
|------|-------------|
| `tempfile.mkstemp()` | Create a temporary file in the safest manner possible; return `(fd, path)` — a file descriptor and its absolute path. |
| `tempfile.NamedTemporaryFile()` | Create a temporary file that has a visible name in the file system and is deleted when closed. |
| `tempfile.TemporaryDirectory()` | Create a temporary directory that is automatically removed when the context manager exits. |

### `textwrap`

| Call | Description |
|------|-------------|
| `textwrap.dedent()` | Remove any common leading whitespace from all lines of a multi-line string. |
| `textwrap.indent()` | Add a given prefix string to the beginning of every line of a text block. |

### `time`

| Call | Description |
|------|-------------|
| `time.monotonic()` | Return the value of a monotonic clock (seconds), which cannot go backward — ideal for measuring elapsed time. |

### `tomllib`

| Call | Description |
|------|-------------|
| `tomllib.load()` | Read and parse a TOML document from an open binary file object into a Python dictionary. |
| `tomllib.loads()` | Parse a TOML-formatted string into a Python dictionary. |

### `unicodedata`

| Call | Description |
|------|-------------|
| `unicodedata.normalize()` | Convert a Unicode string to a specified normal form (`NFC`, `NFD`, `NFKC`, or `NFKD`). |

### `urllib`

| Call | Description |
|------|-------------|
| `urllib.request.Request()` | Construct an HTTP request object with a URL, optional data payload, headers, and method. |
| `urllib.request.urlopen()` | Open a URL (or `Request` object) and return a file-like HTTP response for reading. |

### `warnings`

| Call | Description |
|------|-------------|
| `warnings.warn()` | Issue a warning message that can be filtered, suppressed, or turned into an error by the warnings framework. |

---

## Third-Party Libraries

### `jsonschema`

| Call | Description |
|------|-------------|
| `jsonschema.Draft7Validator()` | Create a JSON Schema validator using the Draft 7 specification to check that data conforms to a schema. |

### `lark`

| Call | Description |
|------|-------------|
| `lark.Lark()` | Instantiate a Lark parser from an EBNF grammar string, choosing an algorithm (Earley, LALR, etc.). |
| `lark.Lark.open()` | Create a Lark parser by reading an EBNF grammar from a file path. |
| `lark.v_args()` | Decorator that controls how matched rule arguments are passed to Transformer methods (inline, tree, etc.). |

### `libcst`

| Call | Description |
|------|-------------|
| `libcst.Comment()` | Construct a CST node representing a Python comment token. |
| `libcst.EmptyLine()` | Construct a CST node representing a blank or comment-only line in source code. |
| `libcst.MetadataWrapper()` | Wrap a CST module so that metadata providers (position, scope, etc.) can be resolved on the tree. |
| `libcst.parse_module()` | Parse a Python source string into a full Concrete Syntax Tree that preserves comments and formatting. |

### `mcp`

| Call | Description |
|------|-------------|
| `mcp.server.fastmcp.FastMCP()` | Create an MCP (Model Context Protocol) server instance that can register tools for LLM agents. |
| `mcp.run()` | Start the MCP server event loop, listening for tool-call requests from clients. |
| `mcp.tool()` | Decorator that registers a Python function as a callable tool in the MCP server. |

### `numpy`

| Call | Description |
|------|-------------|
| `numpy.argsort()` | Return the indices that would sort an array in ascending order. |
| `numpy.array()` | Create an N-dimensional array from a list, tuple, or other sequence. |
| `numpy.linalg.norm()` | Compute the norm (e.g. Euclidean length) of a vector or matrix. |

### `pytest`

| Call | Description |
|------|-------------|
| `pytest.mark.parametrize()` | Decorator that generates multiple test invocations, one for each set of parameter values. |
| `pytest.mark.skipif()` | Decorator that skips a test if a given condition is `True`. |
| `pytest.raises()` | Context manager that asserts a block of code raises a specified exception type. |
| `pytest.skip()` | Unconditionally skip the current test with an optional reason message. |

### `tomli_w`

| Call | Description |
|------|-------------|
| `tomli_w.dumps()` | Serialize a Python dictionary into a TOML-formatted string. |

---

## Summary

| Category | Modules | Unique Calls |
|----------|---------|-------------|
| Standard library | 17 | 60 |
| Third-party | 6 | 15 |
| **Total** | **23** | **75** |
