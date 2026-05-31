#!/usr/bin/env python3
"""Generate PyCSL stub files from test-suite/library_reference/*.rst.

Reads RST documentation files, extracts ``.. function::`` directives,
and emits ``src/pycsl_lib/<module>.py`` stubs with ``#@ \\trusted``
annotations and semantic postconditions derived from the English
descriptions. The directory was renamed from ``data/lib_stubs/`` to
``src/pycsl_lib/`` per the StdlibCoverage workplan PR 3.
"""
import os
import re
import sys
import keyword

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RST_DIR = os.path.join(REPO, "test-suite", "library_reference")
LIB_DIR = os.path.join(REPO, "src", "pycsl_lib")

MAX_PARAMS = 7  # PyCSL transpiler limit

# RST files that are NOT importable modules (category/overview/example pages)
NON_MODULE_RSTS = {
    "index", "intro", "allos", "binary", "concurrency", "datatypes",
    "filesys", "functional", "frameworks", "development", "debug",
    "distribution", "i18n", "internet", "ipc", "language", "markup",
    "mm", "modules", "netdata", "numeric", "persistence", "python",
    "text", "tk", "unix", "windows", "cmdline", "cmdlinelibs",
    "custominterp", "fileformats", "archiving", "compression", "crypto",
    "removed", "superseded", "security_warnings", "audit_events",
    "stdtypes", "functions", "constants", "exceptions", "devmode", "idle",
    "threadsafety", "sys_path_init", "dialog", "profiling",
    "email.examples", "unittest.mock-examples",
}

# asyncio sub-pages that are not separate importable modules
ASYNCIO_SUBPAGES = {
    "asyncio-api-index", "asyncio-dev", "asyncio-eventloop",
    "asyncio-exceptions", "asyncio-extending", "asyncio-future",
    "asyncio-graph", "asyncio-llapi-index", "asyncio-platforms",
    "asyncio-policy", "asyncio-protocol", "asyncio-queue",
    "asyncio-runner", "asyncio-stream", "asyncio-subprocess",
    "asyncio-sync", "asyncio-task",
}

# Image/diagram files that snuck into the RST directory
IMAGE_PATTERNS = re.compile(
    r"^(datetime-|hashlib-|heapq-|pathlib-|turtle-|tachyon-|"
    r"token-list|kde_example|profiling\.|tk_msg)"
)

# WhyML reserved words that cannot be used as parameter names
WHYML_RESERVED = {
    "val", "let", "in", "if", "then", "else", "match", "with",
    "end", "begin", "fun", "function", "rec", "type", "use",
    "module", "theory", "goal", "axiom", "lemma", "predicate",
    "forall", "exists", "true", "false", "not", "mod", "any",
    "abstract", "assert", "clone", "import", "export", "raises",
    "reads", "writes", "alias", "diverges", "pure", "old", "at",
    "result", "void", "ref", "mutable", "ghost", "model",
    "epsilon", "label", "ensures", "requires", "invariant",
    "variant", "returns", "exception", "raise", "try",
    "absurd", "check", "assume", "by", "so",
}

# Python keywords/builtins that clash
PYTHON_CLASH = {"lambda", "yield", "class", "return", "import", "from",
                "global", "nonlocal", "del", "pass", "break", "continue",
                "and", "or", "not", "is", "in", "as", "with", "try",
                "except", "finally", "raise", "assert", "True", "False",
                "None", "async", "await", "type", "match"}

RESERVED = WHYML_RESERVED | PYTHON_CLASH | set(keyword.kwlist)


def _safe_param(name: str) -> str:
    """Make a parameter name safe for both Python and WhyML."""
    name = name.strip().lstrip("*")
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    if not name or name[0].isdigit():
        name = "p_" + name
    if name in RESERVED or keyword.iskeyword(name):
        name = name + "_"
    return name


