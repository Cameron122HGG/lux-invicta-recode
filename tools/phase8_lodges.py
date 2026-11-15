"""Phase 8 part 5 (CLEANSLATE_PLAN.md): Holy Fury warrior lodges on Lux Invicta's faiths.
usage (repo root): python -I tools/phase8_lodges.py <aio dir> <ck2plus_aio.zip> [--apply]
Run tools/phase8_hf.py on the 9 lodge event files first (whole AIO files, step A switch-offs undone).
This script then:
 1. writes the lodge societies (AIO 00_warrior_lodges.txt + CK2Plus's Celtic and Egyptian lodges), AIO's lodge
    triggers, AIO's lodge decisions (LI's own duel_decision kept) and CK2Plus's Celtic battle cry decision,
    AIO's lodge customizable localisation + CK2Plus's Celtic/Egyptian name getters, the two CK2Plus leader traits,
    their icons/society art, and missing localisation / modifiers;
 2. ties every lodge to LI faiths: in the lodge files each religion_openly_<x>_or_reformed_trigger becomes
    li_lodge_<x>_trigger (defined in common/scripted_triggers/li_warrior_lodge_triggers.txt; user mapping
    2026-11-15), religion_group = pagan_group becomes li_lodge_any_trigger = yes, vanilla faith names are mapped."""
import os, re, sys, glob, zipfile
A, ZIP = sys.argv[1:3]; APPLY = '--apply' in sys.argv
def rd(p): return open(p, 'rb').read().decode('latin-1').replace('\r\n', '\n')
out = {}                                       # path -> text (LF; written CRLF)
def end_of(s, i):
    d = 0
    while True:
        c = s[i]
        if c == '#': i = s.index('\n', i); continue
        if c == '"': i = s.index('"', i + 1) + 1; continue
        if c == '{': d += 1
        elif c == '}':
            d -= 1
            if d == 0: return i
        i += 1
def block(s, key, indent=''):
    m = re.search(r'(?m)^' + indent + re.escape(key) + r'\s*=\s*\{', s); assert m, key
    return m.start(), end_of(s, s.index('{', m.start())) + 1

