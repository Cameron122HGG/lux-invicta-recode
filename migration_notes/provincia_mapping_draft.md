# Roman provincia restoration: draft mapping onto LI duchies

Draft for review (2026-11-15). Built by comparing LI's map with vanilla's (`provinces.bmp`, local fit from 989 counties that share a key),
then reading which CK2Plus provincia the matching vanilla county belongs to. A duchy is listed where most of its counties fall in that
provincia. Entries marked **manual** are my judgment where the comparison failed or split (see the note).

Each provincia becomes a titular kingdom `k_provincia_<name>`; creating it needs full control of the listed duchies and moves them de jure
under the new kingdom (CK2Plus behaviour). Sardinia et Corsica is folded into Italia (user, 2026-11-15), so there are 20 provincias.
Usable by the Eastern/Western successor (e_byzantium / e_roman at start) and e_roman_empire.

## Aegyptus (`k_provincia_aegyptus`), 6 duchies

| LI duchy | name | LI kingdom | note |
|---|---|---|---|
| `d_alexandria` | Alexandria | `k_egypt` Ægyptus |  |
| `d_cairo` | Cairo | `k_egypt` Ægyptus |  |
| `d_damietta` | Damietta | `k_egypt` Ægyptus |  |
| `d_sinai` | Sinai | `k_judea` Judah |  |
| `d_cyrenaica` | Cyrenaica | `k_kyrene` Kyrene |  |
| `d_aswan` | Aswan | `k_nubia` Makuria |  |

## Africa (`k_provincia_africa`), 3 duchies

| LI duchy | name | LI kingdom | note |
|---|---|---|---|
| `d_tripolitania` | Tripolitania | `k_africa` Africa |  |
| `d_tunis` | Carthage | `k_carthage` Carthage |  |
| `d_kabylia` | Kabylia | `k_numidia` Numidia |  |

## Armenia (`k_provincia_armenia`), 6 duchies

| LI duchy | name | LI kingdom | note |
|---|---|---|---|
| `d_albania` | Albania | `k_albania` Albania | **manual**: split; CK2Plus has Caucasian Albania |
| `d_armenia` | Ayrarat | `k_armenia` Hayasdan |  |
| `d_provincia_mesopotamia` | Mesopotamia | `k_armenia` Hayasdan |  |
| `d_vaspurakan` | Vaspurakan | `k_armenia` Hayasdan |  |
| `d_abkhazia` | Apkhazeti | `k_georgia` Sak'art'velos |  |
| `d_kartli` | Kartli | `k_georgia` Sak'art'velos |  |

## Britannia (`k_provincia_britannia`), 16 duchies

| LI duchy | name | LI kingdom | note |
|---|---|---|---|
| `d_somerset` | Sumortunsæte | `k_dumnonia` Dumnonia |  |
| `d_canterbury` | Cantware | `k_england` Anglia |  |
| `d_middlesex` | Middelseaxna | `k_england` Anglia |  |
| `d_norfolk` | Iceni Magni | `k_england` Anglia |  |
| `d_hwicce` | Hwicce | `k_mercia` Mercia |  |
| `d_lindsey` | Lindesege | `k_mercia` Mercia |  |
| `d_magonsaete` | Magonsæte | `k_mercia` Mercia |  |
| `d_middle_angles` | Middil Engli | `k_mercia` Mercia |  |
| `d_bernicia` | Beornice | `k_northumbria` Norþhymbra |  |
| `d_derenrice` | Derenrice | `k_northumbria` Norþhymbra |  |
| `d_cumbria` | Cumbria | `k_rheged` Rheged |  |
| `d_dyfed` | Dyfed | `k_wales` Cymru |  |
| `d_glywysing` | Morgannwg | `k_wales` Cymru |  |
| `d_gwynedd` | Gwynedd | `k_wales` Cymru |  |
| `d_powys` | Powys | `k_wales` Cymru |  |
| `d_belgarum` | Venta Belgarum | `k_wessex` Westseaxna |  |

