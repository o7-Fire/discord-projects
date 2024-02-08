from PIL import Image
import random
import discord
from discord import app_commands

on = Image.open("on.png").resize((16,16))
off = Image.open("off.png").resize((16,16))

size = 50

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

grid = {}

def image_grid(imgs, rows, cols):
    assert len(imgs) == rows * cols

    w, h = imgs[0].size
    grid = Image.new('RGB', size=(cols * w, rows * h))
    grid_w, grid_h = grid.size

    for i, img in enumerate(imgs):
        grid.paste(img, box=(i % cols * w, i // cols * h))
    return grid

def newgrid():
    for y in range(size):
        for x in range(size):
            if random.randint(1, 10) == 1:
                grid[f"{str(x)}|{str(y)}"] = "on"
            else:
                grid[f"{str(x)}|{str(y)}"] = "off"

def nextstep():
    global grid
    nextgame = {}
    for y in range(size):
        for x in range(size):
            g = grid[f"{str(x)}|{str(y)}"]
            neighbours = []
            #neighbours = [grid[f"{str(x-1)}|{str(y-1)}"],grid[f"{str(x-1)}|{str(y)}"],
            #              grid[f"{str(x-1)}|{str(y+1)}"],grid[f"{str(x)}|{str(y-1)}"],
            #              grid[f"{str(x)}|{str(y+1)}"],grid[f"{str(x+1)}|{str(y-1)}"],
            #              grid[f"{str(x+1)}|{str(y)}"],grid[f"{str(x+1)}|{str(y+1)}"]]
            for yy in range(3):
                for xx in range(3):
                    f = f"{str(x + xx - 1)}|{str(y + yy - 1)}"
                    xtrue = False
                    ytrue = False
                    if xx - 1 == 0: xtrue = True
                    if yy - 1 == 0: ytrue = True
                    if f in grid and not (xtrue and ytrue):
                        neighbours.append(grid[f])
            alive = 0
            dead = 0
            #print(neighbours)
            for n in neighbours:
                if n == "on":
                    alive += 1
                else:
                    dead += 1
            #print(alive, dead)
            didaction = False
            if g == "off":
                if alive == 3:
                    didaction = True
                    nextgame[f"{str(x)}|{str(y)}"] = "on"
            else:
                if alive < 2:
                    didaction = True
                    nextgame[f"{str(x)}|{str(y)}"] = "off"
                elif alive == 2 or alive == 3:
                    didaction = True
                    nextgame[f"{str(x)}|{str(y)}"] = "on"
                elif alive > 3:
                    didaction = True
                    nextgame[f"{str(x)}|{str(y)}"] = "off"
            if not didaction:
                nextgame[f"{str(x)}|{str(y)}"] = grid[f"{str(x)}|{str(y)}"]
    grid = nextgame


def render():
    nextstep()
    images = []
    for y in range(size):
        for x in range(size):
            if grid[f"{str(x)}|{str(y)}"] == "off":
                images.append(off)
            else:
                images.append(on)
    return image_grid(images, size, size)

async def render_discord():
    secret_channel = client.get_channel(1204968667637358662)
    file = discord.File("render.png")
    temp_message = await secret_channel.send(file=file)
    attachment = temp_message.attachments[0]

    embed = discord.Embed()
    embed.set_image(url=attachment.url)
    return embed

@tree.command(
    name="startgame",
    description="start the game of life",
    guild=discord.Object(id=839297157836308520)
)

async def first_command(interaction):
    newgrid()
    rendered = render()
    rendered.save("render.png")
    embedtosend = await render_discord()
    await interaction.response.send_message(embed=embedtosend)
    while True:
        rendered = render()
        rendered.save("render.png")
        embedtosend = await render_discord()
        await interaction.edit_original_response(embed=embedtosend)

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=839297157836308520))
    print("Ready!")

client.run("")
