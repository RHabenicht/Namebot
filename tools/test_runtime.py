"""Runtime integration and semantic regression tests. Run from any directory."""
import json
import unittest
from namebot import Engine, GenerationError, ROOT

class RuntimeTests(unittest.TestCase):
    def test_all_bundled_programs_and_component_tables(self):
        programs = outputs = tables = 0
        for path in sorted((ROOT / 'data').glob('*.json')):
            resource = json.loads(path.read_text(encoding='utf-8'))
            engine = Engine(resource, 54321)
            for p in resource['programs']:
                programs += 1
                targets = [None] if p['entrypoint'] else list(p['tables'])
                for target in targets:
                    tables += 1
                    if target and not p['tables'][target]['entries']:
                        with self.assertRaises(GenerationError):
                            engine.generate(p['id'], table=target)
                        continue
                    for _ in range(100):
                        value = engine.generate(p['id'], table=target)
                        self.assertIsInstance(value, str)
                        if target is None:
                            self.assertTrue(value)
                        else:
                            expected = {engine.records[i]['value'].strip() for i in p['tables'][target]['entries']}
                            self.assertIn(value, expected)
                        outputs += 1
        print(f'Integration: {programs} programs, {tables} entrypoints/component tables, {outputs} outputs')

    def test_norse_gender_assignments_and_seed(self):
        resource = json.loads((ROOT / 'data/old_norse.json').read_text())
        for gender in ['Male', 'Female', 'Random']:
            a, b = Engine(resource, 17), Engine(resource, 17)
            for _ in range(100):
                output = a.generate('old_norse_names', {'prompt1': gender})
                self.assertEqual(output, b.generate('old_norse_names', {'prompt1': gender}))
                self.assertTrue(a.variables['name'])
                self.assertTrue(a.variables['surname'])
                self.assertIn(a.variables['gender'], ['Male', 'Female'])
                if gender != 'Random':
                    self.assertEqual(a.variables['gender'], gender)
        with self.assertRaises(GenerationError):
            a.generate('old_norse_names', {'prompt1': 'invalid'})

    def fixture(self):
        r = {'pools': {'x': [{'id': 'a', 'value': 'A'}, {'id': 'b', 'value': 'B'}]},
             'programs': [{'id': 'p', 'prompts': [], 'definitions': [], 'entrypoint': 'pool', 'tables': {
                 'pool': {'mode': 'pool', 'entries': ['a', 'b']},
                 'weighted': {'mode': 'weighted', 'entries': [{'weight': 3, 'value': {'op':'text','value':'A'}}, {'weight':1,'value':{'op':'text','value':'B'}}]},
                 'dict': {'mode': 'dictionary', 'entries': [{'key': 7, 'entry': 'a'}]},
                 'ranges': {'mode': 'lookup', 'entries': [{'range':[1,3], 'value':{'op':'text','value':'A'}}, {'range':[4,5], 'value':{'op':'text','value':'B'}}]}
             }}]}
        e = Engine(r, 5);e.generate('p');return e

    def test_decks_weights_lookups_and_reset(self):
        e = self.fixture()
        self.assertEqual({e.table('pool', deck=True) for _ in range(2)}, {'A','B'})
        self.assertEqual({e.table('pool', deck=True) for _ in range(2)}, {'A','B'})
        cards = [e.table('weighted', deck=True) for _ in range(4)]
        self.assertEqual(sorted(cards), ['A','A','A','B'])
        for key, expected in [(1,'A'),(3,'A'),(4,'B'),(5,'B')]:
            self.assertEqual(e.table('ranges', key=key), expected)
        self.assertEqual(e.table('dict', key=7), 'A')
        for table, key in [('ranges', 6), ('dict', 8)]:
            with self.assertRaises(GenerationError): e.table(table,key=key)
        e.variables['stale'] = 'bad';e.generate('p')
        self.assertNotIn('stale',e.variables);self.assertEqual(e.decks,{})

    def test_lazy_branch_and_bounds(self):
        e=self.fixture()
        n={'op':'if','test':{'op':'number','value':1},'then':{'op':'text','value':'good'},'else':{'op':'variable','name':'missing'}}
        self.assertEqual(e.node(n),'good')
        self.assertEqual(e.node({'op':'roll','table':'pool','count':{'op':'number','value':0}}),'')
        for n in [{'op':'dice','count':1,'sides':0},{'op':'roll','table':'pool','count':{'op':'number','value':1001}}]:
            with self.assertRaises(GenerationError):e.node(n)
        e.program['tables']['loop']={'mode':'weighted','entries':[{'weight':1,'value':{'op':'roll','table':'loop','count':{'op':'number','value':1}}}]}
        with self.assertRaises(GenerationError):e.generate('p',table='loop')

if __name__ == '__main__':
    unittest.main(verbosity=2)
