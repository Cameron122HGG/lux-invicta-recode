"""Roman provincia restoration (CK2Plus AIO's CK2Plus_roman_decisions.txt) rebuilt on LI's map.
Decisions (user, 2026-11-15): usable by the Eastern/Western Roman successor and e_roman_empire; CK2Plus's 21 provincias with
Sardinia et Corsica folded into Italia (20); creating one moves its duchies de jure under the new k_provincia kingdom.
The duchy lists come from migration_notes/provincia_mapping.json (reviewed draft: migration_notes/provincia_mapping_draft.md).
usage: python -I phase5b_provincia.py <repo> <aio> <ck2plus_aio.zip> [--apply]
Writes (rerunnable; its own outputs are overwritten):
  common/landed_titles/li_CK2Plus_provincia_titles.txt   20 titular kingdoms (AIO blocks; LI capital, crusade weights)
  decisions/li_CK2Plus_roman_decisions.txt               claim Eastern/Western succession, collapse/expand, 20 create_provincia
  events/li_CK2Plus_roman_provincia_events.txt           Plus.566/569 (succession claimed), Plus.568/570/571 (yearly checks;
                                                         AIO typo in 571 fixed), LIprov.1 (start: e_byzantium = Eastern,
                                                         e_roman = Western successor), LIprov.2 (provincia restored)
  common/on_actions/li_CK2Plus_roman_on_actions.txt      on_startup LIprov.1, on_yearly_pulse 568/570/571
  map/geographical_region.txt                            custom_roman_* regions between the LI provincia markers
  localisation/000_li_roman_provincias.csv               text AIO has and the mod lacks + LI's own
  gfx/flags/k_provincia_*.tga                            from the zip"""
import os, re, sys, json, zipfile, glob
REPO, AIO, ZIP = sys.argv[1:4]
APPLY = '--apply' in sys.argv
def rd(p): return open(p, 'rb').read().decode('latin-1').replace('\r\n', '\n')
def nc(s): return re.sub(r'#[^\n]*', '', s)
def block(s, key, indent=''):
    m = re.search(r'(?m)^' + indent + re.escape(key) + r' = \{', s)
    if not m: raise SystemExit('missing ' + key)
    d = 0
    for j in range(s.index('{', m.start()), len(s)):
        if s[j] == '{': d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0: return s[m.start():j + 1]
MAP = json.load(open(os.path.join(REPO, 'migration_notes/provincia_mapping.json')))
P = sorted(MAP)
REGION = {p: 'custom_roman_' + ('brittania' if p == 'britannia' else p) for p in P}   # AIO's spelling (LoR events use it)
CAPITAL_DUCHY = {'italia': 'd_latium', 'thracia': 'd_thrace', 'phrygia': 'd_nikaea', 'pontus': 'd_paphlagonia',
                 'macedonia': 'd_thessalonika', 'mauretania': 'd_marrakech', 'syria_palaestina': 'd_jerusalem',
                 'mesopotamia': 'd_baghdad', 'viennensis': 'd_dauphine', 'aegyptus': 'd_alexandria', 'africa': 'd_tunis',
                 'illyricum': 'd_dalmatia', 'gallia': 'd_valois', 'germania': 'd_franconia', 'britannia': 'd_middlesex',
                 'hispania': 'd_castilla', 'caledonia': 'd_fiobha', 'hibernia': 'd_laigin', 'pannonia_dacia': 'd_pest',
                 'armenia': 'd_vaspurakan'}
lt = rd(os.path.join(REPO, 'common/landed_titles/landed_titles.txt'))
li_d = set(re.findall(r'(?m)^\s*(d_[\w-]+)\s*=\s*\{', nc(''.join(rd(p) for p in glob.glob(os.path.join(REPO, 'common/landed_titles/*.txt'))))))
for p, ds in MAP.items():
    bad = [d for d in ds if d not in li_d]
    if bad: raise SystemExit(f'{p}: unknown duchies {bad}')
