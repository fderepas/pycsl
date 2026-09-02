import sys, os, json, runpy
sys.path.insert(0,'/home/fabrice/git/pycsl/src/pycsl')
os.environ['PYTHONHASHSEED']='0'
import Module6_WhyMLTranspiler as M
T=M.Module6_WhyMLTranspiler
_o=T._build_callee_no_exception_summary
def patched(self, functions):
    _o(self, functions)
    ks=[k for k in self._module_func_raises if 'csl_to_ir' in k]
    print("REGISTRY KEYS with csl_to_ir:", ks, [self._module_func_raises[k] for k in ks], flush=True)
    for f in functions:
        if str(f.get('name','')).endswith('csl_valid2d'):
            print("csl_valid2d name:", f.get('name'), flush=True)
            print("csl_valid2d body:", json.dumps(f.get('body'))[:800], flush=True)
T._build_callee_no_exception_summary=patched
sys.argv=['pycsl.py','src/self-annotate/src/frontend/Module5_IREmitter.py','--import-path','src/pycsl','--no-proof']
runpy.run_path('/home/fabrice/git/pycsl/src/pycsl/pycsl.py', run_name='__main__')
