"""Exhaustively check the two Roman program outputs, restricted to their used operations."""
from pathlib import Path
from itertools import product
import json
import zipfile

root = Path(__file__).resolve().parent.parent
r = json.loads((root / 'data/latin.json').read_text())
assert r['language'] == 'la'
assert sum(map(len, r['pools'].values())) == 104
records = {x['id']: x for pool in r['pools'].values() for x in pool}
assert not {'Aacademicus', 'Yulenka', 'Achilles'} & {x['value'] for x in records.values()}
for gender in ['male', 'female']:
    program = next(x for x in r['programs'] if x['id'] == 'roman_' + gender)
    tables = program['tables']
    def table(name):
        t = tables[name]
        if t['mode'] == 'pool':
            assert all(records[i]['genders'] == [gender] for i in t['entries'])
            return [records[i]['value'] for i in t['entries']]
        assert t['mode'] == 'weighted' and len(t['entries']) == 1
        return node(t['entries'][0]['value'])
    def node(n):
        if n['op'] == 'text':
            return [n['value']]
        if n['op'] == 'roll':
            assert n['count'] == {'op': 'number', 'value': 1}
            return table(n['table'])
        assert n['op'] == 'concat'
        return [''.join(parts) for parts in product(*(node(c) for c in n['items']))]
    names = table(program['entrypoint'])
    assert len(names) == len(set(names)) == (7680 if gender == 'male' else 480)
    assert all(len(n.split()) == (3 if gender == 'male' else 2) for n in names)
    assert ('Marcus Tullius Rufus' if gender == 'male' else 'Claudia Severa') in names
    print(gender, len(names), 'unique correctly ordered outputs')
with zipfile.ZipFile(root / 'backup/source_tables.zip') as z:
    assert not any(Path(n).name == 'Latin.nam' for n in z.namelist())
print('Rejected Latin source absent from bundled backup')