def cut(text, pat):
    """remove every block whose opening line matches pat (through its closing brace and line end)"""
    while True:
        m = re.search(pat, text)
        if not m: return text
        a = text.rfind('\n', 0, m.start()) + 1; d = 0
        for j in range(text.index('{', m.start()), len(text)):
            if text[j] == '{': d += 1
            elif text[j] == '}':
                d -= 1
                if d == 0: break
        e = text.find('\n', j); text = text[:a] + text[(e + 1 if e >= 0 else j + 1):]
# LI province ids per duchy (regions are written as province lists: those load visibly, duchy lists log "0 province")
_par = {}; _stack = []
for mm in re.finditer(r'([\w-]+)\s*=\s*\{|\{|\}', nc(''.join(rd(p) for p in glob.glob(os.path.join(REPO, 'common/landed_titles/*.txt'))))):
    t = mm.group(0)
    if t == '}':
        if _stack: _stack.pop()
    else:
        k = mm.group(1) or ''
        if re.match(r'[ekdcb]_', k):
            _par.setdefault(k, next((x for x in reversed(_stack) if re.match(r'[ekdcb]_', x)), None))
        _stack.append(k)
_c2p = {}
for f in os.listdir(os.path.join(REPO, 'history/provinces')):
    m = re.match(r'(\d+)', f)
    if m:
        mm = re.search(r'(?m)^\s*title\s*=\s*(c_[\w-]+)', rd(os.path.join(REPO, 'history/provinces', f)))
        if mm: _c2p[mm.group(1)] = int(m.group(1))
def duchy_provinces(d): return sorted(_c2p[c] for c, p in _par.items() if p == d and c in _c2p)
def duchy_capital(d):
    m = re.search(r'(?m)^\s*' + d + r'\s*=\s*\{', lt); c = re.search(r'\bcapital\s*=\s*(\d+)', lt[m.end():m.end() + 600]); return c.group(1)
out = {}
SUCC = ('OR = {\n\t\t\t\thas_landed_title = e_roman_empire\n\n\t\t\t\tprimary_title = {\n\t\t\t\t\tOR = {\n'
        '\t\t\t\t\t\thas_title_flag = eastern_roman_successor\n\t\t\t\t\t\thas_title_flag = western_roman_successor\n'
        '\t\t\t\t\t\t# LI RE: the two Romes of 1066 count even before LIprov.1 has flagged them\n'
        '\t\t\t\t\t\tAND = {\n\t\t\t\t\t\t\tOR = { title = e_byzantium title = e_roman }\n'
        '\t\t\t\t\t\t\tholder_scope = { government = roman_imperial_government }\n\t\t\t\t\t\t}\n'
        '\t\t\t\t\t}\n\t\t\t\t}\n\t\t\t}')
# title scope: inside primary_title = { OR = { ... } } of the provincia titles' allow and gain_effect
START_TITLE = 'AND = { OR = { title = e_byzantium title = e_roman } holder_scope = { government = roman_imperial_government } } # LI RE: the two Romes of 1066'
HEAD = '# LI RE: CK2Plus AIO Roman provincia restoration on LI\'s map (2026-11-15; tools/phase5b_provincia.py). Duchy lists: migration_notes/provincia_mapping.json\n\n'
# ---- titles
tk = rd(os.path.join(AIO, 'common/landed_titles/02_CK2Plus_titular_kingdoms.txt'))
titles = []
for p in P:
    b = block(tk, 'k_provincia_' + p)
    b, n = re.subn(r'capital\s*=\s*\d+[^\n]*', f'capital = {duchy_capital(CAPITAL_DUCHY[p])} # LI RE: capital of {CAPITAL_DUCHY[p]}', b, count=1)
    assert n == 1, p + ': capital not replaced'
    # AIO's crusade weights name vanilla faiths; LI's two weights are added below
    # (any top-level "<faith> = <number>" line, with or without a comment; capital is handled above)
    b = re.sub(r'(?m)^\t(?!capital\b)\w+ = \d+[ \t]*(#[^\n]*)?\n', '', b)
    # the successors at game start count without their flag too (in case LIprov.1 has not run, e.g. an older save)
    b, n = re.subn(r'(?m)^([ \t]*)title = e_roman_empire\n', lambda m: m.group(0) + m.group(1) + START_TITLE + '\n', b)
    assert n >= 2, p + ': successor checks not found'
    # LI (user, 2026-11-15): the provincia holding the emperor's capital is not hidden - drop CK2Plus's NOT_ROMAN_CAPITAL
    # check and the gain_effect that destroyed the title when the top liege's capital lies inside it
    b = cut(b, r'custom_tooltip = \{\s*text = NOT_ROMAN_CAPITAL')
    b = cut(b, r'(?m)^\tgain_effect = \{')
    assert 'NOT_ROMAN_CAPITAL' not in b and 'gain_effect' not in b, p
    b = b.replace('\tdynasty_title_names = no\n', '\tdynasty_title_names = no\n\n\tchristian = 1000 # Crusade target weight\n\tgraecoroman_group = 1000 # LI RE: was roman/hellenic/promethean pagans\n', 1)
    # the title's own region (AIO used vanilla world regions for Hibernia and Pannonia-Dacia, which LI lacks)
    b = re.sub(r'region = (?:custom_roman|world)_\w+', 'region = ' + REGION[p], b)
    titles.append(b)
