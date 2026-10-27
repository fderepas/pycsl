# OPEN ROUTE #421 — A MODULE-GLOBAL / CLASS-BODY INITIALIZER IS TYPED BY A NARROWER DERIVATION THAN A LOCAL: ANYTHING NOT LISTED IS #UND, ADMITTED
**Status: OPEN, Severity 1.** Red-team round 33 (2026-10-27, convergence measurement after the run #3 allow-list repairs; 653 screened / 385 fully proved / 116 confirmed); driver-reproduced on main (see `scratchpad/rt33/driver-repro.txt`).
Witnesses `witnesses-r421/` (55): `b00_slice_list.py`, `b01_memview_bytearray.py`, `b02_mappingproxy.py`, `b03_simplenamespace.py`, `b04_deque.py`, `b05_ordereddict.py`, `b06_counter.py`, `b07_defaultdict.py`, `b08_array.py`, `b09_decimal_snan.py`, `b10_argparse_ns.py`, `b11_bytearray_call.py`, `b12_getenv_default.py`, `b13_next_iter.py`, `b14_max_list.py`, `b15_min_key.py`, `b17_unpack_star.py`, `b18_unpack_list_target.py`, `b20_globals_sub.py`, `b21_dict_fromkeys.py`, `b22_str_split_unbound.py`, `b23_str_method.py`, `b24_bytes_split.py`, `b26_vars_mod.py`, `b27_dir_call.py`, `b33_enum_value.py`, `b41_json_loads.py`, `b42_re_findall.py`, `b43_re_split.py`, `b44_shlex_split_alias.py`, `b45_os_listdir.py`, `b46_glob_glob.py`, `b49_functools_reduce.py`, `b52_copy_copy_list.py`, `b54_class_attr_list_via_inst.py`, `b55_staticmethod_call.py`, `b56_func_result.py`, `b60_walrus_global.py`, `b68_chain_assign.py`, `b69_tuple_assign.py`, `b70_del_rebind.py`, `b71_if_module.py`, `b72_try_module.py`, `h00_cb_func_result.py`, `h01_cb_deque.py`, `h02_cb_json.py`, `h03_cb_chain.py`, `h04_cb_walrus.py`, `h05_cb_unpack.py`, `h06_cb_bytearray.py`, `h07_cb_via_self.py`, `h08_cb_str_split.py`, `h09_cb_if.py`, `h16_glob_tuple_component.py`, `h19_glob_dict_get.py`.

```
#421 A MODULE-GLOBAL / CLASS-BODY INITIALIZER IS TYPED BY A NARROWER DERIVATION THAN A LOCAL: ANYTHING NOT LISTED IS #UND, ADMITTED
     [slips past §7.64 (1)-(4) / §7.83 (2): 42; the documented §7.46/§7.47 #UND residual: 13]   (55 probes)
  Template: `K = <init>` at module level, then `#@ no_exception \all  def f(): s = {K}` (or `{C.K}` for a class body) PROVED,
  CPython TypeError (unhashable) / ValueError. The SAME initializer bound to a LOCAL is refused (c10-c51 control screen:
  json.loads, re.findall, os.listdir, copy.copy([1]), deque(), slice, memoryview, walrus, chained assign, starred unpack,
  file-function `-> list` result: all PYCSL-R349 / not-a-function refusals in a function body).
  (a) slips past an explicit rule of §7.64 / §7.83:
    stdlib FUNCTION results (§7.83 (2) says UNKNOWN unless listed): b41 json.loads  b42 re.findall  b43 re.split
      b44 `from shlex import split as sp; sp("a b")` (the round-32 witness, via a global)  b45 os.listdir  b46 glob.glob
      b49 functools.reduce  b12 os.getenv(.., [1])  h02 class body json.loads
    copy (§7.64 (4): copy.copy(x) has x's class): b52 copy.copy(A) for A = [1]
    stdlib objects by CALL (§7.64 (3) classifies names only): b02 types.MappingProxyType({})  b03 types.SimpleNamespace()
      b04 collections.deque()  b05 OrderedDict()  b06 Counter()  b07 defaultdict(int)  b08 array.array('i')
      b09 decimal.Decimal('sNaN') (hash raises)  b10 argparse.Namespace()  h01 class-body deque()
    builtin containers / latent witnesses 5377-5385 re-reached through a global: b00 slice([1], 2)  b01 memoryview(bytearray)
      b11 bytearray(2)  h06 class-body bytearray(1)  h07 the same read as `self.K` in a method
    bindings (§7.64 (2): "a global's bindings are its store-context names"): b68 `K = A = [1]`  b69 `K, A = [1], 2`
      b17 `K, = ([1],)`  b18 `[K] = [[1]]`  b60 `(K := [1])`  b70 `K = 1; del K; K = [1]`  b71 if/else  b72 try/except
      h03 / h04 / h05 / h09 the same in a class body
    container methods (§7.64 (1): a method call over a container is UNKNOWN): b23 'a b'.split()  b24 b'a b'.split()
      b22 str.split('a b')  b21 dict.fromkeys('ab')  h08 class-body 'a b'.split()
  (b) documented #UND residual (an unknown callee / un-annotated / builtin not on the derivation's list), each with a KNOWN
      class: b56 a FILE function `-> list` (its return type IS read for a local, c01 refused)  h00 the same in a class body
      b55 a staticmethod `-> list`  b54 `C().L`  b13 next(iter(A))  b14 max(A)  b15 min(A, key=len)  b20 globals()['A']
      b26 vars(os)  b27 dir()  b33 Enum member .value  h16 `{(1, K)}` (tuple component)  h19 `d.get(K, 0)` (dict lookup)
  WhyML: the set lowers to `any int`; the hashing check finds no class for K and admits it.
  REPAIR: type a module-global / class-body initializer with the SAME `_ty383` derivation the function bodies use (module
  function returns, §7.83's stdlib list, builtins, method results, bindings), and make a global / class name with more than one
  binding, or a binding other than a single-target Assign, the UNION of its bindings (UNKNOWN when any is underivable). Then
  refuse #UND for a MODULE / CLASS name in a hashing position (it is not a mirror `Dict[str, Any]` local, so the 27-mirror cost
  measured for §7.47 does not apply -- re-measure).
```
