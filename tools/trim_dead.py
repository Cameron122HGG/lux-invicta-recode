"""Copy a vanilla/DLC script file into LI with checks against non-existent cultures/religions/dynasties
removed WITHOUT changing behaviour (constant folding).
usage: python -I trim_dead.py <mod_dir> <vanilla_dir> <src file> <dest file> <top-level unit name> [--apply]
  top-level unit: the block that may be dropped when it can never match (e.g. 'reason' or 'modifier')"""
import os, re, sys
args = [a for a in sys.argv[1:] if a != '--apply']; APPLY = '--apply' in sys.argv
R, V, SRC, DST, UNITS = args[0], args[1], args[2], args[3], set(args[4].split(','))

def nc(t): return re.sub(r'#[^\n]*', '', t)
def rd(p): return open(p, 'rb').read().decode('cp1252', 'replace')
def topkeys(d, depth_want=0, inner=False):
    s = set()
    for dp, _, fs in os.walk(os.path.join(R, d)):
        for f in fs:
            t = nc(rd(os.path.join(dp, f))); dep = 0
            for m in re.finditer(r'([\w-]+)\s*=\s*\{|\{|\}', t):
                x = m.group(0)
                if x == '{': dep += 1
                elif x == '}': dep -= 1
                else:
                    if dep == depth_want: s.add(m.group(1))
                    dep += 1
    return s
cult_groups = topkeys('common/cultures', 0); cultures = topkeys('common/cultures', 1)
rel_groups = topkeys('common/religions', 0); religions = topkeys('common/religions', 1)
dyn = set()
for f in os.listdir(os.path.join(R, 'common/dynasties')):
    dyn |= set(re.findall(r'(?m)^\s*(\d+)\s*=\s*\{', nc(rd(os.path.join(R, 'common/dynasties', f)))))
traits = topkeys('common/traits', 0); artifacts = topkeys('common/artifacts', 0)
societies = topkeys('common/societies', 0)
titles = set()
for dp, _, fs in os.walk(os.path.join(R, 'common/landed_titles')):
    for f in fs: titles |= set(re.findall(r'\b([ekdcb]_[\w-]+)\s*=\s*\{', nc(rd(os.path.join(dp, f)))))
VALID = {'culture': cultures, 'culture_group': cult_groups, 'religion': religions, 'religion_group': rel_groups,
         'dynasty': dyn, 'true_religion': religions, 'secret_religion': religions, 'graphical_culture': None,
         'trait': traits, 'artifact_type': artifacts, 'has_artifact': artifacts,
         'has_landed_title': titles, 'title': titles, 'has_claim': titles, 'has_weak_claim': titles,
         'has_strong_claim': titles, 'society_member_of': societies}
# Scope names used in place of a value ("religion = liege", "culture = attacker"). CleanSlate uses
# these a lot; they are only resolved at runtime, so they are never "dead".
SCOPE_WORDS = {'liege', 'top_liege', 'owner', 'controller', 'location', 'capital_scope', 'holder', 'holder_scope',
               'attacker', 'defender', 'thirdparty', 'educator', 'employer', 'host', 'father', 'mother', 'spouse',
               'real_father', 'mother_even_if_dead', 'father_even_if_dead', 'guardian', 'lover', 'killer',
               'primary_title', 'culture', 'religion', 'heir', 'player_heir', 'regent', 'betrothed', 'current_heir'}
def leaf_dead(k, v):
    if v is None: return False   # bare list entry, no value
    v = v.strip('"')
    if k not in VALID or VALID[k] is None: return False
    if k == 'title' and not re.match(r'[ekdcb]_', v): return False  # 'title = X' with a non-title value (e.g. a loc key)
    if v in ('ROOT', 'FROM', 'PREV', 'THIS', 'none', 'random', 'yes', 'no') or v.startswith(('event_target', 'ROOT', 'FROM', 'PREV', 'THIS')): return False
    if v in SCOPE_WORDS or v.endswith(('_scope', '_title')) or ':' in v: return False
    # "religion = d_knights_templar" means "same religion as that title's holder": a scope, not a name
    if k not in ('title', 'has_landed_title', 'has_claim', 'has_weak_claim', 'has_strong_claim') and re.match(r'[ekdcb]_', v): return False
    return v not in VALID[k]

# ---- parse into nodes with line spans
src = open(SRC, 'rb').read(); nl = b'\r\n' if b'\r\n' in src else b'\n'
text = src.decode('latin-1'); lines = text.split('\n')
tok = re.compile(r'#[^\n]*|"[^"]*"|\{|\}|=|[^\s{}=#"]+')
toks = []; ln = 1
for m in tok.finditer(text):
    ln_here = text.count('\n', 0, m.start()) + 1
    if not m.group(0).startswith('#'): toks.append((m.group(0), ln_here))
pos = 0
def parse_block():
    global pos
    items = []
    while pos < len(toks) and toks[pos][0] != '}':
        k, l0 = toks[pos]; pos += 1
        if pos < len(toks) and toks[pos][0] == '=':
            pos += 1
            if toks[pos][0] == '{':
                pos += 1; ch = parse_block(); l1 = toks[pos][1]; pos += 1
                items.append({'k': k, 'kids': ch, 'l0': l0, 'l1': l1})
            else:
                v, l1 = toks[pos]; pos += 1
                items.append({'k': k, 'v': v, 'l0': l0, 'l1': l1})
        else:
            items.append({'k': k, 'v': None, 'l0': l0, 'l1': l0})  # bare value (e.g. list entries)
    return items
