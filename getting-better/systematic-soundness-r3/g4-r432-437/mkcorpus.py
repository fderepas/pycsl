import os, re, sys
G=sys.argv[1]; OUT=sys.argv[2]
W=G+'/w/'; C=G+'/c/'
plan = [
 # id, src, route, kind, slug, note, driver-call
 (6500,W+'on00_strip.py',432,'W','r432_optional_str_strip','`x: Optional[str]; len(x.strip())`'),
 (6501,W+'on05_method.py',432,'W','r432_optional_user_method','a user method on `Optional[C]`'),
 (6502,W+'on07_dict_get.py',432,'W','r432_optional_dict_get','`.get` on `Optional[Dict[str, int]]`'),
 (6503,W+'on09_int_bitlen.py',432,'W','r432_optional_int_bit_length','`.bit_length()` on `Optional[int]`'),
 (6504,W+'on10_upper_ens.py',432,'W','r432_optional_upper_unused','`y = x.upper()` (value unused) on `Optional[str]`'),
 (6505,W+'on11_union_int_str_upper.py',432,'W','r432_union_int_str_upper','`.upper()` on `Union[int, str]`'),
 (6506,W+'on13_pipe_none.py',432,'W','r432_pep604_str_none_lower','`.lower()` on `str | None`'),
 (6507,W+'op16_upper_opt.py',432,'W','r432_optional_second_param_upper','`.upper()` on a second `Optional[str]` parameter'),
 (6508,W+'w35_local_get.py',432,'W','r432_local_from_dict_get','`v = d.get("a"); v.strip()` (a local derived Optional; g4 probe)'),
 (6509,W+'w30_default_none_param.py',432,'W','r432_param_default_none','`x: str = None; x.strip()` (g4 probe)'),
 (6510,W+'w31_field_chain.py',432,'W','r432_optional_field_chain','`n.next.v` with `next: Optional[Node]` (g4 probe)'),
 (6511,W+'w32_rebind_after_guard.py',432,'W','r432_rebind_after_guard','a rebinding `x = y` after the `is None` early return (g4 probe)'),
 (6512,W+'w33_loop_rebind.py',432,'W','r432_loop_rebind_after_use','a guard outside a loop whose body rebinds the receiver after the use (g4 probe)'),
 (6513,W+'w34_call_between.py',432,'W','r432_call_between_guard_and_use','a call between an attribute-path guard and the use (g4 probe)'),
 (6514,W+'w38_or_guard_wrong.py',432,'W','r432_or_guard_does_not_narrow','`if x is not None or y:` (a disjunction does not narrow; g4 probe)'),
 (6548,W+'w37_isinstance_object.py',432,'W','r432_isinstance_object_does_not_narrow','`isinstance(x, object)` (it does not exclude `None`; g4 probe)'),
 (6549,W+'w41_genexp_deferred.py',432,'W','r432_generator_expression_runs_later','a generator expression built under `if x is not None:` and consumed after `x = None` (g4 probe)'),
 (6515,C+'c01_guard_notnone.py',432,'C','r432_ctl_if_not_none','`if x is not None:` narrows'),
 (6516,C+'c02_early_return.py',432,'C','r432_ctl_early_return','`if x is None: return 0` narrows what follows'),
 (6517,C+'c03_isinstance.py',432,'C','r432_ctl_isinstance','`isinstance(x, str)` narrows a `Union[int, str]`'),
 (6518,C+'c04_opt_class.py',432,'C','r432_ctl_optional_user_class_guard','a guarded user method on `Optional[C]`'),
 (6519,C+'c07_assert.py',432,'C','r432_ctl_assert_not_none','`assert x is not None` narrows'),
 (6520,C+'c08_ifexp.py',432,'C','r432_ctl_ifexp_guard','`x.strip() if x is not None else ..` narrows'),
 (6521,C+'c13_local_opt_guard.py',432,'C','r432_ctl_local_get_guard','a guarded local from `d.get`'),
 (6522,C+'c27_assign_chain.py',432,'C','r432_ctl_assign_derived_str','a local rebound from a narrowed receiver\'s method'),
 (6523,C+'c28_loop_guard.py',432,'C','r432_ctl_loop_continue_guard','`if x is None: continue` inside a loop'),
 (6524,C+'c06_noclaim.py',432,'C','r432_ctl_unclaimed','the same access without a `no_exception` claim'),
 (6525,W+'jj00_join_tuple_opt.py',433,'W','r433_join_tuple_with_optional','`"".join(t)`, `t: Tuple[str, Optional[str]]`'),
 (6526,W+'jj01_join_dict_vals_opt.py',433,'W','r433_join_dict_values_optional','`" ".join(d.values())` over `Optional[str]` values'),
 (6527,W+'jj02_join_union.py',433,'W','r433_join_union_str_int','`"".join(xs)`, `xs: List[Union[str, int]]`'),
 (6528,W+'jj03_join_bytes_opt.py',433,'W','r433_bytes_join_optional','`b"".join(xs)`, `xs: List[Optional[bytes]]`'),
 (6529,W+'jj04_join_any.py',433,'W','r433_join_any','`"".join(xs)`, `xs: List[Any]`'),
 (6530,W+'jj05_join_list_int.py',433,'W','r433_join_list_int','`"".join(xs)`, `xs: List[int]`'),
 (6531,W+'jj06_join_opt_loop.py',433,'W','r433_join_optional_display_in_loop','`",".join([x])` with `x` an `Optional[str]` loop element'),
 (6532,W+'jj10_join_bytes_into_str.py',433,'W','r433_str_join_bytes','`"".join(xs)`, `xs: List[bytes]`'),
 (6533,W+'oo01_join_opt.py',433,'W','r433_join_list_optional_str','`",".join(xs)`, `xs: List[Optional[str]]`'),
 (6534,C+'c41_join_bytes.py',433,'C','r433_ctl_bytes_join_bytes','`b"-".join(xs)`, `xs: List[bytes]`'),
 (6535,C+'c46_join_noclaim.py',433,'C','r433_ctl_unclaimed','a join over `List[int]` without a `no_exception` claim'),
 (6536,W+'oo12_sorted_tuple_str_opt.py',437,'W','r437_sorted_tuple_str_optional','`sorted(xs)`, `xs: List[Tuple[str, Optional[int]]]`'),
 (6537,W+'x04_sorted_optional.py',437,'W','r437_sorted_optional_int','`sorted(xs)`, `xs: List[Optional[int]]`'),
 (6538,W+'x05_sorted_tuple_dict.py',437,'W','r437_sorted_tuple_int_dict','`sorted(xs)`, `xs: List[Tuple[int, Dict[str, int]]]`'),
 (6539,W+'z03_sorted_tuple_obj.py',437,'W','r437_sorted_tuple_user_class','`sorted(xs)` over tuples ending in a user class without `__lt__`'),
 (6540,W+'z04_sorted_tuple_opt.py',437,'W','r437_sorted_tuple_int_optional','`sorted(xs)`, `xs: List[Tuple[int, Optional[int]]]`'),
 (6541,W+'z06_sorted_tuple_str_dict.py',437,'W','r437_sorted_tuple_str_dict','`sorted(xs)`, `xs: List[Tuple[str, Dict[str, int]]]`'),
 (6542,W+'z07_sorted_opt_str.py',437,'W','r437_sorted_optional_str','`sorted(xs)`, `xs: List[Optional[str]]`'),
 (6543,W+'z09_sorted_tuple_list_dict.py',437,'W','r437_sorted_tuple_list_of_dict','`sorted(xs)`, `xs: List[Tuple[int, List[Dict[str, int]]]]`'),
 (6544,W+'z12_sorted_tuple_dict_rev.py',437,'W','r437_sorted_reverse_tuple_dict','`sorted(xs, reverse=True)` over tuples ending in a dict'),
 (6545,W+'z14_sorted_list_opt.py',437,'W','r437_sorted_list_of_optional_lists','`sorted(xs)`, `xs: List[List[Optional[int]]]`'),
 (6546,C+'c48_sorted_int.py',437,'C','r437_ctl_sorted_int_minmax','`sorted(List[int])`, `max(a, b)` / `min(a, b)` over ints'),
 (6547,C+'c49_sorted_noclaim.py',437,'C','r437_ctl_unclaimed_typeerror','`sorted(List[Optional[int]])` under a claim that does not cover TypeError'),
]
exc={432:'AttributeError',433:'TypeError',437:'TypeError'}
code={432:'PYCSL-R432-OPTIONAL-RECEIVER-ATTRIBUTE',433:'PYCSL-R433-JOIN-ELEMENT-CLASS',437:'PYCSL-R437-UNORDERED-ELEMENTS'}
for i,src,r,k,slug,note in plan:
    body=open(src).read()
    if k=='W':
        if src.startswith(G+'/w/') and os.path.basename(src)[:3] in ('w30','w31','w32','w33','w34','w35'):
            pass
        doc=(f'r"""Test {i} -- route #{r} (expected FAIL): {note} under `#@ no_exception \\all`. '
             f'PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises {exc[r]} (the `__main__` '
             f'driver prints VIOLATION). Now REFUSED ({code[r]}).\n"""\n# pycsl-expected: FAIL\n')
    else:
        doc=(f'r"""Test {i} -- route #{r} (expected PASS): CONTROL: {note} is admitted. '
             f'PROVED at base and candidate.\n"""\n# pycsl-expected: PASS\n')
    open(f'{OUT}/{i}_{slug}.py','w').write(doc+body)
    print(i, slug)
