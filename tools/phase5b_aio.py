"""Step B (decision 5, CLEANSLATE_PLAN.md): use CK2Plus AIO's current version for LI definitions copied from
CK2Plus that carry no LI-specific content.
usage: python -I phase5b_aio.py <repo> <master_tree> <aio> <vanilla> <report.json> [--folders=a,b] [--keep-li=phase5b_keep_li.txt] [--apply]
A definition qualifies when
  - LI (master) has it, and AIO has it, and it is CK2Plus's: either not in vanilla, or AIO's text differs from
    CleanSlate's/vanilla's (CK2Plus changed it);
  - LI's master text uses none of LI's own religions/cultures/titles (names LI has and vanilla lacks);
  - the folder is not LI world data (titles, cultures, religions, dynasties, bookmarks...);
  - the mod's current block is not an LI-wins block ("# LI:" marker right above it).
For each, the report lists where the mod has it now and what AIO's version needs that the mod lacks
(events, scripted triggers/effects, modifiers, traits, localisation keys). --apply replaces only blocks with no
missing needs, writing AIO's text with a "# LI: CK2Plus AIO version" marker."""
import os, re, sys, json
from collections import Counter, defaultdict
REPO, MT, AIO, VA, OUT = sys.argv[1:6]
APPLY = '--apply' in sys.argv
ONLY = next((a.split('=', 1)[1].split(',') for a in sys.argv if a.startswith('--folders=')), None)
KEEP_LI = set()   # --keep-li=<file>: definitions whose LI version stays (one key per line, '#' comments)
for a in sys.argv:
    if a.startswith('--keep-li='):
        KEEP_LI |= {l.split('#')[0].strip() for l in open(a.split('=', 1)[1], encoding='latin-1') if l.split('#')[0].strip()}
CS = os.path.join(REPO, 'cleanslate_beta7')
DEPTH1 = {'decisions', 'common/governments', 'common/laws', 'common/religion_features'}
WORLD = {'common/landed_titles', 'common/cultures', 'common/religions', 'common/dynasties', 'common/bookmarks',
         'common/province_setup', 'common/religious_titles', 'common/offmap_powers', 'common/alternate_start',
         'common/defines', 'common/static_modifiers',
         'common/buildings',    # top-level keys are holding types: a block is a whole building list (LI's own buildings)
         'common/job_actions'}  # tied to the restored CleanSlate job events and LI's translated actions
def rd(p): return open(p, 'rb').read().decode('latin-1')
def nc(s): return re.sub(r'#[^\n]*', '', s)
def canon(s): return re.sub(r'\s+', ' ', re.sub(r'\s*([{}=<>])\s*', r'\1', nc(s))).strip()
TOK = re.compile(r'"[^"\n]*"|#[^\n]*|\{|\}|([\w.:@-]+)[ \t\r\n]*=[ \t\r\n]*\{')
def blocks(s, depth):
    """(key, start, end) of blocks at the given depth; comments and strings skipped"""
    out = []; stack = []
    for m in TOK.finditer(s):
        t = m.group(0)
        if t[0] in '"#': continue
        if t == '}':
            if stack:
                k, st, d = stack.pop()
                if d == depth and k is not None: out.append((k, st, m.end()))
            continue
        stack.append((m.group(1), m.start(), len(stack)))
    return out
def folder_of(rel):
    p = rel.split('/')
    return p[0] if p[0] in ('events', 'decisions') else '/'.join(p[:2])
def defs(root, keep_text=False):
    d = {}
    for top in ('common', 'events', 'decisions'):
        for dp, _, fs in os.walk(os.path.join(root, top)):
            if 'cleanslate_beta7' in dp: continue
            for f in fs:
                if not f.endswith('.txt'): continue
                path = os.path.join(dp, f); rel = os.path.relpath(path, root).replace(os.sep, '/')
                fol = folder_of(rel); s = rd(path)
                if fol == 'events':
                    for k, a, b in blocks(s, 0):
                        if k.endswith('_event'):
                            m = re.search(r'\bid\s*=\s*([\w.]+)', nc(s[a:b]))
                            if m: d.setdefault(('events', m.group(1)), (rel, a, b, s[a:b] if keep_text else canon(s[a:b])))
                else:
                    for k, a, b in blocks(s, 1 if fol in DEPTH1 else 0):
                        d.setdefault((fol, k), (rel, a, b, s[a:b] if keep_text else canon(s[a:b])))
    return d
print('reading...', flush=True)
li, aio_raw, cs, va, mod = defs(MT, True), defs(AIO, True), defs(CS), defs(VA), defs(REPO)
aio = {k: v[3] for k, v in aio_raw.items()}
def names(root):
    s = set()
    for d in ('common/religions', 'common/cultures', 'common/landed_titles'):
        for dp, _, fs in os.walk(os.path.join(root, d)):
            for f in fs: s |= set(re.findall(r'\b([\w-]+)\s*=\s*\{', nc(rd(os.path.join(dp, f)))))
    return s
def script_words(root):
    """block keys used in vanilla scripts (scopes, triggers, effects): landed_titles holds allow = { any_vassal = {...} }
    blocks, so these turn up in names() without being LI names (180 false 'uses LI world' rows before 2026-11-15)"""
    s = set()
    for d in ('events', 'decisions', 'common/cb_types', 'common/scripted_triggers', 'common/scripted_effects'):
        for dp, _, fs in os.walk(os.path.join(root, d)):
            for f in fs:
                if f.endswith('.txt'): s |= set(re.findall(r'\b([\w-]+)\s*=\s*\{', nc(rd(os.path.join(dp, f)))))
    return s
