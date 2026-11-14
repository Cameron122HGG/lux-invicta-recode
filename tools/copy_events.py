"""Copy vanilla event definitions into an LI event file, after checking dependencies.
usage: python -I copy_events.py <mod_dir> <vanilla_dir> <vanilla events file> <LI events file> <comment> ID [ID ...] [--apply]"""
import os, re, sys
args = [a for a in sys.argv[1:] if a != '--apply']; APPLY = '--apply' in sys.argv
R, V, VF, LF, NOTE = args[:5]; IDS = args[5:]
DEF = re.compile(r'(?m)^\w+_event\s*=\s*\{\s*id\s*=\s*([\w.]+)')
def rd(p): return open(p, 'rb').read().decode('latin-1')   # lossless: every byte round-trips
def nc(t): return re.sub(r'#[^\n]*', '', t)
def block(t, i):
    # allow comments between the opening brace and the id ("character_event = { #feast_drunkard")
    m = re.search(r'(?m)^\w+_event[ \t]*=[ \t]*\{[ \t]*(?:#[^\n]*)?\s*(?:#[^\n]*\n\s*)*id\s*=\s*' + re.escape(i) + r'\b', t)
    assert m, 'event not found: ' + i
    s = m.start(); k = t.find('{', s); d = 0; e = k
    while True:
        c = t[e]
        if c == '#': e = t.find('\n', e); continue
        if c == '{': d += 1
        elif c == '}':
            d -= 1
            if d == 0: return t[s:e + 1]
        e += 1
def keys(d, root):
    s = set(); p = os.path.join(root, d)
    for f in (os.listdir(p) if os.path.isdir(p) else []):
        t = nc(rd(os.path.join(p, f))); dep = 0
        for m in re.finditer(r'([\w-]+)\s*=\s*\{|\{|\}', t):
            x = m.group(0)
            if x == '{': dep += 1
            elif x == '}': dep -= 1
            else:
                if dep == 0: s.add(m.group(1))
                dep += 1
    return s
lidef = set()
for f in os.listdir(R + '/events'):
    if f.endswith('.txt'): lidef |= set(DEF.findall(nc(rd(R + '/events/' + f))))
vt = rd(os.path.join(V, 'events', VF))
blocks = [block(vt, i) for i in IDS]
allb = '\n\n'.join(blocks).replace('\r\n', '\n')
code = nc(allb)
called = set(re.findall(r'\bid\s*=\s*([\w.]+)', code)) - set(IDS)
print('already defined in LI:', [i for i in IDS if i in lidef])
print('other events called:', sorted(called), '| missing in LI:', sorted(c for c in called if c not in lidef))
se, st = keys('common/scripted_effects', R), keys('common/scripted_triggers', R)
used = set(re.findall(r'\b(\w+_(?:effect|trigger))\s*=\s*yes', code))
print('scripted effects/triggers missing in LI:', sorted(u for u in used if u not in se and u not in st))
mods = set(re.findall(r'(?:add_character_modifier|has_character_modifier)\s*=\s*(?:\{\s*(?:name|modifier)\s*=\s*)?(\w+)', code))
em = keys('common/event_modifiers', R); print('event modifiers missing in LI:', sorted(m for m in mods if m not in em))
for k, v in (('religion', r'\breligion\s*=\s*(\w+)'), ('culture', r'\bculture\s*=\s*(\w+)'), ('title', r'\b([ekdcb]_\w+)\b')):
    print(f'{k} references:', sorted(set(re.findall(v, code)))[:15])
locs = set(re.findall(r'(?:desc|name|text|tooltip)\s*=\s*"?([A-Z][A-Za-z0-9_]+)"?', code))
print('loc keys used:', sorted(locs)[:20])
print('lines to copy:', allb.count('\n') + 1)
if APPLY:
    p = os.path.join(R, 'events', LF); b = open(p, 'rb').read().rstrip(b'\r\n')
    nl = b'\r\n' if b'\r\n' in b else b'\n'
    add = (nl * 2 + b'# ' + NOTE.encode('latin-1') + nl + allb.encode('latin-1').replace(b'\n', nl) + nl)
    open(p, 'wb').write(b + add); print('appended to', LF)
