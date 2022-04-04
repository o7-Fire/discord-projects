import nextcord as discord
from perlin_noise import PerlinNoise
from noise import pnoise2
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
        didJumpThisInput = False
                        
        # handle options
        if option == "<<":
            currentgame[str(user.id)]["Position"]["x"] -= 5
            if not valid_movement(msg, user):
                currentgame[str(user.id)]["Position"]["x"] += 5
            await msg.edit(embed=discord.Embed(description=render(msg, user)))
        elif option == "<":
            currentgame[str(user.id)]["Position"]["x"] -= 1
            if not valid_movement(msg, user):
                currentgame[str(user.id)]["Position"]["x"] += 1
            await msg.edit(embed=discord.Embed(description=render(msg, user)))
        elif option == "^":
            didJumpThisInput = True
            currentgame[str(user.id)]["Position"]["y"] += 1
            if not valid_movement(msg, user) and didJumpThisInput == False:
                currentgame[str(user.id)]["Position"]["y"] -= 1
            await msg.edit(embed=discord.Embed(description=render(msg, user)))
        elif option == "V":
            currentgame[str(user.id)]["Position"]["y"] -= 1
            if not valid_movement(msg, user):
                currentgame[str(user.id)]["Position"]["y"] += 1
            await msg.edit(embed=discord.Embed(description=render(msg, user)))
        elif option == ">":
            currentgame[str(user.id)]["Position"]["x"] += 1
            if not valid_movement(msg, user):
                currentgame[str(user.id)]["Position"]["x"] -= 1
            await msg.edit(embed=discord.Embed(description=render(msg, user)))
        elif option == ">>":
            currentgame[str(user.id)]["Position"]["x"] += 5
            if not valid_movement(msg, user):
                currentgame[str(user.id)]["Position"]["x"] -= 5
            await msg.edit(embed=discord.Embed(description=render(msg, user)))
            
        if not on_floor(interaction.message, interaction.user):
            do = True
            while do:
                if on_floor(interaction.message, interaction.user):
                    do = False
                else:
                    currentgame[str(user.id)]["Position"]["y"] -= 1
                    await msg.edit(embed=discord.Embed(description=render(msg, user)))
                    
class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Movement())

def valid_movement(message, user=0): #checks if sky is on player
    if user == 0:
        user = message.author
    plrx = currentgame[str(user.id)]["Position"]["x"]
    plry = currentgame[str(user.id)]["Position"]["y"]
    if currentgame[str(user.id)]["gamechunks"][f"{str(plrx)}X{str(plry)}"] == "sky" and currentgame[str(user.id)]["gamechunks"][f"{str(plrx)}X{str(plry + 1)}"] == "sky":
        return True
    else:
        return False
    
def on_floor(message, user=0): #checks whats below player, then return false if it is sky
    if user == 0:
        user = message.author
    plrx = currentgame[str(user.id)]["Position"]["x"]
    plry = currentgame[str(user.id)]["Position"]["y"]
    if currentgame[str(user.id)]["gamechunks"][f"{str(plrx)}X{str(plry - 2)}"] == "sky":
        return False
    else:
        return True

def generatechunks(message, user=0):
    if user == 0:
        user = message.author
    noises = []
    seed = currentgame[str(user.id)]["seed"]
    noise = PerlinNoise(octaves=3, seed=seed)
    noise2 = PerlinNoise(octaves=6, seed=seed)
    noise3 = PerlinNoise(octaves=12, seed=seed)
    noise4 = PerlinNoise(octaves=24, seed=seed)
    for x in range(51): #generate 25 wide chunks
        for y in range(51):
            plrx = currentgame[str(user.id)]["Position"]["x"]
            plry = currentgame[str(user.id)]["Position"]["y"]
            tx = plrx + x - 25
            ty = plry + y - 25
            if ty <= -10:
                if not f"{str(tx)}X{str(ty)}" in currentgame[str(user.id)]["gamechunks"]:
                    thenoise = noise([tx / 11, ty / 10]) * 100
                    thenoise += 0.5 * noise2([tx / 11, ty / 10]) * 100
                    thenoise += 0.25 * noise3([tx / 11, ty / 10]) * 100
                    thenoise += 0.125 * noise4([tx / 11, ty / 10]) * 100
                    noises.append(thenoise)
                    if thenoise > -10:
                        if random.randint(1, 50) == 1:
                            currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "iron"
                        else:
                            currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "stone"
                    elif thenoise < -10:
                        currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "sky"
        
            else:
                freq = currentgame[str(user.id)]["seed"]
                thenoise = int(pnoise2(tx/freq / 4, ty/freq / 4) * 75) + 5
                if ty > thenoise:
                    currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "sky"
                elif ty < thenoise:
                    currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "dirt"
                elif ty == thenoise:
                    currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "grass"
                elif 0 < ty < 10:
                    currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "stone"
        
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
    """
    
def render(message, user=0):
    if user == 0:
        user = message.author
    generatechunks(message, user)
    finalmessage = f"Game user: {str(user)}\nOn floor: {str(on_floor(message, user))}\nValid movement: {str(valid_movement(message, user))}\n"
    
    playerpos = False
    debugfinalmessage = ""
    for y in reversed(range(10)):
        for x in range(11):
            plrx = currentgame[str(user.id)]["Position"]["x"]
            plry = currentgame[str(user.id)]["Position"]["y"]
            tx = plrx + x - 5
            ty = plry + y - 4
            #--- debug
            debugfinalmessage += f"({str(tx)}, {str(ty)}) "
            if playerpos == False:
                playerpos = f"{str(plrx)}, {str(plry)} head\n{str(plrx)}, {str(plry - 1)} body"
            #---
            tile = currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"]
            do = True
            if plrx == tx and plry == ty:
                finalmessage += "<:h1:939816513853063218>"
                do = False
            elif plrx == tx and plry == ty + 1:
                finalmessage += "<:b1:939816528277307412>"
                do = False
                
            if do:
                match tile:
                    case "grass":
                        finalmessage += "<:g_:939809738852548628>"
                    case "dirt":
                        finalmessage += "<:d_:939809769462566983>"
                    case "stone":
                        finalmessage += "<:s_:939809867902910524>"
                    case "sky":
                        finalmessage += "<:b2:939815809117724703>"
                    case "iron":
                        finalmessage += "<:i1:960482977559748608>"
        finalmessage += "\n"
        debugfinalmessage += "\n"
    print(f"{debugfinalmessage}\n\n{playerpos}")
    return finalmessage

@client.event
async def on_ready():
    print(str(client.user) + ' has connected to Discord!')
    
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if "setpos " in message.content:
        args = message.content.split(" ")
        currentgame[str(message.author.id)]["Position"]["x"] = int(args[1])
        currentgame[str(message.author.id)]["Position"]["y"] = int(args[2])
        await message.channel.send("Done!")
    if message.content == "start game2":
        random.seed()
        octaves = random.random()
        freq = 150.0 * octaves
        currentgame[str(message.author.id)] = {
            "seed": freq,
            "Position": {
                "x":0, "y":15
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