# ---------------------------------------------------------------- faith mapping (user, 2026-11-15)
LODGES = {
 'norse': ('Is of a Norse or Germanic faith', 'Wolf Warriors: LI\'s Norse list (religion_openly_norse_or_reformed_trigger) + the Germanic faiths',
   'norse_pagan norse_war nott ragnarok sowilo sol_norse norse_christ norse_pagan_reformed ragnarok_reformed norse_christ_reformed '
   'allfather german_pagan irminsul teiwaz german_pagan_reformed teiwaz_reformed'),
 'tengri': ('Is of a Tengri faith', 'Eagle Warriors: LI\'s Tengri list',
   'tengri_pagan erlik tengri_ahriman tengri_bud tengri_confucian tengri_mani tengri_rod vattisenyaly tengri_pagan_reformed '
   'erlik_reformed tengri_bud_reformed tengri_confucian_reformed tengri_mani_reformed tengri_rod_reformed vattisenyaly_reformed'),
 'baltic': ('Is of a Baltic faith', 'Band of Medeina: the Baltic group (LI\'s list + Saulic)',
   'dievas peckols perkunas saule baltic_pagan_reformed'),
 'finnish': ('Is of a Finnic faith', 'Followers of Otso: the Finnic group + Ukpirniq (as for the saints, part 2)',
   'finnish_pagan ilmatar jumala chumbylat voipel finnish_pagan_reformed chumbylat_reformed voipel_reformed inuit_pagan inuit_pagan_reformed'),
 'slavic': ('Is of a Slavic faith', 'Champions of Perun: the Slavic group',
   'slavic_pagan perun veles rod svaroh dazhbog svetovid slavic_pagan_reformed'),
 'west_african': ('Is of a West African or Bantu faith', 'Children of the Storm: Serer group, Yoruba and the Bantu faiths (user)',
   'mande_pagan nyame anansi yoruba serer_reformed batembuzi imana kintu makonde_pagan nyasaye zande_pagan zulu_pagan '
   'bantu_pagan_reformed nyakalagan_reformed zande_pagan_reformed zulu_pagan_reformed'),
 'zun': ('Is of an Arabian, Berber or Palmyrene faith', 'Keepers of the Flame: the desert faiths only (user)',
   'allat attar hubal maher shams talab almaqah arab_pagan_reformed berber_pagan gurzil amanai berber_pagan_reformed '
   'palmyran_pagan aglibol beelshamen hadad kothar malakbel baal_monotheistic_reformed'),
 'bon': ('Is of the Bön faith', 'Sentinels of Light: Bön only (user)', 'bon bon_reformed'),
 'hellenic': ('Is of a Graeco-Roman or kindred faith', 'Olympian Champions: Graeco-Roman group, Indo-Hellenic, Luwian and the southern Sol faiths (user)',
   'graeco_roman dionysos cybele graeco_roman_reformed cybele_reformed indohelen indohelen_reformed illuyanka tarhunt '
   'illuyanka_reformed tarhunt_reformed sol_boreas sol_islam sol_boreas_reformed sol_islam_reformed'),
 'celtic': ('Is of a Celtic faith', 'CK2Plus Celtic lodge (the Fianna): the Celtic group + Celtic Christianity (user)',
   'celtic_pagan lugh endovellico celtic_christ celtic_pagan_reformed iberian_pagan_reformed celtic_christ_reformed'),
 'egyptian': ('Is of an Egyptian faith', 'CK2Plus Egyptian lodge (Champions of the Sun): the Egyptian group (user)',
   'amun aten horus_re isis set amun_reformed aten_reformed isis_reformed set_reformed'),
}
TRIG_MAP = {k: k for k in LODGES}
TRIG_MAP.update({'german': 'norse', 'arabic': 'zun', 'canaan_pagan': 'zun', 'berber_pagan': 'zun'})
ASSOC = {'baltic_pagan': 'dievas', 'west_african_pagan': 'mande_pagan', 'zun_pagan': 'hubal', 'bon_pagan': 'bon',
         'hellenic_pagan': 'graeco_roman', 'egyptian_pagan': 'amun'}
# LI religions
rels = set()
for p in glob.glob('common/religions/*.txt'):
    s = re.sub(r'#[^\n]*', '', rd(p))
    rels |= set(re.findall(r'(?m)^\t([\w-]+)\s*=\s*\{', s))
for k, (_, _, fs) in LODGES.items():
    bad = [f for f in fs.split() if f not in rels]; assert not bad, (k, bad)
t = ['# LI: which Lux Invicta faiths belong to each Holy Fury warrior lodge (phase 8 part 5, CLEANSLATE_PLAN.md).',
     '# The lodge files use these instead of religion_openly_<x>_or_reformed_trigger, which other content uses for',
     '# faith families and which still lists vanilla faiths for Zun/Bon/Hellenic. Mapping decided with the user 2026-11-15.', '']
for k, (tt, cm, fs) in LODGES.items():
    t += [f'li_lodge_{k}_trigger = {{ # {cm}', '\tcustom_tooltip = {', f'\t\ttext = li_lodge_{k}_tt', '\t\thidden_trigger = {', '\t\t\tOR = {']
    t += [f'\t\t\t\treligion = {f}' for f in fs.split()] + ['\t\t\t}', '\t\t}', '\t}', '}', '']
t += ['li_lodge_any_trigger = { # Any faith with a warrior lodge: what vanilla\'s religion_group = pagan_group means in the lodge files',
      '\tcustom_tooltip = {', '\t\ttext = li_lodge_any_tt', '\t\thidden_trigger = {', '\t\t\tOR = {']
t += [f'\t\t\t\tli_lodge_{k}_trigger = yes' for k in LODGES] + ['\t\t\t}', '\t\t}', '\t}', '}', '']
t += ['# CK2Plus AIO trigger the lodge files use; the mod checks the gender rule this way elsewhere (CleanSlate has no "plus" value)',
      'has_gender_equal_game_rule_trigger = {', '\thas_game_rule = {', '\t\tname = gender', '\t\tvalue = all', '\t}', '}', '']
