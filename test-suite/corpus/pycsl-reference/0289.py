"""Test 0289 — Compact TLV/DER header parser kernel"""
# pycsl-flags: --no-proof
_ = 0  # anchor

#@ requires 0 <= n and n <= \length(buf)
#@ requires 0 <= pos and pos <= n
#@ ensures \result[0] == 0 ==> \result[1] == buf[pos]
#@ ensures \result[0] == 0 ==> \result[3] > pos
#@ ensures \result[0] == 0 ==> \result[3] <= n
#@ ensures \result[0] != 0 ==> \result[1] == 0 and \result[2] == 0 and \result[3] == pos
#@ assigns \nothing
def parse_tlv_header(buf: list, n: int, pos: int) -> tuple:
    if pos + 2 > n:
        return (-1, 0, 0, pos)

    tag = buf[pos]
    length_octet = buf[pos + 1]

    if length_octet < 128:
        return (0, tag, length_octet, pos + 2)

    width = length_octet - 128
    if width == 0 or width > 4:
        return (-1, 0, 0, pos)
    if pos + 2 + width > n:
        return (-1, 0, 0, pos)

    length = 0
    i = 0
    #@ loop invariant 0 <= i and i <= width
    #@ loop invariant 0 <= length
    #@ loop invariant pos + 2 + i <= n
    #@ loop variant width - i
    while i < width:
        length = length * 256 + buf[pos + 2 + i]
        i = i + 1

    return (0, tag, length, pos + 2 + width)


if __name__ == "__main__":
    ok1 = [0x30, 0x03, 0x01, 0x02, 0x03]
    r1 = parse_tlv_header(ok1, len(ok1), 0)
    assert r1 == (0, 0x30, 3, 2)
    assert ok1 == [0x30, 0x03, 0x01, 0x02, 0x03]

    ok2 = [0x04, 0x82, 0x01, 0x00, 0xAA, 0xBB]
    r2 = parse_tlv_header(ok2, len(ok2), 0)
    assert r2 == (0, 0x04, 256, 4)
    assert ok2 == [0x04, 0x82, 0x01, 0x00, 0xAA, 0xBB]

    bad1 = [0x30]
    assert parse_tlv_header(bad1, len(bad1), 0) == (-1, 0, 0, 0)

    bad2 = [0x30, 0x82, 0x01]
    assert parse_tlv_header(bad2, len(bad2), 0) == (-1, 0, 0, 0)

    print("PASS")
