"""SR1e-3e Namebot slash-command adapter. Importing does not connect to Discord."""
import io
import logging
import os
import discord
from discord import app_commands
from namebot import GenerationError
from name_service import NameService

log=logging.getLogger('namebot')

def make_client(service=None):
    service=service or NameService()
    class Client(discord.Client):
        async def setup_hook(self):
            # Sync only on explicit configuration; avoid repeated startup writes.
            if os.environ.get('SYNC_COMMANDS')=='1':
                guild_id=os.environ.get('DISCORD_GUILD_ID')
                if guild_id:
                    guild=discord.Object(id=int(guild_id))
                    self.tree.copy_global_to(guild=guild)
                    await self.tree.sync(guild=guild)
                else:
                    await self.tree.sync()
    client=Client(intents=discord.Intents.none(),allowed_mentions=discord.AllowedMentions.none())
    client.tree=app_commands.CommandTree(client)

    async def send(interaction, text, private=False):
        kwargs={'ephemeral':private,'allowed_mentions':discord.AllowedMentions.none()}
        safe=discord.utils.escape_markdown(text)
        if len(safe)<=1900:
            await interaction.response.send_message(safe,**kwargs)
        else:
            await interaction.response.send_message('Results attached.',file=discord.File(io.BytesIO(text.encode('utf-8')),filename='namebot-results.txt'),**kwargs)

    async def resource_choices(interaction,current):
        return [app_commands.Choice(name=r['label'][:100],value=k) for k,r in service.resources.items() if current.casefold() in (k+' '+r['label']).casefold()][:25]

    async def program_choices(interaction,current):
        r=service.resources.get(getattr(interaction.namespace,'set',None),{})
        return [app_commands.Choice(name=p['id'],value=p['id']) for p in r.get('programs',[]) if current.casefold() in p['id'].casefold()][:25]

    async def profile_choices(interaction,current):
        r=service.resources.get(getattr(interaction.namespace,'set',None),{})
        return [app_commands.Choice(name=p['id'],value=p['id']) for p in r.get('profiles',[]) if current.casefold() in p['id'].casefold()][:25]

    @client.tree.command(name='names',description='Generate names from a selected naming set.')
    @app_commands.rename(resource='set')
    @app_commands.autocomplete(resource=resource_choices,program=program_choices,profile=profile_choices)
    @app_commands.choices(gender=[app_commands.Choice(name='Male',value='male'),app_commands.Choice(name='Female',value='female')])
    async def names(interaction:discord.Interaction,resource:str,count:app_commands.Range[int,1,20]=1,program:str|None=None,profile:str|None=None,gender:str|None=None,private:bool=False):
        try:
            results=service.generate(resource,count,program,profile,gender)
        except GenerationError as exc:
            await send(interaction,str(exc),True)
            return
        await send(interaction,'\n'.join(f'{i}. {name}' for i,name in enumerate(results,1)),private)

    @client.tree.command(name='name_sets',description='List available naming sets.')
    async def name_sets(interaction:discord.Interaction):
        await send(interaction,'\n'.join(resource['label'] for resource in service.resources.values()),True)

    @client.tree.command(name='name_options',description='List programs and profiles for a naming set.')
    @app_commands.rename(resource='set')
    @app_commands.autocomplete(resource=resource_choices)
    async def name_options(interaction:discord.Interaction,resource:str):
        try:
            text=service.options(resource)
        except GenerationError as exc:
            text=str(exc)
        await send(interaction,text,True)

    @client.tree.error
    async def error(interaction:discord.Interaction,exc:app_commands.AppCommandError):
        log.error('Namebot command failed',exc_info=(type(exc),exc,exc.__traceback__))
        text='The command could not finish. Check the bot logs.'
        if interaction.response.is_done():
            await interaction.followup.send(text,ephemeral=True,allowed_mentions=discord.AllowedMentions.none())
        else:
            await send(interaction,text,True)
    return client

def main():
    token=os.environ.get('DISCORD_TOKEN')
    if not token:
        raise SystemExit('Set DISCORD_TOKEN in the hosting environment before starting Namebot.')
    guild=os.environ.get('DISCORD_GUILD_ID')
    if guild and (not guild.isdecimal() or int(guild)<=0):
        raise SystemExit('DISCORD_GUILD_ID must be a positive numeric server ID.')
    make_client().run(token)

if __name__=='__main__':
    main()