## Caledonia (`k_provincia_caledonia`), 7 duchies

| LI duchy | name | LI kingdom | note |
|---|---|---|---|
| `d_ce` | Ce | `k_fortriu` Fortriu |  |
| `d_fidach` | Fidach | `k_fortriu` Fortriu |  |
| `d_sudreyjar` | Suðreyjar | `k_orkney` Orkneyjar |  |
| `d_fiobha` | Fìobha | `k_scotland` Alba | **manual**: split; by key |
| `d_galloway` | Na Renna | `k_scotland` Alba |  |
| `d_labhdaidh` | Labhdaidh | `k_scotland` Alba |  |
| `d_srathchluaidh` | Gallgaidelaib | `k_scotland` Alba |  |

## Gallia (`k_provincia_gallia`), 17 duchies

| LI duchy | name | LI kingdom | note |
|---|---|---|---|
| `d_koln` | Köln | `k_austrasia` Austrasia |  |
| `d_luxembourg` | Luxembourg | `k_austrasia` Austrasia |  |
| `d_brabant` | Brabant | `k_belgica` Belgica |  |
| `d_flanders` | Flanders | `k_belgica` Belgica |  |
| `d_brittany` | Brittany | `k_brittany` Armorica |  |
| `d_burgundy` | Burgundy | `k_burgundy` Burgundia |  |
| `d_savoie` | Sapaudia | `k_burgundy` Burgundia |  |
| `d_upper_burgundy` | Upper Burgundy | `k_burgundy` Burgundia |  |
| `d_champagne` | Champagne | `k_france` Francia |  |
| `d_valois` | Valois | `k_france` Francia |  |
| `d_alsace` | Alsace | `k_lotharingia` Middle Francia |  |
| `d_upper_lorraine` | Upper Lorraine | `k_lotharingia` Middle Francia |  |
| `d_anjou` | Andegavia | `k_neustria` Neustria |  |
| `d_berry` | Berry | `k_neustria` Neustria |  |
| `d_orleans` | Orleans | `k_neustria` Neustria |  |
| `d_normandy` | Normandy | `k_normandy` Normania |  |
| `d_rouen` | Rouen | `k_normandy` Normania |  |

## Germania (`k_provincia_germania`), 18 duchies

| LI duchy | name | LI kingdom | note |
|---|---|---|---|
| `d_bavaria` | Bavaria | `k_bavaria` Bavaria |  |
| `d_tyrol` | Tyrol | `k_bavaria` Bavaria |  |
| `d_bohemia` | Bohemia | `k_bohemia` Bohemia |  |
| `d_holstein` | Holstein | `k_denmark` Danmark |  |
| `d_slesvig` | Slesvig | `k_denmark` Danmark |  |
| `d_gelre` | Gelre | `k_frisia` Frisia |  |
| `d_holland` | Holland | `k_frisia` Frisia |  |
| `d_nordmark` | Nordmark | `k_frisia` Frisia |  |
| `d_baden` | West Schwabia | `k_germany` Germania |  |
| `d_brunswick` | Brunswick | `k_germany` Germania |  |
| `d_franconia` | Franconia | `k_germany` Germania |  |
| `d_swabia` | Swabia | `k_germany` Germania |  |
| `d_thuringia` | Thüringia | `k_germany` Germania |  |
| `d_lower_lorraine` | Lower Lorraine | `k_lotharingia` Middle Francia |  |
| `d_moravia` | Moravia | `k_moravia` Velká Morava |  |
| `d_brandenburg` | Brandenburg | `k_wendia` Wendia |  |
| `d_meissen` | Meissen | `k_wendia` Wendia |  |
| `d_saxony` | Saxony | `k_wendia` Wendia |  |

## Hibernia (`k_provincia_hibernia`), 7 duchies

