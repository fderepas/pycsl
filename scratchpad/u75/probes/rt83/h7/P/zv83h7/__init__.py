def _ga(name):
    if name == "_" + "_all__":
        return ["w"]
    raise AttributeError(name)


globals().update(__getattr__=_ga)
