# Discord Bot

Music streaming discord bot created with [Discord.py](https://github.com/Rapptz/discord.py).

## Features

- General Commands
  - `greet` is used to greet another user
  - `mass_ping` is used to rapidly mention a user certain times. **CAUTION** can only be used by admins
  - `ohio` replys back with a mention and a gif
  - `set_presence` command set/change the bot's activity status but can only be used by admins

- Music
  - `play` command invokes voice client to first join the requested user's voice channel than it grabs the requested music form youtube and streams it
  - `join` command only invokes the voice client to join the voice channel
  - `pause` the current state of the voice client
  - `resume` resumes the paused stream
  - `skip` skips the current music and stream the next one from the queue
  - `queue` returns an embed object which displays upcoming queue
  - `volume` is used to set the volume level of the voice client
  - `disconnet` is used to disconnect the voice client from the voice channel
- Anilist
  - `manga`command request [Anilist's](https://anilist.co) graphql for the requested manga and returns an embed with all of the appropriate information
  - `anime` command also request [Anilist's](https://anilist.co) graphql for the requested anime and returns an embed with all of the appropriate information
- Other
  - `help` displays description of all commands


## How to use ?

To run this bot first you need to install the dependencies by running

```sh
pip install -r requirements.txt
```
after installing dependencies you need to install [ffmpeg](https://www.ffmpeg.org) and [opus](https://opus-codec.org) on your machine.

last but not least create a `.env` file in the root directory and put your discord token in it like

```sh
TOKEN = YOUR_TOKEN
```

once everything is done simply call the `bot.py` file

```sh
python bot.py
```

and it will be up and running 😊
