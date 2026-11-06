# Namebot JSON format, version 1

Each resource is a UTF-8 JSON file with `"format": "sr-namebot/1"`. Text values use Unicode NFC normalization.

## Resource fields

| Field | Meaning |
| --- | --- |
| `id` | Stable resource ID that matches its filename. |
| `label` | Display name of the language, naming tradition, or category. |
| `language` | Language tag. Use `und` when the source label leaves the language unspecified. |
| `kind` | `language` or `category`. |
| `status` | `imported` or `needs_source_data`. |
| `profiles` | Regional choices, selection tags, name order, and readiness. |
| `pools` | Unique names or components grouped by role. |
| `programs` | Generator rules stored as JSON nodes. |
| `sources` | Source filenames, encodings, hashes, and retained settings. |

## Pool records

Each record has `id`, `value`, `weight`, `genders`, `profiles`, `sources`, `variants`, and `source_occurrences`.

The `given` and `family` pools hold given names and surnames. A given name present in two source gender categories is stored once with both tags. Other pools hold nicknames, additions, and generator components.

The renderer gives each eligible person-name record the same chance of selection. `source_occurrences` counts the contributing source rows. All English profiles can use records tagged `shared`. The American profile also uses records tagged `american`.

A blank value can be a valid entry, such as an optional gang-name component or an absent surname.

## Programs and table modes

A program has an ID, prompts, definitions, an entrypoint, and a table map. Use `program_id/table_name` to refer to a table. Two programs can then use the same table name.

| Table mode | Contents |
| --- | --- |
| `pool` | Unique record IDs from a named pool, drawn with equal probability. |
| `dictionary` | Original keys mapped to pool record IDs. |
| `lookup` | Non-overlapping inclusive numeric ranges and result nodes. |
| `weighted` | Result nodes with positive integer weights. |

Every operation node has an `op` field.

| Operation | Purpose |
| --- | --- |
| `text`, `number` | Literal values. |
| `variable` | Read a named variable. |
| `dice`, `add` | Roll random integers or add values. |
| `concat` | Join child values in order. |
| `choice` | Choose among child values. |
| `roll`, `deck` | Draw from a table, repeat a draw, or draw without replacement. |
| `lookup` | Read a dictionary or table by key. |
| `compare`, `if` | Select a result based on a condition. |
| `transform` | Apply `proper` or `lower` to text. |

Program definitions and prompts set their variables before the entrypoint runs. A table’s `set` bindings run before result selection. See how `tools/namebot.py` handles whitespace, case, and decks. [Engine contract](RUNNING.md#engine-contract)

## Duplicate policy

Match records within the same resource and pool. Normalize to NFC, ignore case, trim and collapse whitespace, and treat straight and curly apostrophes as equivalent. Keep accents, distinct spellings, and alternative display forms.

Duplicate names and literal components share one record. Dictionary keys can point to the same record. For identical procedural alternatives, add their weights and keep one alternative.

## Sourced starter metadata

Optional `evidence` entries record a reference and the usage it documents. An empty `genders` list means the source left usage unspecified. Regional evidence can include the year and area covered. `locale` identifies a regional naming context independently of linguistic origin.

A profile with `name_order` and `program` selects a program with an explicit order. The Filipino maternal and paternal slots both draw from the family pool. English `regional_sample_programs` return given names from dated regional lists.

## References

- [JSON specification](https://www.rfc-editor.org/rfc/rfc8259)
- [Unicode normalization](https://www.unicode.org/reports/tr15/)