out['common/landed_titles/li_CK2Plus_provincia_titles.txt'] = HEAD + '\n\n'.join(titles) + '\n'
# title history: start inactive (AIO's history/titles/k_provincia_*.txt; without it the titular titles count as active, so
# every create decision hid itself and the titles could be created straight from the title screen). AIO's Holy Fury
# pentarch line is left out.
for p in P:
    out[f'history/titles/k_provincia_{p}.txt'] = ('# LI RE: inactive until restored by create_provincia_' + p + ' (tools/phase5b_provincia.py)\n'
                                                 '1.1.1 = {\n\tactive = no\n}\n')
# ---- decisions
rdec = rd(os.path.join(AIO, 'decisions/CK2Plus_roman_decisions.txt'))
claims = []
for k in ('claim_eastern_roman_empire', 'claim_western_roman_empire'):
    b = block(rdec, k, '\t').replace('has_imperial_government_trigger = yes',
                                      'government = roman_imperial_government # LI RE: AIO checked CK2Plus\'s imperial governments')
    b = b.replace('has_dlc = "Legacy of Rome"', '# has_dlc = "Legacy of Rome" # LI RE: dropped (nothing here needs the DLC)')
    claims.append(b)
NAND = '\n'.join(f'\t\t\t\tis_title_active = k_provincia_{p}' for p in P)
def toggle(name, flag_line, eff):
    return (f'\t{name} = {{\n\t\tis_high_prio = yes\n\n\t\tai = no\n\n\t\tpotential = {{\n'
            f'{flag_line}\n\t\t\t{SUCC}\n\n\t\t\tNAND = {{\n{NAND}\n\t\t\t}}\n\t\t}}\n\n\t\tallow = {{\n\t\t}}\n\n\t\teffect = {{\n'
            f'\t\t\t{eff}\n\t\t}}\n\n\t\tai_will_do = {{\n\t\t\tfactor = 0\n\t\t}}\n\t}}')
dec = claims + [toggle('collapse_provincia_decisions', '\t\t\tNOT = { has_global_flag = provincia_decisions_collapsed }', 'set_global_flag = provincia_decisions_collapsed'),
                toggle('expand_provincia_decisions', '\t\t\thas_global_flag = provincia_decisions_collapsed', 'clr_global_flag = provincia_decisions_collapsed')]
for p in P:
    ds = MAP[p]; R = REGION[p]
    allow = '\n'.join(f'\t\t\tcompletely_controls = {d}' for d in ds)
    move = '\n'.join(f'\t\t\t\t{d} = {{ show_scope_change = no de_jure_liege = PREV }}' for d in ds)
    dec.append(f'''	create_provincia_{p} = {{
		is_high_prio = yes
		ai_check_interval = 12

		only_independent = yes

		potential = {{
			{SUCC}

			is_alternate_start = no # LI RE: AIO's has_dlc = "Legacy of Rome" dropped (nothing here needs the DLC)

			NOR = {{ # LI RE: AIO also hid the provincia holding the emperor's capital; LI shows it (user)
				has_global_flag = provincia_decisions_collapsed
				is_title_active = k_provincia_{p}
			}}

			any_realm_province = {{ # LI RE: AIO checked vanilla world regions; LI uses the provincia's own region
				held_under_PREV = yes

				OR = {{
					region = {R}
					any_neighbor_province = {{ region = {R} }}
				}}
			}}
		}}

		allow = {{
{allow}
			war = no
			is_not_in_regency_trigger = yes
		}}

		effect = {{
			prestige = 100

			k_provincia_{p} = {{
				show_scope_change = no

				activate_title = {{
					title = THIS
					status = yes
				}}

				de_jure_liege = ROOT
				save_event_target_as = li_new_provincia
{move}
			}}

			narrative_event = {{ id = LIprov.2 }}
		}}

		ai_will_do = {{
			factor = 1
		}}
	}}''')
