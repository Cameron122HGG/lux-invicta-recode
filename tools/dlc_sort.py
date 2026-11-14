"""Sort an error.log by DLC / source file.
usage: python -I dlc_sort.py <error.log> <mod_dir> <vanilla_dir>"""
import re, sys, os
from collections import Counter, defaultdict
LOG, R, V = sys.argv[1:4]
lines = open(LOG, encoding='cp1252', errors='replace').read().splitlines()

# vanilla files LI does NOT override (they load from the game folder)
def rel(root, d):
    out = set()
    for dp, _, fs in os.walk(os.path.join(root, d)):
        for f in fs: out.add(os.path.relpath(os.path.join(dp, f), root).replace(chr(92), '/').lower())
    return out
li_files = set().union(*(rel(R, d) for d in ('common', 'events', 'decisions', 'localisation', 'interface', 'music', 'dlc_metadata')))

DLC = [  # (label, filename/namespace pattern)
    ('Holy Fury', r'(^|/)(hf|hfp)_|\bHFP?\.|holy_fury|_fylkir|dead_crown|crusader_(king|queen)|coronation|warrior_lodge|bloodline'),
    ('Jade Dragon', r'(^|/)jd_|\bJD\.|jade_dragon|offmap|kowtow|chinese'),
    ("Monks and Mystics", r'(^|/)mnm_|\bMNM\.|societ'),
    ("Reaper's Due", r'(^|/)rip_|\bRIP\.|disease|hospital'),
    ('Way of Life', r'(^|/)wol_|\bWoL\.'),
    ('Conclave', r'(^|/)(cm|cl)_|council'),
    ('Sons of Abraham', r'(^|/)soa_|\bSoA\.'),
    ('Legacy of Rome / Charlemagne / other', r'(^|/)(lt|ze|tog|sb|sunset|aztec|rajas|horse_lords|hl)_|\bLT\.|\bZE\.|\bHL\.'),
]
def bucket(l):
    fm = re.search(r'file:\s*(?:file:\s*)?([\w/.-]+\.(?:txt|gfx|gui|csv))', l)
    f = fm.group(1).lower() if fm else ''
    if 'customizable_localisation' in f or 'custom_localisation' in f:
        return 'Localisation (customizable loc)', f
    if 'dlc_recommendations' in f: return 'DLC store hints (dlc_recommendations)', f
    if 'portrait_properties' in f or f.startswith('interface/') or 'gfx' in l.lower() and not f: return 'Interface / portraits', f
    if f.startswith('music/'): return 'Music files', f
    key = f or l
    for name, pat in DLC:
        if re.search(pat, key, re.I): return name, f
    m = re.search(r'event: "([\w.]+)"', l)
    if m:
        for name, pat in DLC:
            if re.search(pat, m.group(1), re.I): return name, 'on_action -> ' + m.group(1).split('.')[0]
    return 'Other / LI own', f or re.sub(r'^\[[^\]]*\]: ', '', l)[:70]

c = Counter(); files = defaultdict(Counter); vanilla_only = Counter()
for l in lines:
    b, f = bucket(l); c[b] += 1; files[b][re.sub(r'line: ?\d+', '', f)] += 1
    if f and '/' in f and not f.startswith('on_action') and f not in li_files: vanilla_only[b] += 1
print(f'total {len(lines)} lines')
for b, n in c.most_common():
    print(f'\n{n:5}  {b}   (from vanilla files LI does not override: {vanilla_only[b]})')
    for f, k in files[b].most_common(7): print(f'         {k:5}  {f[:90]}')
