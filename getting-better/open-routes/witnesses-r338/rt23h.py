import sys
def check(rows):
    bad = 0
    for name, fn, args, expect in rows:
        try:
            r = fn(*args); held = (r == expect)
        except Exception as e:
            r = type(e).__name__; held = False
        print(name, r, "HELD" if held else "VIOLATED")
        bad += 0 if held else 1
    sys.exit(1 if bad else 0)
