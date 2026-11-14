"""Phase 5, decision 6: leave out CleanSlate event/decision definitions that LI (master) never had.
usage: python -I phase5_leave_out.py <repo_dir> <master_tree> <removed_ids_out.txt> [--apply]
- Only CleanSlate's files (not li_*) are touched.
- Kept: events LI had; events called from LI's own files (li_*, history, LI on_actions...), with
  everything they call; decisions LI had, counting CleanSlate's renames (catholic_pilgrimage ->
  christian_pilgrimage).
- Removed definitions are cut out with their comment lines; a file left with no definitions is deleted.
- Writes the removed event IDs to <removed_ids_out.txt> for the call switch-off (hf_off.py --ids-file)."""
import os, re, sys
from collections import Counter
REPO, MT, OUT = sys.argv[1:4]; APPLY = '--apply' in sys.argv
def rd(p): return open(p, 'rb').read()
def nc(b): return re.sub(rb'#[^\n]*', b'', b)
DEF = re.compile(rb'(?m)^\w+_event[ \t]*=[ \t]*\{[ \t]*(?:#[^\n]*)?\s*(?:#[^\n]*\n\s*)*id\s*=\s*([\w.]+)')
CALL = re.compile(rb'\bid\s*=\s*([\w.]+)')

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
def with_comments(b, st):
    ls = b.rfind(b'\n', 0, st) + 1
    while ls > 0:
        pls = b.rfind(b'\n', 0, ls - 1) + 1
        if b[pls:ls - 1].strip().startswith(b'#'): ls = pls
        else: break
    return ls

# --- what LI had
li_ev = set(); li_dec = set()
for f in os.listdir(os.path.join(MT, 'events')):
    if f.endswith('.txt'): li_ev |= {x.decode() for x in DEF.findall(rd(os.path.join(MT, 'events', f)))}
for f in os.listdir(os.path.join(MT, 'decisions')):
    if f.endswith('.txt'): li_dec |= {k.decode() for k, _, _ in blocks(rd(os.path.join(MT, 'decisions', f)), 1)}
log = rd(os.path.join(REPO, 'cleanslate_beta7', 'master_changelog.txt')).decode('latin-1')
for a, b in re.findall(r'-\s*([\w.]+)\s*->\s*([\w.]+)', log):
    if a in li_dec: li_dec.add(b)

# --- CleanSlate's event definitions on the branch
ev_file = {}; ev_body = {}
for f in os.listdir(os.path.join(REPO, 'events')):
    if not f.endswith('.txt') or f.lower().startswith('li_'): continue
    b = rd(os.path.join(REPO, 'events', f))
    for m in DEF.finditer(b):
        i = m.group(1).decode(); ev_file[i] = f
# calls from LI's own content keep CleanSlate events alive (closure)
roots = []
for top in ('events', 'decisions', 'common', 'history'):
    for dp, _, fs in os.walk(os.path.join(REPO, top)):
        for f in fs:
            if f.lower().startswith('li_') or top == 'history':
                roots += [x.decode() for x in CALL.findall(nc(rd(os.path.join(dp, f))))]
keep = set(i for i in ev_file if i in li_ev)
todo = [i for i in roots if i in ev_file]
cache = {}
def ev_text(i):
    f = ev_file[i]
    if f not in cache: cache[f] = rd(os.path.join(REPO, 'events', f))
    b = cache[f]; m = re.search(rb'(?m)^\w+_event[ \t]*=[ \t]*\{[ \t]*(?:#[^\n]*)?\s*(?:#[^\n]*\n\s*)*id\s*=\s*' + re.escape(i.encode()) + rb'\b', b)
    for k, st, en in blocks(b, 0):
        if st == m.start(): return b[st:en]
    return b''
while todo:
    i = todo.pop()
    if i in keep or i not in ev_file: continue
    keep.add(i); todo += [x.decode() for x in CALL.findall(nc(ev_text(i)))]
for i in list(keep):   # also everything kept events call
    todo += [x.decode() for x in CALL.findall(nc(ev_text(i)))]
while todo:
    i = todo.pop()
    if i in keep or i not in ev_file: continue
    keep.add(i); todo += [x.decode() for x in CALL.findall(nc(ev_text(i)))]
remove_ev = {i for i in ev_file if i not in keep}

stats = Counter(); deleted = []; written = 0
def process(folder, depth, is_removed):
    global written
    for f in sorted(os.listdir(os.path.join(REPO, folder))):
        if not f.endswith('.txt') or f.lower().startswith('li_'): continue
        p = os.path.join(REPO, folder, f); b = rd(p)
        bl = blocks(b, depth); cut = []
        for k, st, en in bl:
            if folder == 'events':
                if not k.endswith(b'_event'): continue
                m = CALL.search(nc(b[st:en])); key = m.group(1).decode() if m else None
            else: key = k.decode()
            if key and is_removed(key): cut.append((with_comments(b, st), en, key))
        if not cut: continue
        stats[folder + ' definitions removed'] += len(cut)
        left = len([1 for k, st, en in bl if (folder != 'events' or k.endswith(b'_event'))]) - len(cut)
        if left == 0:
            deleted.append(folder + '/' + f)
            if APPLY: os.remove(p)
            continue
        nb = b
        for st, en, key in sorted(cut, reverse=True):
            e2 = en
            while e2 < len(nb) and nb[e2:e2 + 1] in (b' ', b'\t'): e2 += 1
            if nb[e2:e2 + 2] == b'\r\n': e2 += 2
            elif nb[e2:e2 + 1] == b'\n': e2 += 1
            nb = nb[:st] + nb[e2:]
        t = nc(nb); assert t.count(b'{') == t.count(b'}'), 'brace mismatch after cut: ' + f
        written += 1
        if APPLY: open(p, 'wb').write(nb)
process('events', 0, lambda k: k in remove_ev)
process('decisions', 1, lambda k: k not in li_dec)
print(dict(stats), '| files emptied and deleted:', len(deleted), '| files rewritten:', written)
print('CleanSlate events kept because LI calls them (not in master):', len([i for i in keep if i not in li_ev]))
print('sample deleted files:', deleted[:12])
open(OUT, 'w').write('\n'.join(sorted(remove_ev)) + '\n')
print('removed event ids written to', OUT, len(remove_ev))
