"""Test 0291 — Four-limb carry normalization kernel"""
# pycsl-flags: --no-proof
_ = 0  # anchor

BASE = 10


#@ requires 0 <= i and i <= 4
#@ ensures \result >= 1
#@ assigns \nothing
def weight(i: int) -> int:
    if i == 0:
        return 1
    if i == 1:
        return BASE
    if i == 2:
        return BASE * BASE
    if i == 3:
        return BASE * BASE * BASE
    return BASE * BASE * BASE * BASE


#@ requires \length(arr) >= 4
#@ assigns \nothing
def value4(arr: list) -> int:
    return (
        arr[0]
        + BASE * arr[1]
        + BASE * BASE * arr[2]
        + BASE * BASE * BASE * arr[3]
    )


#@ requires \length(arr) >= 4
#@ requires \forall k; 0 <= k and k < 4 ==> 0 <= arr[k] and arr[k] <= 18
#@ ensures 0 <= \result and \result <= 1
#@ ensures \forall k; 0 <= k and k < 4 ==> 0 <= arr[k] and arr[k] < BASE
#@ ensures \forall k; 4 <= k and k < \length(arr) ==> arr[k] == \old(arr[k])
#@ ensures value4(arr) + weight(4) * \result == \old(value4(arr))
#@ assigns arr[0..4]
def carry_normalize4(arr: list) -> int:
    i = 0
    carry = 0
    #@ loop invariant 0 <= i and i <= 4
    #@ loop invariant 0 <= carry and carry <= 1
    #@ loop invariant \forall k; 0 <= k and k < i ==> 0 <= arr[k] and arr[k] < BASE
    #@ loop invariant \forall k; i <= k and k < 4 ==> 0 <= arr[k] and arr[k] <= 18
    #@ loop invariant \forall k; 4 <= k and k < \length(arr) ==> arr[k] == \old(arr[k])
    #@ loop invariant value4(arr) + weight(i) * carry == \old(value4(arr))
    #@ loop variant 4 - i
    while i < 4:
        t = arr[i] + carry
        if t >= BASE:
            arr[i] = t - BASE
            carry = 1
        else:
            arr[i] = t
            carry = 0
        i = i + 1
    return carry


if __name__ == "__main__":
    a = [15, 18, 3, 9]
    old_a = value4(a)
    carry_a = carry_normalize4(a)
    assert a == [5, 9, 4, 9]
    assert 0 <= carry_a <= 1
    assert value4(a) + weight(4) * carry_a == old_a

    b = [18, 18, 18, 18]
    old_b = value4(b)
    carry_b = carry_normalize4(b)
    assert b == [8, 9, 9, 9]
    assert carry_b == 1
    assert value4(b) + weight(4) * carry_b == old_b

    print("PASS")
