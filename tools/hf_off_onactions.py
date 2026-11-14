"""Comment out Holy Fury event IDs in on_actions lists, line by line, keeping their descriptions.
usage: python -I hf_off_onactions.py <mod_dir> <vanilla_dir> <on_actions file (relative)>"""
import os, re, sys
R, V, F = sys.argv[1:4]
NOTE = b' (Holy Fury event not in Lux Invicta, DLC switched off)'
def rd(p): return open(p, 'rb').read()
def strip(b): return re.sub(rb'#[^\n]*', b'', b)
vdef = {}
for f in os.listdir(V + '/events'):
    if f.endswith('.txt'):
        for m in re.finditer(rb'\bid\s*=\s*([\w.]+)', strip(rd(V + '/events/' + f))): vdef.setdefault(m.group(1), f)
lidef = set()
for f in os.listdir(R + '/events'):
    if f.endswith('.txt'): lidef |= set(re.findall(rb'\bid\s*=\s*([\w.]+)', strip(rd(R + '/events/' + f))))
HF = {i for i, f in vdef.items() if re.match(r'(?i)(hf|hfp)_', f) and i not in lidef}

p = os.path.join(R, F); b = rd(p); lines = b.split(b'\n')
in_list = False; depth = 0; kind = None; done = 0; partial = 0
for k, l in enumerate(lines):
    code = l.split(b'#')[0]
    if not in_list:
        m = re.match(rb'\s*(events|random_events)\s*=\s*\{', code)
        if m:
            in_list = True; kind = m.group(1); depth = code.count(b'{') - code.count(b'}')
            if depth <= 0: in_list = False
        continue
    depth += code.count(b'{') - code.count(b'}')
    cr = l.endswith(b'\r'); body = l[:-1] if cr else l
    c, sep, com = body.partition(b'#')
    tokpat = rb'^\s*\d+\s*=\s*([A-Za-z_]+\.\d+)\s*$' if kind == b'random_events' else rb'^\s*([A-Za-z_]+\.\d+)\s*$'
    m = re.match(tokpat, c)
    if m and m.group(1) in HF:
        ind = re.match(rb'[ \t]*', body).group(0)
        rest = body[len(ind):]
        tail = (b'' if sep else b' #') + NOTE
        lines[k] = ind + b'#' + rest + tail + (b'\r' if cr else b'')
        done += 1
    elif any(t in HF for t in re.findall(rb'([A-Za-z_]+\.\d+)', c)):
        partial += 1; print('line with several IDs, left as is:', k + 1, c.strip()[:80])
    if depth <= 0: in_list = False
open(p, 'wb').write(b'\n'.join(lines))
print('commented', done, 'IDs; lines needing manual work:', partial)
