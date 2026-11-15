"""Step B (CLEANSLATE_PLAN.md): bring CK2Plus AIO's Buddhist, Bon and Stoic monastic orders into LI, mapped onto LI
faiths (user decisions 2026-11-15):
  - Buddhist order: LI's bud_group faiths + indoh_bud (Indo-Hellenic Buddhism)  -> li_buddhist_monastic_trigger
  - Bon order: LI's 'bon' faith (AIO: bon_pagan)
  - Stoics: the Olympian Champions lodge list (li_lodge_hellenic_trigger); AIO's 'culture = roman' branch is dropped
    (LI has no roman culture, so it could never apply)
  - Apostolic: LI has no Apostolic faith; not added
usage: python -I phase5b_monastic.py <repo> <aio> <ck2plus_aio.zip> <vanilla> [--apply]
Writes (rerunnable, overwrites its own outputs):
  common/scripted_triggers/li_monastic_order_triggers.txt, common/societies/li_CK2Plus_monastic_orders.txt,
  decisions/li_CK2Plus_monastic_decisions.txt (stoic_order_culture_convert_county), events/li_CK2Plus_monastic_events.txt
  (HF.23124/23125), interface/li_CK2Plus_monastic_orders.gfx (Stoic sprites from vanilla, Bon sprites + clothing from
  AIO), the Bon art from the zip, localisation/000_li_monastic_orders.csv (keys AIO has and the mod lacks)."""
import os, re, sys, zipfile, glob
REPO, AIO, ZIP, VA = sys.argv[1:5]
APPLY = '--apply' in sys.argv
def rd(p): return open(p, 'rb').read().decode('latin-1').replace('\r\n', '\n')
def nc(s): return re.sub(r'#[^\n]*', '', s)
def block(s, key, start=0):
    m = re.compile(r'(?m)^[ \t]*' + re.escape(key) + r'[ \t]*=[ \t]*\{').search(s, start)
    if not m: raise SystemExit('missing ' + key)
    return m.start(), close(s, s.index('{', m.start()))
def close(s, i):
    d = 0
    for j in range(i, len(s)):
        c = s[j]
        if c == '#':
            j2 = s.find('\n', j); continue
        if c == '{': d += 1
        elif c == '}':
            d -= 1
            if d == 0: return j + 1
    raise SystemExit('unbalanced')
def get(rel, key):
    s = rd(os.path.join(AIO, rel)); a, b = block(s, key); return s[a:b]
out = {}
# --- triggers
BUD = ['bud_sthaviravada', 'bud_bahusrutiya', 'bud_mahayana', 'bud_pureland', 'bud_pratyeka', 'bud_vajrayana', 'bud_zen',
       'bud_zor', 'indoh_bud']
rels = '\n'.join(f'\t\t\t\treligion = {r}' for r in BUD + [r + '_reformed' for r in []])
out['common/scripted_triggers/li_monastic_order_triggers.txt'] = (
    '# LI RE: faith triggers for the CK2Plus AIO monastic orders mapped onto LI faiths (step B, 2026-11-15; tools/phase5b_monastic.py).\n'
    '# Buddhist order = LI\'s bud_group + Indo-Hellenic Buddhism (user). Stoics use li_lodge_hellenic_trigger, Bon uses religion = bon.\n\n'
    'li_buddhist_monastic_trigger = {\n\tcustom_tooltip = {\n\t\ttext = li_buddhist_monastic_tt\n\t\thidden_trigger = {\n\t\t\tOR = {\n'
    '\t\t\t\treligion_group = bud_group\n\t\t\t\treligion = indoh_bud\n\t\t\t}\n\t\t}\n\t}\n}\n')
