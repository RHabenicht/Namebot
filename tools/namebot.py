"""Standard-library JSON name generator and command-line interface."""
import argparse
import json
import operator
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parent.parent

class GenerationError(ValueError):
    pass

class Engine:
    def __init__(self, resource, seed=None):
        self.resource = resource
        self.rng = random.Random(seed)
        self.records = {r['id']: r for pool in resource['pools'].values() for r in pool}

    def generate(self, program_id, prompts=None, table=None):
        programs = {p['id']: p for p in self.resource['programs']}
        if program_id not in programs:
            raise GenerationError('Unknown program: ' + program_id)
        self.program = programs[program_id]
        self.variables, self.decks, self.steps = {}, {}, 0
        supplied = prompts or {}
        valid = {p['id'] for p in self.program['prompts']}
        if set(supplied) - valid:
            raise GenerationError('Unknown prompt')
        for p in self.program['prompts']:
            value = supplied.get(p['id'], p['default'])
            if value not in p['choices']:
                raise GenerationError('Invalid choice for ' + p['id'])
            self.variables[p['id']] = value
        try:
            self.bind(self.program['definitions'])
            entry = table or self.program['entrypoint']
            if entry is None:
                raise GenerationError('This source contains component tables; choose --table from --list')
            return str(self.table(entry)).strip()
        except (KeyError, RecursionError) as exc:
            raise GenerationError('Missing reference or excessive recursion: ' + str(exc)) from exc

    def compose(self, program_id, gender=None, given_count=1):
        """Compose personal names from one NAM source, without mixing source tables."""
        if gender not in (None, 'male', 'female'):
            raise GenerationError('Gender must be male, female, or omitted')
        if type(given_count) is not int or not 1 <= given_count <= 3:
            raise GenerationError('Given-name count must be between 1 and 3')
        program = next((p for p in self.resource['programs'] if p['id'] == program_id), None)
        if program is None or program['entrypoint'] is not None:
            raise GenerationError('Full-name composition requires a NAM component program')
        tables = program['tables']
        given = []
        for label in ([gender.upper()] if gender else ['MALE', 'FEMALE']):
            table = tables.get(program_id + '/' + label)
            if table is not None and table.get('pool') == 'given':
                given.extend(table['entries'])
        given = list(dict.fromkeys(given))
        if not given:
            raise GenerationError('No personal given names for this selection; component generators require --table')
        family_table = tables.get(program_id + '/LAST NAMES')
        families = family_table['entries'] if family_table and family_table.get('pool') == 'family' else []
        if given_count > len(given):
            raise GenerationError('Not enough distinct given names')
        chosen = self.rng.sample(given, given_count)
        first = ' '.join(self.records[i]['value'] for i in chosen)
        last = self.records[self.rng.choice(families)]['value'] if families else ''
        order = self.resource['profiles'][0]['name_order']
        values = {'given': first, 'family': last}
        if set(order) != {'given', 'family'}:
            raise GenerationError('Unsupported NAM personal-name order')
        return ' '.join(values[role] for role in order if values[role]).strip()

    def profile_name(self, profile_id, gender=None):
        """Use explicit profile programs or the regional English shared pools."""
        if gender not in (None, 'male', 'female'):
            raise GenerationError('Gender must be male, female, or omitted')
        profile = next((p for p in self.resource['profiles'] if p['id'] == profile_id), None)
        if profile is None:
            raise GenerationError('Unknown profile: ' + profile_id)
        if profile.get('program'):
            if gender is not None and profile.get('gender_filter') != gender:
                raise GenerationError('Choose the matching gender profile; do not override its filter')
            return self.generate(profile['program'])
        if self.resource['id'] != 'english':
            raise GenerationError('Choose a source program with --full-name for this resource')
        tags = set(profile['eligible_profile_tags'])
        parts = []
        for role in profile['name_order']:
            eligible = [r for r in self.resource['pools'][role]
                        if tags.intersection(r['profiles']) and
                        (role != 'given' or gender is None or gender in r['genders'])]
            if not eligible:
                raise GenerationError('Empty profile selection for ' + role)
            parts.append(self.rng.choice(eligible)['value'])
        return ' '.join(x for x in parts if x).strip()

    def tick(self):
        self.steps += 1
        if self.steps > 10000:
            raise GenerationError('Generation exceeded 10,000 operations')

    def bind(self, bindings):
        for b in bindings:
            value = self.node(b['value'])
            # Trim assignment syntax padding; preserve spaces inside values.
            self.variables[b['name']] = value.strip() if isinstance(value, str) else value

    def pick(self, weights):
        if not weights or any(type(w) is not int or w <= 0 for w in weights):
            raise GenerationError('Selection requires positive integer weights')
        roll = self.rng.randrange(sum(weights))
        for i, weight in enumerate(weights):
            if roll < weight:
                return i
            roll -= weight

    def table(self, name, key=None, deck=False):
        self.tick()
        t = self.program['tables'][name]
        self.bind(t.get('set', []))
        mode, entries = t['mode'], t['entries']
        if mode == 'lookup':
            if deck:
                raise GenerationError('Deck selection on lookup tables is unsupported')
            value = self.node(t['roll']) if key is None else key
            hits = [e for e in entries if e['range'][0] <= value <= e['range'][1]]
            if len(hits) != 1:
                raise GenerationError('Lookup has no unique matching range')
            return self.node(hits[0]['value'])
        if key is not None:
            if mode != 'dictionary':
                raise GenerationError('Key lookup requires dictionary or range table')
            hits = [e for e in entries if str(e['key']) == str(key)]
            if len(hits) != 1:
                raise GenerationError('Dictionary key not found')
            return self.records[hits[0]['entry']]['value']
        weights = [e['weight'] for e in entries] if mode == 'weighted' else [1] * len(entries)
        if deck:
            remaining = self.decks.get(name)
            if remaining is None or not any(remaining):
                remaining = weights.copy()
                self.decks[name] = remaining
            eligible = [i for i, w in enumerate(remaining) if w]
            i = eligible[self.pick([remaining[j] for j in eligible])]
            remaining[i] -= 1
        else:
            i = self.pick(weights)
        entry = entries[i]
        if mode == 'pool':
            return self.records[entry]['value']
        if mode == 'dictionary':
            return self.records[entry['entry']]['value']
        if mode == 'weighted':
            return self.node(entry['value'])
        raise GenerationError('Unknown table mode: ' + mode)

    def node(self, n):
        self.tick()
        op = n['op']
        if op in ('text', 'number'):
            return n['value']
        if op == 'variable':
            return self.variables[n['name']]
        if op == 'concat':
            return ''.join(str(self.node(x)) for x in n['items'])
        if op == 'choice':
            return self.node(self.rng.choice(n['items']))
        if op == 'add':
            return sum(self.node(x) for x in n['items'])
        if op == 'dice':
            count, sides = n['count'], n['sides']
            if type(count) is not int or type(sides) is not int or not 0 <= count <= 1000 or not 1 <= sides <= 1000000:
                raise GenerationError('Invalid dice bounds')
            return sum(self.rng.randint(1, sides) for _ in range(count))
        if op in ('roll', 'deck'):
            count = self.node(n['count'])
            if type(count) is not int or not 0 <= count <= 1000:
                raise GenerationError('Invalid repetition count')
            return ''.join(str(self.table(n['table'], deck=op == 'deck')) for _ in range(count))
        if op == 'lookup':
            return self.table(n['table'], key=self.node(n['key']))
        if op == 'compare':
            operations = {'=': operator.eq, '!=': operator.ne, '<': operator.lt, '>': operator.gt, '<=': operator.le, '>=': operator.ge}
            return operations[n['operator']](self.node(n['left']), self.node(n['right']))
        if op == 'if':
            return self.node(n['then'] if self.node(n['test']) else n['else'])
        if op == 'transform':
            value = str(self.node(n['value']))
            if n['transform'] == 'lower':
                return value.lower()
            if n['transform'] == 'proper':
                return value.title()
        raise GenerationError('Unknown operation or transform: ' + str(n))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('resource', nargs='?')
    parser.add_argument('--program')
    parser.add_argument('--table', help='Qualified table name for component sources')
    parser.add_argument('--full-name', action='store_true', help='Compose a personal name from a NAM source')
    parser.add_argument('--gender', choices=['male', 'female'])
    parser.add_argument('--given-count', type=int, default=1)
    parser.add_argument('--profile', help='Profile ID, including English regional profiles')
    parser.add_argument('--count', type=int, default=1)
    parser.add_argument('--seed', type=int)
    parser.add_argument('--prompt', action='append', default=[], metavar='ID=CHOICE')
    parser.add_argument('--list', action='store_true')
    args = parser.parse_args()
    files = {p.stem: p for p in (ROOT / 'data').glob('*.json')}
    if args.list and args.resource is None:
        for name in sorted(files):
            print(name)
        return
    if args.resource not in files:
        parser.error('Choose a resource shown by --list')
    resource = json.loads(files[args.resource].read_text(encoding='utf-8'))
    if args.list:
        print('Profiles: ' + ', '.join(p['id'] for p in resource['profiles']))
        for p in resource['programs']:
            print(p['id'] + (' | tables: ' + ', '.join(p['tables']) if p['entrypoint'] is None else '') + (' | prompts: ' + json.dumps(p['prompts'], ensure_ascii=False) if p['prompts'] else ''))
        return
    if not 1 <= args.count <= 1000:
        parser.error('--count must be between 1 and 1000')
    ids = [p['id'] for p in resource['programs']]
    pid = args.program or (ids[0] if len(ids) == 1 else None)
    if args.profile and (args.program or args.table or args.full_name or args.prompt or args.given_count != 1):
        parser.error('--profile cannot be combined with program, table, full-name, prompt, or given-count controls')
    if args.full_name and (args.table or args.prompt):
        parser.error('--full-name cannot be combined with --table or --prompt')
    if not args.full_name and not args.profile and (args.gender or args.given_count != 1):
        parser.error('--gender and --given-count require --full-name or --profile')
    if pid is None and not args.profile:
        parser.error('Choose --program; available: ' + ', '.join(ids))
    try:
        prompts = dict(p.split('=', 1) for p in args.prompt)
        engine = Engine(resource, args.seed)
        for _ in range(args.count):
            if args.profile:
                value = engine.profile_name(args.profile, args.gender)
            elif args.full_name:
                value = engine.compose(pid, args.gender, args.given_count)
            else:
                value = engine.generate(pid, prompts, args.table)
            print(value)
    except (ValueError, KeyError) as exc:
        parser.error(str(exc))

if __name__ == '__main__':
    main()
