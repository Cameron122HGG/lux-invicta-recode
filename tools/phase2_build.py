"""Phase 2 of CLEANSLATE_PLAN.md: bring LI's new definitions back from master as li_* files.
usage: python -I phase2_build.py <repo_dir> <master_tree> <vanilla_dir> [--apply]
  <master_tree>: an export of master's common/ events/ decisions/ (e.g. `git archive master common events decisions | tar -x -C <dir>`)
Dry run by default.

Rules
- Folders LI replaced wholesale in its old .mod (buildings, trade_routes, societies, artifacts,
  artifact_spawns): LI's folder replaces CleanSlate's whole (files renamed li_*).
- A master file that defines nothing vanilla also defines: copied whole as li_<name> (comments kept).
- A master file that overrides/extends vanilla: only the definitions vanilla does not have are
  extracted into li_<name>, with the wrappers they need (event namespaces, decisions = {...},
  government groups). LI's changes to vanilla definitions are phase 3 and are not touched here.
- Skipped: world folders (already in place), common/on_actions (phase 3), achievements."""
import os, re, sys, shutil
from collections import Counter, defaultdict
REPO, MT, VA = sys.argv[1:4]; APPLY = '--apply' in sys.argv
OWNED = ['common/buildings', 'common/trade_routes', 'common/societies', 'common/artifacts', 'common/artifact_spawns']
WORLD = ['common/landed_titles', 'common/cultures', 'common/religions', 'common/dynasties',
         'common/graphicalculturetypes', 'common/bookmarks', 'common/defines']
SKIP = ['common/on_actions', 'common/achievements.txt', 'common/defines.txt']
WRAP_DEPTH1 = {'decisions': True, 'common/governments': True}   # definitions sit one level down

def rd(p): return open(p, 'rb').read()
def nc(b): return re.sub(rb'#[^\n]*', b'', b)
def folder(rel):
    parts = rel.split('/')
    return parts[0] if parts[0] in ('events', 'decisions') else '/'.join(parts[:2])

def top_blocks(b, depth_want):
    """yield (key, start, end, parent_key) for blocks at depth_want, positions in the ORIGINAL bytes;
    start includes the comment lines directly above the block"""
    out = []; stack = []
    for m in re.finditer(rb'#[^\n]*|"[^"\n]*"|\{|\}|([\w.:@-]+)[ \t\r\n]*=[ \t\r\n]*\{', b):
        s = m.group(0)
        if s.startswith(b'#') or s.startswith(b'"'): continue
        if s == b'}':
            if stack:
                k, st, d, par = stack.pop()
                if d == depth_want and k is not None: out.append((k, st, m.end(), par))
            continue
        k = m.group(1)
        par = stack[-1][0] if stack else None
        stack.append((k, m.start(), len(stack), par))
    return out

def keyset(root, fol, depth):
    ks = set()
    base = os.path.join(root, fol)
    if not os.path.isdir(base): return ks
    for dp, _, fs in os.walk(base):
        for f in fs:
            if not f.endswith('.txt'): continue
            b = nc(rd(os.path.join(dp, f)))
            if fol == 'events':
                ks |= set(x.decode() for x in re.findall(rb'(?m)^\w+_event\s*=\s*\{\s*id\s*=\s*([\w.]+)', b))
            else:
                ks |= set(k.decode() for k, *_ in top_blocks(b, depth))
    return ks

def start_with_comments(b, st):
    # extend start upward over directly preceding comment / blank lines
    ls = b.rfind(b'\n', 0, st) + 1
    while True:
        prev_end = ls - 1
        if prev_end <= 0: break
        pls = b.rfind(b'\n', 0, prev_end) + 1
        line = b[pls:prev_end].strip()
        if line.startswith(b'#'): ls = pls
        else: break
    return ls

files = []
for top in ('common', 'events', 'decisions'):
    for dp, _, fs in os.walk(os.path.join(MT, top)):
        for f in fs: files.append(os.path.relpath(os.path.join(dp, f), MT).replace(os.sep, '/'))
