"""Phase 8 (Holy Fury integration), one part at a time: bring in CK2Plus AIO's version of whole Holy Fury event
files. usage: python -I phase8_hf.py <repo> <aio> <ids_out.txt> <file.txt> [<file.txt> ...] [--apply]
1. each listed events/ file becomes AIO's version (with an LI header); refuses files carrying "# LI:" changes
2. step A's switched-off call sites / on_action entries for the restored events get AIO's line back
   (CleanSlate's if AIO lacks the file or line)
3. writes <ids_out.txt>: events the new files call that the mod still lacks (switch them off with
   hf_off.py --ids-file=... --note=...), numeric ones listed separately for ids_off.py
4. reports what AIO's events need that the mod lacks: scripted triggers/effects/score values, event and
   opinion modifiers, traits, artifacts, localisation keys"""
import os, re, sys, glob, collections
REPO, AIO, OUT = sys.argv[1:4]; FILES = [a for a in sys.argv[4:] if not a.startswith('--')]; APPLY = '--apply' in sys.argv
NOTE = 'event left out of the CleanSlate build: LI never had it (decision 6, CLEANSLATE_PLAN.md)'
def rd(p): return open(p, 'rb').read().decode('latin-1')
def nc(s): return re.sub(r'#[^\n]*', '', s)
DEF = re.compile(r'(?m)^\w+_event[ \t]*=[ \t]*\{[^\n]*\n?(?:\s*#[^\n]*\n)*\s*id\s*=\s*([\w.]+)')
def ids_in(s): return set(DEF.findall(nc(s)))
def calls_in(s):
    s = nc(s); out = set()
    for m in re.finditer(r'\bid\s*=\s*([\w.]+)', s):
        line = s[s.rfind('\n', 0, m.start()) + 1:s.find('\n', m.end())]
        pre = s[max(0, m.start() - 200):m.start()]
        if re.match(r'\s*id\s*=', line) and re.search(r'(?m)^\w+_event\s*=\s*\{[^{}]*$', pre): continue   # a definition
        out.add(m.group(1))
    for lst in re.findall(r'\bevents\s*=\s*\{([^}]*)\}', s): out |= set(re.findall(r'[\w.]+', lst))
    return out
# --- 1. new file texts
new = {}; restored = set()
for f in FILES:
    a = os.path.join(AIO, 'events', f); m = os.path.join(REPO, 'events', f)
    assert os.path.exists(a), 'AIO lacks ' + f
    if os.path.exists(m) and '# LI:' in rd(m): sys.exit('refusing: ' + f + ' carries LI changes')
    t = rd(a).replace('\r\n', '\n')
    hdr = '# LI: CK2Plus AIO version of this Holy Fury file (phase 8, CLEANSLATE_PLAN.md).\n'
    new[f] = hdr + t; restored |= ids_in(t)
mod_ids = set()
for p in glob.glob(os.path.join(REPO, 'events', '*.txt')):
    if os.path.basename(p) not in new: mod_ids |= ids_in(rd(p))
all_ids = mod_ids | restored
print('events restored from AIO:', len(restored), '| of which already in the mod elsewhere:', len(restored & mod_ids))
# --- 3. calls the new files make to events the mod still lacks
missing = collections.Counter()
for f, t in new.items():
    for c in calls_in(t):
        if c not in all_ids and not c.isdigit() or (c.isdigit() and c not in all_ids and len(c) > 1): missing[c] += 1
named = sorted(c for c in missing if not c.isdigit()); numeric = sorted(c for c in missing if c.isdigit())
open(OUT, 'w').write('\n'.join(named) + '\n')
open(OUT.replace('.txt', '_numeric.txt'), 'w').write(' '.join(numeric) + '\n')
print('calls to events still missing:', len(named), 'named,', len(numeric), 'numeric ->', OUT)
by_ns = collections.Counter(c.split('.')[0] for c in named); print('   by namespace:', by_ns.most_common(10))
# --- 4. dependencies
def keyset(root, dirs, depth0=True):
    s = set()
    for d in dirs:
        for p in glob.glob(os.path.join(root, d, '*.txt')): s |= set(re.findall(r'(?m)^\s*(\w+)\s*=\s*\{' if not depth0 else r'(?m)^(\w+)\s*=\s*\{', nc(rd(p))))
    return s
