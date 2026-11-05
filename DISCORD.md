# SR1e-3e Namebot on Discord

The slash-command adapter is implemented and passed six offline tests using discord.py 2.6.4. It has not been logged into Discord, installed in a server, or deployed. Keep this application separate from SR1e-3eGamebot.

## Commands

- `/name_sets`: list available data sets, visible only to you.
- `/name_options set:english`: list program and profile identifiers, visible only to you.
- `/names set:latin program:roman_male count:5`
- `/names set:english profile:british gender:Female count:5`
- `/names set:japanese program:japanese gender:Female count:5`
- `/names set:old_norse gender:Female count:5`
- `/names set:filipino gender:Female count:5`
- `/names set:technical_english program:geordi_gizmo_company count:5`

Set `private:True` to show generated results only to yourself. Public results are the default. Requests allow 1–20 names. Output that exceeds the message budget is returned as a UTF-8 text attachment. Mention parsing is disabled.

Program and profile controls are alternatives. Multiple-program sets require an explicit selection, except Hawaiian, Khmer and Filipino, which select their unfiltered or gendered program automatically. Legacy NAM personal-name programs compose full names. Old Norse maps the gender option to its source prompt. Other procedural programs retain their own gender rules: choose the appropriate program and leave gender blank. Profiles backed by explicit programs and the four English regional profiles are supported; generic legacy `default` profiles still require a program selection. Gang and Native American legacy components remain available through the local command line, not automatic Discord composition.

## Start a separate application

1. Create a dedicated **SR1e-3e Namebot** application at https://discord.com/developers/applications and obtain its bot token.
2. Install it in your test server with the `bot` and `applications.commands` scopes. Allow View Channels, Send Messages and Attach Files in the intended channel. Administrator permission is unnecessary.
3. Configure the environment variables below in the hosting service's private settings. Never put the token in source files or send it in chat.
4. Install dependencies and run from the extracted package directory:

```sh
python -m pip install -r requirements.txt
python -X utf8 tools/discord_bot.py
```

| Variable | Purpose |
| --- | --- |
| `DISCORD_TOKEN` | Required secret token for the separate Namebot application. |
| `DISCORD_GUILD_ID` | Test server ID used when synchronizing server commands. |
| `SYNC_COMMANDS` | Set to `1` for a command-registration startup; otherwise leave unset or `0`. |

Set `DISCORD_GUILD_ID` and `SYNC_COMMANDS=1` for the initial test-server registration. After successful registration, set `SYNC_COMMANDS=0` and restart normally. A startup with synchronization enabled and no guild ID registers commands globally. Changing scope does not remove commands previously registered in another scope. Use the dedicated application so synchronization cannot replace the dicebot's commands.

The included Procfile defines a worker start command. The bot requires a continuously running Python process and outbound Discord connectivity; it does not serve an HTTP page. No database is required. Message Content and other privileged intents are not enabled. This gateway-based adapter does not need an Interactions Endpoint URL.

## Local verification

```sh
python -X utf8 tools/test_discord.py
```

Tests use the real Discord SDK with mocked responses and synchronization, covering command payloads, autocomplete limits, name-generation routes, invalid selections, private errors, mention suppression and attachment output. No test sends a Discord message or registers a command. Existing runtime and renderer tests remain available in RUNNING.md.

## Live test after installation

Run `/name_sets`, `/name_options`, and the examples above in the test server. Confirm private results, public results, correct name counts and autocomplete. Try an invalid program and verify it returns a private explanation. This live server test is still outstanding.

SDK reference: https://discordpy.readthedocs.io/en/v2.6.4/interactions/api.html