def _extract_synopsis(rst_text: str) -> str:
    """Extract the :synopsis: line from the RST module directive."""
    m = re.search(r":synopsis:\s*(.+)", rst_text)
    if m:
        return m.group(1).strip().rstrip(".")
    # Fallback: use the title
    m = re.search(r"^:mod:`[^`]*`\s*---\s*(.+)$", rst_text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return ""


def _parse_functions(rst_text: str):
    """Yield (name, params_str, description) from ``.. function::`` directives."""
    lines = rst_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^\.\.\s+function::\s+(\w+)\s*\((.*)$", line)
        if not m:
            i += 1
            continue
        name = m.group(1)
        # Collect full signature (may span multiple lines if parens are nested)
        sig_rest = m.group(2)
        depth = 1  # we already consumed the opening '('
        for ch in sig_rest:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
        # If parens aren't balanced, consume continuation lines
        j = i + 1
        while depth > 0 and j < len(lines):
            for ch in lines[j]:
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
            sig_rest += " " + lines[j].strip()
            j += 1
        # Strip trailing ) and anything after
        params_str = re.sub(r"\)\s*$", "", sig_rest).strip()
        # Move past signature lines and any alias lines (``.. function:: alias(...)``)
        i = j
        while i < len(lines) and re.match(r"^\s+\w+\(", lines[i]):
            i += 1
        # Extract description: indented block after the directive
        desc_lines = []
        while i < len(lines):
            ln = lines[i]
            if ln == "":
                if desc_lines:
                    desc_lines.append("")
                i += 1
                continue
            if ln.startswith("   ") or ln.startswith("\t"):
                desc_lines.append(ln.strip())
                i += 1
            else:
                break
        desc = " ".join(l for l in desc_lines if l).strip()
        if ":noindex:" in desc:
            continue
        yield name, params_str, desc


def _parse_params(params_str: str):
    """Parse parameter string into list of clean parameter names."""
    if not params_str.strip():
        return []
    # Strip RST optional-parameter brackets: log(x[, base]) -> log(x, base)
    params_str = params_str.replace("[", "").replace("]", "")
    # Remove type annotations like `: int`, default values like `=0`
    # and keyword-only markers like `*`
    params = []
    depth = 0
    current = ""
    for ch in params_str:
        if ch in "([":
            depth += 1
            current += ch
        elif ch in ")]":
            depth -= 1
            current += ch
        elif ch == "," and depth == 0:
            params.append(current.strip())
            current = ""
        else:
            current += ch
    if current.strip():
        params.append(current.strip())

    clean = []
    for p in params:
        p = p.strip()
        if p in ("*", "/", "\\"):
            continue
        if p.startswith("**"):
            continue  # skip **kwargs
        if p.startswith("*") and "=" not in p:
            continue  # skip bare *args unless it has a name with default
        # Remove default value
        p = p.split("=")[0].strip()
        # Remove type annotation
        p = p.split(":")[0].strip()
        # Remove leading * for keyword-only
        p = p.lstrip("*")
        if not p:
            continue
        clean.append(_safe_param(p))
    return clean[:MAX_PARAMS]


def _strip_rst(text: str) -> str:
    """Strip RST inline markup (backticks, emphasis, cross-refs) for keyword matching."""
    text = re.sub(r":[\w.]+:`[^`]*`", "", text)  # :func:`...`, :class:`...`
    text = re.sub(r"``([^`]*)``", r"\1", text)    # ``literal``
    text = re.sub(r"`([^`]*)`", r"\1", text)      # `ref`
    text = re.sub(r"\*\*([^*]*)\*\*", r"\1", text) # **bold**
    text = re.sub(r"\*([^*]*)\*", r"\1", text)     # *emphasis*
    return text


def _infer_annotation(name: str, desc: str, params: list) -> tuple:
    """Infer (requires_list, ensures_str) from function name and description.
    
    Returns a tuple of (list_of_requires, ensures_string).
    """
    desc_clean = _strip_rst(desc)
    desc_lower = desc_clean.lower()
    requires = []
    ensures = None

    # --- Boolean / check / test functions ---
    is_bool = (
        re.search(r"\breturn\s+(true|false)\b", desc_lower)
        or re.search(r"\breturn\s+whether\b", desc_lower)
        or re.search(r"\bcheck\s+(if|whether)\b", desc_lower)
        or name.startswith(("is", "has", "can"))
    )
    if is_bool:
        ensures = "\\result == 0 or \\result == 1"

    # --- Math-specific ---
    if name == "ceil" and params:
        ensures = f"\\result >= {params[0]}"
    elif name == "floor" and params:
        ensures = f"\\result <= {params[0]}"
    elif name in ("fabs", "abs") and params:
        ensures = "\\result >= 0"
    elif name == "sqrt" and params:
        requires.append(f"{params[0]} >= 0")
        ensures = "\\result >= 0"
    elif name in ("factorial",) and params:
        requires.append(f"{params[0]} >= 0")
        ensures = "\\result >= 1"
    elif name in ("comb", "perm") and len(params) >= 2:
        requires.extend([f"{params[0]} >= 0", f"{params[1]} >= 0"])
        ensures = "\\result >= 0"
    elif name in ("gcd", "lcm"):
        ensures = "\\result >= 0"
    elif name == "exp" and params:
        ensures = "\\result >= 0"
    elif name == "exp2" and params:
        ensures = "\\result >= 0"
    elif name in ("log", "log2", "log10", "log1p") and params:
        requires.append(f"{params[0]} >= 0")
    elif name == "pow" and len(params) >= 2:
        pass  # too complex to constrain generically
    elif name == "hypot":
        ensures = "\\result >= 0"
    elif name == "dist" and len(params) >= 2:
        ensures = "\\result >= 0"

    # --- Non-negative returns (size, length, count, index, PID, fd) ---
    if ensures is None:
        if re.search(
            r"\b(length|size|count|number of|index|offset|position|"
            r"pid|process id|file descriptor|fd|port|"
            r"non-negative|nonnegative|>= 0|≥ 0)\b",
            desc_lower,
        ):
            ensures = "\\result >= 0"

    # --- Side-effect only (no meaningful return) ---
    if ensures is None:
        if (re.search(r"\b(set|write|send|close|delete|remove|clear|flush|"
                      r"reset|register|unregister|install|configure|"
                      r"print|terminate|kill|stop|start|pause|resume|"
                      r"lock|unlock|acquire|release|notify|wait|join|"
                      r"seed|init|setup|shutdown|destroy|detach|"
                      r"append|extend|insert|sort|reverse|update|pop|"
                      r"push|put|add)\b", desc_lower)
                and not re.search(r"\breturn\b", desc_lower)):
            ensures = "\\result == 0"

    # --- Fallback: generic non-negative for "return" mentions ---
    if ensures is None:
        if re.search(r"\breturn\b", desc_lower):
            ensures = "\\result >= 0"

    # --- Final fallback ---
    if ensures is None:
        ensures = "\\result >= 0"

    return requires, ensures


def _generate_stub(module_name: str, rst_path: str) -> str:
    """Generate the full .py stub content for a module."""
    with open(rst_path, "r", encoding="utf-8", errors="replace") as f:
        rst_text = f.read()

    synopsis = _extract_synopsis(rst_text)
    if not synopsis:
        synopsis = f"PyCSL trusted stubs for {module_name}"

    lines = [f'"""PyCSL mock for Python\'s {module_name} module — {synopsis}."""']
    lines.append('_ = 0  # anchor')
    lines.append("")

    seen_names = set()
    func_count = 0

    for fname, params_str, desc in _parse_functions(rst_text):
        if fname in seen_names:
            continue
        seen_names.add(fname)

        params = _parse_params(params_str)
        requires_list, ensures = _infer_annotation(fname, desc, params)

        # Build parameter list with type annotations
        param_strs = [f"{p}: int" for p in params]
        param_sig = ", ".join(param_strs)

        # Build contract annotations
        lines.append("#@ \\trusted")
        for req in requires_list:
            lines.append(f"#@ requires {req}")
        if ensures:
            lines.append(f"#@ ensures {ensures}")

        # Build function signature
        # Truncate description for docstring
        short_desc = desc[:120].replace('"', "'") if desc else f"Mock: {fname}"
        if len(desc) > 120:
            short_desc += "..."

        lines.append(f"def {fname}({param_sig}) -> int:")
        lines.append(f'    """Mock: {short_desc}"""')
        lines.append("    return 0")
        lines.append("")
        func_count += 1

    if func_count == 0:
        lines.append("# No functions extracted from RST; module may be class-based or overview-only.")
        lines.append("")

    return "\n".join(lines)


def _module_to_path(module_name: str) -> str:
    """Convert dotted module name to filesystem path under Lib/.
    
    e.g., 'os.path' -> 'Lib/os/path.py'
         'os'      -> 'Lib/os.py'
    """
    parts = module_name.split(".")
    if len(parts) == 1:
        return os.path.join(LIB_DIR, parts[0] + ".py")
    else:
        # Sub-module: create directory structure
        return os.path.join(LIB_DIR, *parts[:-1], parts[-1] + ".py")


def _ensure_init_files(path: str):
    """Create __init__.py files for all parent package directories."""
    dirpath = os.path.dirname(path)
    while dirpath != LIB_DIR and dirpath.startswith(LIB_DIR):
        init = os.path.join(dirpath, "__init__.py")
        if not os.path.exists(init):
            pkg_name = os.path.relpath(dirpath, LIB_DIR).replace(os.sep, ".")
            with open(init, "w") as f:
                f.write(f'"""PyCSL mock for {pkg_name} package."""\n')
                f.write("_ = 0  # anchor\n")
        dirpath = os.path.dirname(dirpath)


def _rst_to_module_name(rst_stem: str) -> str:
    """Convert RST filename stem to Python module name.
    
    Most map directly: 'os' -> 'os', 'os.path' -> 'os.path'
    Special cases: '__future__' -> '__future__', '_thread' -> '_thread'
    """
    return rst_stem


def main():
    import argparse

    ap = argparse.ArgumentParser(
        description="Generate PyCSL stub files from test-suite/library_reference/*.rst."
    )
    ap.add_argument(
        "--skip-existing",
        action="store_true",
        help="Do not overwrite stubs that already exist under "
        "src/pycsl_lib/. Use this for incremental scaffolding "
        "(preserves hand-curated contracts on existing stubs). "
        "Default off — full regeneration overwrites everything.",
    )
    args = ap.parse_args()

    os.makedirs(LIB_DIR, exist_ok=True)

    # Collect all RST stems
    rst_files = sorted(f[:-4] for f in os.listdir(RST_DIR) if f.endswith(".rst"))

    generated = 0
    preserved = 0
    skipped = 0
    errors = []

    for stem in rst_files:
        # Skip non-module RSTs
        if stem in NON_MODULE_RSTS:
            skipped += 1
            continue
        if stem in ASYNCIO_SUBPAGES:
            skipped += 1
            continue
        if IMAGE_PATTERNS.match(stem):
            skipped += 1
            continue

        module_name = _rst_to_module_name(stem)
        rst_path = os.path.join(RST_DIR, stem + ".rst")
        out_path = _module_to_path(module_name)

        # --skip-existing: preserve hand-curated stubs in place
        if args.skip_existing and os.path.exists(out_path):
            preserved += 1
            continue

        try:
            content = _generate_stub(module_name, rst_path)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            _ensure_init_files(out_path)
            with open(out_path, "w") as f:
                f.write(content)
            generated += 1
        except Exception as e:
            errors.append((module_name, str(e)))

    print(f"Generated: {generated} stubs")
    if args.skip_existing:
        print(f"Preserved: {preserved} existing stubs (--skip-existing)")
    print(f"Skipped:   {skipped} non-module RSTs")
    if errors:
        print(f"Errors:    {len(errors)}")
        for mod, err in errors:
            print(f"  {mod}: {err}")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
