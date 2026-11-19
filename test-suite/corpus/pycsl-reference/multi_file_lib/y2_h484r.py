"""Helper for corpus 7678 (route #484): a PEER that rebinds y2_h484g.g with `setattr`."""
import multi_file_lib.y2_h484g as m
setattr(m, 'g', lambda x: 0)
