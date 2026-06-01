"""0420 — struct.pack / struct.unpack round-trip axiom acceptance.

Phase 3+4 acceptance test for missing-bytes-struct-feature.md.

  parse_dir_entry / parse_inode_header
    Document the citation pattern: \\trusted consumers that name
    the axiom in their `#@ proof rocq` directive.

  roundtrip_two_ints
    ACTIVE axiom-discharge test. Body packs (x0, x1) then unpacks;
    postcondition `result == x0` requires the round-trip axiom to
    discharge. Without the axiom: Unknown. With it: closes.
"""
import struct  # noqa


#@ \trusted reviewer: pycsl-self-annotate
#@ ensures True
#@ proof rocq UnixFs.Struct.i1a1.round_trip
# cite:_note: Citation-only — body stays \trusted; the axiom is
#             registered into the emitted mlw preamble.
def parse_dir_entry(data: bytes) -> int:
    """Parse one directory entry from a 32-byte buffer."""
    inode_num, _name_bytes = struct.unpack(">H30s", data)
    return inode_num


#@ \trusted reviewer: pycsl-self-annotate
#@ ensures True
#@ proof rocq UnixFs.Struct.i18.round_trip
# cite:_note: Citation-only — body stays \trusted.
def parse_inode_header(data: bytes) -> int:
    """Parse the mode-field from a 64-byte inode block."""
    (mode, uid, gid, _link_count, _atime, _mtime, _size_lo, _size_hi,
     _p0, _p1, _p2, _p3, _p4, _p5, _p6, _p7, _p8, _p9) = struct.unpack(
        ">IHHHHHII10Ixx", data)
    return mode


#@ ensures \result == x0
#@ proof rocq UnixFs.Struct.i2.round_trip
# cite:_note: ACTIVE axiom-discharge acceptance test for Phase 4.
#             Body packs (x0, x1) then unpacks the result; the
#             postcondition `result == x0` is closed by the round-trip
#             axiom `UnixFs.Struct.i2.round_trip` which states
#             `unpack(pack(x0, x1)) = (x0, x1)`. Without the axiom
#             the SMT solver cannot relate the abstract symbols
#             struct_pack_i2 and struct_unpack_i2 and returns Unknown.
def roundtrip_two_ints(x0: int, x1: int) -> int:
    """Pack two ints then unpack — first slot must equal x0."""
    packed = struct.pack(">HH", x0, x1)
    out_x0, _out_x1 = struct.unpack(">HH", packed)
    return out_x0
