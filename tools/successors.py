"""Classify 'Missing scripted successor' warnings.
usage: python -I successors.py <mod_dir> <historical_setup_errors.log> [out.tsv]"""
import os, re, sys
from collections import Counter, defaultdict
R, LOG = sys.argv[1:3]
OUT = sys.argv[3] if len(sys.argv) > 3 else None

def rd(p): return re.sub(r'#[^\n]*', '', open(p, 'rb').read().decode('cp1252', 'replace'))
def dkey(s):
    y, m, d = (int(x) for x in s.split('.')); return (y, m, d)

# character death dates
death = {}
for f in os.listdir(os.path.join(R, 'history/characters')):
    t = rd(os.path.join(R, 'history/characters', f))
    for m in re.finditer(r'^(\d+)\s*=\s*\{(.*?)^\}', t, re.M | re.S):
        dm = re.search(r'(\d+\.\d+\.\d+)\s*=\s*\{[^{}]*?\bdeath\s*=', m.group(2))
        if dm: death[m.group(1)] = dm.group(1)

# title holder timelines
hist = {}
for f in os.listdir(os.path.join(R, 'history/titles')):
    t = rd(os.path.join(R, 'history/titles', f)); tl = []
    for m in re.finditer(r'(\d+\.\d+\.\d+)\s*=\s*\{([^{}]*)\}', t):
        h = re.search(r'\bholder\s*=\s*"?(\d+)', m.group(2))
        if h: tl.append((dkey(m.group(1)), h.group(1)))
    hist[f[:-4]] = sorted(tl)

log = open(LOG, encoding='cp1252', errors='replace').read()
rows = []; cat = Counter(); per_title = Counter()
for m in re.finditer(r'Missing scripted successor\. Character (.*?) \((\d+)\) dies while holding titles: (.*)', log):
    name, cid, titles = m.group(1), m.group(2), m.group(3).split()
    dd = death.get(cid)
    for t in titles:
        tl = hist.get(t, [])
        if not dd: c = 'no death date found'; nxt = None
        else:
            d = dkey(dd)
            later = [x for x in tl if x[0] > d]
            same = [x for x in tl if x[0] == d and x[1] != cid]
            nxt = later[0] if later else None
            if same: c = 'successor set same day (order issue)'
            elif not tl: c = 'title has no history file/holders (held via another title?)'
            elif nxt and nxt[1] == '0': c = 'next entry ends title (holder = 0)'
            elif nxt: c = 'gap before next holder'
            else: c = 'nothing after: title left to succession'
        cat[c] += 1; per_title[t] += 1
        rows.append((t, name, cid, dd, c, nxt))

print('warnings x titles:', len(rows))
for c, n in cat.most_common(): print(f'{n:5}  {c}')
gaps = [r for r in rows if r[4] == 'gap before next holder']
if gaps:
    import statistics
    ds = [(r[5][0][0] - dkey(r[3])[0]) * 365 + (r[5][0][1] - dkey(r[3])[1]) * 30 + (r[5][0][2] - dkey(r[3])[2]) for r in gaps]
    print('gap length days: min', min(ds), 'median', statistics.median(ds), 'max', max(ds))
    print('gaps of 1 day:', sum(1 for x in ds if x <= 1), '| <= 1 year:', sum(1 for x in ds if x <= 365))
after1066 = [r for r in rows if r[3] and dkey(r[3]) >= (1066, 1, 1)]
print('deaths on/after 1066.1.1:', len(after1066))
print('top titles:', per_title.most_common(12))
end_pre1066 = [r for r in rows if r[4] == 'nothing after: title left to succession']
print('titles left to succession (sample):', [(r[0], r[3]) for r in end_pre1066[:15]])
if OUT:
    with open(OUT, 'w', encoding='utf-8') as o:
        for r in rows: o.write('\t'.join(map(str, r)) + '\n')
