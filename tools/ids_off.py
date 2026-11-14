"""Switch off calls to given event IDs (on_actions lists + one-line call sites).
usage: python -I ids_off.py <mod_dir> "<note>" ID [ID ...]"""
import os, re, sys
R, NOTE = sys.argv[1], sys.argv[2].encode(); IDS = {x.encode() for x in sys.argv[3:]}
tok = rb'(?:[A-Za-z_]+\.)?\d+'
done = []
for d in ('common', 'events', 'decisions'):
    for dp, _, fs in os.walk(os.path.join(R, d)):
        for f in fs:
            if not f.endswith('.txt'): continue
            p = os.path.join(dp, f); b = open(p, 'rb').read(); lines = b.split(b'\n'); ch = False
            in_list = None; depth = 0
            for k, l in enumerate(lines):
                cr = l.endswith(b'\r'); body = l[:-1] if cr else l
                code, sep, com = body.partition(b'#')
                if 'on_actions' in p:
                    if in_list is None:
                        m = re.match(rb'\s*(events|random_events)\s*=\s*\{', code)
                        if m:
                            in_list = m.group(1); depth = code.count(b'{') - code.count(b'}')
                            if depth <= 0: in_list = None
                            continue
                    else:
                        depth += code.count(b'{') - code.count(b'}')
                        ind = re.match(rb'[ \t]*', body).group(0)
                        if in_list == b'random_events':
                            m = re.match(rb'^\s*(\d+)(\s*=\s*)(' + tok + rb')\s*$', code)
                            if m and m.group(3) in IDS:
                                lines[k] = ind + m.group(1) + m.group(2) + b'0 # was ' + m.group(3) + b': ' + (com.strip() + b' ' if sep else b'') + b'(' + NOTE + b')' + (b'\r' if cr else b'')
                                ch = True; done.append((p, m.group(3)))
                        else:
                            m = re.match(rb'^\s*(' + tok + rb')\s*$', code)
                            if m and m.group(1) in IDS:
                                lines[k] = ind + b'#' + body[len(ind):] + (b' (' if sep else b' # (') + NOTE + b')' + (b'\r' if cr else b'')
                                ch = True; done.append((p, m.group(1)))
                        if depth <= 0: in_list = None
                        continue
                # one-line call sites: whole line is "[wrappers =] { ... character_event = { id = X ... } }"
                m = re.search(rb'\b(?:character_event|province_event|letter_event|narrative_event)\s*=\s*\{\s*id\s*=\s*(' + tok + rb')\b', code)
                if m and m.group(1) in IDS and code.count(b'{') == code.count(b'}'):
                    pre = code[:m.start()].strip()
                    if not pre or re.fullmatch(rb'(?:[\w:.@]+\s*=\s*\{\s*)+', pre):
                        ind = re.match(rb'[ \t]*', body).group(0)
                        lines[k] = ind + b'#' + body[len(ind):] + b' # ' + NOTE + (b'\r' if cr else b'')
                        ch = True; done.append((p, m.group(1)))
            if ch: open(p, 'wb').write(b'\n'.join(lines))
for p, i in done: print(os.path.relpath(p, R), i.decode())
print('switched off', len(done))
