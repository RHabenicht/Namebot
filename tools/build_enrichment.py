"""Import sourced naming sets and merge regional evidence into shared English pools."""
import hashlib
import json
import re
import unicodedata


def key(value):
    return unicodedata.normalize('NFC', re.sub(r'\s+', ' ', value.strip())).translate(str.maketrans({'’': "'", '‘': "'", 'ʼ': "'"})).lower()


def source(path, seed):
    return {'file': path.name, 'encoding': 'UTF-8', 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'references': seed['references']}


def merge(resource, role, value, genders, profile, provenance, evidence):
    value = unicodedata.normalize('NFC', value.strip())
    pool = resource['pools'].setdefault(role, [])
    record = next((r for r in pool if key(r['value']) == key(value)), None)
    if record is None:
        record = {'id': role + '_' + hashlib.sha256((role + '\0' + key(value)).encode()).hexdigest()[:12],
                  'value': value, 'weight': 1, 'genders': [], 'profiles': [], 'sources': [], 'variants': [], 'source_occurrences': 0}
        pool.append(record)
    if value != record['value'] and value not in record['variants']:
        record['variants'].append(value)
    record['genders'] = sorted(set(record['genders']) | set(genders))
    record['profiles'] = sorted(set(record['profiles']) | {profile})
    record['sources'] = sorted(set(record['sources']) | {provenance})
    record['source_occurrences'] += 1
    record.setdefault('evidence', []).append(evidence)
    return record


def program(resource, pid, order, gender=None, profile_tag=None):
    tables, nodes = {}, []
    for slot in order:
        role = 'family' if slot == 'maternal_family' else slot
        eligible = [r for r in resource['pools'][role]
                    if (role != 'given' or gender is None or gender in r['genders'])
                    and (profile_tag is None or profile_tag in r['profiles'])]
        if not eligible:
            raise ValueError((resource['id'], pid, slot, 'empty selection'))
        table_id = pid + '/' + slot
        tables[table_id] = {'mode': 'pool', 'pool': role, 'entries': [r['id'] for r in eligible], 'weighting': 'uniform_unique_entries'}
        if nodes:
            nodes.append({'op': 'text', 'value': ' '})
        nodes.append({'op': 'roll', 'table': table_id, 'count': {'op': 'number', 'value': 1}})
    entry = pid + '/full_name'
    tables[entry] = {'mode': 'weighted', 'entries': [{'weight': 1, 'value': {'op': 'concat', 'items': nodes}}]}
    resource['programs'].append({'id': pid, 'source': resource['sources'][-1]['file'], 'entrypoint': entry, 'prompts': [], 'definitions': [], 'tables': tables})
    return pid


def apply_enrichment(resources, directory):
    input_rows = 0
    for identifier in ['hawaiian', 'khmer', 'filipino']:
        path = directory / (identifier + '_source.json')
        seed = json.loads(path.read_text())
        r = {k: seed[k] for k in ['id', 'label', 'language', 'kind', 'scope', 'notes']}
        r.update(format='sr-namebot/1', status='imported', profiles=[], pools={}, programs=[], sources=[source(path, seed)])
        if 'locale' in seed:
            r['locale'] = seed['locale']
        for row in seed['records']:
            merge(r, row['role'], row['value'], row['genders'], 'shared', path.name + '#' + row['reference'],
                  {'reference': row['reference'], 'gender_basis': 'source_observed_usage' if row['genders'] else 'not_specified'})
            input_rows += 1
        for gender in [None, 'male', 'female']:
            pid = identifier + '_' + (gender or 'all')
            program(r, pid, seed['order'], gender)
            r['profiles'].append({'id': pid, 'label': seed['label'] + ' — ' + (gender or 'unfiltered'), 'status': 'sourced_starter',
                                  'eligible_profile_tags': ['shared'], 'name_order': seed['order'], 'program': pid,
                                  'gender_filter': gender, 'unknown_gender_policy': 'include' if gender is None else 'exclude'})
        for pool in r['pools'].values():
            pool.sort(key=lambda x: (key(x['value']), x['id']))
        resources[identifier] = r
    path = directory / 'english_regional_source.json'
    seed = json.loads(path.read_text())
    english = resources['english']
    english['sources'].append(source(path, seed))
    for group in seed['groups']:
        for gender in ['male', 'female']:
            for value in group[gender]:
                merge(english, 'given', value, [gender], group['profile'], path.name + '#' + group['reference'] + '_' + gender,
                      {'reference': group['reference'], 'year': group['year'], 'coverage': group['coverage'], 'gender': gender})
                input_rows += 1
    for profile in english['profiles']:
        tag = profile['id']
        if tag == 'american':
            continue
        profile.update(status='regional_sample_enriched', eligible_profile_tags=['shared', tag], regional_enrichment_needed=True,
                       enrichment_coverage=sorted({g['coverage'] for g in seed['groups'] if g['profile'] == tag}),
                       enrichment_years=[2024], regional_sample_programs={})
        for gender in ['male', 'female']:
            pid = tag + '_sample_' + gender
            # Each table uses regional evidence for this gender, without inheriting other-source gender tags.
            program(english, pid, ['given'], gender, tag)
            allowed = {key(n) for g in seed['groups'] if g['profile'] == tag for n in g[gender]}
            english['programs'][-1]['tables'][pid + '/given']['entries'] = [r['id'] for r in english['pools']['given'] if key(r['value']) in allowed]
            profile['regional_sample_programs'][gender] = pid
    english['notes'] = [
        'English.nam describes mixed English/American names. Shared pools remain available to all English profiles.',
        'Regional evidence tags supplement the shared pool; repeated observations do not increase record weight.',
        'British additions sample England, Wales and Scotland. Australian additions sample New South Wales. New Zealand additions sample national registration lists. All additions concern 2024 births.',
        'The sample programs select only sourced regional given names. Standard profiles retain shared family names, which have not received a regional surname audit.',
        'Regional enrichment remains open: these samples are not complete national populations or forecasts for fictional years.'
    ]
    for pool in english['pools'].values():
        pool.sort(key=lambda x: (key(x['value']), x['id']))
    return input_rows
