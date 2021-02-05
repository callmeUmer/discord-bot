import youtube_dl
import discord
from discord.ext import commands
from async_timeout import timeout
import validators
import asyncio
import pprint

ytdl_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_options)

class YTSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, volume=0.7):
        super().__init__(source, volume)
        self.data = data
        self.url = data.get('url')

    @classmethod
    async def stream(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url']
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Player:

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._ctx = ctx
        self.next = asyncio.Event()
        self.queue = asyncio.Queue()

        ctx.bot.loop.create_task(self.player_loop())

    def toggle_next(self):
        return self.bot.loop.call_soon_threadsafe(self.next.set)

    async def player_loop(self):
         while True:
            self.next.clear()
            source = await self.queue.get()
            self._ctx.guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            await self.next.wait()


class Music(commands.Cog):
    """Cog that handles Music stuff"""
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    def get_player(self, ctx):
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = Player(ctx)
            self.players[ctx.guild.id] = player
        return player

    async def queue_message(self, ctx, player, src):
        vc = player._ctx.guild.voice_client
        if vc is not None:
            if not vc.is_playing():
                await ctx.send(f"Playing `{src.data['title']}`")
            else:
                await ctx.send(f"Added `{src.data['title']}` to queue")



    @commands.command("play", help="Plays from keywords or URL")
    async def play(self, ctx, *, query):
        """Plays the music from given query"""
        player = self.get_player(ctx)

        async with ctx.typing():
            source = await YTSource.stream(url=query, loop=self.bot.loop)
            await player.queue.put(source)
            await self.queue_message(ctx, player, source)



    @commands.command("join", help="Joins a voice channel")
    @play.before_invoke
    async def join(self, ctx):
        """Joins the voice channel"""
        if ctx.author.voice is not None:
            channel = ctx.author.voice.channel
            if ctx.voice_client is not None:
                await ctx.voice_client.move_to(channel)
            else:
                await channel.connect()
                await ctx.send(f"Successfully connected to `{channel}` on the request of {ctx.author.mention}")
        else:
            await ctx.send(f"{ctx.message.author.mention} you are not connected to a voice channel")


    @commands.command("disconnect", help="Disconnects from a voice channel")
    async def disconnect(self, ctx):
        if ctx.voice_client is not None:
            ctx.voice_client.disconnect()
            await ctx.message.add_reaction("⛔")

    @commands.command("skip", help="Disconnects from a voice channel")
    async def stop(self, ctx):
        if ctx.voice_client is not None:
            ctx.voice_client.stop()
            ctx.message.add_reaction("⏭")

    @commands.command("pause", help="Pause the Audio Source")
    async def pause(self, ctx):
        if ctx.voice_client is not None:
            if ctx.voice_client.is_playing():
                ctx.voice_client.pause()
                ctx.message.add_reaction("⏸")

    @commands.command("resume", help="Resume the audio source")
    async def resume(self, ctx):
        if ctx.voice_client is not None:
            if ctx.voice_client.is_paused():
                ctx.voice_client.resume()
                ctx.message.add_reaction("▶")