SCR = ['common/scripted_triggers', 'common/scripted_effects', 'common/scripted_score_values']
MODS = ['common/event_modifiers', 'common/opinion_modifiers']
def loc(root):
    s = set()
    for dp, _, fs in os.walk(os.path.join(root, 'localisation')):
        if 'cleanslate_beta7' in dp: continue
        for fn in fs:
            if fn.endswith('.csv'):
                for line in rd(os.path.join(dp, fn)).split('\n'):
                    k = line.split(';', 1)[0].strip()
                    if k: s.add(k)
    return s
mod_scr, aio_scr = keyset(REPO, SCR), keyset(AIO, SCR)
mod_mod, aio_mod = keyset(REPO, MODS, False), keyset(AIO, MODS, False)
mod_tr, aio_tr = keyset(REPO, ['common/traits']), keyset(AIO, ['common/traits'])
mod_art, aio_art = keyset(REPO, ['common/artifacts']), keyset(AIO, ['common/artifacts'])
mod_loc, aio_loc = loc(REPO), loc(AIO)
need = collections.defaultdict(set)
for f, t in new.items():
    body = nc(t); toks = set(re.findall(r'[\w.-]+', body))
    for x in toks:
        if x in aio_scr and x not in mod_scr: need['scripted'].add(x)
        if x in aio_mod and x not in mod_mod: need['modifiers'].add(x)
        if x in aio_tr and x not in mod_tr: need['traits'].add(x)
        if x in aio_art and x not in mod_art: need['artifacts'].add(x)
        if x in aio_loc and x not in mod_loc and len(x) > 4: need['localisation'].add(x)
for k, v in need.items(): print(f'needs {k}: {len(v)}', sorted(v)[:12])
# --- 2. step A switch-offs for restored events
fixed = 0; unfixed = []
src = {}
for top in ('common/on_actions', 'events', 'decisions', 'common/scripted_effects', 'common/cb_types', 'common/job_titles'):
    for p in glob.glob(os.path.join(REPO, top, '*.txt')):
        rel = os.path.relpath(p, REPO).replace(os.sep, '/')
        if os.path.basename(p) in new and top == 'events': continue
        s = rd(p)
        if NOTE not in s: continue
        nl = '\r\n' if '\r\n' in s else '\n'; lines = s.replace('\r\n', '\n').split('\n')
        refs = [x for x in (os.path.join(AIO, rel), os.path.join(REPO, 'cleanslate_beta7', rel)) if os.path.exists(x)]
        ref = [rd(x).replace('\r\n', '\n').split('\n') for x in refs]
        ch = False
        for n, l in enumerate(lines):
            if NOTE not in l: continue
            hit = [r for r in restored if re.search(r'(?<![\w.])' + re.escape(r) + r'(?![\w.])', l)]
            if not hit: continue
            r = hit[0]; cand = None
            for lines_ref in ref:
                c = [x for x in lines_ref if re.search(r'(?<![\w.])' + re.escape(r) + r'(?![\w.])', x) and not x.lstrip().startswith('#')
                     and not re.match(r'\s*id\s*=\s*' + re.escape(r) + r'\s*$', x)]
                if c and all(x == c[0] for x in c): cand = c[0]; break
            if cand is None:
                # step A wrote "<indent>#<original line> # <NOTE>": put the original back
                m = re.match(r'^(\s*)#(.*?)\s*#?\s*\(?' + re.escape(NOTE) + r'\)?\s*$', l)
                if m and re.search(r'(?<![\w.])' + re.escape(r) + r'(?![\w.])', m.group(2)): cand = m.group(1) + m.group(2).rstrip()
            if cand is not None: lines[n] = cand; ch = True; fixed += 1
            else: unfixed.append((rel, n + 1, l.strip()[:110]))
        if ch and APPLY: open(p, 'wb').write('\n'.join(lines).replace('\n', nl).encode('latin-1'))
print('step A switch-offs restored:', fixed, '| need a manual look:', len(unfixed))
for u in unfixed[:25]: print('   ', u)
if APPLY:
    for f, t in new.items(): open(os.path.join(REPO, 'events', f), 'wb').write(t.replace('\n', '\r\n').encode('latin-1'))
    print('wrote', len(new), 'files')
