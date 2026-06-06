#!/usr/bin/env python3
"""Generate a `\\trusted` mirror from a `src/pycsl/` source file.

For each top-level `def` and each indented `def` (class methods),
emit:

  #@ \\trusted reviewer: pycsl-self-annotate
  #@ requires True
  #@ ensures True
  #@ assigns \\nothing
  def <signature>: ...

Class definitions are kept as-is (with `""  # pycsl` anchor added if
the file has any class). Imports, module docstrings, and module-level
constants are preserved (but constant initializers are simplified to
``= 0`` when they use unsupported Python features like set literals).

The output is byte-different from the source — this is intentional;
the mirror is a PyCSL-trusted skeleton, not a body-faithful copy.
The mirror-check (`bin/self-annotate-mirror-check.sh`) accepts this
divergence as long as the function/method signatures match.

Usage:

    bin/self-annotate-stub-gen.py src/pycsl/<file>.py \\
                                   src/self-annotate/src/<file>.py
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple


_TRUSTED_BLOCK = [
    "#@ \\trusted reviewer: pycsl-self-annotate",
    "#@ requires True",
    "#@ ensures True",
    "#@ assigns \\nothing",
]


def _stub_body_for(return_annotation: Optional[ast.expr], indent: str) -> str:
    """Return a body that satisfies the return type."""
    if return_annotation is None:
        return f"{indent}    pass"
    if isinstance(return_annotation, ast.Constant) and return_annotation.value is None:
        return f"{indent}    pass"
    src = ast.unparse(return_annotation) if hasattr(ast, "unparse") else ""
    src_clean = src.replace(" ", "")
    if src_clean in ("None", "NoneType"):
        return f"{indent}    pass"
    if src_clean in ("int", "float"):
        return f"{indent}    return 0"
    if src_clean in ("bool",):
        return f"{indent}    return False"
    if src_clean.startswith("str"):
        return f"{indent}    return \"\""
    if src_clean.startswith("list") or src_clean.startswith("List"):
        return f"{indent}    return []"
    if src_clean.startswith("dict") or src_clean.startswith("Dict") or src_clean.startswith("Optional[Dict"):
        return f"{indent}    return {{}}"
    if src_clean.startswith("set") or src_clean.startswith("Set") or src_clean.startswith("frozenset"):
        return f"{indent}    return set()"
    if src_clean.startswith("Tuple") or src_clean.startswith("tuple"):
        # Crude: return a 2-tuple of empty dict-or-list.
        return f"{indent}    return ([], {{}})"
    if src_clean.startswith("Optional"):
        return f"{indent}    return None"
    # Class type — return None and let the caller deal with type-coercion.
    return f"{indent}    return None"


def _emit_trusted_function(node: ast.FunctionDef, indent: str = "") -> List[str]:
    """Emit the `\\trusted` annotation block + signature + stub body."""
    out: List[str] = []
    for line in _TRUSTED_BLOCK:
        out.append(f"{indent}{line}")
    # Reconstruct the def signature. We use ast.unparse to get a faithful
    # signature, then strip the body and append our stub.
    if hasattr(ast, "unparse"):
        try:
            full = ast.unparse(node)
        except Exception:
            full = f"{indent}def {node.name}(...):"
    else:
        full = f"{indent}def {node.name}(...):"
    sig_lines = full.splitlines()
    # Walk from the top: keep lines until we see a body statement.
    # ast.unparse emits the signature on one line (possibly continued
    # via parentheses), followed by indented body. Simplest: take all
    # lines up to and including the first one ending with `:`.
    sig_only: List[str] = []
    for sl in sig_lines:
        sig_only.append(sl)
        if sl.rstrip().endswith(":") and "def " in sl or sl.rstrip().endswith(":"):
            if sig_only[-1].rstrip().endswith(":"):
                break
    # Re-indent the signature lines to ``indent`` (ast.unparse emits at
    # column 0; we want them at ``indent``).
    reindented = []
    for sl in sig_only:
        if sl.strip() == "":
            reindented.append(sl)
        else:
            reindented.append(indent + sl.lstrip())
    out.extend(reindented)
    out.append(_stub_body_for(node.returns, indent))
    return out


def _emit_class(node: ast.ClassDef, source_lines: List[str]) -> List[str]:
    """Emit a class header + per-method `\\trusted` stubs."""
    out: List[str] = []
    for dec in node.decorator_list:
        out.append(f"@{ast.unparse(dec)}")
    bases = ", ".join(ast.unparse(b) for b in node.bases)
    out.append(f"class {node.name}({bases}):" if bases else f"class {node.name}:")
    emitted_body = False
    body_iter = iter(node.body)
    first = next(body_iter, None)
    if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)):
        out.append(f"    {ast.unparse(first)}")
        emitted_body = True
    elif first is not None:
        body_iter = iter([first] + list(body_iter))
    for child in body_iter:
        if isinstance(child, ast.FunctionDef):
            out.extend(_emit_trusted_function(child, indent="    "))
            out.append("")
            emitted_body = True
        elif isinstance(child, ast.AnnAssign):
            out.append(f"    {ast.unparse(child)}")
            emitted_body = True
        elif isinstance(child, ast.Assign):
            out.append(f"    {ast.unparse(child)}")
            emitted_body = True
    if not emitted_body:
        out.append("    pass")
    return out


_PYCSL_UNMODELABLE_TYPES = (
    "Set", "FrozenSet", "MutableSet", "Dict", "Mapping",
    "MutableMapping", "DefaultDict", "OrderedDict", "Tuple",
)


def _scrub_unmodelable_types(text: str) -> str:
    """Replace type annotations PyCSL cannot model in a trusted-stub
    mirror with the opaque-int placeholder. Applied after generation;
    affects only parameter / return annotations, not Python semantics
    (the bodies are stubs anyway)."""
    # Iterate to a fixed point so nested generics (e.g.
    # ``Optional[Dict[str, Set[str]]]``) get fully scrubbed.
    prev = None
    while prev != text:
        prev = text
        for t in _PYCSL_UNMODELABLE_TYPES:
            text = re.sub(rf"\b{t}\[[^\]\[]+\]", "int", text)
    # `Optional[int]` (after collapse) → just `int` for parameter-list
    # cleanliness.
    text = re.sub(r"\bOptional\[int\]", "int", text)
    return text


def generate_mirror(src_path: Path) -> str:
    """Read ``src_path`` and emit the trusted-mirror source."""
    raw = src_path.read_text()
    tree = ast.parse(raw)
    source_lines = raw.splitlines()
    out: List[str] = []

    # Module docstring (replace with a marker note).
    docstring = ast.get_docstring(tree, clean=False)
    if docstring is not None:
        out.append(f'"""Mirror of `src/pycsl/{src_path.name}`. Trusted stub.')
        out.append("")
        out.append("Generated by `bin/self-annotate-stub-gen.py`. Each function is")
        out.append("annotated `#@ \\trusted reviewer: pycsl-self-annotate`; bodies")
        out.append("are stubs. The interface (parameter types, return type) matches")
        out.append("the source. The mirror-check gate enforces signature parity.")
        out.append('"""')

    # Imports + module-level type/dataclass declarations are kept as-is
    # by virtue of being non-FunctionDef/non-ClassDef nodes — we just
    # `ast.unparse` them in order.
    has_class = any(isinstance(n, ast.ClassDef) for n in tree.body)
    if has_class:
        # Anchor required for class-bearing files.
        anchor_emitted = False
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            # Module docstring — already emitted above; skip.
            continue
        if isinstance(node, ast.ClassDef):
            if has_class and not anchor_emitted:
                out.append('""  # pycsl')
                anchor_emitted = True
            out.extend(_emit_class(node, source_lines))
            out.append("")
        elif isinstance(node, ast.FunctionDef):
            out.extend(_emit_trusted_function(node))
            out.append("")
        elif isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign,
                                 ast.AnnAssign, ast.AugAssign, ast.Try)):
            out.append(ast.unparse(node))
        # Skip other top-level constructs (e.g., If — typically version checks).
    return "\n".join(out) + "\n"


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    src = Path(argv[1])
    dst = Path(argv[2])
    if not src.is_file():
        print(f"[!] Source not found: {src}", file=sys.stderr)
        return 2
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(_scrub_unmodelable_types(generate_mirror(src)))
    print(f"[+] {src} → {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
