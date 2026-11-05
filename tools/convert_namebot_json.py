"""Convert the checked name collection into UTF-8 JSON resources."""
from pathlib import Path
from collections import OrderedDict
import hashlib
import json
import re
import unicodedata
import zipfile

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / 'SR1e-3e_Namebot_Corrected_Lists.zip'
OUTPUT = ROOT / 'SR1e-3e_Namebot_Universal_JSON'
FORMAT = 'sr-namebot/1'
SETS = {
    'native_american_legacy': ('Native American — legacy English word generator', 'en'),
    'english': ('English', 'en'), 'ancient_greek': ('Ancient Greek', 'grc'),
    'basque': ('Basque', 'eu'), 'chinese': ('Chinese', 'zh'), 'danish': ('Danish', 'da'), 'dutch': ('Dutch', 'nl'),
    'egyptian_legacy': ('Egyptian — legacy collection', 'und'), 'finnish': ('Finnish', 'fi'),
    'french': ('French', 'fr'), 'german': ('German', 'de'),
    'hindi_legacy': ('Hindi — legacy mixed collection', 'hi'),
    'indian_legacy': ('Indian — language unclassified', 'und'), 'irish': ('Irish', 'ga'),
    'italian': ('Italian', 'it'), 'japanese': ('Japanese', 'ja'),
    'norwegian': ('Norwegian', 'no'), 'old_norse': ('Old Norse', 'non'),
    'polish': ('Polish', 'pl'), 'portuguese': ('Portuguese', 'pt'), 'russian': ('Russian', 'ru'),
    'scottish': ('Scottish — language unclassified', 'und'), 'spanish': ('Spanish', 'es'),
    'swedish': ('Swedish', 'sv'), 'turkish': ('Turkish', 'tr'),
    'halfling': ('Halfling', 'und'), 'gangs': ('Gang names', 'en'),
    'technical_english': ('Company and science generators', 'en'),
}
FILE_MAP = {
    'Native American.nam': 'native_american_legacy',
    'American.nam': 'english', 'English.nam': 'english', 'EnglishNames.ipt': 'english',
    'Ancient Greek.nam': 'ancient_greek', 'Basque.nam': 'basque', 'ChineseNames.ipt': 'chinese',
    'Danish.nam': 'danish', 'DanishNames.ipt': 'danish', 'Dutch.nam': 'dutch', 'DutchNames.ipt': 'dutch',
    'Egyptian.nam': 'egyptian_legacy', 'Finnish.nam': 'finnish', 'FrenchNames.ipt': 'french',
    'German.nam': 'german', 'GermanNames.ipt': 'german', 'Hindi.nam': 'hindi_legacy',
    'Hindi 2.nam': 'hindi_legacy', 'Indian.nam': 'indian_legacy', 'Irish.nam': 'irish',
    'IrishName.ipt': 'irish', 'Italian.nam': 'italian', 'ItalianName.ipt': 'italian',
    'Japanese.nam': 'japanese', 'JapaneseName.ipt': 'japanese', 'JapaneseNames.ipt': 'japanese',
    'NorwegianNames.ipt': 'norwegian', 'Old Norse Names.ipt': 'old_norse',
    'PolishNames.ipt': 'polish', 'PortugueseNames.ipt': 'portuguese', 'RussianNames.ipt': 'russian',
    'ScottishNames.ipt': 'scottish', 'SpanishNames.ipt': 'spanish', 'SwedishNames.ipt': 'swedish',
    'TurkishNames.ipt': 'turkish', 'halfling.nam': 'halfling', 'Gangs.nam': 'gangs',
    'Geordi_Gizmo_Company.ipt': 'technical_english', 'Geordi_Gizmo_Science.ipt': 'technical_english',
}


def decode(raw):
    if raw.startswith((b'\xff\xfe', b'\xfe\xff')):
        return raw.decode('utf-16'), 'UTF-16'
    try:
        return raw.decode('utf-8-sig'), 'UTF-8'
    except UnicodeDecodeError:
        return raw.decode('cp1252'), 'Windows-1252-compatible legacy text'


def slug(value):
    return re.sub(r'[^a-z0-9]+', '_', value.lower()).strip('_')


def clean(value):
    return unicodedata.normalize('NFC', re.sub(r'\s+', ' ', value.strip()))


def key(value):
    return clean(value).translate(str.maketrans({'’': "'", '‘': "'", 'ʼ': "'"})).lower()


def literal(value):
    return {'op': 'text', 'value': value}


