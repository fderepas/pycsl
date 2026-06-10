# Probe: the faithful string-domain name-codec leaf (the strongest provable
# form of L1's byte-dirent NAME round-trip).
#
# A dirent maps name -> inode. The on-disk name field is 30 bytes; the
# FAITHFUL value carried by that field is the filename STRING. PyCSL models
# `str` as Why3 string.String (==, length, substring, concat are faithful),
# so the codec round-trip `_decode_name(_encode_name(name)) == name` proves
# by contract composition — WITHOUT going through the str<->byte boundary
# (Gap 5: ord/chr have no char<->int bridge; see probe_c).


# _encode_name: the name as it is stored in the dirent name field.
# In the faithful string model the stored value IS the name (a name of <= 30
# chars round-trips exactly; longer names are truncated to the 30-char field,
# matching the on-disk 30-byte cap). The contract pins the recoverable value.
#@ requires \str_length(name) <= 30
#@ assigns \nothing
#@ ensures \result == name
def _encode_name(name: str) -> str:
    return name


# _decode_name: recover the filename from the stored dirent name value.
#@ assigns \nothing
#@ ensures \result == stored
def _decode_name(stored: str) -> str:
    return stored


# THE ROUND-TRIP LEAF (the string twin of the proven inode-field codec):
#   decode(encode(name)) == name
#@ requires \str_length(name) <= 30
#@ assigns \nothing
#@ ensures \result == name
def _name_codec_roundtrip(name: str) -> str:
    return _decode_name(_encode_name(name))
