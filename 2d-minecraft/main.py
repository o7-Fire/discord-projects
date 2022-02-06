import nextcord as discord
from noise import pnoise2
import random
import time
import math

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
			if stepassist_allowed(msg, user):
				currentgame[str(user.id)]["currentviewy"] += 1
			elif valid_movement(msg, user) == False:
				currentgame[str(user.id)]["currentviewx"] += 5
			await msg.edit(embed=discord.Embed(description=render(msg, user)))
		elif option == "<":
			currentgame[str(user.id)]["currentviewx"] -= 1
			if stepassist_allowed(msg, user):
				currentgame[str(user.id)]["currentviewy"] += 1
			elif valid_movement(msg, user) == False:
				currentgame[str(user.id)]["currentviewx"] += 1
			await msg.edit(embed=discord.Embed(description=render(msg, user)))
		elif option == "^":
			currentgame[str(user.id)]["jumped"] = True
			jumped = True
			currentgame[str(user.id)]["currentviewy"] += 1
			if stepassist_allowed(msg, user):
				currentgame[str(user.id)]["currentviewy"] += 1
			elif valid_movement(msg, user) == False:
				currentgame[str(user.id)]["currentviewy"] -= 1
			await msg.edit(embed=discord.Embed(description=render(msg, user)))
		elif option == "V":
			currentgame[str(user.id)]["jumped"] = False
			jumped = False
			currentgame[str(user.id)]["currentviewy"] -= 1
			if stepassist_allowed(msg, user):
				currentgame[str(user.id)]["currentviewy"] += 1
			elif valid_movement(msg, user) == False:
				currentgame[str(user.id)]["currentviewy"] += 1
			await msg.edit(embed=discord.Embed(description=render(msg, user)))
		elif option == ">":
			currentgame[str(user.id)]["currentviewx"] += 1
			if stepassist_allowed(msg, user):
				currentgame[str(user.id)]["currentviewy"] += 1
			elif valid_movement(msg, user) == False:
				currentgame[str(user.id)]["currentviewx"] -= 1
			await msg.edit(embed=discord.Embed(description=render(msg, user)))
		elif option == ">>":
			currentgame[str(user.id)]["currentviewx"] += 5
			if stepassist_allowed(msg, user):
				currentgame[str(user.id)]["currentviewy"] += 1
			elif valid_movement(msg, user) == False:
				currentgame[str(user.id)]["currentviewx"] -= 5
			await msg.edit(embed=discord.Embed(description=render(msg, user)))
		#for handling the jumps
		if currentgame[str(user.id)]["jumped"] == True and on_floor(msg, user) == False and jumped == False:
			currentgame[str(user.id)]["currentviewy"] -= 1
			await msg.edit(embed=discord.Embed(description=render(msg, user)))
		elif on_floor(msg, user) == False and jumped == False:
			while on_floor(msg, user) == False:
				currentgame[str(user.id)]["currentviewy"] -= 1
				await msg.edit(embed=discord.Embed(description=render(msg, user)))
		currentgame[str(user.id)]["jumped"] = False
		#await interaction.response.send_message(f'Action: {self.values[0]}\nUser: {str(interaction.response.author)}')

class Action(discord.ui.Select):
	def __init__(self):
		options = [
			discord.SelectOption(label='Chop', description='Chops down trees near the character', emoji='🪓'),
			discord.SelectOption(label='Inventory', description='Open inventory', emoji='🧰'),
			discord.SelectOption(label='Game', description='View Game', emoji='🕹️'),
		]
		super().__init__(placeholder='Action', min_values=1, max_values=1, options=options)

	async def callback(self, interaction: discord.Interaction):
		msg = interaction.message
		user = interaction.user
		option = self.values[0]
		
		#handle actions
		if option == "Chop":
			amount = chop(msg, user)
			await msg.edit(embed=discord.Embed(description=render(msg, user, f"Picked up {amount} wood\n")))
		elif option == "Inventory":
			await msg.edit(embed=discord.Embed(description=render_inventory(msg, user)))
		elif option == "Game":
			await msg.edit(embed=discord.Embed(description=render(msg, user)))

