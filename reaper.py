import os
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.environ['TOKEN']

reaper = commands.Bot(command_prefix='!!')

@reaper.event
async def on_ready():
    activity = discord.Game(name="DEVELOPMENT UwU!", type="DEVELOPING")
    await reaper.change_presence(status=discord.Status.online, activity=activity)
    print("Bot is ready!")

@reaper.command(name="greet", help="Greet another user")
async def greeting(ctx, user: discord.Member=None):
    if user != None:
        await ctx.send(f"Hello {user.mention}")
    else:
        await ctx.send("Define a user to greet :)")

@reaper.command(name="set prefix")
@commands.is_owner()
async def set_prefix(ctx, pre=None):
    if pre:
        ctx.send(f"Now the new prefix is {prefix}")
    else:
        ctx.send("please choose a char as a prefix")

@reaper.command(name="ohio")
async def ohioo(ctx):
    _list = [
        'https://i.imgur.com/M6j1RZ4.gif',
        'https://i.imgur.com/i0KxeWD.gif',
        'https://i.imgur.com/fAkisXI.gif',
        'https://i.imgur.com/g81n9Nd.gif',
    ]
    await ctx.send(f"{_list[random.randint(0,len(_list))]} \
                        \n {ctx.message.author.mention} OHIO !!!!!")

@reaper.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("This Member does not exist !")


reaper.run(TOKEN)
