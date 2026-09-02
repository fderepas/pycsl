import sys; sys.path.insert(0,"src/pycsl")
import module6_whyml.expressions as E
orig = E.__dict__.get("ExpressionEmissionMixin")
# monkeypatch _try_emit_refine_str_fold to print
import module6_whyml.expressions as ex
cls = None
for name,obj in vars(ex).items():
    if hasattr(obj,"_try_emit_refine_str_fold"):
        cls=obj; break
print("cls", cls)
