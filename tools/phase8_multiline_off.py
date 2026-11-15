"""Find multi-line switch-offs ('#xxx = { # <note>' followed by commented lines) whose block calls events the mod now defines.
usage: multiline_off.py [--apply] [--keep-off=<ids file>]   (run from the repo root). --apply uncomments those blocks (strips one '#' per line and the note)."""
import re, glob, sys
APPLY = '--apply' in sys.argv
_ko = next((a.split('=', 1)[1] for a in sys.argv if a.startswith('--keep-off=')), None)
KEEP_OFF = {l.strip() for l in open(_ko) if l.strip()} if _ko else set()
NOTES = ['event left out of the CleanSlate build: LI never had it (decision 6, CLEANSLATE_PLAN.md)',
         'Holy Fury event not in Lux Invicta (DLC switched off)',
         'Holy Fury event from a later phase 8 part, not restored yet (CLEANSLATE_PLAN.md)']
def rd(p): return open(p, 'rb').read().decode('latin-1')
DEF = re.compile(r'(?m)^\w+_event[ \t]*=[ \t]*\{[^\n]*\n?(?:\s*#[^\n]*\n)*\s*id\s*=\s*([\w.]+)')
have = set()
for p in glob.glob('events/*.txt'): have |= set(DEF.findall(re.sub(r'#[^\n]*', '', rd(p))))
tot = 0
for top in ('common', 'events', 'decisions'):
    for p in glob.glob(top + '/**/*.txt', recursive=True):
        s = rd(p)
        if not any(n in s for n in NOTES): continue
        nl = '\r\n' if '\r\n' in s else '\n'; L = s.replace('\r\n', '\n').split('\n'); ch = False
        i = 0
        while i < len(L):
            l = L[i]; note = next((n for n in NOTES if n in l), None)
            m = re.match(r'^(\s*)#(.*\{)\s*#\s*\(?' + re.escape(note) + r'\)?\s*$', l) if note else None
            if not m: i += 1; continue
            # collect block: count braces in the uncommented text
            body = [m.group(1) + m.group(2)]; d = m.group(2).count('{') - m.group(2).count('}'); j = i + 1
            while d > 0 and j < len(L):
                mm = re.match(r'^(\s*)#(.*)$', L[j])
                if not mm: break
                t = mm.group(1) + mm.group(2); body.append(t)
                code = re.sub(r'#.*', '', mm.group(2)); d += code.count('{') - code.count('}'); j += 1
            if d != 0: print('UNBALANCED', p, i + 1); i += 1; continue
            ids = set(re.findall(r'\bid\s*=\s*([\w.]+)', '\n'.join(re.sub(r'#.*', '', b) for b in body)))
            if ids and ids <= have and not ids & KEEP_OFF:
                tot += 1; print(p, i + 1, sorted(ids))
                if APPLY: L[i:j] = body; ch = True
            i = j
        if ch: open(p, 'wb').write('\n'.join(L).replace('\n', nl).encode('latin-1'))
print(tot, 'blocks', '(applied)' if APPLY else '')
