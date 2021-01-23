import os
import discord
import random
import nacl
import sys
import ytdl
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.environ['TOKEN']
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!!"))


@bot.event
async def on_ready():
    print("Bot is ready!")

@bot.command(name="greet", help="Greet another user")
async def greeting(ctx, user: discord.Member=None):
    if user is not None:
        await ctx.send(f"Hello {user.mention}")
    else:
        await ctx.send("Define a user to greet :)")


@bot.command(name="set_prefix")
@commands.has_role("echelon")
async def set_prefix(ctx, pre=None):
    if pre:
        await ctx.send(f"Now the new prefix is {prefix}")
    else:
        await ctx.send("please choose a char as a prefix")


@bot.command(name="ohio", help="KAWAIII")
async def ohioo(ctx):
    _list = [
        'https://i.imgur.com/M6j1RZ4.gif',
        'https://i.imgur.com/i0KxeWD.gif',
        'https://i.imgur.com/fAkisXI.gif',
        'https://i.imgur.com/g81n9Nd.gif',
    ]
    await ctx.send(f"{_list[random.randint(0,len(_list))]} \
                        \n {ctx.message.author.mention} OHIO !!!!!")


@bot.command("set_presence", help="set the presence to given str")
@commands.has_role("echelon")
async def set_presence(ctx, *, args=None):
    if args is not None:
        activity = discord.Game(name=args, type=3)
        await bot.change_presence(status=discord.Status.online, activity=activity)
        await ctx.send(f"Changed the Presence to {args}")
    else:
        await ctx.send("Please define the presence")


@bot.command("mass_ping", help="takes two args 1=user 2=times (only admin)")
@commands.has_role("echelon")
async def mass(ctx, user:discord.Member = None, iter: int = 10):
    if user is not None:
        for i in range(iter):
            await ctx.send(user.mention)
    else:
        await ctx.send("You didn't define a user to ping")


@bot.command("play", help="Plays from the url")
async def play(ctx, *, query):

    async with ctx.typing():
        print("pre webhook")
        print(query)
        source = await ytdl.YTSource.from_url(url=query)
        print("post webhook")
        error = lambda e: print('Player error: %s' % e) if e else None
        ctx.voice_client.play(source, after=error)

    await ctx.send('Now playing: {}'.format(query))

@bot.command("join", help="Joins a voice channel")
@play.before_invoke
async def join(ctx):
    if ctx.author.voice is not None:
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
            await ctx.send(f"Successfully connected to `{channel}` on the request of {ctx.author.mention}")
    else:
        await ctx.send(f"{ctx.message.author.mention} you are not connected to a voice channel")


@bot.command("stop", help="Disconnects from a voice channel")
async def stop(ctx):
    if ctx.voice_client is not None:
        return await ctx.voice_client.disconnect()


@bot.command("reboot", help="DON'T EVEN THINK ABOUT IT")
@commands.is_owner()
async def reboot(ctx):
    await ctx.send("REBOOTING ........")
    await ctx.bot.logout()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("This Member does not exist !")
    print(error)


bot.run(TOKEN)