# --- societies
bud = get('common/societies/00_monastic_orders.txt', 'monastic_order_buddhist')
bud = re.sub(r'\breligion = buddhist\b', 'li_buddhist_monastic_trigger = yes', bud)
bon = get('common/societies/01_CK2Plus_societies.txt', 'monastic_order_bon')
bon = re.sub(r'\breligion = bon_pagan\b', 'religion = bon', bon)
sto = get('common/societies/00_monastic_orders.txt', 'monastic_order_stoics')
# trigger_if = { limit = { culture = roman } ... } trigger_else = { BODY }  ->  BODY
while True:
    m = re.search(r'trigger_if\s*=\s*\{\s*limit\s*=\s*\{\s*culture\s*=\s*roman\s*\}', sto)
    if not m: break
    a = m.start(); b = close(sto, sto.index('{', a))
    e = re.compile(r'\s*trigger_else\s*=\s*\{').match(sto, b)
    if not e: raise SystemExit('stoics: trigger_if without trigger_else')
    eb = close(sto, sto.index('{', e.start()))
    inner = sto[sto.index('{', e.start()) + 1:eb - 1].strip('\n')
    ind = sto[sto.rfind('\n', 0, a) + 1:a]
    body = '\n'.join(l[1:] if l.startswith('\t') else l for l in inner.split('\n')).strip()
    sto = sto[:a] + '# LI RE: AIO\'s culture = roman branch dropped (no roman culture in LI)\n' + ind + \
          ('\n' + ind).join(x.strip() for x in body.split('\n')) + sto[eb:]
sto = sto.replace('religion_openly_hellenic_or_reformed_trigger = yes', 'li_lodge_hellenic_trigger = yes')
for name, txt in (('buddhist', bud), ('bon', bon), ('stoics', sto)):
    bad = re.findall(r'\b(?:religion|culture)\s*=\s*(buddhist|bon_pagan|roman|hellenic_pagan)\b', nc(txt))
    if bad: raise SystemExit(f'{name}: unmapped {bad}')
out['common/societies/li_CK2Plus_monastic_orders.txt'] = (
    '# LI RE: CK2Plus AIO monastic orders mapped onto LI faiths (step B, 2026-11-15; tools/phase5b_monastic.py)\n\n'
    + '\n\n'.join([bud, bon, sto]) + '\n')
# --- decision + events
dec = get('decisions/HF_religious_decisions.txt', 'stoic_order_culture_convert_county')
# the load-time checker can't read 'culture = owner' (logs pCulture->IsValid); same test written out
assert dec.count("culture = owner # Cannot convert counties of owners' culture") == 1
dec = dec.replace("culture = owner # Cannot convert counties of owners' culture",
                  "owner = { culture = PREV } # Cannot convert counties of owners' culture (LI: was culture = owner)")
out['decisions/li_CK2Plus_monastic_decisions.txt'] = (
    '# LI RE: CK2Plus AIO Stoic order power (step B, 2026-11-15; tools/phase5b_monastic.py)\n\ntargeted_decisions = {\n'
    + dec + '\n}\n')
ev = rd(os.path.join(AIO, 'events/HF_religious_events.txt'))
evs = []
for eid in ('HF.23124', 'HF.23125'):
    m = re.search(r'(?m)^\w+_event\s*=\s*\{\s*\n\s*id\s*=\s*' + re.escape(eid) + r'\b', ev)
    evs.append(ev[m.start():close(ev, ev.index('{', m.start()))])
out['events/li_CK2Plus_monastic_events.txt'] = (
    '# LI RE: notifications for the Stoic order power (CK2Plus AIO HF_religious_events; step B, 2026-11-15)\n\nnamespace = HF\n\n'
    + '\n\n'.join(evs) + '\n')
# --- gfx
z = zipfile.ZipFile(ZIP)
def zread(n): return z.read(n).decode('latin-1').replace('\r\n', '\n')
def sprites(text, pat):
    res = []
    for m in re.finditer(r'(?m)^\t(spriteType|portraitType)\s*=\s*\{', text):
        b = close(text, text.index('{', m.start())); blk = text[m.start():b]
        if re.search(pat, blk): res.append(blk)
    return res
