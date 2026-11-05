# Namebot JSON format, version 1

Every active data resource is UTF-8 JSON with `"format": "sr-namebot/1"`. JSON is a language-independent structured format; the data can be read by Python or JavaScript. Text values use Unicode NFC normalization.

## Resource fields

| Field | Meaning |
| --- | --- |
| `id` | Stable resource identifier, matching its filename. |
| `label` | Display name of the language, naming tradition, or category. |
| `language` | Language tag; `und` means the source label does not establish a specific language. |
| `kind` | `language` or `category`. |
| `status` | `imported` or `needs_source_data`. |
| `profiles` | Regional choices, selection tags, name order, and readiness. |
| `pools` | Unique name or component records, separated by role. |
| `programs` | Generator instructions expressed as structured JSON. |
| `sources` | Source filenames, encodings, hashes, and retained settings. |

## Pool records

Each record has `id`, `value`, `weight`, `genders`, `profiles`, `sources`, `variants`, and `source_occurrences`.

The principal person-name pools are `given` and `family`. Gender values retain the source's categories. A given name present in both source categories is stored once with both tags. Additional pools hold nicknames, additions, and generator components.

Person-name selection uses each eligible record once. `source_occurrences` records how many source rows contributed; it is provenance, not an implicit frequency weight. Regional eligibility uses `profiles`. Within English, `shared` records are available to all profiles; American-only records also carry `american`.

An empty value can be intentional, such as an absent surname or an optional gang-name component. It is retained rather than treated as a missing record.

## Programs and table modes

A program has its own ID, prompts, definitions, entrypoint, and table map. References are qualified as `program_id/table_name`, preventing different files' identically named tables from colliding.

| Table mode | Contents |
| --- | --- |
| `pool` | Unique record IDs from a named pool; uniform selection. |
| `dictionary` | Original keys mapped to pool record IDs. |
| `lookup` | Non-overlapping inclusive numeric ranges and result nodes. |
| `weighted` | Result nodes with positive integer weights. |

Native operation nodes have an `op` field:

| Operation | Purpose |
| --- | --- |
| `text`, `number` | Literal values. |
| `variable` | Read a named variable. |
| `dice`, `add` | Random integer dice expressions and arithmetic addition. |
| `concat` | Concatenate child values in order. |
| `choice` | Choose between child values. |
| `roll`, `deck` | Random table selection, repeated selection, or a pick without replacement. |
| `lookup` | Read a dictionary/table by key. |
| `compare`, `if` | Conditional selection. |
| `transform` | `proper` or `lower` text transformation. |

Table `set` bindings execute before the result is selected. Program definitions and prompts establish their variables before entrypoint execution. The native interpreter is tools/namebot.py. Its assignment whitespace, transforms and deck semantics are documented in RUNNING.md. Exact parity with the original engine remains unverified.

## Duplicate policy

Matching uses NFC, normalized whitespace, lowercase matching keys, and straight/curly apostrophe equivalence. Display spelling and alternative forms remain available. No accents are removed and no transliteration is used for matching. Different cultures and different semantic pools remain independent.

Duplicate names and literal components become one pool record. Repeated dictionary values can share one record while keeping all keys. Identical procedural alternatives become one weighted alternative with their weights added.

## References

- JSON: https://www.rfc-editor.org/rfc/rfc8259
- Unicode normalization: https://www.unicode.org/reports/tr15/

## Sourced starter metadata

Optional `evidence` records identify a reference and observed usage. Empty `genders` means unspecified, not unisex. Regional evidence can include year and geographic coverage. `locale` identifies a regional naming context independently from linguistic origin. Profiles with `name_order` and `program` select an explicit ordered program; the Filipino maternal and paternal slots both draw from the family pool. English `regional_sample_programs` return only dated regional given names.
