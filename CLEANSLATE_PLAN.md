# Lux Invicta on CleanSlate: migration plan

Branch: `CleanSlate`. Base: CleanSlate 1.0 beta 7 (the changelog inside still says beta 6.1, so check
the ck2plus/CleanSlate GitHub for a newer release before starting). Game: CK2 3.3.3.

## Goal and rules

- Rebuild Lux Invicta on CleanSlate's fixed vanilla files, keeping LI's own content and behaviour.
- No Lux Renata (CK3) lore is brought into the mod. This is a code cleanup.
- Behaviour stays the same unless a change is decided on purpose and noted.
- Every phase ends with an in-game run and an `error.log` comparison. Vanilla 3.3.3 with no mods
  logs 0 lines in `error.log`, so every line LI logs is a real difference.

## Where we start (master after the pre-CleanSlate pass, 2026-11-14)

- `error.log`: 7,227 → 5,564 lines. 5,223 are vanilla French/Spanish/German customizable
  localisation (fixed by CleanSlate's localisation plus a trim). About 340 are other errors, mostly
  Holy Fury branches left on purpose.
- Holy Fury is switched off: calls to Holy Fury events LI does not ship are commented out
  (`(Holy Fury event not in Lux Invicta, DLC switched off)`), and weighted entries became `N = 0`
  or `N = { }` so odds are unchanged.
- Saved logs to compare against: `Crusader Kings II/LI_baseline_logs_2026-11-14` (start),
  `LI_logs_run13_2026-11-14` (end of the pass), `vanilla_logs_2026-11-14` (no mods).

## What the survey found

LI's copies of vanilla files are not based on vanilla 3.3.3. They come from older vanilla versions
and CK2Plus, and the mod bundles many other mods (CK2Plus, VIET, SELIN, ze, rip, wol, oldgods…). A
file-by-file 3-way merge onto CleanSlate fails: 203 of the 228 shared files conflict even with
formatting ignored. So the migration works **definition by definition** (each event, decision,
scripted effect/trigger, modifier, CB, trait, law…).

| LI definition | Count | Plan |
|---|---|---|
| Unchanged from vanilla 3.3.3 | 13,779 | Drop LI's copy and use CleanSlate's fixed version. |
| New in LI | 9,506 | Move into LI's own files, mostly by script. |
| Changed, and uses LI-only content (religions, titles, events…) | ~527 | Real LI changes: port each onto CleanSlate's version by hand. |
| Changed, no LI-only content | ~1,945 | Probably an older vanilla copy: take CleanSlate's version, spot-check. |
| Changed dynasties (4,959) and landed titles (78) | 5,037 | LI's world data: keep LI's. |
| Vanilla definitions LI dropped | 6,985 | They come back with CleanSlate, so they need LI's policy (see phase 5). |

File-level: 7,512 LI-only files and 3,375 LI data files (history, map, gfx) carry over as they are.
889 LI files are byte-identical copies of vanilla and can simply be dropped.

## Layout on the branch

- CleanSlate's files go into the repo with CleanSlate's names. LI's changes to a vanilla definition
  are made in place in the CleanSlate file, marked `# LI:` so they can be found and diffed against
  future CleanSlate releases.
- LI's own definitions live in LI-named files (e.g. `common/scripted_effects/li_*.txt`,
  `events/li_*.txt`), not mixed into CleanSlate's files.
- `Lux Invicta.mod`: CleanSlate's `replace_path` list (all of `common`, `events`, `decisions`,
  `localisation`, `history/*`) plus LI's (`map`, `history/diplomacy`, `dlc_metadata/dlc_characters`).
  Note: CleanSlate's own descriptor says not to replace `interface` or `interface/portraits`.

## Phases

Each phase is its own commit (or several), followed by a run and a log comparison.

0. **Set up.** *(Done 2026-11-14.)* An untouched reference copy of CleanSlate is in
   `cleanslate_beta7/`, which CK2 ignores; later phases build LI's files from it. A separate test
   mod, "CleanSlate beta 7 (baseline test)" (`mod/CleanSlate-beta7`, outside the repo), is used to
   record a baseline log of CleanSlate alone, so CleanSlate's own errors, if any, are known.
   **Baseline result** (`Crusader Kings II/CleanSlate_baseline_logs_2026-11-14`): `error.log` has
   724 lines. They aren't bugs. About 590 are CleanSlate's scope shorthand, which the load-time
   checker can't resolve (`religion = liege`, `culture = attacker`, `religion = d_knights_templar`,
   `… = thirdparty_title_scope`); 101 are "event has no picture" for hidden events; 9 are
   customizable localisation. `historical_setup_errors.log`: 7,370 "Missing scripted successor"
   (vanilla: 7,367). Count only lines beyond these patterns as migration problems.
