_T = dict([("_" + "_all__", ["w"])])


def __getattr__(name):
    if name in _T:
        return _T[name]
    raise AttributeError(name)
