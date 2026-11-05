# Sourced starter additions

These are curated samples for fictional names, not exhaustive cultural directories or guarantees that every random combination is historically attested. Each source JSON includes selected records, reference URLs, scope and attribution. The resulting data retains reference evidence and source hashes.

| Set | Given records | Family records | Output order |
| --- | ---: | ---: | --- |
| Hawaiian | 40 | 30 | Given, family |
| Khmer | 42 | 29 | Family, given |
| Filipino | 30 | 20 | Given, maternal family, paternal family |

Hawaiian spelling preserves the ʻokina and macrons present in the selected sources. Gender tags reflect source observations, not exclusive usage.

Khmer entries retain romanized spelling. An empty gender list means unknown, not unisex. Unfiltered output uses all entries; male and female filters use only explicitly labelled examples, so their pools are small.

Filipino is the correct spelling for the language/national descriptor; Philippines uses “Ph”. This dataset is a national naming category of mixed linguistic origin. Its selected full-name pattern uses a maternal family name as the middle element and a paternal family name last. This is one common pattern, not a universal rule. Family elements are drawn independently; the generator does not establish actual genealogy. Multiword given names and surnames remain intact.

## English regional samples

British additions combine England/Wales and Scotland lists; they do not cover all Britain uniformly. Australian additions are a New South Wales sample. New Zealand additions use national lists. All are dated 2024 birth-name samples, not predictions for Shadowrun's fictional years.

The six regional sample programs return given names only, filtered by source gender category. Standard English profiles also retain shared names and surnames; surnames have not received a regional audit. Duplicate observations add provenance, not selection weight.

## Sources and reuse

See `sources/hawaiian_source.json`, `sources/khmer_source.json`, `sources/filipino_source.json`, and `sources/english_regional_source.json` for direct source links, authors where recorded, dates and selection notes. Wikipedia/Wiktionary references retain contributor attribution and CC BY-SA 4.0 notices; consult the linked source histories for contributors. These additions do not relicense the bundled legacy material.

## Checks and limits

`tools/check_enrichment.py` checks source membership, gender selection, ordering, unique table entries, equal record weights, Hawaiian spelling, and exhaustive output expansion for the 15 simple programs. This is a restricted validation evaluator, not the full legacy generator runtime. Original-engine parity and Discord integration remain untested.
