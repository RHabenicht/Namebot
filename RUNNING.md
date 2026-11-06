# Run Namebot locally

The command-line generator uses the standard library in Python 3.10 or newer and runs offline. Open a terminal in the project folder that contains `tools/` and `data/`.

## List sets and generate names

List the sets, or list the programs and tables in a set.

```sh
python -X utf8 tools/namebot.py --list
python -X utf8 tools/namebot.py latin --list
```

Pick a program when a set offers several. These commands generate ten results each.

```sh
python -X utf8 tools/namebot.py latin --program roman_male --count 10
python -X utf8 tools/namebot.py hawaiian --program hawaiian_all --count 10
python -X utf8 tools/namebot.py khmer --program khmer_all --count 10
python -X utf8 tools/namebot.py filipino --program filipino_all --count 10
python -X utf8 tools/namebot.py old_norse --prompt prompt1=Female --count 10
python -X utf8 tools/namebot.py japanese --program japanesenames --count 10
```

`--count` accepts 1–1,000 results per run. Use `--seed 42` to repeat the same sequence. Each result starts with fresh variables and decks, then continues from the previous result’s random state.

## Personal names

Use `--full-name` to combine given names and surnames from a NAM personal-name source. The renderer defaults to one given name. Use `--given-count` to pick up to three distinct given names. If you leave `--gender` blank, each unique entry from the male and female given-name pools has the same chance of selection. A source without surnames returns given names alone.

```sh
python -X utf8 tools/namebot.py english --program american --full-name --gender female --count 10
python -X utf8 tools/namebot.py japanese --program japanese --full-name --gender male --count 10
python -X utf8 tools/namebot.py dutch --program dutch --full-name --given-count 2 --count 10
python -X utf8 tools/namebot.py basque --full-name --count 10
python -X utf8 tools/namebot.py english --profile british --gender female --count 10
```

An English profile draws given names from the shared pool and any entries tagged for the selected region. It also draws from eligible shared surnames. The dated regional sample programs return given names only. Dutch names also use the `--given-count` setting. The source’s title flags, addition flags, and default counts are retained for verification.

## Component tables

Gang and Native American word generators use their legacy labels to select components. Use a table directly when you want one kind of entry.

```sh
python -X utf8 tools/namebot.py english --list
python -X utf8 tools/namebot.py english --program american --table american/MALE --count 10
```

An empty table returns an error. A table with an intentional blank entry can still return that component.

## Engine contract

The interpreter reads the JSON operation nodes and treats source strings as data. [Operation reference](FORMAT.md#programs-and-table-modes)

Assignments run in order and trim whitespace at the edges of each value. Internal spaces stay in place. This lets padded Old Norse gender assignments match their conditions. Concatenation joins values directly. Compatibility output keeps the legacy female asterisk. The engine trims the edges of the finished result.

Each unique record in a pool has an equal chance of selection. Weighted alternatives use integer tickets. A deck removes one ticket per draw, refills when empty, and resets for each generated result. Random dictionary draws select a key. A missing key or uncovered range produces an error. `proper` uses Python’s Unicode title casing and `lower` uses its Unicode lowercase conversion.

## Verification

```sh
python -X utf8 tools/test_runtime.py
python -X utf8 tools/test_renderer.py
python -X utf8 tools/validate_namebot_json.py .
python -X utf8 tools/check_roman_latin.py
python -X utf8 tools/check_enrichment.py
```

The recorded integration tests covered 56 programs and 94 entrypoints or component tables. They checked 9,200 outputs and verified that two empty tables returned errors. Runtime regression tests cover Old Norse gender selection, seeded repeatability, weighted decks, dictionary and range boundaries, state reset, lazy conditionals, invalid input, and recursion limits.

The renderer passed 2,400 source-membership and ordering checks across 16 NAM programs, plus 400 checks for English profiles. Its regression tests cover absent surnames, multiword components, multiple given names, rejection of component generators as personal-name sources, and conflicting controls.

The checks ran in the development environment. Windows execution, live Discord testing, and exact output parity with Inspiration Pad Pro remain open. [Validation results](VALIDATION.json)
