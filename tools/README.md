# Lux Invicta maintenance tools

Python 3 scripts written during the 2026-11-14 cleanup and for the CleanSlate migration
(see `../CLEANSLATE_PLAN.md`). CK2 ignores this folder.

Run them with `python -I`, which keeps them isolated from whatever folder they read, and pass full
paths. Scripts that change files only do so with `--apply`. Without it they print a dry run. Always
read the dry run first and commit (or keep a backup) before applying. The scripts keep each file's
encoding (Windows-1252 / raw bytes) and line endings.

Typical paths:
- mod: `.../Crusader Kings II/mod/lux-invicta-recode`
- vanilla: `C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings II`
- CleanSlate: the extracted `CleanSlate` folder (the one with `common/`, `events/`, …)

## Surveys (read only)

| Script | What it does |
|---|---|
| `def_survey.py` | Compares every LI definition (event, decision, scripted effect/trigger, modifier, CB, trait…) with vanilla 3.3.3 and CleanSlate: new in LI, unchanged, or changed. Drives phases 2–3 of the plan. |
| `merge_survey.py` | File-level 3-way merge survey (vanilla / LI / CleanSlate) with `git merge-file`. |
| `dlc_sort.py` | Sorts an `error.log` by DLC and source file. |
| `textures.py` | For each "inexistent texture" in `error.log`, looks for the file under another folder, name or extension, or in vanilla. |
| `successors.py` | Classifies "Missing scripted successor" lines in `historical_setup_errors.log`. Vanilla alone logs 7,367 of these, so they are engine noise. |
| `gr_deps.py` | Collects vanilla game-rule events and the events they call, and checks dependencies. |

## Fixers (dry run by default; `--apply` to write)

| Script | What it does |
|---|---|
| `trim_dead.py` | Copies or rewrites a script file with checks for cultures, religions, dynasties, titles, traits, artifacts and claims that don't exist removed, **without changing behaviour**. It folds the logic: dead entries leave `OR`/`NOR` lists, always-true `NOT`s go, and only blocks that can never match are dropped. `--scopes` treats scope blocks (`primary_title = {…}`) as "all of". It refuses to remove a line that also holds a check it keeps. |
| `hf_off.py` | Switches off calls to Holy Fury events LI doesn't ship. One-line calls are commented out with a note, and `random_list` options become `N = { } # was: …` so odds are unchanged. |
| `hf_off_onactions.py` | The same for `on_actions` lists. Weighted `random_events` entries become `N = 0 # was: …`. |
| `ids_off.py` | The same for any list of event IDs, with your own note: `ids_off.py <mod> "<note>" ID …` (applies directly). |
| `copy_events.py` | Copies vanilla event definitions into an LI event file after checking the events, scripted effects/triggers and modifiers they need. |
| `restore_scripted.py` | Restores vanilla scripted triggers/effects that CleanSlate removed but LI text still calls (read from the "Unknown effect-type/trigger-type" lines in `error.log`), with what they call and CleanSlate's renames, into `common/scripted_*/000_li_restored_*.txt`: `restore_scripted.py <repo> <master export> <error.log> [--apply]`. |
| `fix_buildings.py` | Adds missing building prerequisites in province history, and converts buildings of the wrong holding type (castle/city/temple). Reads the holdings from `error.log`. |

## Things learned the hard way

- **Encoding:** CK2 files are Windows-1252. VS Code once saved a history file as UTF-8 and turned
  107 accented characters into `�`. After editing, check changed files for the bytes `EF BF BD`.
- **`coats_of_arms.txt`** has the "WHEN ADDING NEW, ALWAYS ADD AT THE END" comment twice. Texture
  entries must sit inside a `textures = { }` list, or the game crashes on the loading screen.
- **An event definition** is a top-level `xxx_event = { id = … }`. A plain `id = …` match also
  catches calls, and that once hid 30 broken calls.
- **`trigger_if` is not "all of":** a `trigger_if` whose limit can never hold *passes*. Treating it
  as false and removing it from an `OR` once changed behaviour (fixed and audited 2026-11-14).
- **Weighted lists:** never comment out a weighted entry. Keep the weight and empty the entry,
  otherwise the odds of everything else in the list change.
