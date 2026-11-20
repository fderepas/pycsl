# u58 witness 10302: a BARE local `lark/` (namespace portion) in an --import-path root.
print("LOCAL lark/utils.py loaded:", __file__)


#@ ensures \result == False
#@ assigns \nothing
def is_id_start(s: str) -> bool:
    return False
