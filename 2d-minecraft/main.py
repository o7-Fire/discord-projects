import nextcord as discord
from perlin_noise import PerlinNoise
from noise import pnoise2
import random
import time
import asyncio
import math
import os

TOKEN = "" or os.environ.get("TOKEN")
client = discord.Client()
currentgame = {}
block_index = {}
item_index = {}
craftingrecipes2x2 = {}
craftingrecipes3x3 = {}

with open("./asset/craftingrecipes.txt") as f:
    t = f.read().split("\n")
    for c in t:
        tt = c.split(" ")
        craftingrecipes3x3[tt[0]] = {
            "amount": tt[1],
            "itemsneeded": {
            
            }
        }
        for i in range(int((len(tt) - 2) / 2)):
            count = (i*2) + 2
            craftingrecipes3x3[tt[0]]["itemsneeded"][tt[count]] = int(tt[count+1])
print(craftingrecipes3x3)
with open("./asset/craftingrecipes2.txt") as f:
    t = f.read().split("\n")
    for c in t:
        tt = c.split(" ")
        craftingrecipes2x2[tt[0]] = {
            "amount": tt[1],
            "itemsneeded": {
            
            }
        }
        for i in range(int((len(tt) - 2) / 2)):
            count = (i * 2) + 2
            craftingrecipes2x2[tt[0]]["itemsneeded"][tt[count]] = int(tt[count + 1])
with open("./asset/itemindex.txt", "r") as f:
    t = f.read().split("\n")
    for item in t:
        tt = item.split(" ")
        item_index[tt[0]] = {
            "name": tt[1].replace("_", " ")
        }
with open("./asset/blockindex.txt", "r") as f:
    t = f.read().split("\n")
    for block in t:
        tt = block.split(" ")
        block_index[tt[0]] = {
            "name": tt[1].replace("_", " "),
            "drops": {
            
            },
            "hardness":tt[3]
        }
        for drop in tt[2].split(","):
            dropdata = drop.split("_")
            block_index[tt[0]]["drops"][dropdata[1]] = int(dropdata[0])
#print(block_index)
    
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


