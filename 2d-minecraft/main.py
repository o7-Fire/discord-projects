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

class Movement(discord.ui.Select):
	def __init__(self):
		options = [
			discord.SelectOption(label='<<', description='Move the character to the left by 5 units', emoji='◀'),
			discord.SelectOption(label='<', description='Move the character to the left by 1 units', emoji='⬅'),
			discord.SelectOption(label='^', description='Move the character up', emoji='⬆'),
			discord.SelectOption(label='V', description='Move the character up', emoji='⬇'),
			discord.SelectOption(label='>', description='Move the character to the right by 1 units', emoji='➡'),
			discord.SelectOption(label='>>', description='Move the character to the right by 5 units', emoji='▶'),
		]
		super().__init__(placeholder='Movement', min_values=1, max_values=1, options=options)

	async def callback(self, interaction: discord.Interaction):
		jumped = False
		msg = interaction.message
		user = interaction.user
		option = self.values[0]
		
		#handle options
		if option == "<<":
			currentgame[str(user.id)]["currentviewx"] -= 5
			if valid_movement(msg, user) == False:
				currentgame[str(user.id)]["currentviewx"] += 5
			await msg.edit(content=f"{render(msg, user)}")
		elif option == "<":
			currentgame[str(user.id)]["currentviewx"] -= 1
			if valid_movement(msg, user) == False:
				currentgame[str(user.id)]["currentviewx"] += 1
			await msg.edit(content=f"{render(msg, user)}")
		elif option == "^":
			currentgame[str(user.id)]["jumped"] = True
			jumped = True
			currentgame[str(user.id)]["currentviewy"] += 1
			if valid_movement(msg, user) == False:
				currentgame[str(user.id)]["currentviewy"] -= 1
			await msg.edit(content=f"{render(msg, user)}")
		elif option == "V":
			currentgame[str(user.id)]["jumped"] = False
			jumped = False
			currentgame[str(user.id)]["currentviewy"] -= 1
			if valid_movement(msg, user) == False:
				currentgame[str(user.id)]["currentviewy"] += 1
			await msg.edit(content=f"{render(msg, user)}")
		elif option == ">":
			currentgame[str(user.id)]["currentviewx"] += 1
			if valid_movement(msg, user) == False:
				currentgame[str(user.id)]["currentviewx"] -= 1
			await msg.edit(content=f"{render(msg, user)}")
		elif option == ">>":
			currentgame[str(user.id)]["currentviewx"] += 5
			if valid_movement(msg, user) == False:
				currentgame[str(user.id)]["currentviewx"] -= 5
			await msg.edit(content=f"{render(msg, user)}")
		#for handling the jumps
		if currentgame[str(user.id)]["jumped"] == True and on_floor(msg, user) == False and jumped == False:
			currentgame[str(user.id)]["currentviewy"] -= 1
			await msg.edit(content=f"{render(msg, user)}")
		elif on_floor(msg, user) == False and jumped == False:
			while on_floor(msg, user) == False:
				currentgame[str(user.id)]["currentviewy"] -= 1
				await msg.edit(content=f"{render(msg, user)}")
		currentgame[str(user.id)]["jumped"] = False
		#await interaction.response.send_message(f'Action: {self.values[0]}\nUser: {str(interaction.response.author)}')

class Action(discord.ui.Select):
	def __init__(self):
		options = [
			discord.SelectOption(label='Chop', description='Chops down trees near the character', emoji='🪓'),
		]
		super().__init__(placeholder='Action', min_values=1, max_values=1, options=options)

	async def callback(self, interaction: discord.Interaction):
		msg = interaction.message
		user = interaction.user
		option = self.values[0]
		
		#handle actions
		if option == "Chop":
			chop(msg, user)
			await msg.edit(content=f"{render(msg, user)}")

