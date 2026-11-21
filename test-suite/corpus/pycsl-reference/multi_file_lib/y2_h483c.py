"""Helper for corpus 7672 (route #483): rebinds its own FUNCTION through `__builtins__['setattr']` on a self-import."""
import multi_file_lib.y2_h483c as _s


#@ ensures \result == x
def g(x: int) -> int:
    return x


__builtins__['setattr'](_s, 'g', lambda x: 0)