1. **World data.** LI's map, history, landed titles, cultures, religions, dynasties, gfx, music and
   sound replace CleanSlate's. This is where the most errors will appear, because CleanSlate's
   scripts expect vanilla's world. That's expected; phases 2–6 work them down.
   *(Built 2026-11-14 with `tools/phase1_build.py`.)* Kept from LI: map, history, gfx, music,
   sound, interface, localisation, and `common/` landed_titles, cultures, religions, dynasties
   (LI's, per decision 1), graphicalculturetypes, bookmarks, defines.txt. Everything else in
   `common/`, `decisions/`, `events/` and `dlc_metadata/` is CleanSlate's (LI's versions stay in git
   on `master`). Details:
   - CleanSlate's localisation CSVs were added as `localisation/zz_cs_*.csv`, so LI's text wins for
     the 33,540 keys both define (CK2 uses the first file alphabetically). Phase 6 picks per key.
   - Interface: only CleanSlate's cleaned copies of vanilla files were added. Its 55 reorganised
     files (`coat_of_arms/coa_*.txt`, `holdings/CleanSlate_holdings_*.gfx`…) were left out,
     because they would duplicate LI's `coats_of_arms.txt` and sprites. Review them in phase 3.
   - LI's trimmed `dlc_recommendations` was replaced by CleanSlate's: redo it in phase 5.
   - `Lux Invicta.mod` / `mod/lux-invicta-recode.mod`: CleanSlate's `replace_path` list plus
     `history`, `history/diplomacy`, `map`.
2. **LI's new definitions (9,506).** Scripted move into LI-named files. Watch for the 7 keys that
   LI and CleanSlate both added.
3. **LI's real changes (~527).** For each: diff LI against vanilla, apply only LI's change onto
   CleanSlate's definition, and mark it `# LI:`. The ~1,945 older-vanilla copies take CleanSlate's
   version, with a spot-check of a sample per folder.
4. **CleanSlate's renames** across LI's files: `k_papal_state` ↔ `k_papacy` (swapped!),
   `assassins_debt` → `assassins_debt_modifier`, the secret-religion triggers (replaced by an
   `old_religion` event target), and the smith/goldsmith artifact `_flag_*` → `_tier_N` names.
5. **Vanilla content LI dropped (6,985 definitions).** Re-apply LI's decisions to CleanSlate's
   copies:
   - **DLC switched off** for now. Holy Fury, plus the Jade Dragon / Rajas / Horse Lords pieces LI
     lacked. Same comment style and `N = 0` / `N = { }` rule as on master.
   - **Things LI removed on purpose:** Sunni Islamic schools (Mu'tazila/Ash'ari decisions hidden),
     the Mongol decisions (LI has no `e_mongol_empire`), the court griot.
   - **Everything else:** log-driven, as in the pre-CleanSlate pass.
6. **Localisation.** CleanSlate's localisation (reorganised and fixed) plus LI's CSVs, with LI's
   overriding where both define a key. Then trim the French/Spanish/German customizable
   localisation of checks for things LI lacks, using the same behaviour-identical tool.
7. **Re-apply master's fixes that live in replaced files.** Most of the pre-CleanSlate fixes are in
   LI's own data and files and carry over. Re-check the ones made in vanilla-derived files:
   `dynasty = 0` → `none`, the holy order expulsion (SoA.1060), the game rules (generate families
   default off), the Hellenic temple `tier = BARON`, and the conversion decision's war scope.
8. **Holy Fury integration**, the first feature on the new base, one part at a time (crusades;
   warrior lodges and duels; religious and flavour). This is partly lore work, decided per part.

## Tools (currently in the session scratchpad; move into `tools/` in the repo to keep them)

- `def_survey.py`: classifies every LI definition (new / unchanged / changed) against vanilla and
  CleanSlate. It drives phases 2 and 3.
- `merge_survey.py`: file-level 3-way merge survey.
- `trim_dead.py`: removes checks for cultures, religions, dynasties, titles, traits, artifacts and
  claims that don't exist, without changing behaviour (constant folding; drops only blocks that can
  never match).
- `hf_off.py`, `hf_off_onactions.py`, `ids_off.py`: switch off calls to missing events, keeping
  random weights.
- `copy_events.py`: copies vanilla events into LI after checking their dependencies.
- `fix_buildings.py`: fills in missing building prerequisites in province history.

## Open decisions

1. **Dynasties:** CleanSlate fixed some duplicate dynasty IDs, but LI's dynasty file is LI's own
   data. Keep LI's and only check the IDs CleanSlate changed?
2. **Older-vanilla copies (~1,945):** take CleanSlate's version by default, or review each folder
   first?
3. **File naming** for LI's own files: `li_*` prefix, or keep the bundled mods' names (`VIET_*`,
   `ze_*`…) so their origin stays visible?
4. ~~**CleanSlate version**~~ Decided: beta 7 is the latest GitHub release (checked 2026-11-14).