class DropdownView(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(Movement())
		self.add_item(Action())
		
def generatechunks(message, user=0):
	if user == 0:
		user = message.author
	currentviewx = currentgame[str(user.id)]["currentviewx"]
	for x in range(11):
		tree = 0
		if random.randint(1, 13) == 1:
			if random.randint(1, 3) == 1:
				tree = 2
			else:
				tree = 1
		n = int(pnoise2((x + currentviewx) / freq, (x + currentviewx) / 2 / freq, 1) * 10 + 3)
		if f"{x + 1 + currentviewx}tree" in currentgame[str(user.id)]["gamechunks"]:
			theusefuldonothingvalue = 0
		else:
			currentgame[str(user.id)]["gamechunks"][f"{x + 1 + currentviewx}tree"] = tree
		currentgame[str(user.id)]["gamechunks"][f"{x + 1 + currentviewx}"] = n


# def mine():

def chop(message, user=0):
	if user == 0:
		user = message.author
	inventory = currentgame[str(user.id)]["inventory"]
	currentviewx = currentgame[str(user.id)]["currentviewx"]
	tile = currentgame[str(user.id)]["gamechunks"]
	
	def handle_tree(type, reward_min, reward_max):
		if tile[f"{currentviewx + 5}tree"] == type:
			tile[f"{currentviewx + 5}tree"] = 0
			inventory["wood"] += random.randint(reward_min, reward_max)
		elif tile[f"{currentviewx + 7}tree"] == type:
			tile[f"{currentviewx + 7}tree"] = 0
			inventory["wood"] += random.randint(reward_min, reward_max)
	
	handle_tree(1, 10, 20)
	handle_tree(2, 40, 60)


def on_floor(message, user=0):
	if user == 0:
		user = message.author
	currentviewx = currentgame[str(user.id)]["currentviewx"]
	currentviewy = currentgame[str(user.id)]["currentviewy"]
	for x in range(11):
		tile = currentgame[str(user.id)]["gamechunks"][f"{x + 1 + currentviewx}"]
		if tile - currentviewy < 3 and x == 5:
			return False
	return True


def valid_movement(message, user=0):
	if user == 0:
		user = message.author
	generatechunks(message, user)
	currentviewx = currentgame[str(user.id)]["currentviewx"]
	currentviewy = currentgame[str(user.id)]["currentviewy"]
	for x in range(11):
		tile = currentgame[str(user.id)]["gamechunks"][f"{x + 1 + currentviewx}"]
		if tile - currentviewy == 5 and x == 5:
			return False
		elif tile - currentviewy == 4 and x == 5:
			return False
	return True

def render(message, user=0):
	if user == 0:
		user = message.author
	generatechunks(message, user)
	inventory = currentgame[str(user.id)]["inventory"]
	currentviewx = currentgame[str(user.id)]["currentviewx"]
	currentviewy = currentgame[str(user.id)]["currentviewy"]
	finalmessage = f"X: {currentviewx}\nY: {currentviewy}\nUser: {str(user)}\nInventory: {str(inventory['wood'])} wood\nOn Floor: {on_floor(message, user)}\nValid Movement: {valid_movement(message, user)}\n"
	for y in reversed(range(10)):
		for x in range(11):
			tile = currentgame[str(user.id)]["gamechunks"][f"{x + 1 + currentviewx}"]
			tiletree = currentgame[str(user.id)]["gamechunks"][f"{x + 1 + currentviewx}tree"]
			# character
			if y == 5 and x == 5:
				finalmessage += ":brown_circle:"
			elif y == 4 and x == 5:
				finalmessage += ":yellow_square:"
			# tree
			elif tiletree == 1 and y - 1 >= tile - currentviewy >= y - 3:
				finalmessage += ":brown_square:"
			elif tiletree == 1 and tile - currentviewy == y - 4:
				finalmessage += ":green_square:"
			elif tiletree == 2 and y - 1 >= tile - currentviewy >= y - 7:
				finalmessage += ":brown_square:"
			elif tiletree == 2 and tile - currentviewy == y - 8:
				finalmessage += ":green_square:"
			# ground and sky
			elif tile - currentviewy >= y:
				finalmessage += ":green_square:"
			else:
				finalmessage += ":blue_square:"
		finalmessage += "\n"
	return finalmessage
	
async def handle_jump(message, user, jumped):
	if currentgame[str(user.id)]["jumped"] == True and on_floor(message, user) == False and jumped == False:
		currentgame[str(user.id)]["currentviewy"] -= 1
		await message.edit(content=f"{render(message, user)}")
	elif on_floor(message, user) == False and jumped == False:
		while on_floor(message, user) == False:
			currentgame[str(user.id)]["currentviewy"] -= 1
			await message.edit(content=f"{render(message, user)}")
	currentgame[str(user.id)]["jumped"] = False

@client.event
async def on_ready():
	print(str(client.user) + ' has connected to Discord!')
	
@client.event
async def on_message(message):
	if message.author == client.user:
		return
	if message.content == "start game":
		random.seed()
		currentgame[str(message.author.id)] = {
			"currentviewx": 0, "currentviewy": 0, "jumped": False, "climbing": False,
			"inventory": {
				"wood": 0,
			},
			"gamechunks": {
			
			},
		}
		generatechunks(message)
		await message.channel.send(f"{render(message)}", view=DropdownView())

client.run(TOKEN)
