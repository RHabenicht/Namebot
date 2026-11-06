# Namebot on Discord

## Quick start

1. Run `/name_sets` to see the available lists. Select the command under Namebot if Discord shows more than one match.
2. Run `/names` and choose a `set`. Set `count` from 1 to 20. The default is one.
3. Run `/name_options` with the same set to see the available programs and profiles, along with any source credit. If the set needs a choice, pick one `profile` or `program`.
4. Set `private` to `True` for a reply only you can see. By default `/names` replies in the channel.

`/name_help` gives you a private command example. Use `gender` when the selected set or program supports it. For a program with its own gender rules, leave that option blank. Long replies arrive as a UTF-8 text file.

| To generate | Example |
| --- | --- |
| Five British English names | `/names set:english profile:british count:5` |
| Three Japanese names | `/names set:japanese program:japanese count:3` |
| Five Roman names | `/names set:latin program:roman_male count:5` |
| Five company names | `/names set:geordi_gizmo_company count:5` |
| Five technical names | `/names set:geordi_gizmo_technical count:5` |

Both Geordi Gizmo sets come from Joel Crook. [Name source credits](README.md#name-source-credits)

## Host your own copy

1. Create a Namebot application and get its bot token. [Discord Developer Portal](https://discord.com/developers/applications)
2. Install your copy with the `bot` and `applications.commands` scopes. Grant **View Channels**, **Send Messages**, and **Attach Files** in the channels where it will run.
3. Set the variables below in your host’s private environment settings.
4. Run these commands from the project folder.

```sh
python -m pip install -r requirements.txt
python -X utf8 tools/discord_bot.py
```

| Variable | Use |
| --- | --- |
| `DISCORD_TOKEN` | Bot token for your Discord application. Required. |
| `DISCORD_GUILD_ID` | Server ID for a server-only command registration. Leave unset for global registration. |
| `SYNC_COMMANDS` | Set to `1` for a startup that registers commands. Set to `0` or leave unset for normal startup. |

For a test server, start with `SYNC_COMMANDS=1` and `DISCORD_GUILD_ID` set to the server ID. For global registration, start with `SYNC_COMMANDS=1` and leave `DISCORD_GUILD_ID` unset. After registration succeeds, restart with `SYNC_COMMANDS=0`. Discord stores server and global registrations separately.

The `Procfile` starts Namebot as a worker. Keep the worker running with outbound access to Discord. It reads the local JSON data and connects through the Discord Gateway. Leave the Interactions Endpoint URL blank and privileged intents off.

## Check a deployment

In your test server, run `/name_sets`, `/name_options`, and a few `/names` examples. Check that Discord suggests the available lists, that each command returns the requested count, and that private replies are visible only to you. An invalid program should return a private error.

Run the offline adapter tests from the project folder.

```sh
python -X utf8 tools/test_discord.py
```

The offline tests use the Discord SDK with mocked replies and command registration. They cover autocomplete, valid and invalid requests, private replies, mention suppression, and attachments. Live server testing is pending in the project’s test record. [Validation results](VALIDATION.json)

[Generator tests](RUNNING.md#verification) · [Discord SDK reference](https://discordpy.readthedocs.io/en/v2.6.4/interactions/api.html)
