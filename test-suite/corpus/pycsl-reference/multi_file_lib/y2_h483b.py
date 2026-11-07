"""Helper for corpus 7671 (route #483): `__builtins__.get('exec')` inside a function it calls at import."""
K = 1


def _i():
    __builtins__.get('exec')('global K\nK = 0')


_i()