class Mine(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='<^', description='Mine top left', emoji='↖'),
            discord.SelectOption(label='<V', description='Mine bottom left', emoji='↙'),
            discord.SelectOption(label='^', description='Mine up', emoji='⬆'),
            discord.SelectOption(label='V', description='Mine down', emoji='⬇'),
            discord.SelectOption(label='^>', description='Mine top right', emoji='↗'),
            discord.SelectOption(label='V>', description='Mine bottom left', emoji='↘'),
        ]
        super().__init__(placeholder='Mining', min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        msg = interaction.message
        user = interaction.user
        option = self.values[0]
        extramessagetosay = ""
        
        async def randomfunctionformining(x, y):
            global extramessagetosay
            plrx = currentgame[str(user.id)]["Position"]["x"]
            plry = currentgame[str(user.id)]["Position"]["y"]
            thetilename = currentgame[str(user.id)]["gamechunks"][f"{str(plrx + x)}X{str(plry + y)}"]
            currentgame[str(user.id)]["gamechunks"][f"{str(plrx + x)}X{str(plry + y)}"] = "sky"
            
            blockindextile = block_index[thetilename]
            dotheblock = True
            for block in blockindextile["drops"]:
                if dotheblock:
                    amount = 1
                    if blockindextile["drops"][block] != 100:
                        if random.randint(1, 100) == blockindextile["drops"][block]:
                            if block in block_index: extramessagetosay = f"Mined {str(amount)} {block_index[block]['name']}!"
                            else: extramessagetosay = f"Mined {str(amount)} {item_index[block]['name']}!"
                            add_item(user, block, amount)
                            dotheblock = False
                    else: #im sorry for your eyes
                        if block in block_index: extramessagetosay = f"Mined {str(amount)} {block_index[block]['name']}!"
                        else: extramessagetosay = f"Mined {str(amount)} {item_index[block]['name']}!"
                        add_item(user, block, amount)
            await msg.edit(embed=discord.Embed(description=render(msg, user, extramessagetosay)))
        # handle options
        if option == "<^":
            await randomfunctionformining(-1, 0)
        elif option == "<V":
            await randomfunctionformining(-1, -1)
        elif option == "^":
            await randomfunctionformining(0, 1)
        elif option == "V":
            await randomfunctionformining(0, -2)
        elif option == "^>":
            await randomfunctionformining(1, 0)
        elif option == "V>":
            await randomfunctionformining(1, -1)
            
        if not on_floor(interaction.message, interaction.user):
            do = True
            while do:
                if on_floor(interaction.message, interaction.user):
                    do = False
                else:
                    currentgame[str(user.id)]["Position"]["y"] -= 1
                    await msg.edit(embed=discord.Embed(description=render(msg, user, extramessagetosay)))

class Action(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='Inventory', description='Open inventory page', emoji='🧰'),
            discord.SelectOption(label='Crafting', description='Open crafting page', emoji='⚒'),
            discord.SelectOption(label='View recipes', description='Tells you all possible crafting recipes', emoji='⚒'),
            #discord.SelectOption(label='View Game', description='Open the game page', emoji='🕹️'),
            #discord.SelectOption(label='Save Game', description='Saves game to database', emoji='💾'),
            #discord.SelectOption(label='Load Game', description='Loads game from database', emoji='💾'),
        ]
        super().__init__(placeholder='Action', min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        msg = interaction.message
        user = interaction.user
        option = self.values[0]

        # handle actions
        if option == "Inventory":
            await msg.edit(embed=discord.Embed(description=render_inventory(msg, user)))
        elif option == "Crafting":
            await crafting2x2(msg, user)
        elif option == "View recipes":
            await msg.reply(f"<@{str(user.id)}> Check your DMs!")
            finalmessage = "2x2 Recipes (does not require crafting table):\n\n"
            for recipes in craftingrecipes2x2:
                finalmessage += f"{str(craftingrecipes2x2[recipes]['amount'])} {recipes}: "
                for requirements in craftingrecipes2x2[recipes]["itemsneeded"]:
                    finalmessage += f"{str(craftingrecipes2x2[recipes]['itemsneeded'][requirements])} {requirements}, "
                finalmessage = finalmessage[:-2] + "\n"

            finalmessage += "\n3x3 Recipes (requires to be near a crafting table):\n\n"
            for recipes in craftingrecipes3x3:
                finalmessage += f"{str(craftingrecipes3x3[recipes]['amount'])} {recipes}: "
                for requirements in craftingrecipes3x3[recipes]["itemsneeded"]:
                    finalmessage += f"{str(craftingrecipes3x3[recipes]['itemsneeded'][requirements])} {requirements}, "
                finalmessage = finalmessage[:-2] + "\n"
            
            totalmessage = ""
            for line in finalmessage.split("\n"):
                if (len(totalmessage) + len(line)) < 2000:
                    totalmessage += line + "\n"
                else:
                    await user.send(totalmessage)
                    totalmessage = ""
            await user.send(finalmessage)
        """
        if option == "View Game":
            await msg.edit(embed=discord.Embed(description=render(msg, user)))
        elif option == "Save Game":
            try:
                save_game(msg, user)
                await interaction.response.send_message(f"<@{interaction.user.id}> Saved game successfully!")
            except Exception as e:
                await interaction.response.send_message(
                    f"<@{interaction.user.id}> Failed to save game. Error: ```{e}```")
        elif option == "Load Game":
            try:
                res = load_game(msg, user)
                if res == False:
                    await interaction.response.send_message(f"<@{interaction.user.id}> You do not have a save.")
                else:
                    await interaction.response.send_message(f"<@{interaction.user.id}> Game loaded successfully!")
                    await msg.edit(embed=discord.Embed(description=render(msg, user)))
            except Exception as e:
                await interaction.response.send_message(
                    f"<@{interaction.user.id}> Failed to load game. Error: ```{e}```")
        """
        
class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Movement())
        self.add_item(Mine())
        self.add_item(Action())
    
def gettile(tile):
    match tile:
        case "grassblock":return "<:g_:939809738852548628>"
        case "dirt":return "<:d_:939809769462566983>"
        case "stone":return "<:s_:939809867902910524>"
        case "sky":return "<:b2:939815809117724703>"
        case "ironore":return "<:i1:960482977559748608>"
        case "oaklog":return "<:wl1:960812648113504270>"
        case "oakleaf":return "<:wl11:960812925340233758>"
        case "off_furnace":return "<:f1:962212558809477170>"
        case "on_furnace":return "<:f2:962212567550427176>"
        case "craftingtable":return "<:c3:962216007852757004>"
        case "stick":return "<:s1:962218518605074533>"
        
