import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from cogs import general, music

load_dotenv()
TOKEN = os.environ.get('TOKEN')

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!!"),
                   description='ALL-IN-ONE BOT :)')

@bot.event
async def on_ready():
    print("Bot is ready!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send("This Member does not exist !")
    print(error)

bot.add_cog(music.Music(bot))
bot.add_cog(general.General(bot))
bot.run(TOKEN)
