"""Offline SDK and callback tests; no Discord login or network calls."""
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from name_service import NameService
from namebot import GenerationError
from discord_bot import make_client

class ServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.s=NameService()
    def test_routes(self):
        cases=[('latin',{'program':'roman_male'}),('english',{'profile':'british','gender':'female'}),('japanese',{'program':'japanese','gender':'male'}),('old_norse',{'gender':'female'}),('filipino',{'gender':'female'}),('khmer',{}),('hawaiian',{}),('technical_english',{'program':'geordi_gizmo_company'})]
        for resource,options in cases:
            values=self.s.generate(resource,20,**options)
            self.assertEqual(len(values),20)
            self.assertTrue(all(values))
    def test_errors(self):
        for resource,kwargs in [('missing',{}),('latin',{}),('latin',{'count':21}),('english',{'program':'american','profile':'british'}),('gangs',{}),('japanese',{'program':'japanesenames','gender':'female'})]:
            with self.assertRaises(GenerationError):self.s.generate(resource,**kwargs)

class AdapterTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):self.client=make_client()
    async def asyncTearDown(self):await self.client.close()
    def interaction(self):
        return SimpleNamespace(response=SimpleNamespace(send_message=AsyncMock(),is_done=lambda:False),namespace=SimpleNamespace(set='english'))
    async def test_command_payload(self):
        self.assertEqual({c.name for c in self.client.tree.get_commands()},{'names','name_sets','name_options','name_help'})
        payload=self.client.tree.get_command('names').to_dict(self.client.tree)
        options={o['name']:o for o in payload['options']}
        self.assertTrue(options['set']['autocomplete'])
        self.assertEqual(options['count']['max_value'],20)
        self.assertFalse(self.client.intents.message_content)
    async def test_callbacks_and_private_errors(self):
        i=self.interaction()
        await self.client.tree.get_command('names').callback(i,'filipino',3,gender='female')
        args,kwargs=i.response.send_message.call_args
        self.assertEqual(len(args[0].splitlines()),3)
        self.assertFalse(kwargs['allowed_mentions'].everyone)
        i=self.interaction()
        await self.client.tree.get_command('names').callback(i,'missing')
        self.assertTrue(i.response.send_message.call_args.kwargs['ephemeral'])
        i=self.interaction()
        await self.client.tree.get_command('names').callback(i,'dutch')
        self.assertIn('Programs:',i.response.send_message.call_args.args[0])
        self.assertTrue(i.response.send_message.call_args.kwargs['ephemeral'])
        i=self.interaction()
        await self.client.tree.get_command('name_help').callback(i)
        self.assertIn('/name_options',i.response.send_message.call_args.args[0].replace('\\', ''))
        self.assertTrue(i.response.send_message.call_args.kwargs['ephemeral'])
        for name,args in [('name_sets',()),('name_options',('english',))]:
            i=self.interaction();await self.client.tree.get_command(name).callback(i,*args)
            i.response.send_message.assert_awaited_once()
    async def test_long_output_attachment(self):
        service=NameService();service.generate=lambda *a:['ʻĀ'*1200]
        c=make_client(service)
        try:
            i=self.interaction();await c.tree.get_command('names').callback(i,'hawaiian')
            f=i.response.send_message.call_args.kwargs['file']
            self.assertIn('ʻĀ',f.fp.read().decode('utf-8'))
            f.close()
        finally:await c.close()
    async def test_autocomplete_and_sync_scope(self):
        command=self.client.tree.get_command('names')
        for param in ['resource','program','profile']:
            choices=await command._params[param].autocomplete(self.interaction(),'')
            self.assertLessEqual(len(choices),25)
            self.assertTrue(choices)
        with patch.dict('os.environ',{'SYNC_COMMANDS':'0'}),patch.object(self.client.tree,'sync',new_callable=AsyncMock) as sync:
            await self.client.setup_hook();sync.assert_not_awaited()
        with patch.dict('os.environ',{'SYNC_COMMANDS':'1','DISCORD_GUILD_ID':'123'}),patch.object(self.client.tree,'sync',new_callable=AsyncMock) as sync:
            await self.client.setup_hook();self.assertEqual(sync.call_args.kwargs['guild'].id,123)

if __name__=='__main__':unittest.main(verbosity=2)
