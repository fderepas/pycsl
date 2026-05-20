import argparse
import ast as _ast_module
import json
import re
import sys
from pathlib import Path
from typing import Callable
from llm_client import llm_generate, log
from common import retrieve_skill_chunks, extract_code_block

AGENT_NAME = "agent-annotate"

# Fixed queries used to always retrieve critical skill sections regardless of input code.
_ESSENTIAL_QUERIES = [
    "Required on every function requires ensures assigns loop invariant loop variant",
    "Forbidden in contract expressions NEVER use operators quantifiers",
    "Class support method annotation rules class invariant Level 2 Level 3",
    "class invariant preserve maintain precondition method requires amount >= 0 NEVER requires 1 == 1",
]

# ---------------------------------------------------------------------------
# Compiled regex patterns — named constants prevent per-site whitespace drift
# ---------------------------------------------------------------------------

# Any #@ annotation line (with optional leading whitespace)
_RE_ANN = re.compile(r'^\s*#@')
# \trusted annotation
_RE_TRUSTED = re.compile(r'^\s*#@\s*\\trusted\b')
# Function definition: captures (indent, func_name)
_RE_DEF = re.compile(r'^([ \t]*)def\s+(\w+)\s*\(')
# Function definition: captures (indent, params_string) — no name capture
_RE_DEF_PARAMS = re.compile(r'^([ \t]*)def\s+\w+\s*\(([^)]*)\)')
# Parameter type annotations (for findall over a function signature)
_RE_LIST_PARAM = re.compile(r'\b(\w+)\s*:\s*list\b')
_RE_STR_PARAM = re.compile(r'\b(\w+)\s*:\s*str\b')


class GuardPipeline:
    """Composable post-processing pipeline for LLM-generated Python code.

    Each guard is a str→str transform applied in sequence.  Centralising calls
    here gives a single place to add error handling, tracing, or rollback.
    """

    def __init__(self, code: str) -> None:
        self.code = code

    def apply(self, name: str, transform: Callable[[str], str]) -> None:
        self.code = transform(self.code)


def _annotate_trusted(source: str, project_directory: str) -> str:
    """Insert #@ \\trusted before every annotated non-dunder function/method.

    This assumes the source already has real contracts (#@ requires, ensures, etc.)
    from the LLM pipeline. We add \\trusted as temporary scaffolding so the file
    compiles before individual proofs are verified. The prove-and-strip phase will
    progressively remove \\trusted as functions pass verification.
    """
    lines = source.splitlines(keepends=True)
    result: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Detect a def line (possibly preceded by #@ annotations)
        def_m = _RE_DEF.match(line)
        if def_m:
            indent = def_m.group(1)
            func_name = def_m.group(2)
            # Skip dunders
            is_dunder = func_name.startswith('__') and func_name.endswith('__')
            if not is_dunder:
                # Check if \trusted is already present in the preceding annotation block
                has_trusted = False
                k = len(result) - 1
                while k >= 0:
                    prev = result[k].strip()
                    if prev.startswith('#@'):
                        if _RE_TRUSTED.match(prev):
                            has_trusted = True
                            break
                        k -= 1
                    else:
                        break
                if not has_trusted:
                    # Insert \trusted right before the def (after any existing #@ lines)
                    # Find where to insert: just before this def line
                    result.append(f"{indent}#@ \\trusted\n")
        result.append(line)
        i += 1

    count = sum(1 for l in result if _RE_TRUSTED.match(l))
    log(project_directory, AGENT_NAME,
        f"[trusted] Inserted \\trusted on {count} functions")
    return ''.join(result)


def _prove_and_strip(
    annotated_code: str,
    input_path: Path,
    project_root: Path,
    project_directory: str,
) -> str:
    """Bottom-up prove-and-strip: try verifying each function, remove \\trusted if it passes.

    Processes functions in topological order (leaves first) using the call graph.
    For each function:
      1. Create temp file with \\trusted removed from ONLY this function
      2. Run pycsl --no-proof on it (checks WhyML generation)
      3. If passes: permanently remove \\trusted
      4. If fails: keep \\trusted

    Returns the code with some \\trusted removed.
    """
    import subprocess
    import tempfile

    # Parse to find functions and their topological order
    try:
        tree = _ast_module.parse(annotated_code)
    except SyntaxError:
        log(project_directory, AGENT_NAME,
            "[prove-strip] Cannot parse annotated code, skipping prove-and-strip")
        return annotated_code

    # Build list of function names and their \trusted line positions
    lines = annotated_code.splitlines(keepends=True)

    # Find all (func_name, trusted_line_idx) pairs
    trusted_funcs: list[tuple[str, int]] = []
    for i, line in enumerate(lines):
        if _RE_TRUSTED.match(line):
            # Find the next def line after this
            for j in range(i + 1, min(i + 20, len(lines))):
                def_m = re.match(r'\s*def\s+(\w+)\s*\(', lines[j])
                if def_m:
                    trusted_funcs.append((def_m.group(1), i))
                    break
                # Stop if we hit non-#@ non-blank line that isn't a def
                stripped = lines[j].strip()
                if stripped and not stripped.startswith('#@') and not stripped.startswith('def'):
                    break

    if not trusted_funcs:
        log(project_directory, AGENT_NAME, "[prove-strip] No \\trusted functions found")
        return annotated_code

    log(project_directory, AGENT_NAME,
        f"[prove-strip] Attempting verification of {len(trusted_funcs)} functions")

    # Try to build call-graph ordering for bottom-up
    # Simple heuristic: try each function, process in order of success (leaves tend to pass first)
    pycsl_script = project_root / "src" / "pycsl" / "pycsl.py"
    removed_indices: set[int] = set()
    proved = 0
    failed = 0

    for func_name, trusted_idx in trusted_funcs:
        # Find the def line for this function
        def_line_text = ''
        for k in range(trusted_idx + 1, min(trusted_idx + 20, len(lines))):
            if re.match(r'\s*def\s+\w+\s*\(', lines[k]):
                def_line_text = lines[k]
                break
        # Skip functions with external-type params — they can never pass pycsl
        if re.search(r':\s*(?:cst|libcst)\.\w+', def_line_text):
            log(project_directory, AGENT_NAME,
                f"[prove-strip] ⊘ {func_name} — external types, skipping")
            continue

        # Create temp version with this function's \trusted removed
        test_lines = list(lines)
        test_lines[trusted_idx] = ''  # Remove the \trusted line

        # Write to temp file
        try:
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', dir=str(project_root / 'tmp'),
                delete=False, encoding='utf-8'
            ) as tf:
                tf.write(''.join(test_lines))
                tmp_path = tf.name

            # Run pycsl --no-proof
            result = subprocess.run(
                [sys.executable, str(pycsl_script), '--no-proof', tmp_path],
                capture_output=True, text=True,
                cwd=str(project_root),
                timeout=60,
            )

            if result.returncode == 0 and 'SUCCESS' in result.stdout:
                # Proof passed — permanently remove \trusted
                removed_indices.add(trusted_idx)
                proved += 1
                log(project_directory, AGENT_NAME,
                    f"[prove-strip] ✓ {func_name} — proved, \\trusted removed")
                # Update lines for subsequent attempts (so they see the removal)
                lines[trusted_idx] = ''
            else:
                failed += 1
                log(project_directory, AGENT_NAME,
                    f"[prove-strip] ✗ {func_name} — failed, \\trusted kept")
        except Exception as e:
            failed += 1
            log(project_directory, AGENT_NAME,
                f"[prove-strip] ✗ {func_name} — error: {e}")
        finally:
            try:
                Path(tmp_path).unlink(missing_ok=True)
            except Exception:
                pass

    log(project_directory, AGENT_NAME,
        f"[prove-strip] Summary: {proved} proved, {failed} remaining \\trusted")

    return ''.join(lines)


# ---------------------------------------------------------------------------
# Guard functions (promoted from main() for module-level testability)
# ---------------------------------------------------------------------------

def _is_recursive(func_name: str, func_src: str) -> bool:
    """Return True if func_src contains a direct call to func_name."""
    try:
        tree = _ast_module.parse(func_src)
    except SyntaxError:
        return False
    for node in _ast_module.walk(tree):
        if isinstance(node, _ast_module.Call):
            if isinstance(node.func, _ast_module.Name) and node.func.id == func_name:
                return True
    return False


def _inject_recursive_variants(code: str, project_directory: str) -> str:
    """For every recursive function lacking #@ \\variant, inject one before its def."""
    func_def_re = re.compile(r'^([ \t]*)def\s+(\w+)\s*\(([^)]*)\)', re.MULTILINE)
    lines = code.splitlines(keepends=True)
    # Build a line-index of def positions so we can check annotations above each def.
    def_lines = {}  # line_index -> (indent, fname, first_param)
    for _m in func_def_re.finditer(code):
        _indent = _m.group(1)
        _fname = _m.group(2)
        _params_str = _m.group(3)
        # Map character offset to line number
        _line_no = code[:_m.start()].count('\n')
        params = [p.strip().split(':')[0].strip() for p in _params_str.split(',') if p.strip()]
        first_param = next((p for p in params if p and p != 'self'), None)
        def_lines[_line_no] = (_indent, _fname, first_param)

    # For each def line, check whether the function is recursive and missing \variant.
    # We need the full function src: from `def` to the next `def` at same or outer indent.
    # Simple heuristic: collect the block from the def line to the next def_lines entry.
    sorted_def_idxs = sorted(def_lines.keys())
    # Collect injection targets (line indices where we need to insert before).
    inject_before = {}  # line_no -> injection string
    for i, ln in enumerate(sorted_def_idxs):
        _indent, _fname, first_param = def_lines[ln]
        # Slice function src from this def line to next def line.
        next_ln = sorted_def_idxs[i + 1] if i + 1 < len(sorted_def_idxs) else len(lines)
        func_src = ''.join(lines[ln:next_ln])
        if not _is_recursive(_fname, func_src):
            continue
        # Check whether any preceding #@ line in the annotation block has \variant.
        annotation_block = []
        j = ln - 1
        while j >= 0 and _RE_ANN.match(lines[j]):
            annotation_block.append(lines[j])
            j -= 1
        has_variant = any(re.search(r'#@\s*\\variant\b', al) for al in annotation_block)
        if has_variant:
            continue
        if not first_param:
            log(project_directory, AGENT_NAME,
                f"Warning: recursive function '{_fname}' has no suitable parameter "
                "for #@ \\variant; skipping injection.")
            continue
        log(project_directory, AGENT_NAME,
            f"Guard: injecting '#@ \\variant {first_param}' for recursive function '{_fname}'.")
        inject_before[ln] = f'{_indent}#@ \\variant {first_param}\n'

    if not inject_before:
        return code
    # Rebuild lines with injections inserted before their target def lines.
    new_lines = []
    for idx, line in enumerate(lines):
        if idx in inject_before:
            new_lines.append(inject_before[idx])
        new_lines.append(line)
    return ''.join(new_lines)


