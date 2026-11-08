import ast, sys

# map: live file -> set of trusted method names
targets = {
 "src/pycsl/module6_whyml/expressions.py": None,  # fill below
 "src/pycsl/module6_whyml/statements.py": None,
 "src/pycsl/frontend/Module5_IREmitter.py": None,
}

trusted = {
 "src/pycsl/module6_whyml/expressions.py": "_add_abstract_op _is_emit_ir_expr _e _to_bool _coerce_to_int _match_pattern_cond _emit_membership _emit_bitwise_or_power _is_string_expr _handle_binop _iter_len_expr _handle_len_call _handle_join_call _handle_sum_call _resolve_dotted_signature _handle_dotted_call _coerce_dotted_args _dotted_ensures_suffix _handle_struct_call _emit_contract_logic_symbol _linear_form _static_width _handle_call_expr _content_string_method _call_named_builtins _emit_metatype_tags _tag_of_value _handle_isinstance _call_record_constructor _call_bytes_methods _handle_subscript _handle_attribute_expr _push_quant_binder _pop_quant_binder _handle_fstring_expr _handle_ifexpr_expr _expr_to_whyml _expr_to_whyml_string_ctx".split(),
 "src/pycsl/module6_whyml/statements.py": "_add_abstract_op _resolve_dotted_signature _is_emit_ir_expr _coerce_to_int _expr_to_whyml _expr_to_whyml_string_ctx _is_string_expr _track_collection_metadata _e _maybe_emit_no_exception_assert _mutex_inv_application _handle_return_stmt _emit_first_assign _emit_array_local_reassign _handle_assign_stmt _seq_init_expr _seq_operand _handle_ghost_assign_stmt _handle_tuple_unpack_stmt _handle_array_set_stmt _handle_augassign_stmt _handle_expr_stmt _stmts_to_whyml _emit_frame_condition _typed_local_vars _emit_body_code".split(),
 "src/pycsl/frontend/Module5_IREmitter.py": "__init__ visit_Module _get_mutex_invariant_ir _csl_to_ir _csl_in _csl_list_to_ir _py_op_to_str _py_expr_to_ir _py_expr_call _py_expr_fstring _py_stmts_to_ir _py_stmt_raise _match_pattern_to_ir _field_type_from_annotation_inst _emit_typeddict_record _synthesize_typeddict_functional _emit_namedtuple_record _synthesize_namedtuple_functional _emit_protocol_interface _populate_protocol_conformance _collect_class_fields _array_init_size visit_ClassDef _collect_union_arms _normalize_union_annotation _normalize_literal_annotation _encode_callable_annotation _m5_get_type_name _build_function_symbol_table _build_function_ir _detect_array_dimensions _detect_seq_promotion visit_FunctionDef _is_overload_stub generate_json".split(),
}

def has_idiom(fn):
    # find: if X is None: return None  ; then a tuple-unpack Assign target Tuple with value Name X
    # and function ends with a return of something (not None)
    guarded = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.If):
            t = node.test
            # X is None
            if isinstance(t, ast.Compare) and len(t.ops)==1 and isinstance(t.ops[0], ast.Is) \
               and isinstance(t.comparators[0], ast.Constant) and t.comparators[0].value is None \
               and isinstance(t.left, ast.Name):
                # body has return None (or return)
                for b in node.body:
                    if isinstance(b, ast.Return) and (b.value is None or (isinstance(b.value, ast.Constant) and b.value.value is None)):
                        guarded.add(t.left.id)
    # tuple unpack of a guarded var
    unpacked = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign):
            if len(node.targets)==1 and isinstance(node.targets[0], (ast.Tuple, ast.List)) \
               and isinstance(node.value, ast.Name) and node.value.id in guarded:
                unpacked.add(node.value.id)
    return guarded & unpacked

for f, names in trusted.items():
    src = open(f).read()
    tree = ast.parse(src)
    fns = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fns[node.name] = node
    print("===", f, "===")
    for n in names:
        if n not in fns:
            print("  MISSING", n); continue
        hit = has_idiom(fns[n])
        if hit:
            print("  IDIOM ", n, "vars=", hit, "lines", fns[n].lineno, "-", fns[n].end_lineno)