plan = []; stats = Counter(); per = defaultdict(Counter); dup_cs = []
vkeys = {}; ckeys = {}
for rel in sorted(files):
    fol = folder(rel); name = os.path.basename(rel)
    if any(rel == s or rel.startswith(s + '/') for s in WORLD + SKIP): continue
    dst = os.path.dirname(rel) + '/' + (name if name.lower().startswith('li_') else 'li_' + name)
    if fol in OWNED:
        plan.append(('copy', rel, dst, None)); stats['owned folder: copied whole'] += 1; per['owned folder'][fol] += 1; continue
    if not name.endswith('.txt'):
        continue
    depth = 1 if fol in WRAP_DEPTH1 else 0
    if fol not in vkeys: vkeys[fol] = keyset(VA, fol, depth); ckeys[fol] = keyset(os.path.join(REPO), fol, depth)
    # positions must come from the ORIGINAL bytes (top_blocks skips comments itself); they are used
    # to cut the definitions out of the original file
    b = rd(os.path.join(MT, rel))
    if fol == 'events':
        blocks = [(k, st, en, par) for k, st, en, par in top_blocks(b, 0) if k.endswith(b'_event')]
        ids = []
        for k, st, en, par in blocks:
            im = re.search(rb'\bid\s*=\s*([\w.]+)', nc(b[st:en])); ids.append(im.group(1).decode() if im else None)
        keyed = list(zip(ids, blocks))
    else:
        keyed = [(k.decode(), (k, st, en, par)) for k, st, en, par in top_blocks(b, depth)]
    new = [(k, bl) for k, bl in keyed if k and k not in vkeys[fol]]
    old = [(k, bl) for k, bl in keyed if k and k in vkeys[fol]]
    clash = [k for k, _ in new if k in ckeys[fol]]
    dup_cs += [(rel, k) for k in clash]
    # keys CleanSlate also defines (shared CK2Plus heritage): CleanSlate's version is used for now,
    # LI's goes on the phase 3 review list
    new = [(k, bl) for k, bl in new if k not in ckeys[fol]]
    if not new: stats['nothing new (phase 3 only)'] += 1; continue
    if not old and not clash:
        plan.append(('copy', rel, dst, None)); stats['LI-only file: copied whole'] += 1; per['whole'][fol] += 1
    else:
        plan.append(('extract', rel, dst, new)); stats['extracted from vanilla-derived file'] += 1
        per['extracted defs'][fol] += len(new)
print({k: v for k, v in stats.items()})
for g, c in per.items():
    print(f'\n{g}:'); [print(f'   {n:5}  {k}') for k, n in c.most_common(12)]
print('\nnew LI keys that CleanSlate also defines (would clash):', len(dup_cs), dup_cs[:10])

def build_extract(rel, new):
    b = rd(os.path.join(MT, rel)); nl = b'\r\n' if b'\r\n' in b else b'\n'
    out = [b'# Lux Invicta definitions extracted from master:' + rel.encode() + b' (phase 2 of CLEANSLATE_PLAN.md).',
           b'# Only definitions vanilla does not have; LI changes to vanilla definitions are handled in phase 3.', b'']
    fol = folder(rel)
    if fol == 'events':
        out += [m.group(0).strip() for m in re.finditer(rb'(?m)^\s*namespace\s*=\s*\w+', nc(b))] + [b'']
        out += [b[start_with_comments(b, st):en] for k, (kk, st, en, par) in new]
    elif fol in WRAP_DEPTH1:
        groups = defaultdict(list)
        for k, (kk, st, en, par) in new: groups[par].append(b[start_with_comments(b, st):en])
        for par, parts in groups.items():
            out += [par + b' = {'] + parts + [b'}', b'']
    else:
        out += [b[start_with_comments(b, st):en] + nl for k, (kk, st, en, par) in new]
    return nl.join(x.rstrip(b'\r\n') if not x.endswith(nl) else x.rstrip(b'\r\n') for x in out) + nl

if APPLY:
    notes = os.path.join(REPO, 'migration_notes'); os.makedirs(notes, exist_ok=True)
    with open(os.path.join(notes, 'phase2_clashes.txt'), 'w', encoding='utf-8', newline='\r\n') as o:
        o.write('# Phase 2: LI definitions whose key CleanSlate also defines. CleanSlate\'s version is used;\n'
                '# review LI\'s version (from master) in phase 3.  <master file>\t<key>\n')
        for rel, k in dup_cs: o.write(f'{rel}\t{k}\n')
    for fol in OWNED:  # LI's folder replaces CleanSlate's
        d = os.path.join(REPO, fol)
        if os.path.isdir(d): shutil.rmtree(d)
    for kind, rel, dst, new in plan:
        p = os.path.join(REPO, dst); os.makedirs(os.path.dirname(p), exist_ok=True)
        assert not os.path.exists(p), 'exists: ' + dst
        data = rd(os.path.join(MT, rel)) if kind == 'copy' else build_extract(rel, new)
        open(p, 'wb').write(data)
    print('\napplied:', len(plan), 'files written')
