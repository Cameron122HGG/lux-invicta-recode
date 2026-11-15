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
| `phase5b_aio.py` | Step B (decision 5): surveys LI definitions copied from CK2Plus and swaps in AIO's current version where nothing is missing. `--keep-li=phase5b_keep_li.txt` keeps listed definitions as LI wrote them (LI changes the survey can't see). `--drop=x` also swaps rows whose only missing pieces are x, removing x from AIO's text (lines and `if`/`else_if` branches). Compare LI's master text with AIO's for every ready swap before `--apply`, and check the flags AIO's text reads (the survey doesn't see flags or chains). |
| `phase5b_monastic.py` | Step B: builds the Buddhist, Bon and Stoic monastic orders from AIO mapped onto LI faiths (societies, trigger, Stoic decision and events, sprites, text). Rerunnable. |
| `phase5b_provincia.py` | CK2Plus's Roman provincia restoration on LI's map: 20 titular `k_provincia_*` kingdoms, claim/collapse/create decisions, succession events, `custom_roman_*` regions (between markers in `map/geographical_region.txt`), text, flags. Duchy lists from `migration_notes/provincia_mapping.json`. Rerunnable. |
| `make_debug_decisions.py` | Playtest decisions (no AI; hidden until "LI test mode: on"): resources, Roman status/government/successor flags, one restore shortcut per provincia. Writes `decisions/zz_li_debug_decisions.txt` + `localisation/000_li_debug_decisions.csv`; delete both to remove them. |
| `phase5b_deps.py` | Step B: copies single AIO dependencies (scripted triggers/effects, event/opinion modifiers, nicknames, loc keys) into `li_CK2Plus_*` files (objectives/plots too) and `000_li_CK2Plus_stepb.csv`, and lists what each copied item needs in turn. Note: on Windows a `li_CK2Plus_*.txt` name can match an existing LI file in another case; it then appends to that file. |
| `phase8_hf.py` | Phase 8: replaces whole events/ files with CK2Plus AIO's Holy Fury versions, undoes step A's one-line switch-offs for the restored events (`--keep-off=` keeps listed IDs off), and reports missing calls and dependencies. |
| `phase8_multiline_off.py` | Undoes step A switch-offs written as a commented-out block (`#character_event = { # <note>` … `#}`), which `phase8_hf.py` misses, when every event the block calls now exists. `--keep-off=phase8_keep_off.txt` keeps the left-out crusade chains off. |
| `phase8_lodges.py` | Phase 8 part 5: builds the warrior lodges from AIO (societies, triggers, decisions, loc, traits, art) and ties them to LI faiths through `li_warrior_lodge_triggers.txt`. Rerunnable; run `phase8_hf.py` on the lodge event files first. |
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