out['decisions/li_CK2Plus_roman_decisions.txt'] = HEAD + 'decisions = {\n' + '\n\n'.join(dec) + '\n}\n'
# ---- events
pev = rd(os.path.join(AIO, 'events/CK2Plus_specific_realm_events.txt'))
evs = []
for eid in ('Plus.566', 'Plus.568', 'Plus.569', 'Plus.570', 'Plus.571'):
    m = re.search(r'(?m)^\w+_event = \{\s*\n\s*id = ' + re.escape(eid) + r'\b', pev); d = 0
    for j in range(pev.index('{', m.start()), len(pev)):
        if pev[j] == '{': d += 1
        elif pev[j] == '}':
            d -= 1
            if d == 0: break
    e = pev[m.start():j + 1]
    if eid == 'Plus.571':
        bug = ('\t\t\t\tprimary_title = { has_title_flag = western_roman_successor }\n\t\t\t\tNOT = { has_global_flag = east_rome_lives }')
        assert e.count(bug) == 1, 'Plus.571 typo not found'
        e = e.replace(bug, '\t\t\t\tprimary_title = { has_title_flag = western_roman_successor }\n'
                           '\t\t\t\tNOT = { has_global_flag = west_rome_lives } # LI RE: AIO checked east_rome_lives here')
    e = e.replace('picture = GFX_evt_coronation_byzantine', 'picture = GFX_evt_victory_arch_byzantine # LI RE: AIO\'s GFX_evt_coronation_byzantine does not exist')
    evs.append(e)
evs.append('''# LI RE: at game start both Romes exist in 1066 - the Eastern (e_byzantium) and Western (e_roman, S.P.Q.R.) successors
character_event = {
	id = LIprov.1

	is_triggered_only = yes # on_startup (fires for every character: global-flag guard)
	hide_window = yes

	trigger = {
		NOT = { has_global_flag = li_roman_successors_set }
	}

	immediate = {
		set_global_flag = li_roman_successors_set
		log = "LIprov.1: marking the Roman successors (e_byzantium = Eastern, e_roman = Western)"

		e_byzantium = {
			if = {
				limit = { holder_scope = { real_tier = EMPEROR } }
				set_title_flag = eastern_roman_successor
				set_global_flag = east_rome_lives
			}
		}
		e_roman = {
			if = {
				limit = { holder_scope = { real_tier = EMPEROR } }
				set_title_flag = western_roman_successor
				set_global_flag = west_rome_lives
			}
		}
	}
}

# LI RE: a Roman province is restored (AIO used LoR.6, whose text always names Italia)
narrative_event = {
	id = LIprov.2
	title = EVTNAME_LIprov_2
	desc = EVTDESC_LIprov_2
	picture = GFX_evt_victory_arch_byzantine

	is_triggered_only = yes

	option = {
		name = EVTOPTALoR.1
	}
}''')
out['events/li_CK2Plus_roman_provincia_events.txt'] = HEAD + 'namespace = Plus\nnamespace = LIprov\n\n' + '\n\n'.join(evs) + '\n'
out['common/on_actions/li_CK2Plus_roman_on_actions.txt'] = HEAD + '''on_startup = {
	events = {
		LIprov.1 # Mark e_byzantium / e_roman as the Eastern / Western Roman successors
	}
}

on_yearly_pulse = {
	events = {
		Plus.568 # Eastern successor gone: clear east_rome_lives
		Plus.570 # Western successor gone: clear west_rome_lives
		Plus.571 # Successor exists but its flag is missing: restore it
	}
}
'''
# ---- regions (between markers in LI's geographical_region.txt)
MS, ME = '# LI RE: Roman provincia regions (tools/phase5b_provincia.py) - begin', '# LI RE: Roman provincia regions - end'
reg = [MS]
for p in P:
    ids = sorted({i for d in MAP[p] for i in duchy_provinces(d)})
    if not ids: raise SystemExit(p + ': no provinces')
    reg.append(f'{REGION[p]} = {{ # ' + ' '.join(MAP[p]) + '\n\tprovinces = {\n\t\t' + ' '.join(map(str, ids)) + '\n\t}\n}')