| LI duchy | name | LI kingdom | note |
|---|---|---|---|
| `d_breifne` | Bréifne | `k_ireland` Éire |  |
| `d_connacht` | Connacht | `k_ireland` Éire |  |
| `d_laigin` | Laigin | `k_ireland` Éire |  |
| `d_meath` | Mide | `k_ireland` Éire |  |
| `d_munster` | Muman | `k_ireland` Éire |  |
| `d_osraige` | Osraige | `k_ireland` Éire |  |
| `d_ulaid` | Ulaid | `k_ireland` Éire |  |

## Hispania (`k_provincia_hispania`), 18 duchies

| LI duchy | name | LI kingdom | note |
|---|---|---|---|
| `d_cordoba` | Cordoba | `k_andalusia` Andalusia |  |
| `d_granada` | Granada | `k_andalusia` Andalusia |  |
| `d_sevilla` | Seville | `k_andalusia` Andalusia |  |
| `d_barcelona` | Barcelona | `k_aragon` Valentia |  |
| `d_mallorca` | Balearica | `k_aragon` Valentia |  |
| `d_murcia` | Carthago Nova | `k_aragon` Valentia |  |
| `d_valencia` | Valentia | `k_aragon` Valentia |  |
| `d_asturias` | Asturias | `k_asturias` Asturias |  |
| `d_castilla` | Castille | `k_castille` Celdebra |  |
| `d_badajoz` | Badajoz | `k_leon` Legio |  |
| `d_leon` | León | `k_leon` Legio |  |
| `d_navarra` | Navarra | `k_navarra` Cantabria |  |
| `d_algarve` | Algarve | `k_portugal` Lusitania |  |
| `d_beja` | Beja | `k_portugal` Lusitania |  |
| `d_galicia` | Galicia | `k_spanish_galicia` Suevia |  |
| `d_porto` | Portucale | `k_spanish_galicia` Suevia |  |
| `d_toledo` | Toledo | `k_toledo` Toledo |  |
| `d_aragon` | Aragon | `k_visigoths` Gothia |  |

## Illyricum (`k_provincia_illyricum`), 7 duchies

| LI duchy | name | LI kingdom | note |
|---|---|---|---|
| `d_bosnia` | Bosnia | `k_croatia` Illyria |  |
| `d_croatia` | Croatia | `k_croatia` Illyria |  |
| `d_dalmatia` | Dalmatia | `k_croatia` Illyria |  |
| `d_slavonia` | Slavonia | `k_croatia` Illyria |  |
| `d_dioclea` | Duklja | `k_serbia` Serbia |  |
| `d_rashka` | Rashka | `k_serbia` Serbia |  |
| `d_carinthia` | Aquileia | `k_venice` Venetia |  |

## Italia (`k_provincia_italia`), 19 duchies

| LI duchy | name | LI kingdom | note |
|---|---|---|---|
| `d_genoa` | Liguria | `k_genoa` Genoa | **manual**: map split Italia/Viennensis; Liguria |
| `d_pedemontium` | Pedemontium | `k_genoa` Genoa |  |
| `d_ancona` | Ancona | `k_italy` Italia |  |
| `d_ferrara` | Ferraria | `k_italy` Italia |  |
| `d_latium` | Latium | `k_italy` Italia |  |
| `d_pisa` | Pisa | `k_italy` Italia |  |
| `d_spoleto` | Spoleto | `k_italy` Italia |  |
| `d_toscana` | Tuscany | `k_italy` Italia |  |
| `d_lombardia` | Lombardy | `k_lombardia` Lombardia |  |
| `d_modena` | Modena | `k_lombardia` Lombardia |  |
| `d_apulia` | Apulia | `k_sicily` Magna Græcia |  |
| `d_benevento` | Benevento | `k_sicily` Magna Græcia |  |
| `d_calabria` | Calabria | `k_sicily` Magna Græcia |  |
| `d_capua` | Capua | `k_sicily` Magna Græcia |  |
| `d_salerno` | Salerno | `k_sicily` Magna Græcia |  |
| `d_sicily` | Sicily | `k_siracusa` Siracusa |  |
| `d_venice` | Venice | `k_venice` Venetia | **manual**: map: county on sea tile |
| `d_verona` | Verona | `k_venice` Venetia |  |
| `d_sardinia` | Sardinia | `k_italy` Italia | **manual**: CK2Plus's Sardinia et Corsica folded into Italia (user) |

