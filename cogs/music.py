import youtube_dl
import discord
from discord.ext import commands
from async_timeout import timeout
import validators
import itertools
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
    """Player that handles concurrent queues"""
    def __init__(self, ctx):
        self.bot = ctx.bot
        self._ctx = ctx
        self.volume = .5
        self.next = asyncio.Event()
        self.queue = asyncio.Queue()

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Player Loop which handles the queues"""
        while True:
            self.next.clear()
            source = await self.queue.get()
            self._ctx.guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            source.volume = self.volume
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
        if ctx.voice_client is None:
            return
        # get's the player for ctx
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
        """disconnects the bot from a voice channel"""
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()
            await ctx.message.add_reaction("⛔")

    @commands.command("skip", help="Play the next song queued song")
    async def skip(self, ctx):
        """skip the song to next queued one"""
        if ctx.voice_client is not None:
            ctx.voice_client.stop()
            await ctx.message.add_reaction("⏭")

    @commands.command("pause", help="Pause the Audio Source")
    async def pause(self, ctx):
        """pause the voice_client"""
        if ctx.voice_client is not None:
            if ctx.voice_client.is_playing():
                ctx.voice_client.pause()
                await ctx.message.add_reaction("⏸")

    @commands.command("resume", help="Resume the audio source")
    async def resume(self, ctx):
        """Resumes the voice_client"""
        if ctx.voice_client is not None:
            if ctx.voice_client.is_paused():
                ctx.voice_client.resume()
                await ctx.message.add_reaction("▶")

    @commands.command("queue", help="Display the playlist queue", aliases=['q', 'playlist'])
    async def playlist_info(self, ctx):
        """displays the list of queued items"""
        if ctx.voice_client is not None:
            player = self.get_player(ctx)
            if player.queue.empty():
                return ctx.send(embed=discord.Embed(title="Queue is Empty", color=discord.Color.red()))
            q = list(itertools.islice(player.queue._queue, 0, 10))
            fmt = '\n'.join(f"`{num} - {src.data['title']}`" for num, src in enumerate(q, 1))
            embed = discord.Embed(title=f"{len(q)}-Upcoming Music", description=fmt, color=discord.Color.teal())
            await ctx.send(embed=embed)

    @commands.command("volume", help="Change the volume of the voice client")
    async def change_volume(self, ctx, volume:float):
        """Changes the volume of voice client"""
        if ctx.voice_client is not None:
            if volume < 0 or volume > 100:
                return await ctx.send("Please Choose a volume from 0-100")

            player = self.get_player(ctx)
            if ctx.voice_client.source:
                ctx.voice_client.source.volume = volume / 100

            player.volume = volume / 100
            await ctx.send(f"Successfully Changed the volume to {int(volume)}%")
