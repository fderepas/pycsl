#!/bin/bash
# repair_witness.sh <tree> <scratch-dir> — route #488 repair: negative witnesses + controls.
# Run through heavy.sh. Each WITNESS re-narrows ONE repaired frame back to `assigns \nothing`
# in a scratch copy of the mirror file (the honest widened `_e` / `_expr_to_whyml_string_ctx`
# declarations kept) and must NOT type-check / emit (expected FAIL). Each CONTROL is the repaired
# file unchanged and must type-check (expected PASS; its whole-file proof is in the route note).
# W3 restores `_handle_mktuple_expr`'s live body (un-trusted) and must be REFUSED (ir-semantic:
# writing call inside an opaque comprehension) — why that handler is re-trusted.
set -u
T=$1; S=$2; mkdir -p "$S"
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
M=$T/src/self-annotate/src/module6_whyml
FR='#@ assigns self._abstract_ops, self._comp_content_counter, self._current_params, self._current_self_type, self._dict_locals, self._frame_trigger_active, self._func_return_type, self._in_spec, self._last_hval_get_raw, self._last_hval_get_str, self._late_content_ops, self._needs_array_init, self._obj_state_written, self._quant_record_binders, self._quant_scalar_binders, self._string_local_vars, self._todict_arg_wants_pymap, self._uses_build_param_list_cache, self._uses_compute_return_type_cache, self._uses_const_reflect_cache, self._uses_pyast_parser_cache, self._uses_refine_tuple_return_type_cache'
narrow() {  # <src> <dst> <method> : replace the frame line right above `def <method>(` with \nothing
  python3 - "$1" "$2" "$3" "$FR" <<'PY'
import sys
src, dst, meth, fr = sys.argv[1:]
L = open(src).read().split("\n")
i = [k for k, l in enumerate(L) if l.strip().startswith("def %s(" % meth)][0]
assert L[i-1].strip() == fr, L[i-1]
L[i-1] = L[i-1].replace(fr, "#@ assigns \\nothing")
open(dst, "w").write("\n".join(L))
PY
}
run() {  # <label> <expect PASS|FAIL> <file>
  ( cd "$T" && PYTHONHASHSEED=0 .venv/bin/python3 src/pycsl/pycsl.py "$3" --import-path src/pycsl --no-proof > "$3.log" 2>&1 )
  rc=$?; ok=FAIL; [ $rc -eq 0 ] && grep -q 'L3-tc ✓' "$3.log" && ok=PASS
  v=MISMATCH; [ "$ok" = "$2" ] && v=AS-EXPECTED
  echo "$1 expect=$2 got=$ok rc=$rc $v :: $(grep -m1 -E 'left out in the|PIPELINE ERROR|WRITES' "$3.log" | cut -c1-140)"
}
cp "$M/expr_ghost_collections.py" "$S/c_ctl.py"; run C1-collections-control PASS "$S/c_ctl.py"
narrow "$M/expr_ghost_collections.py" "$S/c_w1.py" _handle_has_key_expr; run W1-has_key-nothing FAIL "$S/c_w1.py"
cp "$M/expr_ghost_spec_ops.py" "$S/s_ctl.py"; run C2-spec_ops-control PASS "$S/s_ctl.py"
narrow "$M/expr_ghost_spec_ops.py" "$S/s_w2.py" _handle_fst_expr; run W2-fst-nothing FAIL "$S/s_w2.py"
python3 - "$M/expr_ghost_spec_ops.py" "$S/s_w3.py" <<'PY'
import sys
s = open(sys.argv[1]).read()
i = s.index("    def _handle_mktuple_expr(")
j = s.rindex("    #@ \\trusted reviewer: pycsl-self-annotate\n", 0, i)
s = s[:j] + s[j:i].replace("    #@ \\trusted reviewer: pycsl-self-annotate\n", "", 1) + s[i:]
k = s.index('        return ""\n', s.index("    def _handle_mktuple_expr("))
s = s[:k] + '        parts = ", ".join([self._e(e, lr) for e in node.elts])\n        return f"({parts})"\n' + s[k+len('        return ""\n'):]
assert 'parts = ", ".join([self._e(e, lr) for e in node.elts])' in s
open(sys.argv[2], "w").write(s)
PY
run W3-mktuple-untrusted FAIL "$S/s_w3.py"
echo DONE
