# SR1e-3e Namebot — unified data

The working format is **UTF-8 JSON**. Name lists from different source formats now use the same record structure. The files are organized by language, naming tradition, or generator category.

- `data/` — harmonized names, regional profiles, and structured generator rules.
- `catalog.json` — file inventory, source accounting, and duplicate counts.
- `FORMAT.md` — the data contract.
- `VALIDATION.json` — completed checks and runtime work still pending.
- `HANDOFF.md` — the current state and next work for a fresh project chat.
- `backup/source_tables.zip` — preserved source tables and repair history.
- `tools/` — repeatable conversion and validation scripts.

The imported collection has **48,495 unique pool records** across 32 populated sets. It merges 5,214 duplicate rows from 44 source files. These totals include name components and generator vocabulary as well as personal names.

English uses one shared file with American, British, Australian, and New Zealand profiles. British, Australian, and New Zealand profiles now include dated regional samples. Hawaiian, Khmer, and Filipino contain sourced starter lists. See ENRICHMENT.md for coverage and naming rules.

Names that belong to more than one culture or region may appear in more than one set. Accented and genuinely different spellings remain separate. Source spelling variants and credits are preserved.

The data and references passed structural validation. A working Python command-line generator is included; see RUNNING.md for commands and runtime limits. The Discord adapter is implemented and tested offline; installation and live server testing remain pending. See DISCORD.md.

## Additional sources imported November 2, 2026

- `Native American.nam` populates `data/native_american_legacy.json` as an English component generator. The source gives no tribal or Indigenous-language attribution. Its table labels and blank entry are preserved, without treating the components as verified given names or surnames.
- The Native American source and its credits are retained. Source spelling `Squirel` is preserved.
- Hawaiian, Khmer and Filipino are now populated; details and limitations are in ENRICHMENT.md.

## Roman Latin replacement

The rejected `Latin.nam` has been removed from the bundled source archive and converter. `sources/latin_roman_source.json` now supplies `data/latin.json`; `tools/build_roman_latin.py` rebuilds it. The resource has 104 component records: 16 masculine praenomina, 24 masculine and 24 feminine nomina, and 20 masculine and 20 feminine cognomina. See `LATIN.md` for scope, sources, and usage.

Personal NAM lists support full-name composition, gender selection, and multiple given names. English regional profiles are selectable directly. See RUNNING.md for examples.

## Name source credits

Names were collected from open sources found online. The credits below cover the imported tables.

| Sets | Credit |
| --- | --- |
| Ancient Greek, Basque, Egyptian, Finnish, Gang names, Halfling, Hindi, Indian, Native American | Gurth |
| Danish, Dutch, English, German, Irish, Italian, Japanese | Gurth and Joel Crook |
| Geordi Gizmo Company and Geordi Gizmo Technical | Joel Crook |
| Roman Latin | Christian Schwietzke and Nightlife |
