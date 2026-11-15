"""Step B (CLEANSLATE_PLAN.md): copy single CK2Plus AIO dependencies into the mod so blocked step B swaps become ready.
usage: python -I phase5b_deps.py <repo> <aio> <item> ... [--apply]
Each item is looked up in AIO as a top-level block in scripted_triggers / scripted_effects / event_modifiers /
opinion_modifiers / nicknames, or as a localisation key. Blocks go to li_CK2Plus_<kind>.txt in the same folder
(appended, with an "# LI RE: CK2Plus AIO version" header on a new file); localisation keys, plus each copied block's own
name/_desc keys, go to localisation/000_li_CK2Plus_stepb.csv. Prints what the copied text needs that neither the
mod nor this run provides (scripted items, modifiers, events, loc), so those can be added or the item dropped.
Dry run by default."""
import os, re, sys, glob
REPO, AIO = sys.argv[1:3]
ITEMS = [a for a in sys.argv[3:] if not a.startswith('--')]
APPLY = '--apply' in sys.argv
KINDS = [('common/scripted_triggers', 'li_CK2Plus_stepb_triggers.txt'), ('common/scripted_effects', 'li_CK2Plus_stepb_effects.txt'),
         ('common/event_modifiers', 'li_CK2Plus_timers.txt'), ('common/opinion_modifiers', 'li_CK2Plus_opinion_modifiers.txt'),
         ('common/nicknames', 'li_CK2Plus_nicknames.txt'), ('common/objectives', 'li_CK2Plus_plots.txt')]
LOC_OUT = 'localisation/000_li_CK2Plus_stepb.csv'
HEAD = '# LI RE: CK2Plus AIO version (step B, decision 5): dependencies of AIO definitions the mod uses (tools/phase5b_deps.py).'
def rd(p): return open(p, 'rb').read().decode('latin-1')
def nc(s): return re.sub(r'#[^\n]*', '', s)
def top_blocks(s):
    out = {}; d = 0; i = 0; st = None; key = None
    for m in re.finditer(r'(?m)#[^\n]*|"[^"\n]*"|\{|\}|^([\w.-]+)[ \t]*=[ \t]*(?=\{)', s):
        t = m.group(0)
        if t[0] in '#"': continue
        if m.group(1) is not None and d == 0: key, st = m.group(1), m.start(); continue
        if t == '{': d += 1
        elif t == '}':
            d -= 1
            if d == 0 and key: out.setdefault(key, s[st:m.end()]); key = None
    return out
def defs(root, folder):
    d = {}
    for p in sorted(glob.glob(os.path.join(root, folder, '*.txt'))):
        for k, v in top_blocks(rd(p)).items(): d.setdefault(k, v)
    return d
def loc(root):
    d = {}
    for p in sorted(glob.glob(os.path.join(root, 'localisation', '**', '*.csv'), recursive=True)):
        for line in rd(p).replace('\r\n', '\n').split('\n'):
            k = line.split(';', 1)[0].strip()
            if k and not k.startswith('#'): d.setdefault(k, line)
    return d
aio = {f: defs(AIO, f) for f, _ in KINDS}; mod = {f: defs(REPO, f) for f, _ in KINDS}
aio_loc, mod_loc = loc(AIO), loc(REPO)
mod_events = set()
for p in glob.glob(os.path.join(REPO, 'events', '*.txt')):
    mod_events |= set(re.findall(r'(?m)^\w+_event\s*=\s*\{[^\n]*\n?(?:\s*#[^\n]*\n)*\s*id\s*=\s*([\w.]+)', nc(rd(p))))
have = set().union(*[set(v) for v in mod.values()]) | set(mod_loc)
for f in ('common/traits', 'common/objectives', 'common/societies', 'common/minor_titles', 'common/laws', 'common/artifacts'):
    have |= set(defs(REPO, f))
add = {f: [] for f, _ in KINDS}; add_loc = []
for it in ITEMS:
    src = next((f for f, _ in KINDS if it in aio[f]), None)
    if src:
        if it in mod[src]: print(f'{it}: already in the mod'); continue
        add[src].append(it); have.add(it)
        for lk in (it, it + '_desc'):
            if lk in aio_loc and lk not in mod_loc: add_loc.append(lk); have.add(lk)
        print(f'{it}: {src}')
    elif it in aio_loc:
        if it in mod_loc: print(f'{it}: loc already in the mod'); continue
        add_loc.append(it); have.add(it); print(f'{it}: localisation')
    else: print(f'{it}: NOT FOUND in AIO')
# what the copied text needs
aio_all = set().union(*[set(v) for v in aio.values()]) | set(aio_loc)
for f, _ in KINDS:
    for it in add[f]:
        body = nc(aio[f][it])
        need = sorted({x for x in re.findall(r'[\w.-]+', body) if x in aio_all and x not in have and x != it} |
                      {e for e in re.findall(r'\bid\s*=\s*([\w.]+)', body) if e not in mod_events})
        if need: print(f'  needs ({it}):', need)
if APPLY:
    for f, fn in KINDS:
        if not add[f]: continue
        p = os.path.join(REPO, f, fn); old = rd(p).replace('\r\n', '\n') if os.path.exists(p) else HEAD + '\n'
        new = old.rstrip('\n') + '\n\n' + '\n\n'.join(aio[f][k].replace('\r\n', '\n') for k in add[f]) + '\n'
        open(p, 'wb').write(new.replace('\n', '\r\n').encode('latin-1'))
    if add_loc:
        p = os.path.join(REPO, LOC_OUT)
        old = rd(p).replace('\r\n', '\n') if os.path.exists(p) else '#CODE;ENGLISH;FRENCH;GERMAN;;SPANISH;;;;;;;;;x\n# LI RE: CK2Plus AIO text for step B dependencies (tools/phase5b_deps.py).\n'
        new = old.rstrip('\n') + '\n' + '\n'.join(aio_loc[k] for k in add_loc) + '\n'
        open(p, 'wb').write(new.replace('\n', '\r\n').encode('latin-1'))
    print('written:', {f: len(v) for f, v in add.items() if v}, 'loc', len(add_loc))
