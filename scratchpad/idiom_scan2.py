import ast, glob

trusted = {
 "expressions": "_add_abstract_op _is_emit_ir_expr _e _to_bool _coerce_to_int _match_pattern_cond _emit_membership _emit_bitwise_or_power _is_string_expr _handle_binop _iter_len_expr _handle_len_call _handle_join_call _handle_sum_call _resolve_dotted_signature _handle_dotted_call _coerce_dotted_args _dotted_ensures_suffix _handle_struct_call _emit_contract_logic_symbol _linear_form _static_width _handle_call_expr _content_string_method _call_named_builtins _emit_metatype_tags _tag_of_value _handle_isinstance _call_record_constructor _call_bytes_methods _handle_subscript _handle_attribute_expr _push_quant_binder _pop_quant_binder _handle_fstring_expr _handle_ifexpr_expr _expr_to_whyml _expr_to_whyml_string_ctx".split(),
 "statements": "_track_collection_metadata _maybe_emit_no_exception_assert _mutex_inv_application _handle_return_stmt _emit_first_assign _emit_array_local_reassign _handle_assign_stmt _seq_init_expr _seq_operand _handle_ghost_assign_stmt _handle_tuple_unpack_stmt _handle_array_set_stmt _handle_augassign_stmt _handle_expr_stmt _stmts_to_whyml _emit_frame_condition _typed_local_vars _emit_body_code".split(),
 "Module5": "visit_Module _get_mutex_invariant_ir _csl_to_ir _csl_in _csl_list_to_ir _py_op_to_str _py_expr_to_ir _py_expr_call _py_expr_fstring _py_stmts_to_ir _py_stmt_raise _match_pattern_to_ir _field_type_from_annotation_inst _emit_typeddict_record _synthesize_typeddict_functional _emit_namedtuple_record _synthesize_namedtuple_functional _emit_protocol_interface _populate_protocol_conformance _collect_class_fields _array_init_size visit_ClassDef _collect_union_arms _normalize_union_annotation _normalize_literal_annotation _encode_callable_annotation _m5_get_type_name _build_function_symbol_table _build_function_ir _detect_array_dimensions _detect_seq_promotion visit_FunctionDef _is_overload_stub generate_json".split(),
}
allnames=set()
for v in trusted.values(): allnames|=set(v)

# collect all funcs from all live pycsl files
livefiles = glob.glob("src/pycsl/**/*.py", recursive=True)
funcloc={}  # name -> list of (file, node)
for f in livefiles:
    try: tree=ast.parse(open(f).read())
    except: continue
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
            funcloc.setdefault(node.name,[]).append((f,node))

def guards(fn):
    g=set()
    for node in ast.walk(fn):
        if isinstance(node,ast.If):
            t=node.test; var=None
            if isinstance(t,ast.Compare) and len(t.ops)==1 and isinstance(t.ops[0],ast.Is) and isinstance(t.comparators[0],ast.Constant) and t.comparators[0].value is None and isinstance(t.left,ast.Name):
                var=t.left.id
            elif isinstance(t,ast.UnaryOp) and isinstance(t.op,ast.Not) and isinstance(t.operand,ast.Name):
                var=t.operand.id
            elif isinstance(t,ast.Name):
                pass
            if var:
                for b in node.body:
                    if isinstance(b,ast.Return):
                        g.add(var)
    return g
def unpacks(fn):
    u={}
    for node in ast.walk(fn):
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],(ast.Tuple,ast.List)):
            if isinstance(node.value,ast.Name):
                u.setdefault(node.value.id,0)
    return set(u)

for name in sorted(allnames):
    locs=funcloc.get(name,[])
    if not locs:
        print("NOLIVE", name); continue
    for f,node in locs:
        g=guards(node); u=unpacks(node)
        hit=g&u
        if hit:
            print(f"IDIOM {name}  file={f}  vars={hit}  L{node.lineno}-{node.end_lineno}")
