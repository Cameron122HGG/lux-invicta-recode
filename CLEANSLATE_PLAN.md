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
   *(Built 2026-11-14 with `tools/phase2_build.py`; decision 3: `li_` prefix.)* 360 `li_*` files:
   - LI's 5 wholly-replaced folders (buildings, trade_routes, societies, artifacts,
     artifact_spawns) replace CleanSlate's whole, as in LI's old `.mod` (50 files).
   - 259 LI-only files copied whole, comments kept.
   - 51 files extracted from LI's edited copies of vanilla files: only definitions vanilla lacks,
     with event namespaces and `decisions = {}` / government-group wrappers.
   - 351 master files had nothing new; their LI changes are phase 3.
   - 84 LI definitions whose key CleanSlate also defines (shared CK2Plus heritage, e.g.
     `faction_succ_ultimogeniture`, `GBC.*` events) are left out, so CleanSlate's version is used.
     They're listed for phase 3 in `migration_notes/phase2_clashes.txt`.
   - Checked: all `li_` files have balanced braces; no duplicate event IDs.
   - Follow-up: laws and religion features also sit inside group blocks (`laws = {}`,
     `de_jure_laws = {}`, `law_groups = {}`, `religion_doctrine = {}`…), so the first run missed
     LI's laws (the phase 2 run logged 133,000 "Bad law" lines). Re-run with
     `--only=common/laws,common/religion_features`: `li_0_term_laws`, `li_slavery_laws` whole, plus 150
     laws from 3 files. Religion features had nothing new.