def expression(value):
    value = value.strip()
    if value.startswith('{') and value.endswith('}'):
        value = value[1:-1].strip()
    dice = re.fullmatch(r'(\d+)d(\d+)([+-]\d+)?', value, re.I)
    if dice:
        node = {'op': 'dice', 'count': int(dice[1]), 'sides': int(dice[2])}
        if dice[3]:
            node = {'op': 'add', 'items': [node, {'op': 'number', 'value': int(dice[3])}]}
        return node
    if re.fullmatch(r'-?\d+', value):
        return {'op': 'number', 'value': int(value)}
    if re.fullmatch(r'\$?[A-Za-z_][A-Za-z0-9_]*', value):
        return {'op': 'variable', 'name': value.lstrip('$').lower()}
    raise ValueError(('Unsupported expression', value))


class Template:
    def __init__(self, text, scope):
        self.text, self.scope, self.pos = text, scope, 0

    @staticmethod
    def close(text, start, opening, closing):
        depth, escape = 0, False
        for i in range(start, len(text)):
            character = text[i]
            if escape:
                escape = False
                continue
            if character == '\\':
                escape = True
                continue
            if character == opening:
                depth += 1
            elif character == closing:
                depth -= 1
                if depth == 0:
                    return i
        raise ValueError(('Unbalanced expression', text[start:]))

    def child(self, text):
        return Template(text, self.scope).parse()

    def condition(self):
        start = self.pos + len('[when]')
        do = self.text.index('[do]', start)
        condition = self.text[start:do].strip()
        match = re.fullmatch(r'(.+?)\s*(<=|>=|!=|=|<|>)\s*(.+)', condition)
        if not match:
            raise ValueError(('Unsupported condition', condition))
        left = expression(match[1])
        right_text = match[3].strip()
        right = expression(right_text) if right_text.startswith('{') or re.fullmatch(r'-?\d+', right_text) else literal(right_text)
        level, otherwise, end = 0, None, None
        for token in re.finditer(r'\[(when|else|end)\]', self.text[do + 4:]):
            index = do + 4 + token.start()
            if token[1] == 'when':
                level += 1
            elif token[1] == 'end':
                if level == 0:
                    end = index
                    break
                level -= 1
            elif token[1] == 'else' and level == 0:
                otherwise = index
        if end is None:
            raise ValueError('Missing conditional end')
        yes = self.text[do + 4:otherwise if otherwise is not None else end]
        no = self.text[otherwise + 6:end] if otherwise is not None else ''
        self.pos = end + 5
        return {'op': 'if', 'test': {'op': 'compare', 'operator': match[2], 'left': left, 'right': right}, 'then': self.child(yes), 'else': self.child(no)}

    def bracket(self, content):
        depth, split = 0, None
        for index, character in enumerate(content):
            if character in '[{':
                depth += 1
            elif character in ']}':
                depth -= 1
            elif content[index:index + 2] == '>>' and depth == 0:
                split = index
                break
        filters = []
        if split is not None:
            filters = [part.strip().lower() for part in content[split + 2:].split('>>')]
            content = content[:split].strip()
        if content.startswith(('@', '!', '#')):
            kind, arguments = content[0], content[1:].strip()
            repetition = re.fullmatch(r'(\{[^{}]+\}|\d+)\s+(.+)', arguments)
            count = expression(repetition[1]) if repetition else {'op': 'number', 'value': 1}
            target = repetition[2].strip() if repetition else arguments
            node = {'op': {'@': 'roll', '!': 'deck', '#': 'lookup'}[kind], 'table': self.scope + '/' + target}
            node['key' if kind == '#' else 'count'] = count
        elif content.startswith('|'):
            node = {'op': 'choice', 'items': [self.child(part) for part in content[1:].split('|')]}
        else:
            node = self.child(content)
        for transform in filters:
            if transform not in {'proper', 'lower'}:
                raise ValueError(('Unsupported filter', transform))
            node = {'op': 'transform', 'transform': transform, 'value': node}
        return node

    def parse(self):
        nodes, buffer = [], []
        def flush():
            if buffer:
                nodes.append(literal(''.join(buffer)))
                buffer.clear()
        while self.pos < len(self.text):
            character = self.text[self.pos]
            if self.text.startswith('[when]', self.pos):
                flush()
                nodes.append(self.condition())
                continue
            if character == '[':
                flush()
                end = self.close(self.text, self.pos, '[', ']')
                nodes.append(self.bracket(self.text[self.pos + 1:end]))
                self.pos = end + 1
                continue
            if character == '{':
                flush()
                end = self.close(self.text, self.pos, '{', '}')
                nodes.append(expression(self.text[self.pos + 1:end]))
                self.pos = end + 1
                continue
            if character == '\\' and self.pos + 1 < len(self.text):
                escaped = self.text[self.pos + 1]
                buffer.append({'_': ' ', 'z': '', 'n': '\n', 't': '\t'}.get(escaped, escaped))
                self.pos += 2
                continue
            buffer.append(character)
            self.pos += 1
        flush()
        return nodes[0] if len(nodes) == 1 else {'op': 'concat', 'items': nodes}


