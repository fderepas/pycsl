# formal_os_codec.py — os inode byte-codec CONSEQUENCE tests — PUBLIC API ONLY.
#
# The inode byte codec (src/pycsl_lib/os/codec.py) serializes an 18-field
# inode record to a 64-byte big-endian byte array (_pack_inode) and
# deserializes it back (_unpack_inode). The keystone consequence is the
# ROUND-TRIP: unpack(pack(fields)) reconstructs every field exactly.
#
# These theorems CALL THE PUBLIC CODEC API (the codec module's exported
# functions) and assert the OBSERVED CONSEQUENCE — field preservation
# across the pack/unpack round-trip — never the call's own return code.
#
# Non-vacuity: a byte-order swap, a field-offset error, or a width mismatch
# in either direction would break at least one field's equality, failing
# the postcondition. The codec is body-verified inline in codec.py (G0a,
# zero \trusted); these tests re-prove the consequence from the CALLER
# side via contract composition, independently of the body proof.

from pycsl_lib.os.codec import _pack_inode, _inode_round_trip


# (1) The keystone round-trip via the composed helper _inode_round_trip.
# Consequence: all 18 fields are preserved. The caller observes the
# reconstructed fields and asserts each equals the original.
#@ requires \valid(fields, 18)
#@ requires 0 <= fields[0] and fields[0] <= 4294967295
#@ for k in range(1, 6):
#@     requires 0 <= fields[k] and fields[k] <= 65535
#@ requires 0 <= fields[6] and fields[6] <= 4294967295
#@ requires 0 <= fields[7] and fields[7] <= 4294967295
#@ for k in range(8, 18):
#@     requires 0 <= fields[k] and fields[k] <= 4294967295
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
def codec_roundtrip_all_fields(fields: list) -> list:
    return _inode_round_trip(fields)


# (2) pack WIDTH consequence: _pack_inode always emits exactly 64 bytes.
# Non-vacuous: a truncation or off-by-one in the packer would break the
# width. The caller observes the byte-array length via the narrow interface.
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
def codec_pack_width_64(fields: list) -> list:
    return _pack_inode(fields)


# NOTE on the DECOMPOSED round-trip and BYTE-BOUND consequences:
# _pack_inode carries a narrow `#@ interface` (only \length == 64); its
# per-byte bounds (0..255) and field-encoding ensures are HIDDEN from
# importers to keep the os proof light (codec.py docstring, G0b). The
# decomposed round-trip (caller packs then unpacks) and the byte-bound
# consequence therefore CANNOT be proven from the caller side — the
# interface is opaque to them. These properties ARE body-proven inline
# in codec.py (G0a, zero \trusted, verified SUCCESS); they are not gaps
# in the proof, only in the caller-visible interface. The keystone
# round-trip consequence (all 18 fields preserved) IS caller-provable
# via the transparent _inode_round_trip (theorem 1 above), which carries
# the full field-equality interface. Widening _pack_inode's interface
# was considered and rejected: it would change UIFS's proof context
# (UIFS unproven count must not increase). See
# getting-better/20260623-1500-codec-interface-opacity.md.
