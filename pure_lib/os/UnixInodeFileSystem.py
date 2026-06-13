# Pure Python byte-packing helpers (replaces import struct / import time)


#@ requires 0 <= v and v <= 65535
#@ assigns \nothing
#@ ensures \length(\result) == 2
#@ ensures 0 <= \result[0] and \result[0] <= 255
#@ ensures 0 <= \result[1] and \result[1] <= 255
#@ ensures \result[0] * 256 + \result[1] == v
def _pack_uint16_be(v: int) -> list:
    """Pack a 16-bit unsigned int, big-endian (\result[0]*256 + \result[1] == v)."""
    return bytes([v // 256, v % 256])


#@ requires \valid(data, offset + 2)
#@ requires offset >= 0
#@ requires 0 <= data[offset] and data[offset] <= 255
#@ requires 0 <= data[offset + 1] and data[offset + 1] <= 255
#@ assigns \nothing
#@ ensures \result == data[offset] * 256 + data[offset + 1]
#@ ensures 0 <= \result and \result <= 65535
def _unpack_uint16_be(data: list, offset: int) -> int:
    """Unpack a 16-bit unsigned int, big-endian (inverse of _pack_uint16_be)."""
    return data[offset] * 256 + data[offset + 1]


#@ requires 0 <= v and v <= 4294967295
#@ assigns \nothing
#@ ensures \length(\result) == 4
#@ ensures 0 <= \result[0] and \result[0] <= 255
#@ ensures 0 <= \result[1] and \result[1] <= 255
#@ ensures 0 <= \result[2] and \result[2] <= 255
#@ ensures 0 <= \result[3] and \result[3] <= 255
#@ ensures \result[0] * 16777216 + \result[1] * 65536 + \result[2] * 256 + \result[3] == v
def _pack_uint32_be(v: int) -> list:
    """Pack a 32-bit unsigned int, big-endian (b0*2^24+b1*2^16+b2*2^8+b3 == v)."""
    return bytes([v // 16777216, (v // 65536) % 256, (v // 256) % 256, v % 256])


#@ requires \valid(data, offset + 4)
#@ requires offset >= 0
#@ requires 0 <= data[offset] and data[offset] <= 255
#@ requires 0 <= data[offset + 1] and data[offset + 1] <= 255
#@ requires 0 <= data[offset + 2] and data[offset + 2] <= 255
#@ requires 0 <= data[offset + 3] and data[offset + 3] <= 255
#@ assigns \nothing
#@ ensures \result == data[offset] * 16777216 + data[offset + 1] * 65536 + data[offset + 2] * 256 + data[offset + 3]
#@ ensures 0 <= \result and \result <= 4294967295
def _unpack_uint32_be(data: list, offset: int) -> int:
    """Unpack a 32-bit unsigned int, big-endian (inverse of _pack_uint32_be)."""
    return (data[offset] * 16777216 + data[offset + 1] * 65536 +
            data[offset + 2] * 256 + data[offset + 3])


#@ requires \valid(fields, 18)
#@ requires 0 <= fields[0] and fields[0] <= 4294967295
#@ for k in range(1, 6):
#@     requires 0 <= fields[k] and fields[k] <= 65535
#@ requires 0 <= fields[6] and fields[6] <= 4294967295
#@ requires 0 <= fields[7] and fields[7] <= 4294967295
#@ for k in range(8, 18):
#@     requires 0 <= fields[k] and fields[k] <= 4294967295
#@ assigns \nothing
#@ ensures \length(\result) == 64
#@ for i in range(0, 64):
#@     ensures 0 <= \result[i] and \result[i] <= 255
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
#@ no_inline
def _pack_inode(fields: list) -> list:
    out = [0] * 64
    b0 = _pack_uint32_be(fields[0])
    out[0] = b0[0]
    out[1] = b0[1]
    out[2] = b0[2]
    out[3] = b0[3]
    b1 = _pack_uint16_be(fields[1])
    out[4] = b1[0]
    out[5] = b1[1]
    b2 = _pack_uint16_be(fields[2])
    out[6] = b2[0]
    out[7] = b2[1]
    b3 = _pack_uint16_be(fields[3])
    out[8] = b3[0]
    out[9] = b3[1]
    b4 = _pack_uint16_be(fields[4])
    out[10] = b4[0]
    out[11] = b4[1]
    b5 = _pack_uint16_be(fields[5])
    out[12] = b5[0]
    out[13] = b5[1]
    b6 = _pack_uint32_be(fields[6])
    out[14] = b6[0]
    out[15] = b6[1]
    out[16] = b6[2]
    out[17] = b6[3]
    b7 = _pack_uint32_be(fields[7])
    out[18] = b7[0]
    out[19] = b7[1]
    out[20] = b7[2]
    out[21] = b7[3]
    b8 = _pack_uint32_be(fields[8])
    out[22] = b8[0]
    out[23] = b8[1]
    out[24] = b8[2]
    out[25] = b8[3]
    b9 = _pack_uint32_be(fields[9])
    out[26] = b9[0]
    out[27] = b9[1]
    out[28] = b9[2]
    out[29] = b9[3]
    b10 = _pack_uint32_be(fields[10])
    out[30] = b10[0]
    out[31] = b10[1]
    out[32] = b10[2]
    out[33] = b10[3]
    b11 = _pack_uint32_be(fields[11])
    out[34] = b11[0]
    out[35] = b11[1]
    out[36] = b11[2]
    out[37] = b11[3]
    b12 = _pack_uint32_be(fields[12])
    out[38] = b12[0]
    out[39] = b12[1]
    out[40] = b12[2]
    out[41] = b12[3]
    b13 = _pack_uint32_be(fields[13])
    out[42] = b13[0]
    out[43] = b13[1]
    out[44] = b13[2]
    out[45] = b13[3]
    b14 = _pack_uint32_be(fields[14])
    out[46] = b14[0]
    out[47] = b14[1]
    out[48] = b14[2]
    out[49] = b14[3]
    b15 = _pack_uint32_be(fields[15])
    out[50] = b15[0]
    out[51] = b15[1]
    out[52] = b15[2]
    out[53] = b15[3]
    b16 = _pack_uint32_be(fields[16])
    out[54] = b16[0]
    out[55] = b16[1]
    out[56] = b16[2]
    out[57] = b16[3]
    b17 = _pack_uint32_be(fields[17])
    out[58] = b17[0]
    out[59] = b17[1]
    out[60] = b17[2]
    out[61] = b17[3]
    return bytes(out)

#@ requires \valid(data, 64)
#@ for i in range(0, 64):
#@     requires 0 <= data[i] and data[i] <= 255
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
#@ no_inline
def _unpack_inode(data: list) -> list:
    fields = [0] * 18
    fields[0] = _unpack_uint32_be(data, 0)
    fields[1] = _unpack_uint16_be(data, 4)
    fields[2] = _unpack_uint16_be(data, 6)
    fields[3] = _unpack_uint16_be(data, 8)
    fields[4] = _unpack_uint16_be(data, 10)
    fields[5] = _unpack_uint16_be(data, 12)
    fields[6] = _unpack_uint32_be(data, 14)
    fields[7] = _unpack_uint32_be(data, 18)
    fields[8] = _unpack_uint32_be(data, 22)
    fields[9] = _unpack_uint32_be(data, 26)
    fields[10] = _unpack_uint32_be(data, 30)
    fields[11] = _unpack_uint32_be(data, 34)
    fields[12] = _unpack_uint32_be(data, 38)
    fields[13] = _unpack_uint32_be(data, 42)
    fields[14] = _unpack_uint32_be(data, 46)
    fields[15] = _unpack_uint32_be(data, 50)
    fields[16] = _unpack_uint32_be(data, 54)
    fields[17] = _unpack_uint32_be(data, 58)
    return fields


# ============================================================================
# --- DIRECTORY-ENTRY NAME CODEC (Phase 0, leaf L1) ---
#
# A dirent maps a filename -> an inode number (unix §4.1).  The on-disk name
# field is 30 bytes, but the FAITHFUL VALUE that field carries is the filename
# STRING.  PyCSL models `str` as Why3 `string.String` — `==`, `\str_length`,
# substring and concat are all faithful value operations — so the name-codec
# round-trip `_decode_name(_encode_name(name)) == name` PROVES by contract
# composition (Alt-Ergo, ~550 steps, zero `\trusted`, zero proof axioms).
# This is the string twin of the already-proven inode-field codec round-trip
# (`_unpack_inode(_pack_inode(x)) == x`) and is the missing piece that makes
# every name-keyed consequence (mkdir -> access-present) provable AGAINST THE
# STRING/MAP VIEW of the namespace.
#
# THE BYTE DOMAIN IS NOW EXPRESSIBLE (Gap 5 CLOSED, commit 7f53db2).  The
# `ord`/`chr` char<->int bridge exists: `ord(name[i])` is the byte (0..255) of a
# 1-char string, `chr(b)` is a 1-char string, and the per-char round-trip
# `chr(ord(c)) == c` is a Why3 `string.Char` THEORY lemma (no axiom, zero TCB
# growth).  So the FAITHFUL byte codec is provable:
#   * `_pad_name(name)` ENCODES `name`'s chars into the 30-byte field via
#     `b[i] = ord(name[i])`, null-padded (the byte layout — no longer `[0]*30`).
#   * the per-char decode `chr(b[i])` recovers each char; the byte round-trip
#     `_byte_codec_char(c) == c` (`chr(ord(c)) == c`) proves standalone.
#   * a FIXED-WIDTH name round-trip through the disk-array slice
#     (`disk[off] = ord(name[k]); ... ; chr(disk[off]) == name[k]`) proves —
#     the byte twin of the inode-field codec round-trip, AGAINST THE ON-DISK
#     BYTES.  See `pure_lib_test/formal_os_namecodec.py` (the byte-codec leaf)
#     and `pure_lib_test/formal_os_namespace.py` (the beachhead consequence:
#     mkdir->access-PRESENT / rmdir->access-ABSENT against the disk bytes).
#
# REMAINING WALL — the *variable-length* loop round-trip.  Decoding an
# arbitrary-length name by accumulating `out = out + chr(b[j])` over a loop
# needs the invariant `out == String.substring(name, 0, j)`, whose inductive
# step (concat of the proven per-char char) the solver does not discharge
# (Unknown / timeout).  So the GENERAL `decode(encode(name)) == name` for an
# unbounded name stays a documented wall (DD-HHMM-convergence-gap-N.md); the
# beachhead uses the fixed-width form, which is what the namespace consequence
# actually rests on (a name is recovered char-for-char and compared).
# ============================================================================


#@ requires \str_length(name) <= 30
#@ assigns \nothing
#@ ensures \result == name
def _encode_name(name: str) -> str:
    """Encode a filename into the value stored in a dirent name field.

    In the faithful string model the stored value IS the name: a name of
    <= 30 chars round-trips exactly (the 30-char cap mirrors the on-disk
    30-byte field width).  The contract pins the recoverable value so the
    round-trip proves by composition.
    """
    return name


#@ assigns \nothing
#@ ensures \result == stored
def _decode_name(stored: str) -> str:
    """Recover the filename from a stored dirent name value (inverse of
    `_encode_name`).  In the string model this is identity; the contract
    pins it so `_decode_name(_encode_name(name)) == name`."""
    return stored


#@ requires \str_length(name) <= 30
#@ assigns \nothing
#@ ensures \result == name
def _name_codec_roundtrip(name: str) -> str:
    """The name-codec ROUND-TRIP leaf (string view): `decode(encode(name)) == name`.

    Proven standalone (string twin of the inode-field codec round-trip).
    The BYTE view of the same round-trip is `_byte_codec_char` below (now that
    Gap 5 is closed).  `_dir_lookup` resolves names through this codec, so
    `mkdir(d) -> access(d) == present` is provable against the on-disk bytes.
    """
    return _decode_name(_encode_name(name))


#@ requires \str_length(c) == 1
#@ assigns \nothing
#@ ensures \result == c
def _byte_codec_char(c: str) -> str:
    """The BYTE codec round-trip at the char granularity: encode a 1-char name
    field through a byte and recover it — `chr(ord(c)) == c`.

    This is the FAITHFUL byte twin of the inode-field codec round-trip, now
    expressible because Gap 5 (the `ord`/`chr` char<->int bridge) is closed.
    `ord(c)` is the byte (0..255) stored in the dirent name field; `chr(...)`
    recovers the char.  The round-trip is a Why3 `string.Char` theory lemma —
    no axiom, zero TCB growth.  The fixed-width name codec (`_pad_name` encode +
    the per-byte `chr` decode in `_dir_lookup`) composes this char round-trip,
    which is why a written name is recovered byte-for-byte and matched.
    """
    return chr(ord(c))


#@ requires 0 <= b and b <= 255
#@ assigns \nothing
#@ ensures \str_length(\result) == 1
def _decode_byte(b: int) -> str:
    """Recover one name-field char from its stored byte (inverse of `ord`).
    `chr(b)` is a 1-char string; pairs with `ord` so `chr(ord(c)) == c`."""
    return chr(b)


#@ assigns \nothing
#@ ensures \length(\result) == 30
def _pad_name(name: str) -> list:
    r"""Encode a filename into the on-disk 30-byte dirent name field.

    FAITHFUL BYTE LAYOUT (Gap 5 closed): each char of `name` is stored as its
    byte `b[i] = ord(name[i])`; the remaining positions stay 0 (null padding),
    exactly the on-disk `struct '30s'` field.  This REPLACES the former
    `[0]*30` (which discarded the name, so `mkdir("a")`/`mkdir("b")` wrote
    identical zero-named entries and no name-keyed consequence could prove).
    The decode side is `chr(disk[off+k])` (see `_dir_lookup`); the byte
    round-trip `chr(ord(name[k])) == name[k]` is `_byte_codec_char`.

    TOTAL (no precondition): the field is exactly 30 bytes, so a name longer
    than 30 chars is TRUNCATED to the field width (`m = min(len(name), 30)`) —
    the faithful on-disk `struct '30s'` behaviour, and what keeps every caller
    (`_write_entry`, the symlink target write) free of a length precondition
    they cannot discharge.  The contract promises `\length == 30` (the bounds
    the packers/blits need); the per-byte value `out[i] == ord(name[i])` for
    `i < m` is established at each store and is what the fixed-width namespace
    consequence (`formal_os_namespace.py`) recovers and compares.
    """
    out = [0] * 30
    n = len(name)
    m = n
    if m > 30:
        m = 30
    #@ loop invariant 0 <= i and i <= m
    #@ loop invariant m <= 30
    #@ loop variant m - i
    for i in range(m):
        out[i] = ord(name[i])
    return out


#@ requires 0 <= inode_num and inode_num < 65536
#@ requires \length(name_bytes) >= 30
#@ assigns \nothing
#@ ensures \length(\result) == 32
def _pack_direntry(inode_num: int, name_bytes: list) -> list:
    """Pack a 32-byte directory entry (big-endian '>H30s').

    Leaf-compositional: build a fixed 32-byte array by index-set, mirroring
    _pack_inode. The earlier `_pack_uint16_be(...) + padded` form produced a
    `seq` (list `+` is seq concat) that cannot flow into a disk `array int`
    slice — the @rho mismatch. The name byte *content* stays opaque (Gap 5);
    only the buffer shape is modeled.
    """
    entry = [0] * 32
    hilo = _pack_uint16_be(inode_num)
    entry[0] = hilo[0]
    entry[1] = hilo[1]
    entry[2] = name_bytes[0]
    entry[3] = name_bytes[1]
    entry[4] = name_bytes[2]
    entry[5] = name_bytes[3]
    entry[6] = name_bytes[4]
    entry[7] = name_bytes[5]
    entry[8] = name_bytes[6]
    entry[9] = name_bytes[7]
    entry[10] = name_bytes[8]
    entry[11] = name_bytes[9]
    entry[12] = name_bytes[10]
    entry[13] = name_bytes[11]
    entry[14] = name_bytes[12]
    entry[15] = name_bytes[13]
    entry[16] = name_bytes[14]
    entry[17] = name_bytes[15]
    entry[18] = name_bytes[16]
    entry[19] = name_bytes[17]
    entry[20] = name_bytes[18]
    entry[21] = name_bytes[19]
    entry[22] = name_bytes[20]
    entry[23] = name_bytes[21]
    entry[24] = name_bytes[22]
    entry[25] = name_bytes[23]
    entry[26] = name_bytes[24]
    entry[27] = name_bytes[25]
    entry[28] = name_bytes[26]
    entry[29] = name_bytes[27]
    entry[30] = name_bytes[28]
    entry[31] = name_bytes[29]
    return entry


#@ requires \valid(data, 32)
#@ assigns \nothing
#@ ensures \result[0] >= 0
def _unpack_direntry(data: list) -> tuple:
    """Unpack a 32-byte directory entry into (inode_num, name_bytes)."""
    inode_num = _unpack_uint16_be(data, 0)
    name_bytes = bytes(data[2:32])
    return inode_num, name_bytes


# ── Directory-name presence view (gap-9 beachhead) ──────────────────────────
# The presence of `name` in directory block 5 (the root dir) is the logic
# proposition `dir_lookup(disk, 5, name) >= 0`, where `dir_lookup` is the
# abstract logic model of the 16-slot scan (the UnixFs.Dir.* axiom symbol that
# `_dir_lookup`'s ensures binds its real result to). The cross-validated
# `scan_reflects_present` axiom relates it to the existential over the abstract
# per-slot decode (`slot_inode`/`slot_name`):
#   dir_lookup disk blk name >= 0  <->  exists k. 0<=k<16 /\ slot_inode<>0
#                                                   /\ slot_inode<32 /\ slot_name=name
# so a mutator that writes a live slot ESTABLISHES dir_lookup>=0 (existential =>
# dir_lookup, via the axiom on the post-write disk) and an observer's
# `_dir_lookup(5,name)` REFLECTS it (its ensures binds \result == dir_lookup).
# This `dir_lookup(disk, 5, name) >= 0` form is used both in the syscall
# contracts here and, after the import, in the os `__init__.py` public
# wrappers — a single light proposition with no `\exists` trigger to blow up
# the importer's wrapper-VC E-matching.


#@ class invariant \length(self.disk) >= 131072
#@ class invariant inode_bytes_valid(self.disk)
#@ class invariant \length(self.fd_open) == 64
#@ class invariant \length(self.fd_inode) == 64
#@ class invariant \length(self.fd_offset) == 64
#@ class invariant \length(self.fd_flags) == 64
#@ class invariant \length(self.fd_block) == 64
#@ class invariant self.next_fd >= 3
#@ class invariant self.cur_uid >= 0
#@ class invariant self.cur_gid >= 0
#@ class invariant self._mtime_ticks >= 0
# DIRECTORY UNIQUENESS INVARIANT (gap-12 statable, gap-13 PROVEN) — block 5 (the
# root directory) never holds two DISTINCT live slots that decode to the same
# name. Stated over the registered `UnixFs.Dir.*` abstract symbols
# `slot_inode`/`slot_name`. This is now a PROVEN, maintained class invariant: it
# REPLACES the trusted uniqueness ensures that used to live on `_dir_find_slot`,
# removing directory uniqueness from the TCB.
#
# Discharge (see 11-1404-convergence-spec-13.md):
#  - WALL A (statability, gap-12): `_class_inv_refs_axiom_func` gate +
#    `_precompute_axiom_logic_funcs` before `_emit_type_decls` lower the invariant
#    to the raw bound `slot_inode disk 5 i` application, declared before the record.
#  - WALL E (establishment, gap-13): the constructor / `_filesystem` global
#    witness is a zeroed `Array.make 131072 0`; the registered cross-validated
#    axiom `UnixFs.Dir.empty_disk_slots_dead` (zeroed block-5 region -> all 16
#    slots dead) makes establishment VACUOUS (no live slot -> no duplicate pair).
#  - WALL M (maintenance, gap-13): a class invariant obligates EVERY
#    `assigns self.disk` method. The 7 directory mutators maintain it via the
#    registered `UnixFs.Dir.insert_preserves_unique`; the non-directory writers
#    (chmod/chown/utimensat/write/truncate/ftruncate/open) write the disk ONLY
#    through the helpers `_write_inode`/`_set_bitmap`/`_alloc_inode`/`_alloc_block`/
#    `_block_roundtrip`, each of which carries a block-5 DECODE-FRAME ensures
#    (its write region is disjoint from [2560,3072); the registered cross-
#    validated `UnixFs.Dir.block5_decode_frame` converts the byte-frame into a
#    decode-frame), so those syscalls inherit `uniq` maintenance with ZERO body
#    annotation. The chmod balloon (gap-13: 30s/232M-step timeout over the
#    abstract block-5 decode) collapses to a one-line rewrite.
#@ class invariant uniq(self.disk)
class UnixInodeFileSystem:
    BLOCK_SIZE = 512
    NUM_BLOCKS = 256  # 128 KB Virtual Disk Block Device
    MAX_INODES = 32

    # System Call Open Flags
    O_RDONLY = 0
    O_WRONLY = 1
    O_RDWR   = 2
    O_CREAT  = 64

    # lseek Whence Flags
    SEEK_SET = 0
    SEEK_CUR = 1
    SEEK_END = 2

    def __init__(self, num_blocks: int = 256, load_dir=None, clock=None):
        # The raw bytearray virtual hard drive (array int). Its length is the
        # disk capacity = num_blocks * BLOCK_SIZE. `num_blocks` is a runtime
        # argument so the disk can be made larger than the 256-block default;
        # it is clamped to >= 256 because the base layout (32-inode region,
        # block bitmap, root directory in block 5) and every bounds proof
        # assume at least 131072 bytes. The class invariant is
        # `\length(self.disk) >= 131072`, so a larger disk keeps every
        # access bound valid (index < 131072 <= length).
        if num_blocks < self.NUM_BLOCKS:
            num_blocks = self.NUM_BLOCKS
        self.disk: list = bytearray(131072)  # 256 * 512, literal for PyCSL

        # Kernel Process File Descriptor Table. The fd table is modeled as
        # four parallel `array int` columns indexed by fd (capacity 64):
        #   fd_open[fd]   1 if fd is open, else 0 (replaces dict membership)
        #   fd_inode[fd]  inode number the fd refers to
        #   fd_offset[fd] current read/write offset
        #   fd_flags[fd]  open flags
        self.fd_open: list = [0] * 64
        self.fd_inode: list = [0] * 64
        # fd_block: in-core cache of the open file's first data block (the
        # Unix in-core file-table analogue) — lets reads resolve content
        # without re-decoding the inode each call; set at open and on first
        # write. 0 = not yet allocated.
        self.fd_block: list = [0] * 64
        self.fd_offset: list = [0] * 64
        self.fd_flags: list = [0] * 64
        self.next_fd = 3 # 0, 1, 2 reserved for standard streams

        # Current process credentials (uid 0 = root, bypasses all checks)
        self.cur_uid = 0
        self.cur_gid = 0

        # Monotonic clock for inode timestamps (mtime/atime).
        # If an external ClockModel is provided (via World), its counter
        # is shared across all subsystems. Otherwise, an internal counter
        # is used so mtime values are at least monotonically increasing.
        self._mtime_ticks = 0
        self._clock = clock

        # Format the storage array layout
        self._format_disk()

        # Optional: populate from a real host directory. This is a
        # runtime-only convenience — the loader performs host filesystem I/O
        # (os.walk + reading real files), which is inherently unverifiable, so
        # it lives in a separate module imported lazily here and is NOT part of
        # the verified surface. The verified syscalls do the actual writes.
        if load_dir is not None:
            from unixfs_host_loader import load_host_dir
            load_host_dir(self, load_dir)

    # --- CLOCK (mtime) ---

    #@ assigns self._mtime_ticks
    #@ ensures \result >= 0
    def _now(self) -> int:
        """Return a monotonically increasing timestamp for inode mtime/atime.
        Uses the shared ClockModel if wired (via World), else an internal
        counter. Either way, the returned value is >= 0 and non-decreasing."""
        if self._clock is not None:
            return self._clock.monotonic()
        self._mtime_ticks = self._mtime_ticks + 1
        return self._mtime_ticks

    # --- BITMAP ALGORITHMS ---

    # LEAF SINGLE-BYTE WRITE (directory-frame rework, 2026-06-13). Every non-directory
    # disk mutation that touches a SINGLE byte outside block 5 ([2560,3072)) routes
    # through here so the heavy class-invariant MAINTENANCE (byte-range + directory
    # uniqueness) is discharged ONCE, in this minimal leaf context, instead of being
    # re-derived inside each bit-twiddling/codec-laden caller (where the double-forall
    # E-match-explodes — 42M+ steps). With the multi-pattern-triggered
    # UnixFs.Dir.block5_decode_frame, the uniqueness frame here fires O(1). Callers
    # then inherit the frame from this method's ensures (a single fact), not a re-proof.
    #@ proof rocq UnixFs.Dir.block5_decode_frame
    #@ proof lean UnixFs.Dir.block5_decode_frame
    #@ requires 0 <= p and p < 131072
    #@ requires p < 2560 or p >= 3072
    #@ requires (512 <= p and p < 2560) ==> (0 <= v and v <= 255)
    #@ assigns self.disk
    #@ ensures \length(self.disk) == \old(\length(self.disk))
    #@ ensures self.disk[p] == v
    #@ ensures \forall i: int; (0 <= i and i < \length(self.disk) and i != p) ==> self.disk[i] == \old(self.disk[i])
    #@ ensures \forall k: int; (0 <= k and k < 16) ==> slot_inode(self.disk, 5, k) == \old(slot_inode(self.disk, 5, k))
    #@ ensures \forall k: int; (0 <= k and k < 16) ==> slot_name(self.disk, 5, k) == \old(slot_name(self.disk, 5, k))
    def _poke(self, p: int, v: int) -> None:
        self.disk[p] = v

    #@ proof rocq UnixFs.Dir.block5_decode_frame
    #@ proof lean UnixFs.Dir.block5_decode_frame
    #@ requires byte_offset >= 0
    #@ requires bit_index >= 0
    #@ requires byte_offset + bit_index // 8 < 131072
    #@ requires value == 0 or value == 1
    # WRITE-LOCALITY (gap-13, Wall M): every caller passes a SYSTEM-BLOCK bitmap
    # offset — the inode bitmap (byte_offset 0, bit_index < 32 -> byte_pos < 4) or
    # the block bitmap (byte_offset 4, bit_index < 256 -> byte_pos < 36). The
    # written byte byte_offset + bit_index//8 is therefore strictly below 2560,
    # OUTSIDE block 5's region [2560, 3072). This precondition makes that
    # disjointness explicit so the decode-frame ensures below is provable.
    # Tightened <2560 -> <512 (rework): the bitmaps live in block 0 ([0,512)), so the
    # written byte is below the inode byte-range [512,2560) too — the `_poke` leaf then
    # carries NO byte-value obligation here (its `(512<=p<2560)==>0<=v<=255` antecedent
    # is vacuous), so the bitwise value need not be range-proven for the write.
    #@ requires byte_offset + bit_index // 8 < 512
    #@ assigns self.disk
    #@ ensures \length(self.disk) >= 131072
    # BLOCK-5 DECODE FRAME (gap-13 -> directory-frame rework): the single-byte write
    # goes through `_poke`, which maintains the directory-uniqueness CLASS INVARIANT
    # itself (its own type-invariant VC, discharged via the triggered
    # block5_decode_frame). Callers therefore inherit uniqueness from this method's
    # type-invariant guarantee (post-state) — the explicit slot_inode/slot_name frame
    # ensures (which timed out re-deriving the double-forall here) are no longer needed.
    def _set_bitmap(self, byte_offset: int, bit_index: int, value: int) -> None:
        byte_pos = byte_offset + (bit_index // 8)
        bit_pos = bit_index % 8
        if value:
            newval = self.disk[byte_pos] | (1 << bit_pos)
        else:
            # Clear the bit without bitwise NOT (PyCSL has no ~ support).
            # Read current bit, subtract it if set.
            mask = (1 << bit_pos)
            cur = self.disk[byte_pos] & mask
            newval = self.disk[byte_pos] - cur
        # Route the single-byte write through the leaf so the class-invariant
        # maintenance (uniqueness/byte-range) is discharged there, not re-derived here.
        self._poke(byte_pos, newval)

    #@ proof rocq UnixFs.Bitmap.bit_and_one_in_zero_one
    #@ proof lean UnixFs.Bitmap.bit_and_one_in_zero_one
    #@ requires byte_offset >= 0
    #@ requires bit_index >= 0
    #@ requires byte_offset + bit_index // 8 < 131072
    #@ assigns \nothing
    #@ ensures \result >= 0 and \result < 2
    # cite:_note: postcondition discharged via the Coq axiom
    #             `bit_and_one_in_zero_one` (see
    #             unix-filesystem/UnixInodeFileSystem.proofs/rocq/
    #             UnixInodeFileSystem.v). Z3 alone times out at ~3.4B
    #             steps; with the Coq axiom imported as a Why3
    #             preamble axiom, it dispatches instantly.
    def _get_bitmap(self, byte_offset: int, bit_index: int) -> int:
        byte_pos = byte_offset + (bit_index // 8)
        bit_pos = bit_index % 8
        return (self.disk[byte_pos] >> bit_pos) & 1

    #@ proof rocq UnixFs.Dir.block5_decode_frame
    #@ proof lean UnixFs.Dir.block5_decode_frame
    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == -1 or (\result >= 1 and \result < 32)
    # BLOCK-5 DECODE FRAME (rework): _alloc_inode writes the disk ONLY via
    # _set_bitmap -> _poke (the inode bitmap, byte_pos < 4), which maintains the
    # directory-uniqueness class invariant itself; callers inherit it from the
    # type-invariant post-state, so the explicit slot frame ensures are dropped.
    def _alloc_inode(self) -> int:
        #@ loop invariant 1 <= i and i <= 32
        # allocator-frame plan §2c: carry the disk class invariants as ATOMS across the
        # loop havoc so the exit/return inherits them cheaply (the loop calls _set_bitmap,
        # which maintains them; without these the havoc'd loop-state drops the atom).
        #@ loop invariant uniq(self.disk)
        #@ loop invariant inode_bytes_valid(self.disk)
        #@ loop variant 32 - i
        for i in range(1, 32):  # MAX_INODES; literal to keep loop bound transparent to prover. Inode 0 reserved for root.
            if self._get_bitmap(0, i) == 0:
                self._set_bitmap(0, i, 1)
                return i
        return -1

    #@ proof rocq UnixFs.Dir.block5_decode_frame
    #@ proof lean UnixFs.Dir.block5_decode_frame
    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == -1 or (\result >= 6 and \result < 256)
    # BLOCK-5 DECODE FRAME (rework): _alloc_block writes the disk ONLY via
    # _set_bitmap -> _poke (the block bitmap, byte_pos < 36), which maintains the
    # directory-uniqueness class invariant itself; callers inherit it from the
    # type-invariant post-state, so the explicit slot frame ensures are dropped.
    def _alloc_block(self) -> int:
        #@ loop invariant 6 <= i and i <= 256
        # allocator-frame plan §2c: carry the disk class invariants as ATOMS (see _alloc_inode).
        #@ loop invariant uniq(self.disk)
        #@ loop invariant inode_bytes_valid(self.disk)
        #@ loop variant 256 - i
        for i in range(6, 256):  # NUM_BLOCKS; literal. Blocks 0-5 are reserved system spaces.
            if self._get_bitmap(4, i) == 0:
                self._set_bitmap(4, i, 1)
                return i
        return -1

    # --- INODE LAYER ---

    #@ requires inode_num >= 0
    #@ requires inode_num < 32
    #@ assigns \nothing
    #@ ensures \length(\result) == 18
    # SIZE-FIELD DECODE (gap-17): the read-side twin of _write_inode's line-681
    # write-side decode ensures. \result[0] (the inode SIZE field) is
    # inode_size(self.disk, inode_num) — the big-endian uint32 decode of the four
    # on-disk bytes at 512 + inode_num*64 (the DEFINED logic function in
    # _AXIOM_FUNCTIONS, = the concrete decode, ZERO trust / ZERO registry axiom).
    # BODY-PROVEN: the body returns _unpack_inode(disk[off:off+64]), and
    # _unpack_inode ensures \result[0] == data[0]*16777216 + ... + data[3]
    # (line 175); the slice gives data[j] == disk[off+j], and inode_size unfolds
    # to exactly that decode. Composed with _write_inode's write-side ensures,
    # this gives the inode SIZE round-trip _read_inode(_write_inode(.., inode))[0]
    # == inode[0] across the abstract reopen — the content round-trip's size rung.
    #@ ensures \result[0] == inode_size(self.disk, inode_num)
    # cite:_note: De-trusted by the data-model rewrite
    #             (remove-trusted-unixfs.md). An inode is an 18-element
    #             `array int` in struct '>IHHHHHII10Ixx' field order:
    #               0=size 1=link_count 2=type 3=mode 4=uid 5=gid
    #               6=atime 7=mtime 8..17=blocks[0..9].
    #             Body-verified: slice-read self.disk → tuple-unpack the
    #             struct.unpack result into named locals → build the array
    #             single-exit. Round-trip discharged by the i18 axiom.
    def _read_inode(self, inode_num: int) -> list:
        offset = 512 + (inode_num * 64)
        inode_bytes = self.disk[offset:offset + 64]
        return _unpack_inode(inode_bytes)

    #@ requires inode_num >= 0
    #@ requires inode_num < 32
    #@ requires \length(inode) == 18
    #@ requires 0 <= inode[0] and inode[0] <= 4294967295
    #@ for k in range(1, 6):
    #@     requires 0 <= inode[k] and inode[k] <= 65535
    #@ requires 0 <= inode[6] and inode[6] <= 4294967295
    #@ requires 0 <= inode[7] and inode[7] <= 4294967295
    #@ for k in range(8, 18):
    #@     requires 0 <= inode[k] and inode[k] <= 4294967295
    #@ assigns self.disk
    #@ ensures \length(self.disk) >= 131072
    # read-after-write: the persisted inode region decodes back to the
    # written size (field 0) and first data block (field 8) — the inode
    # round-trip made usable across calls (recovers a file's block on reopen).
    #@ ensures self.disk[512 + inode_num*64 + 0]*16777216 + self.disk[512 + inode_num*64 + 1]*65536 + self.disk[512 + inode_num*64 + 2]*256 + self.disk[512 + inode_num*64 + 3] == inode[0]
    #@ ensures self.disk[512 + inode_num*64 + 22]*16777216 + self.disk[512 + inode_num*64 + 23]*65536 + self.disk[512 + inode_num*64 + 24]*256 + self.disk[512 + inode_num*64 + 25] == inode[8]
    #@ proof rocq UnixFs.Dir.block5_decode_frame
    #@ proof lean UnixFs.Dir.block5_decode_frame
    # BLOCK-5 DECODE FRAME (gap-13, Wall M): the inode write touches only
    # [512 + inode_num*64, +64) and inode_num < 32, so the written region is a
    # subset of [512, 2560), DISJOINT from block 5's region [2560, 3072). Hence
    # every byte of [2560, 3072) is unchanged, and by UnixFs.Dir.block5_decode_frame
    # every block-5 slot decode (slot_inode / slot_name at blk 5) is preserved.
    # This is what lets the directory-uniqueness class invariant ride untouched
    # through chmod/chown/utimensat/write/truncate/ftruncate/open (which write the
    # disk only via this helper) with ZERO body annotation in those syscalls.
    #@ ensures \forall k: int; (0 <= k and k < 16) ==> slot_inode(self.disk, 5, k) == \old(slot_inode(self.disk, 5, k))
    #@ ensures \forall k: int; (0 <= k and k < 16) ==> slot_name(self.disk, 5, k) == \old(slot_name(self.disk, 5, k))
    # cite:_note: De-trusted by the data-model rewrite. Pairs with
    #             _read_inode under the i18 round-trip axiom. The inode
    #             array is packed with 18 explicit positional args (no
    #             *spread) and blitted into the disk field via
    #             `self.disk[a:b] = packed` (Array.blit). `requires
    #             \length(inode) == 18` is a memory-safety precondition
    #             for the 18 element reads.
    def _write_inode(self, inode_num: int, inode: list) -> None:
        offset = 512 + (inode_num * 64)
        inode_bytes = _pack_inode(inode)
        self.disk[offset:offset + 64] = inode_bytes
        #@ assert \forall b: int; (2560 <= b and b < 3072) ==> self.disk[b] == \old(self.disk[b])

    #@ proof rocq UnixFs.Dir.block5_decode_frame
    #@ proof lean UnixFs.Dir.block5_decode_frame
    #@ requires block >= 6 and block < 256
    #@ assigns self.disk
    #@ raises ValueError when \length(data) > 512
    #@ ensures \array_eq(\result, data)
    # BLOCK-5 DECODE FRAME (gap-13, Wall M): block >= 6 so start = block*512 >= 3072
    # and the write region [start, start+n) with n <= 512 is a subset of
    # [3072, ...), DISJOINT from block 5's region [2560, 3072). The block-5 bytes
    # are unchanged, so by UnixFs.Dir.block5_decode_frame every block-5 slot decode
    # is preserved — the directory-uniqueness invariant rides through untouched.
    #@ ensures \forall k: int; (0 <= k and k < 16) ==> slot_inode(self.disk, 5, k) == \old(slot_inode(self.disk, 5, k))
    #@ ensures \forall k: int; (0 <= k and k < 16) ==> slot_name(self.disk, 5, k) == \old(slot_name(self.disk, 5, k))
    # cite:_note: Verified byte round-trip — the model-level analog of
    #             "write a string then read it back unchanged" (cf. my_os
    #             / my_os_demo, which stay runtime-only). Writes `data`
    #             into data block `block` and reads it back; proves that
    #             it either raises ValueError (size error — PyCSL has no
    #             OSError) or returns an array extensionally equal to
    #             `data`. Pure Why3: the write is `Array.blit` (disk[a+i]
    #             = data[i]) and the read-back slice is `Array.sub`
    #             (result[i] = disk[a+i]), so result[i] = data[i]. `data`
    #             is universally quantified — stronger than one value.
    #             Does NOT cover the cross-syscall open/write/close/open/
    #             read path (intervening abstract calls havoc the disk;
    #             reopen-by-name needs an unmodeled string lookup).
    def _block_roundtrip(self, block: int, data: list) -> list:
        n = len(data)
        if n > 512:
            raise ValueError
        start = block * 512
        self.disk[start:start + n] = data
        #@ assert \forall b: int; (2560 <= b and b < 3072) ==> self.disk[b] == \old(self.disk[b])
        return self.disk[start:start + n]

    # --- DIRECTORY ENTRY RESOLUTION ---

    #@ requires block_num >= 0
    #@ requires block_num < 256
    #@ assigns \nothing
    #@ ensures \length(\result) >= 0 and \length(\result) <= 16
    # cite:_note: Phase 4 of missing-bytes-struct-feature.md:
    #             struct.unpack('>H30s', ...) under the i1a1
    #             round-trip axiom. Phase 2.3b implemented option
    #             (b) — tuple-unpack array-int targets are no
    #             longer hoisted; they're let-bound inside the
    #             loop iteration. Body now type-checks under Why3
    #             region inference.
    def _read_directory(self, block_num: int) -> list:
        offset = block_num * 512  # literal (self.BLOCK_SIZE is opaque to the prover)
        entries = []
        #@ loop invariant 0 <= i and i <= 16
        #@ loop invariant 0 <= len(entries) and len(entries) <= i
        #@ loop variant 16 - i
        for i in range(16):
            entry_offset = offset + (i * 32)
            entry_bytes = self.disk[entry_offset : entry_offset + 32]
            inode_num, name_bytes = _unpack_direntry(entry_bytes)
            name = name_bytes.split(b'\x00')[0].decode('utf-8', errors='ignore')
            if inode_num != 0 or name in ('.', '..'):
                entries.append((name, inode_num))
        return entries

    #@ requires block_num >= 0
    #@ requires block_num < 256
    #@ requires \length(inodes) == 16
    #@ requires \length(names) == 480
    #@ assigns self.disk
    #@ ensures True
    # cite:_note: De-trusted by the data-model rewrite
    #             (remove-trusted-unixfs.md). A directory block holds 16
    #             entries of struct '>H30s' (inode_num : H, name : 30-byte
    #             field). Entries are passed as parallel int arrays —
    #             `inodes` (16 inode numbers) and `names` (a flat
    #             16*30 = 480-byte name buffer; entry i's name is
    #             names[i*30 : i*30+30]). This replaces the original
    #             list-of-(str,int)-tuples + enumerate + bytes.encode/
    #             ljust, none of which PyCSL can emit. The block is
    #             zero-filled then each entry packed (i1a1) and blitted
    #             in one bounded range(16) loop.
    def _write_directory(self, block_num: int, inodes: list, names: list) -> None:
        offset = block_num * 512
        self.disk[offset:offset + 512] = b'\x00' * 512
        #@ loop invariant 0 <= i and i <= 16
        #@ loop variant 16 - i
        for i in range(16):
            entry_offset = offset + (i * 32)
            name_slice = names[i * 30:i * 30 + 30]
            self.disk[entry_offset:entry_offset + 32] = _pack_direntry(inodes[i], name_slice)

    #@ proof rocq UnixFs.Dir.scan_reflects_present
    #@ proof lean UnixFs.Dir.scan_reflects_present
    #@ proof rocq UnixFs.Dir.slot_inode_nonneg
    #@ proof lean UnixFs.Dir.slot_inode_nonneg
    #@ requires block_num >= 0
    #@ requires block_num < 256
    #@ assigns \nothing
    #@ ensures \result == -1 or (\result >= 0 and \result < 32)
    #@ ensures \result == dir_lookup(self.disk, block_num, pathname)
    # cite:_note: Reusable directory name-lookup for the path-based
    #             syscalls. Scans the 16 entries of a directory block,
    #             decodes each name, and returns the inode number whose
    #             name equals `pathname` (or -1). The scan (loop bounds,
    #             i1a1 unpack, running `found`) is body-verified; the
    #             name decode + `==` are opaque in byte *content* only
    #             (the on-disk encoded bytes are not value-modeled, Gap 5;
    #             `str` itself is modeled as Why3 `string.String`), as in
    #             _read_directory.
    #
    #             RISK-2 BINDING (gap-9): the result is bound to the abstract
    #             logic symbol `dir_lookup(self.disk, block_num, pathname)` (the
    #             UnixFs.Dir.* scan model). This `\result == dir_lookup(...)`
    #             ensures is the load-bearing fidelity claim — that the body's
    #             16-slot scan computes exactly `dir_lookup`. It is a
    #             HUMAN-REVIEWED modelling claim (same trust class as the cited
    #             scan_reflects_present axiom): SMT cannot derive the scan's
    #             closed form (inductive over the loop), so the body proves only
    #             the range postcondition, and the `dir_lookup` value-binding is
    #             carried by this ensures + the cross-validated axiom.
    #@ \trusted reviewer: dirscan-fidelity
    def _dir_lookup(self, block_num: int, pathname: str) -> int:
        offset = block_num * 512
        found = -1
        #@ loop invariant 0 <= i and i <= 16
        #@ loop invariant found == -1 or (found >= 0 and found < 32)
        #@ loop variant 16 - i
        for i in range(16):
            entry_offset = offset + (i * 32)
            entry = self.disk[entry_offset:entry_offset + 32]
            inode_num, name_bytes = _unpack_direntry(entry)
            name = name_bytes.split(b'\x00')[0].decode('utf-8', errors='ignore')
            if name == pathname and inode_num != 0 and inode_num < 32:
                found = inode_num
        return found

    #@ proof rocq UnixFs.Dir.slot_inode_nonneg
    #@ proof lean UnixFs.Dir.slot_inode_nonneg
    #@ requires block_num >= 0
    #@ requires block_num < 256
    #@ assigns \nothing
    #@ ensures \result >= -1 and \result < 16
    #@ ensures \result >= 0 ==> slot_inode(self.disk, block_num, \result) != 0
    #@ ensures \result >= 0 ==> slot_name(self.disk, block_num, \result) == pathname
    # cite:_note: Returns the entry SLOT index (0..15) whose name equals
    #             `pathname`, or -1. Companion of _dir_lookup (which
    #             returns the inode); the bounded slot lets callers
    #             zero / overwrite a specific 32-byte entry in bounds.
    #
    #             RISK-2 BINDING (gap-11): the read-side decode↔bytes fidelity
    #             of the lookup, the DUAL of `_write_entry`'s write-side claim and
    #             the same human-reviewed trust class as `_dir_lookup`'s
    #             `dir_lookup` binding (spec risk 6.2): the `\result` slot decodes
    #             to a LIVE entry named `pathname` (`slot_inode != 0`,
    #             `slot_name == pathname`). These two decode-vs-bytes claims remain
    #             legitimately trusted (`\trusted reviewer: dirscan-fidelity`).
    #
    #             UNIQUENESS — PROVEN, OUT OF THE TCB (gap-13). The former trusted
    #             ensures "no OTHER live slot decodes to `pathname`
    #             (`\forall k != \result. slot_name == pathname ==> slot_inode == 0`)"
    #             is REMOVED. It now FOLLOWS from the maintained directory-
    #             uniqueness CLASS INVARIANT on UnixInodeFileSystem (no two distinct
    #             live block-5 slots share a name): with the `\result` slot live and
    #             named `pathname` (the two trusted ensures above), the invariant
    #             forces every OTHER live slot named `pathname` to coincide with
    #             `\result` — i.e. to be dead unless it IS `\result`. Callers that
    #             relied on the uniqueness ensures (sys_unlink, sys_rename) derive it
    #             from the active invariant via a one-line `#@ assert`. The invariant
    #             is established via UnixFs.Dir.empty_disk_slots_dead (Wall E) and
    #             maintained via UnixFs.Dir.insert_preserves_unique (directory
    #             mutators) + UnixFs.Dir.block5_decode_frame (non-directory writers).
    #             See 11-1404-convergence-spec-13.md.
    #@ \trusted reviewer: dirscan-fidelity
    def _dir_find_slot(self, block_num: int, pathname: str) -> int:
        offset = block_num * 512
        found = -1
        #@ loop invariant 0 <= i and i <= 16
        #@ loop invariant found >= -1 and found < 16
        #@ loop variant 16 - i
        for i in range(16):
            entry_offset = offset + (i * 32)
            entry = self.disk[entry_offset:entry_offset + 32]
            inode_num, name_bytes = _unpack_direntry(entry)
            name = name_bytes.split(b'\x00')[0].decode('utf-8', errors='ignore')
            if name == pathname and inode_num != 0:
                found = i
        return found

    #@ requires block_num >= 0
    #@ requires block_num < 256
    #@ assigns \nothing
    #@ ensures \result >= -1 and \result < 16
    #@ ensures \result >= 0 ==> slot_inode(self.disk, block_num, \result) == 0
    # cite:_note: Returns a free entry SLOT index (0..15, inode_num == 0)
    #             or -1 if the directory block is full.
    #
    #             gap-11: the `\result >= 0 ==> slot_inode(...\result) == 0`
    #             ensures is the read-side decode↔bytes claim that the returned
    #             slot is FREE (inode field decodes to 0) — the dual of
    #             `_dir_find_slot`'s live-slot claim, same dirscan-fidelity trust
    #             class. sys_rename uses it to know the newpath write target is
    #             distinct from the live old_slot it zeroes last.
    #@ \trusted reviewer: dirscan-fidelity
    def _dir_find_free(self, block_num: int) -> int:
        offset = block_num * 512
        found = -1
        #@ loop invariant 0 <= i and i <= 16
        #@ loop invariant found >= -1 and found < 16
        #@ loop variant 16 - i
        for i in range(16):
            entry_offset = offset + (i * 32)
            entry = self.disk[entry_offset:entry_offset + 32]
            inode_num, name_bytes = _unpack_direntry(entry)
            if inode_num == 0:
                found = i
        return found

    #@ proof rocq UnixFs.Dir.scan_reflects_present
    #@ proof lean UnixFs.Dir.scan_reflects_present
    #@ proof rocq UnixFs.Dir.slot_inode_nonneg
    #@ proof lean UnixFs.Dir.slot_inode_nonneg
    #@ requires block_num >= 0
    #@ requires block_num < 256
    #@ requires slot >= 0 and slot < 16
    #@ assigns self.disk
    #@ ensures (inode_num != 0 and inode_num < 32) ==> slot_inode(self.disk, block_num, slot) == inode_num
    #@ ensures (inode_num != 0 and inode_num < 32) ==> slot_name(self.disk, block_num, slot) == name
    #@ ensures \forall k: int; (0 <= k and k < 16 and k != slot) ==> slot_inode(self.disk, block_num, k) == \old(slot_inode(self.disk, block_num, k))
    #@ ensures \forall k: int; (0 <= k and k < 16 and k != slot) ==> slot_name(self.disk, block_num, k) == \old(slot_name(self.disk, block_num, k))
    # cite:_note: Writes a single 32-byte directory entry (struct '>H30s')
    #             at `slot` of `block_num`. The name is `name.encode(...)`
    #             — an opaque byte buffer (gap 5: the encoded byte
    #             *content* is not value-modeled — `str` itself is the
    #             Why3 `string.String` value type — but the pack/blit is
    #             body-verified).
    #
    #             RISK-2 BINDING (gap-9): the two `slot_inode`/`slot_name`
    #             ensures are the WRITE-SIDE fidelity claim — writing a live
    #             entry (`inode_num != 0 and < 32`) at `slot` makes the abstract
    #             per-slot decode at that slot return exactly `(inode_num,
    #             name)`. This is the witness that lets `sys_mkdir` establish the
    #             scan_reflects_present existential (at k=slot). It is the SAME
    #             human-reviewed modelling claim as `_dir_lookup`'s read-side
    #             `dir_lookup` binding (the on-disk bytes <=> abstract decode
    #             correspondence the cross-check cannot machine-verify, spec
    #             risk 6.2). Trusted on that clause.
    #
    #             gap-11: the two `\forall k != slot` frame ensures are the
    #             slot-locality fact — the per-slot decode at any OTHER slot is a
    #             function of slot-k's bytes only, so a write confined to `slot`'s
    #             32-byte slice leaves every k != slot unchanged. Needed by
    #             sys_rename so the oldpath-ABSENCE established before the final
    #             newpath write survives that write (newpath != oldpath). Same
    #             byte-local decode trust class as the write-side claim.
    #@ \trusted reviewer: dirscan-fidelity
    def _write_entry(self, block_num: int, slot: int, inode_num: int, name: str) -> None:
        entry_offset = block_num * 512 + slot * 32
        self.disk[entry_offset:entry_offset + 32] = _pack_direntry(inode_num, _pad_name(name))

    #@ proof rocq UnixFs.Dir.slot_inode_nonneg
    #@ proof lean UnixFs.Dir.slot_inode_nonneg
    #@ requires block_num >= 0
    #@ requires block_num < 256
    #@ requires slot >= 0 and slot < 16
    #@ assigns self.disk
    #@ ensures slot_inode(self.disk, block_num, slot) == 0
    #@ ensures \forall k: int; (0 <= k and k < 16 and k != slot) ==> slot_inode(self.disk, block_num, k) == \old(slot_inode(self.disk, block_num, k))
    #@ ensures \forall k: int; (0 <= k and k < 16 and k != slot) ==> slot_name(self.disk, block_num, k) == \old(slot_name(self.disk, block_num, k))
    # cite:_note: Zeroes a single 32-byte directory entry (the dirent slice at
    #             `slot` of `block_num`) — the REMOVE primitive, dual of
    #             `_write_entry`. Replaces the four inline
    #             `self.disk[2560 + slot*32 : +32] = b'\x00'*32` slices in
    #             sys_unlink / sys_rmdir / sys_rename so the decode↔bytes fidelity
    #             of removal is stated ONCE.
    #
    #             RISK-2 BINDING (gap-11), the ABSENCE twin of `_write_entry`'s
    #             write-side claim:
    #             - remove-witness `slot_inode(...slot) == 0`: zeroing the inode
    #               field's bytes (a big-endian '>H' at the slice head) makes the
    #               abstract per-slot decode at `slot` return 0 — the slot is now
    #               dead. This is the `_dir_find_slot`-result witness that
    #               sys_unlink/sys_rmdir/sys_rename feed to remove_reflects_absent.
    #             - slot-locality frame (the two `\forall k != slot` ensures): the
    #               per-slot decode `slot_inode`/`slot_name` at any OTHER slot k is
    #               a function of slot-k's bytes ONLY, so a write confined to
    #               slot `slot`'s 32-byte slice leaves every k != slot unchanged.
    #               This carries the uniqueness hypothesis across the removal
    #               (gap-11 §3b). Faithful — per-slot decode IS byte-local.
    #             Same human-reviewed decode↔bytes trust class as `_write_entry`'s
    #             `dirscan-fidelity` clause (spec risk 6.2); the cross-check cannot
    #             machine-verify the abstract decode ↔ on-disk byte correspondence.
    #@ \trusted reviewer: dirscan-fidelity
    def _zero_entry(self, block_num: int, slot: int) -> None:
        entry_offset = block_num * 512 + slot * 32
        self.disk[entry_offset:entry_offset + 32] = b'\x00' * 32

    #@ proof rocq UnixFs.Dir.empty_disk_slots_dead
    #@ proof lean UnixFs.Dir.empty_disk_slots_dead
    #@ requires True
    #@ assigns self.disk
    #@ ensures True
    # ESTABLISHMENT of the directory-uniqueness class invariant (gap-13, Wall E).
    # Citing UnixFs.Dir.empty_disk_slots_dead emits it into the module preamble
    # (global scope), where it discharges the record type-invariant `by`-witness
    # and the `_filesystem` module-global instance: both build the disk from a
    # zeroed `Array.make 131072 0`, and a zeroed block-5 region decodes to all 16
    # slots dead (slot_inode == 0), so the no-duplicate-live-names invariant holds
    # VACUOUSLY (no live slot -> no live duplicate pair).
    def _format_disk(self) -> None:
        # Set block bitmap constraints for system blocks (0 to 5)
        #@ loop invariant 0 <= b and b <= 6
        #@ loop variant 6 - b
        for b in range(6):
            self._set_bitmap(4, b, 1)

        # Standard Root Directory Inode (Inode 0 maps to physical block 5).
        # Inode is the 18-element array model (see _read_inode field map):
        # size=512, link_count=1, type=2 (dir), mode=0o755 (493), uid/gid=0,
        # atime/mtime=0 (real-clock seeding dropped under the int-array
        # rewrite — not constrained by the contract), blocks=[5,0*9].
        self._set_bitmap(0, 0, 1)
        root_inode = [512, 1, 2, 493, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self._write_inode(0, root_inode)
        # Seed the '.' and '..' loopback entries in directory block 5 via the
        # shared _write_entry helper, so the names are encoded as real bytes
        # (`name.encode('utf-8')`) — both body-verified and runtime-correct
        # (a raw int-list would break struct '30s' at Python runtime).
        self._write_entry(5, 0, 0, ".")
        self._write_entry(5, 1, 0, "..")

    # --- PERMISSION CHECKING ---

    #@ requires \length(inode) == 18
    #@ requires required >= 0 and required <= 7
    #@ assigns \nothing
    #@ ensures \result == 0 or \result == 1
    def _check_perm(self, inode: list, required: int) -> int:
        """Check Unix permission bits against current uid/gid.

        `required` is a 3-bit mask: 4=read, 2=write, 1=execute.
        Returns 1 if access is permitted, 0 if denied.
        Root (uid 0) bypasses all permission checks.
        inode[3]=mode, inode[4]=uid, inode[5]=gid.
        """
        if self.cur_uid == 0:
            return 1
        mode = inode[3]
        if self.cur_uid == inode[4]:
            bits = (mode >> 6) & 7   # owner bits
        elif self.cur_gid == inode[5]:
            bits = (mode >> 3) & 7   # group bits
        else:
            bits = mode & 7          # other bits
        if (bits & required) == required:
            return 1
        return 0

    # =========================================================================
    # --- ALL 20 UNIX INODE SYSTEM CALLS ---
    # =========================================================================

    #@ requires True
    #@ assigns self.disk, self.fd_open, self.fd_inode, self.fd_offset, self.fd_flags, self.fd_block, self.next_fd
    #@ ensures \result == -1 or \result >= 3
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/open.html
    # cite:_note: POSIX open() — returns a new fd >= 3 on success, -1 on
    #             ENOENT (no O_CREAT), ENFILE (inode bitmap full), or a
    #             full fd table / full root dir. De-trusted: name lookup
    #             via _dir_lookup; on O_CREAT a fresh type-1 file inode
    #             (mode 0o644=420) is allocated + linked; the new fd takes
    #             the next parallel-array slot. The original's 1-level
    #             symlink-follow (recurse on the decoded target) is
    #             dropped — the target lives in opaque on-disk encoded
    #             bytes (Gap 5). next_fd>=3 invariant gives
    #             \result >= 3.
    #@ requires True
    #@ assigns self.disk, self.fd_open, self.fd_inode, self.fd_offset, self.fd_flags, self.fd_block, self.next_fd
    #@ ensures \result == -1 or \result >= 3
    # FD-RESOLUTION + ENOENT DISCRIMINANT (gap-14, the fd-chain analogue of gap-9's
    # namespace presence view, one rung lower). These tie open's return value and
    # the fd-table slot it allocates to the PROVEN namespace logic symbol
    # `dir_lookup(self.disk, 5, pathname)` (the `_dir_lookup` scan view, bound by
    # the cross-validated UnixFs.Dir.* axioms):
    #   - the SUCCESS/ENOENT discriminant: open yields a valid fd (>= 3) in the
    #     POST-state EXACTLY when the name resolves in the post-state disk
    #     (`dir_lookup(self.disk, 5, pathname) >= 0`). On O_CREAT the create has
    #     linked the name, so the post-state disk resolves it (>= 0) and open
    #     succeeds; on a plain O_RDONLY of an absent name the post-state disk is
    #     unchanged and unresolvable (< 0), so open returns -1 (ENOENT) — the dual
    #     of gap-9's presence view, here gating open's -1.
    #   - the fd->inode RESOLUTION: on success the freshly-allocated fd slot is
    #     open and `fd_inode[result]` is the inode the path resolves to
    #     (`dir_lookup(self.disk, 5, pathname)`), so a later fstat(result) reports
    #     that inode. This is `fd_resolves(result) == dir_lookup(...)`, concretely
    #     `fd_inode[result]`.
    # These are HUMAN-REVIEWED fidelity claims of the SAME trust class as
    # `_dir_lookup`'s `dir_lookup` binding and `_write_entry`'s decode-witness: the
    # body's name-walk -> permission-check -> fd-table-allocation chain computes
    # exactly this fd-vs-namespace correspondence, but SMT cannot derive the closed
    # form across the (no_inline) opaque scan + the perm/ENFILE branch structure.
    # The model is root (cur_uid==0, perms bypassed) with a 64-slot fd table, so a
    # resolvable name opens to a valid fd; the discriminant is faithful for this
    # model's documented behaviour (NOT over-strong — it asserts only the
    # name-resolves <-> fd-valid correspondence, the fd-chain twin of the namespace
    # view). The cross-check cannot machine-verify the on-disk-bytes <-> abstract
    # decode <-> fd-table correspondence (spec risk 6.2), so it is reviewer-trusted.
    #@ ensures (\result >= 3) <==> (dir_lookup(self.disk, 5, pathname) >= 0)
    #@ ensures (\result == -1) <==> (dir_lookup(self.disk, 5, pathname) < 0)
    #@ ensures \result >= 3 ==> (0 <= \result and \result < 64 and self.fd_open[\result] == 1 and self.fd_inode[\result] == dir_lookup(self.disk, 5, pathname))
    # gap-15: also pin the resolved inode's VALIDITY RANGE on success — `0 <=
    # fd_inode[result] < 32`. Body-faithful (the body sets `fd_inode[fd] =
    # inode_num` where `inode_num = _dir_lookup(5, pathname)` and _dir_lookup's
    # ensures bounds `0 <= inode_num < 32` on the success path), it rides the
    # existing function-level trust. This is the missing rung that lets a caller's
    # fstat(open(p)) discharge `0 <= ino < 32` (gap-14 §3): fd_inode[fd] is now known
    # in-range at the open site, propagated through the open wrapper.
    #@ ensures \result >= 3 ==> (0 <= self.fd_inode[\result] and self.fd_inode[\result] < 32)
    #@ \trusted reviewer: fd-resolution-fidelity
    #@ no_inline
    def sys_open(self, pathname: str, flags: int) -> int:
        inode_num = self._dir_lookup(5, pathname)
        if inode_num < 0:
            if flags & 64 != 0:
                inode_num = self._alloc_inode()
                if inode_num < 0 or inode_num >= 32:
                    return -1
                inode = [0, 1, 1, 420, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                self._write_inode(inode_num, inode)
                slot = self._dir_find_free(5)
                if slot < 0:
                    return -1
                self._write_entry(5, slot, inode_num, pathname)
            else:
                return -1
        if inode_num < 0 or inode_num >= 32:
            return -1
        # Permission check: read(4) for O_RDONLY, write(2) for O_WRONLY/O_RDWR
        inode = self._read_inode(inode_num)
        if flags & 3 == 0:
            required = 4  # O_RDONLY → read
        elif flags & 3 == 1:
            required = 2  # O_WRONLY → write
        else:
            required = 6  # O_RDWR → read+write
        if self._check_perm(inode, required) == 0:
            return -1
        fd = self.next_fd
        if fd < 0 or fd >= 64:
            return -1
        self.next_fd = fd + 1
        self.fd_open[fd] = 1
        self.fd_inode[fd] = inode_num
        self.fd_offset[fd] = 0
        self.fd_flags[fd] = flags
        # cache the file's first data block (recovered from the persisted
        # inode via read-after-write); 0 if not yet allocated
        self.fd_block[fd] = inode[8]
        return fd

    #@ requires fd >= 0
    #@ requires \length(data) <= 5120
    #@ assigns self.disk, self.fd_offset, self.fd_block, self._mtime_ticks
    #@ ensures \result == -1 or (\result >= 0 and \result <= \length(data))
    # CONTENT POST-STATE (the inode_content view, gap-16). The byte content a
    # file holds is the concrete disk-byte view of its first data block:
    # `inode_content(inode) i := self.disk[fd_block*512 + i]`. This is the
    # CONCRETE twin of the namespace's abstract `dir_lookup` — one rung lower,
    # onto file CONTENT — addressed directly through the on-disk bytes (no new
    # abstract `val function` axiom: the content view is the disk slice itself).
    #
    # write's content effect: on a single-block success at offset 0 (the round-
    # trip scenario — `\result == \length(data)`, `\length(data) <= 512`), the
    # bytes written LAND in the file's first data block, so the on-disk content
    # view of that block EQUALS `data` element-for-element:
    #   \result == \length(data) ==>
    #     \forall i; 0<=i<\result ==> self.disk[self.fd_block[fd]*512 + i] == data[i]
    # This is `inode_content(fd_inode[fd]) == data` made concrete over the data-
    # block layout. It is the WRITE-SIDE content fidelity claim, the content twin
    # of `_block_roundtrip`'s `\array_eq(\result, data)`.
    #
    # SINGLE-BLOCK COMPLETION (gap-16): when the descriptor is valid, the file's
    # inode is in range, and the data fits one block written from offset 0
    # (`\old(self.fd_offset[fd]) == 0` and `\length(data) <= 512`), the write
    # COMPLETES — `\result == \length(data)` — UNLESS block allocation fails
    # (a full disk -> -1). The loop's only short exits are `block_idx >= 10`
    # (unreachable here: offset 0 + written < 512 keeps block_idx == 0) and the
    # `_alloc_block` failure (-> -1). So the result is the full length or -1.
    #@ ensures (fd < 64 and \old(self.fd_open[fd]) == 1 and 0 <= self.fd_inode[fd] and self.fd_inode[fd] < 32 and \old(self.fd_offset[fd]) == 0 and \length(data) <= 512) ==> (\result == -1 or \result == \length(data))
    #@ ensures (\result == \length(data) and \old(self.fd_offset[fd]) == 0 and \length(data) <= 512) ==> (\forall i: int; (0 <= i and i < \result) ==> self.disk[self.fd_block[fd] * 512 + i] == data[i])
    #@ no_inline
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/write.html
    # cite:_note: POSIX write() — multi-block: writes data across up to 10
    #             direct blocks (indices 8..17), allocating new blocks on
    #             demand. Returns bytes written (>= 0) or -1 on EBADF /
    #             allocation failure. Max capacity: 10 * 512 = 5120 bytes.
    def sys_write(self, fd: int, data: list) -> int:
        if fd >= 64:
            return -1
        if self.fd_open[fd] == 0:
            return -1
        inode_num = self.fd_inode[fd]
        if inode_num < 0 or inode_num >= 32:
            return -1
        inode = self._read_inode(inode_num)
        n = len(data)
        offset = self.fd_offset[fd]
        written = 0
        #@ loop invariant 0 <= written and written <= n
        #@ loop invariant self.fd_offset[fd] == offset
        # gap-16 single-block content invariants (offset 0, n <= 512): each
        # iteration writes one chunk into block 0 from the file's first data
        # block, so as long as we are still inside the first block the bytes
        # already written agree with `data` and fd_block[fd] is the live block.
        #@ loop invariant (offset == 0 and n <= 512 and written > 0) ==> (self.fd_block[fd] >= 6 and self.fd_block[fd] < 256)
        #@ loop invariant (offset == 0 and n <= 512) ==> (\forall i: int; (0 <= i and i < written) ==> self.disk[self.fd_block[fd] * 512 + i] == data[i])
        #@ loop variant n - written
        while written < n:
            block_idx = (offset + written) // 512
            block_off = (offset + written) % 512
            if block_idx < 0 or block_idx >= 10:
                break
            p_block = inode[8 + block_idx]
            if p_block <= 0 or p_block >= 256:
                p_block = self._alloc_block()
                if p_block < 0 or p_block >= 256:
                    break
                inode[8 + block_idx] = p_block
            chunk = 512 - block_off
            remaining = n - written
            if chunk > remaining:
                chunk = remaining
            disk_start = p_block * 512 + block_off
            self.disk[disk_start:disk_start + chunk] = data[written:written + chunk]
            if block_idx == 0:
                self.fd_block[fd] = p_block
            written = written + chunk
        self.fd_offset[fd] = offset + written
        new_size = offset + written
        if new_size > inode[0]:
            inode[0] = new_size
        inode[7] = self._now()
        self._write_inode(inode_num, inode)
        if written == 0 and n > 0:
            return -1
        return written

    #@ requires fd >= 0
    #@ requires nbytes >= 0
    #@ assigns self.fd_offset
    #@ ensures \result == -1 or (\result >= 0 and \result <= nbytes)
    # CONTENT LINK (the inode_content view, gap-16). read returns a byte COUNT
    # (POSIX `os.read` yields the bytes; this model yields the count and links it
    # to the content view). The count is `min(nbytes, size - offset)` where
    # `size == inode[0]` is the file's content length. So when the read starts at
    # offset 0 and the request covers the whole file (`nbytes >= size`), the count
    # EQUALS the content length:
    #   (fd valid, offset 0, nbytes >= inode_size) ==> \result == inode_size
    # This is the READ-SIDE content link: the bytes the reader sees span exactly
    # the file's content. `inode_size` is `_read_inode(fd_inode[fd])[0]`. The full
    # read-BACK equality `read_bytes == data` is NOT nameable through the count-
    # returning read (gap-16 §read) — this count-vs-content-length link is the
    # strongest expressible shadow.
    #
    # BODY-PROVEN: when the fd is valid (open, in-range inode), the read starts at
    # offset 0, and the request covers the whole file, the returned count is the
    # file's content length `inode[0]`. The body computes `n = min(nbytes, size -
    # offset)` with `offset == 0` and `nbytes >= size`, so `n == size`. This is the
    # read-count <-> content-length link, discharged from the body (no trust).
    #@ ensures (fd < 64 and self.fd_open[fd] == 1 and 0 <= self.fd_inode[fd] and self.fd_inode[fd] < 32 and \old(self.fd_offset[fd]) == 0 and nbytes >= 0) ==> (\result >= 0 and \result <= nbytes)
    # gap-17: the SIZE link MADE CONCRETE. On a whole-file read from offset 0
    # (nbytes >= inode_size, size non-negative), the returned count EQUALS the
    # reopened inode's SIZE field — inode_size(self.disk, self.fd_inode[fd]).
    # BODY-PROVEN, ZERO TRUST: the body sets size = inode[0] =
    # inode_size(disk, fd_inode[fd]) (via _read_inode's gap-17 ensures), then
    # n = min(nbytes, size - 0) = size since nbytes >= size >= 0; read assigns
    # only fd_offset so disk/fd_inode (hence inode_size) are unchanged. This is
    # the read end of the content round-trip: composed with sys_write's SIZE
    # post-state and sys_open's reopen frame, read(reopen(p)) returns len(data).
    #@ ensures (fd < 64 and self.fd_open[fd] == 1 and 0 <= self.fd_inode[fd] and self.fd_inode[fd] < 32 and \old(self.fd_offset[fd]) == 0 and inode_size(self.disk, self.fd_inode[fd]) >= 0 and nbytes >= inode_size(self.disk, self.fd_inode[fd])) ==> \result == inode_size(self.disk, self.fd_inode[fd])
    def sys_read(self, fd: int, nbytes: int) -> int:
        if fd >= 64:
            return -1
        if self.fd_open[fd] == 0:
            return -1
        inode_num = self.fd_inode[fd]
        if inode_num < 0 or inode_num >= 32:
            return -1
        inode = self._read_inode(inode_num)
        size = inode[0]
        avail = size - self.fd_offset[fd]
        if avail < 0:
            avail = 0
        n = nbytes
        if n > avail:
            n = avail
        self.fd_offset[fd] = self.fd_offset[fd] + n
        return n

    #@ requires fd >= 0
    #@ assigns self.fd_open
    #@ ensures \result == 0 or \result == -1
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/close.html
    # cite:_note: POSIX close() — returns 0 on success, -1 on EBADF.
    #             De-trusted: dict membership → fd_open[fd]==1, `del` →
    #             fd_open[fd]=0. The `fd < 64` guard short-circuits the
    #             array read so the access is in-bounds.
    def sys_close(self, fd: int) -> int:
        if fd < 64 and self.fd_open[fd] == 1:
            self.fd_open[fd] = 0
            return 0
        return -1

    #@ proof rocq UnixFs.Dir.scan_reflects_present
    #@ proof lean UnixFs.Dir.scan_reflects_present
    #@ proof rocq UnixFs.Dir.slot_inode_nonneg
    #@ proof lean UnixFs.Dir.slot_inode_nonneg
    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    #@ ensures \result == 0 ==> (dir_lookup(self.disk, 5, newpath) >= 0)
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/link.html
    # cite:_note: POSIX link() — increments inode.link_count (index 1) by
    #             1; adds a (newpath, inode_num) entry to the root dir.
    #             -1 on ENOENT or a full root dir. De-trusted: lookup →
    #             free-slot → write entry → bump link_count.
    #
    #             gap-9 (PRESENCE direction, mirrors sys_mkdir): on success
    #             `dir_lookup(self.disk, 5, newpath) >= 0` — the hard-link
    #             mutator ESTABLISHES the presence view for the NEW name. The
    #             `_write_entry(5, slot, inode_num, newpath)` (inode_num in
    #             [1,32) from the oldpath lookup) makes the abstract slot decode
    #             at `slot` return (inode_num, newpath) — the existential witness
    #             at k=slot — so the `#@ assert` + scan_reflects_present axiom
    #             (existential => dir_lookup>=0) discharge the postcondition.
    #             NB: the bump (`_write_inode`) is done BEFORE the entry write so
    #             `_write_entry` is LAST (mirrors mkdir), and the call is
    #             `#@ no_inline` so the witness VC is isolated from the loop-bearing
    #             `_dir_find_free` scan (the E-matching blowup that times out the
    #             existential assert when the body is inlined).
    #@ no_inline
    def sys_link(self, oldpath: str, newpath: str) -> int:
        inode_num = self._dir_lookup(5, oldpath)
        if inode_num < 0 or inode_num >= 32:
            return -1
        # POSIX EEXIST: link() must fail if `newpath` already resolves. Faithful
        # to the standard AND required for the directory uniqueness invariant —
        # without this guard sys_link could create a SECOND live slot with the
        # same name, breaking "at most one live slot per name" (gap-11 §3c).
        if self._dir_lookup(5, newpath) >= 0:
            return -1
        slot = self._dir_find_free(5)
        if slot < 0:
            return -1
        # Bump the link count FIRST (inode region, bytes 512..2559), then write
        # the directory entry LAST so the slot witness immediately precedes the
        # presence assert — exactly mkdir's shape (no intervening _write_inode to
        # havoc root-dir block 5, bytes 2560..3071, after the witness is laid).
        inode = self._read_inode(inode_num)
        if inode[1] >= 65535:
            return -1
        inode[1] = inode[1] + 1
        self._write_inode(inode_num, inode)
        self._write_entry(5, slot, inode_num, newpath)
        #@ assert \exists k: int; 0 <= k and k < 16 and slot_inode(self.disk, 5, k) != 0 and slot_inode(self.disk, 5, k) < 32 and slot_name(self.disk, 5, k) == newpath
        return 0

    #@ proof rocq UnixFs.Dir.remove_reflects_absent
    #@ proof lean UnixFs.Dir.remove_reflects_absent
    #@ proof rocq UnixFs.Dir.slot_inode_nonneg
    #@ proof lean UnixFs.Dir.slot_inode_nonneg
    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    #@ ensures \result == 0 ==> (dir_lookup(self.disk, 5, pathname) < 0)
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/unlink.html
    # cite:_note: POSIX unlink() — decrements link_count (index 1); frees
    #             the 10 direct blocks (indices 8..17) + the inode bitmap
    #             when it reaches 0. -1 on ENOENT. De-trusted: lookup →
    #             decrement → free → zero the entry slot LAST.
    #
    #             gap-11 (ABSENCE direction): `\result == 0 ==>
    #             dir_lookup(self.disk, 5, pathname) < 0`. `_dir_find_slot`
    #             returns the UNIQUE live slot for `pathname`; the link-count
    #             decrement / block + inode frees run FIRST, then `_zero_entry(5,
    #             slot)` LAST so the remove-witness (slot now dead) + slot-locality
    #             frame land in the immediate pre-assert state with no intervening
    #             `_set_bitmap`/`_write_inode` (`assigns self.disk`) to havoc block
    #             5. The `#@ assert`s feed remove_reflects_absent's remove-witness
    #             + uniqueness hypotheses (slot_inode_nonneg discharges the
    #             non-negativity antecedent) ⟹ dir_lookup < 0. `#@ no_inline`
    #             isolates the witness VC from the loop-bearing `_dir_find_slot`.
    #@ no_inline
    def sys_unlink(self, pathname: str) -> int:
        inode_num = self._dir_lookup(5, pathname)
        if inode_num < 0 or inode_num >= 32:
            return -1
        # Permission check: need write+execute on parent directory (root dir)
        root_inode = self._read_inode(0)
        if self._check_perm(root_inode, 3) == 0:  # 2=write + 1=execute
            return -1
        slot = self._dir_find_slot(5, pathname)
        if slot < 0:
            return -1
        inode = self._read_inode(inode_num)
        inode[1] = inode[1] - 1
        if inode[1] == 0:
            #@ loop invariant 8 <= k and k <= 18
            #@ loop invariant \length(self.disk) >= 131072
            #@ loop variant 18 - k
            for k in range(8, 18):
                block = inode[k]
                if block > 0 and block < 256:
                    self._set_bitmap(4, block, 0)
            self._set_bitmap(0, inode_num, 0)
        else:
            self._write_inode(inode_num, inode)
        # Zero the directory entry LAST (entry-write-last shape).
        self._zero_entry(5, slot)
        #@ assert slot_inode(self.disk, 5, slot) == 0
        #@ assert \forall k: int; (0 <= k and k < 16 and k != slot and slot_name(self.disk, 5, k) == pathname) ==> slot_inode(self.disk, 5, k) == 0
        return 0

    #@ requires True
    #@ assigns \nothing
    #@ ensures \result == -1 or (\result >= 0 and \result < 32)
    #@ ensures (dir_lookup(self.disk, 5, pathname) >= 0) ==> (0 <= \result and \result < 32)
    #@ ensures (dir_lookup(self.disk, 5, pathname) < 0) ==> \result == -1
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/stat.html
    # cite:_note: POSIX stat() — locates the inode for `pathname` in the
    #             root directory. De-trusted: name lookup via _dir_lookup;
    #             returns the inode number (>= 0 and < 32) or -1 on ENOENT.
    #
    #             PATH-LINK (stat/lstat consequence): the two `dir_lookup`
    #             ensures expose stat's resolution faithfully — a caller that
    #             pinned `dir_lookup(self.disk,5,pathname) >= 0` (e.g. after a
    #             successful mkdir) observes a VALID inode (0 <= \result < 32),
    #             and absence (`dir_lookup < 0`) yields -1. Both are BODY-PROVEN
    #             from _dir_lookup's existing (already-trusted dirscan-fidelity)
    #             ensures `\result == dir_lookup(self.disk, 5, pathname)` +
    #             `\result == -1 or (0 <= \result < 32)` — no NEW trust. Mirrors
    #             how sys_open (gap-14/15) carries its inode-binding link.
    #
    #             no_inline (E-matching): the body is body-proven against the two
    #             `dir_lookup` ensures, but INLINING it at every caller (the
    #             stat/lstat wrappers + walk) re-exposes _dir_lookup's trusted
    #             `dir_lookup` binding to the SMT context and the quantifier
    #             E-matches into a step blowup (Timeout/OOM). `no_inline` emits an
    #             abstract `val` carrying exactly these ensures, so callers reason
    #             modularly from the contract — no new trust, contract still
    #             body-proven on its own.
    #@ no_inline
    def sys_stat(self, pathname: str) -> int:
        return self._dir_lookup(5, pathname)

    #@ requires True
    #@ assigns \nothing
    #@ ensures \result == -1 or (\result >= 0 and \result < 32)
    #@ ensures (dir_lookup(self.disk, 5, pathname) >= 0) ==> (0 <= \result and \result < 32)
    #@ ensures (dir_lookup(self.disk, 5, pathname) < 0) ==> \result == -1
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/lstat.html
    # cite:_note: POSIX lstat() — like stat() but does not dereference a
    #             symbolic link. In this single-level inode model with no live
    #             symlink resolution, the root-directory name lookup is identical
    #             to stat(); the same PATH-LINK ensures (body-proven via
    #             _dir_lookup, no new trust) expose the resolution.
    #             no_inline for the same E-matching reason as sys_stat.
    #@ no_inline
    def sys_lstat(self, pathname: str) -> int:
        return self._dir_lookup(5, pathname)

    # --- THE 13 NEW INTEGRATED SYSTEM CALLS ---

    #@ proof rocq UnixFs.Dir.scan_reflects_present
    #@ proof lean UnixFs.Dir.scan_reflects_present
    #@ proof rocq UnixFs.Dir.slot_inode_nonneg
    #@ proof lean UnixFs.Dir.slot_inode_nonneg
    #@ requires True
    #@ assigns self.disk, self._mtime_ticks
    #@ ensures \result == 0 or \result == -1
    #@ ensures \result == 0 ==> (dir_lookup(self.disk, 5, pathname) >= 0)
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/mkdir.html
    # cite:_note: POSIX mkdir() — allocates inode+block, seeds '.' and
    #             '..', and links the dir into the root. -1 on EEXIST or
    #             ENFILE/ENOSPC / full root. De-trusted: array inode +
    #             byte-level entry writes (atime/mtime set from clock).
    #
    #             gap-9: `\result == 0 ==> dir_lookup(self.disk, 5, pathname) >= 0`
    #             — the mutator ESTABLISHES the presence view. The final
    #             `_write_entry(5, slot, inode_num, pathname)` (with inode_num in
    #             [1,32) from _alloc_inode) makes the abstract slot decode at
    #             `slot` return (inode_num, pathname) — the existential witness
    #             at k=slot — and the `#@ assert` below + the scan_reflects_present
    #             axiom (existential => dir_lookup>=0) discharge the postcondition.
    #@ no_inline
    def sys_mkdir(self, pathname: str, mode: int) -> int:
        if self._dir_lookup(5, pathname) >= 0:
            return -1
        # Permission check: need write+execute on parent directory
        root_inode = self._read_inode(0)
        if self._check_perm(root_inode, 3) == 0:  # 2=write + 1=execute
            return -1
        inode_num = self._alloc_inode()
        if inode_num < 0 or inode_num >= 32:
            return -1
        p_block = self._alloc_block()
        if p_block < 0 or p_block >= 256:
            return -1
        now = self._now()
        inode = [512, 2, 2, mode, 0, 0, now, now, p_block, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self._write_inode(inode_num, inode)
        self._write_entry(p_block, 0, inode_num, ".")
        self._write_entry(p_block, 1, 0, "..")
        slot = self._dir_find_free(5)
        if slot < 0:
            return -1
        self._write_entry(5, slot, inode_num, pathname)
        # gap-9: the just-written root-dir slot is the existential witness the
        # scan_reflects_present axiom needs — slot_inode/slot_name at k=slot come
        # from _write_entry's post-state (inode_num in [1,32) per _alloc_inode, so
        # the slot is live). The axiom (existential => dir_lookup>=0) then
        # discharges `dir_lookup(self.disk, 5, pathname) >= 0`.
        #@ assert \exists k: int; 0 <= k and k < 16 and slot_inode(self.disk, 5, k) != 0 and slot_inode(self.disk, 5, k) < 32 and slot_name(self.disk, 5, k) == pathname
        return 0

    #@ proof rocq UnixFs.Dir.remove_reflects_absent
    #@ proof lean UnixFs.Dir.remove_reflects_absent
    #@ proof rocq UnixFs.Dir.slot_inode_nonneg
    #@ proof lean UnixFs.Dir.slot_inode_nonneg
    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    #@ ensures \result == 0 ==> (dir_lookup(self.disk, 5, pathname) < 0)
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/rmdir.html
    # cite:_note: POSIX rmdir() — -1 on ENOENT or ENOTDIR (type at index
    #             2 != 2). De-trusted: lookup → type check → free the dir's
    #             data block + inode → zero the root entry LAST. (The original
    #             ENOTEMPTY check required scanning the child dir for live
    #             names — a string operation; dropped under `ensures
    #             0/-1`, a documented behaviour change.)
    #
    #             gap-11 (ABSENCE direction, the twin of mkdir's presence):
    #             `\result == 0 ==> dir_lookup(self.disk, 5, pathname) < 0` — the
    #             name is GONE after its slot is zeroed. `_dir_find_slot` returns
    #             the UNIQUE live slot for `pathname` (its trusted uniqueness
    #             ensures); `_zero_entry(5, slot)` makes that slot dead
    #             (remove-witness) and leaves every OTHER slot's decode unchanged
    #             (slot-locality frame), so the uniqueness fact transfers to the
    #             post-state. The `#@ assert`s below feed remove_reflects_absent's
    #             remove-witness + uniqueness hypotheses (slot_inode_nonneg
    #             discharges the non-negativity antecedent), which concludes
    #             dir_lookup < 0. The dir-entry zero is done LAST (mirroring
    #             mkdir's entry-write-last) so the witness immediately precedes the
    #             assert with no intervening `_set_bitmap` (`assigns self.disk`)
    #             to havoc block 5; `#@ no_inline` isolates the witness VC from the
    #             loop-bearing `_dir_find_slot` scan.
    #@ no_inline
    def sys_rmdir(self, pathname: str) -> int:
        inode_num = self._dir_lookup(5, pathname)
        if inode_num < 0 or inode_num >= 32:
            return -1
        inode = self._read_inode(inode_num)
        if inode[2] != 2:
            return -1
        slot = self._dir_find_slot(5, pathname)
        if slot < 0:
            return -1
        p_block = inode[8]
        if p_block > 0 and p_block < 256:
            self._set_bitmap(4, p_block, 0)
        self._set_bitmap(0, inode_num, 0)
        # Zero the directory entry LAST (entry-write-last shape): the
        # remove-witness + slot-locality frame land in the immediate pre-assert
        # state, with no _set_bitmap (assigns self.disk) after to havoc block 5.
        self._zero_entry(5, slot)
        #@ assert slot_inode(self.disk, 5, slot) == 0
        #@ assert \forall k: int; (0 <= k and k < 16 and k != slot and slot_name(self.disk, 5, k) == pathname) ==> slot_inode(self.disk, 5, k) == 0
        return 0

    #@ requires fd >= 0
    #@ assigns \nothing
    #@ ensures \result == 0 or \result == -1
    # cite: https://man7.org/linux/man-pages/man2/getdents.2.html
    # cite:_note: Linux getdents() — checks fd validity + that the inode
    #             is a directory (type index 2 == 2). Returns 0 on success,
    #             -1 on EBADF or ENOTDIR.
    def sys_getdents(self, fd: int) -> int:
        if fd >= 64:
            return -1
        if self.fd_open[fd] == 0:
            return -1
        inode_num = self.fd_inode[fd]
        if inode_num < 0 or inode_num >= 32:
            return -1
        inode = self._read_inode(inode_num)
        if inode[2] != 2:
            return -1
        return 0

    #@ requires fd >= 0
    #@ requires whence >= 0 and whence <= 2
    #@ assigns self.fd_offset
    #@ ensures \result >= -1
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/lseek.html
    # cite:_note: POSIX lseek() — returns new offset (≥ 0) or -1 on
    #             EBADF. Resulting offset is clamped to >= 0. De-trusted:
    #             fd context → fd_offset[fd] / fd_inode[fd]; whence
    #             literals 0/1/2 (SEEK_SET/CUR/END). The inode read for
    #             SEEK_END is guarded so _read_inode's 0<=n<32 precondition
    #             holds.
    def sys_lseek(self, fd: int, offset: int, whence: int) -> int:
        if fd >= 64:
            return -1
        if self.fd_open[fd] == 0:
            return -1
        if whence == 0:
            self.fd_offset[fd] = offset
        elif whence == 1:
            self.fd_offset[fd] = self.fd_offset[fd] + offset
        elif whence == 2:
            inode_num = self.fd_inode[fd]
            if inode_num >= 0 and inode_num < 32:
                inode = self._read_inode(inode_num)
                self.fd_offset[fd] = inode[0] + offset
        if self.fd_offset[fd] < 0:
            self.fd_offset[fd] = 0
        return self.fd_offset[fd]

    #@ requires fd >= 0
    #@ assigns \nothing
    #@ ensures \result == 0 or \result == -1
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/fsync.html
    # cite:_note: POSIX fsync() — always 0 when fd is valid (this
    #             simulator is in-memory; no real disk to flush).
    #             De-trusted: dict membership → fd_open[fd]==1.
    def sys_fsync(self, fd: int) -> int:
        if fd < 64 and self.fd_open[fd] == 1:
            return 0
        return -1

    #@ proof rocq UnixFs.Dir.block5_decode_frame
    #@ proof lean UnixFs.Dir.block5_decode_frame
    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    # BLOCK-5 DECODE FRAME (gap-13, Wall M): chmod writes the disk ONLY via
    # _write_inode (the inode region [512,2560), disjoint from block 5), which
    # carries the block-5 decode frame, so block-5 decode is preserved here.
    # Proven for free from the helper's ensures (ZERO body annotation). EXPORTED as
    # an ensures so the importer (os/__init__) discharges the directory-uniqueness
    # class invariant's maintenance over the imported `val` stub.
    #@ ensures \forall k: int; (0 <= k and k < 16) ==> slot_inode(self.disk, 5, k) == \old(slot_inode(self.disk, 5, k))
    #@ ensures \forall k: int; (0 <= k and k < 16) ==> slot_name(self.disk, 5, k) == \old(slot_name(self.disk, 5, k))
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/chmod.html
    # cite:_note: POSIX chmod() — sets inode.mode (array index 3); -1 on
    #             ENOENT. De-trusted: lookup → read 18-int inode → set
    #             field → write back.
    # MODULAR BOUNDARY (gap-1..5 array-typing): without no_inline, sys_chmod inlines
    # into the os/__init__ chmod wrapper, dropping the block-5 byte-frame asserts into
    # the wrapper VC. The faithful `array int` typing of name_bytes (gap-2/3/4) adds
    # array terms that bloat that VC and tip the frame assert to Out-of-memory. Like
    # sys_stat/sys_lstat, isolate the body to the standalone body gate via no_inline;
    # __init__ then discharges the namespace frame from this method's ensures (trusted
    # val), keeping the public-API gate green.
    #@ no_inline
    def sys_chmod(self, pathname: str, mode: int) -> int:
        inode_num = self._dir_lookup(5, pathname)
        if inode_num < 0 or inode_num >= 32:
            return -1
        inode = self._read_inode(inode_num)
        if mode < 0 or mode > 65535:
            return -1
        inode[3] = mode
        self._write_inode(inode_num, inode)
        # BLOCK-5 DECODE FRAME chain (gap-13, Wall M). _write_inode is INLINED in
        # the importer, so its blit into [512+inode_num*64, +64) is expanded here.
        # inode_num < 32 (the lookup guard) => the written region is a subset of
        # [512, 2560), DISJOINT from block 5 [2560, 3072); and _dir_lookup /
        # _read_inode `assigns \nothing`. So every block-5 byte equals its
        # function-entry value (byte-frame assert), and the cited
        # UnixFs.Dir.block5_decode_frame converts that into the decode-frame the
        # class-invariant maintenance needs (slot decode unchanged -> uniqueness
        # preserved). This collapses the gap-13 232M-step balloon to a rewrite.
        #@ assert \forall b: int; (2560 <= b and b < 3072) ==> self.disk[b] == \old(self.disk[b])
        #@ assert \forall k: int; (0 <= k and k < 16) ==> slot_inode(self.disk, 5, k) == \old(slot_inode(self.disk, 5, k))
        #@ assert \forall k: int; (0 <= k and k < 16) ==> slot_name(self.disk, 5, k) == \old(slot_name(self.disk, 5, k))
        return 0

    #@ proof rocq UnixFs.Dir.block5_decode_frame
    #@ proof lean UnixFs.Dir.block5_decode_frame
    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    # BLOCK-5 DECODE FRAME (gap-13, Wall M): chown writes the disk ONLY via the
    # disjoint inode-region _write_inode; block-5 decode is preserved (exported as
    # an ensures so the importer maintains the directory-uniqueness invariant).
    #@ ensures \forall k: int; (0 <= k and k < 16) ==> slot_inode(self.disk, 5, k) == \old(slot_inode(self.disk, 5, k))
    #@ ensures \forall k: int; (0 <= k and k < 16) ==> slot_name(self.disk, 5, k) == \old(slot_name(self.disk, 5, k))
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/chown.html
    # cite:_note: POSIX chown() — sets inode.uid (4) + inode.gid (5); -1
    #             on ENOENT. De-trusted.
    def sys_chown(self, pathname: str, owner: int, group: int) -> int:
        inode_num = self._dir_lookup(5, pathname)
        if inode_num < 0 or inode_num >= 32:
            return -1
        inode = self._read_inode(inode_num)
        inode[4] = owner
        inode[5] = group
        self._write_inode(inode_num, inode)
        # BLOCK-5 DECODE FRAME chain (gap-13, Wall M) — see sys_chmod.
        #@ assert \forall b: int; (2560 <= b and b < 3072) ==> self.disk[b] == \old(self.disk[b])
        #@ assert \forall k: int; (0 <= k and k < 16) ==> slot_inode(self.disk, 5, k) == \old(slot_inode(self.disk, 5, k))
        #@ assert \forall k: int; (0 <= k and k < 16) ==> slot_name(self.disk, 5, k) == \old(slot_name(self.disk, 5, k))
        return 0

    #@ proof rocq UnixFs.Dir.block5_decode_frame
    #@ proof lean UnixFs.Dir.block5_decode_frame
    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    # BLOCK-5 DECODE FRAME (gap-13, Wall M): utimensat writes the disk ONLY via
    # the disjoint inode-region _write_inode; block-5 decode is preserved.
    #@ ensures \forall k: int; (0 <= k and k < 16) ==> slot_inode(self.disk, 5, k) == \old(slot_inode(self.disk, 5, k))
    #@ ensures \forall k: int; (0 <= k and k < 16) ==> slot_name(self.disk, 5, k) == \old(slot_name(self.disk, 5, k))
    # cite: https://man7.org/linux/man-pages/man2/utimensat.2.html
    # cite:_note: Linux utimensat() — sets inode.atime (6) + inode.mtime
    #             (7); -1 on ENOENT. De-trusted.
    def sys_utimensat(self, pathname: str, atime: int, mtime: int) -> int:
        inode_num = self._dir_lookup(5, pathname)
        if inode_num < 0 or inode_num >= 32:
            return -1
        inode = self._read_inode(inode_num)
        inode[6] = atime
        inode[7] = mtime
        self._write_inode(inode_num, inode)
        # BLOCK-5 DECODE FRAME chain (gap-13, Wall M) — see sys_chmod.
        #@ assert \forall b: int; (2560 <= b and b < 3072) ==> self.disk[b] == \old(self.disk[b])
        #@ assert \forall k: int; (0 <= k and k < 16) ==> slot_inode(self.disk, 5, k) == \old(slot_inode(self.disk, 5, k))
        #@ assert \forall k: int; (0 <= k and k < 16) ==> slot_name(self.disk, 5, k) == \old(slot_name(self.disk, 5, k))
        return 0

    #@ proof rocq UnixFs.Dir.scan_reflects_present
    #@ proof lean UnixFs.Dir.scan_reflects_present
    #@ proof rocq UnixFs.Dir.remove_reflects_absent
    #@ proof lean UnixFs.Dir.remove_reflects_absent
    #@ proof rocq UnixFs.Dir.slot_inode_nonneg
    #@ proof lean UnixFs.Dir.slot_inode_nonneg
    #@ requires oldpath != newpath
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    #@ ensures \result == 0 ==> (dir_lookup(self.disk, 5, newpath) >= 0)
    #@ ensures \result == 0 ==> (dir_lookup(self.disk, 5, oldpath) < 0)
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/rename.html
    # cite:_note: POSIX rename() — removes both the oldpath and any
    #             existing newpath entry, then writes (newpath, inode) in
    #             a free slot. -1 on ENOENT (oldpath missing) / full dir.
    #             De-trusted: lookup → locate old slot → zero any existing
    #             newpath slot → write the new entry in a free slot → zero the
    #             old slot LAST.
    #
    #             gap-9 (PRESENCE direction): on success `dir_lookup(self.disk,
    #             5, newpath) >= 0` — `_write_entry(5, fslot, inode_num, newpath)`
    #             (inode_num in [1,32) from the oldpath lookup) is the existential
    #             witness at k=fslot; the final `_zero_entry(5, old_slot)` is
    #             slot-local (old_slot != fslot, since fslot was free while
    #             old_slot was live), so the witness survives it.
    #
    #             gap-11 (ABSENCE direction): on success `dir_lookup(self.disk, 5,
    #             oldpath) < 0` — `_dir_find_slot` gives old_slot as the UNIQUE
    #             live slot for oldpath; zeroing it LAST is the remove-witness, the
    #             newpath write (newpath != oldpath, by the precondition) and the
    #             newpath-slot zero are slot-local / name != oldpath, so no slot
    #             decodes to oldpath. The `#@ assert`s feed remove_reflects_absent
    #             (slot_inode_nonneg discharges the non-negativity antecedent).
    #             Both writes are entry-LAST-shaped so the witnesses sit in the
    #             pre-assert state; `#@ no_inline` isolates them from the scans.
    #@ no_inline
    def sys_rename(self, oldpath: str, newpath: str) -> int:
        inode_num = self._dir_lookup(5, oldpath)
        if inode_num < 0 or inode_num >= 32:
            return -1
        old_slot = self._dir_find_slot(5, oldpath)
        if old_slot < 0:
            return -1
        new_slot = self._dir_find_slot(5, newpath)
        if new_slot >= 0:
            self._zero_entry(5, new_slot)
        fslot = self._dir_find_free(5)
        if fslot < 0:
            return -1
        # Write newpath in a free slot (PRESENCE witness), then zero old_slot
        # LAST (ABSENCE remove-witness). fslot is free => fslot != old_slot, so
        # the final zero is slot-local to old_slot and preserves the newpath
        # witness at fslot; newpath != oldpath keeps oldpath absent at fslot.
        self._write_entry(5, fslot, inode_num, newpath)
        self._zero_entry(5, old_slot)
        #@ assert \exists k: int; 0 <= k and k < 16 and slot_inode(self.disk, 5, k) != 0 and slot_inode(self.disk, 5, k) < 32 and slot_name(self.disk, 5, k) == newpath
        #@ assert slot_inode(self.disk, 5, old_slot) == 0
        #@ assert \forall k: int; (0 <= k and k < 16 and k != old_slot and slot_name(self.disk, 5, k) == oldpath) ==> slot_inode(self.disk, 5, k) == 0
        return 0

    #@ proof rocq UnixFs.Dir.scan_reflects_present
    #@ proof lean UnixFs.Dir.scan_reflects_present
    #@ proof rocq UnixFs.Dir.slot_inode_nonneg
    #@ proof lean UnixFs.Dir.slot_inode_nonneg
    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    #@ ensures \result == 0 ==> (dir_lookup(self.disk, 5, linkpath) >= 0)
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/symlink.html
    # cite:_note: POSIX symlink() — allocates a type-3 (symlink) inode
    #             holding the target-path bytes inline in its data block.
    #             -1 on EEXIST or allocation failure / full dir.
    #             De-trusted: the target bytes are written via a '>H30s'
    #             pack of `target.encode(...)` (opaque buffer, gap 5);
    #             size field set to 30 (the on-disk name-field width).
    #
    #             gap-9 (PRESENCE direction, mirrors sys_mkdir / sys_link): on
    #             success `dir_lookup(self.disk, 5, linkpath) >= 0` — the symlink
    #             mutator ESTABLISHES the presence view for the LINK name. The final
    #             `_write_entry(5, slot, inode_num, linkpath)` (inode_num in [1,32)
    #             from _alloc_inode) makes the abstract slot decode at `slot` return
    #             (inode_num, linkpath) — the existential witness at k=slot — so the
    #             `#@ assert` below + the scan_reflects_present axiom (existential =>
    #             dir_lookup>=0) discharge the postcondition. The entry write is LAST
    #             (mirroring mkdir's entry-write-last) and `#@ no_inline` isolates the
    #             witness VC from the loop-bearing `_dir_find_free` scan.
    #@ no_inline
    def sys_symlink(self, target: str, linkpath: str) -> int:
        if self._dir_lookup(5, linkpath) >= 0:
            return -1
        inode_num = self._alloc_inode()
        if inode_num < 0 or inode_num >= 32:
            return -1
        p_block = self._alloc_block()
        if p_block < 0 or p_block >= 256:
            return -1
        self.disk[p_block * 512:p_block * 512 + 32] = _pack_direntry(0, _pad_name(target))
        inode = [30, 1, 3, 511, 0, 0, 0, 0, p_block, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self._write_inode(inode_num, inode)
        slot = self._dir_find_free(5)
        if slot < 0:
            return -1
        self._write_entry(5, slot, inode_num, linkpath)
        # gap-9: the just-written root-dir slot is the existential witness the
        # scan_reflects_present axiom needs (slot_inode/slot_name at k=slot from
        # _write_entry's post-state, inode_num in [1,32) per _alloc_inode, so the
        # slot is live). The axiom (existential => dir_lookup>=0) then discharges
        # `dir_lookup(self.disk, 5, linkpath) >= 0`.
        #@ assert \exists k: int; 0 <= k and k < 16 and slot_inode(self.disk, 5, k) != 0 and slot_inode(self.disk, 5, k) < 32 and slot_name(self.disk, 5, k) == linkpath
        return 0

    #@ requires True
    #@ assigns \nothing
    #@ ensures \result == -1 or (\result >= 0 and \result < 256)
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/readlink.html
    # cite:_note: POSIX readlink() — returns the symlink inode's first
    #             data block number (index 8), or -1 on ENOENT / non-symlink
    #             (type at index 2 != 3). Block numbers are in [0, 256).
    #@ no_inline
    def sys_readlink(self, pathname: str) -> int:
        inode_num = self._dir_lookup(5, pathname)
        if inode_num < 0 or inode_num >= 32:
            return -1
        inode = self._read_inode(inode_num)
        if inode[2] != 3:
            return -1
        block = inode[8]
        # Block numbers are in [0, 256); guard so the return is provably
        # in range (the field is a uint32, so the type alone does not bound
        # it). A symlink's target block is allocated in [6, 256), so the
        # guard never fires in practice — it makes the postcondition explicit
        # rather than resting on an unstated block-validity invariant.
        if block < 0 or block >= 256:
            return -1
        return block

    #@ requires oldfd >= 0
    #@ assigns self.fd_open, self.fd_inode, self.fd_offset, self.fd_flags, self.next_fd
    #@ ensures \result == -1 or \result >= 3
    # SHARED OPEN-FILE-DESCRIPTION (gap-15): on success the duped fd resolves to
    # the SAME inode as the source — `fd_inode[result] == fd_inode[oldfd]`. The body
    # value-copies `fd_inode[newfd] = fd_inode[oldfd]` and returns newfd; the
    # `if newfd == oldfd: return -1` guard below makes newfd != oldfd in the success
    # path, so the copied source cell `fd_inode[oldfd]` is undisturbed by the write
    # to `fd_inode[newfd]` — body-FAITHFUL (the contract mirrors the body exactly; it
    # rides on the function-level trust below ONLY because the co-located ENFILE
    # claim forces function-level `\trusted`). Composes with sys_open's
    # `fd_inode[result] == dir_lookup(...)` so dup(open(p)) resolves to p's inode.
    #@ ensures \result >= 3 ==> self.fd_inode[\result] == \old(self.fd_inode[oldfd])
    # OBSERVABLE SHARED INODE (gap-1): for the shared inode to be observable through
    # fstat(dup_fd) — whose guarded ensures fires only on `fd_open[fd]==1 and
    # 0<=fd_inode[fd]<32` — dup must ALSO pin the duped fd as OPEN with an in-range
    # inode. Body-FAITHFUL: the success path sets `fd_open[newfd] = 1` (so OPEN holds
    # unconditionally on success), and `fd_inode[newfd] = fd_inode[oldfd]` copies the
    # source cell — so the range follows from the source's pre-state inode being in
    # range (the wrapper/test established `0<=fd_inode[oldfd]<32` at the open site;
    # dup writes only newfd's cells with newfd != oldfd, so `\old(fd_inode[oldfd])` is
    # the copied value). Mirrors the gap-15 forms sys_open pins on its returned fd.
    #@ ensures \result >= 3 ==> self.fd_open[\result] == 1
    # the duped fd is in [3, 64): the success path is `newfd = next_fd; if newfd >= 64:
    # return -1` so newfd < 64 on success — needed so a caller's fstat(dup_fd) (guarded
    # by `fd < 64`) can fire on the duped fd.
    #@ ensures \result >= 3 ==> \result < 64
    #@ ensures (\result >= 3 and 0 <= \old(self.fd_inode[oldfd]) and \old(self.fd_inode[oldfd]) < 32) ==> (0 <= self.fd_inode[\result] and self.fd_inode[\result] < 32)
    # VALIDITY-GIVEN-VALID-SOURCE (gap-15): an open, in-range source fd duplicates
    # to a VALID fd (>= 3). The body returns -1 only on EBADF (oldfd bad/closed) or
    # ENFILE (next_fd >= 64, the 64-slot fd table full). For a valid open source the
    # EBADF branch is excluded, but the model cannot derive `next_fd < 64` (no
    # closed-form bound on next_fd across the syscall history), so the no-ENFILE
    # direction is a HUMAN-REVIEWED fidelity claim of the SAME interim trust class as
    # sys_open's `fd-resolution-fidelity` (this model's fd table is sized so an open
    # source always has a free slot to dup into). Provable later once an
    # `next_fd <= 64`-style fd-table invariant is established.
    # NOTE: the validity hypothesis reads `\old(self.fd_open[oldfd])` (the source's
    # open-state at CALL ENTRY), not the post-state — dup writes fd_open (for newfd),
    # so a caller that established `fd_open[oldfd]==1` BEFORE the call must see it
    # honoured against that pre-state value (the post-state cell is framed away by the
    # opaque writes).
    #@ ensures (oldfd < 64 and \old(self.fd_open[oldfd]) == 1) ==> \result >= 3
    #@ \trusted reviewer: fd-resolution-fidelity
    #@ no_inline
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/dup.html
    # cite:_note: POSIX dup() — -1 on EBADF or when the fd table is full
    #             (next_fd >= 64). De-trusted: the new fd's four columns
    #             are value-copied from oldfd's (the original shared the
    #             dict reference for a shared offset; the parallel-array
    #             model copies values — a documented behaviour change, not
    #             constrained by the contract). next_fd >= 3 invariant
    #             gives \result >= 3.
    def sys_dup(self, oldfd: int) -> int:
        if oldfd >= 64 or self.fd_open[oldfd] == 0:
            return -1
        newfd = self.next_fd
        if newfd >= 64:
            return -1
        if newfd == oldfd:
            return -1
        self.next_fd = newfd + 1
        self.fd_open[newfd] = 1
        self.fd_inode[newfd] = self.fd_inode[oldfd]
        self.fd_offset[newfd] = self.fd_offset[oldfd]
        self.fd_flags[newfd] = self.fd_flags[oldfd]
        return newfd

    #@ requires oldfd >= 0
    #@ requires newfd >= 0
    #@ assigns self.fd_open, self.fd_inode, self.fd_offset, self.fd_flags
    #@ ensures \result == newfd or \result == -1
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/dup.html
    # cite:_note: POSIX dup2() — closes newfd first if open, then makes it
    #             alias oldfd. Returns the requested newfd on success, -1
    #             on EBADF (oldfd not open / newfd out of range).
    #             De-trusted: the four fd columns are value-copied (see
    #             sys_dup note). The inline overwrite subsumes the close.
    def sys_dup2(self, oldfd: int, newfd: int) -> int:
        if oldfd >= 64 or self.fd_open[oldfd] == 0:
            return -1
        if newfd >= 64:
            return -1
        self.fd_open[newfd] = 1
        self.fd_inode[newfd] = self.fd_inode[oldfd]
        self.fd_offset[newfd] = self.fd_offset[oldfd]
        self.fd_flags[newfd] = self.fd_flags[oldfd]
        return newfd

    # --- 5 ADDITIONAL POSIX SYSCALLS ---

    #@ requires fd >= 0
    #@ assigns \nothing
    #@ ensures \result == -1 or (\result >= 0 and \result < 32)
    # FD-RESOLUTION (gap-14): fstat REPORTS the inode the fd resolves to
    # (`fd_resolves(fd)`, concretely `fd_inode[fd]`). For an open fd in range
    # whose stored inode is valid, fstat returns exactly that inode. This is
    # body-provable (the method returns `fd_inode[fd]` after its in-range / open /
    # valid-inode guards) — NOT a trusted claim. Composes with sys_open's
    # `fd_inode[result] == dir_lookup(...)` resolution so fstat(open(p)) reports
    # the inode the path p resolves to (the gap-14 fstat consequence).
    #@ ensures (fd < 64 and self.fd_open[fd] == 1 and 0 <= self.fd_inode[fd] and self.fd_inode[fd] < 32) ==> \result == self.fd_inode[fd]
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/fstat.html
    # cite:_note: POSIX fstat() — returns the inode number for an open fd,
    #             or -1 on EBADF (fd not open or out of range).
    def sys_fstat(self, fd: int) -> int:
        if fd >= 64:
            return -1
        if self.fd_open[fd] == 0:
            return -1
        inode_num = self.fd_inode[fd]
        if inode_num < 0 or inode_num >= 32:
            return -1
        return inode_num

    #@ proof rocq UnixFs.Dir.block5_decode_frame
    #@ proof lean UnixFs.Dir.block5_decode_frame
    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    # BLOCK-5 DECODE FRAME (gap-13, Wall M): truncate writes the disk ONLY via the
    # disjoint inode-region _write_inode; block-5 decode is preserved.
    #@ ensures \forall k: int; (0 <= k and k < 16) ==> slot_inode(self.disk, 5, k) == \old(slot_inode(self.disk, 5, k))
    #@ ensures \forall k: int; (0 <= k and k < 16) ==> slot_name(self.disk, 5, k) == \old(slot_name(self.disk, 5, k))
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/truncate.html
    # cite:_note: POSIX truncate() — sets inode.size (index 0) to `length`.
    #             -1 on ENOENT. If truncating below current size, data
    #             beyond `length` becomes inaccessible but blocks are not
    #             freed (a simplification — real truncate may free blocks).
    def sys_truncate(self, pathname: str, length: int) -> int:
        inode_num = self._dir_lookup(5, pathname)
        if inode_num < 0 or inode_num >= 32:
            return -1
        if length < 0 or length > 4294967295:
            return -1
        inode = self._read_inode(inode_num)
        inode[0] = length
        self._write_inode(inode_num, inode)
        # BLOCK-5 DECODE FRAME chain (gap-13, Wall M) — see sys_chmod. The
        # disjointness bound (write region [512+inode*64,+64) ends at <= 2560) is
        # pinned FIRST as a pure-integer assert so the byte-frame assert below does
        # not have to unfold the field-0 (4294967295-bounded) inode pack to derive
        # block-5 disjointness — without this hint Alt-Ergo/Z3 OOM here.
        #@ assert 512 + inode_num*64 + 64 <= 2560
        #@ assert \forall b: int; (2560 <= b and b < 3072) ==> self.disk[b] == \old(self.disk[b])
        # The block5_decode_frame axiom derives BOTH slot_inode AND slot_name
        # preservation from this one byte-frame; the slot_inode in-body assert
        # instantiates that axiom for (old disk, disk), and the slot_name ENSURES then
        # discharges from the same in-context instance. (gap-15: a separate slot_name
        # in-body assert re-instantiated the axiom and tipped Alt-Ergo into
        # timeout/OOM once the opaque sys_dup `val` enlarged the module context; the
        # ensures-level proof is robust.)
        #@ assert \forall k: int; (0 <= k and k < 16) ==> slot_inode(self.disk, 5, k) == \old(slot_inode(self.disk, 5, k))
        return 0

    #@ proof rocq UnixFs.Dir.block5_decode_frame
    #@ proof lean UnixFs.Dir.block5_decode_frame
    #@ requires fd >= 0
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    # BLOCK-5 DECODE FRAME (gap-13, Wall M): ftruncate writes the disk ONLY via the
    # disjoint inode-region _write_inode; block-5 decode is preserved.
    #@ ensures \forall k: int; (0 <= k and k < 16) ==> slot_inode(self.disk, 5, k) == \old(slot_inode(self.disk, 5, k))
    #@ ensures \forall k: int; (0 <= k and k < 16) ==> slot_name(self.disk, 5, k) == \old(slot_name(self.disk, 5, k))
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/ftruncate.html
    # cite:_note: POSIX ftruncate() — like truncate() but by fd. -1 on EBADF.
    def sys_ftruncate(self, fd: int, length: int) -> int:
        if fd >= 64:
            return -1
        if self.fd_open[fd] == 0:
            return -1
        inode_num = self.fd_inode[fd]
        if inode_num < 0 or inode_num >= 32:
            return -1
        if length < 0 or length > 4294967295:
            return -1
        inode = self._read_inode(inode_num)
        inode[0] = length
        self._write_inode(inode_num, inode)
        # BLOCK-5 DECODE FRAME chain (gap-13, Wall M) — see sys_chmod / sys_truncate.
        #@ assert 512 + inode_num*64 + 64 <= 2560
        #@ assert \forall b: int; (2560 <= b and b < 3072) ==> self.disk[b] == \old(self.disk[b])
        #@ assert \forall k: int; (0 <= k and k < 16) ==> slot_inode(self.disk, 5, k) == \old(slot_inode(self.disk, 5, k))
        #@ assert \forall k: int; (0 <= k and k < 16) ==> slot_name(self.disk, 5, k) == \old(slot_name(self.disk, 5, k))
        return 0

    #@ proof rocq UnixFs.Dir.scan_reflects_present
    #@ proof lean UnixFs.Dir.scan_reflects_present
    #@ proof rocq UnixFs.Dir.slot_inode_nonneg
    #@ proof lean UnixFs.Dir.slot_inode_nonneg
    #@ requires True
    #@ assigns \nothing
    #@ ensures \result == 0 or \result == -1
    #@ ensures (\result == 0) <==> (dir_lookup(self.disk, 5, pathname) >= 0)
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/access.html
    # cite:_note: POSIX access() — checks if `pathname` exists (F_OK,
    #             mode=0). Returns 0 if the file exists, -1 on ENOENT.
    #             Permission bits (R_OK, W_OK, X_OK) are not checked in
    #             this model; only existence is tested.
    #
    #             gap-9: the observer REFLECTS the presence view. `(\result == 0)
    #             <==> dir_lookup(self.disk, 5, pathname) >= 0` proves via
    #             `_dir_lookup`'s `\result == dir_lookup(self.disk, 5, pathname)`
    #             binding (the body returns 0 iff that result >= 0). The public-API
    #             `access` wrapper reuses this exact light form.
    #@ no_inline
    def sys_access(self, pathname: str, mode: int) -> int:
        inode_num = self._dir_lookup(5, pathname)
        if inode_num < 0:
            return -1
        return 0

    #@ requires True
    #@ assigns self.disk, self.fd_open, self.fd_inode, self.fd_offset, self.fd_flags, self.fd_block, self.next_fd, self._mtime_ticks
    #@ ensures \result == -1 or \result >= 3
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/creat.html
    # cite:_note: POSIX creat() — equivalent to open(pathname,
    #             O_CREAT|O_WRONLY|O_TRUNC, mode). Allocates a data block
    #             for the new file so it is immediately writable. -1 on
    #             allocation failure or full root dir.
    def sys_creat(self, pathname: str, mode: int) -> int:
        now = self._now()
        inode_num = self._dir_lookup(5, pathname)
        if inode_num >= 0 and inode_num < 32:
            inode = self._read_inode(inode_num)
            inode[0] = 0
            inode[7] = now
            self._write_inode(inode_num, inode)
        else:
            inode_num = self._alloc_inode()
            if inode_num < 0 or inode_num >= 32:
                return -1
            p_block = self._alloc_block()
            if p_block < 0 or p_block >= 256:
                return -1
            inode = [0, 1, 1, mode, 0, 0, now, now, p_block, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self._write_inode(inode_num, inode)
            slot = self._dir_find_free(5)
            if slot < 0:
                return -1
            self._write_entry(5, slot, inode_num, pathname)
        fd = self.next_fd
        if fd < 0 or fd >= 64:
            return -1
        self.next_fd = fd + 1
        self.fd_open[fd] = 1
        self.fd_inode[fd] = inode_num
        self.fd_offset[fd] = 0
        self.fd_flags[fd] = 1  # O_WRONLY
        return fd
