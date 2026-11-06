# Namebot maintenance notes

This repository holds the name lists, Python generator, and Discord adapter for SR1e-3e Namebot. The Discord application is listed as **Namebot**. [Discord setup](DISCORD.md#host-your-own-copy)

## Source import

The import combined 44 files into 32 UTF-8 JSON resources using `sr-namebot/1`. The inputs were 18 NAM files, 21 IPT files, and five curated JSON sources. Of 53,709 input rows, 5,214 were duplicates, leaving 48,495 unique pool records.

IPT rules become JSON operation nodes. The import keeps source-labelled gender categories, accents, spelling variants, table keys, and explicit procedural weights. `catalog.json` lists the sets and counts. `backup/source_tables.zip` preserves the source collection and the original versions of repaired files. [Format and duplicate rules](FORMAT.md)

## Source distinctions

- `data/english.json` stores shared entries once and uses profile tags for American, British, Australian, and New Zealand selections. `American.nam` supplies American-labelled entries. `English.nam` mixes English and American names. The British, Australian, and New Zealand additions come from selected 2024 birth-name lists. [Regional sources](ENRICHMENT.md#english-regional-samples)
- Hawaiian uses language tag `haw` and Khmer uses `km`. The Filipino set uses `und` with locale `fil-PH` because its entries have several linguistic origins. Each set has a program for its name order. [Starter sources](ENRICHMENT.md)
- `JapaneseName.ipt` supplies stored names. `JapaneseNames.ipt` generates names from syllables and includes a separate stored male-name table. Pick the corresponding program in `data/japanese.json`.
- Chinese given names, English-style given names, and nicknames use separate pools.
- The gang NAM files use `MALE` and `FEMALE` as table labels for word components. The Native American NAM file supplies an English word generator with no specific tribal or language attribution. The import keeps its original labels, blank component, and spelling `Squirel`.
- The company and technical generators share `data/technical_english.json`. Each program keeps its own table references.
- The legacy Hindi, Indian, Egyptian, and Scottish labels need classification review. Keep the original labels and recorded scope until that review is complete.
- The import preserves Dutch addition flags and default counts for later verification. Compatibility programs keep the legacy female `*` marker. The personal-name renderer uses the record’s gender tags.
- `sources/latin_roman_source.json` replaced the mixed Latin import. It contains 104 elements. Run `tools/build_roman_latin.py` to rebuild `data/latin.json`. [Roman naming programs](LATIN.md)

## Checks on record

`tools/validate_namebot_json.py` checked UTF-8 parsing, duplicate properties, pool uniqueness, normalized values, IDs, source references, and all 4,820 operation nodes. It checked table references, dictionary keys, range overlap, weights, and English profile tags.

Runtime checks covered 56 programs. The personal-name renderer supports 16 NAM source programs with gender selection and given-name counts, as well as the English regional profiles. Exact behavior against the original Inspiration Pad Pro executable, Windows execution, and live Discord testing remain open. [Validation results](VALIDATION.json)

## Rebuild and validate

Run these commands from the project root.

```sh
python tools/convert_namebot_json.py --source backup/source_tables.zip --output .
python tools/validate_namebot_json.py .
python tools/check_roman_latin.py
python tools/check_enrichment.py
```

## Next work

1. Expand the starter lists, especially Khmer given names with explicit gender labels.
2. Broaden the regional English samples and audit surname coverage.
3. Verify the Dutch title and addition flags and compare native output with the original engine.
4. Verify a hosted Discord instance with the server checks in the [Discord guide](DISCORD.md#check-a-deployment).

Keep the source credits with each import. [Name source credits](README.md#name-source-credits)
