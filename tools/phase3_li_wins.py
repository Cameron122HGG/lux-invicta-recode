"""Phase 3, "LI's version wins": definitions LI changed that use LI's own content get LI's master
version in place of CleanSlate's, marked # LI:. Also adds LI's own on_action entries.
usage: python -I phase3_li_wins.py <repo_dir> <master_tree> <vanilla_dir> [--apply]
- Only definitions that exist in vanilla, differ in LI, and use LI-only names (religions, cultures,
  titles, traits, modifiers, scripted triggers/effects, events) are replaced.
- CleanSlate's renamed IDs (fair -> attractive...) are applied to the inserted text.
- on_actions: event IDs in LI's master lists that CleanSlate's lists lack go into
  common/on_actions/li_on_actions.txt (CK2 merges on_action lists across files); weights kept."""
import os, re, sys
from collections import Counter, defaultdict
REPO, MT, VA = sys.argv[1:4]; APPLY = '--apply' in sys.argv
SKIP = ('common/dynasties', 'common/landed_titles', 'common/cultures', 'common/religions', 'common/bookmarks',
        'common/on_actions', 'common/defines', 'common/buildings', 'common/trade_routes', 'common/societies',
        'common/artifacts', 'common/artifact_spawns', 'common/offmap_powers')
DEPTH1 = {'decisions', 'common/governments', 'common/laws', 'common/religion_features'}
def rd(p): return open(p, 'rb').read()
def nc(b): return re.sub(rb'#[^\n]*', b'', b)
def canon(b): return re.sub(rb'\s+', b' ', re.sub(rb'\s*([{}=<>])\s*', rb'\1', nc(b))).strip()
def blocks(b, depth):
    out = []; stack = []
    for m in re.finditer(rb'#[^\n]*|"[^"\n]*"|\{|\}|([\w.:@-]+)[ \t\r\n]*=[ \t\r\n]*\{', b):
        s = m.group(0)
        if s.startswith((b'#', b'"')): continue
        if s == b'}':
            if stack:
                k, st, d = stack.pop()
                if d == depth and k is not None: out.append((k, st, m.end()))
            continue
        stack.append((m.group(1), m.start(), len(stack)))
    return out
def folder(rel):
    p = rel.split('/'); return p[0] if p[0] in ('events', 'decisions') else '/'.join(p[:2])
def defs(root, li_only_files=False):
    """(folder, key) -> (file, start, end) ; text read lazily"""
    d = {}
    for top in ('common', 'events', 'decisions'):
        for dp, _, fs in os.walk(os.path.join(root, top)):
            for f in fs:
                if not f.endswith('.txt'): continue
                rel = os.path.relpath(os.path.join(dp, f), root).replace(os.sep, '/')
                fol = folder(rel)
                if fol.startswith(SKIP) or rel.startswith('cleanslate_beta7'): continue
                if li_only_files is False and f.lower().startswith('li_'): continue
                b = rd(os.path.join(dp, f))
                for k, st, en in blocks(b, 1 if fol in DEPTH1 else 0):
                    if top == 'events':
                        if not k.endswith(b'_event'): continue
                        m = re.search(rb'\bid\s*=\s*([\w.]+)', nc(b[st:en]))
                        if not m: continue
                        key = m.group(1).decode()
                    else: key = k.decode()
                    d.setdefault((fol, key), (rel, st, en))
    return d
ma, va, br = defs(MT, None), defs(VA), defs(REPO)
text = {}
def body(root, rel, st, en):
    k = (root, rel)
    if k not in text: text[k] = rd(os.path.join(root, rel))
    return text[k][st:en]
# LI-only names
def names(root):
    s = set()
    for d in ('common/religions', 'common/cultures', 'common/landed_titles', 'common/traits', 'common/event_modifiers',
              'common/scripted_effects', 'common/scripted_triggers', 'common/opinion_modifiers', 'common/minor_titles'):
        for dp, _, fs in os.walk(os.path.join(root, d)):
            for f in fs: s |= set(re.findall(rb'\b([\w-]+)\s*=\s*\{', nc(rd(os.path.join(dp, f)))))
    return s
li_names = {x for x in names(MT) - names(VA) if len(x) > 3}
li_names |= {k.encode() for (fol, k) in ma if fol == 'events' and (fol, k) not in va}
# CleanSlate renames (same sections as cs_renames.py)
log = rd(os.path.join(REPO, 'cleanslate_beta7', 'master_changelog.txt')).decode('latin-1').replace('\r', '')
REN = {}
for m in re.finditer(r'(?m)^(Renamed[^\n]*)\n((?:[ \t]*-[^\n]*->[^\n]*\n)+)', log):
    s = log.rfind('\n= ', 0, m.start()); sec = log[s:log.find('\n', s + 1)]
    if any(w in sec for w in ('Traits', 'modifiers', 'Scripted', 'Decisions', 'Combat')):
        REN.update({a: b for a, b in re.findall(r'-\s*([\w.]+)\s*->\s*([\w.]+)', m.group(2))})