## Macedonia (`k_provincia_macedonia`), 8 duchies

| LI duchy | name | LI kingdom | note |
|---|---|---|---|
| `d_dyrrachion` | Dyrrachion | `k_epirus` Epirus |  |
| `d_nikopolis` | Nikopolis | `k_epirus` Epirus |  |
| `d_athens` | Athenai | `k_greece` Ellada |  |
| `d_hellas` | Ellas | `k_greece` Ellada |  |
| `d_krete` | Krete | `k_krete` Krete |  |
| `d_lychnidos` | Lychnidos | `k_macedonia` Makedonia |  |
| `d_thessalonika` | Thessaloníki | `k_macedonia` Makedonia |  |
| `d_achaia` | Peloponnesos | `k_sparta` Sparta |  |

## Mauretania (`k_provincia_mauretania`), 6 duchies

| LI duchy | name | LI kingdom | note |
|---|---|---|---|
| `d_alger` | Alger | `k_mauretania` Mauretania |  |
| `d_fes` | Fes | `k_mauretania` Mauretania |  |
| `d_marrakech` | Marrakech | `k_mauretania` Mauretania |  |
| `d_sijilmasa` | Sijilmasa | `k_mauretania` Mauretania | **manual**: split; by key |
| `d_tangiers` | Tangier | `k_mauretania` Mauretania |  |
| `d_tlemcen` | Tlemcen | `k_mauretania` Mauretania |  |

## Mesopotamia (`k_provincia_mesopotamia`), 7 duchies

| LI duchy | name | LI kingdom | note |
|---|---|---|---|
| `d_kermanshah` | Kirmanshah | `k_media` Media | **manual**: by key; split |
| `d_kurdistan` | Kurdistan | `k_media` Media | **manual**: by key |
| `d_baghdad` | Bagdad | `k_mesopotamia` Mesopotamia | **manual**: by key (Middle East renumbered) |
| `d_basra` | Al-Basrah | `k_mesopotamia` Mesopotamia | **manual**: by key |
| `d_mosul` | Mûsil | `k_mesopotamia` Mesopotamia |  |
| `d_tigris` | Idigina | `k_mesopotamia` Mesopotamia | **manual**: by key |
| `d_susa` | Susa | `k_persia` Pârsa |  |

## Pannonia et Dacia (`k_provincia_pannonia_dacia`), 9 duchies

| LI duchy | name | LI kingdom | note |
|---|---|---|---|
| `d_esztergom` | Strigonium | `k_avars` Avaria |  |
| `d_pecs` | Lower Pannonia | `k_avars` Avaria |  |
| `d_osterreich` | Austria | `k_bavaria` Bavaria | **manual**: split Germania/Pannonia (Noricum) |
| `d_moldau` | Moldova | `k_dacia` Dacia | **manual**: split; CK2Plus has Moldavia |
| `d_temes` | Temes | `k_dacia` Dacia |  |
| `d_wallachia` | Tara Romaneasca | `k_dacia` Dacia |  |
| `d_pest` | Pannonia | `k_hungary` Hungaria |  |
| `d_ungvar` | Ungvar | `k_hungary` Hungaria |  |
| `d_nyitra` | Nitra | `k_moravia` Velká Morava |  |

## Phrygia (`k_provincia_phrygia`), 5 duchies

