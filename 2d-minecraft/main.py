import discord
from noise import pnoise2
import random
import time

TOKEN = ""
client = discord.Client()
random.seed()
octaves = random.random()

freq = 50.0 * octaves
maxheight = 10
currentgame = {}
lastmsg = {}
lastbot = ""

def generatechunks(message, user=0):
	if user == 0:
		user = message.author
	currentviewx = currentgame[str(user.id)]["currentviewx"]
	for x in range(11):
		tree = 0
		if random.randint(1, 13) == 1:
			tree = 1
		n = int(pnoise2((x + currentviewx) / freq, (x + currentviewx) / 2 / freq, 1) * 10 + 3)
		if f"{x + 1 + currentviewx}tree" in currentgame[str(user.id)]["gamechunks"]:
			theusefuldonothingvalue = 0
		else:
			currentgame[str(user.id)]["gamechunks"][f"{x + 1 + currentviewx}tree"] = tree
		currentgame[str(user.id)]["gamechunks"][f"{x + 1 + currentviewx}"] = n
		
def chop(message, user=0):
	if user == 0:
		user = message.author
	inventory = currentgame[str(user.id)]["inventory"]
	currentviewx = currentgame[str(user.id)]["currentviewx"]
	tile = currentgame[str(user.id)]["gamechunks"]
	if tile[f"{currentviewx + 5}tree"] == 1:
		tile[f"{currentviewx + 5}tree"] = 0
		inventory["wood"] += random.randint(10, 20)
	elif tile[f"{currentviewx + 7}tree"] == 1:
		tile[f"{currentviewx + 7}tree"] = 0
		inventory["wood"] += random.randint(10, 20)
		
def render(message, user=0):
	if user == 0:
		user = message.author
	generatechunks(message, user)
	inventory = currentgame[str(user.id)]["inventory"]
	currentviewx = currentgame[str(user.id)]["currentviewx"]
	currentviewy = currentgame[str(user.id)]["currentviewy"]
	finalmessage = f"X: {currentviewx}\nY: {currentviewy}\nUser: {str(user)}\nInventory: {str(inventory['wood'])} wood\n"
	for y in reversed(range(10)):
		for x in range(11):
			tile = currentgame[str(user.id)]["gamechunks"][f"{x + 1 + currentviewx}"]
			tiletree = currentgame[str(user.id)]["gamechunks"][f"{x + 1 + currentviewx}tree"]
			#character
			if tile - currentviewy == y - 2 and x == 5:
				finalmessage += ":brown_circle:"
			elif tile - currentviewy == y - 1 and x == 5:
				finalmessage += ":yellow_square:"
			#tree
			elif tiletree == 1 and tile - currentviewy == y - 1:
				finalmessage += ":brown_square:"
			elif tiletree == 1 and tile - currentviewy == y - 2:
				finalmessage += ":brown_square:"
			elif tiletree == 1 and tile - currentviewy == y - 3:
				finalmessage += ":green_square:"
			#ground and sky
			elif tile - currentviewy >= y:
				finalmessage += ":green_square:"
			else:
				finalmessage += ":blue_square:"
		finalmessage += "\n"
	return finalmessage

@client.event
async def on_ready():
	print(str(client.user) + ' has connected to Discord!')

@client.event
async def on_reaction_add(reaction, user):
	if reaction.emoji == "⬅":
		message = lastmsg[str(user.id)]
		currentgame[str(user.id)]["currentviewx"] -= 1
		await message.edit(content=f"{render(message, user)}")
	elif reaction.emoji == "◀":
		message = lastmsg[str(user.id)]
		currentgame[str(user.id)]["currentviewx"] -= 5
		await message.edit(content=f"{render(message, user)}")
	elif reaction.emoji == "⬆":
		message = lastmsg[str(user.id)]
		currentgame[str(user.id)]["currentviewy"] += 1
		await message.edit(content=f"{render(message, user)}")
	elif reaction.emoji == "⬇":
		message = lastmsg[str(user.id)]
		currentgame[str(user.id)]["currentviewy"] -= 1
		await message.edit(content=f"{render(message, user)}")
	elif reaction.emoji == "➡":
		message = lastmsg[str(user.id)]
		currentgame[str(user.id)]["currentviewx"] += 1
		await message.edit(content=f"{render(message, user)}")
	elif reaction.emoji == "▶":
		message = lastmsg[str(user.id)]
		currentgame[str(user.id)]["currentviewx"] += 5
		await message.edit(content=f"{render(message, user)}")
	elif reaction.emoji == "🪓":
		message = lastmsg[str(user.id)]
		chop(message, user)
		await message.edit(content=f"{render(message, user)}")
	
@client.event
async def on_message(message):
	global lastbot
	if message.author == client.user:
		lastbot = message
		if message.content.startswith("X: "):
			emojis = ["◀", "⬅", "⬆", "⬇", "➡", "▶", "🪓"]
			for emoji in emojis:
				await message.add_reaction(emoji)
		else:
			return
	if message.content == "start game":
		currentgame[str(message.author.id)] = {
			"currentviewx":0, "currentviewy":0,
			"inventory": {
				"wood": 0,
			},
			"gamechunks": {
			
			},
		}
		generatechunks(message)
		
		await message.channel.send(f"{render(message)}")
		time.sleep(1)
		lastmsg[str(message.author.id)] = lastbot

client.run(TOKEN)