class DropdownView(discord.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(Movement())
		self.add_item(Action())
		
def handle_number(x, y):
	a = str(x)
	if len(a) > y:
		b = ""
		for i in range(len(a)):
			b += "9"
		return b
	while len(a) != y and len(a) < y:
		a = f"0{a}"
	return a

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
		n2 = int(pnoise2(n / freq, (x + currentviewx) / freq, 1) * 10 + 3)
		if f"{x + 1 + currentviewx}tree" in currentgame[str(user.id)]["gamechunks"]:
			theusefuldonothingvalue = 0
		else:
			currentgame[str(user.id)]["gamechunks"][f"{x + 1 + currentviewx}tree"] = tree
		currentgame[str(user.id)]["gamechunks"][f"{x + 1 + currentviewx}"] = n
		currentgame[str(user.id)]["gamechunks"][f"{x + 1 + currentviewx}s"] = n - n2


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
			amount = random.randint(reward_min, reward_max)
			inventory["wood"] += amount
			return amount
		elif tile[f"{currentviewx + 7}tree"] == type:
			tile[f"{currentviewx + 7}tree"] = 0
			amount = random.randint(reward_min, reward_max)
			inventory["wood"] += amount
			return amount
		else:
			return "A"
	
	val = handle_tree(1, 10, 20)
	if val != "A": return val
	val = handle_tree(2, 40, 60)
	if val != "A": return val
	return None


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

def stepassist_allowed(message, user=0):
	a = 0
	if user == 0:
		user = message.author
	generatechunks(message, user)
	currentviewx = currentgame[str(user.id)]["currentviewx"]
	currentviewy = currentgame[str(user.id)]["currentviewy"]
	for x in range(11):
		tile = currentgame[str(user.id)]["gamechunks"][f"{x + 1 + currentviewx}"]
		if tile - currentviewy == 5 and x == 5:
			a += 1
		elif tile - currentviewy == 4 and x == 5:
			a += 1
	if a == 1:
		return True
	else:
		return False

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

def render(message, user=0, additional_string=""):
	if user == 0:
		user = message.author
	generatechunks(message, user)
	inventory = currentgame[str(user.id)]["inventory"]
	currentviewx = currentgame[str(user.id)]["currentviewx"]
	currentviewy = currentgame[str(user.id)]["currentviewy"]
	finalmessage = f"X: {currentviewx}\nY: {currentviewy}\nUser: {str(user)}\n{additional_string}"
	for y in reversed(range(10)):
		for x in range(11):
			tile = currentgame[str(user.id)]["gamechunks"][f"{x + 1 + currentviewx}"]
			tilestone = currentgame[str(user.id)]["gamechunks"][f"{x + 1 + currentviewx}s"]
			tiletree = currentgame[str(user.id)]["gamechunks"][f"{x + 1 + currentviewx}tree"]
			# character
			if y == 5 and x == 5:
				finalmessage += "<:head:939816513853063218>"
			elif y == 4 and x == 5:
				finalmessage += "<:body:939816528277307412>"
			# tree
			elif tiletree == 1 and y - 1 >= tile - currentviewy >= y - 3:
				finalmessage += "<:L2:939809793814695947>"
			elif tiletree == 1 and tile - currentviewy == y - 4:
				finalmessage += "<:L1:939809848533585930>"
			elif tiletree == 2 and y - 1 >= tile - currentviewy >= y - 7:
				finalmessage += "<:L2:939809793814695947>"
			elif tiletree == 2 and tile - currentviewy == y - 8:
				finalmessage += "<:L1:939809848533585930>"
			# ground and sky
			elif tile - currentviewy == y:
				finalmessage += "<:g_:939809738852548628>"
			elif tile - currentviewy > y and tilestone - currentviewy < y:
				finalmessage += "<:d_:939809769462566983>"
			elif tilestone - currentviewy >= y:
				finalmessage +=  "<:s_:939809867902910524>"
			else:
				finalmessage += "<:background:939815809117724703>"
		finalmessage += "\n"
	return finalmessage

def render_inventory(message, user=0):
	if user == 0:
		user = message.author
	currentviewx = currentgame[str(user.id)]["currentviewx"]
	currentviewy = currentgame[str(user.id)]["currentviewy"]
	inventory = currentgame[str(user.id)]["inventory"]
	finalmessage = f"X: {currentviewx}\nY: {currentviewy}\nUser: {str(user)}\n"
	def handle_item(dict, key, msg):
		if key == "wood"and dict[key] != 0:
			return f"{handle_number(dict[key], 3)} <:w_:939809931740217384>"
		elif key == "dirt" and dict[key] != 0:
			return f"{handle_number(dict[key], 3)} <:d_:939809769462566983>"
		elif key == "stone" and dict[key] != 0:
			return f"{handle_number(dict[key], 3)} <:s_:939809867902910524>"
	a = 1
	for item in inventory:
		if a != 3:
			handled = handle_item(inventory, item, finalmessage)
			if handled != None:
				finalmessage += f"{handled}"
		else:
			handled = handle_item(inventory, item, finalmessage)
			if handled != None:
				finalmessage += f"{handled}\n"
			a = 0
		a += 1
	return finalmessage

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
				"wood": 0, "dirt": 0, "stone": 0,
			},
			"gamechunks": {
			
			},
		}
		generatechunks(message)
		embed = discord.Embed(description=render(message))
		await message.channel.send(embed=embed, view=DropdownView())

client.run(TOKEN)