| LI duchy | name | LI kingdom | note |
|---|---|---|---|
| `d_nikaea` | Nikaea | `k_byzantium` Romania |  |
| `d_anatolia` | Anatolia | `k_isauria` Isauria |  |
| `d_cibyrrhaeot` | Cibyrrhaeot | `k_isauria` Isauria | **manual**: split; by key |
| `d_thracesia` | Thrakesion | `k_isauria` Isauria |  |
| `d_samos` | Samos | `k_pergamon` Pergamon |  |

## Pontus (`k_provincia_pontus`), 5 duchies

| LI duchy | name | LI kingdom | note |
|---|---|---|---|
| `d_charsianon` | Charsianon | `k_galatia` Galatia |  |
| `d_kappadokia` | Kappadokia | `k_galatia` Galatia |  |
| `d_armeniacon` | Pontos | `k_pontus` Pontos |  |
| `d_paphlagonia` | Paphlagonia | `k_pontus` Pontos |  |
| `d_trebizond` | Trebizond | `k_trebizond` Trebizond |  |

## Syria Palaestina (`k_provincia_syria_palaestina`), 11 duchies

| LI duchy | name | LI kingdom | note |
|---|---|---|---|
| `d_damascus` | Qsar Bardawil | `k_amman` Amman |  |
| `d_edessa` | Edessa | `k_armenia` Hayasdan |  |
| `d_armenia_minor` | Kilikia | `k_cilicia` Kilikia |  |
| `d_seleukia` | Seleukia | `k_isauria` Isauria |  |
| `d_ascalon` | Ascalon | `k_judea` Judah |  |
| `d_galilee` | Galilee | `k_judea` Judah |  |
| `d_jerusalem` | Jerusalem | `k_judea` Judah |  |
| `d_arabia_petrae` | Arabia Petraea | `k_nabatea` Nabatea | **manual**: 3/7 counties |
| `d_aleppo` | Palmyra | `k_palmyra` Palmyra |  |
| `d_antioch` | Antioch | `k_syria` Antioch |  |
| `d_tripoli` | Tripoli | `k_syria` Antioch |  |

## Thracia (`k_provincia_thracia`), 5 duchies

| LI duchy | name | LI kingdom | note |
|---|---|---|---|
| `d_karvuna` | Karvuna | `k_bulgaria` Bulgaria |  |
| `d_turnovo` | Tylis | `k_bulgaria` Bulgaria |  |
| `d_vidin` | Vidin | `k_bulgaria` Bulgaria |  |
| `d_thrace` | Thrace | `k_byzantium` Romania | **manual**: map: Constantinople not matched |
| `d_makedonia` | Makedonía | `k_macedonia` Makedonia |  |

## Viennensis (`k_provincia_viennensis`), 9 duchies

| LI duchy | name | LI kingdom | note |
|---|---|---|---|
| `d_aquitaine` | Aquitaine | `k_aquitaine` Aquitaine |  |
| `d_bourbon` | La Marche | `k_aquitaine` Aquitaine |  |
| `d_gascogne` | Vasconia | `k_aquitaine` Aquitaine |  |
| `d_poitou` | Pictavia | `k_aquitaine` Aquitaine |  |
| `d_dauphine` | Dauphiné | `k_arles` Arles |  |
| `d_provence` | Provence | `k_arles` Arles |  |
| `d_auvergne` | Arvernia | `k_septimania` Septimania |  |
| `d_septimania` | Septimania | `k_septimania` Septimania |  |
| `d_toulouse` | Toulouse | `k_septimania` Septimania |  |

## Not assigned (outside every provincia or too split)

`d_garama` (Fezzan, 1 of 3 counties in Africa), `d_mecklemburg`, `d_lesser_poland`, `d_silesia` (mostly outside Germania/Pannonia),
`d_aydhab`, `d_napata`, `d_dongola` (Nubia beyond Aswan), `d_ouadane`, `d_canarias`, `d_cherson`, `d_derbent`, `d_skane`, `d_sjaelland`, Scandinavia, the
Baltic and everything east of Mesopotamia.