def pool_role(table, dataset):
    value = table.lower()
    if dataset in {'gangs', 'technical_english', 'native_american_legacy'}:
        return 'component_' + slug(table), []
    if dataset == 'chinese' and value.startswith('english'):
        return ('english_nickname' if 'nickname' in value else 'english_given'), ['female' if 'female' in value else 'male']
    if value == 'male' or 'malefirstname' in value and 'female' not in value or value in {'norsemalename', 'japanmalenames'}:
        return 'given', ['male']
    if value == 'female' or 'femalefirstname' in value or value == 'norsefemalename':
        return 'given', ['female']
    if value in {'last names'} or value.endswith('lastname'):
        return 'family', []
    if value == 'additions':
        return 'addition', []
    return 'component_' + slug(table), []


def build():
    resources, indexes, input_rows, source_digest = {}, {}, 0, hashlib.sha256(INPUT.read_bytes()).hexdigest()
    for identifier, (label, language) in SETS.items():
        resources[identifier] = {'format': FORMAT, 'id': identifier, 'label': label, 'language': language, 'kind': 'category' if identifier in {'gangs', 'halfling', 'technical_english', 'native_american_legacy'} else 'language', 'status': 'imported', 'profiles': [], 'pools': {}, 'programs': [], 'sources': []}
        indexes[identifier] = {}

    def add(resource, role, value, genders, source, table):
        nonlocal input_rows
        input_rows += 1
        value = clean(value)
        marker = role + '\0' + key(value)
        pool = resource['pools'].setdefault(role, [])
        by_key = indexes[resource['id']]
        if marker not in by_key:
            identifier = role + '_' + hashlib.sha256(marker.encode()).hexdigest()[:12]
            record = {'id': identifier, 'value': value, 'weight': 1, 'genders': [], 'profiles': [], 'sources': [], 'variants': [], 'source_occurrences': 0}
            by_key[marker] = record
            pool.append(record)
        record = by_key[marker]
        if value != record['value'] and value not in record['variants']:
            record['variants'].append(value)
            if record['value'].islower() and not value.islower():
                record['variants'].remove(value)
                record['variants'].append(record['value'])
                record['value'] = value
        record['genders'] = sorted(set(record['genders']) | set(genders))
        profile = 'american' if source == 'American.nam' else 'shared'
        record['profiles'] = sorted(set(record['profiles']) | {profile})
        provenance = source + '#' + table
        if provenance not in record['sources']:
            record['sources'].append(provenance)
        record['source_occurrences'] += 1
        return record['id']

    def literal_table(resource, source, table, rows, keyed=False):
        role, genders = pool_role(table, resource['id'])
        resource['pools'].setdefault(role, [])
        ids = [add(resource, role, text, genders, source, table) for _, text in rows]
        if keyed:
            return {'mode': 'dictionary', 'pool': role, 'entries': [{'key': key_value, 'entry': identifier} for (key_value, _), identifier in zip(rows, ids)]}
        return {'mode': 'pool', 'pool': role, 'entries': list(dict.fromkeys(ids)), 'weighting': 'uniform_unique_entries'}

    with zipfile.ZipFile(INPUT) as archive:
        source_files = {Path(name).name: archive.read(name) for name in archive.namelist() if name.startswith('SR1e-3e_Namebot/lists/')}
    assert set(source_files) == set(FILE_MAP)
    for filename, raw in sorted(source_files.items()):
        text, encoding = decode(raw)
        resource = resources[FILE_MAP[filename]]
        source_id = slug(Path(filename).stem)
        source = {'file': filename, 'sha256': hashlib.sha256(raw).hexdigest(), 'encoding': encoding}
        resource['sources'].append(source)
        program = {'id': source_id, 'source': filename, 'entrypoint': None, 'prompts': [], 'definitions': [], 'tables': {}}
        if filename.endswith('.nam'):
            lines = text.splitlines()
            marks = {'COMMENT', 'MALE', 'FEMALE', 'LAST NAMES', 'ADDITIONS', 'DEFAULTS', 'END'}
            starts = [(i, line.strip()) for i, line in enumerate(lines) if line.strip() in marks]
            for pos, (start, label) in enumerate(starts):
                end = starts[pos + 1][0] if pos + 1 < len(starts) else len(lines)
                block = [line for line in lines[start + 1:end] if line.strip()]
                if label == 'COMMENT' and filename in {'Native American.nam'}:
                    source['comment'] = '\n'.join(block)
                if label == 'DEFAULTS':
                    source['legacy_defaults'] = {line.split('=', 1)[0].strip(): line.split('=', 1)[1].strip() for line in block}
                if label not in {'MALE', 'FEMALE', 'LAST NAMES', 'ADDITIONS'}:
                    continue
                count = int(block[0].strip())
                rows = []
                for line in block[1:]:
                    match = re.fullmatch(r'\s*(\d+)(?:\s+(.*))?', line)
                    assert match
                    rows.append((int(match[1]), match[2] or ''))
                assert len(rows) == count, (filename, label, count, len(rows))
                program['tables'][source_id + '/' + label] = literal_table(resource, filename, label, rows)
        else:
            tables, current = OrderedDict(), None
            for number, line in enumerate(text.splitlines(), 1):
                value = line.strip()
                if not value or value.startswith(('//', ';', '#')):
                    continue
                header = re.fullmatch(r'Table:\s*(.+?)\s*', value, re.I)
                if header:
                    current = {'name': header[1], 'type': 'random', 'entries': [], 'set': []}
                    tables[header[1]] = current
                    continue
                command = re.match(r'^([A-Za-z]+):\s*(.*)$', value)
                if command:
                    kind, body = command[1].lower(), command[2]
                    if kind == 'endtable':
                        current = None
                    elif kind in {'type', 'roll'}:
                        current[kind] = body.lower()
                    elif kind in {'set', 'define'}:
                        variable, body = body.split('=', 1)
                        target = current['set'] if kind == 'set' and current else program['definitions']
                        target.append({'name': variable.strip().lower(), 'value': Template(body.strip(), source_id).parse()})
                    elif kind == 'prompt':
                        prompt = re.fullmatch(r'(.*?)\{(.*?)\}\s*(.*)', body)
                        assert prompt
                        program['prompts'].append({'id': 'prompt' + str(len(program['prompts']) + 1), 'label': prompt[1].strip(), 'choices': [item.strip() for item in prompt[2].split('|')], 'default': prompt[3].strip()})
                    else:
                        raise ValueError(('Unsupported directive', filename, number, kind))
                elif current is not None:
                    current['entries'].append(value)
                else:
                    raise ValueError(('Entry outside a table', filename, number))
            program['entrypoint'] = source_id + '/' + next(iter(tables))
            for table_name, table in tables.items():
                table_id = source_id + '/' + table_name
                plain = all(not re.search(r'[\[\]{}\\]', entry) and not re.match(r'\d+(?:-\d+)?:', entry) for entry in table['entries'])
                if plain:
                    converted = literal_table(resource, filename, table_name, list(enumerate(table['entries'], 1)))
                elif table['type'] == 'dictionary':
                    rows = []
                    for entry in table['entries']:
                        match = re.fullmatch(r'(\d+):(.*)', entry)
                        assert match
                        rows.append((int(match[1]), match[2]))
                    converted = literal_table(resource, filename, table_name, rows, keyed=True)
                else:
                    converted = {'mode': 'lookup' if table['type'] == 'lookup' else 'weighted', 'entries': []}
                    if 'roll' in table:
                        converted['roll'] = expression(table['roll'])
                    merged = {}
                    for entry in table['entries']:
                        match = re.fullmatch(r'(\d+)(?:-(\d+))?:(.*)', entry)
                        body = match[3] if match else entry
                        node = Template(body, source_id).parse()
                        row = {'value': node}
                        if converted['mode'] == 'lookup':
                            assert match
                            row['range'] = [int(match[1]), int(match[2] or match[1])]
                            converted['entries'].append(row)
                        else:
                            weight = int(match[1]) if match else 1
                            signature = json.dumps(node, sort_keys=True, ensure_ascii=False)
                            if signature in merged:
                                merged[signature]['weight'] += weight
                            else:
                                row['weight'] = weight
                                converted['entries'].append(row)
                                merged[signature] = row
                if table['set']:
                    converted['set'] = table['set']
                program['tables'][table_id] = converted
        resource['programs'].append(program)

    for identifier, resource in resources.items():
        if identifier == 'english':
            for profile, label, locale in [('american', 'American English', 'en-US'), ('british', 'British English', 'en-GB'), ('australian', 'Australian English', 'en-AU'), ('new_zealand', 'New Zealand English', 'en-NZ')]:
                resource['profiles'].append({'id': profile, 'label': label, 'locale': locale, 'status': 'source_labelled' if profile == 'american' else 'shared_english_starter', 'eligible_profile_tags': ['shared', 'american'] if profile == 'american' else ['shared'], 'regional_enrichment_needed': profile != 'american', 'name_order': ['given', 'family']})
            resource['notes'] = ['English.nam explicitly describes mixed English/American names. It and EnglishNames.ipt form the shared English pool.', 'British, Australian and New Zealand profiles currently use shared English starter data. No new regional names or frequency claims have been added.']
        elif identifier not in {'gangs', 'technical_english', 'native_american_legacy'}:
            resource['profiles'].append({'id': 'default', 'label': resource['label'], 'status': 'source_labelled', 'eligible_profile_tags': ['shared'], 'name_order': ['family', 'given'] if identifier in {'japanese', 'chinese'} else ['given', 'family']})
        if identifier in {'hindi_legacy', 'indian_legacy', 'egyptian_legacy', 'scottish'}:
            resource['classification_review_needed'] = True
            resource.setdefault('notes', []).append('Legacy naming-set labels are preserved. Do not infer an individual name\'s language, religion, ethnicity, or regional frequency from these labels.')
        if identifier == 'native_american_legacy':
            resource['classification_review_needed'] = True
            resource['notes'] = ['English word-combination generator from a legacy source, with no named tribal or Indigenous-language attribution.', 'MALE/FEMALE/LAST NAMES are retained as component tables, not verified given names or surnames. The blank FEMALE entry is intentional.', 'Source spelling Squirel is preserved pending editorial review.']
        if identifier == 'japanese':
            resource.setdefault('notes', []).append('Listed-name programs and the separate syllable generator remain distinct selectable programs.')
        if identifier == 'gangs':
            resource['notes'] = ['Legacy MALE/FEMALE tables are gang-name components, not character genders. Their blank entry and source table references are retained.']
        for pool in resource['pools'].values():
            pool.sort(key=lambda row: (key(row['value']), row['id']))
            for row in pool:
                row['variants'] = sorted(set(row['variants']) - {row['value']})
                row['sources'].sort()
    for identifier, label, language in [('hawaiian', 'Hawaiian', 'haw'), ('khmer', 'Cambodian / Khmer', 'km'), ('filipino', 'Filipino', 'fil')]:
        resources[identifier] = {'format': FORMAT, 'id': identifier, 'label': label, 'language': language, 'kind': 'language', 'status': 'needs_source_data', 'profiles': [], 'pools': {}, 'programs': [], 'sources': [], 'notes': ['Requested naming set. No source list has been supplied or researched for import yet.']}

    from build_roman_latin import build_roman_latin
    resources['latin'] = build_roman_latin(ROOT.parent / 'sources' / 'latin_roman_source.json')
    input_rows += sum(len(pool) for pool in resources['latin']['pools'].values())
    from build_enrichment import apply_enrichment
    input_rows += apply_enrichment(resources, ROOT.parent / 'sources')
    OUTPUT.mkdir(exist_ok=True)
    data_dir = OUTPUT / 'data'
    data_dir.mkdir(exist_ok=True)
    for identifier, resource in sorted(resources.items()):
        (data_dir / (identifier + '.json')).write_text(json.dumps(resource, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    unique = sum(len(pool) for resource in resources.values() for pool in resource['pools'].values())
    report = {'format': FORMAT, 'project': 'SR1e-3e Namebot', 'date': '2026-11-04', 'source_files': len({s['file'] for r in resources.values() for s in r['sources']}), 'input_pool_rows': input_rows, 'unique_pool_records': unique, 'duplicate_pool_rows_merged': input_rows - unique, 'populated_resources': sum(r['status'] != 'needs_source_data' for r in resources.values()), 'awaiting_source_data': [i for i, r in resources.items() if r['status'] == 'needs_source_data'], 'source_archive_sha256': source_digest, 'resources': [{'id': identifier, 'file': 'data/' + identifier + '.json', 'status': resource['status'], 'records': sum(len(pool) for pool in resource['pools'].values()), 'source_files': [source['file'] for source in resource['sources']]} for identifier, resource in sorted(resources.items())]}
    (OUTPUT / 'catalog.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({name: value for name, value in report.items() if name != 'resources'}, ensure_ascii=False))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=INPUT)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    arguments = parser.parse_args()
    INPUT = arguments.source.resolve()
    OUTPUT = arguments.output.resolve()
    build()
