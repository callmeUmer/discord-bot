import os
import re
import discord
import requests
import json
from discord.ext import commands

ANIME_QUERY = """
query ($query: String) {
  Page {
    media(search: $query, type: ANIME) {
      id
      title {
        romaji
        english
        native
      }
      coverImage {
        large
        color
      }
      format
      type
      bannerImage
      description
      averageScore
      popularity
      episodes
      season
      hashtag
      isAdult
      startDate {
        year
        month
        day
      }
      endDate {
        year
        month
        day
      }
    }
  }
}
"""

ANILIST_API_URL = "https://graphql.anilist.co"
ANILIST_IMAGE_URL = "https://img.anili.st/media/"



class Anime(commands.Cog):
    """Cog utilizes anilist's graphql api to search for an anime"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="anime")
    async def anime(self, ctx, *, title):
        response = self.request_anime(title)
        await ctx.send(embed=self.create_embed(response.json()))

    def create_embed(self, response):
        try:
            first_entry = response['data']['Page']['media'][0]

            emb = discord.Embed(
                title = self.get_title(first_entry),
                description = self.get_cleaned_desc(first_entry),
                color = self.get_color(first_entry))

            emb.add_field(name = "Romaji",
                value = first_entry["title"]["romaji"],
                inline = True)

            emb.add_field(name = "English",
                value = first_entry["title"]["english"],
                inline = True)

            emb.add_field(name = "Native",
                value = first_entry["title"]["native"],
                inline = True)

            emb.add_field(name = "Average Score",
                value = str(first_entry["averageScore"]) + '%',
                inline = True)

            emb.add_field(name = "Episodes",
                value = first_entry["episodes"],
                inline = True)

            emb.add_field(name = "Season",
                value = first_entry["season"],
                inline = True)

            emb.add_field(name = "Start Date",
                value = self.format_date(first_entry["startDate"]),
                inline = True)

            emb.add_field(name = "End Date",
                value = self.format_date(first_entry["endDate"]),
                inline = True)

            emb.set_image(url = ANILIST_IMAGE_URL + str(first_entry["id"]))
            return emb
        except IndexError:
            emb = discord.Embed(title = "Anime Not Found",
            color = discord.Color.red())
            return emb

    def request_anime(self, title):
        q = {"query": ANIME_QUERY, "variables":{"query": title}}
        return requests.post(ANILIST_API_URL, json=q)

    def get_title(self, res):
        return res["title"]["english"]

    def get_cleaned_desc(self, res):
        p = re.compile(r'<.*?>')
        return p.sub('', res["description"])

    def get_color(self, res):
        code = res["coverImage"]['color'][1:] # remove hash from str
        return int(f"0x{code}", 16)

    def format_date(self, date):
        return f"{date['day']}/{date['month']}/{date['year']}"
