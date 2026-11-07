import sys, os, runpy
sys.path.insert(0,'/home/fabrice/git/pycsl/src/pycsl')
os.environ['PYTHONHASHSEED']='0'
import module6_whyml.expressions as E
M=E.ExpressionEmissionMixin
_o=M._disp_state_independent
def patched(self, disp):
    cls = getattr(self, "_current_self_type", None)
    mw = getattr(self, "_module_method_writes", {}) or {}
    funcs=[f for f in (self.ir.get("functions") or []) if f.get("kind")=="method" and f.get("self_type")==cls]
    def _res(nm0):
        for f in funcs:
            nm=str(f.get("name",""))
            if nm==nm0 or nm.endswith("_"+nm0) or nm.endswith(nm0): return f
        return None
    d=_res(disp)
    r=_o(self,disp)
    info=''
    if d is None: info='NO DISPF'
    else:
        if mw.get(str(d.get('name',''))): info='DISP WRITES'
        else:
            try: rec=self._recognize_pyx_dispatcher(d)
            except Exception as e: rec=None; info='REC EXC %s'%e
            if rec is None: info=info or 'REC NONE'
            else:
                bad=[]
                for e2 in rec[2]:
                    hf=_res(e2[-1])
                    if hf is None: bad.append((e2[-1],'unresolved'))
                    elif mw.get(str(hf.get('name',''))): bad.append((e2[-1],mw[str(hf.get('name',''))]))
                info='OK' if not bad else 'BAD %s'%bad[:4]
    print("GATE disp=%-20s cls=%-25s -> %s   (%s)" % (disp, cls, r, info), flush=True)
    return r
M._disp_state_independent=patched
sys.argv=['pycsl.py','src/self-annotate/src/frontend/Module5_IREmitter.py','--import-path','src/pycsl','--no-proof']
runpy.run_path('/home/fabrice/git/pycsl/src/pycsl/pycsl.py', run_name='__main__')
