# Run Namebot locally

Requires Python 3.10 or newer. No external packages, Discord account, database, or network connection are needed. Extract the ZIP and open a terminal in the extracted package folder.

List available resources and programs:

```sh
python -X utf8 tools/namebot.py --list
python -X utf8 tools/namebot.py latin --list
```

Generate names:

```sh
python -X utf8 tools/namebot.py latin --program roman_male --count 10
python -X utf8 tools/namebot.py hawaiian --program hawaiian_all --count 10
python -X utf8 tools/namebot.py khmer --program khmer_all --count 10
python -X utf8 tools/namebot.py filipino --program filipino_all --count 10
python -X utf8 tools/namebot.py old_norse --prompt prompt1=Female --count 10
python -X utf8 tools/namebot.py japanese --program japanesenames --count 10
```

Use `--seed 42` to repeat a sequence. Each generated result resets variables and decks while continuing the random sequence. Choose a program explicitly when a resource has several. Regional English sample programs return given names only.

Legacy NAM sources can now generate personal names with `--full-name`. Choose a source program when there are several, and optionally select gender or 1–3 distinct given names. Omitted gender selects uniformly from the deduplicated union of male and female source entries. No surname is invented when the source has none.

```sh
python -X utf8 tools/namebot.py english --program american --full-name --gender female --count 10
python -X utf8 tools/namebot.py japanese --program japanese --full-name --gender male --count 10
python -X utf8 tools/namebot.py dutch --program dutch --full-name --given-count 2 --count 10
python -X utf8 tools/namebot.py basque --full-name --count 10
python -X utf8 tools/namebot.py english --profile british --gender female --count 10
```

English profiles combine eligible shared and regional given names with eligible shared surnames. They do not restrict output to the dated regional top-name samples. Source-specific NAM composition stays within the selected source. Dutch title/addition flags and legacy default counts are not applied automatically; one given name is the default, and `--given-count` is explicit.

Gang and Native American legacy word generators remain component-only. Their legacy male/female labels are not treated as personal-name genders. Individual tables are still available:

```sh
python -X utf8 tools/namebot.py english --list
python -X utf8 tools/namebot.py english --program american --table american/MALE --count 10
```

An empty table produces an explanatory error. An intentional empty entry remains a possible blank component. The count limit is 1–1,000 results per invocation.

## Engine contract

The engine executes all operation types present in the bundle: text, numbers, variables, dice, addition, concatenation, choice, rolls, decks, dictionary/range lookups, comparisons, conditionals and case transforms. It never evaluates source strings as code.

Assignments evaluate in order and trim outer whitespace; internal spaces remain. This allows the padded Old Norse gender assignments to match their conditions. Concatenation inserts no implicit separator. Final output trims outer whitespace only. Legacy female asterisk markers remain in compatibility output.

Pool selection is uniform over unique entries. Weighted alternatives use integer weights. A deck removes one ticket per draw, with weighted alternatives represented by their weights, and refills upon exhaustion; it resets per generated result. Dictionary random selection is over keys. Missing keys and uncovered ranges fail explicitly. `proper` uses Python Unicode title casing and `lower` uses Unicode lowercase.

These are the native engine's documented semantics. Exact whitespace, capitalization and deck parity with Inspiration Pad Pro have not been verified against the original executable. NAM personal-name composition is implemented for 16 source programs. Dutch addition flags still need verification; no automatic titles are attached. The command line is functional; The Discord adapter is implemented and tested offline; hosting and live server tests remain pending. See DISCORD.md.

## Verification

```sh
python -X utf8 tools/test_runtime.py
python -X utf8 tools/test_renderer.py
python -X utf8 tools/validate_namebot_json.py .
python -X utf8 tools/check_roman_latin.py
python -X utf8 tools/check_enrichment.py
```

Runtime integration checks cover 56 programs and 94 entrypoints/component tables: 9,200 outputs plus expected rejection of two empty component tables. Additional checks cover Old Norse gender selection and seeded repeatability, deck depletion/refill, weighted tickets, dictionary/range boundaries, state reset, lazy conditionals, invalid inputs and recursion limits. Tests ran in the development environment; Windows execution and Discord integration have not been tested.

The personal-name renderer passed 2,400 source-membership and ordering checks across 16 NAM personal source programs, plus 400 English regional-profile checks. Regression tests cover absent surnames, multiword components, multiple given names, rejected component-generator misuse and conflicting command-line controls.
