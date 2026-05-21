"""Test 0290 — PNG chunk-sequence state machine"""
# pycsl-flags: --no-proof
_ = 0  # anchor

K_IHDR = 0
K_PLTE = 1
K_IDAT = 2
K_IEND = 3


#@ requires 0 <= state and state <= 3
#@ requires 0 <= kind and kind <= 3
#@ ensures \result == -1 or (0 <= \result and \result <= 3)
#@ assigns \nothing
def next_png_state(state: int, kind: int) -> int:
    if state == 0:
        if kind == K_IHDR:
            return 1
        return -1
    if state == 1:
        if kind == K_PLTE:
            return 1
        if kind == K_IDAT:
            return 2
        if kind == K_IEND:
            return 3
        return -1
    if state == 2:
        if kind == K_IDAT:
            return 2
        if kind == K_IEND:
            return 3
        return -1
    if kind == K_IEND:
        return -1
    return -1


#@ requires n >= 0
#@ requires \length(kinds) >= n
#@ requires \forall i; 0 <= i and i < n ==> 0 <= kinds[i] and kinds[i] <= 3
#@ ensures \result == 0 or \result == 1
#@ ensures \result == 0 ==> n > 0
#@ ensures \result == 0 ==> kinds[0] == K_IHDR
#@ ensures \result == 0 ==> kinds[n - 1] == K_IEND
#@ assigns \nothing
def png_chunk_sequence_status(kinds: list, n: int) -> int:
    state = 0
    ended = 0
    status = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant 0 <= state and state <= 3
    #@ loop invariant 0 <= ended and ended <= 1
    #@ loop invariant 0 <= status and status <= 1
    #@ loop invariant ended == 1 ==> state == 3
    #@ loop invariant (status == 0 and i > 0) ==> kinds[0] == K_IHDR
    #@ loop variant n - i
    while i < n:
        kind = kinds[i]
        if status == 0:
            if ended == 1:
                status = 1
            else:
                next_state = next_png_state(state, kind)
                if next_state < 0:
                    status = 1
                else:
                    state = next_state
                    if next_state == 3:
                        ended = 1
        i = i + 1
    if status == 0 and state == 3 and ended == 1:
        return 0
    return 1


if __name__ == "__main__":
    ok = [K_IHDR, K_PLTE, K_IDAT, K_IDAT, K_IEND]
    bad_1 = [K_PLTE, K_IHDR, K_IEND]
    bad_2 = [K_IHDR, K_IDAT, K_IEND, K_PLTE]
    assert png_chunk_sequence_status(ok, len(ok)) == 0
    assert png_chunk_sequence_status(bad_1, len(bad_1)) == 1
    assert png_chunk_sequence_status(bad_2, len(bad_2)) == 1
    print("PASS")