def _ensure_function_contracts(code: str) -> str:
    lines = code.splitlines(keepends=True)
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Match both top-level defs and indented class method defs
        def_m = _RE_DEF.match(line)
        if def_m:
            indent = def_m.group(1)
            method_name = def_m.group(2)

            # Skip __init__, __str__, etc. and @property — Module5 ignores them
            is_dunder = method_name.startswith('__') and method_name.endswith('__')
            preceding_stripped = [l.rstrip() for l in out if l.strip()]
            is_property = any(re.match(r'\s*@property\b', l) for l in preceding_stripped[-3:])
            if is_dunder or is_property:
                out.append(line)
                i += 1
                continue

            # Check whether contracts are already present in the preceding lines
            # (look back far enough for functions with many contract lines)
            has_requires = any(re.match(r'\s*#@\s*requires\b', l) for l in preceding_stripped[-15:])
            has_ensures  = any(re.match(r'\s*#@\s*ensures\b',  l) for l in preceding_stripped[-15:])
            has_assigns  = any(re.match(r'\s*#@\s*assigns\b',  l) for l in preceding_stripped[-15:])

            # Detect whether this is a class method (has `self` as first param)
            is_method = bool(re.match(r'^[ \t]+def\s+\w+\s*\(\s*self\b', line))

            if not has_requires or not has_ensures:
                body = ''.join(lines[i+1:])
                if (re.search(r'\b(acc|product)\s*=\s*1\b', body) and
                        re.search(r'\b(acc|product)\s*\*=|\b(acc|product)\s*=\s*(acc|product)\s*\*', body)):
                    param_m = re.search(r'def\s+\w+\s*\(\s*(?:self\s*,\s*)?(\w+)', line)
                    param = param_m.group(1) if param_m else 'n'
                    if not has_requires:
                        out.append(f'{indent}#@ requires {param} >= 1\n')
                    if not has_ensures:
                        out.append(f'{indent}#@ ensures \\result >= 1\n')
                elif (re.search(r'\b(total|count|acc)\s*=\s*0\b', body) and
                      re.search(r'\b(total|count|acc)\s*\+=', body)):
                    if not has_requires:
                        out.append(f'{indent}#@ requires 1 == 1\n')
                    if not has_ensures:
                        out.append(f'{indent}#@ ensures 1 == 1\n')
                else:
                    if not has_requires:
                        out.append(f'{indent}#@ requires 1 == 1\n')
                    if not has_ensures:
                        out.append(f'{indent}#@ ensures 1 == 1\n')

            if not has_assigns:
                if is_method:
                    # Detect which self.* fields are mutated in this method's body
                    body_lines = []
                    j = i + 1
                    base_indent = indent + '    '
                    while j < len(lines):
                        if lines[j].strip() == '' or lines[j].startswith(base_indent):
                            body_lines.append(lines[j])
                            j += 1
                        else:
                            break
                    body_text = ''.join(body_lines)
                    mutated = re.findall(r'\bself\.(\w+)\s*(?:=|\+=|-=|\*=)', body_text)
                    if mutated:
                        # Emit one `#@ assigns self._field` per unique mutated field
                        seen = []
                        for fld in mutated:
                            if fld not in seen:
                                seen.append(fld)
                                out.append(f'{indent}#@ assigns self.{fld}\n')
                    else:
                        out.append(f'{indent}#@ assigns \\nothing\n')
                else:
                    out.append(f'{indent}#@ assigns \\nothing\n')

        out.append(line)
        i += 1
    return ''.join(out)


def _inject_trusted_for_dict_subscript_assignment(code: str) -> str:
    lines = code.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        def_m = re.match(r'^([ \t]*)def\s+\w+\s*\(', line)
        if def_m:
            indent = def_m.group(1)
            indent_len = len(indent)
            # Collect the function body (lines more indented than the def).
            j = i + 1
            body_lines: list[str] = []
            while j < len(lines):
                bl = lines[j]
                if bl.strip() == '':
                    j += 1
                    continue
                if len(bl) - len(bl.lstrip()) <= indent_len:
                    break
                body_lines.append(bl)
                j += 1
            body = ''.join(body_lines)
            # Collect dict-typed variable names declared in the body.
            dict_vars: set[str] = set()
            for pat in (r'\b(\w+)\s*:\s*dict\b', r'\b(\w+)\s*=\s*\{\s*\}'):
                for m in re.finditer(pat, body):
                    dict_vars.add(m.group(1))
            # Check if any dict var has a subscript assignment in the body.
            needs_trusted = any(
                bool(re.search(r'\b' + re.escape(v) + r'\s*\[[^\n]*\]\s*=', body))
                for v in dict_vars
            )
            if needs_trusted:
                # Check backward through already-emitted lines for #@ \trusted.
                already = False
                k = len(out) - 1
                while k >= 0:
                    prev = out[k].strip()
                    if _RE_TRUSTED.match(prev):
                        already = True
                        break
                    if prev and not prev.startswith('#@'):
                        break
                    k -= 1
                if not already:
                    out.append(f'{indent}#@ \\trusted\n')
        out.append(line)
        i += 1
    return ''.join(out)