3. **LI's real changes (~527).** For each: diff LI against vanilla, apply only LI's change onto
   CleanSlate's definition, and mark it `# LI:`. The ~1,945 older-vanilla copies take CleanSlate's
   version, with a spot-check of a sample per folder.
   *(Started 2026-11-14.)* First fixes, driven by the phase 2 run's log:
   - CleanSlate's renamed IDs applied to LI's files with `tools/cs_renames.py` (pulled forward from
     phase 4): 76 renames, 555 lines in 49 files. Covers traits (`fair` → `attractive`,
     `robust` → `brawny`…), event/opinion modifiers, scripted triggers/effects, decisions and combat
     tactics, including `GFX_trait_*` sprite names and LI's localisation keys. Cultures, religions,
     titles and governments are **not** renamed: those are LI's own world (see phase 5). The
     changelog's `slow_ever` is a typo for `slow_fever`.
   - 29 vanilla events that CleanSlate removed or inlined, but that LI's content still calls
     (holy order borrowing/donations `SoA.1010/1015/1140`, pagan feasts, pilgrimages, regency
     duels…), restored from LI's master versions into `events/li_restored_events.txt`.
   - Renames, second pass: character history writes many trait names in quotes (`"fair"`), and
     LI's `interface/portrait_properties` and `customizable_localisation` `.txt` files are code.
     `cs_renames.py` now covers both (84 more replacements; files identical to CleanSlate's skipped).
   - `common/offmap_powers/00_offmap_powers.txt`: LI's master version replaces CleanSlate's whole.
     LI rebuilt China around its own religions (1,285 changed lines against vanilla), while
     CleanSlate's China preferences check vanilla religions LI lacks (2,583 error lines). LI's
     policies and statuses equal vanilla, so CleanSlate's versions stay. Review CleanSlate's
     `00_offmap_powers.txt` for real fixes later.
   - **"LI's version wins" (2026-11-14, `tools/phase3_li_wins.py`).** 676 definitions that LI
     changed and that use LI's own content (336 events, 70 decisions, 55 minor titles, 43 scripted
     triggers, 34 traits…) now carry LI's master text in place of CleanSlate's, with CleanSlate's
     renames applied and the marker `# LI: Lux Invicta's version (from master)…`. CleanSlate's fixes
     inside those definitions are given up for now; compare against `cleanslate_beta7/` later.
     111 LI-changed definitions that CleanSlate dropped entirely were skipped.
   - **LI's on_action entries.** Phase 2 had skipped `on_actions`, so most of LI's own pulse and
     trigger events weren't hooked up. 1,134 entries are now in `common/on_actions/li_on_actions.txt`
     (CK2 merges on_action lists across files). 88 more pointed at events CleanSlate removed or
     merged; those 134 events (with what they call) were restored from master into
     `events/li_restored_events.txt`, and hooked up in `li_on_actions_restored.txt`. Checked: no event
     ID defined twice, and no event listed twice in one on_action.
   - Follow-up after the "LI wins" run (6,618 lines): 152 more events that LI's restored
     definitions call, but CleanSlate had removed or merged, were restored from master into
     `li_restored_events.txt` (no duplicate IDs). `dlc_recommendations` was re-trimmed from
     CleanSlate's copy (110 dead checks, 24 hints). Behaviour-identical trims were applied to 14
     CleanSlate files (630 lines removed). **Still open:** ~1,400 load-time errors from whole dead
     vanilla branches in CleanSlate files (scripted triggers like `religion = lollard`, `if` limits
     on vanilla religions, Templar-only events). They never run in LI, but removing them safely
     needs per-case handling (e.g. a dead trigger becomes `always = no`; an `if` with an `else`
     can't simply be deleted).
   - Trait icons: CleanSlate's renamed traits look for icons under the new names
     (`gfx/traits/attractive…`), which phase 1 hadn't brought over with LI's gfx (1,030 error lines).
     29 icons added to `gfx/traits`: LI's own art copied to the new name where LI had it (`fair`,
     `martial_cleric`, `syphilitic`), CleanSlate's icon for the other 26. 7 language-flag icons
     (`gfx/interface/*_flag.dds`) that CleanSlate's interface uses were added too.
   - **`trim_dead.py` correctness fix (2026-11-14).** With `--scopes` it treated every block as
     "all of", including `trigger_if`. But a `trigger_if` whose limit can never hold *passes*, so the
     old tool wrongly removed such blocks from `OR` lists. Fixed: `trigger_if`/`trigger_else_if` with a
     dead limit count as true; `NAND` with a dead child counts as true; effect, weight and count blocks
     (`if`, `else`, `calc_true_if`, `ai_chance`, `option`…) pass nothing up. An all-dead `OR` keeps its
     entries rather than becoming empty. A `trigger_if` that a `trigger_else` follows is never removed.
     Also new: `society_member_of` checks (against LI's societies), and `--defs` to fold plain
     definitions such as scripted triggers. **Audit:** every trim made with `--scopes` was re-run from
     its pre-trim version. 6 branch files were rebuilt (`03_cb_score_values`,
     `00_religion_feature_triggers`, `00_secret_religious_communities_triggers`, `03_crusade_triggers`,
     `00_religion_effects`, `00_scripted_effects`). The others, and master's portrait/Holy Fury trims,
     were already correct.
   - **CK2Plus AIO survey (2026-11-14)** (`mod/ck2plus_aio.zip`, 12 Nov 2026, CK2Plus with
     CleanSlate built in). Of LI's definitions: 435 are CK2Plus content (not vanilla; 28 identical to
     AIO, 407 changed since LI copied them); 1,555 are vanilla definitions CK2Plus also changed. Of
     those, 852 (dynasties aside) have no LI-specific content and 203 use LI's own
     religions/cultures/titles. AIO keeps almost all vanilla DLC content (2,305 of 2,339 CleanSlate
     events LI never had). `mod/ck2plus.zip` (Jul 2025) is CK2Plus *on top of* CleanSlate, so it holds
     only CK2Plus's own changes.
   - **Decision 5:** for definitions LI copied from CK2Plus that have no LI-specific content, use
     **CK2Plus AIO's current versions** (already migrated to CleanSlate and maintained). Those parts
     will play like today's CK2Plus. The ~203 that use LI's world are ported by hand.
   - **Step B (decision 5), started 2026-11-14** with `tools/phase5b_aio.py` (survey, then `--apply`
     per folder). A definition is swapped for AIO's text when LI's master copy differs from vanilla,
     AIO's differs from CleanSlate's/vanilla's, LI's text uses none of LI's own names, and the mod's
     current block is not LI-wins, world data, an on_action list or a Holy Fury file. Marker:
     `# LI: CK2Plus AIO version (step B, decision 5)`. Survey: 484 real swaps; 606 where the mod
     (CleanSlate) already equals AIO; 443 that need AIO content the mod lacks (`in_command_trigger`,
     `obj_get_nick`, Holy Fury lodges…); 544 that use LI's world (hand port).
     **Batch 1 applied:** 298 definitions in 78 files (modifiers, traits, static modifiers, decisions,
     CBs, laws, minor titles, artifacts…). **Batch 2 (186 events)** waits for a test run.
     Batch 1 test (+45 lines) showed two mistakes, both fixed: in `common/buildings` each top-level
     block is a whole holding type's building list, so the swap had replaced LI's castle/city/temple/
     tribal/nomad/hospital/family-palace/trade-post buildings with CK2Plus's (using a tech LI removed,
     `TECH_TEMPLE_CONSTRUCTION`). The 5 building files and `00_job_actions.txt` (AIO's
     `action_assist_arrest` lists event 940, which the mod lacks) were restored to their pre-batch
     state, and the tool now skips both folders and checks `events = { }` lists. Dead vanilla religions
     in AIO's religion features, societies and religion triggers were trimmed. Re-run: 5,361 (clean).
     **Batch 2 applied:** 184 events in 49 files. The tool now also skips blocks that carry an
     `# LI:` fix inside them (so the `TOG.1000`/`HL.2000`/`100420` triggers and similar stay).
     **Still to do in step B:** 443 definitions that need AIO content the mod lacks, and 543 that
     use LI's world (hand port).
     **Re-survey after phase 8 (2026-11-15):** 1,089 where the mod already equals AIO (was 606); 9 ready swaps
     with nothing missing (6 decisions, `selfish_pattern_against`, `check_if_ancestor_worship_worthy_effect`,
     society `the_assassins`); 400 that need AIO content (211 need one item: `obj_get_nick` 74 nicknames,
     `in_command_trigger` 53, `sent_druidic_training` 10…; some needs are things LI left out on purpose, e.g.
     `the_cold_ones`, `chalcedonian`, `roman_pagan`, `martial_lady*`, so those rows are hand-port or skip);
     543 that use LI's world (unchanged); 105 skipped as Holy Fury files.
     **Batch 3 applied (2026-11-15):** AIO's `obj_get_nick` ambition (`common/objectives/li_CK2Plus_ambitions.txt`,
     with its hidden `ai_objective_timer` in `common/event_modifiers/li_CK2Plus_timers.txt`) and `in_command_trigger`
     (`common/scripted_triggers/li_CK2Plus_war_triggers.txt`) brought in, which freed 127 definitions. 131 swapped
     in 19 files: 74 nicknames, 53 events (court, crusade, feast, feudal life, friends/rivals, hunting, prison,
     legends, traits, WoL lover/seduction/theology), `selfish_pattern_against`, and the decisions
     `chinese_kow_tow_pilgrimage`, `hermetic_grand_debate`, `hold_nomad_wargames`. **Kept LI's version** of 5 the
     survey marked ready, listed in `tools/phase5b_keep_li.txt` (`--keep-li=`): `the_assassins` and
     `assassins_recruit` (LI's Qarmatian Assassins and per-faith orders), `employ_spymaster`/`employ_chancellor`
     (LI triggers, RoI.30121), `check_if_ancestor_worship_worthy_effect` (AIO checks the seafaring trigger in its
     "Unrelenting" weights). **Lesson:** the survey's "no LI names" test misses LI changes that use vanilla names
     (Qarmatian) or LI's own triggers; compare LI's master text with AIO's before applying.
     Untested in game.
4. **CleanSlate's renames** across LI's files: `k_papal_state` ↔ `k_papacy` (swapped!),
   `assassins_debt` → `assassins_debt_modifier`, the secret-religion triggers (replaced by an
   `old_religion` event target), and the smith/goldsmith artifact `_flag_*` → `_tier_N` names.
5. **Vanilla content LI dropped (6,985 definitions).** Re-apply LI's decisions to CleanSlate's
   copies:
   - **Decision 6 (2026-11-14): leave out** CleanSlate's event/decision content that LI never had
     (1,687 events in 60 files, plus parts of shared files; per-DLC table in the session notes), and
     switch off calls to it, keeping random weights. It stays in `cleanslate_beta7/` for later.
     *(Step A, done 2026-11-14.)* `tools/phase5_leave_out.py` removed 1,967 CleanSlate events and 229
     decisions that LI's master never had (57 files emptied and deleted, 73 trimmed). It kept 448
     CleanSlate events that LI's content calls (e.g. its refactored holy-order letters) and counted
     renamed decisions as LI's. Calls to the removed events were switched off with the note "event
     left out of the CleanSlate build: LI never had it (decision 6…)":
     - 211 call sites via `hf_off.py --ids-file=… --note=…`;
     - ~370 `on_actions` entries via `hf_off_onactions.py` (namespaced IDs);
     - 157 numeric IDs via `ids_off.py`;
     - 1 by hand (`repeat_event = { # comment` in `05_competition_effects.txt`).
     A final scan found no live call to a removed event.
   - **DLC switched off** for now. Holy Fury, plus the Jade Dragon / Rajas / Horse Lords pieces LI
     lacked. Same comment style and `N = 0` / `N = { }` rule as on master.
   - **Things LI removed on purpose:** Sunni Islamic schools (Mu'tazila/Ash'ari decisions hidden),
     the Mongol decisions (LI has no `e_mongol_empire`), the court griot.
   - **Everything else:** log-driven, as in the pre-CleanSlate pass.
   - **Step A review (2026-11-14).** Step A matched events by ID, which is wrong in three ways:
     1. *Renumbered events.* CleanSlate gave many vanilla events new IDs (`910` → `chancellor.001`),
        so its versions of events LI had looked new and were removed. Restored: the 5 council job
        event files (173 events; every job action had lost its event), the Charlemagne councillor
        chain `CK2.18000`–`18004` (with 3 decision calls), and 3 LI-wins job actions translated from
        old numbers (`913 914`, `900–903`, `20218`) to CleanSlate's IDs.
     2. *Router events.* CleanSlate turned many MTTH events into triggered-only events started by a
        new hidden "router" event in its on_actions. Step A removed the routers (new IDs) and zeroed
        their entries, so LI content went silent without any error line. 42 routers restored with
        CleanSlate's on_action lines: Muslim honorary titles, polygamy, court ambition, religious,
        health (Voice of Jesus/Satan), imprisonment, feast/hunt cancelled, Republic trade, relics,
        WoL business, Nerge, the married-life courtier (`30039`) and the imprisoned Orthodox bishop
        (`39229`). Holy Fury routers, CleanSlate-only additions and routers whose targets LI reaches
        itself were left out.
     3. *Merged decisions.* CleanSlate merged vanilla's 7 devil-worshipper recruit decisions into one,
        which step A removed; LI's 6 own versions (LI-world religion limits) were restored from master
        into `li_mnm_society_decisions.txt`.
     The audit scripts (`renumbered_audit`, `routers`, `dec_audit`, `orphan_targets`) found these; the
     other candidates were checked by hand and are fine. The 15-candidate and 229-decision audits are
     done. Housekeeping events `CK2.689/690/691/63106` stay off (LI runs its own 689/63106).
   - **LI-wins / CleanSlate mismatches (2026-11-14).** Where an event chain mixes LI's and
     CleanSlate's versions, one side can lack the setup the other expects:
     - CleanSlate events whose trigger moved into a router but that LI's on_actions fire directly got
       their trigger back: `HL.2000`/`HL.2010` (minor clan revolt), `100420` (tournament cheating),
       `TOG.1000` (peasant revolt holding check). LI's `30040` entry now fires the router `30039`.
     - CleanSlate on_actions that fire LI-wins events needing `FROM` from an LI caller were zeroed
       (`N = 0`): `TOG.3400` (buffalo woman), `SoA.1003` (master never fired it), `WoL.7042`, and LI's
       own direct `39230` entry.
     - Holy order joining: LI's SoA.1030 + CleanSlate's SoA.1031 → master's SoA.1031–1033 + 2864, and
       an original LI bug fixed (1032 saved `holy_order`, 2864 read `order_target`).
     - The ultimogeniture faction ultimatum is LI's jordarkelf version again (`jordarkelf_factions.2`).
     - **Lesson:** after restoring master text, run `tools/cs_renames.py` (`li_restored_events.txt`
       had missed 24 renames, e.g. `gamer`); master text pasted into CleanSlate-named files needs the
       renames applied by hand.
   - **Other log-driven fixes (2026-11-14):** 30 vanilla scripted triggers/effects CleanSlate removed
     but LI calls (`tools/restore_scripted.py` → `common/scripted_*/000_li_restored_*.txt`);
     `remove_education_effect`; the warrior-lodge trigger `always = no`; the year-slider and
     letter-intrigue sprites; LI's original MNM.6990 (9 assassin orders each keyed on its own title)
     and the Cult of Kali recruit check; 204 dead `secretly_*` opposites; a `trim_dead` sweep over the
     23 biggest non-localisation script files. Run 3s: 5,341 lines (3,738 localisation, ~1,600 other,
     of which ~1,330 are dead vanilla checks that can't be removed safely).
6. **Localisation.** CleanSlate's localisation (reorganised and fixed) plus LI's CSVs, with LI's
   overriding where both define a key. Then trim the French/Spanish/German customizable
   localisation of checks for things LI lacks, using the same behaviour-identical tool.
   *(Started 2026-11-14.)* The 3,738 log lines were dead title/culture/religion/society checks in
   customizable localisation (2,453 French, 1,085 Spanish). `trim_dead.py` with unit `text` removed
   7,768 lines from 6 files: entries that can never be valid, and dead entries in `OR`/`NOR` lists.
   No `defined_text` lost or emptied; `00_customizable_localisation_DE_Warrior_lodges.txt` was left
   alone (Holy Fury; it would empty 4 definitions). Missing keys: 115 referenced by events and
   decisions are in no CSV (CleanSlate alone: 152); most are `create_character` names. The real ones
   (`EVTDESC_TOG_75xx_*` West African ancestor variants, `EVTDESC66050/66051`) were missing on master
   too: original LI gaps, for later.
7. **Re-apply master's fixes that live in replaced files.** Most of the pre-CleanSlate fixes are in
   LI's own data and files and carry over. Re-check the ones made in vanilla-derived files:
   `dynasty = 0` → `none`, the holy order expulsion (SoA.1060), the game rules (generate families
   default off), the Hellenic temple `tier = BARON`, and the conversion decision's war scope.
   *(Done 2026-11-14.)* Every line master's 19 fix commits added was searched for on the branch. Present:
   history, interface/coats of arms, holy order expulsion (139/139), `d_vesta_temple`, `dynasty = none`,
   the conversion war scope, the Hellenic temple, the game-rule events (GR.14–23, GR.30), 39704/39706,
   all switched-off calls. Not needed: master's Holy Fury switch-offs (handled by step A and CleanSlate's
   own Holy Fury files), `baptized_by_satan` (CleanSlate defines the trait). **Re-applied (4):**
   generate-families default `off`, `song_dynasty_futou_trigger` (`dynasty = 1051151` → `always = no`),
   `taoist_opinion` → `tao_opinion` in the earned bloodlines, and the Sunni school decisions
   (`embrace_mutazila`/`embrace_ashari`) hidden again, each marked "(master fix, phase 7)".
8. **Holy Fury integration**, the first feature on the new base, one part at a time (crusades;
   warrior lodges and duels; religious and flavour). This is partly lore work, decided per part.
   - The rival-in-battle event (`WoL.11013`/`WoL.11014`, which LI had on master) is commented out
     in CleanSlate's `wol_war_events.txt` and moved into its Holy Fury duel events (`HFP.10113` in
     `hfp_duel_events.txt`). LI lacks it while Holy Fury is off; it comes back with the duels part
     (user decision 2026-11-14: wait for phase 8, don't uncomment master's version).
   - **State (2026-11-14):** 1,084 of CleanSlate's 2,203 Holy Fury events are in the mod. Complete:
     coronation, sway/antagonize, tribal, saintly pilgrimage; mostly: religious, bloodlines, baptism,
     pregnancy; a few: battle (4/53), duels (7/37), health (7/96); none: warrior lodges (9 event files,
     9 societies), Holy Fury crusades/children's crusade/Reconquista (1/205), sainthood, eldership,
     bloodline acquisition, realm events. 330 calls to Holy Fury events are switched off (step A note);
     83 Holy Fury on_action entries are live. Of the 9 lodge religions LI has `norse_pagan`,
     `tengri_pagan`, `slavic_pagan`, `finnish_pagan`, but not Baltic, West African, Zun, Bön or Hellenic.
   - **Decisions (user, 2026-11-14):**
     - **Source: CK2Plus AIO's Holy Fury content** (consistent with decision 5), not plain CleanSlate's.
     - **Warrior lodges: map LI's own pagan faiths onto the lodges** (lore decisions per faith, made with
       the user), not only the 4 that exist, and not left out.
     - **Order:** mechanical parts first.
   - **Parts, in order** (one at a time, a test run after each):
     1. Mechanical, no lore: battle events, commander duels (brings back `WoL.11013`/`HFP.10113`),
        remaining pregnancy/health events, realm and random flavour, Holy Fury holy order events.
     2. Sainthood and ancestor worship (mapped to LI's titles).
     3. Bloodline acquisition (legendary deeds), checked against LI's own bloodlines.
     4. Crusades: the Holy Fury crusade system, children's crusade, Reconquista (LI's Iberia/titles).
     5. Warrior lodges, with the faith mapping.
   - **Per part:** restore AIO's events/societies/decisions for that part; undo step A's switch-offs for
     those IDs (and master-style Holy Fury switch-offs); check dependencies (events, scripted items,
     score values, modifiers, localisation); `trim_dead`; orphaned-target check; test run.
     Tool: `tools/phase8_hf.py <repo> <aio> <ids_out> <files…> [--apply]`, then `hf_off.py --ids-file=… --note=…`
     for calls into later parts (note: "Holy Fury event from a later phase 8 part, not restored yet").
   - **Part 1 applied (2026-11-14):** AIO's `HF_battle_events`, `hfp_duel_events`, `HFP_health_events`,
     `HFP_pregnancy_events`, `HFP_random_flavor_events` (replaced) and `HFP_realm_events`,
     `HFP_holy_order_events` (new): 469 events. 64 step A switch-offs undone (`15_holy_fury.txt`,
     `00_health_effects.txt`, `01_duel_effects.txt`). Calls into later parts switched off: `HF.12405`
     (battle bard bloodline, part 3), `HFP.41090` (crusade levy refill, part 4). No missing dependencies.
     Test run (+50, all load-time): `HFP_realm_events` (Hansa, Swiss, Antioch, Cyprus, Austria, Byzantine
     restoration, Papal States/Romagna, HRE stem duchies, Slavic Union, Teutonic/Santiago/Calatrava/Holy
     Sepulchre formation) and `HFP_holy_order_events` turned out to be vanilla-world realm content, not
     mechanical. Both taken out again; their 17 entries in `15_holy_fury.txt` switched off with the
     "later phase 8 part" note. **They move to part 4** (crusades, holy orders and titles, with lore
     decisions). Part 1 keeps battle, duels, health, pregnancy and random flavour (433 events).
     Re-run: 1,693 (part 1 done).
   - **Part 2 applied (2026-11-14):** AIO's `HF_sainthood_events`, `HF_saint_flavour_events`,
     `HF_saintly_bloodlines_events`, `HF_ancestor_worship_events` (49 events); 16 step A switch-offs undone
     (`HF.40000` beatification and `HF.40100` ancestor worship are live again). Pagan sainthood is gated by
     the `religion_beatification` feature, which LI's reformed faiths can already choose. User decisions:
     all of LI's reformed pagan faiths can found saintly bloodlines; Celtic → Germanic family, Egyptian and
     Near-Eastern → Hellenic (both commented as stand-ins), Sol → Hellenic. New
     `common/scripted_triggers/li_pagan_saint_triggers.txt` (9 families, 50 faiths); the event's 45 vanilla
     faith branches check those triggers, the bloodline takes the saint's own faith, the pagan description
     checks "not Christian", `k_papacy` → `k_papal_state` (LI's Pope). Aztec branches stay (no LI faith).
     **Moved to step B:** CK2Plus's own Christian sainthood (`CK2Plus_religion_christian_sainthood.txt`):
     it belongs to CK2Plus's Christian religion system (its own on_actions and effects, 5 traits with
     icons, 129 localisation keys), so it comes in with that system, not with Holy Fury.
   - **Part 3 applied (2026-11-14):** AIO's `HF_bloodline_acquisition_events` (44 events, legendary deeds;
     5 step A switch-offs undone). `HF_bloodline_events` keeps its 4 LI-wins events; 19 missing events added from
     AIO: Holy Fury's special executions (brazen bull, macabre banquet, dragon fire) with their 3 prisoner
     decisions in `HF_bloodline_decisions.txt`, the mental-decay check, the Chinese Imperialism bloodline
     (`adopt_chinese_imperialism`), and **Ashoka's tests** (its `religion = buddhist` checks → `religion_group =
     bud_group`). User decision: **not** Alexander's tomb (LI has its own `alexander` bloodline), Teuta or
     Matilda (tied to vanilla's world); those quests stay switched off. `HF.12405` (battle bards) belongs to
     part 5 (warrior lodge legends).
   - **Part 4 decisions (user, 2026-11-15):** vanilla's named holy orders (Templars, Hospitallers, Teutonic and
     Livonian Orders, Santiago, Calatrava): generic content maps to the faith's LI order (`d_holycatholic`…),
     order-founding content stays out; Holy Fury realm events (`HFP_realm_events`): out; Reconquista: out
     (revisit with LI's Iberian lore); Fourth Crusade / Latin Empire path: off.
   - **Part 4 step A applied (2026-11-15):** AIO's `HF_crusade_events`, `HFP_crusade_events` (replaced),
     `HF_childrens_crusade_events`, `HFP_crusade_flavour` and decisions `HFP_crusades.txt`
     (`select_crusade_beneficiary`, `dynamic_crusader_state`): 172 events, 78 step A switch-offs undone, with
     `phase8_hf.py --keep-off=` keeping the Fourth Crusade (`HF.49000/49006/49008`) and Teutonic Northern Crusade
     (`HF.49100-49121`) chains off; only the crusade bloodlines (`HF.49020/49021`) are live from that file.
     Adapted: `k_papacy` → `k_papal_state`; children's crusade regions `world_europe_west_gaul` →
     `world_europe_west_francia`, `world_middle_east_asia_minor` → `world_asia_minor`; `HFP.42212` picks a ruler
     leading a holy order of the character's faith instead of vanilla's named orders. Crusade announcement
     event `200` restored from AIO (LI's old 320/322/323 stay for the old system).
   - **Part 4 step B applied (2026-11-15):** `events/HFP_holy_order_events.txt` is AIO's file cut down to
     `HFP.44000-44004` (scratchpad `holy_orders.py`). `HFP.44002/44003` (an order leaves a liege it finds unfit)
     are generic and unchanged. The island request `HFP.44000/44001/44004` now goes to a holy order of the
     island holder's faith (LI has one per faith, `d_holy<faith>`) instead of `d_knights_hospitaller`: a
     `random_character` with `holy_order = yes`, `religion = ROOT` and none of the islands yet saves
     `holy_order_target`, then sends the letter. `d_corsica` → `c_corsica` (a county in LI's `d_sardinia`), the
     Hospitaller rename dropped, the order keeps its own `holy_order` title, and the donor is saved as
     `island_donor` for the narrative event. New loc `localisation/000_li_holy_order_events.csv` (sorts before
     `HolyFury.csv`) names the order. On_actions: `HFP.44000` (3 entries) and `HFP.44002` back on;
     `HFP.44005/44008/44009` (Teutonic/Livonian) and `HFP.40033/44036` (realm events) keep their switch-off
     with a "left out by decision" note.
   - **Loading screens (2026-11-15):** both descriptors now `replace_path = "gfx/loadingscreens"`, so only LI's
     `load_0-16`/`load_99` show (the base game's `load_17-20`, Holy Fury era, used to show through; master too).
   - **Part 5 decisions (user, 2026-11-15):** 11 lodges: vanilla's 9 plus CK2Plus AIO's Celtic (the Fianna) and
     Egyptian (Champions of the Sun) lodges. Faiths, in `common/scripted_triggers/li_warrior_lodge_triggers.txt`:
     Wolf Warriors = LI's Norse list + the Germanic faiths; Eagle Warriors = LI's Tengri list; Band of Medeina =
     Baltic group (+ Saulic); Followers of Otso = Finnic group + Ukpirniq (as the saints); Champions of Perun =
     Slavic group; Children of the Storm = Serer group, Yoruba and the Bantu faiths; Keepers of the Flame = the
     desert faiths only (Arabian, Berber, Palmyrene); Sentinels of Light = Bön only; Olympian Champions =
     Graeco-Roman group, Indo-Hellenic, Luwian and the southern Sol faiths; Celtic lodge = Celtic group + Celtic
     Christianity; Egyptian lodge = Egyptian group. Other LI faiths use the lodges' generic path (tribal, not
     zealous, lodge has 10 members), as non-pagans do in vanilla.
   - **Part 5 applied (2026-11-15):** `tools/phase8_hf.py` on the 9 lodge event files (317 events, 71 step A
     switch-offs undone), then `tools/phase8_lodges.py` (rerunnable): societies `00_warrior_lodges.txt` (AIO) +
     `01_li_CK2Plus_warrior_lodges.txt` (CK2Plus Celtic/Egyptian), AIO lodge triggers, AIO lodge decisions with
     LI's own `duel_decision` kept, CK2Plus `celtic_battle_cry_decision`, AIO lodge customizable loc + CK2Plus
     name getters (`09_li_CK2Plus_warrior_lodges.txt`), traits `celtic_leader`/`egyptian_leader`
     (`li_CK2Plus_lodge_traits.txt`) with icons and society art from `ck2plus_aio.zip`
     (`interface/li_CK2Plus_warrior_lodges.gfx`), modifiers `celtic_battle_cry`/`do_not_disturb`, notify events
     `PlusBuildings.001-010` (`events/li_CK2Plus_building_notify_events.txt`), loc `000_li_warrior_lodges.csv`
     (66 AIO keys + tooltips). In the lodge files `religion_openly_<x>_or_reformed_trigger` → `li_lodge_<x>_trigger`
     (other content keeps the shared triggers), `religion_group = pagan_group` → `li_lodge_any_trigger = yes`,
     `associated_religion` mapped to LI faiths (dievas, mande_pagan, hubal, bon, graeco_roman, amun); Celtic lines
     dropped from the Wolf Warriors, Egyptian/vanilla desert lines from the Keepers of the Flame; dead CK2Plus
     refs dropped (`machas_javelin`/`montu` weights, `ca_con_wall_6`, `martial_lady*` traits).
     `has_gender_equal_game_rule_trigger` defined as the gender rule `all`. `HF.12405` (battle bards) back on.
   - **Multi-line switch-offs (found 2026-11-15):** `phase8_hf.py` only undid switch-offs whose own line names the
     event, so calls step A had commented out as a block (`#character_event = { # <note>` / `#id = …` / `#}`)
     stayed off in parts 1-4: 70 blocks (duel, health, crusade, competition, bloodline and sainthood effects,
     CBs, job titles). `tools/phase8_multiline_off.py --keep-off=tools/phase8_keep_off.txt --apply` restored
     them (Northern Crusade `HF.49112` stays off). Also 4 master-era Holy Fury switch-offs in LI text restored
     (`HF.20024`, `HF.41300`, `HF.25631`, LI duel decision's `HFP.10095`). **Lesson:** `restore_ids.py` copies the
     AIO/CleanSlate line holding the ID, which is wrong when LI's line is a one-line call with another wrapper
     (it produced a bare `id =`, a `clear_delayed_event` and an unwrapped `letter_event`); those 3 were put back
     from the original commented line. A scan of every `id =` outside an event-call block found no other case.
   - **Phase 8 status:** parts 1-5 done (untested in game: part 5). Left out by decision: Holy Fury realm events,
     Reconquista, Teutonic/Livonian orders, Fourth/Northern Crusade, the Alexander/Teuta/Matilda quests.
   - **"Province 0" traced (2026-11-14).** Events looping over demesne provinces (VIET region checks, saint
     flavour) hit an invalid province. A temporary debug event (removed again) logged rulers holding a
     barony or county with no location: LI's populist revolt (`li_rebel_events_the_old_gods.txt`) created
     its rebel leader's title as a landless **county**, which CK2 does not support (same cause as
     `c_vesta_temple`). Original LI bug, on master too; now `tier = DUKE` like every other rebel title,
     and it was the only landless county/barony `create_title` in the mod. Lesson: `on_startup` fires for
     every character, so a once-per-game event needs a global-flag guard.
   - **Province numbers (2026-11-14).** LI renumbered parts of its map, so numeric province references written
     for vanilla's map can point elsewhere (vanilla 1513/1448 are river tiles in LI). Fixed: the Jade Dragon
     invasion spawn points in CleanSlate's `jd_chinese_war_events`/`jd_chinese_invasion_events` (vanilla
     counties LI lacks → LI's Kroran 1207, Chatigama 1572, Ganges delta 1309; 108 "Invalid province" lines);
     LI's own `religious_titles.txt` caliphate/holy-city requirements (Jerusalem 774→814, Medina 718→724,
     Baghdad 693→731, Damascus 809→755, Cordoba 181→192: original LI bug, 39 references); the Library of
     Alexandria fallback (802→999). Reviewed and fine: `00_province_triggers.txt` (126 references) is LI's own
     silk road list, already in LI's numbering (Venetia, Konstantinoupolis, Itil, Merv, Bagdad, the Tarim, the
     Indian Ocean and Mediterranean sea lanes; 1577/1578 are LI's silk route start points);
     `common/technology.txt`'s numbers are tech levels; the other audit hits are `trigger_switch` values or
     already LI-numbered. No further province-number fixes needed.

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
