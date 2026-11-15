"""Test decisions for playtesting (2026-11-15). AI never takes them; they only show after "LI test mode: on".
usage: python -I make_debug_decisions.py <repo> [--apply]
Writes decisions/zz_li_debug_decisions.txt and localisation/000_li_debug_decisions.csv. To remove the test decisions,
delete those two files. The provincia shortcuts follow migration_notes/provincia_mapping.json (same effect as the real
create_provincia decisions in decisions/li_CK2Plus_roman_decisions.txt)."""
import os, sys, json
REPO = sys.argv[1]; APPLY = '--apply' in sys.argv
MAP = json.load(open(os.path.join(REPO, 'migration_notes/provincia_mapping.json')))
P = sorted(MAP)
NAMES = {'aegyptus': 'Aegyptus', 'africa': 'Africa', 'armenia': 'Armenia', 'britannia': 'Britannia', 'caledonia': 'Caledonia',
         'gallia': 'Gallia', 'germania': 'Germania', 'hibernia': 'Hibernia', 'hispania': 'Hispania', 'illyricum': 'Illyricum',
         'italia': 'Italia', 'macedonia': 'Macedonia', 'mauretania': 'Mauretania', 'mesopotamia': 'Mesopotamia',
         'pannonia_dacia': 'Pannonia et Dacia', 'phrygia': 'Phrygia', 'pontus': 'Pontus', 'syria_palaestina': 'Syria Palaestina',
         'thracia': 'Thracia', 'viennensis': 'Viennensis'}
ON = 'has_global_flag = li_debug_mode'
def dec(key, potential, effect, allow='', name='', desc=''):
    loc.append(f'{key};DEBUG: {name};;;;;;;;;;;;;x'); loc.append(f'{key}_desc;{desc};;;;;;;;;;;;;x')
    return (f'\t{key} = {{\n\t\tai = no\n\n\t\tpotential = {{\n\t\t\tai = no\n{potential}\t\t}}\n\n\t\tallow = {{\n{allow}\t\t}}\n\n'
            f'\t\teffect = {{\n{effect}\t\t}}\n\n\t\tai_will_do = {{\n\t\t\tfactor = 0\n\t\t}}\n\t}}')
loc = ['#CODE;ENGLISH;FRENCH;GERMAN;;SPANISH;;;;;;;;;x', '# LI: test decisions (tools/make_debug_decisions.py) - delete with decisions/zz_li_debug_decisions.txt']
D = []
# ---- switches
D.append(dec('li_debug_mode_on', '\t\t\tNOT = { has_global_flag = li_debug_mode }\n', '\t\t\tset_global_flag = li_debug_mode\n',
             name='LI test mode: on', desc='Shows the LI test decisions (resources, Roman tests). They have no AI and do nothing until taken.'))
D.append(dec('li_debug_mode_off', f'\t\t\t{ON}\n', '\t\t\tclr_global_flag = li_debug_mode\n\t\t\tclr_global_flag = li_debug_provincias\n',
             name='LI test mode: off', desc='Hides the LI test decisions again.'))
# ---- resources
D.append(dec('li_debug_resources', f'\t\t\t{ON}\n', '\t\t\twealth = 1000\n\t\t\tprestige = 1000\n\t\t\tpiety = 1000\n',
             name='+1000 gold, prestige and piety', desc='Enough to afford titles, claims and decisions.'))
# ---- Roman status (allow lists every condition, so its tooltip shows the state; it can't be taken)
status = ('\t\t\tcustom_tooltip = { text = li_debug_tt_east_lives has_global_flag = east_rome_lives }\n'
          '\t\t\tcustom_tooltip = { text = li_debug_tt_west_lives has_global_flag = west_rome_lives }\n'
          '\t\t\tcustom_tooltip = { text = li_debug_tt_restored has_global_flag = rome_restored }\n'
          '\t\t\tcustom_tooltip = { text = li_debug_tt_east_mine primary_title = { has_title_flag = eastern_roman_successor } }\n'
          '\t\t\tcustom_tooltip = { text = li_debug_tt_west_mine primary_title = { has_title_flag = western_roman_successor } }\n'
          '\t\t\tcustom_tooltip = { text = li_debug_tt_gov government = roman_imperial_government }\n'
          '\t\t\tcustom_tooltip = { text = li_debug_tt_law primary_title = { has_law = succ_byzantine_elective } }\n'
          '\t\t\tcustom_tooltip = { text = li_debug_tt_collapsed NOT = { has_global_flag = provincia_decisions_collapsed } }\n')
loc += ['li_debug_tt_east_lives;An Eastern Roman successor exists (east_rome_lives);;;;;;;;;;;;;x',
        'li_debug_tt_west_lives;A Western Roman successor exists (west_rome_lives);;;;;;;;;;;;;x',
        'li_debug_tt_restored;The Roman Empire is restored (rome_restored);;;;;;;;;;;;;x',
        'li_debug_tt_east_mine;My primary title is the Eastern successor;;;;;;;;;;;;;x',
        'li_debug_tt_west_mine;My primary title is the Western successor;;;;;;;;;;;;;x',
        'li_debug_tt_gov;I have the Roman imperial government;;;;;;;;;;;;;x',
        'li_debug_tt_law;My primary title has Imperial Elective;;;;;;;;;;;;;x',
        'li_debug_tt_collapsed;Provincia decisions are not collapsed;;;;;;;;;;;;;x']
