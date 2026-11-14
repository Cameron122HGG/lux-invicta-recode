"""Collect vanilla game_rule_events (GR.x) blocks plus the GR events they call, and check their dependencies.
usage: python -I gr_deps.py <vanilla_dir> <mod_dir> "GR.14,GR.30" <out.txt>"""
import re, os, sys
V, R = sys.argv[1:3]
WANT = sys.argv[3].split(',')
def rd(p): return open(p, 'rb').read().decode('cp1252', 'replace')
def nc(t): return re.sub(r'#[^\n]*', '', t)
vt = rd(V + '/events/game_rule_events.txt')

def block(t, i):
    m = re.search(r'^\w+_event\s*=\s*\{\s*(?:#[^\n]*\s*)*id\s*=\s*' + re.escape(i) + r'\b', t, re.M)
    if not m: return None
    s = m.start(); k = t.find('{', s); d = 0; e = k
    while True:
        c = t[e]
        if c == '#': e = t.find('\n', e); continue
        if c == '{': d += 1
        elif c == '}':
            d -= 1
            if d == 0: return t[s:e + 1]
        e += 1

lidef = set()
for f in os.listdir(R + '/events'):
    if f.endswith('.txt'): lidef |= set(re.findall(r'\bid\s*=\s*([\w.]+)', nc(rd(R + '/events/' + f))))
def keys(d, root):
    s = set()
    p = os.path.join(root, d)
    if not os.path.isdir(p): return s
    for f in os.listdir(p):
        t = nc(rd(os.path.join(p, f))); dep = 0
        for m in re.finditer(r'([\w-]+)\s*=\s*\{|\{|\}', t):
            x = m.group(0)
            if x == '{': dep += 1
            elif x == '}': dep -= 1
            else:
                if dep == 0: s.add(m.group(1))
                dep += 1
    return s
li_se, li_st = keys('common/scripted_effects', R), keys('common/scripted_triggers', R)
va_se, va_st = keys('common/scripted_effects', V), keys('common/scripted_triggers', V)

todo = list(WANT); got = {}
while todo:
    i = todo.pop()
    if i in got: continue
    b = block(vt, i); got[i] = b
    if b is None: print('NOT IN vanilla game_rule_events:', i); continue
    for j in re.findall(r'\bid\s*=\s*([\w.]+)', nc(b))[1:]:
        if j.startswith('GR.') and j not in got and j not in lidef: todo.append(j)
allb = '\n'.join(x for x in got.values() if x)
calls = set(re.findall(r'\b(\w+_(?:effect|trigger))\s*=\s*yes', nc(allb)))
print('events to copy:', sorted(got, key=lambda x: int(x.split('.')[1])), '| total lines', allb.count('\n'))
print('other event ids called:', sorted(set(re.findall(r'\bid\s*=\s*([\w.]+)', nc(allb))) - set(got) - lidef))
miss = sorted(c for c in calls if c not in li_se and c not in li_st)
print('scripted effects/triggers used but missing in LI:', miss)
print('   of those, defined in vanilla:', [c for c in miss if c in va_se or c in va_st])
open(sys.argv[4], 'w', encoding='cp1252', errors='replace').write(allb)