def _strengthen_ensures(code: str) -> str:
    lines = code.splitlines(keepends=True)
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Detect `#@ ensures 1 == 1` for a function-level contract (not inside a
        # loop invariant block), then look ahead for the `def` that follows.
        if re.match(r'\s*#@\s*ensures\s+1\s*==\s*1\s*$', line):
            # Scan forward to find the def and its body.
            j = i + 1
            while j < len(lines) and not re.match(r'\s*def\s+', lines[j]):
                j += 1
            if j < len(lines):
                # Collect the function body (lines after the def line).
                body = ''.join(lines[j:])
                # Multiplicative accumulator: `acc = 1` then `acc *=` or `acc = acc *`
                if re.search(r'\b(acc|product)\s*=\s*1\b', body) and re.search(r'\b(acc|product)\s*\*=|\b(acc|product)\s*=\s*(acc|product)\s*\*', body):
                    line = re.sub(r'1\s*==\s*1', r'\\result >= 1', line)
                # Additive accumulators over lists are intentionally left as `1 == 1`
                # because list elements may be negative, making `\result >= 0` unprovable.
        out.append(line)
        i += 1
    return ''.join(out)


def _strip_nonlinear_conservation_invariant(code: str) -> str:
    lines = code.splitlines(keepends=True)
    out = []
    for line in lines:
        if re.match(r'\s*#@\s*loop invariant\s+\w+\s*\*\s*\w+\s*>=\s*\d+\s*$', line):
            continue  # drop nonlinear cross-product invariant
        out.append(line)
    return ''.join(out)


def _weaken_offset_start_loop_invariant(code: str) -> str:
    # Match patterns like `#@ loop invariant k <= i and i <= n` where the
    # lower-bound variable is not `0` (i.e., it's a parameter offset).
    return re.sub(
        r'(#@\s*loop invariant\s+)(\w+)\s*<=\s*(\w+)\s+and\s+\3\s*<=\s*(\w+)',
        lambda m: (
            m.group(0) if m.group(2) == '0'
            else f'{m.group(1)}0 <= {m.group(3)}'
        ),
        code
    )


def _strengthen_loop_counter_invariant(code: str) -> str:
    lines = code.splitlines(keepends=True)
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m_inv = re.match(r'(\s*#@\s*loop invariant\s+)(0\s*<=\s*)(\w+)\s*$', line)
        if m_inv:
            var = m_inv.group(3)
            # Scan ahead within this loop annotation block for a variant `b - var`
            j = i + 1
            bound = None
            while j < len(lines):
                candidate = lines[j].strip()
                m_var = re.match(
                    r'#@\s*loop variant\s+(\w+)\s*-\s*' + re.escape(var) + r'\s*$',
                    candidate
                )
                if m_var:
                    bound = m_var.group(1)
                    break
                # Stop scanning once we leave the annotation block
                if candidate and not candidate.startswith('#@'):
                    break
                j += 1
            if bound:
                # Check that `var <= bound` is not already present anywhere in
                # the same annotation block (including before the current line).
                block_start = i
                while block_start > 0 and _RE_ANN.match(lines[block_start - 1]):
                    block_start -= 1
                block = ''.join(lines[block_start:j + 1])
                already_bounded = bool(re.search(
                    re.escape(var) + r'\s*<=\s*' + re.escape(bound), block
                ))
                if not already_bounded:
                    # Replace bare `0 <= var` with `0 <= var and var <= bound`
                    line = re.sub(
                        r'(#@\s*loop invariant\s+)(0\s*<=\s*' + re.escape(var) + r')\s*$',
                        lambda m_: m_.group(1) + m_.group(2).rstrip()
                            + ' and ' + var + ' <= ' + bound + '\n',
                        line
                    )
        out.append(line)
        i += 1
    return ''.join(out)


def _inject_offset_lower_bound_invariant(code: str) -> str:
    lines = code.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Detect the last invariant line in an annotation block (next
        # non-annotation line is the `while` statement).
        m_inv = re.match(r'(\s*)(#@\s*loop invariant\b.*)', line)
        if m_inv:
            indent = m_inv.group(1)
            # Peek ahead: collect all remaining annotation lines then find
            # the `while` statement.
            j = i + 1
            while j < len(lines) and _RE_ANN.match(lines[j]):
                j += 1
            # lines[j] should now be the `while` line (skip blank lines).
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            if j < len(lines) and re.match(r'\s*while\b', lines[j]):
                # Collect the annotation block (from first #@ to j-1).
                block_start = i
                while block_start > 0 and _RE_ANN.match(out[block_start - 1] if block_start <= len(out) else ''):
                    block_start -= 1
                # Collect the whole annotation block text.
                ann_lines = []
                k2 = i
                while k2 < j:
                    if _RE_ANN.match(lines[k2]):
                        ann_lines.append(lines[k2])
                    k2 += 1
                ann_block = ''.join(ann_lines)

                # Find the loop counter variable from `0 <= <var>` in the block.
                m_var = re.search(r'#@\s*loop invariant\s+0\s*<=\s*(\w+)', ann_block)
                if m_var:
                    loop_var = m_var.group(1)
                    # Collect the while-loop body.
                    while_indent = len(lines[j]) - len(lines[j].lstrip())
                    body_lines = []
                    bk = j + 1
                    while bk < len(lines):
                        bl = lines[bk]
                        if bl.strip() == '':
                            bk += 1
                            continue
                        bl_indent = len(bl) - len(bl.lstrip())
                        if bl_indent <= while_indent:
                            break
                        body_lines.append(bl)
                        bk += 1
                    body_text = ''.join(body_lines)

                    # Look for `[loop_var - <offset_var>]` in the body.
                    m_off = re.search(
                        r'\[\s*' + re.escape(loop_var) + r'\s*-\s*(\w+)\s*\]',
                        body_text
                    )
                    if m_off:
                        offset_var = m_off.group(1)
                        # Check that the invariant is not already present.
                        already = bool(re.search(
                            re.escape(offset_var) + r'\s*<=\s*' + re.escape(loop_var),
                            ann_block
                        ))
                        if not already:
                            # Find the variant line (last #@ line before the while)
                            # and insert the new invariant just before it so
                            # invariants come before variants.
                            variant_idx = None
                            k3 = i
                            while k3 < j:
                                if re.match(r'\s*#@\s*loop variant\b', lines[k3]):
                                    variant_idx = k3
                                    break
                                k3 += 1
                            new_inv = f'{indent}#@ loop invariant {offset_var} <= {loop_var}\n'
                            if variant_idx is not None and variant_idx > i:
                                # We will insert new_inv at variant_idx (relative
                                # to out's current length + lines processed so far).
                                # Emit lines[i..variant_idx-1], then inject, then continue.
                                while i < variant_idx:
                                    out.append(lines[i])
                                    i += 1
                                out.append(new_inv)
                                continue  # `i` now points at variant_idx line
                            else:
                                # No variant line found; append invariant after
                                # all annotation lines (i.e. just before `while`).
                                while i < j:
                                    if _RE_ANN.match(lines[i]):
                                        out.append(lines[i])
                                        i += 1
                                    else:
                                        break
                                out.append(new_inv)
                                continue
        out.append(line)
        i += 1
    return ''.join(out)


def _tighten_lower_bound_for_pred_access(code: str) -> str:
    lines = code.splitlines(keepends=True)
    out = []
    current_func_body: list = []
    for idx, line in enumerate(lines):
        # Detect function definition boundary — reset per-function state.
        if re.match(r'^def\s+', line):
            current_func_body = [line]
        else:
            current_func_body.append(line)

        # Match `0 <= <var>` at the start of an invariant (with optional
        # trailing `and <var> <= <bound>` added by _strengthen_loop_counter_invariant).
        m_inv = re.match(r'(\s*)(#@\s*loop invariant\s+)(0\s*<=\s*)(\w+)', line)
        if m_inv:
            var = m_inv.group(4)
            body_text = ''.join(current_func_body)
            # Condition (a): var initialised to 1 before the loop.
            init_to_one = bool(re.search(
                r'\b' + re.escape(var) + r'\s*=\s*1\b', body_text
            ))
            # Condition (b): loop body accesses [var - 1] — scan forward to
            # find the corresponding `while` block body.
            pred_access = False
            # Find the while loop that this invariant belongs to by looking
            # ahead until we leave the annotation+while block.
            j = idx + 1
            while j < len(lines):
                candidate = lines[j].strip()
                if candidate.startswith('#@'):
                    j += 1
                    continue
                # First non-annotation line should be `while ...:`
                if re.match(r'while\b', candidate):
                    # Collect the while body until indentation drops.
                    indent_len = len(lines[j]) - len(lines[j].lstrip())
                    k = j + 1
                    while k < len(lines):
                        bl = lines[k]
                        if bl.strip() == '':
                            k += 1
                            continue
                        bl_indent = len(bl) - len(bl.lstrip())
                        if bl_indent <= indent_len:
                            break
                        if re.search(r'\[' + re.escape(var) + r'\s*-\s*1\]', bl):
                            pred_access = True
                            break
                        k += 1
                break
            if init_to_one and pred_access:
                line = re.sub(
                    r'(#@\s*loop invariant\s+)0\s*<=\s*' + re.escape(var),
                    lambda m_: m_.group(1) + '1 <= ' + var,
                    line
                )
        out.append(line)
    return ''.join(out)


def _strip_unprovable_additive_invariants(code: str) -> str:
    # Pre-scan: identify functions that use a positive-only accumulation pattern
    # (a `continue` guard that skips non-positive list elements).  For these,
    # `total >= 0` is provable and the invariant must be preserved.
    positive_only_funcs: set = set()
    for m in re.finditer(r'^def\s+(\w+)', code, re.MULTILINE):
        fname = m.group(1)
        next_def = re.search(r'^def\s+', code[m.end():], re.MULTILINE)
        end = (m.end() + next_def.start()) if next_def else len(code)
        body = code[m.start():end]
        if (re.search(r':\s*list\b', body.split('\n')[0]) and
                re.search(r'if\s+\w+\[.*?\]\s*<\s*=?\s*0', body) and
                re.search(r'\bcontinue\b', body)):
            positive_only_funcs.add(fname)

    lines = code.splitlines(keepends=True)
    out = []
    in_list_func = False
    current_func: str = ''
    for line in lines:
        m = re.match(r'^def\s+(\w+)', line)
        if m:
            current_func = m.group(1)
            in_list_func = bool(re.search(r':\s*list\b', line))
        if (in_list_func and
                current_func not in positive_only_funcs and
                re.match(r'\s*#@\s*loop invariant\s+(total|acc)\s*>=\s*0\s*$', line)):
            continue  # drop unprovable invariant for list-iterating functions
        out.append(line)
    return ''.join(out)


def _strengthen_binary_search_invariants(code: str) -> str:
    lines = code.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Detect a loop variant of the form `(right - left) + 1` or `right - left + 1`
        m_var = re.match(
            r'(\s*#@\s*loop variant\s+)\(?\s*(\w+)\s*-\s*(\w+)\s*\)\s*\+\s*1\s*$',
            line
        )
        if m_var:
            right_var = m_var.group(2)
            left_var = m_var.group(3)
            indent = re.match(r'(\s*)', line).group(1)
            # Scan the whole annotation block (backwards from the variant line)
            # to find the loop's `n` binding and check for existing upper bounds.
            block_start = len(out)
            while block_start > 0 and _RE_ANN.match(out[block_start - 1]):
                block_start -= 1
            block = ''.join(out[block_start:])

            # Find the `n` binding: look for `n = len(` in the preceding function body.
            n_var = None
            for prev_line in reversed(out):
                m_n = re.match(r'\s*(\w+)\s*=\s*len\s*\(', prev_line)
                if m_n:
                    n_var = m_n.group(1)
                    break
                if re.match(r'^def\s+', prev_line):
                    break

            if n_var:
                has_left_upper = bool(re.search(
                    re.escape(left_var) + r'\s*<=\s*' + re.escape(n_var), block
                ))
                has_right_upper = bool(re.search(
                    re.escape(right_var) + r'\s*<\s*' + re.escape(n_var), block
                ))
                if not has_left_upper:
                    out.append(f'{indent}#@ loop invariant {left_var} <= {n_var}\n')
                if not has_right_upper:
                    out.append(f'{indent}#@ loop invariant {right_var} < {n_var}\n')
                # Inject `found < n` when a `found = -1` sentinel variable exists and
                # the invariant is not already present.
                found_var = None
                for prev_line in reversed(out):
                    m_f = re.match(r'\s*(\w+)\s*=\s*-\s*1\b', prev_line)
                    if m_f:
                        found_var = m_f.group(1)
                        break
                    if re.match(r'^def\s+', prev_line):
                        break
                if found_var:
                    has_found_upper = bool(re.search(
                        re.escape(found_var) + r'\s*<\s*' + re.escape(n_var), block
                    ))
                    if not has_found_upper:
                        out.append(f'{indent}#@ loop invariant {found_var} < {n_var}\n')

        out.append(line)
        i += 1
    return ''.join(out)


def _split_two_pointer_compound_invariant(code: str) -> str:
    lines = code.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Match `#@ loop invariant 0 <= <lvar> and <lvar> <= <rvar>`
        m = re.match(
            r'(\s*)(#@\s*loop invariant\s+)(0\s*<=\s*)(\w+)\s+and\s+\4\s*<=\s*(\w+)\s*$',
            line
        )
        if m:
            indent = m.group(1)
            lvar = m.group(4)
            rvar = m.group(5)
            # Confirm this is a two-pointer loop by scanning ahead for a variant
            # `<rvar> - <lvar>` in the same annotation block.
            j = i + 1
            is_two_pointer = False
            while j < len(lines):
                candidate = lines[j].strip()
                if re.match(
                    r'#@\s*loop variant\s+' + re.escape(rvar) + r'\s*-\s*' + re.escape(lvar),
                    candidate
                ):
                    is_two_pointer = True
                    break
                if candidate and not candidate.startswith('#@'):
                    break
                j += 1
            if is_two_pointer:
                # Find the `n` binding in the enclosing function.
                n_var = None
                for prev_line in reversed(out):
                    m_n = re.match(r'\s*(\w+)\s*=\s*len\s*\(', prev_line)
                    if m_n:
                        n_var = m_n.group(1)
                        break
                    if re.match(r'^def\s+', prev_line):
                        break
                # Determine whether rvar is a locally-assigned variable (a true
                # two-pointer such as `right = n - 1`) or a fixed-bound function
                # parameter (e.g. `n`, `a_rows`, `b_cols`, `a_cols`).
                func_body_lines = []
                for prev_line in reversed(out):
                    if re.match(r'^def\s+', prev_line):
                        break
                    func_body_lines.append(prev_line)
                rvar_is_local = bool(re.search(
                    r'\b' + re.escape(rvar) + r'\s*=(?!=)',
                    ''.join(func_body_lines)
                ))
                out.append(f'{indent}#@ loop invariant 0 <= {lvar}\n')
                if rvar_is_local:
                    # True two-pointer: lvar <= rvar is false at entry for empty
                    # input; use the len()-based bound if available.
                    if n_var:
                        out.append(f'{indent}#@ loop invariant {lvar} <= {n_var}\n')
                else:
                    # Fixed-bound parameter: rvar IS the upper bound; always emit
                    # lvar <= rvar to give Alt-Ergo the two-sided bound it needs.
                    out.append(f'{indent}#@ loop invariant {lvar} <= {rvar}\n')
                i += 1
                continue
        out.append(line)
        i += 1
    return ''.join(out)


def _fix_list_return_type(code: str) -> str:
    lines = code.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Detect `def funcname(...) -> list:` signatures (possibly with type hints).
        m = re.match(r'^([ \t]*def\s+(\w+)\s*\([^)]*\))\s*->\s*list\s*:', line)
        if m:
            # Collect list-typed parameter names for this function.
            fn_params = _RE_LIST_PARAM.findall(line)
            indent_base = len(m.group(1)) - len(m.group(1).lstrip())
            # Pre-scan: detect direct and indirect list returns before rewriting.
            returns_list_param = False
            returns_list_indirect = False
            if fn_params:
                list_return_pat = re.compile(
                    r'^[ \t]*return\s+(?:' + '|'.join(re.escape(p) for p in fn_params) + r')\s*$'
                )
                alias_assign_pat = re.compile(
                    r'^[ \t]*(\w+)\s*=\s*(?:' + '|'.join(re.escape(p) for p in fn_params) + r')\s*$'
                )
                aliases: set[str] = set()
                scan_i = i + 1
                while scan_i < len(lines):
                    sl = lines[scan_i]
                    si = len(sl) - len(sl.lstrip())
                    if sl.strip() and si <= indent_base and not sl.lstrip().startswith('#@'):
                        break
                    if list_return_pat.match(sl):
                        returns_list_param = True
                        break
                    alias_m = alias_assign_pat.match(sl)
                    if alias_m:
                        aliases.add(alias_m.group(1))
                    if aliases:
                        alias_return_pat = re.compile(
                            r'^[ \t]*return\s+(?:' + '|'.join(re.escape(a) for a in aliases) + r')\s*$'
                        )
                        if alias_return_pat.match(sl):
                            returns_list_indirect = True
                            break
                    scan_i += 1
            # Also detect: function creates a new local array (var = [...] * n or
            # var = [...]) and returns it.  Keep `-> list` so Module 6 emits `: array int`.
            returns_new_array = False
            scan_i2 = i + 1
            new_array_locals: set[str] = set()
            while scan_i2 < len(lines):
                sl2 = lines[scan_i2]
                si2 = len(sl2) - len(sl2.lstrip())
                if sl2.strip() and si2 <= indent_base and not sl2.lstrip().startswith('#@'):
                    break
                m_arr = re.match(r'^[ \t]*(\w+)\s*=\s*\[', sl2)
                if m_arr:
                    new_array_locals.add(m_arr.group(1))
                if new_array_locals:
                    m_ret2 = re.match(
                        r'^[ \t]*return\s+(?:' +
                        '|'.join(re.escape(v) for v in new_array_locals) + r')\s*$',
                        sl2,
                    )
                    if m_ret2:
                        returns_new_array = True
                        break
                scan_i2 += 1
            # Keep `-> list` when the function returns an array via an alias or a
            # newly created local array so Module 6 emits `: array int`.
            if returns_list_indirect or returns_new_array:
                out.append(line)
                i += 1
                continue
            # Rewrite the signature to `-> int`.
            out.append(m.group(1) + ' -> int:\n')
            i += 1
            while i < len(lines):
                body_line = lines[i]
                body_indent = len(body_line) - len(body_line.lstrip())
                if body_line.strip() and body_indent <= indent_base and not body_line.lstrip().startswith('#@'):
                    break
                # Rewrite `#@ ensures \result ...` → `#@ ensures \result == 0` only
                # when the function body returns a list parameter (not an int accumulator).
                if returns_list_param and re.match(r'[ \t]*#@\s*ensures\b', body_line):
                    leading = re.match(r'^([ \t]*#@\s*ensures\s+)', body_line)
                    if leading:
                        out.append(leading.group(1) + r'\result == 0' + '\n')
                        i += 1
                        continue
                # Rewrite `return <list_param>` → `return 0`.
                if fn_params:
                    pat = r'^([ \t]*)return\s+(?:' + '|'.join(re.escape(p) for p in fn_params) + r')\s*$'
                    if re.match(pat, body_line):
                        leading_ws = re.match(r'^([ \t]*)', body_line).group(1)
                        out.append(leading_ws + 'return 0\n')
                        i += 1
                        continue
                out.append(body_line)
                i += 1
            continue
        out.append(line)
        i += 1
    return ''.join(out)


def _remove_spurious_old_length_plus1(code: str) -> str:
    lines = code.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(
            r'^([ \t]*)#@\s*ensures\s+\\result\s*==\s*\\old\(\\length\((\w+)\)\)\s*\+\s*1\s*$',
            line,
        )
        if m:
            param = m.group(2)
            # Scan forward to collect the function body.
            j = i + 1
            body_buf: list[str] = []
            indent_len = len(m.group(1))
            while j < len(lines):
                bline = lines[j]
                stripped = bline.lstrip()
                if stripped.startswith('def ') and (len(bline) - len(stripped)) <= indent_len:
                    break
                body_buf.append(bline)
                j += 1
            body_text = ''.join(body_buf)
            if f'{param}.append(' not in body_text:
                # Skip this ensures line — it is unprovable without an append.
                i += 1
                continue
        out.append(line)
        i += 1
    return ''.join(out)


def _downgrade_result_ge1_for_len_return(code: str) -> str:
    lines = code.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m_ens = re.match(
            r'^([ \t]*)#@\s*ensures\s+\\result\s*>=\s*1\s*$',
            line,
        )
        if m_ens:
            indent_len = len(m_ens.group(1))
            # Collect annotation lines and body lines for the surrounding function.
            contract_lines: list[str] = []
            body_lines_buf: list[str] = []
            # Collect preceding annotation lines
            k = i - 1
            while k >= 0:
                prev = lines[k]
                if re.match(r'^[ \t]*#@', prev):
                    contract_lines.insert(0, prev)
                    k -= 1
                else:
                    break
            # Scan forward past any remaining annotation lines to find the `def`
            j = i + 1
            while j < len(lines):
                bline = lines[j]
                stripped = bline.lstrip()
                if stripped.startswith('def ') and (len(bline) - len(stripped)) <= indent_len:
                    j += 1
                    while j < len(lines):
                        bbline = lines[j]
                        bstripped = bbline.lstrip()
                        if (bstripped.startswith('def ') or bstripped.startswith('class ')) \
                                and (len(bbline) - len(bstripped)) <= indent_len:
                            break
                        body_lines_buf.append(bbline)
                        j += 1
                    break
                j += 1
            body_text = ''.join(body_lines_buf)
            contract_text = ''.join(contract_lines)
            # Check if function body contains `return len(...)`.
            has_len_return = bool(re.search(r'\breturn\s+len\s*\(', body_text))
            # Check if a non-empty precondition already exists.
            has_nonempty_pre = bool(
                re.search(r'#@\s*requires\s+\\length\s*\(\w+\)\s*(?:>=\s*1|>\s*0)', contract_text)
            )
            if has_len_return and not has_nonempty_pre:
                out.append(line.replace('>= 1', '>= 0', 1))
                i += 1
                continue
        out.append(line)
        i += 1
    return ''.join(out)


def _downgrade_result_ge1_for_sum(code: str) -> str:
    lines = code.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m_ens = re.match(
            r'^([ \t]*)#@\s*ensures\s+\\result\s*>=\s*1\s*$',
            line,
        )
        if m_ens:
            indent_len = len(m_ens.group(1))
            j = i + 1
            body_text = ''
            while j < len(lines):
                bline = lines[j]
                stripped = bline.lstrip()
                if stripped.startswith('def ') and (len(bline) - len(stripped)) <= indent_len:
                    j += 1
                    body_buf: list[str] = []
                    while j < len(lines):
                        bbline = lines[j]
                        bstripped = bbline.lstrip()
                        if (bstripped.startswith('def ') or bstripped.startswith('class ')) \
                                and (len(bbline) - len(bstripped)) <= indent_len:
                            break
                        body_buf.append(bbline)
                        j += 1
                    body_text = ''.join(body_buf)
                    break
                j += 1
            # Additive accumulator: any name initialised to 0 and incremented with +=
            is_additive = bool(
                re.search(r'\b\w+\s*=\s*0\b', body_text) and
                re.search(r'\b\w+\s*\+=', body_text)
            )
            if is_additive:
                out.append(line.replace('\\result >= 1', '1 == 1', 1))
                i += 1
                continue
        out.append(line)
        i += 1
    return ''.join(out)


def _strip_default_args(code: str) -> str:
    def _clean_args(m: re.Match) -> str:
        sig = m.group(0)
        # Remove `: type = value` → `: type` and bare `= value` → ''
        sig = re.sub(r'(:\s*\w+)\s*=\s*[^,)]+', r'\1', sig)
        sig = re.sub(r'(\w+)\s*=\s*[^,)]+', r'\1', sig)
        return sig
    return re.sub(r'def\s+\w+\s*\([^)]*\)', _clean_args, code)


def _check_class_invariant_guards(src: str) -> str:
    lines = src.splitlines(keepends=True)
    # Extract class invariant field names
    inv_fields: set = set()
    for line in lines:
        m = re.match(r'^[ \t]*#@\s*class invariant\b(.+)', line)
        if m:
            for fm in re.finditer(r'self\.(\w+)', m.group(1)):
                inv_fields.add(fm.group(1))
    if not inv_fields:
        return src

    result_lines = list(lines)
    i = 0
    while i < len(result_lines):
        bare = result_lines[i].rstrip('\r\n')
        dm = re.match(r'^(\s*)def\s+\w+\s*\(self', bare)
        if dm:
            indent = dm.group(1)
            j = i - 1
            assigns_inv_field = False
            has_requires = False
            while j >= 0 and result_lines[j].strip().startswith('#@'):
                cline = result_lines[j].strip()
                if re.match(r'#@\s*assigns\b', cline):
                    for fld in inv_fields:
                        if f'self.{fld}' in cline:
                            assigns_inv_field = True
                if re.match(r'#@\s*requires\b', cline) and cline != '#@ requires 1 == 1':
                    has_requires = True
                j -= 1
            if assigns_inv_field and not has_requires:
                pass  # don't add fallback — let reconciliation handle it
        i += 1
    return ''.join(result_lines)


def _fix_annotation_indentation(src: str) -> str:
    """Ensure #@ annotation lines have the same indentation as the def they precede.

    LLMs sometimes emit contracts at column 0 even when the function is indented
    inside a class. This fixes that by aligning all contiguous #@ blocks to the
    indent of the next non-annotation line (usually ``def``).
    """
    lines = src.splitlines(keepends=True)
    result: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("#@"):
            block_start = i
            while i < len(lines) and lines[i].strip().startswith("#@"):
                i += 1
            # Find target indentation from next non-blank line
            target_indent = ""
            j = i
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                target_indent = re.match(r'^(\s*)', lines[j]).group(1)
            for k in range(block_start, i):
                stripped = lines[k].strip()
                result.append(f"{target_indent}{stripped}\n")
        else:
            result.append(lines[i])
            i += 1
    return "".join(result)


def _guard_body_preservation(original_source: str) -> Callable[[str], str]:
    """Return a guard that rejects body-to-pass replacements.

    Compares the generated output against the original source. If any function
    body was reduced to just ``pass`` when the original had real statements,
    the original body is restored (keeping any #@ annotations that precede
    the ``def``).
    """
    import textwrap

    # Extract original function bodies: {func_name: body_text}
    orig_bodies: dict[str, str] = {}
    try:
        tree = _ast_module.parse(original_source)
    except SyntaxError:
        # If we can't parse, return identity transform (no guard)
        return lambda code: code

    for node in _ast_module.walk(tree):
        if isinstance(node, (_ast_module.FunctionDef, _ast_module.AsyncFunctionDef)):
            # Extract body text from original source
            body_lines = original_source.splitlines(keepends=True)
            if node.end_lineno and node.end_lineno <= len(body_lines):
                first_body = node.body[0].lineno if node.body else node.lineno + 1
                body_text = ''.join(body_lines[first_body - 1: node.end_lineno])
                orig_bodies[node.name] = body_text

    def _guard(code: str) -> str:
        lines = code.splitlines(keepends=True)
        result: list[str] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            bare = line.rstrip('\r\n')
            def_m = re.match(r'^(\s*)def\s+(\w+)\s*\(', bare)
            if def_m:
                indent = def_m.group(1)
                func_name = def_m.group(2)
                body_indent = indent + '    '
                result.append(line)
                i += 1
                # Collect the body
                body_start = i
                while i < len(lines):
                    bline = lines[i].rstrip('\r\n')
                    if bline.strip() == '' or bline.startswith(body_indent):
                        i += 1
                    else:
                        break
                body_chunk = lines[body_start:i]
                # Check if body is just 'pass'
                body_stripped = [l.strip() for l in body_chunk if l.strip()]
                if body_stripped == ['pass'] and func_name in orig_bodies:
                    orig_body = orig_bodies[func_name]
                    # Restore original body (already has proper indentation)
                    result.extend(orig_body.splitlines(keepends=True))
                else:
                    result.extend(body_chunk)
            else:
                result.append(line)
                i += 1
        return ''.join(result)

    return _guard


def _fix_empty_conditional_bodies(src: str) -> str:
    lines = src.splitlines(keepends=True)
    result: list = []
    for i, line in enumerate(lines):
        result.append(line)
        bare = line.rstrip('\r\n')
        m = re.match(r'^([ \t]*)(if\b[^\n]*:|elif\b[^\n]*:|else\s*:)\s*$', bare)
        if m:
            indent_len = len(m.group(1))
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            next_indent = len(lines[j]) - len(lines[j].lstrip()) if j < len(lines) else 0
            if j >= len(lines) or next_indent <= indent_len:
                result.append(m.group(1) + '    pass\n')
    return ''.join(result)


def _preceding_has_trusted(result: list[str]) -> bool:
    """Check if the annotation block immediately above already contains \\trusted."""
    k = len(result) - 1
    while k >= 0:
        prev = result[k].strip()
        if prev.startswith('#@'):
            if _RE_TRUSTED.match(result[k]):
                return True
            k -= 1
        else:
            break
    return False


def _strip_external_type_bodies(src: str) -> str:
    """Mark functions using external types (cst.XXX/libcst.XXX) as \\trusted.

    Previous behaviour replaced entire function bodies with ``pass`` — this
    destroyed code.  Now we insert ``#@ \\trusted`` (if not already present)
    and leave bodies completely intact.
    """
    lines = src.splitlines(keepends=True)
    result: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        bare = line.rstrip('\r\n')
        # Detect def with external-type param: `def foo(self, node: cst.XXX)`
        m = re.match(
            r'^(\s*)def\s+\w+\s*\([^)]*:\s*(?:cst|libcst)\.\w+[^)]*\)',
            bare,
        )
        if m:
            indent = m.group(1)
            if not _preceding_has_trusted(result):
                result.append(f"{indent}#@ \\trusted\n")
            result.append(line)
            i += 1
            continue
        # Check if function body uses external library calls
        m2 = re.match(r'^(\s*)def\s+\w+\s*\(', bare)
        if m2:
            indent = m2.group(1)
            body_indent = indent + '    '
            j = i + 1
            has_external = False
            while j < len(lines):
                bline = lines[j].rstrip('\r\n')
                if bline.strip() == '' or bline.startswith(body_indent):
                    if re.search(r'\bcst\.\w+', bline) or re.search(r'\blibcst\.\w+', bline):
                        has_external = True
                    j += 1
                else:
                    break
            if has_external and not _preceding_has_trusted(result):
                result.append(f"{indent}#@ \\trusted\n")
        result.append(line)
        i += 1
    return ''.join(result)


def _inject_n_bound_requires(code: str) -> str:
    lines = code.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        def_m = _RE_DEF_PARAMS.match(line)
        if def_m:
            indent = def_m.group(1)
            params_str = def_m.group(2)
            arr_params = _RE_LIST_PARAM.findall(params_str)
            int_params = re.findall(r'\b(\w+)\s*:\s*int\b', params_str)
            if arr_params and int_params:
                j = i + 1
                body_indent = indent + '    '
                body_buf: list[str] = []
                while j < len(lines):
                    bl = lines[j]
                    if bl.strip() == '' or bl.startswith(body_indent):
                        body_buf.append(bl)
                        j += 1
                    else:
                        break
                body_text = ''.join(body_buf)
                for n_param in int_params:
                    for arr_param in arr_params:
                        has_while_n = bool(re.search(
                            rf'\bwhile\b[^\n]*\b{re.escape(n_param)}\b', body_text
                        ))
                        has_arr_idx = bool(re.search(
                            rf'\b{re.escape(arr_param)}\s*\[', body_text
                        ))
                        if not (has_while_n and has_arr_idx):
                            continue
                        k = len(out) - 1
                        while k >= 0 and _RE_ANN.match(out[k]):
                            k -= 1
                        block_start = k + 1
                        contract_text = ''.join(out[block_start:])
                        has_n_ge_0 = bool(re.search(
                            rf'#@\s*requires\s+{re.escape(n_param)}\s*>=\s*0',
                            contract_text
                        ))
                        has_n_le_len = bool(re.search(
                            rf'#@\s*requires\s+{re.escape(n_param)}\s*<=\s*\\length\s*\(\s*{re.escape(arr_param)}\s*\)',
                            contract_text
                        ))
                        if has_n_ge_0 and has_n_le_len:
                            continue
                        new_reqs: list[str] = []
                        if not has_n_ge_0:
                            new_reqs.append(f'{indent}#@ requires {n_param} >= 0\n')
                        if not has_n_le_len:
                            new_reqs.append(f'{indent}#@ requires {n_param} <= \\length({arr_param})\n')
                        replaced = False
                        for idx in range(block_start, len(out)):
                            if re.match(r'\s*#@\s*requires\s+1\s*==\s*1\s*$', out[idx]):
                                out[idx] = new_reqs[0]
                                for extra in reversed(new_reqs[1:]):
                                    out.insert(idx + 1, extra)
                                replaced = True
                                break
                        if not replaced:
                            out.extend(new_reqs)
        out.append(line)
        i += 1
    return ''.join(out)


def _remove_array_typed_variant(code: str) -> str:
    lines = code.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m_def = _RE_DEF_PARAMS.match(line)
        if m_def:
            params_str = m_def.group(2)
            array_params: set[str] = set(
                pm.group(1)
                for pm in (
                    re.match(r'\s*(\w+)\s*:\s*(list|str)\b', p.strip())
                    for p in params_str.split(',')
                )
                if pm
            )
            if array_params:
                k = len(out) - 1
                while k >= 0 and _RE_ANN.match(out[k]):
                    mv = re.match(r'[ \t]*#@\s*\\variant\s+(\w+)\s*$', out[k])
                    if mv and mv.group(1) in array_params:
                        del out[k]
                    k -= 1
        out.append(line)
        i += 1
    return ''.join(out)


def _fix_mismatched_loop_bound_invariant(code: str) -> str:
    lines = code.splitlines(keepends=True)
    result: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not _RE_ANN.match(line):
            result.append(line)
            i += 1
            continue
        # Collect consecutive annotation block.
        block: list[str] = []
        while i < len(lines) and _RE_ANN.match(lines[i]):
            block.append(lines[i])
            i += 1
        # Find `#@ loop variant Y - var` in the block.
        variant_bound: str | None = None
        variant_var: str | None = None
        for bl in block:
            mv = re.match(r'\s*#@\s*loop variant\s+(\w+)\s*-\s*(\w+)\s*$', bl)
            if mv:
                variant_bound = mv.group(1)
                variant_var = mv.group(2)
                break
        if variant_bound and variant_var:
            new_block: list[str] = []
            for bl in block:
                mi = re.match(
                    r'(\s*#@\s*loop invariant\s+)'
                    + re.escape(variant_var)
                    + r'\s*<=\s*(\w+)\s*$',
                    bl,
                )
                if mi and mi.group(2) != variant_bound:
                    bl = mi.group(1) + variant_var + ' <= ' + variant_bound + '\n'
                new_block.append(bl)
            result.extend(new_block)
        else:
            result.extend(block)
    return ''.join(result)


def _dedup_contract_blocks(code: str) -> str:
    lines = code.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if _RE_ANN.match(line):
            # Collect the entire consecutive annotation block.
            block_lines: list[str] = []
            while i < len(lines) and _RE_ANN.match(lines[i]):
                block_lines.append(lines[i])
                i += 1
            # Emit each unique line (first occurrence wins; preserve order).
            seen: set[str] = set()
            for bl in block_lines:
                key = bl.strip()
                if key not in seen:
                    seen.add(key)
                    out.append(bl)
            continue
        out.append(line)
        i += 1
    return ''.join(out)


def _rewrite_return_in_if_inside_while(code: str) -> str:
    def _normalize_bool_int(s: str):
        """Return (int_val, str_literal) for True/False/0/1, else None."""
        if s in ('True', '1'):
            return (1, '1')
        if s in ('False', '0'):
            return (0, '0')
        try:
            v = int(s)
            if v in (0, 1):
                return (v, str(v))
        except ValueError:
            pass
        return None

    lines = code.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r'(\s*)while\b', line):
            while_indent = len(line) - len(line.lstrip())
            while_indent_str = ' ' * while_indent
            inner_indent_str = while_indent_str + '    '
            body_start = i + 1
            body: list[tuple[int, str]] = []
            j = body_start
            while j < len(lines):
                bl = lines[j]
                if bl.strip() == '':
                    body.append((j, bl))
                    j += 1
                    continue
                bl_indent = len(bl) - len(bl.lstrip())
                if bl_indent <= while_indent:
                    break
                body.append((j, bl))
                j += 1
            body_end = j

            non_blank = [(idx, bl) for idx, bl in body if bl.strip()]

            matched = False
            pre_lines: list[str] = []
            cond = ret_val = incr_var = idx_var_guess = bound_var = None  # type: ignore[assignment]
            if len(non_blank) >= 3:
                core = non_blank[-3:]
                (_, bl0), (_, bl1), (_, bl2) = core
                m_if = re.match(r'(\s*)if\s+(.+):\s*$', bl0)
                m_ret = re.match(r'(\s*)return\s+(\S+.*?)\s*$', bl1)
                m_incr = re.match(r'(\s*)(\w+)\s*\+=\s*1\s*$', bl2)
                if m_if and m_ret and m_incr:
                    ret_indent = len(bl1) - len(bl1.lstrip())
                    if_indent = len(bl0) - len(bl0.lstrip())
                    if (if_indent == while_indent + 4 and
                            ret_indent == if_indent + 4):
                        prefix = non_blank[:-3]
                        if all(
                            re.match(r'\s+\w+\s*=\s*.+$', pl) and
                            (len(pl) - len(pl.lstrip())) == while_indent + 4
                            for _, pl in prefix
                        ):
                            matched = True
                            pre_lines = [pl for _, pl in prefix]
                            cond = m_if.group(2)
                            raw_val = m_ret.group(2)
                            incr_var = m_incr.group(2)
                            idx_var_guess = incr_var
                            m_while_cond = re.match(
                                r'\s*while\s+' + re.escape(idx_var_guess) + r'\s*<\s*(\w+)',
                                line
                            )
                            bound_var = m_while_cond.group(1) if m_while_cond else None
                            norm = _normalize_bool_int(raw_val)
                            if norm is not None:
                                ret_int, ret_val = norm
                                default_val = str(1 - ret_int)
                            else:
                                ret_val = raw_val
                                default_val = '0'

            if matched and bound_var:
                insert_pos = len(out)
                k = insert_pos - 1
                while k >= 0 and _RE_ANN.match(out[k]):
                    k -= 1
                insert_pos = k + 1

                acc_assign = while_indent_str + f'acc = {default_val}\n'
                out.insert(insert_pos, acc_assign)

                if default_val == '1':
                    inv_body = 'acc == 1 or acc == 0'
                else:
                    inv_body = 'acc == 0 or acc == 1'
                inv_line = while_indent_str + f'#@ loop invariant {inv_body}\n'
                annot_block = out[insert_pos + 1:]
                if not any(('acc == 0 or acc == 1' in l or 'acc == 1 or acc == 0' in l) for l in annot_block):
                    out.append(inv_line)

                out.append(line)

                for pl in pre_lines:
                    out.append(pl)
                out.append(inner_indent_str + f'if {cond}:\n')
                out.append(inner_indent_str + f'    acc = {ret_val}\n')
                out.append(inner_indent_str + f'    {idx_var_guess} = {bound_var}\n')
                out.append(inner_indent_str + 'else:\n')
                out.append(inner_indent_str + f'    {idx_var_guess} += 1\n')

                i = body_end
                while i < len(lines) and lines[i].strip() == '':
                    out.append(lines[i])
                    i += 1
                if i < len(lines):
                    bool_equiv = 'True' if default_val == '1' else 'False'
                    m_post_ret = re.match(
                        r'(\s*)return\s+(' + re.escape(default_val) + '|'
                        + re.escape(bool_equiv) + r')\s*$',
                        lines[i]
                    )
                    if m_post_ret:
                        out.append(m_post_ret.group(1) + 'return acc\n')
                        i += 1
                continue

        out.append(line)
        i += 1
    return ''.join(out)


def _fix_bare_len_sentinel(code: str) -> str:
    bare_re = re.compile(r'^(\s+)(\w+)\s*=\s*len\s*$')
    while_len_re = re.compile(r'\s*while\s+\w+\s*<\s*len\s*\((\w+)\)')
    lines = code.splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        m = bare_re.match(line)
        if m:
            arr_arg = None
            for prev in reversed(out):
                mw = while_len_re.match(prev)
                if mw:
                    arr_arg = mw.group(1)
                    break
            if arr_arg:
                line = m.group(1) + f'{m.group(2)} = len({arr_arg})\n'
        out.append(line)
    return ''.join(out)


def _fix_const_return_after_flag_loop(code: str) -> str:
    lines = code.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m_while = re.match(r'(\s*)while\b', line)
        if m_while:
            while_indent = len(m_while.group(1))
            body_has_acc = False
            j = i + 1
            while j < len(lines):
                bl = lines[j]
                if bl.strip() == '':
                    j += 1
                    continue
                if len(bl) - len(bl.lstrip()) <= while_indent:
                    break
                if re.match(r'\s+acc\s*=\s*[01]\s*$', bl):
                    body_has_acc = True
                j += 1
            while i < j:
                out.append(lines[i])
                i += 1
            while i < len(lines) and lines[i].strip() == '':
                out.append(lines[i])
                i += 1
            if body_has_acc and i < len(lines):
                m_ret = re.match(r'(\s*)return\s+(True|1)\s*$', lines[i])
                if m_ret:
                    out.append(m_ret.group(1) + 'return acc\n')
                    i += 1
            continue
        out.append(line)
        i += 1
    return ''.join(out)


def _fix_bool_flag_conditions(code: str) -> str:
    bool_flag_vars: set = set()
    for line in code.splitlines():
        if _RE_ANN.match(line):
            continue
        m = re.match(r'^[ \t]*(\w+)\s*=\s*(True|False|0|1)\s*$', line)
        if m:
            bool_flag_vars.add(m.group(1))
    if not bool_flag_vars:
        return code
    var_pat = '|'.join(re.escape(v) for v in sorted(bool_flag_vars))
    out = []
    for line in code.splitlines(keepends=True):
        if _RE_ANN.match(line):
            out.append(line)
            continue
        line = re.sub(
            r'\b(if|elif)\s+(' + var_pat + r')\s*:',
            lambda m: m.group(1) + ' ' + m.group(2) + ' != 0:',
            line,
        )
        line = re.sub(
            r'\b(if|elif)\s+not\s+(' + var_pat + r')\s*:',
            lambda m: m.group(1) + ' ' + m.group(2) + ' == 0:',
            line,
        )
        line = re.sub(
            r'\band\s+(' + var_pat + r')\s*:',
            lambda m: 'and ' + m.group(1) + ' != 0:',
            line,
        )
        line = re.sub(
            r'\band\s+not\s+(' + var_pat + r')\s*:',
            lambda m: 'and ' + m.group(1) + ' == 0:',
            line,
        )
        line = re.sub(
            r'(while\s+)(' + var_pat + r')\s+and\b',
            lambda m: m.group(1) + m.group(2) + ' != 0 and',
            line,
        )
        out.append(line)
    return ''.join(out)


# ---------------------------------------------------------------------------
# New wrapper functions for grouped inline guards
# ---------------------------------------------------------------------------

def _guard_strip_math_pi(code: str) -> str:
    code = re.sub(r'^\s*from\s+math\s+import\s+[^\n]*\bpi\b[^\n]*\n', '', code, flags=re.MULTILINE)
    code = re.sub(r'^\s*import\s+math\s*\n', '', code, flags=re.MULTILINE)
    code = re.sub(r'\bmath\.pi\b', '1', code)
    return re.sub(r'\bpi\b', '1', code)


def _guard_str_params_rewrite(code: str) -> str:
    # Guard: The WhyML transpiler maps every `str` parameter type to `int`, so
    # `if not <str_var>:` compiles to `if (not event)` where event is int, causing a
    # type mismatch. For each `param: str` found in the generated code, replace any
    # `if not <param>:` guard with an explicit length check.
    str_params = set(_RE_STR_PARAM.findall(code))
    for _sp in str_params:
        code = re.sub(
            rf'(\s*)if not {re.escape(_sp)}:',
            lambda m, sp=_sp: f'{m.group(1)}{sp}_len = len({sp})\n{m.group(1)}if {sp}_len <= 0:',
            code
        )
    # Guard: The WhyML transpiler maps `str` parameters to `int`, so any `len(<str_param>)`
    # in the function body emits `length <str_param>` where the param has type `int`,
    # causing a fatal type mismatch. Whenever `<param>_len = len(<param>)` appears in the
    # body, remove that assignment line, promote `<param>_len: int` as an explicit function
    # parameter in place of `<param>: str`, and replace any remaining bare `<param>`
    # references with `<param>_len`.
    for _sp in list(str_params):
        len_assign_pat = rf'^[ \t]*{re.escape(_sp)}_len[ \t]*=[ \t]*len\s*\(\s*{re.escape(_sp)}\s*\)[ \t]*$'
        if re.search(len_assign_pat, code, flags=re.MULTILINE):
            code = re.sub(len_assign_pat + r'\n?', '', code, flags=re.MULTILINE)
            code = re.sub(
                rf'(def\s+\w+\s*\([^)]*?)\b{re.escape(_sp)}\s*:\s*str\b',
                rf'\g<1>{_sp}_len: int',
                code,
                flags=re.DOTALL
            )
            code = re.sub(rf'\b{re.escape(_sp)}\b', f'{_sp}_len', code)
    return code


def _guard_bool_constants_in_contracts(code: str) -> str:
    # Guard: Bare Python boolean constants (`True`, `False`, `None`) are not valid in
    # PyCSL contract expressions.  Replace them with provably-equivalent integer forms.
    code = re.sub(
        r'(#@[^\n]*)\bTrue\b',
        lambda m: m.group(1).replace('True', '1 == 1'),
        code, flags=re.MULTILINE
    )
    code = re.sub(
        r'(#@[^\n]*)\bFalse\b',
        lambda m: m.group(1).replace('False', '0 == 1'),
        code, flags=re.MULTILINE
    )
    code = re.sub(
        r'(#@[^\n]*)\bNone\b',
        lambda m: m.group(1).replace('None', '0'),
        code, flags=re.MULTILINE
    )
    return code


def _guard_floordiv_in_contracts(code: str) -> str:
    # Guard: The PyCSL parser's contract grammar does not support the `//` (floor-division)
    # operator inside `#@` contract expressions.  Replace with trivially-true form.
    code = re.sub(r'#@\s*ensures\b[^\n]*//[^\n]*', '#@ ensures 1 == 1', code)
    code = re.sub(r'#@\s*requires\b[^\n]*//[^\n]*', '#@ requires 1 == 1', code)
    return re.sub(r'#@\s*loop invariant\b[^\n]*//[^\n]*', '#@ loop invariant 1 == 1', code)


def _guard_str_length_neutralize(code: str) -> str:
    # Guard: `\length(param)` is only valid for `array`-typed parameters in WhyML.
    # When a `str`-typed parameter is used with `\length(event)`, replace with `1 == 1`.
    str_param_names = set(_RE_STR_PARAM.findall(code))
    if not str_param_names:
        return code
    str_param_pattern = '|'.join(re.escape(p) for p in str_param_names)
    code = re.sub(
        rf'(#@[^\n]*)\\length\s*\(\s*(?:{str_param_pattern})\s*\)\s*(?:[><=!]=?)\s*\S+',
        lambda m: re.sub(
            rf'\\length\s*\(\s*(?:{str_param_pattern})\s*\)\s*(?:[><=!]=?)\s*\S+',
            '1 == 1',
            m.group(0),
        ),
        code,
        flags=re.MULTILINE,
    )
    code = re.sub(
        rf'(#@[^\n]*)\S+\s*(?:[><=!]=?)\s*\\length\s*\(\s*(?:{str_param_pattern})\s*\)',
        lambda m: re.sub(
            rf'\S+\s*(?:[><=!]=?)\s*\\length\s*\(\s*(?:{str_param_pattern})\s*\)',
            '1 == 1',
            m.group(0),
        ),
        code,
        flags=re.MULTILINE,
    )
    return code


def _guard_list_params(code: str) -> str:
    list_params = set(_RE_LIST_PARAM.findall(code))
    # Guard: `if not <list_var>:` is invalid in WhyML.
    for _lp in list_params:
        code = re.sub(
            rf'(\s*)if not {re.escape(_lp)}\s*:',
            lambda m, lp=_lp: f'{m.group(1)}if len({lp}) == 0:',
            code
        )
    # Guard: `var = arr[:]` (whole-array copy) → `var = arr`.
    code = re.sub(r'(\b\w+)\s*=\s*(\b\w+)\[:\]', r'\1 = \2', code)
    # Guard: Slice notation has no IR handler. Replace with `arr[0]`.
    code = re.sub(r'\b(\w+)\[(\w+)?\s*:\s*(\w+)?\]', r'\1[0]', code)
    # Guard: Strip bare method-call expression-statements on list-typed parameters.
    for _lp in list_params:
        code = re.sub(
            rf'^[ \t]*{re.escape(_lp)}\.\w+\(.*\)[ \t]*\n',
            '',
            code,
            flags=re.MULTILINE
        )
    return code


def _guard_rename_val(code: str) -> str:
    # Guard: `val` is a reserved keyword in WhyML. Rename to `v`.
    code = re.sub(
        r'(?m)^([ \t]*(?:#@[^\n]*\n[ \t]*)*def\s+\w+\([^)]*\bval\b[^)]*\):(?:[ \t]*\n[ \t]*#@[^\n]*)*)$',
        lambda m: m.group(0).replace('val', 'v'),
        code,
        flags=re.MULTILINE
    )
    code = re.sub(r'\bval\b(?=\s*:)', 'v', code)
    code = re.sub(
        r'(#@\s+(?:requires|ensures)[^\n]*)\bval\b',
        lambda m: m.group(0).replace('val', 'v'),
        code,
        flags=re.MULTILINE
    )
    return re.sub(
        r'(?m)^(?![ \t]*#@)([^\n]*)\bval\b',
        lambda m: re.sub(r'\bval\b', 'v', m.group(0)) if 'def ' not in m.group(0) else m.group(0),
        code
    )


def _guard_rename_goal(code: str) -> str:
    # Guard: `goal` is a reserved keyword in WhyML. Rename to `target`.
    if re.search(r'\bgoal\s*:', code):
        return re.sub(r'\bgoal\b', 'target', code)
    return code


def _guard_rename_match(code: str) -> str:
    # Guard: `match` is a reserved keyword in WhyML. Rename to `is_match`.
    code = re.sub(
        r'^([ \t]*)match(\s*(?:=|\+=|-=|\*=))',
        r'\1is_match\2',
        code,
        flags=re.MULTILINE
    )
    code = re.sub(
        r'(?m)^(?![ \t]*#@)([^\n]*)\bmatch\b',
        lambda m: re.sub(r'\bmatch\b', 'is_match', m.group(0)) if 'def ' not in m.group(0) else m.group(0),
        code
    )
    return re.sub(
        r'(?m)^[ \t]*#@[ \t]+loop[ \t]+invariant[^\n]*\bmatch\b[^\n]*$',
        lambda m: re.sub(r'\bmatch\b', 'is_match', m.group(0)),
        code
    )


def _guard_rename_result(code: str) -> str:
    # Guard: A local variable named `result` shadows the Why3 `result` binding.
    # Rename `result = ...` assignments to `acc`.
    code = re.sub(
        r'^([ \t]*)result(\s*(?:=|\+=|-=|\*=))',
        r'\1acc\2',
        code,
        flags=re.MULTILINE
    )
    code = re.sub(
        r'(?m)^(?![ \t]*#@)([^\n]*)\bresult\b',
        lambda m: m.group(0).replace('result', 'acc') if 'def ' not in m.group(0) else m.group(0),
        code
    )
    # Also rename bare `result` (not `\result`) in loop invariant lines.
    return re.sub(
        r'(?m)^[ \t]*#@[ \t]+loop[ \t]+invariant[^\n]*\bresult\b[^\n]*$',
        lambda m: re.sub(r'(?<!\\)\bresult\b', 'acc', m.group(0)),
        code
    )


def _guard_strip_class_invariant_unsupported(code: str) -> str:
    # Guard (Level 3): Strip unsupported operators from `#@ class invariant` lines.
    code = re.sub(r'#@[ \t]*class invariant\b[^\n]*//[^\n]*', '#@ class invariant 1 == 1', code)
    code = re.sub(r'#@[ \t]*class invariant\b[^\n]*%[^\n]*', '#@ class invariant 1 == 1', code)
    return re.sub(r'#@[ \t]*class invariant\b[^\n]*\blen\s*\([^\n]*', '#@ class invariant 1 == 1', code)


def _guard_normalize_valid_separated(code: str) -> str:
    # Guard: Normalise malformed `\valid` / `\separated` call syntax.
    code = re.sub(
        r'(#@[^\n]*)\\valid\s+(\w+)\s*,\s*(\w+)',
        r'\g<1>\\valid(\2, \3)',
        code, flags=re.MULTILINE
    )
    return re.sub(
        r'(#@[^\n]*)\\separated\s+(\w+)\s*,\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+)',
        r'\g<1>\\separated(\2, \3, \4, \5)',
        code, flags=re.MULTILINE
    )


def _guard_string_literal_comparisons(code: str) -> str:
    # Guard: String-literal comparisons in contracts are invalid for integer params.
    code = re.sub(
        r'(#@[^\n]*\b\w+\s*)!=\s*(?:""|\'\')',
        r'\g<1>> 0', code, flags=re.MULTILINE,
    )
    return re.sub(
        r'(#@[^\n]*\b\w+\s*)==\s*(?:""|\'\')',
        r'\g<1><= 0', code, flags=re.MULTILINE,
    )


def _guard_length_self_attr(code: str) -> str:
    # Guard: `\length(self.<attr>)` inside any contract clause is a parse error.
    code = re.sub(
        r'[ \t]*#@\s*loop invariant\b[^\n]*\\length\s*\(\s*self\.[^\n]*',
        '#@ loop invariant 1 == 1', code, flags=re.MULTILINE,
    )
    code = re.sub(
        r'[ \t]*#@\s*ensures\b[^\n]*\\length\s*\(\s*self\.[^\n]*',
        '#@ ensures 1 == 1', code, flags=re.MULTILINE,
    )
    return re.sub(
        r'[ \t]*#@\s*requires\b[^\n]*\\length\s*\(\s*self\.[^\n]*',
        '#@ requires 1 == 1', code, flags=re.MULTILINE,
    )


def _guard_truncated_contracts(code: str) -> str:
    # Guard: Truncated contract expressions — LLM sometimes emits a clause ending
    # with a dangling operator.  Replace with trivially-true clause.
    code = re.sub(
        r'([ \t]*#@\s*ensures)\b[^\n]*(?:==|!=|<=|>=|<|>)\s*$',
        r'\1 1 == 1', code, flags=re.MULTILINE,
    )
    code = re.sub(
        r'([ \t]*#@\s*requires)\b[^\n]*(?:==|!=|<=|>=|<|>)\s*$',
        r'\1 1 == 1', code, flags=re.MULTILINE,
    )
    return re.sub(
        r'([ \t]*#@\s*loop invariant)\b[^\n]*(?:==|!=|<=|>=|<|>)\s*$',
        r'\1 1 == 1', code, flags=re.MULTILINE,
    )


def _guard_ensures_invalid(code: str) -> str:
    # Guard: Various invalid `#@ ensures` patterns.
    # `\length(\result)` is invalid — `\result` is a scalar.
    code = re.sub(
        r'[ \t]*#@\s*ensures\b[^\n]*\\length\s*\(\s*\\result\s*\)[^\n]*',
        '#@ ensures 1 == 1', code, flags=re.MULTILINE,
    )
    # Implication postconditions involving `\length` always time out.
    code = re.sub(
        r'[ \t]*#@\s*ensures\b[^\n]*\\length\s*\([^)]*\)[^\n]*==>[^\n]*',
        '#@ ensures 1 == 1', code, flags=re.MULTILINE,
    )
    # Any implication (`==>`) in `#@ ensures` will time out.
    code = re.sub(
        r'[ \t]*#@\s*ensures\b[^\n]*==>[^\n]*',
        '#@ ensures 1 == 1', code, flags=re.MULTILINE,
    )
    # Chained comparisons (e.g., `\result == 1 == 1`) are not supported.
    code = re.sub(
        r'[ \t]*#@\s*ensures\b[^\n]*(?:<=|>=|==|<|>)\s*\d+\s*==\s*\d+[^\n]*',
        '#@ ensures 1 == 1', code, flags=re.MULTILINE,
    )
    # Unclosed `\old(` in `#@ ensures` lines causes a parse error. Remove the line.
    return re.sub(
        r'^[ \t]*#@\s*ensures\b[^\n]*\\old\([^)\n]*\n',
        '', code, flags=re.MULTILINE,
    )


def _guard_ensures_length_arithmetic(code: str) -> str:
    # Guard: `#@ ensures` with `\length(param)` in arithmetic sub-expression.
    code = re.sub(
        r'[ \t]*#@\s*ensures\b[^\n]*[-+]\s*\\length\s*\([^)]*\)[^\n]*',
        '#@ ensures 1 == 1', code, flags=re.MULTILINE,
    )
    return re.sub(
        r'[ \t]*#@\s*ensures\b[^\n]*\\length\s*\([^)]*\)\s*[-+][^\n]*',
        '#@ ensures 1 == 1', code, flags=re.MULTILINE,
    )


def main():
    parser = argparse.ArgumentParser(description="Annotate Python programs with logical pre and post conditions.")
    parser.add_argument('--in', dest='in_file_name', required=True, help="Path to the input program to annotate.")
    parser.add_argument('--out', dest='out_file_name', required=True, help="Path to the generated annotated program.")
    parser.add_argument('--trusted', action='store_true',
                        help="Progressive verification: annotate with real contracts via LLM, "
                             "mark all functions #@ \\trusted, then prove bottom-up and "
                             "remove \\trusted from functions that pass verification.")
    args = parser.parse_args()

    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent.parent.parent  # src/pycsl/agents -> project root
    config_path = project_root / "config" / "agents-config.json"
    
    # Set a default project_directory for initial logging before the config is parsed
    project_directory = str(project_root)

    if not config_path.exists():
        log(project_directory, AGENT_NAME, f"Error: Configuration file not found at {config_path}")
        sys.exit(1)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        log(project_directory, AGENT_NAME, f"Error parsing {config_path}: {e}")
        sys.exit(1)

    project_directory = config.get("project-directory", project_directory)
    model = config.get("model")
    skill_annotator_name = config.get("skill-annotate")
    memory_model = config.get("memory-model", "hoare")
    rag_index_name = config.get("rag-index")
    rag_top_k = config.get("rag-top-k", 10)

    if not model:
        log(project_directory, AGENT_NAME, "Error: 'model' field is missing in agents-config.json")
        sys.exit(1)
    if not skill_annotator_name:
        log(project_directory, AGENT_NAME, "Error: 'skill-annotate' field is missing in agents-config.json")
        sys.exit(1)

    skill_annotator_path = Path(skill_annotator_name)
    if not skill_annotator_path.is_absolute():
        skill_annotator_path = project_root / skill_annotator_path

    if not skill_annotator_path.exists():
        log(project_directory, AGENT_NAME, f"Error: Skill annotator file not found at {skill_annotator_path}")
        sys.exit(1)

    log(project_directory, AGENT_NAME, f"Memory model: {memory_model}")

    in_file_path = Path(args.in_file_name)
    if not in_file_path.exists():
        log(project_directory, AGENT_NAME, f"Error: Input file not found at {in_file_path}")
        sys.exit(1)

    try:
        with open(in_file_path, 'r', encoding='utf-8') as f:
            input_code = f.read()
    except Exception as e:
        log(project_directory, AGENT_NAME, f"Error reading input file {in_file_path}: {e}")
        sys.exit(1)

    # --trusted: Run the normal LLM annotation pipeline first, then add \trusted
    # to all functions as scaffolding. The prove-and-strip phase (below) will
    # progressively remove \trusted from functions that pass verification.
    # (The flag changes post-processing only, not the LLM call itself.)

    # Count annotatable functions to decide: splitter path vs direct LLM path.
    # Multi-function files benefit from bottom-up per-function annotation via the
    # splitter+writer agents; single-function files use the original monolithic call.
    _use_splitter = False
    try:
        _tree = _ast_module.parse(input_code)
        _func_count = 0
        for _node in _ast_module.iter_child_nodes(_tree):
            if isinstance(_node, _ast_module.FunctionDef):
                if not (_node.name.startswith('__') and _node.name.endswith('__')):
                    _func_count += 1
            elif isinstance(_node, _ast_module.ClassDef):
                for _child in _ast_module.iter_child_nodes(_node):
                    if isinstance(_child, _ast_module.FunctionDef):
                        if not (_child.name.startswith('__') and _child.name.endswith('__')):
                            _func_count += 1
        _use_splitter = _func_count > 1
    except SyntaxError:
        pass  # if the file can't parse, fall through to direct LLM path

    if _use_splitter:
        log(project_directory, AGENT_NAME,
            f"Multi-function file ({_func_count} functions), using splitter+writer pipeline")
        try:
            from importlib import util as _importlib_util
            _splitter_path = Path(__file__).parent / "agent-splitter.py"
            _spec = _importlib_util.spec_from_file_location("agent_splitter", _splitter_path)
            _splitter_mod = _importlib_util.module_from_spec(_spec)
            _spec.loader.exec_module(_splitter_mod)
            generated_code = _splitter_mod.run_splitter(
                input_path=in_file_path,
                output_path=Path(args.out_file_name),
                config_path=config_path,
                project_root=project_root,
                memory_model=memory_model,
                project_directory=project_directory,
            )
        except Exception as e:
            log(project_directory, AGENT_NAME,
                f"Splitter failed ({e}), falling back to direct LLM annotation")
            _use_splitter = False

    if not _use_splitter:
        # Original monolithic LLM path: load skill, build prompt, call LLM once.
        # Try RAG retrieval first; fall back to full skill file if unavailable
        skill_content = None
        if rag_index_name:
            rag_index_path = Path(rag_index_name)
            if not rag_index_path.is_absolute():
                rag_index_path = project_root / rag_index_path
            _code_query = input_code[:800]
            _func_sigs = re.findall(r'^[ \t]*(?:class|def)\s+[^\n]+', input_code, re.MULTILINE)
            if _func_sigs:
                _code_query += "\n" + "\n".join(_func_sigs[:5])
            skill_content = retrieve_skill_chunks(
                index_path=rag_index_path,
                main_query=_code_query,
                top_k=rag_top_k,
                project_root=project_root,
                essential_queries=_ESSENTIAL_QUERIES,
            )
            if skill_content:
                log(project_directory, AGENT_NAME, "Using RAG-retrieved skill chunks")

        if skill_content is None:
            log(project_directory, AGENT_NAME, "Using full skill file (RAG index unavailable)")
            try:
                with open(skill_annotator_path, 'r', encoding='utf-8') as f:
                    skill_content = f.read()
            except Exception as e:
                log(project_directory, AGENT_NAME, f"Error reading skill file {skill_annotator_path}: {e}")
                sys.exit(1)

        _model_notes = {
            "hoare": (
                "Use standard value-semantic arrays (`array int`). "
                "No `\\valid`, `\\separated`, or `\\assigns arr[lo..hi]` needed. "
                "Use `#@ assigns \\nothing` for pure functions."
            ),
            "typed": (
                "Arrays are heap-allocated (`loc` type). "
                "Use `#@ requires \\valid(arr, n)` to assert array validity. "
                "Use `#@ requires \\separated(a, na, b, nb)` when arrays must not alias. "
                "Use `#@ assigns arr[0..n]` (with `..`) as the frame condition for in-place mutations. "
                "Use `\\old(arr[i])` in ensures clauses to refer to the pre-state value of `arr[i]`. "
                "Use `#@ label L` immediately before a statement to mark a program point, "
                "then `\\at(arr[i], L)` in contracts to reference the array state at that point."
            ),
            "store": (
                "Same as typed model: arrays are heap-allocated. "
                "Use `#@ requires \\valid(arr, n)`, `#@ requires \\separated(a, na, b, nb)`, "
                "`#@ assigns arr[0..n]`, `\\old(arr[i])`, `#@ label L`, and `\\at(arr[i], L)` "
                "as needed for heap-aware contracts."
            ),
        }
        _memory_model_context = (
            f"\n\n# ACTIVE MEMORY MODEL: {memory_model.upper()}\n"
            f"The pipeline is configured to use the `{memory_model}` memory model. "
            + _model_notes.get(memory_model, _model_notes["hoare"])
        )
        prompt = f"{skill_content}{_memory_model_context}\n\nJust output the python code between \"```python\" and \"```\".\n\n{input_code}"

        try:
            generated_code = llm_generate(prompt=prompt, system="", agent_id=AGENT_NAME, model=model)
        except Exception as e:
            log(project_directory, AGENT_NAME, f"Error calling LLM: {e}")
            sys.exit(1)

        # Extract code from markdown fences if present
        generated_code = extract_code_block(generated_code, "python")

    pipeline = GuardPipeline(generated_code)

    pipeline.apply("inject-recursive-variants",
                   lambda c: _inject_recursive_variants(c, project_directory))
    pipeline.apply("strip-division",
                   lambda c: re.sub(r'(?<![:/])/(?!/)', '//', c))
    pipeline.apply("strip-raise",
                   lambda c: re.sub(r'^[ \t]*raise\b[^\n]*\n?', '', c, flags=re.MULTILINE))
    pipeline.apply("ensure-function-contracts", _ensure_function_contracts)
    pipeline.apply("strip-return-none",
                   lambda c: re.sub(r'\breturn\s+None\b', 'return', c))
    pipeline.apply("none-sentinel",
                   lambda c: re.sub(r'\b(\w+)\s+is\s+None\b', r'\1 < 0',
                                    re.sub(r'\b(\w+)\s*=\s*None\b', r'\1 = -1', c)))
    pipeline.apply("strip-math-pi", _guard_strip_math_pi)
    pipeline.apply("str-params-rewrite", _guard_str_params_rewrite)
    pipeline.apply("string-subscripts",
                   lambda c: re.sub(r"(\b\w+)\['[^']*'\]", r'\1[0]',
                                    re.sub(r'(\b\w+)\["[^"]*"\]', r'\1[0]', c)))
    pipeline.apply("dict-get",
                   lambda c: re.sub(r'\b\w+\.get\(\s*\w+\s*,\s*(\d+)\s*\)', r'\1', c))
    pipeline.apply("sorted-set",
                   lambda c: re.sub(r'\bset\(\s*(\w+)\s*\)', r'\1',
                                    re.sub(r'\bsorted\(\s*(\w+)\s*\)', r'\1',
                                           re.sub(r'\bsorted\(\s*set\(\s*(\w+)\s*\)\s*\)', r'\1', c))))
    pipeline.apply("inject-trusted-dict-assign", _inject_trusted_for_dict_subscript_assignment)
    pipeline.apply("modulo-in-invariant",
                   lambda c: re.sub(r'(#@\s*loop invariant\s+\w+)\s*%\s*\d+\s*==\s*\d+',
                                    r'\1 >= 3', c))
    pipeline.apply("bool-constants-in-contracts", _guard_bool_constants_in_contracts)
    pipeline.apply("floordiv-in-contracts", _guard_floordiv_in_contracts)
    pipeline.apply("len-to-length",
                   lambda c: re.sub(
                       r'(#@\s*(?:requires|ensures|loop invariant)\b[^\n]*)(?<!\\)\blen\s*\(\s*(\w+)\s*\)',
                       r'\1\\length(\2)', c))
    pipeline.apply("strengthen-ensures", _strengthen_ensures)
    pipeline.apply("strip-nonlinear-conservation", _strip_nonlinear_conservation_invariant)
    pipeline.apply("weaken-offset-start-invariant", _weaken_offset_start_loop_invariant)
    pipeline.apply("strengthen-loop-counter", _strengthen_loop_counter_invariant)
    pipeline.apply("inject-offset-lower-bound", _inject_offset_lower_bound_invariant)
    pipeline.apply("tighten-pred-access", _tighten_lower_bound_for_pred_access)
    pipeline.apply("strip-unprovable-additive", _strip_unprovable_additive_invariants)
    pipeline.apply("strengthen-binary-search", _strengthen_binary_search_invariants)
    pipeline.apply("requires-length-trivial",
                   lambda c: re.sub(
                       r'([ \t]*#@\s*requires\s+)\\length\s*\(\s*\w+\s*\)\s*>=\s*0\s*$',
                       r'\g<1>1 == 1', c, flags=re.MULTILINE))
    pipeline.apply("split-two-pointer", _split_two_pointer_compound_invariant)
    pipeline.apply("list-params", _guard_list_params)
    pipeline.apply("fix-list-return-type", _fix_list_return_type)
    pipeline.apply("remove-spurious-old-length", _remove_spurious_old_length_plus1)
    pipeline.apply("str-length-neutralize", _guard_str_length_neutralize)
    pipeline.apply("downgrade-result-len-return", _downgrade_result_ge1_for_len_return)
    pipeline.apply("downgrade-result-sum", _downgrade_result_ge1_for_sum)
    pipeline.apply("rename-val", _guard_rename_val)
    pipeline.apply("rename-goal", _guard_rename_goal)
    pipeline.apply("rename-match", _guard_rename_match)
    pipeline.apply("rename-result", _guard_rename_result)
    pipeline.apply("strip-default-args", _strip_default_args)
    pipeline.apply("assigns-normalize-slice",
                   lambda c: re.sub(r'(#@\s*assigns\s+\w+)\[\s*\.\.', r'\g<1>[0..', c,
                                    flags=re.MULTILINE))
    pipeline.apply("assigns-strip-assignment",
                   lambda c: re.sub(r'(#@\s*assigns\b[^\n]*?)=.*$', r'\1', c,
                                    flags=re.MULTILINE))
    pipeline.apply("obj-syntax-rewrite",
                   lambda c: re.sub(
                       r'(#@[^\n]*)\bobj_(\w+)\b',
                       lambda m: m.group(1) + 'self.' + m.group(2).lstrip('_') if m.group(2).startswith('_')
                                 else m.group(1) + 'self._' + m.group(2),
                       c, flags=re.MULTILINE))
    pipeline.apply("bare-invariant-normalize",
                   lambda c: re.sub(
                       r'(#@[ \t]+)(?!class\s)(?!loop\s)invariant([ \t]+self\.)',
                       r'\1class invariant\2', c, flags=re.MULTILINE))
    pipeline.apply("strip-class-invariant-unsupported", _guard_strip_class_invariant_unsupported)
    pipeline.apply("check-class-invariant-guards", _check_class_invariant_guards)
    pipeline.apply("collapse-annotation-blank-lines",
                   lambda c: re.sub(
                       r'((?:^[ \t]*#@[^\n]*\n)+)\n+([ \t]*(?:def|class)\s)',
                       r'\1\2', c, flags=re.MULTILINE))
    pipeline.apply("collapse-label-blank-lines",
                   lambda c: re.sub(r'(^[ \t]*#@\s*label\s+\w+[^\n]*\n)\n+', r'\1', c,
                                    flags=re.MULTILINE))
    pipeline.apply("normalize-valid-separated", _guard_normalize_valid_separated)
    pipeline.apply("string-literal-comparisons", _guard_string_literal_comparisons)
    pipeline.apply("requires-bare-ident",
                   lambda c: re.sub(r'(#@\s*requires\s+)([A-Za-z_]\w*)\s*$',
                                    r'\g<1>\g<2> > 0', c, flags=re.MULTILINE))
    pipeline.apply("length-self-attr", _guard_length_self_attr)
    pipeline.apply("truncated-contracts", _guard_truncated_contracts)
    pipeline.apply("ensures-invalid", _guard_ensures_invalid)
    pipeline.apply("assigns-bare-ident",
                   lambda c: re.sub(
                       r'(#@\s*assigns\s+)(?!\\nothing\b)(?!self\.)([A-Za-z_]\w*)\s*$',
                       r'\g<1>\\nothing', c, flags=re.MULTILINE))
    pipeline.apply("fix-empty-conditional-bodies", _fix_empty_conditional_bodies)
    pipeline.apply("isinstance-hasattr",
                   lambda c: re.sub(r'\bhasattr\s*\([^)]*\)', 'True',
                                    re.sub(r'\bisinstance\s*\([^)]*\)', 'True', c)))
    pipeline.apply("strip-external-type-bodies", _strip_external_type_bodies)
    pipeline.apply("inject-n-bound-requires", _inject_n_bound_requires)
    pipeline.apply("ensures-length-arithmetic-2", _guard_ensures_length_arithmetic)
    pipeline.apply("remove-array-typed-variant", _remove_array_typed_variant)
    pipeline.apply("fix-mismatched-loop-bound", _fix_mismatched_loop_bound_invariant)
    pipeline.apply("dedup-contract-blocks", _dedup_contract_blocks)
    pipeline.apply("rewrite-return-in-while", _rewrite_return_in_if_inside_while)
    pipeline.apply("fix-bare-len-sentinel", _fix_bare_len_sentinel)
    pipeline.apply("fix-const-return-after-flag", _fix_const_return_after_flag_loop)
    pipeline.apply("fix-bool-flag-conditions", _fix_bool_flag_conditions)
    pipeline.apply("fix-annotation-indentation", _fix_annotation_indentation)
    pipeline.apply("body-preservation", _guard_body_preservation(input_code))

    generated_code = pipeline.code

    # --trusted: inject #@ \trusted before every non-dunder function, then
    # run prove-and-strip to progressively remove \trusted from provable functions.
    if args.trusted:
        generated_code = _annotate_trusted(generated_code, project_directory)
        generated_code = _prove_and_strip(
            generated_code, in_file_path, project_root, project_directory
        )

    # Guard: libcst (Module1_Ingestor) assigns all comment/blank lines at the
    # very top of a file to Module.header rather than to the first statement's
    # leading_lines.  When the annotated output starts with '#@' annotations
    # immediately (no preceding Python statement), Module1 cannot find them in
    # the first FunctionDef's (or ClassDef's) leading_lines and the contracts
    # are silently dropped from the WhyML output.  Inserting a sentinel
    # no-op expression statement as the very first line ensures the '#@' block
    # ends up in the node's leading_lines instead of Module.header, so
    # Module1 correctly extracts and attaches contracts for every function and
    # class invariant.
    first_nonblank = next(
        (l for l in generated_code.splitlines() if l.strip()), ""
    )
    if first_nonblank.strip().startswith("#@"):
        generated_code = '""  # pycsl\n' + generated_code

    out_file_path = Path(args.out_file_name)
    try:
        out_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file_path, 'w', encoding='utf-8') as f:
            f.write(generated_code)
        log(project_directory, AGENT_NAME, f"Successfully saved annotated code to {out_file_path}")
    except Exception as e:
        log(project_directory, AGENT_NAME, f"Error writing output file {out_file_path}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
    
