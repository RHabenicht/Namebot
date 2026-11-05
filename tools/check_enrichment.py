"""Check sourced membership and exhaustively render the simple enrichment programs.
This deliberately does not implement the complete legacy rule engine.
"""
from pathlib import Path
from itertools import product
import json
from build_enrichment import key
root = Path(__file__).resolve().parent.parent
total = 0
program_count = 0
for identifier in ['hawaiian', 'khmer', 'filipino', 'english']:
    r = json.loads((root / 'data' / (identifier + '.json')).read_text())
    seed = json.loads((root / 'sources' / (('english_regional' if identifier == 'english' else identifier) + '_source.json')).read_text())
    records = {v['id']: v for pool in r['pools'].values() for v in pool}
    if identifier != 'english':
        for role, pool in r['pools'].items():
            assert {key(x['value']) for x in pool} == {key(x['value']) for x in seed['records'] if x['role'] == role}
        if identifier == 'hawaiian':
            values = {x['value'] for x in records.values()}
            assert 'ʻAilana' in values and 'Hōkū' in values
            assert key('ʻAilana') != key('Ailana')
    for p in r['programs']:
        if identifier == 'english' and '_sample_' not in p['id']:
            continue
        program_count += 1
        gender = p['id'].rsplit('_', 1)[-1]
        gender = None if gender == 'all' else gender
        parts = p['tables'][p['entrypoint']]['entries'][0]['value']['items']
        rolls = [n for n in parts if n['op'] == 'roll']
        expected_order = ['given'] if identifier == 'english' else seed['order']
        assert [n['table'].rsplit('/', 1)[-1] for n in rolls] == expected_order
        for n, slot in zip(rolls, expected_order):
            table = p['tables'][n['table']]
            ids = table['entries']
            assert ids and len(ids) == len(set(ids))
            assert all(records[i]['weight'] == 1 for i in ids)
            if identifier == 'english':
                region = p['id'].split('_sample_')[0]
                expected = {key(v) for g in seed['groups'] if g['profile'] == region for v in g[gender]}
            else:
                role = 'family' if slot == 'maternal_family' else slot
                expected = {key(v['value']) for v in seed['records'] if v['role'] == role and (role != 'given' or gender is None or gender in v['genders'])}
            assert {key(records[i]['value']) for i in ids} == expected
        def table(name):
            t = p['tables'][name]
            if t['mode'] == 'pool':
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
            return [''.join(v) for v in product(*(node(c) for c in n['items']))]
        outputs = table(p['entrypoint'])
        assert outputs and all(s and s == s.strip() and '  ' not in s for s in outputs)
        total += len(outputs)
        print(p['id'], len(outputs), 'ordered outputs checked')
assert program_count == 15
print(json.dumps({'enrichment_programs_checked': program_count, 'enrichment_outputs_checked': total}))
