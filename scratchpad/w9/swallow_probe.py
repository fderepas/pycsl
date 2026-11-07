"""Record every exception that is CAUGHT (and not re-raised) inside src/pycsl during one
emission, using sys.monitoring's EXCEPTION_HANDLED event (3.12+). The point is not that
catching is wrong — most of these are recognizers declining — but that a swallow which
FIRES IN NORMAL OPERATION is masking a real error, and the campaign's whole method is that
a silent fallback is where unsound lowerings live."""
import os, sys, collections

ROOT = sys.argv[1]
target = sys.argv[2]
sys.path.insert(0, os.path.join(ROOT, "src", "pycsl"))

TOOL = 5
hits = collections.Counter()
SRC = os.path.join(ROOT, "src", "pycsl")

def on_handled(code, offset, exc):
    fn = code.co_filename
    if not fn.startswith(SRC):
        return
    hits[(os.path.relpath(fn, ROOT), code.co_name, type(exc).__name__)] += 1

mon = sys.monitoring
mon.use_tool_id(TOOL, "swallow-probe")
mon.set_events(TOOL, mon.events.EXCEPTION_HANDLED)
mon.register_callback(TOOL, mon.events.EXCEPTION_HANDLED, on_handled)

sys.argv = ["pycsl.py", target, "--import-path", os.path.join(ROOT, "src", "pycsl"),
            "--no-proof", "--no-typecheck"]
import pycsl
try:
    pycsl.main()
except SystemExit:
    pass
except Exception:
    pass
mon.set_events(TOOL, 0)
mon.free_tool_id(TOOL)
for (f, fn, exc), n in sorted(hits.items(), key=lambda kv: -kv[1]):
    sys.stderr.write("SWALLOW\t%d\t%s\t%s\t%s\n" % (n, f, fn, exc))
