import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.environ['TOKEN']

reaper = commands.Bot(command_prefix='!!')

@reaper.command(name="greet")
async def greeting(ctx, user: discord.Member):
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
async def greeting(ctx):
    await ctx.send()

@reaper.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("This Member does not exist !")


reaper.run(TOKEN)
reaper.close()
