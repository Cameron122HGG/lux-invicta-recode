"""Apply CleanSlate's renamed IDs (from its master_changelog.txt) to LI's own files.
usage: python -I cs_renames.py <repo_dir> [--apply]
Renamed: traits, event/opinion modifiers, scripted triggers/effects, decisions, combat tactics.
NOT renamed (LI's own world, which LI defines itself): cultures/religions, landed titles, governments.
Files touched: li_* script files, history/, interface/ (sprite names such as GFX_trait_<trait>),
and the keys (never the text) of LI's localisation CSVs (not the zz_cs_ ones).
Code only: comments and quoted strings are left alone."""
import os, re, sys
from collections import Counter, defaultdict
REPO = sys.argv[1]; APPLY = '--apply' in sys.argv
WANT = {'= Traits =', '= Event/opinion modifiers =', '= Scripted triggers/effects =', '= Decisions =', '= Combat tactics'}
log = open(os.path.join(REPO, 'cleanslate_beta7', 'master_changelog.txt'), 'rb').read().decode('latin-1').replace('\r', '')
REN = {}
for m in re.finditer(r'(?m)^(Renamed[^\n]*)\n((?:[ \t]*-[^\n]*->[^\n]*\n)+)', log):
    s = log.rfind('\n= ', 0, m.start()); sec = log[s:log.find('\n', s + 1)].strip()
    if not any(sec.startswith(w) for w in WANT): continue
    for a, b in re.findall(r'-\s*([\w.]+)\s*->\s*([\w.]+)', m.group(2)): REN[a] = b
assert 'fair' in REN and REN['fair'] == 'attractive'
FIXES = {'has_typhoid_fever': 'slow_fever'}   # the changelog says "slow_ever"; CleanSlate defines slow_fever
REN.update({k: v for k, v in FIXES.items() if k in REN})
# sanity: the "new" name must be defined in CleanSlate (catches typos in the changelog)
cs_text = []
for top in ('common', 'decisions'):
    for dp, _, fs in os.walk(os.path.join(REPO, 'cleanslate_beta7', top)):
        for f in fs:
            if f.endswith('.txt'): cs_text.append(open(os.path.join(dp, f), 'rb').read().decode('latin-1'))
cs_all = '\n'.join(cs_text)
for a, b in list(REN.items()):
    if not re.search(r'(?m)^\s*' + re.escape(b) + r'\s*=\s*\{', cs_all):
        print(f'WARNING: {a} -> {b}: "{b}" is not defined in CleanSlate common/ - skipped'); del REN[a]
pat = re.compile(r'(?<![\w.:@])(' + '|'.join(sorted(map(re.escape, REN), key=len, reverse=True)) + r')(?![\w.:@])')
GFX = re.compile(r'(GFX_trait_)(' + '|'.join(sorted(map(re.escape, REN), key=len, reverse=True)) + r')\b')

def li_files():
    for top in ('common', 'events', 'decisions'):
        for dp, _, fs in os.walk(os.path.join(REPO, top)):
            for f in fs:
                if f.lower().startswith('li_') or any(w in dp.replace(os.sep, '/') for w in
                        ('common/landed_titles', 'common/cultures', 'common/religions', 'common/dynasties', 'common/bookmarks')):
                    yield os.path.join(dp, f), 'script'
    for top in ('history', 'interface'):
        for dp, _, fs in os.walk(os.path.join(REPO, top)):
            for f in fs: yield os.path.join(dp, f), ('gfx' if top == 'interface' else 'script')
    for f in os.listdir(os.path.join(REPO, 'localisation')):
        if f.endswith('.csv') and not f.startswith('zz_cs_'): yield os.path.join(REPO, 'localisation', f), 'loc'

def sub_code(text, rx, repl, hits):
    # replace only outside comments and quoted strings
    out = []; pos = 0
    for m in re.finditer(r'#[^\n]*|"[^"\n]*"', text):
        seg = text[pos:m.start()]
        out.append(rx.sub(lambda x: (hits.update([x.group(0)]), repl(x))[1], seg)); out.append(m.group(0)); pos = m.end()
    out.append(rx.sub(lambda x: (hits.update([x.group(0)]), repl(x))[1], text[pos:]))
    return ''.join(out)

per = defaultdict(Counter); files_changed = 0
for p, kind in li_files():
    if not os.path.isfile(p): continue
    raw = open(p, 'rb').read(); t = raw.decode('latin-1'); hits = Counter()
    if kind == 'loc':
        lines = t.split('\n')
        for i, l in enumerate(lines):
            key, sep, rest = l.partition(';')
            k2 = key.strip(); base = re.match(r'([\w.]+?)(_desc|_male|_female|_child)?$', k2)
            if base and base.group(1) in REN:
                lines[i] = key.replace(base.group(1), REN[base.group(1)], 1) + sep + rest; hits[base.group(1)] += 1
        nt = '\n'.join(lines)
    elif kind == 'gfx':
        nt = GFX.sub(lambda x: (hits.update([x.group(2)]), x.group(1) + REN[x.group(2)])[1], t)
    else:
        nt = sub_code(t, pat, lambda x: REN[x.group(1)], hits)
    if hits:
        area = os.path.relpath(p, REPO).replace(os.sep, '/').split('/')[0]
        for k, n in hits.items(): per[area][k] += n
        files_changed += 1
        if APPLY: open(p, 'wb').write(nt.encode('latin-1'))
print(len(REN), 'renames in use |', files_changed, 'files', '(applied)' if APPLY else '(dry run)')
for area, c in per.items():
    print(f'\n{area}: {sum(c.values())} replacements'); [print(f'   {n:5}  {k} -> {REN[k]}') for k, n in c.most_common(12)]