reg.append('custom_roman_provinces = {\n\tregions = {\n' + '\n'.join(f'\t\t{REGION[p]}' for p in P) + '\n\t}\n}')
reg.append(ME)
gr_path = os.path.join(REPO, 'map/geographical_region.txt'); gr = rd(gr_path)
if MS in gr: gr = gr[:gr.index(MS)].rstrip('\n') + '\n' + gr[gr.index(ME) + len(ME):].lstrip('\n')
dup = [r for r in REGION.values() if re.search(r'(?m)^' + r + r'\s*=', gr)]
if dup: raise SystemExit(f'region names already in LI geographical_region.txt: {dup}')
gr = gr.rstrip('\n') + '\n\n' + '\n\n'.join(reg) + '\n'
# ---- localisation
def loc(root, skip=()):
    d = {}
    for p in sorted(glob.glob(os.path.join(root, 'localisation', '**', '*.csv'), recursive=True)):
        if os.path.basename(p) in skip: continue
        for line in rd(p).split('\n'):
            k = line.split(';', 1)[0].strip()
            if k and not k.startswith('#'): d.setdefault(k, line)
    return d
mloc, aloc = loc(REPO, ('000_li_roman_provincias.csv',)), loc(AIO)
toks = set(re.findall(r'[\w.-]+', nc('\n'.join(out.values()))))
toks |= {t + s for t in toks for s in ('_desc', '_adj')} | {'EVTNAME_Plus_566', 'EVTDESC_Plus_566', 'EVTOPTA_Plus_566', 'EVTNAME_Plus_569', 'EVTDESC_Plus_569'}
need = sorted(k for k in toks if k in aloc and k not in mloc)
csv = ['#CODE;ENGLISH;FRENCH;GERMAN;;SPANISH;;;;;;;;;x',
       '# LI RE: Roman provincia restoration (tools/phase5b_provincia.py, 2026-11-15)',
       'EVTNAME_LIprov_2;A Roman Province Restored;;;;;;;;;;;;;x',
       'EVTDESC_LIprov_2;For the first time in centuries, the old Roman province of [li_new_provincia.GetBaseName] is whole again under the rule of [Root.GetTitledName]. Its lands answer once more to the Empire, as they did in the days of the Caesars.;;;;;;;;;;;;;x'] \
      + [aloc[k] for k in need]
out['localisation/000_li_roman_provincias.csv'] = '\n'.join(csv) + '\n'
# ---- flags
z = zipfile.ZipFile(ZIP); names = {n.lower(): n for n in z.namelist()}
flags = {f'gfx/flags/k_provincia_{p}.tga': names.get(f'gfx/flags/k_provincia_{p}.tga') for p in P}
print('provincias', len(P), 'duchies', sum(len(v) for v in MAP.values()), '| loc keys from AIO', len(need), '| flags', sum(1 for v in flags.values() if v))
missing_flags = [k for k, v in flags.items() if not v]
if missing_flags: print('MISSING flags', missing_flags)
for k, v in out.items(): print(f'{k}: {v.count(chr(10))} lines')
if APPLY:
    for k, v in out.items():
        open(os.path.join(REPO, k), 'wb').write(v.replace('\n', '\r\n').encode('latin-1'))
    raw = open(gr_path, 'rb').read(); nl = '\r\n' if b'\r\n' in raw else '\n'
    open(gr_path, 'wb').write(gr.replace('\n', nl).encode('latin-1'))
    for k, v in flags.items():
        if v: open(os.path.join(REPO, k), 'wb').write(z.read(v))
    print('written')