D.append(dec('li_debug_roman_status', f'\t\t\t{ON}\n', '', allow=status + '\t\t\talways = no\n',
             name='Roman status (hover)', desc='Hover the allow list: green/red shows the Roman successor flags, government, succession law and provincia list state. Cannot be taken.'))
D.append(dec('li_debug_roman_government', f'\t\t\t{ON}\n\t\t\tNOT = {{ government = roman_imperial_government }}\n',
             '\t\t\tset_government_type = roman_imperial_government\n',
             name='Set Roman imperial government', desc='Switches you to the Roman imperial government (the game may switch you back if you do not hold a Roman empire as primary title).'))
for side, Side, other in (('eastern', 'Eastern', 'western'), ('western', 'Western', 'eastern')):
    g = 'east_rome_lives' if side == 'eastern' else 'west_rome_lives'
    D.append(dec(f'li_debug_make_{side}_successor', f'\t\t\t{ON}\n\t\t\treal_tier = EMPEROR\n',
                 f'\t\t\tprimary_title = {{\n\t\t\t\tclr_title_flag = {other}_roman_successor\n\t\t\t\tset_title_flag = {side}_roman_successor\n\t\t\t}}\n'
                 f'\t\t\tset_global_flag = {g}\n',
                 name=f'Make my empire the {Side} successor', desc=f'Flags your primary title as the {Side} Roman successor and sets {g}, without the claim decision.'))
D.append(dec('li_debug_clear_successors', f'\t\t\t{ON}\n',
             '\t\t\tany_title = {\n\t\t\t\tlimit = {\n\t\t\t\t\tOR = {\n\t\t\t\t\t\thas_title_flag = eastern_roman_successor\n'
             '\t\t\t\t\t\thas_title_flag = western_roman_successor\n\t\t\t\t\t}\n\t\t\t\t}\n'
             '\t\t\t\tclr_title_flag = eastern_roman_successor\n\t\t\t\tclr_title_flag = western_roman_successor\n\t\t\t}\n'
             '\t\t\tclr_global_flag = east_rome_lives\n\t\t\tclr_global_flag = west_rome_lives\n',
             name='Clear all Roman successors', desc='Removes both successor flags everywhere, so the claim decisions can be tested.'))
D.append(dec('li_debug_provincias_on', f'\t\t\t{ON}\n\t\t\tNOT = {{ has_global_flag = li_debug_provincias }}\n',
             '\t\t\tset_global_flag = li_debug_provincias\n',
             name='Show provincia shortcuts', desc='Lists one shortcut per provincia that restores it at once, as if its decision had passed.'))
D.append(dec('li_debug_provincias_off', f'\t\t\t{ON}\n\t\t\thas_global_flag = li_debug_provincias\n',
             '\t\t\tclr_global_flag = li_debug_provincias\n', name='Hide provincia shortcuts', desc='Hides the provincia shortcuts.'))
for p in P:
    move = ''.join(f'\t\t\t\t{d} = {{ show_scope_change = no de_jure_liege = PREV }}\n' for d in MAP[p])
    D.append(dec(f'li_debug_restore_provincia_{p}',
                 f'\t\t\t{ON}\n\t\t\thas_global_flag = li_debug_provincias\n\t\t\tNOT = {{ is_title_active = k_provincia_{p} }}\n',
                 f'\t\t\tk_provincia_{p} = {{\n\t\t\t\tactivate_title = {{ title = THIS status = yes }}\n\t\t\t\tde_jure_liege = ROOT\n'
                 f'\t\t\t\tsave_event_target_as = li_new_provincia\n{move}\t\t\t}}\n\t\t\tnarrative_event = {{ id = LIprov.2 }}\n',
                 name=f'Restore Provincia {NAMES.get(p, p)} now',
                 desc=f'Activates k_provincia_{p} and moves its {len(MAP[p])} duchies under it de jure, without the control requirements.'))
out = {'decisions/zz_li_debug_decisions.txt': '# LI: TEST DECISIONS (tools/make_debug_decisions.py). Delete this file and localisation/000_li_debug_decisions.csv to remove them.\n\ndecisions = {\n' + '\n\n'.join(D) + '\n}\n',
       'localisation/000_li_debug_decisions.csv': '\n'.join(loc) + '\n'}
for k, v in out.items(): print(k, v.count('\n'), 'lines')
print(len(D), 'decisions')
if APPLY:
    for k, v in out.items(): open(os.path.join(REPO, k), 'wb').write(v.replace('\n', '\r\n').encode('latin-1'))
    print('written')