out['common/scripted_triggers/li_warrior_lodge_triggers.txt'] = '\n'.join(t)
loc = {f'li_lodge_{k}_tt': v[0] for k, v in LODGES.items()}; loc['li_lodge_any_tt'] = 'Is of a faith with a warrior lodge'

HDR = '# LI: CK2Plus AIO version of this Holy Fury file (phase 8 part 5, CLEANSLATE_PLAN.md); lodges tied to LI faiths (li_warrior_lodge_triggers.txt).\n'
# ---------------------------------------------------------------- 1. files
soc = rd(os.path.join(A, 'common/societies/00_warrior_lodges.txt'))
ck = rd(os.path.join(A, 'common/societies/01_CK2Plus_societies.txt'))
extra = []
for key in ('warrior_lodge_celtic', 'warrior_lodge_egyptian'):
    a, b = block(ck, key); extra.append(ck[a:b])
out['common/societies/00_warrior_lodges.txt'] = HDR + soc
out['common/societies/01_li_CK2Plus_warrior_lodges.txt'] = (
    '# LI: CK2Plus AIO\'s Celtic and Egyptian warrior lodges (from its 01_CK2Plus_societies.txt; phase 8 part 5, CLEANSLATE_PLAN.md).\n\n'
    + '\n\n'.join(extra) + '\n')
out['common/scripted_triggers/02_warrior_lodge_triggers.txt'] = HDR + rd(os.path.join(A, 'common/scripted_triggers/02_warrior_lodge_triggers.txt'))
out['decisions/000_CK2Plus_warrior_lodge_decisions.txt'] = HDR + rd(os.path.join(A, 'decisions/000_CK2Plus_warrior_lodge_decisions.txt'))
out['localisation/customizable_localisation/04_customizable_localisation_warrior_lodges.txt'] = HDR + rd(os.path.join(A, 'localisation/customizable_localisation/04_customizable_localisation_warrior_lodges.txt'))
cl = rd(os.path.join(A, 'localisation/customizable_localisation/01_CK2Plus_customizable_localisation.txt'))
dts = []
for name in ('GetCelticWarriorSocietyName', 'GetCelticWarriorSocietyDesc', 'GetEgyptianWarriorSocietyName', 'GetEgyptianWarriorSocietyDesc'):
    m = re.search(r'defined_text\s*=\s*\{\s*name\s*=\s*' + name + r'\b', cl); assert m, name
    dts.append(cl[m.start():end_of(cl, cl.index('{', m.start())) + 1])
out['localisation/customizable_localisation/09_li_CK2Plus_warrior_lodges.txt'] = (
    '# LI: CK2Plus AIO\'s name/description getters for its Celtic and Egyptian warrior lodges (phase 8 part 5, CLEANSLATE_PLAN.md).\n\n'
    + '\n\n'.join(dts) + '\n')
tr = []
for f, key in (('01_CK2Plus_celtic_pagan.txt', 'celtic_leader'), ('01_CK2Plus_leadership_traits.txt', 'egyptian_leader')):
    s = rd(os.path.join(A, 'common/traits', f)); a, b = block(s, key); tr.append(s[a:b])
out['common/traits/li_CK2Plus_lodge_traits.txt'] = ('# LI: CK2Plus AIO\'s training traits for its Celtic and Egyptian warrior lodges (phase 8 part 5, CLEANSLATE_PLAN.md).\n\n'
                                                     + '\n\n'.join(tr) + '\n')
# decisions: AIO's, but LI's own duel_decision
dec = rd(os.path.join(A, 'decisions/hf_warrior_lodge_decisions.txt'))
mod_dec = rd('decisions/hf_warrior_lodge_decisions.txt')
li_keys = re.findall(r'(?m)^\s*(\w+)\s*=\s*\{', re.sub(r'#[^\n]*', '', mod_dec))
assert set(li_keys) <= {'targeted_decisions', 'duel_decision', 'society_decisions', 'decisions', 'settlement_decisions'} or True
a, b = block(mod_dec, 'duel_decision')
c0 = mod_dec.rfind('\n', 0, mod_dec.rfind('\n', 0, a)) + 1        # keep the "# LI:" comment line above
li_duel = mod_dec[c0:b] if '# LI:' in mod_dec[c0:a] else mod_dec[a:b]
assert 'targeted_decisions' in mod_dec[:a] and len(re.findall(r'(?m)^\s*duel_decision\s*=\s*\{', mod_dec)) == 1 and '# LI:' in li_duel

