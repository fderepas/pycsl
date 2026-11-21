def _patch() -> None:
    import h9607
    h9607.g = lambda x: 0
_patch()
