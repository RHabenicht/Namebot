# SR1e-3e Namebot

Namebot generates names for Shadowrun characters, gangs, and businesses. Pick a language, a naming tradition, or a generator such as Geordi Gizmo.

## Use Namebot

- Find the slash commands, examples, and self-hosting steps in the [Discord guide](DISCORD.md).
- Run the generator on your computer with Python 3.10 or newer. [Local instructions](RUNNING.md)

The Discord adapter passed offline tests. The project’s test record lists live server testing as pending. [Validation results](VALIDATION.json)

## Name lists

The collection has **48,495 unique records** across 32 sets. The import merged 5,214 duplicate rows from 44 source files. The total includes name parts and other entries used by the procedural generators.

English uses one shared dataset with American, British, Australian, and New Zealand profiles. The last three include given names drawn from 2024 lists. Hawaiian, Khmer, and Filipino have sourced starter lists with their own name order. [Sources and coverage](ENRICHMENT.md)

The Roman Latin set follows first- and second-century citizen naming patterns. It uses separate programs for masculine and feminine names. [Roman Latin names](LATIN.md)

`Native American.nam` supplies an English word generator. The source gives no tribal or Indigenous-language attribution. The import keeps its table labels, blank entry, and the spelling `Squirel`.

## Data files

The name lists and generator rules are stored as UTF-8 JSON in `data/`. Names can appear in more than one language or regional set. The import keeps accents, distinct spellings, and source credits.

| File | Use |
| --- | --- |
| `catalog.json` | Look up sets, source files, and record counts. |
| [FORMAT.md](FORMAT.md) | Read the JSON format and duplicate rules. |
| [HANDOFF.md](HANDOFF.md) | Rebuild the data and check pending work. |
| `backup/source_tables.zip` | Inspect the source tables and repair history. |
| `tools/` | Run the generator, conversion scripts, and tests. |

## Name source credits

Names were collected from open sources found online. The credits below cover the imported tables.

| Sets | Credit |
| --- | --- |
| Ancient Greek, Basque, Egyptian, Finnish, Gang names, Halfling, Hindi, Indian, Native American | Gurth |
| Danish, Dutch, English, German, Irish, Italian, Japanese | Gurth and Joel Crook |
| Geordi Gizmo Company and Geordi Gizmo Technical | Joel Crook |
| Roman Latin | Christian Schwietzke and Nightlife |
