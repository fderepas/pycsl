import sys
sys.path.insert(0,'/usr/lib/python3.13')
import json
d=json.load(open('scratchpad/allir.json'))
FUN={f['name']:f for f in d['functions']}

def collect(node, strs, calls):
    if isinstance(node, dict):
        if node.get('type')=='String' and 'value' in node:
            strs.append(node['value'])
        if node.get('type')=='Call' and isinstance(node.get('func'),str):
            calls.append(node['func'])
        for v in node.values(): collect(v, strs, calls)
    elif isinstance(node, list):
        for x in node: collect(x, strs, calls)
    return strs, calls

EXPECT = {
 '_union_c8_walk': (
   {"stmt","If","While","For","Match","test","body","orelse","cases"},
   {"_union_c8_walk","_union_c8_test_references_union_var","_union_c8_recognized_guard","_union_c11_check_dead_arms","isinstance","warnings.warn"}),
 '_union_c8_test_references_union_var': (
   {"type","Var","name"},
   {"_union_c8_test_references_union_var","isinstance","any","test.values","test.get"}),
 '_union_c8_recognized_guard': (
   {"type","BinOp","==","!=","None","Var","String","op","left","right","in","not in","Tuple","ArrayLit","SetLit","Call","func","args","elts","isinstance"},
   {"isinstance","any","all"}),
 '_union_c11_check_dead_arms': (
   {"cases","pattern","ctor"},
   {"warnings.warn"}),
}
for name,(es,ec) in EXPECT.items():
    f=FUN.get(name)
    if not f: print(name,"MISSING"); continue
    strs,calls=collect(f['body'],[],[])
    S=set(strs); C=set(calls)
    miss_s=es-S; miss_c=ec-C
    print(name, "params",f.get('formal_params'),"ret",f.get('return_annotation'))
    print("   str_miss", miss_s, "| call_miss", miss_c)
