"""Personal-name composition, source isolation, and command-line regression checks."""
import json
import subprocess
import sys
import unittest
from namebot import ROOT, Engine, GenerationError

class RendererTests(unittest.TestCase):
    def test_all_personal_nam_sources(self):
        sources = outputs = 0
        for file in sorted((ROOT / 'data').glob('*.json')):
            resource = json.loads(file.read_text())
            for p in resource['programs']:
                if p['entrypoint'] is not None or not any(t.get('pool') == 'given' for t in p['tables'].values()):
                    continue
                sources += 1
                engine = Engine(resource, 419)
                for gender in [None, 'male', 'female']:
                    labels = [gender.upper()] if gender else ['MALE','FEMALE']
                    given = {engine.records[i]['value'] for label in labels for i in p['tables'].get(p['id']+'/'+label,{}).get('entries',[])}
                    families = {engine.records[i]['value'] for i in p['tables'].get(p['id']+'/LAST NAMES',{}).get('entries',[])} or {''}
                    family_first = resource['profiles'][0]['name_order'][0] == 'family'
                    for _ in range(50):
                        value = engine.compose(p['id'], gender)
                        # Exact component membership; do not split multiword names.
                        self.assertTrue(any(value == (' '.join(x for x in (f,g) if x) if family_first else ' '.join(x for x in (g,f) if x)).strip() for g in given for f in families))
                        self.assertNotIn('a,m,', value)
                        outputs += 1
        self.assertEqual(sources,16)
        print(f'NAM renderer: {sources} personal source programs, {outputs} outputs')

    def test_blank_family_and_multiple_given_names(self):
        r={'id':'fixture','pools':{'given':[{'id':'a','value':'Mary Ann'}, {'id':'b','value':'Anne-Marie'}], 'family':[{'id':'c','value':''}]},
           'profiles':[{'name_order':['given','family']}], 'programs':[{'id':'p','entrypoint':None,'tables':{'p/FEMALE':{'pool':'given','entries':['a','b']}, 'p/LAST NAMES':{'pool':'family','entries':['c']}}}]}
        e=Engine(r,3)
        self.assertIn(e.compose('p','female',2),['Mary Ann Anne-Marie','Anne-Marie Mary Ann'])
        with self.assertRaises(GenerationError):e.compose('p','male')
        with self.assertRaises(GenerationError):e.compose('p','female',3)
        for i in ['gangs','native_american_legacy']:
            resource=json.loads((ROOT/'data'/f'{i}.json').read_text())
            with self.assertRaises(GenerationError):Engine(resource).compose(resource['programs'][0]['id'])

    def test_english_profile_eligibility(self):
        r=json.loads((ROOT/'data/english.json').read_text())
        outputs=0
        for p in r['profiles']:
            tags=set(p['eligible_profile_tags'])
            family={v['value'] for v in r['pools']['family'] if tags.intersection(v['profiles'])}
            for gender in ['male','female']:
                given={v['value'] for v in r['pools']['given'] if gender in v['genders'] and tags.intersection(v['profiles'])}
                a,b=Engine(r,100),Engine(r,100)
                for _ in range(50):
                    value=a.profile_name(p['id'],gender)
                    self.assertEqual(value,b.profile_name(p['id'],gender))
                    self.assertTrue(any(value==g+' '+f for g in given for f in family))
                    outputs+=1
        print(f'English profiles: {outputs} outputs')

    def test_cli_rejects_conflicting_controls(self):
        cases=[['english','--profile','british','--program','american'], ['english','--program','american','--gender','female'], ['english','--program','american','--full-name','--table','american/MALE']]
        for case in cases:
            result=subprocess.run([sys.executable,str(ROOT/'tools/namebot.py'),*case],capture_output=True,text=True)
            self.assertEqual(result.returncode,2)
            self.assertNotIn('Traceback',result.stderr)
        result=subprocess.run([sys.executable,str(ROOT/'tools/namebot.py'),'basque','--full-name','--gender','female','--count','3'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(len(result.stdout.splitlines()),3)

if __name__=='__main__':unittest.main(verbosity=2)
