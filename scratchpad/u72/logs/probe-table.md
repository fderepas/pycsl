| probe | CPython | L20 b0 | u70 | head |
|---|---|---|---|---|
| 10420_r624_module_qualified_call_local_def_false | result 1 | - | REFUSED  | FAILED |
| 10421_r624_alias_qualified_call_local_def_false | result 1 | - | REFUSED  | FAILED |
| 10422_r625_two_libs_same_function_false | result 3 | - | REFUSED  | FAILED |
| 10423_r625_qualified_and_from_import_two_libs_false | result 3 | - | REFUSED  | FAILED |
| 10424_r624_qualified_call_no_clash_ctl | (assert ok) | - | SUCCESS | SUCCESS |
| 10425_r624_from_import_alias_beside_local_def_ctl | (assert ok) | - | SUCCESS | SUCCESS |
| 10426_r625_alias_two_libs_ctl | (assert ok) | - | SUCCESS | SUCCESS |
| 10427_r624_same_dependency_function_twice_ctl | (assert ok) | - | SUCCESS | SUCCESS |
| 10450_r628_reexport_qualified_local_def_false | result 1 | - | SUCCESS | FAILED |
| 10451_r628_assign_reexport_local_def_false | result 1 | - | SUCCESS | FAILED |
| 10452_r628_reexport_vs_other_lib_qualified_false | result 3 | - | SUCCESS | FAILED |
| 10453_r629_two_libs_same_base_tail_false | result 21 | - | SUCCESS | REFUSED  |
| 10454_r629_from_import_vs_qualified_base_false | result 1 | - | SUCCESS | REFUSED  |
| 10455_r630_local_def_named_like_inherited_method_false | result 1 | - | SUCCESS | REFUSED  |
| 10456_r630_inlined_method_calls_local_helper_false | result 1 | - | SUCCESS | FAILED |
| 10457_o1_star_import_then_local_def_ctl | (assert ok) | - | REFUSED  | SUCCESS |
| 10458_o2_lib_private_helper_vs_local_ctl | (assert ok) | - | REFUSED  | SUCCESS |
| 10459_o3_lib_private_helper_vs_local_from_ctl | (assert ok) | - | REFUSED  | SUCCESS |
| 10460_o4_two_libs_private_helpers_ctl | (assert ok) | - | REFUSED  | SUCCESS |
| 10461_o5_two_libs_private_helpers_from_ctl | (assert ok) | - | REFUSED  | SUCCESS |
| 10462_r628_reexport_followed_ctl | (assert ok) | - | FAILED | SUCCESS |
| 10463_r629_single_lib_attribute_base_ctl | (assert ok) | - | FAILED | FAILED |
| 10464_r630_inlined_method_library_helper_ctl | (assert ok) | - | FAILED | SUCCESS |
| a01_reexport_qualified_local_def | 1 | - | SUCCESS | FAILED |
| a02_reexport_qualified_nolocal | 1 | - | FAILED | FAILED |
| a03_reexport_from_import | 1 | - | FAILED | FAILED |
| a04_reexport_qualified_vs_from_other | 3 | - | SUCCESS | FAILED |
| a05_reexport_qualified_vs_qualified_other | 3 | - | SUCCESS | FAILED |
| a06_reexport_alias_local_def | 1 | - | SUCCESS | FAILED |
| a07_pkg_init_reexport_local_def | 1 | - | SUCCESS | FAILED |
| a08_missing_attr_local_def_noexc | AttributeError: module 'rt80_liba' has n | - | REFUSED  | REFUSED  |
| a09_assign_reexport_local_def | 2 | - | SUCCESS | FAILED |
| b01_lib_rebind_qualified | 2 | - | REFUSED  | REFUSED  |
| b02_lib_rebind_from | 2 | - | REFUSED  | REFUSED  |
| b03_lib_rebind_star | 2 | - | REFUSED  | REFUSED  |
| c01_lib_conddef_qualified | 2 | - | REFUSED  | REFUSED  |
| c02_lib_trydef_qualified | 2 | - | REFUSED  | REFUSED  |
| c03_lib_redef_qualified | 2 | - | REFUSED  | REFUSED  |
| c327a_methodless_classes_casefold | (assert ok) | - | SUCCESS | SUCCESS |
| c327b_lifted_pair_plus_casefold | (assert ok) | - | REFUSED PYCSL-R327-IDENT-COLLISION | REFUSED PYCSL-R327-IDENT-COLLISION |
| d01_base_qualified_local_base | 1 | - | REFUSED  | REFUSED  |
| d02_base_two_libs | 21 | - | FAILED | REFUSED  |
| d03_base_qualified_vs_from_import | 1 | - | FAILED | REFUSED  |
| d04_base_ctl | 1 | - | FAILED | FAILED |
| d05_base_two_libs_param | 21 | - | SUCCESS | REFUSED  |
| d06_base_qualified_vs_from_param | 1 | - | SUCCESS | REFUSED  |
| d07_base_two_libs_param_ctl | 21 | - | FAILED | REFUSED  |
| d08_base_from_vs_qualified_param_b | 1 | - | SUCCESS | REFUSED  |
| d09_base_local_var | 21 | - | SUCCESS | REFUSED  |
| d10_base_fields_two_libs | 21 | - | FAILED | REFUSED  |
| d11_base_method_vs_local_mangled | 1 | - | SUCCESS | REFUSED  |
| e01_classes_C_c_exempt | (assert ok) | - | REFUSED PYCSL-R327-IDENT-COLLISION | REFUSED PYCSL-SEM-WHYML-NAME-CLASH |
| e02_class_helper_vs_other_lib_qualified | 2 | - | REFUSED  | FAILED |
| e02_method_vs_nested_in_method_exempt | (assert ok) | - | REFUSED  | REFUSED  |
| e03_class_helper_vs_local_def | 3 | - | FAILED | FAILED |
| e04_class_method_inline_global_local_helper | 1 | - | SUCCESS | FAILED |
| e04_diverges_upper_vs_lower | (assert ok) | - | REFUSED PYCSL-R327-IDENT-COLLISION | REFUSED PYCSL-SEM-WHYML-NAME-CLASH |
| e05_class_method_contract_helper_local | 1 | - | REFUSED  | FAILED |
| e05_rebind_noreturn_diff_sig | (assert ok) | - | SUCCESS | FAILED |
| e06_rebind_diverges_then_def | (assert ok) | - | REFUSED  | REFUSED  |
| e07_conditional_def_exempt | (assert ok) | - | REFUSED  | REFUSED  |
| e08_trusted_parent_nested_noreturn | (assert ok) | - | SUCCESS | FAILED |
| e09_import_noreturn_same_name | (assert ok) | - | FAILED | FAILED |
| e10_async_rebind | (assert ok) | - | REFUSED  | REFUSED  |
| e11_property_noreturn_exempt | (assert ok) | - | REFUSED  | REFUSED  |
| e12_import_call_noreturn | (assert ok) | - | REFUSED  | FAILED |
| e13_qualified_noreturn_lib_exempt | (assert ok) | - | FAILED | FAILED |
| e14_qualified_noreturn_call_local_vacuous | (assert ok) | - | REFUSED  | FAILED |
| f01_pkg_two_submodules | 3 | - | REFUSED  | FAILED |
| f02_pkg_from_submodules | 3 | - | REFUSED PYCSL-R325-OPAQUE-INT-FALLBACK | REFUSED PYCSL-R325-OPAQUE-INT-FALLBACK |
| f03_pkg_alias_submodules | 3 | - | REFUSED  | FAILED |
| f04_pkg_one_submodule_local_def | 1 | - | REFUSED  | FAILED |
| g01_star_then_local_def_true | 2 | - | REFUSED  | SUCCESS |
| g02_local_def_then_star_false | 1 | - | REFUSED  | REFUSED  |
| g03_star_beside_other_lib_qualified | 2 | - | SUCCESS | SUCCESS |
| h01_same_alias_two_modules | 2 | - | REFUSED  | REFUSED  |
| h02_same_alias_reexport | 2 | - | REFUSED  | REFUSED  |
| i01_upper_qualified_local_lower | 1 | - | REFUSED PYCSL-R327-IDENT-COLLISION | REFUSED PYCSL-SEM-WHYML-NAME-CLASH |
| j01_deep_reexport_plus_qualified_true | 2 | - | SUCCESS | SUCCESS |
| k02_class_and_helper_same_lib_true | 2 | - | FAILED | FAILED |
| k03_class_and_qualified_helper_true | 2 | - | FAILED | FAILED |
| m01_method_named_like_lib_fn | 3 | - | FAILED | FAILED |
| n01_lib_def_then_import_qualified | 2 | - | REFUSED  | REFUSED  |
| n02_lib_def_then_import_from | 2 | - | REFUSED  | REFUSED  |
| n03_lib_def_then_star_qualified | 2 | - | REFUSED  | REFUSED  |
| o01_qualified_ctor_two_libs | 21 | - | FAILED | REFUSED PYCSL-R325-OPAQUE-INT-FALLBACK |
| p01_lib_private_helper_vs_local_true | 6 | - | REFUSED  | SUCCESS |
| p02_two_libs_private_helpers_true | 3 | - | REFUSED  | SUCCESS |
| p03_two_libs_private_helpers_from_true | 3 | - | REFUSED  | SUCCESS |
| p04_lib_private_helper_vs_local_from_true | 6 | - | REFUSED  | SUCCESS |
| q01_module_name_rebound | 2 | - | REFUSED  | REFUSED  |
| q02_module_attr_monkeypatch | 2 | - | REFUSED  | REFUSED  |
| q03_dep_monkeypatches_other | 2 | - | REFUSED  | REFUSED  |
| q04_from_import_monkeypatched | 2 | - | REFUSED  | REFUSED  |
| qa70 | ? | - | SUCCESS | SUCCESS |
| qb70 | ? | - | SUCCESS | SUCCESS |
| qc72 | ? | - | SUCCESS | SUCCESS |
| qd72 | ? | - | SUCCESS | SUCCESS |
| qe72 | ? | - | SUCCESS | SUCCESS |
| qf72 | ? | - | SUCCESS | SUCCESS |
| qg72 | ? | - | SUCCESS | SUCCESS |
| qh72 | ? | - | SUCCESS | SUCCESS |
| qi72 | ? | - | SUCCESS | SUCCESS |
| qj72 | ? | - | SUCCESS | SUCCESS |
| qk72 | ? | - | SUCCESS | SUCCESS |
| v01_mutrec3_third_vacuous | (assert ok) | - | FAILED | FAILED |
| v01f_mutrec3_vac_f | (assert ok) | - | FAILED | FAILED |
| v01g_mutrec3_vac_g | (assert ok) | - | FAILED | FAILED |
| v02_mutrec3_third_vacuous_prog | (assert ok) | - | FAILED | FAILED |
| v02f_mutrec3_prog_vac_f | (assert ok) | - | FAILED | FAILED |
| v03_mutrec_two_classes | (assert ok) | - | REFUSED  | REFUSED  |
| v04_mutrec_nested | (assert ok) | - | FAILED | FAILED |
| v04b_mutrec_nested_with_vac | (assert ok) | - | SUCCESS | FAILED |
| v05_mutrec_lemma | (assert ok) | - | FAILED | FAILED |
| v06_mutrec_mixed_prog_first | (assert ok) | - | FAILED | FAILED |
| v06b_mutrec_mixed_with_prog_vac | (assert ok) | - | FAILED | FAILED |
| v07_mutrec_three_way_first_logic | (assert ok) | - | FAILED | FAILED |
| v07a_mutrec3_vac_a | (assert ok) | - | FAILED | FAILED |
| v07b_mutrec3_vac_b | (assert ok) | - | FAILED | FAILED |
| w01_conditional_def | 1 | - | REFUSED  | REFUSED  |
| w02_try_def | 1 | - | REFUSED  | REFUSED  |
| w03_method_vs_nested_in_method | 1 | - | REFUSED  | REFUSED  |
| w04_trusted_parent_lift | 1 | - | FAILED | FAILED |
| w05_py_constant | 1 | - | REFUSED PYCSL-R327-IDENT-COLLISION | REFUSED PYCSL-SEM-WHYML-NAME-CLASH |
| w06_multifile_mangled | 1 | - | SUCCESS | REFUSED  |
| w07_classes_C_c | 1 | - | REFUSED PYCSL-R327-IDENT-COLLISION | REFUSED PYCSL-SEM-WHYML-NAME-CLASH |
| w08_unicode | 1 | - | REFUSED PYCSL-R327-IDENT-COLLISION | REFUSED PYCSL-SEM-WHYML-NAME-CLASH |
| w09_rebind_ctl | 2 | - | REFUSED  | REFUSED  |
| w10_class_rebind | 2 | - | FAILED | FAILED |
| w11_multifile_helper_shadow | 1 | - | REFUSED  | FAILED |
| w11b_multifile_helper_shadow | 1 | - | REFUSED  | FAILED |
| w12_property_setter | 1 | - | REFUSED  | REFUSED  |
| w13_nested_class_same_name | 1 | - | REFUSED  | REFUSED  |
| w14_module_qualified_call_local_shadow | 1 | - | REFUSED  | FAILED |
| w14b_alias_qualified_call_local_shadow | 1 | - | REFUSED  | FAILED |
| w14c_module_qualified_call_ctl | 1 | - | SUCCESS | SUCCESS |
| w15_trusted_parent_nested_upper_ctl | 1 2 | - | REFUSED PYCSL-R327-IDENT-COLLISION | REFUSED PYCSL-SEM-WHYML-NAME-CLASH |
| w16_trusted_parent_nested_py_constant_ctl | 1 2 | - | REFUSED PYCSL-R327-IDENT-COLLISION | REFUSED PYCSL-SEM-WHYML-NAME-CLASH |
| w17_from_import_alias_local_shadow | 1 | - | FAILED | FAILED |
| w18_method_named_like_imported | 1 | - | FAILED | FAILED |
| w19_two_libs_same_function_name | 3 | - | REFUSED  | FAILED |
| w19c_two_libs_ctl | 3 | - | REFUSED  | SUCCESS |
| x01_class_contract_helper_noclash | 1 | - | FAILED | FAILED |
| x02_direct_reexport_vs_qualified_other | 3 | - | SUCCESS | FAILED |
| x03_lib_shadows_builtin_abs | 10 | - | SUCCESS | FAILED |
| x04_bare_and_attribute_same_class_true | 11 | - | SUCCESS | SUCCESS |
| x05_star_bare_base_vs_module_import | 1 | - | SUCCESS | REFUSED  |
| x06_assign_bare_base_true | 2 | - | REFUSED  | REFUSED  |
| x07_qualified_ctor_with_from_import_same_class_true | 1 | - | SUCCESS | SUCCESS |
| x08_star_reexport_vs_qualified_other | 3 | - | SUCCESS | FAILED |
| x09_base_class_inlined_method_local_helper | 1 | - | SUCCESS | FAILED |
