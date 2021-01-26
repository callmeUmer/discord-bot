import youtube_dl
import discord
from discord.ext import commands
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
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url']
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    """Cog that handles Music stuff"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command("play", help="Plays from keywords or URL")
    async def play(self, ctx, *, query):
        """Plays the music from given query"""
        valid = validators.url(query)
        query = query if valid else "ytsearch:" + query

        async with ctx.typing():
            source = await YTSource.from_url(url=query, loop=self.bot.loop)
            error = lambda e: print('Player error: %s' % e) if e else None
            ctx.voice_client.play(source, after=error)

        await ctx.send('Now playing: `{}`'.format(source.data['title']))


    @commands.command("join", help="Joins a voice channel")
    @play.before_invoke
    async def join(self, ctx):
        """Joins the voice channel"""
        if ctx.author.voice is not None:
            channel = ctx.author.voice.channel
            if ctx.voice_client is not None:
                if ctx.voice_client.is_playing():
                    ctx.voice_client.stop()
                await ctx.voice_client.move_to(channel)
            else:
                await channel.connect()
                await ctx.send(f"Successfully connected to `{channel}` on the request of {ctx.author.mention}")
        else:
            await ctx.send(f"{ctx.message.author.mention} you are not connected to a voice channel")


    @commands.command("stop", help="Disconnects from a voice channel")
    async def stop(self, ctx):
        if ctx.voice_client is not None:
            return await ctx.voice_client.disconnect()
