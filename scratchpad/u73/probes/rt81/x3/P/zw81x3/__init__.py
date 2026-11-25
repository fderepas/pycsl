def __getattr__(name):
    if name == "_" + "_all__":
        return ["w"]
    raise AttributeError(name)
