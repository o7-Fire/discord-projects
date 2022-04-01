import nextcord as discord
from perlin_noise import PerlinNoise
import random
import time
import math
import os

TOKEN = ""
client = discord.Client()
currentgame = {}

class Movement(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='<<', description='Move the character to the left by 5 units', emoji='◀'),
            discord.SelectOption(label='<', description='Move the character to the left by 1 units', emoji='⬅'),
            discord.SelectOption(label='^', description='Move the character up', emoji='⬆'),
            discord.SelectOption(label='V', description='Move the character down', emoji='⬇'),
            discord.SelectOption(label='>', description='Move the character to the right by 1 units', emoji='➡'),
            discord.SelectOption(label='>>', description='Move the character to the right by 5 units', emoji='▶'),
        ]
        super().__init__(placeholder='Movement', min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        msg = interaction.message
        user = interaction.user
        option = self.values[0]

        # handle options
        if option == "<<":
            currentgame[str(user.id)]["Position"]["x"] -= 5
            await msg.edit(embed=discord.Embed(description=render(msg, user)))
        elif option == "<":
            currentgame[str(user.id)]["Position"]["x"] -= 1
            await msg.edit(embed=discord.Embed(description=render(msg, user)))
        elif option == "^":
            currentgame[str(user.id)]["Position"]["y"] += 1
            await msg.edit(embed=discord.Embed(description=render(msg, user)))
        elif option == "V":
            currentgame[str(user.id)]["Position"]["y"] -= 1
            await msg.edit(embed=discord.Embed(description=render(msg, user)))
        elif option == ">":
            currentgame[str(user.id)]["Position"]["x"] += 1
            await msg.edit(embed=discord.Embed(description=render(msg, user)))
        elif option == ">>":
            currentgame[str(user.id)]["Position"]["x"] += 5
            await msg.edit(embed=discord.Embed(description=render(msg, user)))
            
class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Movement())

def generatechunks(message, user=0):
    if user == 0:
        user = message.author
    noises = []
    seed = currentgame[str(user.id)]["seed"]
    noise = PerlinNoise(octaves=3, seed=seed)
    noise2 = PerlinNoise(octaves=6, seed=seed)
    noise3 = PerlinNoise(octaves=12, seed=seed)
    noise4 = PerlinNoise(octaves=24, seed=seed)
    for x in range(14): #3 extra range
        for y in range(13):
            plrx = currentgame[str(user.id)]["Position"]["x"]
            plry = currentgame[str(user.id)]["Position"]["y"] - 4
            tx = currentgame[str(user.id)]["Position"]["x"] + x - 8
            ty = currentgame[str(user.id)]["Position"]["y"] + y - 7
            do = True
            if plrx == x and plry == y:
                currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "head"
                do = False
            elif plrx == x and plry == y - 1:
                currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "body"
                do = False
            
            if do:
                if not f"{str(tx)}X{str(ty)}" in currentgame[str(user.id)]["gamechunks"]:
                    thenoise = noise([x / 14, y / 13]) * 100
                    thenoise += 0.5 * noise2([x / 14, y / 13]) * 100
                    thenoise += 0.25 * noise3([x / 14, y / 13]) * 100
                    thenoise += 0.125 * noise4([x / 14, y / 13]) * 100
                    noises.append(thenoise)
                    if thenoise > -10:
                        currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "stone"
                    elif thenoise < -10:
                        currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "sky"
                
                """
                if 5 < thenoise < 10:
                    currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "grass"
                elif 10 < thenoise < 20:
                    currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "dirt"
                elif 20 < thenoise < 30:
                    currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "stone"
                else:
                    currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "sky"
                """
    lastsmallnoise = 0
    lastbignoise = 0
    for n in noises:
        if n > lastbignoise:
            lastbignoise = n
        elif n < lastsmallnoise:
            lastsmallnoise = n
    print("lowest noise", lastsmallnoise)
    print("highest noise", lastbignoise)
    
def render(message, user=0):
    if user == 0:
        user = message.author
    generatechunks(message, user)
    finalmessage = f"Game user: {str(user)}\n"
    for y in reversed(range(10)):
        for x in range(11):
            tx = currentgame[str(user.id)]["Position"]["x"] + x - 5
            ty = currentgame[str(user.id)]["Position"]["y"] + y - 4
            tile = currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"]
            if tile == "head":
                finalmessage += "<:head:939816513853063218>"
            elif tile == "body":
                finalmessage += "<:body:939816528277307412>"
            elif tile == "grass":
                finalmessage += "<:g_:939809738852548628>"
            elif tile == "dirt":
                finalmessage += "<:d_:939809769462566983>"
            elif tile == "stone":
                finalmessage += "<:s_:939809867902910524>"
            elif tile == "sky":
                finalmessage += "<:background:939815809117724703>"
        finalmessage += "\n"
    return finalmessage

@client.event
async def on_ready():
    print(str(client.user) + ' has connected to Discord!')
    
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == "start game2":
        random.seed()
        octaves = random.random()
        freq = 150.0 * octaves
        currentgame[str(message.author.id)] = {
            "seed": freq,
            "Position": {
                "x":0, "y":0
            },
            "inventory": {
                "wood": 0, "dirt": 0, "stone": 0,
            },
            "gamechunks": {
            
            }
        }
        embed = discord.Embed(description=render(message))
        await message.channel.send(embed=embed, view=DropdownView())
        
client.run(TOKEN)
