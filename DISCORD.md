# SR1e-3e Namebot on Discord

## Quick start

Run `/name_help` in Discord for a private walkthrough and a command example.

1. Type `/name_sets`, select the Namebot command from Discord’s suggestions, and send it. Namebot replies privately with the available lists.
2. Type `/names`, select the Namebot command, and use **set** to pick a list. Use **count** to generate 1–20 results. The default is one.
3. If a set requires a **profile** or **program**, Namebot shows the available choices when you leave both blank. To see the choices and source credits ahead of time, run `/name_options` with the same set. It shows the available choices and any source credit listed for that set. Choose either a profile or a program for a given roll.
4. Set **private** to **True** if you want the generated names visible only to you. Results are posted in the channel by default.

| To generate | Example |
| --- | --- |
| Five British English names | `/names set:english profile:british count:5` |
| Three Japanese names | `/names set:japanese program:japanese count:3` |
| Five Roman names | `/names set:latin program:roman_male count:5` |
| Five company names | `/names set:geordi_gizmo_company count:5` |
| Five technical names | `/names set:geordi_gizmo_technical count:5` |

Both Geordi Gizmo sets are by Joel Crook. The [source credits](README.md#name-source-credits) are also listed in the README.

Use **gender** when the selected set or program supports it. If a program has its own gender rules, pick the program and leave **gender** blank. Long results arrive as a UTF-8 text attachment.

## Set up Namebot

1. Create an **SR1e-3e Namebot** application at https://discord.com/developers/applications and obtain its bot token.
2. Add Namebot to your Discord server with the `bot` and `applications.commands` scopes. Allow View Channels, Send Messages and Attach Files in the intended channel. Administrator permission is unnecessary.
3. Configure the environment variables below in the hosting service's private settings. Never put the token in source files or send it in chat.
4. Install dependencies and run from the extracted package directory:

```sh
python -m pip install -r requirements.txt
python -X utf8 tools/discord_bot.py
```

| Variable | Purpose |
| --- | --- |
| `DISCORD_TOKEN` | Required secret token for the Namebot application. |
| `DISCORD_GUILD_ID` | Your Discord server ID used when synchronizing server commands. |
| `SYNC_COMMANDS` | Set to `1` for a command-registration startup; otherwise leave unset or `0`. |

Set `DISCORD_GUILD_ID` and `SYNC_COMMANDS=1` for the initial registration on your server. After successful registration, set `SYNC_COMMANDS=0` and restart normally. A startup with synchronization enabled and no guild ID registers commands globally. Changing scope does not remove commands previously registered in another scope.

The included Procfile defines a worker start command. The bot requires a continuously running Python process and outbound Discord connectivity; it does not serve an HTTP page. No database is required. Message Content and other privileged intents are not enabled. This gateway-based adapter does not need an Interactions Endpoint URL.

## Local verification

```sh
python -X utf8 tools/test_discord.py
```

Tests use the real Discord SDK with mocked responses and synchronization, covering command payloads, autocomplete limits, name-generation routes, invalid selections, private errors, mention suppression and attachment output. No test sends a Discord message or registers a command. Existing runtime and renderer tests remain available in RUNNING.md.

## Live test after installation

Run `/name_sets`, `/name_options`, and the examples above in your Discord server. Confirm private results, public results, correct name counts and autocomplete. Try an invalid program and verify it returns a private explanation. This live server test is still outstanding.

SDK reference: https://discordpy.readthedocs.io/en/v2.6.4/interactions/api.html