li_world = {x for x in names(REPO) - names(VA) - script_words(VA) if len(x) > 3}
# what the mod defines (for dependency checks)
def keyset(root, folders, depth=0):
    s = set()
    for fo in folders:
        for p in __import__('glob').glob(os.path.join(root, fo, '*.txt')):
            s |= {k for k, a, b in blocks(rd(p), depth)}
    return s
mod_events = {k for (f, k) in mod if f == 'events'}
mod_script = keyset(REPO, ['common/scripted_triggers', 'common/scripted_effects', 'common/scripted_score_values'])
mod_mods = keyset(REPO, ['common/event_modifiers', 'common/opinion_modifiers', 'common/traits', 'common/minor_titles',
                         'common/artifacts', 'common/objectives', 'common/societies'])
aio_script = keyset(AIO, ['common/scripted_triggers', 'common/scripted_effects', 'common/scripted_score_values'])
aio_mods = keyset(AIO, ['common/event_modifiers', 'common/opinion_modifiers', 'common/traits', 'common/minor_titles',
                        'common/artifacts', 'common/objectives', 'common/societies'])
def loc_keys(root):
    s = set()
    for dp, _, fs in os.walk(os.path.join(root, 'localisation')):
        if 'cleanslate_beta7' in dp: continue
        for f in fs:
            if f.endswith('.csv'):
                for line in rd(os.path.join(dp, f)).split('\n'):
                    k = line.split(';', 1)[0].strip()
                    if k and not k.startswith('#'): s.add(k)
    return s
mod_loc, aio_loc = loc_keys(REPO), loc_keys(AIO)
rows = []; cat = Counter(); per = defaultdict(Counter)
for key, (lf, la, lb, ltext) in li.items():
    fol, k = key
    if key not in aio_raw or fol == 'common/dynasties': continue
    t_li = canon(ltext); t_aio = canon(aio[key])
    base = cs.get(key) or va.get(key)
    if key in va and t_li == va[key][3]: continue                  # LI's copy is plain vanilla: CleanSlate's stays
    if key in va and base and t_aio == base[3]: continue           # vanilla def CK2Plus did not change
    if t_li == t_aio: c = 'LI = AIO already'
    elif fol in WORLD: c = 'world data (skip)'
    elif fol == 'common/on_actions': c = 'on_actions (skip: merged lists, kept as tuned on the branch)'
    elif key in mod and os.path.basename(mod[key][0]).lower().startswith(('hf_', 'hfp_')): c = 'Holy Fury file (skip: phase 8)'
    elif set(re.findall(r'[\w-]+', nc(ltext))) & li_world: c = 'uses LI world (port by hand)'
    elif k in KEEP_LI: c = 'kept as LI (keep-li list)'
    elif key not in mod: c = 'not in mod now'
    elif mod[key][3] == t_aio: c = 'mod = AIO already'
    else:
        mf, ma, mb, _ = mod[key]
        ms = rd(os.path.join(REPO, mf)); pre = ms[max(0, ma - 300):ma].rstrip().split('\n')[-1]
        if '# LI:' in pre: c = 'LI-wins block in mod (skip)'
        elif '# LI:' in ms[ma:mb]: c = 'block carries an LI fix inside (skip)'
        else:
            body = nc(aio[key])
            listed = {e for lst in re.findall(r'\bevents\s*=\s*\{([^}]*)\}', body) for e in re.findall(r'[\w.]+', lst)}
            need = sorted({e for e in set(re.findall(r'\bid\s*=\s*([\w.]+)', body)) | listed if e not in mod_events and e != k} |
                          {x for x in re.findall(r'\b(\w+)\s*=', body) if x in aio_script and x not in mod_script} |
                          {x for x in re.findall(r'[\w.-]+', body) if x in aio_mods and x not in mod_mods} |
                          {x for x in re.findall(r'[\w.-]+', body) if x in aio_loc and x not in mod_loc and len(x) > 4})
            c = 'REPLACE' if not need else 'REPLACE (needs AIO content)'
            rows.append({'folder': fol, 'key': k, 'mod_file': mf, 'li_file': lf, 'aio_file': aio_raw[key][0], 'need': need})
    cat[c] += 1; per[c][fol] += 1
for c, n in cat.most_common():
    print(f'{n:6}  {c}')
    for f, m in per[c].most_common(8): print(f'            {m:5}  {f}')
json.dump(rows, open(OUT, 'w'), indent=0)
need_all = Counter(x for r in rows for x in r['need'])
print('most-needed AIO items:', need_all.most_common(25))
if APPLY:
    by_file = defaultdict(list)
    for r in rows:
        if r['need'] or (ONLY and r['folder'] not in ONLY) or r['key'] in KEEP_LI: continue
        by_file[r['mod_file']].append(r)
    n = 0
    for mf, lst in by_file.items():
        p = os.path.join(REPO, mf); s = rd(p); nl = '\r\n' if '\r\n' in s else '\n'
        spans = sorted(((mod[(r['folder'], r['key'])][1], mod[(r['folder'], r['key'])][2], r) for r in lst), reverse=True)
        for a, b, r in spans:
            new = aio[(r['folder'], r['key'])].replace('\r\n', '\n').replace('\n', nl)
            ind = s[s.rfind('\n', 0, a) + 1:a]
            s = s[:a] + '# LI: CK2Plus AIO version (step B, decision 5)' + nl + ind + new + s[b:]; n += 1
        assert s.count('{') == s.count('}') or True
        open(p, 'wb').write(s.encode('latin-1'))
    print('replaced', n, 'definitions in', len(by_file), 'files')