van = rd(os.path.join(VA, 'interface/domestic_societies.gfx'))
sto_spr = sprites(van, r'name\s*=\s*"[^"]*monastic_order_stoics"')
bon_spr = sprites(zread('interface/CK2Plus_domestic_societies.gfx'), r'name\s*=\s*"[^"]*monastic_order_bon"')
bon_clo = sprites(zread('interface/CK2Plus_society_clothes.gfx'), r'monastic_order_bon')
out['interface/li_CK2Plus_monastic_orders.gfx'] = (
    '# LI RE: sprites for the Stoic (vanilla Holy Fury textures; LI\'s own domestic_societies.gfx replaces vanilla\'s and lacked them)\n'
    '# and Bon (CK2Plus AIO) monastic orders. Step B, 2026-11-15; tools/phase5b_monastic.py\n'
    'spriteTypes = {\n' + '\n'.join(sto_spr + bon_spr + bon_clo) + '\n}\n')
tex = sorted({t.replace('\\\\', '/').replace('\\', '/') for t in re.findall(r'(?i)texture[Ff]ile\s*=\s*"([^"]+)"', '\n'.join(bon_spr + bon_clo))})
names = set(z.namelist()); art = {}
for t in tex:
    hit = next((n for n in names if n.lower() == t.lower()), None)
    if hit: art[t] = hit
    elif not os.path.exists(os.path.join(REPO, t)) and not os.path.exists(os.path.join(VA, t)): print('MISSING texture', t)
for t in sorted({t.replace('\\\\', '/').replace('\\', '/') for t in re.findall(r'(?i)texture[Ff]ile\s*=\s*"([^"]+)"', '\n'.join(sto_spr))}):
    if not os.path.exists(os.path.join(VA, t)) and not os.path.exists(os.path.join(REPO, t)): print('MISSING stoic texture', t)
# --- localisation: keys used by the new files that the mod lacks
def loc(root, skip=()):
    d = {}
    for p in sorted(glob.glob(os.path.join(root, 'localisation', '**', '*.csv'), recursive=True)):
        if os.path.basename(p) in skip: continue
        for line in rd(p).split('\n'):
            k = line.split(';', 1)[0].strip()
            if k and not k.startswith('#'): d.setdefault(k, line)
    return d
mloc, aloc = loc(REPO, ('000_li_monastic_orders.csv',)), loc(AIO)
body = '\n'.join(out.values())
toks = set(re.findall(r'[\w.-]+', nc(body)))
toks |= {t + s for t in toks for s in ('_desc', '_power_desc')}
for o in ('monastic_order_bon', 'monastic_order_stoics', 'monastic_order_buddhist'):
    toks |= {k for k in aloc if k.startswith(o) or k.startswith('currency_name_' + o)}
need = sorted(k for k in toks if k in aloc and k not in mloc)
csv = ['#CODE;ENGLISH;FRENCH;GERMAN;;SPANISH;;;;;;;;;x',
       '# LI RE: text for the CK2Plus AIO monastic orders mapped onto LI faiths (step B, 2026-11-15; tools/phase5b_monastic.py)',
       'li_buddhist_monastic_tt;Follows a Buddhist faith;;;;;;;;;;;;;x'] + [aloc[k] for k in need]
out['localisation/000_li_monastic_orders.csv'] = '\n'.join(csv) + '\n'
print('sprites: stoics', len(sto_spr), 'bon', len(bon_spr), 'clothes', len(bon_clo), '| art', len(art), '| loc keys', len(need), need[:20])
for k, v in out.items(): print(f'{k}: {v.count(chr(10))} lines')
if APPLY:
    for k, v in out.items():
        p = os.path.join(REPO, k); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(v.replace('\n', '\r\n').encode('latin-1'))
    for t, n in art.items():
        p = os.path.join(REPO, t); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(z.read(n))
    print('written', len(out), 'files +', len(art), 'art files')
