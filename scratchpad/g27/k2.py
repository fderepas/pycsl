r"""K2 — deferral census #2: `_lemma_calls_trusted` matches a BARE name, and a dotted call
emits `"self.helper"`, so a lemma method may call a \trusted method and export its contract."""
_ = 0  # anchor


class C:
    #@ \trusted
    #@ ensures \result == 1 and \result == 2
    #@ assigns \nothing
    def bogus(self) -> int:
        return 1

    #@ lemma
    #@ ensures 1 == 2
    #@ assigns \nothing
    def leak(self) -> None:
        x = self.bogus()
