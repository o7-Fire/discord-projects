import nextcord as discord
from perlin_noise import PerlinNoise
from noise import pnoise2
import random
from PIL import Image
import time
import asyncio
import math
import os

TOKEN = ""
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
            embedtosend = await render_discord(msg, user)
            await msg.edit(embed=embedtosend)
        elif option == "<":
            currentgame[str(user.id)]["Position"]["x"] -= 1
            if not valid_movement(msg, user):
                currentgame[str(user.id)]["Position"]["x"] += 1
            embedtosend = await render_discord(msg, user)
            await msg.edit(embed=embedtosend)
        elif option == "^":
            if currentgame[str(user.id)]["jumped_frame"] == False:
                currentgame[str(user.id)]["jumped_frame"] = True
            else:
                currentgame[str(user.id)]["jumped_frame"] = False
            currentgame[str(user.id)]["Position"]["y"] += 1
            if not valid_movement(msg, user):
                currentgame[str(user.id)]["Position"]["y"] -= 1
            await render_discord("send", msg, user)
            embedtosend = await render_discord(msg, user)
            await msg.edit(embed=embedtosend)
        elif option == "V":
            currentgame[str(user.id)]["Position"]["y"] -= 1
            if not valid_movement(msg, user):
                currentgame[str(user.id)]["Position"]["y"] += 1
            embedtosend = await render_discord(msg, user)
            await msg.edit(embed=embedtosend)
        elif option == ">":
            currentgame[str(user.id)]["Position"]["x"] += 1
            if not valid_movement(msg, user):
                currentgame[str(user.id)]["Position"]["x"] -= 1
            embedtosend = await render_discord(msg, user)
            await msg.edit(embed=embedtosend)
        elif option == ">>":
            currentgame[str(user.id)]["Position"]["x"] += 5
            if not valid_movement(msg, user):
                currentgame[str(user.id)]["Position"]["x"] -= 5
            embedtosend = await render_discord(msg, user)
            await msg.edit(embed=embedtosend)
            
        if currentgame[str(user.id)]["jumped_frame"] == False: #gotta make sure
            if not on_floor(interaction.message, interaction.user):
                do = True
                while do:
                    if on_floor(interaction.message, interaction.user):
                        do = False
                    else:
                        currentgame[str(user.id)]["Position"]["y"] -= 1
                        embedtosend = await render_discord(msg, user)
                        await msg.edit(embed=embedtosend)


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
            
            if thetilename != "sky":
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
                embedtosend = await render_discord(msg, user, additionalmessage=extramessagetosay)
                await msg.edit(embed=embedtosend)
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
                    embedtosend = await render_discord(msg, user, additionalmessage=extramessagetosay)
                    await msg.edit(embed=embedtosend)


class Place(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='<^', description='Place held item to top left', emoji='↖'),
            discord.SelectOption(label='<V', description='Place held item to bottom left', emoji='↙'),
            discord.SelectOption(label='^', description='Place held item to up', emoji='⬆'),
            discord.SelectOption(label='V', description='Place held item to down', emoji='⬇'),
            discord.SelectOption(label='^>', description='Place held item to top right', emoji='↗'),
            discord.SelectOption(label='V>', description='Place held item to bottom left', emoji='↘'),
        ]
        super().__init__(placeholder='Place', min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        msg = interaction.message
        user = interaction.user
        option = self.values[0]
        extramessagetosay = ""
        
        async def randomfunctionforplacing(x, y):
            global extramessagetosay
            plrx = currentgame[str(user.id)]["Position"]["x"]
            plry = currentgame[str(user.id)]["Position"]["y"]
            thetilename = currentgame[str(user.id)]["gamechunks"][f"{str(plrx + x)}X{str(plry + y)}"]
            currentgame[str(user.id)]["gamechunks"][f"{str(plrx + x)}X{str(plry + y)}"] = "sky"
            held_item = currentgame[str(user.id)]["held_item"]
            if held_item != "nothing":
                currentgame[str(user.id)]["gamechunks"][f"{str(plrx + x)}X{str(plry + y)}"] = held_item
                add_item(user, held_item, -1)
                if int(currentgame[str(user.id)]["inventory"][held_item]) < 1:
                    currentgame[str(user.id)]["held_item"] = "nothing"
            embedtosend = await render_discord(msg, user, additionalmessage=extramessagetosay)
            await msg.edit(embed=embedtosend)
        
        # handle options
        if option == "<^":
            await randomfunctionforplacing(-1, 0)
        elif option == "<V":
            await randomfunctionforplacing(-1, -1)
        elif option == "^":
            await randomfunctionforplacing(0, 1)
        elif option == "V":
            await randomfunctionforplacing(0, -2)
        elif option == "^>":
            await randomfunctionforplacing(1, 0)
        elif option == "V>":
            await randomfunctionforplacing(1, -1)
            
class Action(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='Inventory', description='Open inventory page', emoji='🧰'),
            discord.SelectOption(label='Crafting', description='Open crafting page', emoji='⚒'),
            discord.SelectOption(label='View recipes', description='Tells you all possible crafting recipes', emoji='⚒'),
            discord.SelectOption(label='Equip block', description='Equips a type of block onto your hand', emoji='🕹️'),
            discord.SelectOption(label='Save game', description='Saves game to database', emoji='💾'),
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
            if nearcraftingtable(msg, user):
                await crafting(msg, user, "3x3")
            else:
                await crafting(msg, user, "2x2")
                
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
            
        elif option == "Equip block":
            game = currentgame[str(user.id)]
            async def deleteall(list):
                await asyncio.sleep(3)
                for message in list:
                    await message.delete()
            def check(msg):
                return msg.author == user
            clientmsg1 = await msg.reply(f"What do you want to hold?")
            mesg = await client.wait_for('message', check=check, timeout=30)
            if mesg.content in block_index:
                if mesg.content in game["inventory"]:
                    if int(game["inventory"][mesg.content]) > 0:
                        currentgame[str(user.id)]["held_item"] = mesg.content
                        clientmsg2 = await mesg.reply("Equipped block!")
                        await deleteall([clientmsg1, mesg, clientmsg2])
                    else:
                        clientmsg2 = await mesg.reply("You do not have enough blocks.")
                        await deleteall([clientmsg1, mesg, clientmsg2])
                else:
                    clientmsg2 = await mesg.reply("You do not have any of those blocks.")
                    await deleteall([clientmsg1, mesg, clientmsg2])
            else:
                clientmsg2 = await mesg.reply("That is not in the block index.")
                await deleteall([clientmsg1, mesg, clientmsg2])
            
        elif option == "Save game":
            s = savegame(msg, user)
            if s == False:
                await msg.reply(f"<@{str(user.id)}> Failed to save game.")
            else:
                await msg.reply(f"<@{str(user.id)}> Saved game successfully!")
        
class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Movement())
        self.add_item(Mine())
        self.add_item(Place())
        self.add_item(Action())


