"""framefix.py <mirror.py-relpath> [--apply]
Give the cross-mixin `_expr_to_whyml` protocol stub its honest `#@ assigns`, then merge the
same field set into every CONVERTED method in the file whose body calls it. Prints a summary.
"""
import ast, sys, os, re
FIELDS = ["self._comp_content_counter","self._current_params","self._current_self_type",
          "self._frame_trigger_active","self._func_return_type","self._in_spec",
          "self._last_hval_get_raw","self._last_hval_get_str","self._needs_array_init",
          "self._obj_state_written","self._string_local_vars","self._todict_arg_wants_pymap",
          "self._uses_build_param_list_cache","self._uses_compute_return_type_cache",
          "self._uses_const_reflect_cache","self._uses_pyast_parser_cache",
          "self._uses_refine_tuple_return_type_cache"]
rel = sys.argv[1]
P = os.path.join("src/self-annotate/src", rel)
src = open(P).read()
lines = src.split("\n")
tree = ast.parse(src)
MARK = re.compile(r"^#@\s*\\trusted\b")

def block(fn):
    """(start_idx, end_idx) of the `#@`/comment block above fn, and whether trusted."""
    first = min([d.lineno for d in fn.decorator_list] + [fn.lineno]) - 1
    i = first - 1
    tr = False
    while i >= 0:
        st = lines[i].strip()
        if not (st.startswith("#") or st.startswith("@") or st == ""):
            break
        if MARK.match(st):
            tr = True
        i -= 1
    return i + 1, first, tr

targets = []
def walk(scope, cls):
    for n in scope:
        if isinstance(n, ast.ClassDef):
            walk(n.body, n.name)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            b0, b1, tr = block(n)
            body = ast.unparse(n)
            calls = "self._expr_to_whyml(" in body
            is_stub = (n.name == "_expr_to_whyml")
            if is_stub or (calls and not tr):
                targets.append((n.name, cls, b0, b1, tr, is_stub))
walk(tree.body, None)

out = list(lines)
for name, cls, b0, b1, tr, is_stub in sorted(targets, key=lambda t: -t[2]):
    ind = None
    have = None
    for k in range(b0, b1):
        st = out[k].strip()
        if st.startswith("#@ assigns"):
            have = k
        if ind is None and st.startswith("#@"):
            ind = out[k][:len(out[k]) - len(out[k].lstrip())]
    if ind is None:
        ind = out[b1][:len(out[b1]) - len(out[b1].lstrip())]
    cur = []
    if have is not None:
        txt = out[have].strip()[len("#@ assigns"):].strip()
        if txt and txt != "\\nothing":
            cur = [x.strip() for x in txt.split(",") if x.strip()]
    merged = sorted(set(cur) | set(FIELDS))
    newline = ind + "#@ assigns " + ", ".join(merged)
    if have is not None:
        out[have] = newline
    else:
        out.insert(b1, newline)
    print(("STUB " if is_stub else "CALLER "), (cls or "") + "." + name, "->", len(merged), "fields")
if "--apply" in sys.argv:
    open(P, "w").write("\n".join(out))
    print("APPLIED to", P)