REN['has_typhoid_fever'] = 'slow_fever'
renpat = re.compile(rb'(?<![\w.:@"])(' + b'|'.join(re.escape(k.encode()) for k in sorted(REN, key=len, reverse=True)) + rb')(?![\w.:@"])')
def rename(b):
    out = []; pos = 0
    for m in re.finditer(rb'#[^\n]*|"[^"\n]*"', b):
        out.append(renpat.sub(lambda x: REN[x.group(1).decode()].encode(), b[pos:m.start()]))
        q = m.group(0)
        if q.startswith(b'"') and q[1:-1].decode('latin-1') in REN: q = b'"' + REN[q[1:-1].decode('latin-1')].encode() + b'"'
        out.append(q); pos = m.end()
    out.append(renpat.sub(lambda x: REN[x.group(1).decode()].encode(), b[pos:])); return b''.join(out)

plan = defaultdict(list); stats = Counter(); missing = Counter()
for key, (rel, st, en) in ma.items():
    if key not in va: continue
    lb = body(MT, rel, st, en); vb = body(VA, *va[key])
    if canon(lb) == canon(vb): continue
    if not (set(re.findall(rb'[\w.-]+', nc(lb))) & li_names): continue
    if key not in br: missing[key[0]] += 1; continue
    brel, bst, ben = br[key]
    if canon(body(REPO, brel, bst, ben)) == canon(lb): continue
    plan[brel].append((bst, ben, lb, key)); stats[key[0]] += 1
print('definitions to replace with LI\'s version:', sum(stats.values()), 'in', len(plan), 'files')
for k, n in stats.most_common(12): print(f'   {n:5}  {k}')
print('LI-changed definitions CleanSlate no longer has (skipped):', sum(missing.values()), dict(missing.most_common(6)))

# on_actions: LI's own entries
def onact(root, only_li=None):
    d = defaultdict(lambda: {'events': [], 'random_events': []})
    base = os.path.join(root, 'common', 'on_actions')
    for f in os.listdir(base):
        if not f.endswith('.txt'): continue
        b = rd(os.path.join(base, f))
        for k, st, en in blocks(b, 0):
            blk = b[st:en]
            for lm in re.finditer(rb'(events|random_events)\s*=\s*\{', blk):
                i = lm.end(); depth = 1; j = i
                while depth:
                    c = blk[j:j + 1]
                    if c == b'#': j = blk.find(b'\n', j); continue
                    if c == b'{': depth += 1
                    elif c == b'}': depth -= 1
                    j += 1
                inner = nc(blk[i:j - 1])
                if lm.group(1) == b'random_events':
                    d[k.decode()]['random_events'] += [(w.decode(), e.decode()) for w, e in re.findall(rb'(\d+)\s*=\s*((?:[A-Za-z_]+\.)?\d+)', inner)]
                else:
                    d[k.decode()]['events'] += [e.decode() for e in re.findall(rb'(?<![\w.=])((?:[A-Za-z_]+\.)?\d+)(?![\w.]|\s*=)', inner)]
    return d
mo, bo = onact(MT), onact(REPO)
br_ev = {k for (fol, k) in br if fol == 'events'} | {k for (fol, k) in defs(REPO, True) if fol == 'events'}
add = {}; addn = 0; dead = 0
for act, lists in mo.items():
    have_e = set(bo[act]['events']); have_r = {e for w, e in bo[act]['random_events']}
    ne = [e for e in lists['events'] if e not in have_e and e != '0']
    nr = [(w, e) for w, e in lists['random_events'] if e not in have_r and e != '0']
    dead += sum(1 for e in ne if e not in br_ev) + sum(1 for w, e in nr if e not in br_ev)
    ne = [e for e in ne if e in br_ev]; nr = [(w, e) for w, e in nr if e in br_ev]
    if ne or nr: add[act] = (ne, nr); addn += len(ne) + len(nr)
print(f'on_actions: {addn} LI entries to add in {len(add)} on_actions ({dead} LI entries skipped: event not defined on the branch)')

if APPLY:
    for rel, items in plan.items():
        p = os.path.join(REPO, rel); b = rd(p); nl = b'\r\n' if b'\r\n' in b else b'\n'
        for st, en, lb, key in sorted(items, reverse=True):
            ins = b'# LI: Lux Invicta\'s version (from master), not CleanSlate\'s - it uses LI\'s own world.' + nl + rename(lb).replace(b'\r\n', b'\n').replace(b'\n', nl)
            b = b[:st] + ins + b[en:]
        t = nc(b); assert t.count(b'{') == t.count(b'}'), rel
        open(p, 'wb').write(b)
    if add:
        nl = b'\r\n'
        out = [b'# Lux Invicta\'s own on_action entries (from master) that CleanSlate\'s on_actions lack.',
               b'# CK2 merges on_action lists across files. Phase 3 of CLEANSLATE_PLAN.md.', b'']
        for act, (ne, nr) in sorted(add.items()):
            out.append(act.encode() + b' = {')
            if ne: out += [b'\tevents = {'] + [b'\t\t' + e.encode() for e in ne] + [b'\t}']
            if nr: out += [b'\trandom_events = {'] + [b'\t\t' + w.encode() + b' = ' + e.encode() for w, e in nr] + [b'\t}']
            out += [b'}', b'']
        p = os.path.join(REPO, 'common', 'on_actions', 'li_on_actions.txt'); assert not os.path.exists(p)
        open(p, 'wb').write(nl.join(out))
    print('applied')
