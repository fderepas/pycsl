"""Helper for corpus 7677 (route #484): a PEER that rebinds y2_h484g.g inside a function it calls at import."""


def _patch() -> None:
    import multi_file_lib.y2_h484g as h
    h.g = lambda x: 0


_patch()
