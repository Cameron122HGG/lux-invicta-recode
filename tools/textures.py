"""For each "inexistent texture" in error.log, look for the file elsewhere (other folder, other extension, vanilla).
usage: python -I textures.py <mod_dir> <vanilla_dir> <error.log>"""
import os, re, sys
from collections import defaultdict
R, V, LOG = sys.argv[1:4]
BS = chr(92)
log = open(LOG, encoding='cp1252', errors='replace').read()
miss = re.findall(r'Sprite type "([^"]+)" is referencing inexistent texture: "([^"]+)"', log)

def index(root):
    by_name = defaultdict(list)
    for dp, dn, fs in os.walk(os.path.join(root, 'gfx')):
        for f in fs:
            by_name[f.lower()].append(os.path.relpath(os.path.join(dp, f), root).replace(BS, '/'))
    return by_name
li, va = index(R), index(V)

# which .gfx file defines each sprite
gfxdef = {}
for dp, dn, fs in os.walk(os.path.join(R, 'interface')):
    for f in fs:
        if f.endswith('.gfx'):
            t = open(os.path.join(dp, f), 'rb').read().decode('cp1252', 'replace')
            for m in re.finditer(r'name\s*=\s*"([^"]+)"', t):
                gfxdef.setdefault(m.group(1), os.path.relpath(os.path.join(dp, f), R).replace(BS, '/'))

for sprite, tex in sorted(set(miss), key=lambda x: x[1]):
    tex = tex.replace(BS, '/')
    name = tex.split('/')[-1].lower(); stem = name.rsplit('.', 1)[0]
    same = li.get(name, [])
    other_ext = [p for k, v in li.items() if k.rsplit('.', 1)[0] == stem and k != name for p in v]
    vexists = os.path.exists(os.path.join(V, tex))
    folder_exists = os.path.isdir(os.path.join(R, os.path.dirname(tex)))
    print(f"{sprite:48} {tex}")
    print(f"    defined in {gfxdef.get(sprite,'?')} | folder in LI: {folder_exists} | in vanilla at same path: {vexists}")
    if same: print('    same filename in LI:', same[:3])
    if other_ext: print('    other extension in LI:', other_ext[:3])
