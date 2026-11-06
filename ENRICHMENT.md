# Hawaiian, Khmer, Filipino, and regional English names

These starter lists supply names for fictional characters. The source JSON files record the selected entries, references, and coverage.

| Set | Given records | Family records | Output order |
| --- | ---: | ---: | --- |
| Hawaiian | 40 | 30 | Given, family |
| Khmer | 42 | 29 | Family, given |
| Filipino | 30 | 20 | Given, maternal family, paternal family |

The Hawaiian set keeps the ʻokina and macrons found in the sources. Its gender tags reflect the usage recorded there.

The Khmer set uses romanized spellings. A blank gender list marks an entry whose usage is unspecified. Male and female filters draw from the smaller pools of explicitly labelled entries.

The Filipino set draws from a mix of linguistic sources. The program uses a common full-name order with the maternal family name in the middle and the paternal family name last. It draws each family name independently and keeps multiword names together.

## English regional samples

The British sample draws from lists for England and Wales and for Scotland. The Australian sample covers New South Wales. The New Zealand sample uses national lists. Each sample covers given names from 2024 births.

The six regional sample programs return given names by the source gender category. Standard profiles also use shared English names and surnames. Repeated entries retain each source reference and have the same selection weight as entries recorded once.

## Sources and reuse

The source files give the reference links, authors where recorded, dates, and selection notes.

- [Hawaiian](sources/hawaiian_source.json)
- [Khmer](sources/khmer_source.json)
- [Filipino](sources/filipino_source.json)
- [Regional English](sources/english_regional_source.json)

The Wikipedia and Wiktionary references retain contributor attribution and CC BY-SA 4.0 notices. The bundled legacy material retains its own source credits and terms.

## Checks

`tools/check_enrichment.py` checks source membership, gender selection, name order, duplicate table entries, equal record weights, and Hawaiian spelling. It also enumerates the outputs of all 15 starter programs. [Interpreter tests](RUNNING.md#verification)
