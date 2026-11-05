"""Build the curated Roman citizen naming resource from its documented source seed."""
import hashlib
import json


def build_roman_latin(path):
    raw = path.read_bytes()
    seed = json.loads(raw)
    resource = {
        'format': 'sr-namebot/1', 'id': 'latin', 'label': 'Latin — Roman citizen names',
        'language': 'la', 'kind': 'language', 'status': 'imported',
        'scope': seed['scope'], 'profiles': [], 'pools': {}, 'programs': [],
        'sources': [{'file': path.name, 'sha256': hashlib.sha256(raw).hexdigest(),
                     'encoding': 'UTF-8', 'references': seed['references']}],
        'notes': [seed['feminine_rule'], seed['spelling'], seed['selection'],
                  'Generated full names are fictional combinations, not attested historical people or verified family branches.',
                  'This limited citizen profile does not model adoption, inherited family restrictions, filiation, voting tribes, enslaved people, or every provincial and period-specific naming practice.',
                  'Cognomina may be Latin names of non-Latin origin; this starter selects Latin-form elements and does not claim to exhaust Roman usage.']}
    for gender in ['male', 'female']:
        roles = ['praenomen', 'nomen', 'cognomen'] if gender == 'male' else ['nomen', 'cognomen']
        pid = 'roman_' + gender
        resource['profiles'].append({'id': pid, 'label': 'Roman citizen — ' + gender,
                                     'genders': [gender], 'status': 'curated',
                                     'eligible_profile_tags': [pid], 'name_order': roles,
                                     'program': pid})
        tables = {}
        for role in roles:
            pool = role + '_' + gender
            records = []
            for base in seed[role + '_male']:
                value = base if gender == 'male' else base[:-2] + 'a'
                record = {'id': pool + '_' + hashlib.sha256(value.encode()).hexdigest()[:12],
                          'value': value, 'weight': 1, 'genders': [gender], 'profiles': [pid],
                          'sources': [path.name + '#' + role + '_male'],
                          'variants': [], 'source_occurrences': 1,
                          'evidence': 'listed_in_reference' if gender == 'male' else 'grammatically_derived',
                          'reference': 'georges'}
                if gender == 'female':
                    record['derived_from'] = base
                    record['derivation'] = 'final us -> a; selected regular forms only'
                records.append(record)
            resource['pools'][pool] = sorted(records, key=lambda r: r['value'])
            tables[pid + '/' + role] = {'mode': 'pool', 'pool': pool,
                                       'entries': [r['id'] for r in records],
                                       'weighting': 'uniform_unique_entries'}
        nodes = []
        for role in roles:
            if nodes:
                nodes.append({'op': 'text', 'value': ' '})
            nodes.append({'op': 'roll', 'table': pid + '/' + role, 'count': {'op': 'number', 'value': 1}})
        tables[pid + '/full_name'] = {'mode': 'weighted', 'entries': [
            {'weight': 1, 'value': {'op': 'concat', 'items': nodes}}]}
        resource['programs'].append({'id': pid, 'source': path.name,
                                     'entrypoint': pid + '/full_name',
                                     'prompts': [], 'definitions': [], 'tables': tables})
    return resource
