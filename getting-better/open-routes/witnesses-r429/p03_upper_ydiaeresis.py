#@ ensures \result < 256
def f(s: str) -> int:
    return ord(s.upper()[0])


if __name__ == "__main__":
    try:
        r = f('\u00ff')
        if not (r < 256):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
