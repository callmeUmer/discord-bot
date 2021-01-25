import os
import discord
import random
import nacl
import validators
import sys
from discord.ext import commands


class General(commands.Cog):
    """Cog that handles general commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="greet", help="Greet another user")
    async def greeting(self, ctx, user: discord.Member=None):
        if user is not None:
            await ctx.send(f"Hello {user.mention}")
        else:
            await ctx.send("Define a user to greet :)")


    @commands.command(name="set_prefix")
    @commands.has_role("echelon")
    async def set_prefix(self, ctx, pre=None):
        if pre:
            await ctx.send(f"Now the new prefix is {prefix}")
        else:
            await ctx.send("please choose a char as a prefix")


    @commands.command(name="ohio", help="KAWAIII")
    async def ohioo(self, ctx):
        _list = [
            'https://i.imgur.com/M6j1RZ4.gif',
            'https://i.imgur.com/i0KxeWD.gif',
            'https://i.imgur.com/fAkisXI.gif',
            'https://i.imgur.com/g81n9Nd.gif',
        ]
        await ctx.send(f"{_list[random.randint(0,len(_list))]} \
                            \n {ctx.message.author.mention} OHIO !!!!!")


    @commands.command("set_presence", help="set the presence to given str")
    @commands.has_role("echelon")
    async def set_presence(self, ctx, *, args=None):
        if args is not None:
            activity = discord.Game(name=args, type=3)
            await self.bot.change_presence(status=discord.Status.online, activity=activity)
            await ctx.send(f"Changed the Presence to `{args}`")
        else:
            await ctx.send("Please define the presence")


    @commands.command("mass_ping", help="takes two args 1=user 2=times (only admin)")
    @commands.has_role("echelon")
    async def mass(self, ctx, user:discord.Member = None, iter: int = 10):
        if user is not None:
            for i in range(iter):
                await ctx.send(user.mention)
        else:
            await ctx.send("You didn't define a user to ping")


    @commands.command("reboot", help="DON'T EVEN THINK ABOUT IT")
    @commands.is_owner()
    async def reboot(self, ctx):
        await ctx.send("REBOOTING ........")
        await ctx.bot.logout()
