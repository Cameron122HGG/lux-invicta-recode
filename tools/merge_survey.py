"""File-level 3-way merge survey (base = vanilla, ours = LI, theirs = CleanSlate) using git merge-file.
usage: python -I merge_survey.py <mod_dir> <cleanslate_dir> <vanilla_dir> <out.json>"""
import os, sys, subprocess, tempfile, hashlib, json
from collections import Counter, defaultdict
LI, CS, VA, OUT = sys.argv[1:5]
DIRS = ['common', 'events', 'decisions', 'localisation', 'interface', 'history', 'map', 'gfx', 'dlc_metadata', 'music', 'sound']
def files(root):
    out = {}
    for d in DIRS:
        for dp, _, fs in os.walk(os.path.join(root, d)):
            if '.transfer' in dp: continue
            for f in fs:
                p = os.path.join(dp, f); out[os.path.relpath(p, root).replace(chr(92), '/').lower()] = p
    return out
li, cs, va = files(LI), files(CS), files(VA)
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()
cat = Counter(); per = defaultdict(Counter); conflicts = []; rows = []
tmp = tempfile.mkdtemp()
for k, p in sorted(li.items()):
    top = k.split('/')[0]; sub = '/'.join(k.split('/')[:2])
    if k in va and md5(p) == md5(va[k]): c = 'LI copy identical to vanilla (drop: use CleanSlate/vanilla)'
    elif k not in va: c = 'LI-only file (keep as is)'
    elif top in ('history', 'map', 'gfx', 'music', 'sound'): c = 'LI replaces vanilla data (keep LI)'
    elif k not in cs: c = 'LI edit of vanilla file that CleanSlate renamed/split (manual: merge by definitions)'
    else:
        # 3-way merge
        a, b, o = [os.path.join(tmp, x) for x in ('ours', 'base', 'theirs')]
        for src, dst in ((p, a), (va[k], b), (cs[k], o)):
            open(dst, 'wb').write(open(src, 'rb').read().replace(b'\r\n', b'\n'))
        r = subprocess.run(['git', 'merge-file', '-q', a, b, o], capture_output=True)
        n = r.returncode
        if n == 0: c = 'LI edit + CleanSlate edit merge cleanly (3-way)'
        elif n > 0: c = 'LI edit + CleanSlate edit: 3-way merge has conflicts'; conflicts.append((k, n))
        else: c = 'merge error'
    cat[c] += 1; per[c][sub] += 1; rows.append((k, c))
print(f'LI files surveyed: {len(li)}')
for c, n in cat.most_common():
    print(f'\n{n:6}  {c}')
    for s, m in per[c].most_common(8): print(f'          {m:5}  {s}')
conflicts.sort(key=lambda x: -x[1])
print('\nfiles with most conflict hunks:', conflicts[:15], '| total conflict hunks', sum(n for _, n in conflicts))
cs_only = [k for k in cs if k not in li and k.split('/')[0] in ('common', 'events', 'decisions', 'localisation')]
print('CleanSlate script/loc files LI has no counterpart for:', len(cs_only))
json.dump({'rows': rows, 'conflicts': conflicts}, open(OUT, 'w'))