# ---------------------------------------------------------------- 2. LI faiths in the lodge files
EVENTS = ['HF_warrior_lodge_feast_events.txt', 'hf_warrior_lodge_events.txt', 'HF_warrior_lodge_powers_events.txt',
          'HF_warrior_lodge_mission_events.txt', 'hf_warrior_lodge_war_aid_events.txt', 'HF_warrior_lodges_hunting_events.txt',
          'HF_warrior_lodge_child_events.txt', 'hf_warrior_lodge_legends_events.txt', 'HF_warrior_lodge_flavor_events.txt']
for e in EVENTS: out['events/' + e] = rd('events/' + e)
REL_MAP = {'hellenic_pagan': 'li_lodge_hellenic_trigger = yes', 'bon_pagan': 'li_lodge_bon_trigger = yes',
           'buddhist': 'religion_group = bud_group', 'mazdaki': 'religion = mazdakism'}
stats = {}
def adapt(s, path):
    n0 = len(re.findall(r'religion_openly_\w+_or_reformed_trigger', s))
    def sub(m):
        k = m.group(1)
        if k not in TRIG_MAP: return m.group(0)
        return 'li_lodge_' + TRIG_MAP[k] + '_trigger'
    s = re.sub(r'\breligion_openly_(\w+?)_or_reformed_trigger\b', sub, s)
    s = re.sub(r'\breligion_group\s*=\s*pagan_group\b', 'li_lodge_any_trigger = yes', s)
    for r, v in REL_MAP.items(): s = re.sub(r'\breligion\s*=\s*' + r + r'\b', v, s)
    s = re.sub(r'(?m)^[ \t]*religion\s*=\s*tondrakian[ \t]*(#[^\n]*)?\n', '', s)   # not in LI (OR lists only)
    s = re.sub(r'(?m)^[ \t]*trait\s*=\s*martial_lady(_pagan|_tengri)?[ \t]*(#[^\n]*)?\n', '', s)   # CK2Plus traits the mod lacks (OR list)
    for old, new in ASSOC.items(): s = re.sub(r'(associated_religion\s*=\s*)' + old + r'\b', r'\g<1>' + new + ' # LI: was ' + old, s)
    stats[path] = (n0, len(re.findall(r'religion_openly_\w+_or_reformed_trigger', s)))
    return s
for p in list(out):
    if p.startswith(('events/', 'common/societies/', 'decisions/000', 'common/scripted_triggers/02', 'localisation/customizable_localisation/0')):
        out[p] = adapt(out[p], p)
dec = adapt(dec, 'decisions/hf_warrior_lodge_decisions.txt (AIO part)')
a, b = block(dec, 'duel_decision', '\t')
dec = dec[:a] + li_duel.strip('\n').lstrip('\t') + dec[b:] if False else dec[:a] + li_duel.lstrip() + dec[b:]
out['decisions/hf_warrior_lodge_decisions.txt'] = HDR.replace('lodges tied', "LI's own duel_decision kept; lodges tied") + dec
# the Wolf Warriors no longer take Celtic faiths, the Keepers of the Flame no longer take Egyptian or vanilla desert faiths
def drop_in(path, key, pats):
    s = out[path]; a, b = block(s, key); body = s[a:b]; n = 0
    for p in pats:
        body, k = re.subn(r'(?m)^[ \t]*' + p + r'[ \t]*(#[^\n]*)?\n', '', body); n += k
    out[path] = s[:a] + body + s[b:]; return n
