"""Shared request validation and generation for the Discord adapter."""
import json
from namebot import ROOT, Engine, GenerationError

# Keep source IDs in the data and use shorter names in Discord.
PUBLIC_SETS = {
    'egyptian_legacy': ('egyptian', 'Egyptian'),
    'hindi_legacy': ('hindi', 'Hindi'),
    'indian_legacy': ('indian', 'Indian'),
    'native_american_legacy': ('native_american', 'Native American (English word generator)'),
    'scottish': ('scottish', 'Scottish'),
}

class NameService:
    def __init__(self):
        self.resources = {}
        self.resource_aliases = {}
        for path in sorted((ROOT / 'data').glob('*.json')):
            resource = json.loads(path.read_text(encoding='utf-8'))
            public_id, label = PUBLIC_SETS.get(path.stem, (path.stem, resource['label']))
            self.resources[public_id] = {**resource, 'label': label}
            if public_id != path.stem:
                self.resource_aliases[path.stem] = public_id

    def generate(self, resource, count=1, program=None, profile=None, gender=None):
        resource = self.resource_aliases.get(resource, resource)
        if resource not in self.resources:
            raise GenerationError('Unknown set. Use /name_sets.')
        if type(count) is not int or not 1 <= count <= 20:
            raise GenerationError('Choose 1–20 names.')
        if gender not in (None,'male','female'):
            raise GenerationError('Choose male or female, or leave gender blank.')
        if program and profile:
            raise GenerationError('Choose a program or a profile, not both.')
        r=self.resources[resource]
        engine=Engine(r)
        if profile:
            return [engine.profile_name(profile,gender) for _ in range(count)]
        programs={p['id']:p for p in r['programs']}
        if not program:
            # Curated resources explicitly supply one program per gender choice.
            candidate=r['id']+'_'+(gender or 'all')
            if candidate in programs:
                program=candidate
                gender=None
            elif len(programs)==1:
                program=next(iter(programs))
            else:
                raise GenerationError('Choose a program or profile using /name_options.')
        if program not in programs:
            raise GenerationError('Unknown program for this set. Use /name_options.')
        p=programs[program]
        if p['entrypoint'] is None:
            return [engine.compose(program,gender) for _ in range(count)]
        prompts={}
        if gender:
            if program=='old_norse_names':
                prompts={'prompt1':gender.title()}
            else:
                raise GenerationError('This program defines its own gender rules. Choose the appropriate program and leave gender blank.')
        return [engine.generate(program,prompts) for _ in range(count)]

    def options(self, resource):
        resource = self.resource_aliases.get(resource, resource)
        if resource not in self.resources:
            raise GenerationError('Unknown set. Use /name_sets.')
        r=self.resources[resource]
        return r['label']+'\nPrograms: '+', '.join(p['id'] for p in r['programs'])+'\nProfiles: '+(', '.join(p['id'] for p in r['profiles']) or 'none')