def image_grid(imgs, rows, cols):
    assert len(imgs) == rows * cols
    
    w, h = imgs[0].size
    grid = Image.new('RGB', size=(cols * w, rows * h))
    grid_w, grid_h = grid.size
    
    for i, img in enumerate(imgs):
        grid.paste(img, box=(i % cols * w, i // cols * h))
    return grid

def gettile(tile):
    if os.path.exists(f"./asset/image/{tile}.png"):
        img = Image.open(f"./asset/image/{tile}.png")
        return img.resize((16, 16))
    elif os.path.exists(f"./asset/image/{tile}.jpg"):
        img = Image.open(f"./asset/image/{tile}.png")
        return img.resize((16, 16))
    else:
        img = Image.open(f"./asset/image/missingno.png")
        return img.resize((16, 16))
        
def savegame(message, user=0):
    if user == 0:
        user = message.author
    try:
        with open(f"./saves/{str(user.id)}.txt", "w+") as f:
            game = currentgame[str(user.id)]
            finalmessage = f"{str(game['seed'])}\n{str(game['Position']['x'])} {str(game['Position']['y'])}\n"
            for item in game["inventory"]:
                finalmessage += f"{item}_{game['inventory'][item]} "
            finalmessage = finalmessage[:-1]
            finalmessage += "\n"
            for tile in game["gamechunks"]:
                finalmessage += f"{tile}_{game['gamechunks'][tile]} "
            finalmessage = finalmessage[:-1]
            f.write(finalmessage)
        return True
    except:
        return False #impossible
        
def loadgame(message, user=0):
    if user == 0:
        user = message.author
    total = 0
    game = currentgame[str(user.id)]
    if os.path.exists(f"./saves/{str(user.id)}.txt"):
        with open(f"./saves/{str(user.id)}.txt", "r+") as f:
            for line in f.read().split("\n"):
                total += 1
                if total == 1:
                    game["seed"] = float(line)
                elif total == 2:
                    splitted = line.split(" ")
                    game["Position"]["x"] = int(splitted[0])
                    game["Position"]["y"] = int(splitted[1])
                elif total == 3:
                    items = line.split(" ")
                    for splitted in items:
                        itemsplit = splitted.split("_")
                        game["inventory"][itemsplit[0]] = itemsplit[1]
                elif total == 4:
                    tiles = line.split(" ")
                    for splitted in tiles:
                        tilesplit = splitted.split("_")
                        game["gamechunks"][tilesplit[0]] = tilesplit[1]
                else:
                    raise Exception("this isnt a possible error")
        return True
    else:
        return False
    
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
        
def nearcraftingtable(message, user=0): #checks if sky is on player
    if user == 0:
        user = message.author
    plrx = currentgame[str(user.id)]["Position"]["x"]
    plry = currentgame[str(user.id)]["Position"]["y"]
    for x in range(3):
        for y in range(4):
            thex = x - 1
            they = y - 1
            if currentgame[str(user.id)]["gamechunks"][f"{str(plrx + thex)}X{str(plry + they)}"] == "craftingtable":
                return True
    return False
        
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


async def crafting(message, user=0, type="2x2"):
    if type == "2x2":
        therecipetype = craftingrecipes2x2
    else:
        therecipetype = craftingrecipes3x3
    if user == 0:
        user = message.author

    async def deleteall(list):
        await asyncio.sleep(3)
        for message in list:
            await message.delete()
    def check(msg):
        return msg.author == user
    
    clientmsg1 = await message.reply(f"What do you want to craft? ({type})")
    msg = await client.wait_for('message', check=check, timeout=30)
    
    therecipe = ""
    do = False
    for recipes in therecipetype:
        if recipes == msg.content:
            do = True
            therecipe = recipes
    
    if not do:
        clientmsg2 = await msg.reply("No crafting recipe found for that.")
        deleteall([clientmsg1, msg, clientmsg2])
    else:
        recipe = therecipetype[therecipe]
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
                    currentgame[str(user.id)]["inventory"][requirement] = currentgame[str(user.id)]["inventory"][
                                                                              requirement] - recipe["itemsneeded"][
                                                                              requirement]
                add_item(user, therecipe, recipe['amount'])
                clientmsg5 = await mesg.reply(f"Crafted {recipe['amount']} {therecipe}.")
                deleteall([clientmsg1, msg, clientmsg3, mesg, clientmsg5])
            else:
                clientmsg4 = await mesg.reply("You do not have the required items to craft it.")
                deleteall([clientmsg1, msg, clientmsg3, mesg, clientmsg4])
        else:
            deleteall([clientmsg1, msg, clientmsg3, mesg])
        
def render_inventory(message, user=0, additional_message=""):
    if user == 0:
        user = message.author
    finalmessage = f"Game user: {str(user)}\n{additional_message}\n"
    inventory = currentgame[str(user.id)]["inventory"]
    for item in inventory:
        finalmessage += f", {str(inventory[item])} {item}"
    finalmessage = finalmessage.replace(", ", "", 1)
    return finalmessage

async def render_discord(message, user, additionalmessage=""):
    r = render(message, user, additional_message=additionalmessage)
    secret_channel = client.get_channel(966580292032802837)
    r[1].save(f"./temp/{user.id}.png")
    file = discord.File(f"./temp/{user.id}.png")
    temp_message = await secret_channel.send(file=file)
    attachment = temp_message.attachments[0]
    
    embed = discord.Embed(description=r[0])
    embed.set_image(url=attachment.url)
    return embed
    
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
                    if currentgame[str(user.id)]["cangeneratemodels"]:
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
    images = []
    for y in reversed(range(21)):
        for x in range(31):
            plrx = currentgame[str(user.id)]["Position"]["x"]
            plry = currentgame[str(user.id)]["Position"]["y"]
            tx = plrx + x - 15
            ty = plry + y - 10
            #--- debug
            debugfinalmessage += f"({str(tx)}, {str(ty)}) "
            if playerpos == False:
                playerpos = f"{str(plrx)}, {str(plry)} head\n{str(plrx)}, {str(plry - 1)} body"
            #---
            tile = currentgame[str(user.id)]["gamechunks"][f"{str(tx)}X{str(ty)}"]
            do = True
            if plrx == tx and plry == ty:
                images.append(gettile("head"))
                do = False
            elif plrx == tx and plry == ty + 1:
                images.append(gettile("body"))
                do = False
                
            if do:
                images.append(gettile(tile))
        debugfinalmessage += "\n"  # debug
    print(f"{debugfinalmessage}\n\n{playerpos}") #debug
    return [finalmessage, image_grid(images, rows=21, cols=31)]

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
        await message.channel.send("Done!")
    if message.content.startswith("additem "):
        args = message.content.split(" ")
        add_item(message.author, args[1], args[2])
    if message.content == "start game":
        random.seed()
        octaves = random.random()
        freq = 150.0 * octaves
        currentgame[str(message.author.id)] = {
            "cangeneratemodels": True, #a simple solution for a problem that will need to be solved later
            "jumped_frame":False,
            "held_item": "nothing",
            "seed": freq,
            "Position": {
                "x": 0, "y": 50
            },
            "inventory": {
                "oaklog":0
            },
            "gamechunks": {
        
            },
            "cheats": {
                "noclip": False,
            }
        }

        currentgame[str(message.author.id)]["cangeneratemodels"] = False
        l = loadgame(message, message.author)
        #print(l)
        #print(currentgame[str(message.author.id)]["Position"])
        if l == False:
            do = True
            while do:
                generatechunks(message, message.author)
                if on_floor(message, message.author):
                    do = False
                else:
                    currentgame[str(message.author.id)]["Position"]["y"] -= 1
            embedtosend = await render_discord(message, message.author)
            await message.channel.send(embed=embedtosend, view=DropdownView())
        else:
            embedtosend = await render_discord(message, message.author)
            await message.channel.send(embed=embedtosend, view=DropdownView())
            await message.channel.send("Game loaded successfully!")
            currentgame[str(message.author.id)]["cangeneratemodels"] = True
            
client.run(TOKEN)