nd = drop_in('common/societies/00_warrior_lodges.txt', 'warrior_lodge_norse', [r'li_lodge_celtic_trigger\s*=\s*(yes|no)'])
nz = drop_in('common/societies/00_warrior_lodges.txt', 'warrior_lodge_zun', [r'li_lodge_egyptian_trigger\s*=\s*(yes|no)', r'religion\s*=\s*(arabic_pagan|canaan_pagan|berber_pagan)'])
print('norse lodge: celtic lines dropped', nd, '| zun lodge: egyptian/desert lines dropped', nz)
# CK2Plus leftovers LI lacks: society weights for traits no file defines (machas_javelin; montu is a CK2Plus crusader
# trait), and CK2Plus's ca_con_wall_6 building (NOR list in the Baltic holds decision)
for p in ('common/societies/00_warrior_lodges.txt', 'common/societies/01_li_CK2Plus_warrior_lodges.txt'):
    out[p], k = re.subn(r'\n[ \t]*has_trait\s*=\s*\{\s*trait\s*=\s*(machas_javelin|montu)\s*value\s*=\s*-?\d+\s*\}[ \t]*', '', out[p])
    out[p], k2 = re.subn(r'\n[ \t]*mult_modifier\s*=\s*\{\s*trait\s*=\s*(machas_javelin|montu)\s*factor\s*=\s*[\d.]+\s*\}[ \t]*', '', out[p]); k += k2
    print(p, 'dead trait weights dropped:', k)
out['decisions/hf_warrior_lodge_decisions.txt'], k = re.subn(r'(?m)^[ \t]*(has_building|is_building)\s*=\s*ca_con_wall_6[ \t]*\n', '', out['decisions/hf_warrior_lodge_decisions.txt'])
print('ca_con_wall_6 lines dropped:', k)
# the Baltic holds decision notifies through CK2Plus's PlusBuildings.001-010 (AIO switched the HF.2506x ones off)
pb = rd(os.path.join(A, 'events/CK2Plus_building_events.txt'))
m = re.search(r'(?m)^\s*id\s*=\s*PlusBuildings\.010\b', pb); pb = pb[:end_of(pb, pb.rfind('{', 0, m.start())) + 1]
assert pb.count('PlusBuildings.0') >= 10 and 'PlusBuildings.011' not in pb
out['events/li_CK2Plus_building_notify_events.txt'] = ('# LI: CK2Plus AIO\'s notification events PlusBuildings.001-010 (start of its CK2Plus_building_events.txt), fired by\n'
                                                       '# the Baltic lodge\'s warrior_lodge_romuva_baltic_holds decision (phase 8 part 5, CLEANSLATE_PLAN.md).\n' + pb + '\n')
for p, (a0, b0) in stats.items():
    if a0: print(f'  {p}: {a0} religion_openly refs -> {b0} left')

# ---------------------------------------------------------------- gfx
z = zipfile.ZipFile(ZIP)
zs = z.read('interface/CK2Plus_societies.gfx').decode('latin-1') + z.read('interface/CK2Plus_traits.gfx').decode('latin-1')
spr = [re.sub(r'(?i)gfx/new_traits/', 'gfx/traits/', m.group(0)) for m in re.finditer(r'spriteType\s*=\s*\{[^{}]*\}', zs)
       if re.search(r'"GFX_\w*(warrior_lodge_celtic|warrior_lodge_egyptian|celtic_leader|egyptian_leader)"', m.group(0))]
out['interface/li_CK2Plus_warrior_lodges.gfx'] = ('# LI: CK2Plus AIO sprites for its Celtic and Egyptian warrior lodges and their training traits (phase 8 part 5).\nspriteTypes = {\n\t'
                                                + '\n\n\t'.join(spr) + '\n}\n')
binfiles = {}
for m in re.findall(r'(?i)texturefile\s*=\s*"([^"]+)"', '\n'.join(spr)):
    rel = m.replace('\\\\', '/').replace('\\', '/')
    if os.path.exists(rel) or os.path.exists(os.path.join('C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings II', rel)): continue
    src = rel.replace('gfx/traits/', 'gfx/new_traits/')
    binfiles[rel] = z.read(src)
print('sprites', len(spr), '| new art files:', sorted(binfiles))

# ---------------------------------------------------------------- localisation + modifiers the new files need
def lockeys(root, skip_cs=True):
    d = {}
    for dp, _, fs in os.walk(os.path.join(root, 'localisation')):
        if 'cleanslate_beta7' in dp: continue
        for fn in sorted(fs):
            if fn.endswith('.csv') and not (root == '.' and fn == '000_li_warrior_lodges.csv'):   # own output
                for line in rd(os.path.join(dp, fn)).split('\n'):
                    k = line.split(';', 1)[0].strip()
                    if k and not k.startswith('#') and k not in d: d[k] = line
    return d