root = parse_block()

drop = set(); stats = {'leaf removed': 0, 'NOT removed': 0, 'units dropped': 0, 'unsure': 0}
ANDS = {'trigger', 'AND', 'modifier', 'limit', 'potential', 'allow'}; ORS = {'OR'}; NORS = {'NOR'}
# --scopes: every other block (scope changes such as primary_title = {...}, any_x = {...}) is an
# "all of" block too: if one of its checks can never be true, the block can never be true
SCOPES_AS_AND = '--scopes' in sys.argv
# blocks that are not "all of" triggers: their value is never passed up (dead entries inside their
# own OR lists can still be removed)
OPAQUE = {'trigger_else', 'if', 'else_if', 'else', 'while', 'calc_true_if', 'ai_chance', 'chance', 'mean_time_to_happen',
          'option', 'immediate', 'after', 'effect', 'hidden_effect', 'random_list', 'random', 'weight_multiplier',
          'trigger_switch', 'switch', 'break_if', 'ai_will_do', 'ai_target_filter'}
def span(n): return set(range(n['l0'], n['l1'] + 1))
def fold(n, ctx):
    """returns 'F' (always false), 'T' (always true) or None (unknown); marks droppable lines"""
    if 'v' in n:
        return 'F' if leaf_dead(n['k'], n['v']) else None
    k = n['k']; kids = n['kids']
    vals = [(c, fold(c, k)) for c in kids]
    if k == 'NOT':
        if len(kids) == 1 and vals[0][1] == 'F': return 'T'
        if any(v == 'F' for _, v in vals): stats['unsure'] += 1
        return None
    if k == 'NAND':                       # not (all of): one dead child makes it always true
        return 'T' if any(v == 'F' for _, v in vals) else None
    if k in ('trigger_if', 'trigger_else_if'):
        # a trigger_if whose limit can never hold is skipped, so it PASSES (true), not false
        lim = [v for c, v in vals if c['k'] == 'limit']
        return 'T' if lim and lim[0] == 'F' else None
    if k in OPAQUE: return None           # effects, weights, counts: nothing to pass up
    if k in ORS or k in NORS:
        live = [v for c, v in vals if v != 'F']
        # never empty the list: an all-dead OR/NOR keeps its entries (its value is passed up instead)
        if not live: return 'T' if k in NORS else 'F'
        for c, v in vals:
            if v == 'F': drop.update(span(c)); stats['leaf removed' if 'v' in c else 'NOT removed'] += 1
        return None
    if k in ANDS or k in UNITS or SCOPES_AS_AND:
        if any(v == 'F' for _, v in vals): return 'F'
        for i, (c, v) in enumerate(vals):
            if v != 'T': continue
            # never remove a trigger_if / trigger_else_if that a trigger_else(_if) follows: the chain would break
            nxt = vals[i + 1][0]['k'] if i + 1 < len(vals) else None
            if c['k'] in ('trigger_if', 'trigger_else_if') and nxt in ('trigger_else', 'trigger_else_if'): continue
            drop.update(span(c)); stats['NOT removed'] += 1
        return None
    return None
def walk_units(items):
    for n in items:
        if 'kids' not in n: continue
        if n['k'] in UNITS:
            r = fold(n, None)
            if r == 'F':
                drop.update(span(n)); stats['units dropped'] += 1
        else:
            walk_units(n['kids'])
walk_units(root)
# --defs: also fold every top-level definition (scripted triggers etc.), so dead entries in their
# OR/NOR lists and always-true NOTs are removed too. A definition itself is never dropped.
if '--defs' in sys.argv:
    for n in root:
        if 'kids' in n: fold(n, None)

# safety: no kept leaf may sit on a dropped line (lines are removed whole)
def leaves(items, inside_dropped=False):
    for n in items:
        nd = inside_dropped or span(n) <= drop
        if 'kids' in n: yield from leaves(n['kids'], nd)
        else: yield n, nd
clash = [(n['k'], n.get('v'), n['l0']) for n, nd in leaves(root) if not nd and n['l0'] in drop]
assert not clash, ('kept checks share a dropped line', clash[:5])
left = [(n['k'], n['v'], n['l0']) for n, nd in leaves(root) if not nd and 'v' in n and n['v'] and leaf_dead(n['k'], n['v'])]
print('dead checks left untouched (could not prove safe to remove):', len(left), left[:12])
out =[l for i, l in enumerate(lines, 1) if i not in drop]
res = '\n'.join(out)
chk = nc(res); assert chk.count('{') == chk.count('}'), 'brace mismatch'
print(stats, '| lines', len(lines), '->', len(out))
if APPLY:
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    hdr = ('# Lux Invicta copy of the vanilla/DLC file "' + os.path.basename(SRC) + '": checks for cultures, religions\n'
           '# and dynasties that do not exist in LI were removed (behaviour otherwise unchanged; units that could\n'
           '# never match were dropped).\n')
    open(DST, 'wb').write((hdr + res).replace('\r\n', '\n').replace('\n', nl.decode()).encode('latin-1'))
    print('written', DST)
