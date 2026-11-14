"""Restore vanilla scripted triggers/effects CleanSlate removed but LI text still calls.
usage: restore_scripted.py <repo> <master_tree> <error.log> [--apply]"""
import os, re, sys, glob
REPO, MASTER, LOG = sys.argv[1:4]; APPLY = '--apply' in sys.argv
CS = os.path.join(REPO, 'cleanslate_beta7')
# --- CleanSlate rename map (same parsing as tools/cs_renames.py)
WANT = {'= Traits =', '= Event/opinion modifiers =', '= Scripted triggers/effects =', '= Decisions =', '= Combat tactics'}
log = open(os.path.join(CS, 'master_changelog.txt'), 'rb').read().decode('latin-1').replace('\r', '')
REN = {}
for m in re.finditer(r'(?m)^(Renamed[^\n]*)\n((?:[ \t]*-[^\n]*->[^\n]*\n)+)', log):
    s = log.rfind('\n= ', 0, m.start()); sec = log[s:log.find('\n', s + 1)].strip()
    if not any(sec.startswith(w) for w in WANT): continue
    for a, b in re.findall(r'-\s*([\w.]+)\s*->\s*([\w.]+)', m.group(2)): REN[a] = b
REN['has_typhoid_fever'] = 'slow_fever' if 'has_typhoid_fever' in REN else REN.get('has_typhoid_fever')
REN = {a: b for a, b in REN.items() if b}
pat = re.compile(r'(?<![\w.:@])(' + '|'.join(sorted(map(re.escape, REN), key=len, reverse=True)) + r')(?![\w.:@])')

def defs(root, kind):
    out = {}
    for f in sorted(glob.glob(os.path.join(root, 'common', kind, '*.txt'))):
        s = open(f, 'rb').read().decode('latin-1')
        for m in re.finditer(r'(?m)^([A-Za-z_][\w]*)[ \t]*=[ \t]*\{', s):
            d = 0; i = m.end() - 1
            while True:
                c = s[i]
                if c == '#': i = s.find('\n', i); continue
                if c == '"': i = s.find('"', i + 1) + 1; continue
                if c == '{': d += 1
                elif c == '}':
                    d -= 1
                    if d == 0: break
                i += 1
            # include comment lines directly above
            st = m.start()
            while True:
                p = s.rfind('\n', 0, st - 1) + 1
                if st > 0 and s[p:st].lstrip().startswith('#'): st = p
                else: break
            out[m.group(1)] = (s[st:i + 1].replace('\r\n', '\n'), os.path.basename(f))
    return out
names = set()
for l in open(LOG, encoding='cp1252', errors='replace'):
    m = re.search(r'Unknown (?:effect|trigger)-type: "(\w+_(?:effect|trigger))"', l)
    if m: names.add(m.group(1))
have = {k: set(defs(REPO, k)) for k in ('scripted_triggers', 'scripted_effects')}
mdefs = {k: defs(MASTER, k) for k in ('scripted_triggers', 'scripted_effects')}
want = {k: {} for k in mdefs}
todo = sorted(names); missing = []
while todo:
    n = todo.pop()
    for k in mdefs:
        if n in mdefs[k] and n not in have[k] and n not in want[k]:
            want[k][n] = mdefs[k][n]
            body = re.sub(r'#[^\n]*', '', mdefs[k][n][0])
            for t in set(re.findall(r'\b(\w+_(?:trigger|effect))\s*=', body)):
                if t != n and not any(t in have[x] for x in have): todo.append(t)
            break
    else:
        if not any(n in have[x] or n in want[x] for x in have): missing.append(n)
print('restore:', {k: sorted(v) for k, v in want.items()})
print('not found anywhere:', missing)
HDR = ('# LI: vanilla 3.3.3 scripted {} that CleanSlate removed (see its master_changelog.txt), restored from master\n'
       '# because LI text (LI-wins definitions, restored events, li_* files) still calls them. CleanSlate renames applied.\n'
       '# 000_ prefix: loads before the files that use them.\n\n')
def calls_other(text):  # callees first, so a definition never calls one further down the file
    body = re.sub(r'#[^\n]*', '', text.split('{', 1)[1])
    return bool(re.search(r'\b\w+_(?:trigger|effect)\s*=', body))
for k, d in want.items():
    if not d: continue
    txt = HDR.format(k.split('_')[1]) + '\n\n'.join(pat.sub(lambda m: REN[m.group(1)], v[0]).strip('\n') + '\n' for v in
                                                   sorted(d.values(), key=lambda v: (calls_other(v[0]), v[1])))
    renamed = sorted(set(m.group(1) for v in d.values() for m in pat.finditer(re.sub(r'#[^\n]*', '', v[0]))))
    print(k, len(d), 'defs; renames applied:', renamed)
    out = os.path.join(REPO, 'common', k, '000_li_restored_' + k + '.txt')
    if APPLY: open(out, 'wb').write(txt.replace('\n', '\r\n').encode('latin-1'))
    else: open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dry_' + k + '.txt'), 'w', encoding='latin-1').write(txt)
