"""Shared request validation and generation for the Discord adapter."""
import json
from namebot import ROOT, Engine, GenerationError

class NameService:
    def __init__(self):
        self.resources = {p.stem: json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT/'data').glob('*.json'))}

    def generate(self, resource, count=1, program=None, profile=None, gender=None):
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
            candidate=resource+'_'+(gender or 'all')
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
        if resource not in self.resources:
            raise GenerationError('Unknown set. Use /name_sets.')
        r=self.resources[resource]
        return r['label']+'\nPrograms: '+', '.join(p['id'] for p in r['programs'])+'\nProfiles: '+(', '.join(p['id'] for p in r['profiles']) or 'none')
