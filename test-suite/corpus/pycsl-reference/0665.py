"""Test 0665 — G0a (09-0702-os-plan): the 18-field inode codec round-trip proves INLINE in minimal context.

`roundtrip(fields) = unpack_inode(pack_inode(fields))` reconstructs all 18 fields (`esult[k]==fields[k]`)
by COMPOSITION of the codec's value contracts — pack ensures `result[off]*...==fields[k]` + 64 byte
bounds; unpack ensures `result[k]==data[off]*...` from the byte bounds. ~42s in this minimal file. The
SAME proof times out >300s inside the full UnixInodeFileSystem module (context inflation), which is why
the plan extracts the codec to its own minimal-context module so the round-trip is provable inline and
the cross-validated `UnixFs.Struct.i18.round_trip` AXIOM can be ELIMINATED (09-0702-os-status §2-B,
09-0702-os-plan G0/G3). Two pass-2 fixes applied: unrolled loops + specific per-byte requires (a
quantified `forall i<64` times out on instantiation)."""
#@ requires 0 <= v and v <= 65535
#@ assigns \nothing
#@ ensures \length(\result) == 2
#@ ensures 0 <= \result[0] and \result[0] <= 255
#@ ensures 0 <= \result[1] and \result[1] <= 255
#@ ensures \result[0]*256 + \result[1] == v
def pack16(v: int) -> list:
    return bytes([v // 256, v % 256])

#@ requires 0 <= v and v <= 4294967295
#@ assigns \nothing
#@ ensures \length(\result) == 4
#@ ensures 0 <= \result[0] and \result[0] <= 255
#@ ensures 0 <= \result[1] and \result[1] <= 255
#@ ensures 0 <= \result[2] and \result[2] <= 255
#@ ensures 0 <= \result[3] and \result[3] <= 255
#@ ensures \result[0]*16777216 + \result[1]*65536 + \result[2]*256 + \result[3] == v
def pack32(v: int) -> list:
    return bytes([v // 16777216, (v // 65536) % 256, (v // 256) % 256, v % 256])

#@ requires \valid(data, offset + 2)
#@ requires offset >= 0
#@ requires 0 <= data[offset] and data[offset] <= 255
#@ requires 0 <= data[offset+1] and data[offset+1] <= 255
#@ assigns \nothing
#@ ensures \result == data[offset]*256 + data[offset+1]
def unpack16(data: list, offset: int) -> int:
    return data[offset]*256 + data[offset+1]

#@ requires \valid(data, offset + 4)
#@ requires offset >= 0
#@ requires 0 <= data[offset+0] and data[offset+0] <= 255
#@ requires 0 <= data[offset+1] and data[offset+1] <= 255
#@ requires 0 <= data[offset+2] and data[offset+2] <= 255
#@ requires 0 <= data[offset+3] and data[offset+3] <= 255
#@ assigns \nothing
#@ ensures \result == data[offset]*16777216 + data[offset+1]*65536 + data[offset+2]*256 + data[offset+3]
def unpack32(data: list, offset: int) -> int:
    return data[offset]*16777216 + data[offset+1]*65536 + data[offset+2]*256 + data[offset+3]

#@ requires \valid(fields, 18)
#@ requires 0 <= fields[0] and fields[0] <= 4294967295
#@ requires 0 <= fields[1] and fields[1] <= 65535
#@ requires 0 <= fields[2] and fields[2] <= 65535
#@ requires 0 <= fields[3] and fields[3] <= 65535
#@ requires 0 <= fields[4] and fields[4] <= 65535
#@ requires 0 <= fields[5] and fields[5] <= 65535
#@ requires 0 <= fields[6] and fields[6] <= 4294967295
#@ requires 0 <= fields[7] and fields[7] <= 4294967295
#@ requires 0 <= fields[8] and fields[8] <= 4294967295
#@ requires 0 <= fields[9] and fields[9] <= 4294967295
#@ requires 0 <= fields[10] and fields[10] <= 4294967295
#@ requires 0 <= fields[11] and fields[11] <= 4294967295
#@ requires 0 <= fields[12] and fields[12] <= 4294967295
#@ requires 0 <= fields[13] and fields[13] <= 4294967295
#@ requires 0 <= fields[14] and fields[14] <= 4294967295
#@ requires 0 <= fields[15] and fields[15] <= 4294967295
#@ requires 0 <= fields[16] and fields[16] <= 4294967295
#@ requires 0 <= fields[17] and fields[17] <= 4294967295
#@ assigns \nothing
#@ ensures \length(\result) == 64
#@ ensures 0 <= \result[0] and \result[0] <= 255
#@ ensures 0 <= \result[1] and \result[1] <= 255
#@ ensures 0 <= \result[2] and \result[2] <= 255
#@ ensures 0 <= \result[3] and \result[3] <= 255
#@ ensures 0 <= \result[4] and \result[4] <= 255
#@ ensures 0 <= \result[5] and \result[5] <= 255
#@ ensures 0 <= \result[6] and \result[6] <= 255
#@ ensures 0 <= \result[7] and \result[7] <= 255
#@ ensures 0 <= \result[8] and \result[8] <= 255
#@ ensures 0 <= \result[9] and \result[9] <= 255
#@ ensures 0 <= \result[10] and \result[10] <= 255
#@ ensures 0 <= \result[11] and \result[11] <= 255
#@ ensures 0 <= \result[12] and \result[12] <= 255
#@ ensures 0 <= \result[13] and \result[13] <= 255
#@ ensures 0 <= \result[14] and \result[14] <= 255
#@ ensures 0 <= \result[15] and \result[15] <= 255
#@ ensures 0 <= \result[16] and \result[16] <= 255
#@ ensures 0 <= \result[17] and \result[17] <= 255
#@ ensures 0 <= \result[18] and \result[18] <= 255
#@ ensures 0 <= \result[19] and \result[19] <= 255
#@ ensures 0 <= \result[20] and \result[20] <= 255
#@ ensures 0 <= \result[21] and \result[21] <= 255
#@ ensures 0 <= \result[22] and \result[22] <= 255
#@ ensures 0 <= \result[23] and \result[23] <= 255
#@ ensures 0 <= \result[24] and \result[24] <= 255
#@ ensures 0 <= \result[25] and \result[25] <= 255
#@ ensures 0 <= \result[26] and \result[26] <= 255
#@ ensures 0 <= \result[27] and \result[27] <= 255
#@ ensures 0 <= \result[28] and \result[28] <= 255
#@ ensures 0 <= \result[29] and \result[29] <= 255
#@ ensures 0 <= \result[30] and \result[30] <= 255
#@ ensures 0 <= \result[31] and \result[31] <= 255
#@ ensures 0 <= \result[32] and \result[32] <= 255
#@ ensures 0 <= \result[33] and \result[33] <= 255
#@ ensures 0 <= \result[34] and \result[34] <= 255
#@ ensures 0 <= \result[35] and \result[35] <= 255
#@ ensures 0 <= \result[36] and \result[36] <= 255
#@ ensures 0 <= \result[37] and \result[37] <= 255
#@ ensures 0 <= \result[38] and \result[38] <= 255
#@ ensures 0 <= \result[39] and \result[39] <= 255
#@ ensures 0 <= \result[40] and \result[40] <= 255
#@ ensures 0 <= \result[41] and \result[41] <= 255
#@ ensures 0 <= \result[42] and \result[42] <= 255
#@ ensures 0 <= \result[43] and \result[43] <= 255
#@ ensures 0 <= \result[44] and \result[44] <= 255
#@ ensures 0 <= \result[45] and \result[45] <= 255
#@ ensures 0 <= \result[46] and \result[46] <= 255
#@ ensures 0 <= \result[47] and \result[47] <= 255
#@ ensures 0 <= \result[48] and \result[48] <= 255
#@ ensures 0 <= \result[49] and \result[49] <= 255
#@ ensures 0 <= \result[50] and \result[50] <= 255
#@ ensures 0 <= \result[51] and \result[51] <= 255
#@ ensures 0 <= \result[52] and \result[52] <= 255
#@ ensures 0 <= \result[53] and \result[53] <= 255
#@ ensures 0 <= \result[54] and \result[54] <= 255
#@ ensures 0 <= \result[55] and \result[55] <= 255
#@ ensures 0 <= \result[56] and \result[56] <= 255
#@ ensures 0 <= \result[57] and \result[57] <= 255
#@ ensures 0 <= \result[58] and \result[58] <= 255
#@ ensures 0 <= \result[59] and \result[59] <= 255
#@ ensures 0 <= \result[60] and \result[60] <= 255
#@ ensures 0 <= \result[61] and \result[61] <= 255
#@ ensures 0 <= \result[62] and \result[62] <= 255
#@ ensures 0 <= \result[63] and \result[63] <= 255
#@ ensures \result[0]*16777216 + \result[1]*65536 + \result[2]*256 + \result[3] == fields[0]
#@ ensures \result[4]*256 + \result[5] == fields[1]
#@ ensures \result[6]*256 + \result[7] == fields[2]
#@ ensures \result[8]*256 + \result[9] == fields[3]
#@ ensures \result[10]*256 + \result[11] == fields[4]
#@ ensures \result[12]*256 + \result[13] == fields[5]
#@ ensures \result[14]*16777216 + \result[15]*65536 + \result[16]*256 + \result[17] == fields[6]
#@ ensures \result[18]*16777216 + \result[19]*65536 + \result[20]*256 + \result[21] == fields[7]
#@ ensures \result[22]*16777216 + \result[23]*65536 + \result[24]*256 + \result[25] == fields[8]
#@ ensures \result[26]*16777216 + \result[27]*65536 + \result[28]*256 + \result[29] == fields[9]
#@ ensures \result[30]*16777216 + \result[31]*65536 + \result[32]*256 + \result[33] == fields[10]
#@ ensures \result[34]*16777216 + \result[35]*65536 + \result[36]*256 + \result[37] == fields[11]
#@ ensures \result[38]*16777216 + \result[39]*65536 + \result[40]*256 + \result[41] == fields[12]
#@ ensures \result[42]*16777216 + \result[43]*65536 + \result[44]*256 + \result[45] == fields[13]
#@ ensures \result[46]*16777216 + \result[47]*65536 + \result[48]*256 + \result[49] == fields[14]
#@ ensures \result[50]*16777216 + \result[51]*65536 + \result[52]*256 + \result[53] == fields[15]
#@ ensures \result[54]*16777216 + \result[55]*65536 + \result[56]*256 + \result[57] == fields[16]
#@ ensures \result[58]*16777216 + \result[59]*65536 + \result[60]*256 + \result[61] == fields[17]
def pack_inode(fields: list) -> list:
    out = [0] * 64
    b0 = pack32(fields[0])
    out[0] = b0[0]
    out[1] = b0[1]
    out[2] = b0[2]
    out[3] = b0[3]
    b1 = pack16(fields[1])
    out[4] = b1[0]
    out[5] = b1[1]
    b2 = pack16(fields[2])
    out[6] = b2[0]
    out[7] = b2[1]
    b3 = pack16(fields[3])
    out[8] = b3[0]
    out[9] = b3[1]
    b4 = pack16(fields[4])
    out[10] = b4[0]
    out[11] = b4[1]
    b5 = pack16(fields[5])
    out[12] = b5[0]
    out[13] = b5[1]
    b6 = pack32(fields[6])
    out[14] = b6[0]
    out[15] = b6[1]
    out[16] = b6[2]
    out[17] = b6[3]
    b7 = pack32(fields[7])
    out[18] = b7[0]
    out[19] = b7[1]
    out[20] = b7[2]
    out[21] = b7[3]
    b8 = pack32(fields[8])
    out[22] = b8[0]
    out[23] = b8[1]
    out[24] = b8[2]
    out[25] = b8[3]
    b9 = pack32(fields[9])
    out[26] = b9[0]
    out[27] = b9[1]
    out[28] = b9[2]
    out[29] = b9[3]
    b10 = pack32(fields[10])
    out[30] = b10[0]
    out[31] = b10[1]
    out[32] = b10[2]
    out[33] = b10[3]
    b11 = pack32(fields[11])
    out[34] = b11[0]
    out[35] = b11[1]
    out[36] = b11[2]
    out[37] = b11[3]
    b12 = pack32(fields[12])
    out[38] = b12[0]
    out[39] = b12[1]
    out[40] = b12[2]
    out[41] = b12[3]
    b13 = pack32(fields[13])
    out[42] = b13[0]
    out[43] = b13[1]
    out[44] = b13[2]
    out[45] = b13[3]
    b14 = pack32(fields[14])
    out[46] = b14[0]
    out[47] = b14[1]
    out[48] = b14[2]
    out[49] = b14[3]
    b15 = pack32(fields[15])
    out[50] = b15[0]
    out[51] = b15[1]
    out[52] = b15[2]
    out[53] = b15[3]
    b16 = pack32(fields[16])
    out[54] = b16[0]
    out[55] = b16[1]
    out[56] = b16[2]
    out[57] = b16[3]
    b17 = pack32(fields[17])
    out[58] = b17[0]
    out[59] = b17[1]
    out[60] = b17[2]
    out[61] = b17[3]
    return bytes(out)

#@ requires \valid(data, 64)
#@ requires 0 <= data[0] and data[0] <= 255
#@ requires 0 <= data[1] and data[1] <= 255
#@ requires 0 <= data[2] and data[2] <= 255
#@ requires 0 <= data[3] and data[3] <= 255
#@ requires 0 <= data[4] and data[4] <= 255
#@ requires 0 <= data[5] and data[5] <= 255
#@ requires 0 <= data[6] and data[6] <= 255
#@ requires 0 <= data[7] and data[7] <= 255
#@ requires 0 <= data[8] and data[8] <= 255
#@ requires 0 <= data[9] and data[9] <= 255
#@ requires 0 <= data[10] and data[10] <= 255
#@ requires 0 <= data[11] and data[11] <= 255
#@ requires 0 <= data[12] and data[12] <= 255
#@ requires 0 <= data[13] and data[13] <= 255
#@ requires 0 <= data[14] and data[14] <= 255
#@ requires 0 <= data[15] and data[15] <= 255
#@ requires 0 <= data[16] and data[16] <= 255
#@ requires 0 <= data[17] and data[17] <= 255
#@ requires 0 <= data[18] and data[18] <= 255
#@ requires 0 <= data[19] and data[19] <= 255
#@ requires 0 <= data[20] and data[20] <= 255
#@ requires 0 <= data[21] and data[21] <= 255
#@ requires 0 <= data[22] and data[22] <= 255
#@ requires 0 <= data[23] and data[23] <= 255
#@ requires 0 <= data[24] and data[24] <= 255
#@ requires 0 <= data[25] and data[25] <= 255
#@ requires 0 <= data[26] and data[26] <= 255
#@ requires 0 <= data[27] and data[27] <= 255
#@ requires 0 <= data[28] and data[28] <= 255
#@ requires 0 <= data[29] and data[29] <= 255
#@ requires 0 <= data[30] and data[30] <= 255
#@ requires 0 <= data[31] and data[31] <= 255
#@ requires 0 <= data[32] and data[32] <= 255
#@ requires 0 <= data[33] and data[33] <= 255
#@ requires 0 <= data[34] and data[34] <= 255
#@ requires 0 <= data[35] and data[35] <= 255
#@ requires 0 <= data[36] and data[36] <= 255
#@ requires 0 <= data[37] and data[37] <= 255
#@ requires 0 <= data[38] and data[38] <= 255
#@ requires 0 <= data[39] and data[39] <= 255
#@ requires 0 <= data[40] and data[40] <= 255
#@ requires 0 <= data[41] and data[41] <= 255
#@ requires 0 <= data[42] and data[42] <= 255
#@ requires 0 <= data[43] and data[43] <= 255
#@ requires 0 <= data[44] and data[44] <= 255
#@ requires 0 <= data[45] and data[45] <= 255
#@ requires 0 <= data[46] and data[46] <= 255
#@ requires 0 <= data[47] and data[47] <= 255
#@ requires 0 <= data[48] and data[48] <= 255
#@ requires 0 <= data[49] and data[49] <= 255
#@ requires 0 <= data[50] and data[50] <= 255
#@ requires 0 <= data[51] and data[51] <= 255
#@ requires 0 <= data[52] and data[52] <= 255
#@ requires 0 <= data[53] and data[53] <= 255
#@ requires 0 <= data[54] and data[54] <= 255
#@ requires 0 <= data[55] and data[55] <= 255
#@ requires 0 <= data[56] and data[56] <= 255
#@ requires 0 <= data[57] and data[57] <= 255
#@ requires 0 <= data[58] and data[58] <= 255
#@ requires 0 <= data[59] and data[59] <= 255
#@ requires 0 <= data[60] and data[60] <= 255
#@ requires 0 <= data[61] and data[61] <= 255
#@ requires 0 <= data[62] and data[62] <= 255
#@ requires 0 <= data[63] and data[63] <= 255
#@ assigns \nothing
#@ ensures \length(\result) == 18
#@ ensures \result[0] == data[0]*16777216 + data[1]*65536 + data[2]*256 + data[3]
#@ ensures \result[1] == data[4]*256 + data[5]
#@ ensures \result[2] == data[6]*256 + data[7]
#@ ensures \result[3] == data[8]*256 + data[9]
#@ ensures \result[4] == data[10]*256 + data[11]
#@ ensures \result[5] == data[12]*256 + data[13]
#@ ensures \result[6] == data[14]*16777216 + data[15]*65536 + data[16]*256 + data[17]
#@ ensures \result[7] == data[18]*16777216 + data[19]*65536 + data[20]*256 + data[21]
#@ ensures \result[8] == data[22]*16777216 + data[23]*65536 + data[24]*256 + data[25]
#@ ensures \result[9] == data[26]*16777216 + data[27]*65536 + data[28]*256 + data[29]
#@ ensures \result[10] == data[30]*16777216 + data[31]*65536 + data[32]*256 + data[33]
#@ ensures \result[11] == data[34]*16777216 + data[35]*65536 + data[36]*256 + data[37]
#@ ensures \result[12] == data[38]*16777216 + data[39]*65536 + data[40]*256 + data[41]
#@ ensures \result[13] == data[42]*16777216 + data[43]*65536 + data[44]*256 + data[45]
#@ ensures \result[14] == data[46]*16777216 + data[47]*65536 + data[48]*256 + data[49]
#@ ensures \result[15] == data[50]*16777216 + data[51]*65536 + data[52]*256 + data[53]
#@ ensures \result[16] == data[54]*16777216 + data[55]*65536 + data[56]*256 + data[57]
#@ ensures \result[17] == data[58]*16777216 + data[59]*65536 + data[60]*256 + data[61]
def unpack_inode(data: list) -> list:
    fields = [0] * 18
    fields[0] = unpack32(data, 0)
    fields[1] = unpack16(data, 4)
    fields[2] = unpack16(data, 6)
    fields[3] = unpack16(data, 8)
    fields[4] = unpack16(data, 10)
    fields[5] = unpack16(data, 12)
    fields[6] = unpack32(data, 14)
    fields[7] = unpack32(data, 18)
    fields[8] = unpack32(data, 22)
    fields[9] = unpack32(data, 26)
    fields[10] = unpack32(data, 30)
    fields[11] = unpack32(data, 34)
    fields[12] = unpack32(data, 38)
    fields[13] = unpack32(data, 42)
    fields[14] = unpack32(data, 46)
    fields[15] = unpack32(data, 50)
    fields[16] = unpack32(data, 54)
    fields[17] = unpack32(data, 58)
    return fields

# round-trip as a program function (binds the intermediate; \result[k] is L0-legal)
#@ requires \valid(fields, 18)
#@ requires 0 <= fields[0] and fields[0] <= 4294967295
#@ requires 0 <= fields[1] and fields[1] <= 65535
#@ requires 0 <= fields[2] and fields[2] <= 65535
#@ requires 0 <= fields[3] and fields[3] <= 65535
#@ requires 0 <= fields[4] and fields[4] <= 65535
#@ requires 0 <= fields[5] and fields[5] <= 65535
#@ requires 0 <= fields[6] and fields[6] <= 4294967295
#@ requires 0 <= fields[7] and fields[7] <= 4294967295
#@ requires 0 <= fields[8] and fields[8] <= 4294967295
#@ requires 0 <= fields[9] and fields[9] <= 4294967295
#@ requires 0 <= fields[10] and fields[10] <= 4294967295
#@ requires 0 <= fields[11] and fields[11] <= 4294967295
#@ requires 0 <= fields[12] and fields[12] <= 4294967295
#@ requires 0 <= fields[13] and fields[13] <= 4294967295
#@ requires 0 <= fields[14] and fields[14] <= 4294967295
#@ requires 0 <= fields[15] and fields[15] <= 4294967295
#@ requires 0 <= fields[16] and fields[16] <= 4294967295
#@ requires 0 <= fields[17] and fields[17] <= 4294967295
#@ assigns \nothing
#@ ensures \result[0] == fields[0]
#@ ensures \result[1] == fields[1]
#@ ensures \result[2] == fields[2]
#@ ensures \result[3] == fields[3]
#@ ensures \result[4] == fields[4]
#@ ensures \result[5] == fields[5]
#@ ensures \result[6] == fields[6]
#@ ensures \result[7] == fields[7]
#@ ensures \result[8] == fields[8]
#@ ensures \result[9] == fields[9]
#@ ensures \result[10] == fields[10]
#@ ensures \result[11] == fields[11]
#@ ensures \result[12] == fields[12]
#@ ensures \result[13] == fields[13]
#@ ensures \result[14] == fields[14]
#@ ensures \result[15] == fields[15]
#@ ensures \result[16] == fields[16]
#@ ensures \result[17] == fields[17]
def roundtrip(fields: list) -> list:
    packed = pack_inode(fields)
    return unpack_inode(packed)
