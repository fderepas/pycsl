import json, collections, sys
d=json.load(open('census.json'))
NODE={'type','value','args','func','object','attr','field','left','right','receiver','index','body','elts','slice','op','target','targets','stmt','keys','lower','upper','test','orelse','iter','handlers','cases','generators','base','inner','pattern','alternatives','operand','values','fn','arg','binder','ty','idx'}
PROG={'functions','contracts','requires','ensures','symbol_table','params','return_annotation','kind','self_type','type_params','type_decls','inductive_decls','overrides','sub_method','base_method','raises','fields','field_types','field_value_types','constructors','whyml_name','defaults','no_exception_all','no_exception','formal_params','members','methods','class_invariants','init_body','bases','method','method_deps','sig','module_globals','init_ensures','class','uses','sibling_concrete','proof','trusted','verify_module','from_conforms_to','payload','arity','is_typeddict','field_none_defaults','ordering','act_name','base_type','exc_type','finalbody','name','qualname'}
JSON={'prover-result','answer','term','loc','file-name','start-line','bucket','relied_on_by','vcs','trusted_dependencies','function','summary'}
def cluster(r):
    ops=r.get('ops',{}); ks=collections.Counter(k for k,s,h in r.get('reads',[]))
    f=r['file']
    if f=='pycsl.py' or (ks and set(ks)&JSON and len(set(ks)&JSON)>=len(set(ks))/2): return 'J'
    if 'isinstance(x, dict|list) (generic walk)' in ops and ('.items() iteration' in ops or 'dict comprehension' in ops or '.values() iteration' in ops): return 'G'
    if not ks:
        return 'M' if ops else 'X'
    nnode=sum(n for k,n in ks.items() if k in NODE); nprog=sum(n for k,n in ks.items() if k in PROG and k!='name')
    if 'type' in ks and nnode>=nprog: return 'N'
    if nprog>0 and nprog>=nnode: return 'P'
    if nnode>0: return 'N'
    return 'P'
NAMES={'N':'IR expr/stmt node read (dispatch on node["type"], project value/name/args/...)',
 'P':'IR program/decl record read (functions/contracts/type_params/symbol_table/... lists & nested dicts)',
 'G':'generic Any-tree walker / rebuild (isinstance dict|list + .items()/dict-comp)',
 'J':'external JSON/report record (why3 --json, soundness report)',
 'M':'non-IR keyed map via variable keys (Dict[int,List[CSLNode]], Dict[Tuple,str], module dict, setdefault-append)',
 'X':'no dict read in own body (DICT came from a callee/ripple/unannotated value)'}
rows=collections.defaultdict(list)
for r in d:
    if not r['chain']: continue
    fams=r['chain']['fams']
    if 'DICT' in fams or 'PYVAL' in fams:
        rows[cluster(r)].append(r)
if __name__=='__main__':
    print('cluster | in-chain(DICT|PYVAL) | DICT first | DICT only (all) | DICT only & COMPLETE | names(only)')
    for c in 'NPGJMX':
        L=rows[c]
        first=[r for r in L if r['chain']['fams'] and r['chain']['fams'][0] in ('DICT','PYVAL')]
        only=[r for r in L if set(r['chain']['fams'])<= {'DICT','PYVAL','RIPPLE'}]
        oc=[r for r in only if r['chain']['cat']=='COMPLETE']
        print(c, len(L), len(first), len(only), len(oc), [r['qual'].split('.')[-1] for r in only])
    for c in 'NPGJMX':
        print('==',c,NAMES[c]); print('  ', sorted(r['qual'] for r in rows[c]))
    # key/shape/op profile per cluster
    for c in 'NPGJ':
        ks=collections.Counter(); sh=collections.defaultdict(collections.Counter); ops=collections.Counter()
        for r in rows[c]:
            for k,s,h in r.get('reads',[]): ks[k]+=1; sh[k][s]+=1
            for o in r.get('ops',{}): ops[o]+=1
        print('##',c,'keys:',[(k,n,sh[k].most_common(2)) for k,n in ks.most_common(12)])
        print('   ops:',ops.most_common(12))