def valid_movement(message, user=0): #checks if sky is on player
    if currentgame[str(user.id)]["cheats"]["noclip"]:
        return True
    else:
        if user == 0:
            user = message.author
        plrx = currentgame[str(user.id)]["Position"]["x"]
        plry = currentgame[str(user.id)]["Position"]["y"]
        if currentgame[str(user.id)]["gamechunks"][f"{str(plrx)}X{str(plry)}"] == "sky" or currentgame[str(user.id)]["gamechunks"][f"{str(plrx)}X{str(plry + 1)}"] == "sky":
            return True
        else:
            return False
    
def on_floor(message, user=0): #checks whats below player, then return false if it is sky
    if currentgame[str(user.id)]["cheats"]["noclip"]:
        return True
    else:
        if user == 0:
            user = message.author
        plrx = currentgame[str(user.id)]["Position"]["x"]
        plry = currentgame[str(user.id)]["Position"]["y"]
        if currentgame[str(user.id)]["gamechunks"][f"{str(plrx)}X{str(plry - 2)}"] == "sky":
            return False
        else:
            return True

def add_item(user, itemname, amount):
    if itemname in currentgame[str(user.id)]["inventory"]:
        currentgame[str(user.id)]["inventory"][itemname] = currentgame[str(user.id)]["inventory"][itemname] + amount
    else:
        currentgame[str(user.id)]["inventory"][itemname] = int(amount)
    
def generate_models(modelname, user, x, y):
    with open(f"./models/{modelname}.txt", "r") as f:
        data = f.read().split("\n")
    for tile in data:
        data2 = tile.split(" ")
        if data2[2] != "air":
            currentgame[str(user.id)]["gamechunks"][f"{str(x + int(data2[0]))}X{str(y + int(data2[1]))}"] = data2[2]
   
async def crafting2x2(message, user=0):
    if user == 0:
        user = message.author
    def check(msg):
        return msg.author == user
    clientmsg1 = await message.reply("What do you want to craft? (2x2)")
    msg = await client.wait_for('message', check=check, timeout=30)
    
    therecipe = ""
    do = False
    for recipes in craftingrecipes2x2:
        if recipes == msg.content:
            do = True
            therecipe = recipes
            
    if not do:
        clientmsg2 = await msg.reply("No crafting recipe found for that.")
        await asyncio.sleep(3)
        await clientmsg1.delete()
        await msg.delete()
        await clientmsg2.delete()
    else:
        recipe = craftingrecipes2x2[therecipe]
        finalmessage = f"To craft {recipe['amount']} {therecipe} you need "
        for requirement in recipe["itemsneeded"]:
            finalmessage += f"{recipe['itemsneeded'][requirement]} {requirement}, "
        finalmessage = finalmessage[:-2] + ". Do you want to craft? (Y/N)"
        clientmsg3 = await msg.reply(finalmessage)
        mesg = await client.wait_for('message', check=check, timeout=30)
        
        if mesg.content == "Y":
            meetallrequirements = True
            for requirement in recipe["itemsneeded"]:
                if currentgame[str(user.id)]["inventory"][requirement]:
                    if currentgame[str(user.id)]["inventory"][requirement] > recipe["itemsneeded"][requirement]:
                        theveryusefuldonothingvalue = 0
                    else:
                        meetallrequirements = False
                else:
                    meetallrequirements = False
                    
            if meetallrequirements:
                for requirement in recipe["itemsneeded"]:
                    currentgame[str(user.id)]["inventory"][requirement] = currentgame[str(user.id)]["inventory"][requirement] - recipe["itemsneeded"][requirement]
                add_item(user, therecipe, recipe['amount'])
                clientmsg5 = await mesg.reply(f"Crafted {recipe['amount']} {therecipe}.")
                await asyncio.sleep(3)
                await clientmsg1.delete()
                await msg.delete()
                await clientmsg3.delete()
                await mesg.delete()
                await clientmsg5.delete()
            else:
                clientmsg4 = await mesg.reply("You do not have the required items to craft it.")
                await asyncio.sleep(3)
                await clientmsg1.delete()
                await msg.delete()
                await clientmsg3.delete()
                await mesg.delete()
                await clientmsg4.delete()
        else:
            await asyncio.sleep(3)
            await clientmsg1.delete()
            await msg.delete()
            await clientmsg3.delete()
            await mesg.delete()
        
