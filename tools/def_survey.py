"""Classify every LI definition (event, decision, effect, trigger, modifier...) as new / unchanged / changed
against vanilla and CleanSlate.
usage: python -I def_survey.py <mod_dir> <cleanslate_dir> <vanilla_dir> <out.json>"""
import os, re, sys, json
from collections import Counter, defaultdict
LI, CS, VA, OUT = sys.argv[1:5]
def rd(p): return open(p, 'rb').read().decode('latin-1')
def canon(t):  # compare ignoring comments, whitespace and formatting
    t = re.sub(r'#[^\n]*', '', t); return re.sub(r'\s+', ' ', re.sub(r'\s*([{}=<>])\s*', r'\1', t)).strip()

def blocks(text):
    """yield (key, text) of top-level blocks; for decisions/on_actions-style files also one level down"""
    t = text; i = 0; n = len(t); depth = 0; out = []
    tok = re.compile(r'#[^\n]*|"[^"]*"|\{|\}|([\w.:@-]+)\s*=\s*\{')
    stack = []
    for m in tok.finditer(t):
        s = m.group(0)
        if s.startswith('#') or s.startswith('"'): continue
        if s == '}':
            if stack:
                k, st, d = stack.pop()
                if k is not None: out.append((k, d, t[st:m.end()]))
            continue
        k = m.group(1) if s != '{' else None
        stack.append((k, m.start(), len(stack)))
    return out

def defs(root):
    d = {}  # (kind, key) -> (canon text, file)
    for top in ('common', 'decisions', 'events'):
        for dp, _, fs in os.walk(os.path.join(root, top)):
            if '.transfer' in dp: continue
            for f in fs:
                if not f.endswith('.txt'): continue
                p = os.path.join(dp, f); rel = os.path.relpath(p, root).replace(chr(92), '/')
                t = rd(p)
                if top == 'events':
                    for m in re.finditer(r'(?m)^(\w+_event)\s*=\s*\{', re.sub(r'#[^\n]*', '', t)):
                        pass
                    nc = re.sub(r'#[^\n]*', '', t)
                    for k, dep, b in blocks(nc):
                        if dep == 0 and k.endswith('_event'):
                            im = re.search(r'\bid\s*=\s*([\w.]+)', b)
                            if im: d[('event', im.group(1))] = (canon(b), rel)
                else:
                    kind = '/'.join(rel.split('/')[:2]) if top == 'common' else 'decisions'
                    nc = re.sub(r'#[^\n]*', '', t)
                    want = 1 if top == 'decisions' or kind in ('common/on_actions',) else 0
                    for k, dep, b in blocks(nc):
                        if dep == want: d[(kind, k)] = (canon(b), rel)
    return d
li, va, cs = defs(LI), defs(VA), defs(CS)
cat = Counter(); per = defaultdict(Counter); rows = []
for key, (t, f) in li.items():
    if key not in va:
        c = 'new in LI' + (' (also in CleanSlate!)' if key in cs else '')
    elif t == va[key][0]: c = 'unchanged from vanilla 3.3.3 (drop, take CleanSlate)'
    else: c = 'LI differs from vanilla 3.3.3 (review: LI change or older vanilla?)'
    cat[c] += 1; per[c][key[0] if key[0] != 'event' else 'events'] += 1; rows.append((key[0], key[1], f, c))
gone = [k for k in va if k not in li and k[0] in {x[0] for x in li}]
print('LI definitions:', len(li))
for c, n in cat.most_common():
    print(f'\n{n:6}  {c}')
    for s, m in per[c].most_common(10): print(f'          {m:5}  {s}')
print('\nvanilla definitions LI dropped (kinds LI overrides):', len(gone))
json.dump(rows, open(OUT, 'w'))
