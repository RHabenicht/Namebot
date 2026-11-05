"""Validate the unified data without requiring third-party packages."""
from pathlib import Path
import argparse
import json
import re
import unicodedata


def pairs_unique(pairs):
    result = {}
    for name, value in pairs:
        assert name not in result, ('duplicate JSON object property', name)
        result[name] = value
    return result


def match_key(value):
    value = unicodedata.normalize('NFC', re.sub(r'\s+', ' ', value.strip()))
    return value.translate(str.maketrans({'’': "'", '‘': "'", 'ʼ': "'"})).lower()


def validate(directory):
    catalog = json.loads((directory / 'catalog.json').read_text(encoding='utf-8'), object_pairs_hook=pairs_unique)
    total, occurrences, populated, pending, source_files, rule_nodes = 0, 0, 0, 0, set(), 0
    operations = {'text', 'number', 'variable', 'dice', 'add', 'if', 'compare', 'concat', 'roll', 'deck', 'lookup', 'choice', 'transform'}
    for metadata in catalog['resources']:
        path = directory / metadata['file']
        resource = json.loads(path.read_bytes().decode('utf-8'), object_pairs_hook=pairs_unique)
        assert resource['format'] == 'sr-namebot/1'
        assert resource['id'] == metadata['id'] == path.stem
        assert isinstance(resource['profiles'], list)
        if resource['status'] == 'needs_source_data':
            pending += 1
            assert not resource['pools'] and not resource['programs'] and not resource['sources']
            continue
        populated += 1
        source_files.update(source['file'] for source in resource['sources'])
        by_pool = {}
        for role, records in resource['pools'].items():
            seen, ids = set(), set()
            for record in records:
                value = record['value']
                assert value == unicodedata.normalize('NFC', value)
                assert match_key(value) not in seen, ('duplicate pool entry', path.name, role, value)
                seen.add(match_key(value))
                assert record['id'] not in ids
                ids.add(record['id'])
                assert record['weight'] == 1
                assert record['sources'] and len(set(record['sources'])) == len(record['sources'])
                assert isinstance(record['source_occurrences'], int) and record['source_occurrences'] >= len(record['sources'])
                assert all(match_key(other) == match_key(value) for other in record['variants'])
                total += 1
                occurrences += record['source_occurrences']
            by_pool[role] = ids
        for program in resource['programs']:
            tables = program['tables']
            assert program['entrypoint'] is None or program['entrypoint'] in tables
            def walk(node):
                nonlocal rule_nodes
                if isinstance(node, dict):
                    if 'op' in node:
                        rule_nodes += 1
                        assert node['op'] in operations, ('unknown operation', node)
                        if node['op'] in {'roll', 'deck', 'lookup'}:
                            assert node['table'] in tables, ('unresolved table reference', program['id'], node['table'])
                        if node['op'] == 'dice':
                            assert isinstance(node['count'], int) and node['count'] > 0
                            assert isinstance(node['sides'], int) and node['sides'] > 0
                        if node['op'] == 'transform':
                            assert node['transform'] in {'proper', 'lower'}
                    for value in node.values():
                        walk(value)
                elif isinstance(node, list):
                    for value in node:
                        walk(value)
            for name, table in tables.items():
                mode = table['mode']
                assert mode in {'pool', 'dictionary', 'lookup', 'weighted'}
                if mode in {'pool', 'dictionary'}:
                    assert table['pool'] in by_pool, ('missing pool', path.name, name, table['pool'])
                    identifiers = table['entries'] if mode == 'pool' else [row['entry'] for row in table['entries']]
                    assert set(identifiers) <= by_pool[table['pool']]
                    if mode == 'pool':
                        assert len(identifiers) == len(set(identifiers))
                    else:
                        keys = [row['key'] for row in table['entries']]
                        assert len(keys) == len(set(keys))
                elif mode == 'weighted':
                    signatures = [json.dumps(row['value'], sort_keys=True, ensure_ascii=False) for row in table['entries']]
                    assert len(signatures) == len(set(signatures))
                    assert all(isinstance(row['weight'], int) and row['weight'] > 0 for row in table['entries'])
                elif mode == 'lookup':
                    numbers = [number for row in table['entries'] for number in range(row['range'][0], row['range'][1] + 1)]
                    assert len(numbers) == len(set(numbers))
            walk(program)
        for profile in resource['profiles']:
            if resource['id'] == 'english':
                assert profile['id'] in {'american', 'british', 'australian', 'new_zealand'}
                assert profile['eligible_profile_tags'] == ['shared', profile['id']]
    assert total == catalog['unique_pool_records']
    assert occurrences == catalog['input_pool_rows']
    assert occurrences - total == catalog['duplicate_pool_rows_merged']
    assert populated == catalog['populated_resources']
    assert len(source_files) == catalog['source_files'] == 44
    assert pending == len(catalog['awaiting_source_data']) == 0
    assert match_key('Jose') != match_key('José')
    assert match_key('Weiß') != match_key('Weiss')
    assert match_key('José') == match_key('Jose\u0301')
    assert match_key("O'Connor") == match_key('O’Connor')
    assert match_key('Abhay') == match_key('abhay')
    result = {'status': 'passed', 'source_files_accounted_for': len(source_files), 'populated_sets': populated, 'sets_awaiting_sources': pending, 'unique_pool_records': total, 'duplicate_pool_rows_merged': occurrences - total, 'native_rule_nodes_checked': rule_nodes, 'original_engine_parity_tests': 'not_run', 'discord_runtime_tests': 'not_run'}
    (directory / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    print(json.dumps(validate(parser.parse_args().directory.resolve())))
