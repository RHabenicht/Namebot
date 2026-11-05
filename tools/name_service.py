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

# Credits apply to the imported tables, including mixed-source sets.
SOURCE_CREDITS = {
    'ancient_greek': 'Gurth',
    'basque': 'Gurth',
    'egyptian_legacy': 'Gurth',
    'finnish': 'Gurth',
    'gangs': 'Gurth',
    'halfling': 'Gurth',
    'hindi_legacy': 'Gurth',
    'indian_legacy': 'Gurth',
    'native_american_legacy': 'Gurth',
    'danish': 'Gurth and Joel Crook',
    'dutch': 'Gurth and Joel Crook',
    'english': 'Gurth and Joel Crook',
    'german': 'Gurth and Joel Crook',
    'irish': 'Gurth and Joel Crook',
    'italian': 'Gurth and Joel Crook',
    'japanese': 'Gurth and Joel Crook',
    'technical_english': 'Joel Crook',
    'latin': 'Christian Schwietzke and Nightlife',
}

class NameService:
    def __init__(self):
        self.resources = {}
        self.resource_aliases = {}
        self.hidden_resources = {}
        for path in sorted((ROOT / 'data').glob('*.json')):
            resource = json.loads(path.read_text(encoding='utf-8'))
            if path.stem == 'technical_english':
                self.hidden_resources[path.stem] = {**resource, 'label': 'Geordi Gizmo'}
                programs = {program['id']: program for program in resource['programs']}
                self.resources['geordi_gizmo_company'] = {
                    **resource, 'label': 'Geordi Gizmo Company',
                    'programs': [programs['geordi_gizmo_company']],
                }
                self.resources['geordi_gizmo_technical'] = {
                    **resource, 'label': 'Geordi Gizmo Technical',
                    'programs': [programs['geordi_gizmo_science']],
                }
                continue
            public_id, label = PUBLIC_SETS.get(path.stem, (path.stem, resource['label']))
            self.resources[public_id] = {**resource, 'label': label}
            if public_id != path.stem:
                self.resource_aliases[path.stem] = public_id

    def _get_resource(self, resource):
        resource = self.resource_aliases.get(resource, resource)
        result = self.resources.get(resource) or self.hidden_resources.get(resource)
        if result is None:
            raise GenerationError('Unknown set. Use /name_sets.')
        return result

    def generate(self, resource, count=1, program=None, profile=None, gender=None):
        r = self._get_resource(resource)
        if type(count) is not int or not 1 <= count <= 20:
            raise GenerationError('Choose 1–20 names.')
        if gender not in (None,'male','female'):
            raise GenerationError('Choose male or female, or leave gender blank.')
        if program and profile:
            raise GenerationError('Choose a program or a profile, not both.')
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
        r = self._get_resource(resource)
        credit = SOURCE_CREDITS.get(r['id'])
        heading = r['label']
        if credit:
            heading += '\nCredit: ' + credit
        return heading+'\nPrograms: '+', '.join(p['id'] for p in r['programs'])+'\nProfiles: '+(', '.join(p['id'] for p in r['profiles']) or 'none')