def render_inventory(message, user=0, additional_message=""):
    if user == 0:
        user = message.author
    finalmessage = f"Game user: {str(user)}\n{additional_message}\n"
    inventory = currentgame[str(user.id)]["inventory"]
    for item in inventory:
        finalmessage += f", {str(inventory[item])} {item}"
    finalmessage = finalmessage.replace(", ", "", 1)
    return finalmessage

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

            if not f"{str(tx)}X{str(ty)}" in currentgame[str(user.id)]["gamechunks"]:
                freq = currentgame[str(user.id)]["seed"]
                thenoise = int(pnoise2(tx / freq / 4, ty / freq / 4) * 75) + 5
                if ty > thenoise:
                    currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "sky"
                elif thenoise-5 < ty < thenoise:
                    currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "dirt"
                elif ty == thenoise:
                    currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "grassblock"
                    if random.randint(1, 12) == 1:
                        if random.randint(1, 3) == 1:
                            generate_models("largeoaktree", user, tx-4, ty)
                        else:
                            generate_models("oaktree", user, tx - 2, ty + 1)
                elif thenoise - 12 < ty < thenoise - 5:
                    currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "stone"
                else:
                    thenoise = noise([tx / 11, ty / 10]) * 100
                    thenoise += 0.5 * noise2([tx / 11, ty / 10]) * 100
                    thenoise += 0.25 * noise3([tx / 11, ty / 10]) * 100
                    thenoise += 0.125 * noise4([tx / 11, ty / 10]) * 100
                    noises.append(thenoise)
                    if thenoise > -10:
                        if random.randint(1, 50) == 1:
                            currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "ironore"
                        else:
                            currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"] = "stone"
                    elif thenoise < -10:
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
    """
    
def render(message, user=0, additional_message=""):
    if user == 0:
        user = message.author
    generatechunks(message, user)
    #finalmessage = f"Game user: {str(user)}\nOn floor: {str(on_floor(message, user))}\nValid movement: {str(valid_movement(message, user))}\n" \
    #               f"Noclip: {str(currentgame[str(user.id)]['cheats']['noclip'])}\n{additional_message}\n"
    finalmessage = f"Game user: {str(user)}\n{additional_message}\n"
    
    playerpos = False #debug
    debugfinalmessage = "" #debug
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
                finalmessage += gettile(tile)
        finalmessage += "\n"
        debugfinalmessage += "\n"  # debug
    print(f"{debugfinalmessage}\n\n{playerpos}") #debug
    return finalmessage

@client.event
async def on_ready():
    print(str(client.user) + ' has connected to Discord!')
    
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == "noclip":
        if currentgame[str(message.author.id)]["cheats"]["noclip"]:
            currentgame[str(message.author.id)]["cheats"]["noclip"] = False
        else:
            currentgame[str(message.author.id)]["cheats"]["noclip"] = True
        await message.channel.send("Done!")
    if "setpos " in message.content:
        args = message.content.split(" ")
        currentgame[str(message.author.id)]["Position"]["x"] = int(args[1])
        currentgame[str(message.author.id)]["Position"]["y"] = int(args[2])
        render(message)
        await message.channel.send("Done!")
    if message.content.startswith("additem "):
        args = message.content.split(" ")
        add_item(message.author, args[1], args[2])
    if message.content == "start game2":
        random.seed()
        octaves = random.random()
        freq = 150.0 * octaves
        currentgame[str(message.author.id)] = {
            "seed": freq,
            "Position": {
                "x":0, "y":50
            },
            "inventory": {

            },
            "gamechunks": {
            
            },
            "cheats": {
                "noclip":False,
            }
        }
        do = True
        while do:
            generatechunks(message, message.author)
            if on_floor(message, message.author):
                do = False
            else:
                currentgame[str(message.author.id)]["Position"]["y"] -= 1
        embed = discord.Embed(description=render(message))
        await message.channel.send(embed=embed, view=DropdownView())
        
client.run(TOKEN)
