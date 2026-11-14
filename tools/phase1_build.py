"""Phase 1 of CLEANSLATE_PLAN.md: CleanSlate's scripts + LI's world data.
usage: python -I phase1_build.py <repo_dir> [--apply]
Dry run by default: prints what would be copied from cleanslate_beta7/ and which LI files would be
removed from the working tree (they stay in git on master and come back in phases 2-3)."""
import os, sys, shutil
from collections import Counter
REPO = sys.argv[1]; APPLY = '--apply' in sys.argv
REF = os.path.join(REPO, 'cleanslate_beta7')

# LI's world data: kept as LI has it, CleanSlate's version of these is not used
WORLD = ['map', 'history', 'gfx', 'music', 'sound', 'interface',
         'common/landed_titles', 'common/cultures', 'common/religions', 'common/dynasties',
         'common/graphicalculturetypes', 'common/bookmarks', 'common/defines', 'common/defines.txt',
         'localisation']            # LI's loc stays; CleanSlate's loc is added alongside (phase 6 sorts conflicts)
# CleanSlate script folders that replace LI's
SCRIPT = ['common', 'decisions', 'events', 'dlc_metadata', 'tutorial']
SKIP_REPO = {'.git', '.vscode', 'tools', 'cleanslate_beta7', '.transfer your modding stuff here'}

def is_world(rel):
    return any(rel == w or rel.startswith(w + '/') for w in WORLD)
def walk(root, top):
    for dp, dn, fs in os.walk(os.path.join(root, top)):
        for f in fs:
            yield os.path.relpath(os.path.join(dp, f), root).replace(os.sep, '/')

li = set()
for top in os.listdir(REPO):
    if top in SKIP_REPO or not os.path.isdir(os.path.join(REPO, top)): continue
    li |= set(walk(REPO, top))
cs = set()
for top in SCRIPT + ['localisation', 'interface']:
    if os.path.isdir(os.path.join(REF, top)): cs |= set(walk(REF, top))

VANILLA = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
assert VANILLA, 'usage: phase1_build.py <repo_dir> <vanilla_dir> [--apply]'
remove = sorted(f for f in li if f.split('/')[0] in SCRIPT and not is_world(f))
copy = []; deferred = []; dest = {}
for f in sorted(cs):
    if not is_world(f): copy.append(f); dest[f] = f; continue
    if f.startswith('interface/'):
        # only CleanSlate's cleaned copies of vanilla interface files (they replace that vanilla file);
        # CleanSlate's reorganised splits (coa_*.txt, CleanSlate_holdings_*.gfx...) would duplicate LI's
        if f in li: continue
        if os.path.exists(os.path.join(VANILLA, f)): copy.append(f); dest[f] = f
        else: deferred.append(f)
    elif f.startswith('localisation/'):
        d, name = os.path.split(f)
        if name.endswith('.csv') and d == 'localisation':
            dest[f] = d + '/zz_cs_' + name   # loads after LI's files, so LI's text wins (phase 6 sorts keys)
        elif f in li: continue
        else: dest[f] = f
        copy.append(f)
keep = sorted(f for f in li if is_world(f))

def summary(name, files):
    c = Counter('/'.join(f.split('/')[:2]) if f.startswith('common/') else f.split('/')[0] for f in files)
    print(f'\n{name}: {len(files)} files'); [print(f'   {n:5}  {k}') for k, n in c.most_common(14)]
summary('LI script files removed from the branch working tree (kept in git/master)', remove)
summary('CleanSlate files copied in from cleanslate_beta7/', copy)
summary('LI world data kept', keep)
summary('CleanSlate interface files deferred to phase 3 (reorganised splits, not vanilla copies)', deferred)
clash = [dest[f] for f in copy if dest[f] in li and dest[f] not in remove]
print('\nCleanSlate files that would overwrite a kept LI file:', len(clash), clash[:5])
if APPLY:
    assert not clash
    for f in remove: os.remove(os.path.join(REPO, f))
    for f in copy:
        d = os.path.join(REPO, dest[f]); os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(os.path.join(REF, f), d)
    for dp, dn, fs in sorted(os.walk(REPO), reverse=True):   # drop folders left empty
        if dp.startswith(os.path.join(REPO, '.git')): continue
        if not os.listdir(dp): os.rmdir(dp)
    print('\napplied')
