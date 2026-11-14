"""Switch off calls to Holy Fury events that Lux Invicta does not ship.
usage: python -I hf_off.py <mod_dir> <vanilla_dir> [--apply]"""
import os, re, sys
from collections import defaultdict
R, V = sys.argv[1:3]; APPLY = '--apply' in sys.argv
NOTE = b'Holy Fury event not in Lux Invicta (DLC switched off)'

def rd(p): return open(p, 'rb').read()
def strip(b): return re.sub(rb'#[^\n]*', b'', b)

# an event DEFINITION starts a top-level line; calls are nested, so they do not count
DEF = re.compile(rb'(?m)^\w+_event\s*=\s*\{\s*id\s*=\s*([\w.]+)')
vdef = {}
for f in os.listdir(V + '/events'):
    if f.endswith('.txt'):
        for m in re.finditer(DEF, strip(rd(V + '/events/' + f))): vdef.setdefault(m.group(1), f)
lidef = set()
for f in os.listdir(R + '/events'):
    if f.endswith('.txt'): lidef |= set(re.findall(DEF, strip(rd(R + '/events/' + f))))
HF = {i for i, f in vdef.items() if re.match(r'(?i)(hf|hfp)_', f) and i not in lidef}

report = defaultdict(list); manual = []

def fix_on_actions(path, b):
    nl = b'\r\n' if b'\r\n' in b else b'\n'
    out = []; pos = 0; changed = False
    for m in re.finditer(rb'^([ \t]*)(events|random_events)\s*=\s*\{', b, re.M):
        # find matching close brace (lists are flat, but may contain comments)
        start = m.end(); depth = 1; i = start
        while depth:
            c = b[i:i + 1]
            if c == b'#': i = b.find(b'\n', i); continue
            if c == b'{': depth += 1
            elif c == b'}': depth -= 1
            i += 1
        body = b[start:i - 1]; removed = []
        def drop(line):
            code, _, com = line.partition(b'#')
            if m.group(2) == b'random_events':
                new = re.sub(rb'\b\d+\s*=\s*([A-Za-z_]+\.\d+)\b', lambda x: (removed.append(x.group(1)) or b'') if x.group(1) in HF else x.group(0), code)
            else:
                new = re.sub(rb'(?<![\w.])([A-Za-z_]+\.\d+)\b', lambda x: (removed.append(x.group(1)) or b'') if x.group(1) in HF else x.group(0), code)
            return new + (b'#' + com if _ else b'')
        nb = b'\n'.join(drop(l) for l in body.split(b'\n'))
        if removed:
            changed = True
            ind = m.group(1) + b'\t'
            note = nl + ind + b'# removed: ' + b' '.join(removed) + b' - ' + NOTE
            out.append(b[pos:start] + note + nb); pos = i - 1
            report[path] += [x.decode() for x in removed]
    out.append(b[pos:])
    return b''.join(out), changed

def fix_calls(path, b):
    lines = b.split(b'\n'); changed = False
    text = b
    # map byte offset -> line index
    starts = [0]
    for l in lines[:-1]: starts.append(starts[-1] + len(l) + 1)
    import bisect
    to_comment = set()
    for m in re.finditer(rb'\b(character_event|province_event|letter_event|narrative_event|repeat_event)\s*=\s*\{\s*id\s*=\s*([\w.]+)', text):
        if m.group(2) not in HF: continue
        ln = bisect.bisect_right(starts, m.start()) - 1
        if b'#' in text[starts[ln]:m.start()]: continue  # already commented
        # find the end of this call block
        i = text.find(b'{', m.start()) + 1; depth = 1
        while depth:
            c = text[i:i + 1]
            if c == b'#': i = text.find(b'\n', i); continue
            if c == b'{': depth += 1
            elif c == b'}': depth -= 1
            i += 1
        le = bisect.bisect_right(starts, i - 1) - 1
        before = text[starts[ln]:m.start()].strip(); after = text[i:starts[le] + len(lines[le])].strip()
        if before or (after and not after.startswith(b'#')):
            # allow one-line wrappers that contain only this call, e.g. "scope = { character_event = { ... } }"
            a_code = after.split(b'#')[0].strip()
            wrap_open = re.fullmatch(rb'(?:[\w:.@]+\s*=\s*\{\s*)+', before) if before else None
            n_open = len(re.findall(rb'\{', before)); n_close = a_code.count(b'}')
            if not (ln == le and wrap_open and re.fullmatch(rb'(?:\}\s*)+', a_code or b'') and n_open == n_close):
                manual.append((path, ln + 1, m.group(2).decode())); continue
            # weighted option of a random_list ("30 = { character_event = {...} }"): keep the weight, empty the option
            wm = re.fullmatch(rb'(\d+)\s*=\s*\{\s*', before)
            if wm:
                l = lines[ln]; cr = l.endswith(b'\r'); body = l[:-1] if cr else l
                ind = re.match(rb'[ \t]*', body).group(0)
                lines[ln] = ind + wm.group(1) + b' = { } # was: ' + body[len(ind):].strip() + b' (' + NOTE + b')' + (b'\r' if cr else b'')
                report[path].append(m.group(2).decode()); changed = True
                continue
        for k in range(ln, le + 1): to_comment.add(k)
        report[path].append(m.group(2).decode())
    if not to_comment: return (b'\n'.join(lines), True) if changed else (b, False)
    first = True
    for k in sorted(to_comment):
        l = lines[k]; cr = l.endswith(b'\r'); body = l[:-1] if cr else l
        ind = re.match(rb'[ \t]*', body).group(0)
        tag = b' # ' + NOTE if (k - 1) not in to_comment else b''
        lines[k] = ind + b'#' + body[len(ind):] + tag + (b'\r' if cr else b'')
    return b'\n'.join(lines), True

for d in ('common', 'events', 'decisions'):
    for dp, _, fs in os.walk(os.path.join(R, d)):
        for f in fs:
            if not f.endswith('.txt'): continue
            p = os.path.join(dp, f); rp = os.path.relpath(p, R).replace(chr(92), '/'); b = rd(p)
            if 'on_actions' in rp: continue  # on_actions are handled line by line by hf_off_onactions.py
            nb, ch1 = b, False
            nb, ch2 = fix_calls(rp, nb)
            if (ch1 or ch2) and APPLY:
                open(p, 'wb').write(nb)

tot = sum(len(v) for v in report.values())
print(f'Holy Fury IDs missing from LI: {len(HF)} | calls switched off: {tot} in {len(report)} files')
for p, v in sorted(report.items(), key=lambda x: -len(x[1])): print(f'  {len(v):4}  {p}')
print('needs manual handling (call shares a line with other code):', len(manual))
for x in manual: print('   ', x)