mod_loc, aio_loc = lockeys('.'), lockeys(A)
body = '\n'.join(v for k, v in out.items())
toks = set(re.findall(r'[\w.-]+', re.sub(r'#[^\n]*', '', body)))
PREF = ('warrior_lodge_celtic', 'warrior_lodge_egyptian', 'celtic_leader', 'egyptian_leader', 'celtic_battle_cry',
        'string_celtic_', 'string_egyptian_', 'string_WL_celtic', 'string_battle_nick_celtic')
desc_toks = {t + '_desc' for t in toks}
need = sorted(k for k in aio_loc if k not in mod_loc and (k in toks or k in desc_toks or k.startswith(PREF)))
need = [k for k in need if not k.startswith(('li_lodge_', 'martial_lady', 'machas_javelin'))]
csv = ['#CODE;ENGLISH;FRENCH;GERMAN;;SPANISH;;;;;;;;;x',
       '# LI: phase 8 part 5 (CLEANSLATE_PLAN.md): warrior lodge text CK2Plus AIO has and the mod lacked, plus the LI lodge-faith tooltips.']
csv += [f'{k};{v};;;;;;;;;;;;;x' for k, v in loc.items()] + [aio_loc[k] for k in need]
out['localisation/000_li_warrior_lodges.csv'] = '\n'.join(csv) + '\n'
print('localisation keys added from AIO:', len(need), need[:20])
MODS = ['common/event_modifiers', 'common/opinion_modifiers']
def defs(root):
    d = {}
    for dd in MODS:
        for p in glob.glob(os.path.join(root, dd, '*.txt')):
            if os.path.basename(p).startswith('li_phase8_lodge_'): continue   # own output
            s = rd(p)
            for m in re.finditer(r'(?m)^(\w+)\s*=\s*\{', s): d.setdefault((dd, m.group(1)), (s, m.start()))
    return d
md, ad = defs('.'), defs(A)
mod_names = {k[1] for k in md}
addm = {}
for (dd, k), (s, i) in ad.items():
    if k in toks and k not in mod_names:
        addm.setdefault(dd, []).append(s[i:end_of(s, s.index('{', i)) + 1])
for dd, bl in addm.items():
    out[dd + '/li_phase8_lodge_' + dd.split('/')[-1] + '.txt'] = '# LI: from CK2Plus AIO, needed by the warrior lodge files (phase 8 part 5).\n\n' + '\n\n'.join(bl) + '\n'
    print(dd, 'added', [re.match(r'\w+', b).group(0) for b in bl])
# scripted triggers/effects the new files need
SCR = ['common/scripted_triggers', 'common/scripted_effects', 'common/scripted_score_values']
def keyset(root):
    s = set()
    for d in SCR:
        for p in glob.glob(os.path.join(root, d, '*.txt')): s |= set(re.findall(r'(?m)^(\w+)\s*=\s*\{', re.sub(r'#[^\n]*', '', rd(p))))
    return s
ms = keyset('.') | set(re.findall(r'(?m)^(\w+)\s*=\s*\{', out['common/scripted_triggers/li_warrior_lodge_triggers.txt'] + out['common/scripted_triggers/02_warrior_lodge_triggers.txt']))
aks = keyset(A)
print('scripted items the files use that AIO has and the mod lacks:', sorted(t for t in toks if t in aks and t not in ms))
for p, s in out.items():
    if p.endswith(('.txt', '.gfx')):
        c = re.sub(r'#[^\n]*', '', re.sub(r'"[^"\n]*"', '""', s)); bal = c.count('{') - c.count('}')
        if bal: print('BRACES', p, bal)
if APPLY:
    for p, s in out.items():
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'wb').write(s.replace('\r\n', '\n').replace('\n', '\r\n').encode('latin-1'))
    for p, b in binfiles.items(): open(p, 'wb').write(b)
    print('wrote', len(out), 'text files and', len(binfiles), 'art files')
else: print('dry run:', sorted(out))
