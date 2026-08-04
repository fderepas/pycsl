from __future__ import annotations
from typing import Any, Dict, List, Set, Tuple
from module6_whyml.identifiers import whyml_ident, safe_mutex_name, safe_exc_name
from module6_whyml.ir_scanner import IRScanner
""  # pycsl
class PreambleEmissionMixin:
    'Preamble emission: top-of-file `use` clauses, exception type declarations, helper let-bindings, axiom blocks, shared state for the concurrent memory model, record/sum type declarations, and opaque class aliases. Mixed into Module6_WhyMLTranspiler.'
    _AXIOM_REGISTRY: int = {'Pycsl.Reference.Gcd.gcd_result_nonneg': 'forall a b : int. a >= 0 -> b >= 0 -> 0 <= gcd a b', 'Pycsl.Reference.Gcd.gcd_result_positive': 'forall a b : int. a >= 0 -> b >= 0 -> (a > 0 \\/ b > 0) -> gcd a b > 0', 'Pycsl.Reference.Gcd.gcd_divides_a': 'forall a b : int. a >= 0 -> b >= 0 -> (a > 0 \\/ b > 0) -> mod a (gcd a b) = 0', 'Pycsl.Reference.Gcd.gcd_divides_b': 'forall a b : int. a >= 0 -> b >= 0 -> (a > 0 \\/ b > 0) -> mod b (gcd a b) = 0', 'Pycsl.Reference.Gcd.gcd_0': 'forall a : int. a >= 0 -> gcd a 0 = a', 'Pycsl.Reference.Gcd.gcd_step': 'forall a b : int. a >= 0 -> b >= 0 -> b > 0 -> gcd a b = gcd b (mod a b)', 'Pycsl.Reference.Gcd.gcd_greatest': 'forall a b k : int. a >= 0 -> b >= 0 -> k >= 0 -> (a > 0 \\/ b > 0) -> k > 0 -> mod a k = 0 -> mod b k = 0 -> k <= gcd a b', 'Pycsl.Reference.Perm.permut_refl': 'forall s : array int. permut s s', 'Pycsl.Reference.Perm.rev_permutation': 'forall s : array int. permut (array_rev s) s', 'Pycsl.Reference.Json.mirror_involution': 'forall x : json. json_mirror (json_mirror x) = x', 'UnixFs.Bitmap.bit_and_one_in_zero_one': 'forall n : int. 0 <= bit_and n 1 /\\ bit_and n 1 < 2', 'UnixFs.Struct.i1a1.round_trip': 'forall fmt : int. forall x0 : int. forall x1 : array int. struct_unpack_i1a1 fmt (struct_pack_i1a1 fmt x0 x1) = (x0, x1)', 'UnixFs.Struct.i2.round_trip': 'forall fmt x0 x1 : int. struct_unpack_i2 fmt (struct_pack_i2 fmt x0 x1) = (x0, x1)', 'UnixFs.Struct.i18.round_trip': 'forall fmt x0 x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14 x15 x16 x17 : int. struct_unpack_i18 fmt (struct_pack_i18 fmt x0 x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14 x15 x16 x17) = (x0, x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15, x16, x17)', 'UnixFs.Dir.scan_reflects_present': 'forall disk : array int. forall blk : int. forall name : string. ( forall j : int. 0 <= j < 16 -> slot_inode disk blk j >= 0 ) -> ( ( dir_lookup disk blk name >= 0 ) <-> ( exists k : int. 0 <= k < 16 /\\ slot_inode disk blk k <> 0 /\\ slot_inode disk blk k < 32 /\\ slot_name disk blk k = name ) )', 'UnixFs.Dir.dir_lookup_present_witness': 'forall disk : array int, blk : int, k : int [dir_lookup disk blk (slot_name disk blk k)]. ( forall j : int. 0 <= j < 16 -> slot_inode disk blk j >= 0 ) -> 0 <= k < 16 -> slot_inode disk blk k <> 0 -> slot_inode disk blk k < 32 -> dir_lookup disk blk (slot_name disk blk k) >= 0', 'UnixFs.Dir.dir_lookup_present_zero_frame': 'forall d0 d1 : array int, s : int, name : string [dir_lookup d1 5 name, slot_inode d1 5 s]. 0 <= s < 16 -> slot_inode d1 5 s = 0 -> ( forall k : int. 0 <= k < 16 -> k <> s ->     slot_inode d1 5 k = slot_inode d0 5 k /\\     slot_name  d1 5 k = slot_name  d0 5 k ) -> name <> slot_name d0 5 s -> dir_lookup d0 5 name >= 0 -> dir_lookup d1 5 name >= 0', 'UnixFs.Content.block_content_eq_intro': 'forall d : array int, blk : int, data : array int [block_content_eq d blk data]. ( forall i : int. 0 <= i < Array.length data -> d[blk * 512 + i] = data[i] ) -> block_content_eq d blk data', 'UnixFs.Content.block_content_eq_elim': 'forall d : array int, blk : int, data : array int [block_content_eq d blk data]. block_content_eq d blk data -> ( forall i : int. 0 <= i < Array.length data -> d[blk * 512 + i] = data[i] )', 'UnixFs.Dir.slot_inode_nonneg': 'forall disk : array int. forall blk : int. forall k : int. slot_inode disk blk k >= 0', 'UnixFs.Dir.slot_inode_byte_decode': 'forall disk : array int. forall blk : int. forall k : int. forall b0 b1 : int [disk[blk * 512 + 32 * k]]. disk[blk * 512 + 32 * k] = b0 -> disk[blk * 512 + 32 * k + 1] = b1 -> slot_inode disk blk k = 256 * b0 + b1', 'UnixFs.Dir.slot_name_byte_decode': 'forall disk : array int. forall blk : int. forall k : int [disk[blk * 512 + 32 * k + 2]]. slot_name disk blk k = field_to_str disk (blk * 512 + 32 * k + 2) 30', 'UnixFs.Dir.remove_reflects_absent': 'forall disk : array int. forall blk : int. forall name : string. forall s : int. ( forall j : int. slot_inode disk blk j >= 0 ) -> ( 0 <= s < 16 ) -> ( slot_inode disk blk s = 0 ) -> ( forall k : int. 0 <= k < 16 -> k <> s ->     slot_name disk blk k = name -> slot_inode disk blk k = 0 ) -> dir_lookup disk blk name < 0', 'UnixFs.Dir.remove_unique_absent': 'forall d0 d1 : array int, s : int [slot_inode d1 5 s, slot_inode d0 5 s]. uniq d0 -> slots_lt32 d0 -> 0 <= s < 16 -> slot_inode d0 5 s <> 0 -> slot_inode d1 5 s = 0 -> ( forall k : int. 0 <= k < 16 -> k <> s ->     slot_inode d1 5 k = slot_inode d0 5 k ) -> ( forall k : int. 0 <= k < 16 -> k <> s ->     slot_name  d1 5 k = slot_name  d0 5 k ) -> ( forall k : int. 0 <= k < 16 -> k <> s ->     slot_name d1 5 k = slot_name d0 5 s -> slot_inode d1 5 k = 0 )', 'UnixFs.Dir.dir_lookup_remove_absent': 'forall d0 d1 : array int, s : int [slot_inode d1 5 s, slot_inode d0 5 s]. ( forall j : int. slot_inode d1 5 j >= 0 ) -> uniq d0 -> slots_lt32 d0 -> 0 <= s < 16 -> slot_inode d0 5 s <> 0 -> slot_inode d1 5 s = 0 -> ( forall k : int. 0 <= k < 16 -> k <> s ->     slot_inode d1 5 k = slot_inode d0 5 k ) -> ( forall k : int. 0 <= k < 16 -> k <> s ->     slot_name  d1 5 k = slot_name  d0 5 k ) -> dir_lookup d1 5 (slot_name d0 5 s) < 0', 'UnixFs.Dir.establish_uniq': 'forall d : array int [uniq d]. ( forall k : int. 0 <= k < 16 -> slot_inode d 5 k = 0 ) -> uniq d', 'UnixFs.Dir.establish_slots_lt32': 'forall d : array int [slots_lt32 d]. ( forall k : int. 0 <= k < 16 -> slot_inode d 5 k = 0 ) -> slots_lt32 d', 'UnixFs.Dir.zero_preserves_uniq': 'forall d0 d1 : array int, s : int [slot_inode d1 5 s, uniq d0]. uniq d0 -> slot_inode d1 5 s = 0 -> ( forall k : int. 0 <= k < 16 -> k <> s ->     slot_inode d1 5 k = slot_inode d0 5 k /\\     slot_name  d1 5 k = slot_name  d0 5 k ) -> uniq d1', 'UnixFs.Dir.zero_preserves_slots_lt32': 'forall d0 d1 : array int, s : int [slot_inode d1 5 s, slots_lt32 d0]. slots_lt32 d0 -> slot_inode d1 5 s = 0 -> ( forall k : int. 0 <= k < 16 -> k <> s ->     slot_inode d1 5 k = slot_inode d0 5 k ) -> slots_lt32 d1', 'UnixFs.Dir.insert_preserves_uniq_folded': 'forall d0 d1 : array int, s : int [slot_name d1 5 s, uniq d0]. uniq d0 -> 0 <= s < 16 -> ( forall k : int. 0 <= k < 16 ->     slot_inode d0 5 k <> 0 -> slot_inode d0 5 k < 32 ->     slot_name d0 5 k <> slot_name d1 5 s ) -> ( forall k : int. 0 <= k < 16 -> k <> s ->     slot_inode d1 5 k = slot_inode d0 5 k /\\     slot_name  d1 5 k = slot_name  d0 5 k ) -> ( slot_inode d1 5 s <> 0 -> slot_inode d1 5 s < 32 ) -> uniq d1', 'UnixFs.Dir.insert_preserves_slots_lt32': 'forall d0 d1 : array int, s : int [slot_inode d1 5 s, slots_lt32 d0]. slots_lt32 d0 -> 0 <= s < 16 -> slot_inode d1 5 s < 32 -> ( forall k : int. 0 <= k < 16 -> k <> s ->     slot_inode d1 5 k = slot_inode d0 5 k ) -> slots_lt32 d1', 'UnixFs.Dir.dir_blit_marker_intro': 'forall d0 d1 : array int, s b0 b1 : int, name : string [dir_blit_marker d0 d1 s b0 b1 name]. 0 <= String.length name -> String.length name <= 30 -> d1[2560 + 32 * s] = b0 -> d1[2560 + 32 * s + 1] = b1 -> ( forall i : int. 0 <= i < String.length name ->     Char.code (Char.get name i) <> 0 ) -> ( forall i : int. 0 <= i < String.length name ->     d1[2560 + 32 * s + 2 + i] = Char.code (Char.get name i) ) -> ( String.length name < 30 -> d1[2560 + 32 * s + 2 + String.length name] = 0 ) -> ( forall b : int. 0 <= b < 512 ->     (b < 32 * s \\/ 32 * s + 32 <= b) -> d1[2560 + b] = d0[2560 + b] ) -> dir_blit_marker d0 d1 s b0 b1 name', 'UnixFs.Dir.dir_blit_marker_intro_zero': 'forall d0 d1 : array int, s b0 b1 : int, name : string [dir_blit_marker d0 d1 s b0 b1 name]. String.length name = 0 -> d1[2560 + 32 * s] = b0 -> d1[2560 + 32 * s + 1] = b1 -> d1[2560 + 32 * s + 2] = 0 -> ( forall b : int. 0 <= b < 512 ->     (b < 32 * s \\/ 32 * s + 32 <= b) -> d1[2560 + b] = d0[2560 + b] ) -> dir_blit_marker d0 d1 s b0 b1 name', 'UnixFs.Dir.dir_blit_marker_insert': 'forall d0 d1 : array int, s b0 b1 : int, name : string [dir_blit_marker d0 d1 s b0 b1 name]. dir_blit_marker d0 d1 s b0 b1 name -> uniq d0 -> slots_lt32 d0 -> 0 <= s < 16 -> 256 * b0 + b1 <> 0 -> 256 * b0 + b1 < 32 -> ( forall k : int. 0 <= k < 16 -> k <> s ->     slot_inode d0 5 k <> 0 -> slot_inode d0 5 k < 32 ->     slot_name d0 5 k <> name ) -> ( slot_inode d1 5 s = 256 * b0 + b1   /\\ slot_name d1 5 s = name   /\\ ( forall k : int. 0 <= k < 16 -> k <> s ->          slot_inode d1 5 k = slot_inode d0 5 k /\\          slot_name  d1 5 k = slot_name  d0 5 k )   /\\ uniq d1 /\\ slots_lt32 d1 )', 'UnixFs.Dir.dir_blit_marker_frame_only': 'forall d0 d1 : array int, s b0 b1 : int, name : string [dir_blit_marker d0 d1 s b0 b1 name]. dir_blit_marker d0 d1 s b0 b1 name -> 0 <= s < 16 -> ( forall k : int. 0 <= k < 16 -> k <> s ->     slot_inode d1 5 k = slot_inode d0 5 k /\\     slot_name  d1 5 k = slot_name  d0 5 k )', 'UnixFs.Dir.dir_blit_marker_value_inode': 'forall d0 d1 : array int, s b0 b1 : int, name : string [dir_blit_marker d0 d1 s b0 b1 name]. dir_blit_marker d0 d1 s b0 b1 name -> slot_inode d1 5 s = 256 * b0 + b1', 'UnixFs.Dir.dir_scan_prefix_base': 'forall d : array int, blk : int, name : string [dir_scan_prefix d blk name 0 (-1)]. dir_scan_prefix d blk name 0 (-1)', 'UnixFs.Dir.dir_scan_prefix_step': 'forall d : array int, blk i r : int, name : string [dir_scan_prefix d blk name i r]. 0 <= i -> i < 16 -> dir_scan_prefix d blk name i r -> ( ( slot_inode d blk i <> 0 /\\ slot_inode d blk i < 32       /\\ slot_name d blk i = name ) ->     dir_scan_prefix d blk name (i + 1) (slot_inode d blk i) ) /\\ ( not ( slot_inode d blk i <> 0 /\\ slot_inode d blk i < 32              /\\ slot_name d blk i = name ) ->     dir_scan_prefix d blk name (i + 1) r )', 'UnixFs.Dir.dir_scan_result_intro': 'forall d : array int, blk r : int, name : string [dir_scan_prefix d blk name 16 r]. dir_scan_prefix d blk name 16 r -> dir_scan_result d blk name r', 'UnixFs.Dir.dir_scan_result_value': 'forall d : array int, blk r : int, name : string [dir_scan_result d blk name r]. dir_scan_result d blk name r -> dir_lookup d blk name = r', 'UnixFs.Dir.dir_find_slot_prefix_base': 'forall d : array int, blk : int, name : string [dir_find_slot_prefix d blk name 0 (-1)]. dir_find_slot_prefix d blk name 0 (-1)', 'UnixFs.Dir.dir_find_slot_prefix_step': 'forall d : array int, blk i r : int, name : string [dir_find_slot_prefix d blk name i r]. 0 <= i -> i < 16 -> dir_find_slot_prefix d blk name i r -> ( ( slot_inode d blk i <> 0 /\\ slot_inode d blk i < 32       /\\ slot_name d blk i = name ) ->     dir_find_slot_prefix d blk name (i + 1) i ) /\\ ( not ( slot_inode d blk i <> 0 /\\ slot_inode d blk i < 32              /\\ slot_name d blk i = name ) ->     dir_find_slot_prefix d blk name (i + 1) r )', 'UnixFs.Dir.dir_find_slot_result_intro': 'forall d : array int, blk r : int, name : string [dir_find_slot_prefix d blk name 16 r]. dir_find_slot_prefix d blk name 16 r -> dir_find_slot_result d blk name r', 'UnixFs.Dir.dir_find_slot_result_value': 'forall d : array int, blk r : int, name : string [dir_find_slot_result d blk name r]. dir_find_slot_result d blk name r -> r >= 0 -> slot_inode d blk r <> 0 /\\ slot_name d blk r = name', 'UnixFs.Dir.dir_find_free_prefix_base': 'forall d : array int, blk : int [dir_find_free_prefix d blk 0 (-1)]. dir_find_free_prefix d blk 0 (-1)', 'UnixFs.Dir.dir_find_free_prefix_step': 'forall d : array int, blk i r : int [dir_find_free_prefix d blk i r]. 0 <= i -> i < 16 -> dir_find_free_prefix d blk i r -> ( ( slot_inode d blk i = 0 ) ->     dir_find_free_prefix d blk (i + 1) i ) /\\ ( ( slot_inode d blk i <> 0 ) ->     dir_find_free_prefix d blk (i + 1) r )', 'UnixFs.Dir.dir_find_free_result_intro': 'forall d : array int, blk r : int [dir_find_free_prefix d blk 16 r]. dir_find_free_prefix d blk 16 r -> dir_find_free_result d blk r', 'UnixFs.Dir.dir_find_free_result_value': 'forall d : array int, blk r : int [dir_find_free_result d blk r]. dir_find_free_result d blk r -> r >= 0 -> slot_inode d blk r = 0', 'UnixFs.Dir.dir_blit_marker_at_intro': 'forall d0 d1 : array int, blk s b0 b1 : int, name : string [dir_blit_marker_at d0 d1 blk s b0 b1 name]. 0 <= String.length name -> String.length name <= 30 -> d1[blk * 512 + 32 * s] = b0 -> d1[blk * 512 + 32 * s + 1] = b1 -> ( forall i : int. 0 <= i < String.length name ->     Char.code (Char.get name i) <> 0 ) -> ( forall i : int. 0 <= i < String.length name ->     d1[blk * 512 + 32 * s + 2 + i] = Char.code (Char.get name i) ) -> ( String.length name < 30 ->     d1[blk * 512 + 32 * s + 2 + String.length name] = 0 ) -> ( forall b : int. 0 <= b < 512 ->     (b < 32 * s \\/ 32 * s + 32 <= b) ->     d1[blk * 512 + b] = d0[blk * 512 + b] ) -> dir_blit_marker_at d0 d1 blk s b0 b1 name', 'UnixFs.Dir.dir_blit_marker_at_value_inode': 'forall d0 d1 : array int, blk s b0 b1 : int, name : string [dir_blit_marker_at d0 d1 blk s b0 b1 name]. dir_blit_marker_at d0 d1 blk s b0 b1 name -> slot_inode d1 blk s = 256 * b0 + b1', 'UnixFs.Dir.dir_blit_marker_at_value_name': 'forall d0 d1 : array int, blk s b0 b1 : int, name : string [dir_blit_marker_at d0 d1 blk s b0 b1 name]. dir_blit_marker_at d0 d1 blk s b0 b1 name -> slot_name d1 blk s = name', 'UnixFs.Dir.dir_blit_marker_at_frame_only': 'forall d0 d1 : array int, blk s b0 b1 : int, name : string [dir_blit_marker_at d0 d1 blk s b0 b1 name]. dir_blit_marker_at d0 d1 blk s b0 b1 name -> 0 <= s < 16 -> ( forall k : int. 0 <= k < 16 -> k <> s ->     slot_inode d1 blk k = slot_inode d0 blk k /\\     slot_name  d1 blk k = slot_name  d0 blk k )', 'UnixFs.Dir.dir_lookup_frame': 'forall d0 d1 : array int, name : string [dir_lookup d1 5 name, dir_lookup d0 5 name]. ( forall k : int. 0 <= k < 16 ->     slot_inode d1 5 k = slot_inode d0 5 k /\\     slot_name  d1 5 k = slot_name  d0 5 k ) -> dir_lookup d1 5 name = dir_lookup d0 5 name', 'UnixFs.Dir.insert_preserves_unique': 'forall d0 : array int. forall d1 : array int. forall blk : int. forall s : int. forall nm : string. ( forall j : int. 0 <= j < 16 -> slot_inode d0 blk j >= 0 ) -> ( 0 <= s < 16 ) -> ( forall i j : int. 0 <= i < 16 -> 0 <= j < 16 ->     slot_inode d0 blk i <> 0 -> slot_inode d0 blk i < 32 ->     slot_inode d0 blk j <> 0 -> slot_inode d0 blk j < 32 ->     slot_name d0 blk i = slot_name d0 blk j -> i = j ) -> ( forall k : int. 0 <= k < 16 ->     slot_inode d0 blk k <> 0 -> slot_inode d0 blk k < 32 ->     slot_name d0 blk k <> nm ) -> ( forall k : int. 0 <= k < 16 -> k <> s ->     slot_inode d1 blk k = slot_inode d0 blk k /\\     slot_name  d1 blk k = slot_name  d0 blk k ) -> ( slot_inode d1 blk s <> 0 -> slot_inode d1 blk s < 32 ) -> ( slot_name  d1 blk s = nm ) -> ( forall i j : int. 0 <= i < 16 -> 0 <= j < 16 ->     slot_inode d1 blk i <> 0 -> slot_inode d1 blk i < 32 ->     slot_inode d1 blk j <> 0 -> slot_inode d1 blk j < 32 ->     slot_name d1 blk i = slot_name d1 blk j -> i = j )', 'UnixFs.Dir.empty_disk_slots_dead': 'forall disk : array int. forall blk : int. ( forall b : int. blk * 512 <= b < blk * 512 + 512 -> disk[b] = 0 ) -> ( forall k : int. 0 <= k < 16 -> slot_inode disk blk k = 0 )', 'UnixFs.Dir.uniq_intro': 'forall d : array int [uniq d]. ( forall i j : int. (0 <= i < 16 /\\ 0 <= j < 16 /\\ slot_inode d 5 i <> 0 /\\ slot_inode d 5 i < 32 /\\ slot_inode d 5 j <> 0 /\\ slot_inode d 5 j < 32 /\\ slot_name d 5 i = slot_name d 5 j) -> i = j) -> uniq d', 'UnixFs.Dir.uniq_elim': 'forall d : array int [uniq d]. uniq d -> ( forall i j : int. (0 <= i < 16 /\\ 0 <= j < 16 /\\ slot_inode d 5 i <> 0 /\\ slot_inode d 5 i < 32 /\\ slot_inode d 5 j <> 0 /\\ slot_inode d 5 j < 32 /\\ slot_name d 5 i = slot_name d 5 j) -> i = j)', 'UnixFs.Dir.ibv_intro': 'forall d : array int [inode_bytes_valid d]. ( forall i : int. 512 <= i < 2560 -> 0 <= d[i] <= 255 ) -> inode_bytes_valid d', 'UnixFs.Dir.ibv_elim': 'forall d : array int [inode_bytes_valid d]. inode_bytes_valid d -> ( forall i : int. 512 <= i < 2560 -> 0 <= d[i] <= 255 )', 'UnixFs.Dir.slots_lt32_intro': 'forall d : array int [slots_lt32 d]. ( forall k : int. 0 <= k < 16 -> slot_inode d 5 k < 32 ) -> slots_lt32 d', 'UnixFs.Dir.slots_lt32_elim': 'forall d : array int [slots_lt32 d]. slots_lt32 d -> ( forall k : int. 0 <= k < 16 -> slot_inode d 5 k < 32 )', 'UnixFs.Field.field_to_str_round_trip': 'forall d : array int. forall off width : int. forall name : string [field_to_str d off width]. 0 <= String.length name -> String.length name <= width -> ( forall i : int. 0 <= i < String.length name ->     Char.code (Char.get name i) <> 0 ) -> ( forall i : int. 0 <= i < String.length name ->     d[off + i] = Char.code (Char.get name i) ) -> ( String.length name < width -> d[off + String.length name] = 0 ) -> field_to_str d off width = name', 'UnixFs.Field.field_to_str_frame': 'forall d0 d1 : array int. forall off width : int [field_to_str d1 off width, field_to_str d0 off width]. 0 <= width -> ( forall i : int. 0 <= i < width -> d0[off + i] = d1[off + i] ) -> field_to_str d0 off width = field_to_str d1 off width', 'Pycsl.Reference.FieldPred.field_nonneg_intro': 'forall x : int [field_nonneg x]. x >= 0 -> field_nonneg x', 'Pycsl.Reference.FieldPred.field_nonneg_elim': 'forall x : int [field_nonneg x]. field_nonneg x -> x >= 0', 'Pycsl.Strmod.StrLen.length_nonneg': 'forall s : string. String.length s >= 0', 'Pycsl.Strmod.Capwords.capwords_length_nongrowing': 'forall s : string. String.length (capwords_def s) <= String.length s', 'Pycsl.Strmod.Capwords.capwords_empty': 'capwords_def "" = ""'}
    _CLASS_INV_AXIOMS: frozenset = frozenset({'UnixFs.Dir.empty_disk_slots_dead', 'UnixFs.Dir.ibv_intro', 'UnixFs.Dir.ibv_elim', 'UnixFs.Content.block_content_eq_intro', 'UnixFs.Content.block_content_eq_elim', 'UnixFs.Dir.establish_uniq', 'UnixFs.Dir.establish_slots_lt32', 'Pycsl.Reference.FieldPred.field_nonneg_intro', 'Pycsl.Reference.FieldPred.field_nonneg_elim'})
    _DEFINITIONAL_AXIOMS: frozenset = frozenset({'UnixFs.Dir.ibv_intro', 'UnixFs.Dir.ibv_elim', 'UnixFs.Content.block_content_eq_intro', 'UnixFs.Content.block_content_eq_elim', 'Pycsl.Reference.FieldPred.field_nonneg_intro', 'Pycsl.Reference.FieldPred.field_nonneg_elim'})
    _AXIOM_FUNCTIONS: Dict[str, List[str]] = {'Pycsl.Reference.Gcd.': ['function gcd (a : int) (b : int) : int'], 'Pycsl.Reference.FieldPred.': ['predicate field_nonneg (x: int)'], 'Pycsl.Strmod.Capwords.': ['val function capwords_def (s: string) : string'], 'UnixFs.Field.': ['val function field_to_str (d: array int) (off: int) (width: int) : string'], 'Pycsl.Reference.Perm.': ['predicate permut (a: array int) (b: array int)'], 'Pycsl.Reference.Perm.rev_permutation': ['val function array_rev (a: array int) : array int'], 'Pycsl.Reference.Json.': ['val function json_mirror (x: json) : json'], 'UnixFs.Bitmap.': ['val function bit_and (x : int) (y : int) : int'], 'UnixFs.Struct.i1a1.': ['val function struct_pack_i1a1 (fmt: int) (x0: int) (x1: array int) : array int\n    ensures { Array.length result = 32 }', 'val function struct_unpack_i1a1 (fmt: int) (data: array int) : (int, array int)'], 'UnixFs.Struct.i2.': ['val function struct_pack_i2 (fmt: int) (x0: int) (x1: int) : array int', 'val function struct_unpack_i2 (fmt: int) (data: array int) : (int, int)'], 'UnixFs.Struct.i18.': ['val function struct_pack_i18 (fmt: int) (x0: int) (x1: int) (x2: int) (x3: int) (x4: int) (x5: int) (x6: int) (x7: int) (x8: int) (x9: int) (x10: int) (x11: int) (x12: int) (x13: int) (x14: int) (x15: int) (x16: int) (x17: int) : array int\n    ensures { Array.length result = 64 }', 'val function struct_unpack_i18 (fmt: int) (data: array int) : (int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int)'], 'UnixFs.Content.': ['function inode_size (disk: array int) (ino: int) : int =\n    disk[512 + ino*64 + 0] * 16777216 + disk[512 + ino*64 + 1] * 65536\n    + disk[512 + ino*64 + 2] * 256 + disk[512 + ino*64 + 3]', 'predicate block_content_eq (d: array int) (blk: int) (data: array int)'], 'UnixFs.Dir.': ['val function slot_inode (disk: array int) (blk: int) (k: int) : int', 'val function slot_name  (disk: array int) (blk: int) (k: int) : string', 'val function dir_lookup (disk: array int) (blk: int) (name: string) : int', 'predicate uniq (d: array int)', 'predicate inode_bytes_valid (d: array int)', 'predicate slots_lt32 (d: array int)', 'predicate dir_blit_marker (d0 d1: array int) (s b0 b1: int) (name: string)', 'predicate dir_scan_result (d: array int) (blk: int) (name: string) (r: int)', 'predicate dir_scan_prefix (d: array int) (blk: int) (name: string) (i: int) (r: int)'], 'UnixFs.Dir.dir_find_slot': ['predicate dir_find_slot_result (d: array int) (blk: int) (name: string) (r: int)', 'predicate dir_find_slot_prefix (d: array int) (blk: int) (name: string) (i: int) (r: int)'], 'UnixFs.Dir.dir_find_free': ['predicate dir_find_free_result (d: array int) (blk: int) (r: int)', 'predicate dir_find_free_prefix (d: array int) (blk: int) (i: int) (r: int)'], 'UnixFs.Dir.dir_blit_marker_at': ['predicate dir_blit_marker_at (d0 d1: array int) (blk s b0 b1: int) (name: string)']}
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @staticmethod
    def _func_returns_string_seq(func: Dict[str, Any]) -> bool:
        """str-list-elements: does `func` return a seq local whose elements are STRING
        (`seq_value_types[v] == "string"`)? Such a list is emitted as `array string` and
        carried through the `Return_seq_str (seq string)` exception."""
        svt = func.get("seq_value_types", {})
        if not svt:
            return False
        found = [False]

        def rec(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("stmt") == "Return":
                    v = node.get("value")
                    if (isinstance(v, dict) and v.get("type") == "Var"
                            and svt.get(v.get("name")) == "string"):
                        found[0] = True
                for x in node.values():
                    rec(x)
            elif isinstance(node, list):
                for x in node:
                    rec(x)

        rec(func.get("body", []))
        return found[0]

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _scan_preamble_needs(self, functions: List[int], all_bodies: List[Any]) -> int:
        return {}

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_preamble_uses(self, needs: int, module_name: str='PyCSL_Program') -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_preamble_exceptions(self, needs: int) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_preamble_helpers(self, needs: int) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _inductive_refs_global_or_axiom_func(self, ir: int) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _class_inv_refs_axiom_func(self, ir: int) -> bool:
        return False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _precompute_axiom_logic_funcs(self, ir: int) -> None:
        pass

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_class_inv_axioms(self, ir: int) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_preamble_axioms(self, ir: int) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_preamble_no_exception_predicates(self, needs: int) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_preamble(self, needs: int, module_name: str='PyCSL_Program') -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _collect_critical_mutexes(self) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_shared_state(self) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _mutex_inv_params(self, mutex: str, inv_str: str) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _mutex_inv_application(self, mutex: str, inv_str: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _inductive_referenced_axiom_decls(self, inductive_decls: List[int]) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_uncited_axiom_func_decls(self) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _inductive_sig_whyml(self, signature: str) -> str:
        return ""

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_inductive_decls(self, inductive_decls: List[int]) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _subst_self_in_expr(self, expr: Any, repl: str) -> Any:
        return None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _fresh_globals_facts(self) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_module_globals(self) -> List[str]:
        return []

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_type_decls(self, type_decls: List[int]) -> Tuple[List[str], int]:
        return ([], {})

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _emit_opaque_class_aliases(self, functions: List[int], out: List[str], declared_types: int) -> None:
        pass


