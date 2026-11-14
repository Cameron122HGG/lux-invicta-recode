"""Add missing building prerequisites in province history (Lux Invicta CleanSlate).
usage: python -I fix_buildings.py <mod_dir> <error.log> <backup_dir> [--apply]"""
import os, re, sys, shutil
from collections import defaultdict

MOD, LOG, BAK = sys.argv[1:4]
APPLY = "--apply" in sys.argv

def rd(p): return open(p, 'rb').read().decode('cp1252')

# --- building definitions: name -> (holding_type, [requirements])
bdefs = {}
for f in os.listdir(os.path.join(MOD, 'common/buildings')):
    t = re.sub(r'#[^\n]*', '', rd(os.path.join(MOD, 'common/buildings', f)))
    depth, holding, cur, start = 0, None, None, 0
    for m in re.finditer(r'([\w-]+)\s*=\s*\{|\{|\}', t):
        s = m.group(0)
        if s == '{': depth += 1; continue
        if s == '}':
            depth -= 1
            if depth == 1 and cur:
                body = t[start:m.start()]
                req = []
                pm = re.search(r'prerequisites\s*=\s*\{([^}]*)\}', body)
                if pm: req += pm.group(1).split()
                um = re.search(r'upgrades_from\s*=\s*(\w+)', body)
                if um: req.append(um.group(1))
                bdefs[cur] = (holding, req); cur = None
            continue
        key = m.group(1)
        if depth == 0: holding = key
        elif depth == 1: cur, start = key, m.end()
        depth += 1

PREFIX = {'castle': 'ca', 'city': 'ct', 'temple': 'tp'}

def closure(b, have, out):
    for r in bdefs.get(b, (None, []))[1]:
        if r not in have and r not in out:
            closure(r, have, out)
            out.append(r)

log = open(LOG, encoding='cp1252', errors='replace').read()
holdings = sorted(set(re.findall(r"constructed in '(\w+)' while", log)))

files = {}
for f in os.listdir(os.path.join(MOD, 'history/provinces')):
    t = rd(os.path.join(MOD, 'history/provinces', f))
    for h in holdings:
        if re.search(r'^\s*' + h + r'\s*=\s*(castle|city|temple)\b', t, re.M):
            files[h] = f

report = []
for h in holdings:
    path = os.path.join(MOD, 'history/provinces', files[h])
    raw = rd(path); nl = '\r\n' if '\r\n' in raw else '\n'
    lines = raw.split(nl)
    htype = re.search(r'^\s*' + h + r'\s*=\s*(\w+)', raw, re.M).group(1)
    pre = PREFIX[htype]
    have, out, changes = set(), [], []
    for line in lines:
        m = re.match(r'^(\s*)' + h + r'\s*=\s*(\w+_\d+)\s*$', line)
        if not m:
            out.append(line); continue
        ind, b = m.group(1), m.group(2)
        btype = bdefs.get(b, (None,))[0]
        if btype and btype != htype:
            nb = pre + b[2:] if b[:2] in ('ca', 'ct', 'tp') else None
            if nb in bdefs:
                changes.append(f"{b} -> {nb} (wrong holding type)"); b = nb
            else:
                changes.append(f"{b} commented out (no {htype} equivalent)")
                out.append(f"{ind}#{h} = {b} # {htype} holding cannot have this building"); continue
        if b in have:
            changes.append(f"duplicate {b} removed"); continue
        need = []; closure(b, have, need)
        for r in need:
            out.append(f"{ind}{h} = {r}"); have.add(r)
        if need: changes.append(f"{b}: added {' '.join(need)}")
        out.append(f"{ind}{h} = {b}"); have.add(b)
    report.append((h, htype, files[h], changes))
    if APPLY and out != lines:
        dst = os.path.join(BAK, 'history__provinces__' + files[h])
        if not os.path.exists(dst): shutil.copy(path, dst)
        open(path, 'wb').write(nl.join(out).encode('cp1252'))

for h, ht, f, ch in report:
    print(f"== {h} ({ht}) {f}")
    for c in ch: print("   ", c)
