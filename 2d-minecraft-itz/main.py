import nextcord as discord
import os
from Game import Game
from View import DropdownView

TOKEN = "" or os.environ.get("TOKEN")
client = discord.Client()


@client.event
async def on_ready():
    print(str(client.user) + ' has connected to Discord!')


games: dict = {}


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == "test":
        embed = discord.Embed(title="Test", description="This is a test embed", color=0x00ff00)
        embed.set_author(name="Test Author")
        embed.set_footer(text="Test Footer")
        await message.channel.send(embed=embed)
    if message.content.startswith("!game"):
        if message.author.id in games:
            await message.channel.send("You are already in a game!")
            return
        game = Game(message.author.id)
        games[message.author.id] = game
        embed = discord.Embed(title="Game", description=await game.render(), color=0x00ff00)
        embed.set_author(name=message.author.name)
        await message.channel.send(embed=embed, view=DropdownView(game))
    if message.content.startswith("!delete"):
        if message.author.id not in games:
            await message.channel.send("You are not in a game!")
            return
        games[message.author.id].delete()
        del games[message.author.id]


client.run(TOKEN)
