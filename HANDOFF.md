# SR1e-3e Namebot

This is a separate Discord naming and random-table project. Keep it separate from SR1e-3eGamebot and its Python port. No Namebot GitHub repository, Discord application, or hosting service has been created in this work.

## User's goal

Generate personal names, street handles, NPCs, gangs, businesses, and eventually random items. The user has supplied legacy `.nam` and Inspiration Pad Pro `.ipt` files. The active request is to harmonize them into one format, remove duplicate entries, and organize them by language or naming tradition, with regional English profiles.

Project name: **SR1e-3e Namebot**.

## Current deliverable

- Format: UTF-8 JSON, identified by `"format": "sr-namebot/1"`.
- All 44 checked source files are accounted for: 18 NAM, 21 IPT, and five curated JSON sources.
- There are 32 populated JSON resources and no empty source slots.
- 53,709 input pool rows became 48,495 unique pool records. 5,214 duplicate rows were merged.
- Source-labelled gender categories, accents, alternative spellings, provenance, lookup keys, and explicit procedural weights are retained.
- Rules from IPT have been translated to structured JSON operation nodes. They are not stored as executable IPT strings.
- `catalog.json` lists resources and counts. `VALIDATION.json` records the checks actually run.
- `backup/source_tables.zip` preserves the corrected source collection and the original versions of repaired files.

## English profiles

`data/english.json` contains shared English data plus American, British, Australian, and New Zealand profiles. Shared names are stored once and selected by profile tags.

`American.nam` supplies American-labelled entries. The older `English.nam` explicitly says it mixes English and American names. Neither it nor `EnglishNames.ipt` establishes an exclusively British list. British, Australian, and New Zealand now have sourced 2024 given-name samples alongside shared English data. Coverage remains limited; no frequencies are inferred. See ENRICHMENT.md.

## Newly requested sets

- Hawaiian: `data/hawaiian.json`, language tag `haw`.
- Cambodian / Khmer: `data/khmer.json`, language tag `km`.
- Filipino: `data/filipino.json`, language tag `und`, locale `fil-PH`, because this national naming set has multiple linguistic origins. The spelling is **Filipino**.

These three now contain sourced starter entries and explicit name-order programs. Keep naming tradition, language, and region as separate concepts. Hawaiian is a distinct requested set; the New Zealand request is currently an English regional profile.

## Harmonization policy

- Merge duplicates within the same resource and semantic pool.
- Match Unicode NFC, case differences, surrounding/repeated whitespace, and straight/curly apostrophe differences.
- Keep accents and actual spelling differences: `Jose` and `José`, or `Weiss` and `Weiß`, remain distinct.
- Preserve display variants and source references on the merged record.
- A person-name record has weight 1 after merging; duplicate source rows do not increase its selection chance.
- Names can legitimately occur in different language or regional sets. Do not remove a name from one culture merely because another uses it.
- Preserve the keys of dictionaries, including paired Norse bynames and meanings. Repeated values may share one pool record while their original keys remain.
- Repeated procedural alternatives are combined by adding their explicit weights. This removes duplicate rows without discarding the rule's weighting.

## Important source distinctions

- Both Japanese IPT files are retained. `JapaneseName.ipt` contains stored names; `JapaneseNames.ipt` is a syllable generator with an additional stored male-name list. These remain separate selectable programs within `data/japanese.json`.
- Chinese English-style given names and nicknames have separate pools from Chinese given names.
- Gang NAM labels `MALE` and `FEMALE` describe legacy gang-name components, not character genders. The blank component is retained.
- Company and science generators share `data/technical_english.json`; table references remain scoped to each source program.
- Hindi/Indian/Egyptian/Scottish legacy labels are broad or mixed. Their files explicitly require classification review; do not silently relabel all entries as a single verified modern language.
- Dutch additions and defaults are preserved. Meanings of the legacy addition flags still need review before a new renderer uses them.
- Legacy female `*` output markers remain in compatibility program nodes. The standard person-name renderer should use the record's gender metadata rather than displaying those markers.

## Validation completed

`tools/validate_namebot_json.py` passed using only Python's standard library. It checked UTF-8 JSON parsing, duplicate object properties, pool uniqueness, NFC values, record IDs, source accounting, provenance, native operation names, all 4,820 rule nodes, per-program table references, dictionary keys, lookup overlap, positive weights, and regional English profile tags.

No comparison against the original Inspiration Pad Pro engine has been run. The native interpreter and command-line interface are implemented in tools/namebot.py. Runtime tests passed across 56 programs; see RUNNING.md. The Discord adapter is implemented and tested offline; do not describe the bot as deployed. See DISCORD.md.

## Next work

1. Expand the sourced starter sets as needed, especially gender-labelled Khmer given names.
2. Broaden regional English coverage and audit surnames; existing samples cover only selected 2024 birth lists.
3. The native JSON rule interpreter is implemented. The personal-name renderer now handles all 16 NAM personal source programs, optional gender and given-name count, plus English regional profiles. Dutch title/addition flags remain unapplied pending verification.
4. Runtime generation checks now pass, including Old Norse and procedural Japanese. Compare exact behavior against the original engine when available.
5. Discord commands are implemented. Configure the separate Namebot application and hosting, then perform live server checks from DISCORD.md. Keep all Namebot work separate from dicebot.

Preserve source credits. Do not add generated-by or tool/assistant authorship branding to project files, commits, or public documentation.

## Rebuild and validate

From this package's root:

```sh
python tools/convert_namebot_json.py --source backup/source_tables.zip --output .
python tools/validate_namebot_json.py .
python tools/check_roman_latin.py
python tools/check_enrichment.py
```

## Additional sources imported November 2, 2026

- `Native American.nam` populates `data/native_american_legacy.json` as an English component generator. The source gives no tribal or Indigenous-language attribution. Its table labels and blank entry are preserved, without treating the components as verified given names or surnames.
- The Native American source and its credits are retained. Source spelling `Squirel` is preserved.
- Hawaiian, Khmer and Filipino are now populated; details and limitations are in ENRICHMENT.md.

## Roman Latin replacement

The rejected `Latin.nam` has been removed from the bundled source archive and converter. `sources/latin_roman_source.json` now supplies `data/latin.json`; `tools/build_roman_latin.py` rebuilds it. The resource has 104 component records: 16 masculine praenomina, 24 masculine and 24 feminine nomina, and 20 masculine and 20 feminine cognomina. See `LATIN.md` for scope, sources, and usage.
