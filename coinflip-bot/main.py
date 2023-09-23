import discord
import random

TOKEN = ""

client = discord.Client(intents=discord.Intents.all())
data = {}

class bomb_button(discord.ui.View):
    @discord.ui.button(label=f"Bet all", style=discord.ButtonStyle.primary)
    async def b1(self, interaction, button):
        bet = data[interaction.user.id]
        if random.randint(0, 1) == 1:
            data[interaction.user.id] = data[interaction.user.id] + bet
            embed=discord.Embed(description=f"You gained {str(bet)}.\n\nYou now have {data[interaction.user.id]}.",color=interaction.user.color or discord.Color.random())
            await interaction.response.edit_message(embed=embed)
        else:
            data[interaction.user.id] = data[interaction.user.id] - bet
            embed=discord.Embed(description=f"You lost {str(bet)}.\n\nYou now have {data[interaction.user.id]}.",color=interaction.user.color or discord.Color.random())
            await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label=f"Bet 1/2", style=discord.ButtonStyle.primary)
    async def b2(self, interaction, button):
        bet = data[interaction.user.id] / 2
        if random.randint(0, 1) == 1:
            data[interaction.user.id] = data[interaction.user.id] + bet
            embed=discord.Embed(description=f"You gained {str(bet)}.\n\nYou now have {data[interaction.user.id]}.",color=interaction.user.color or discord.Color.random())
            await interaction.response.edit_message(embed=embed)
        else:
            data[interaction.user.id] = data[interaction.user.id] - bet
            embed=discord.Embed(description=f"You lost {str(bet)}.\n\nYou now have {data[interaction.user.id]}.",color=interaction.user.color or discord.Color.random())
            await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label=f"Bet 1/4", style=discord.ButtonStyle.primary)
    async def b3(self, interaction, button):
        bet = data[interaction.user.id] / 4
        if random.randint(0, 1) == 1:
            data[interaction.user.id] = data[interaction.user.id] + bet
            embed=discord.Embed(description=f"You gained {str(bet)}.\n\nYou now have {data[interaction.user.id]}.",color=interaction.user.color or discord.Color.random())
            await interaction.response.edit_message(embed=embed)
        else:
            data[interaction.user.id] = data[interaction.user.id] - bet
            embed=discord.Embed(description=f"You lost {str(bet)}.\n\nYou now have {data[interaction.user.id]}.",color=interaction.user.color or discord.Color.random())
            await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label=f"Bet 1/8", style=discord.ButtonStyle.primary)
    async def b4(self, interaction, button):
        bet = data[interaction.user.id] / 8
        if random.randint(0, 1) == 1:
            data[interaction.user.id] = data[interaction.user.id] + bet
            embed=discord.Embed(description=f"You gained {str(bet)}.\n\nYou now have {data[interaction.user.id]}.",color=interaction.user.color or discord.Color.random())
            await interaction.response.edit_message(embed=embed)
        else:
            data[interaction.user.id] = data[interaction.user.id] - bet
            embed=discord.Embed(description=f"You lost {str(bet)}.\n\nYou now have {data[interaction.user.id]}.",color=interaction.user.color or discord.Color.random())
            await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label=f"Bet 1/16", style=discord.ButtonStyle.primary)
    async def b5(self, interaction, button):
        bet = data[interaction.user.id] / 16
        if random.randint(0, 1) == 1:
            data[interaction.user.id] = data[interaction.user.id] + bet
            embed=discord.Embed(description=f"You gained {str(bet)}.\n\nYou now have {data[interaction.user.id]}.",color=interaction.user.color or discord.Color.random())
            await interaction.response.edit_message(embed=embed)
        else:
            data[interaction.user.id] = data[interaction.user.id] - bet
            embed=discord.Embed(description=f"You lost {str(bet)}.\n\nYou now have {data[interaction.user.id]}.",color=interaction.user.color or discord.Color.random())
            await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label=f"Bet 1/32", style=discord.ButtonStyle.primary)
    async def b6(self, interaction, button):
        bet = data[interaction.user.id] / 32
        if random.randint(0, 1) == 1:
            data[interaction.user.id] = data[interaction.user.id] + bet
            embed=discord.Embed(description=f"You gained {str(bet)}.\n\nYou now have {data[interaction.user.id]}.",color=interaction.user.color or discord.Color.random())
            await interaction.response.edit_message(embed=embed)
        else:
            data[interaction.user.id] = data[interaction.user.id] - bet
            embed=discord.Embed(description=f"You lost {str(bet)}.\n\nYou now have {data[interaction.user.id]}.",color=interaction.user.color or discord.Color.random())
            await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label=f"Bet 1/64", style=discord.ButtonStyle.primary)
    async def b7(self, interaction, button):
        bet = data[interaction.user.id] / 64
        if random.randint(0, 1) == 1:
            data[interaction.user.id] = data[interaction.user.id] + bet
            embed=discord.Embed(description=f"You gained {str(bet)}.\n\nYou now have {data[interaction.user.id]}.",color=interaction.user.color or discord.Color.random())
            await interaction.response.edit_message(embed=embed)
        else:
            data[interaction.user.id] = data[interaction.user.id] - bet
            embed=discord.Embed(description=f"You lost {str(bet)}.\n\nYou now have {data[interaction.user.id]}.",color=interaction.user.color or discord.Color.random())
            await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label=f"Bet 1/128", style=discord.ButtonStyle.primary)
    async def b8(self, interaction, button):
        bet = data[interaction.user.id] / 128
        if random.randint(0, 1) == 1:
            data[interaction.user.id] = data[interaction.user.id] + bet
            embed=discord.Embed(description=f"You gained {str(bet)}.\n\nYou now have {data[interaction.user.id]}.",color=interaction.user.color or discord.Color.random())
            await interaction.response.edit_message(embed=embed)
        else:
            data[interaction.user.id] = data[interaction.user.id] - bet
            embed=discord.Embed(description=f"You lost {str(bet)}.\n\nYou now have {data[interaction.user.id]}.",color=interaction.user.color or discord.Color.random())
            await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label=f"Bet 1/256", style=discord.ButtonStyle.primary)
    async def b9(self, interaction, button):
        bet = data[interaction.user.id] / 256
        if random.randint(0, 1) == 1:
            data[interaction.user.id] = data[interaction.user.id] + bet
            embed=discord.Embed(description=f"You gained {str(bet)}.\n\nYou now have {data[interaction.user.id]}.",color=interaction.user.color or discord.Color.random())
            await interaction.response.edit_message(embed=embed)
        else:
            data[interaction.user.id] = data[interaction.user.id] - bet
            embed=discord.Embed(description=f"You lost {str(bet)}.\n\nYou now have {data[interaction.user.id]}.",color=interaction.user.color or discord.Color.random())
            await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label=f"Bet 1/512", style=discord.ButtonStyle.primary)
    async def b10(self, interaction, button):
        bet = data[interaction.user.id] / 512
        if random.randint(0, 1) == 1:
            data[interaction.user.id] = data[interaction.user.id] + bet
            embed=discord.Embed(description=f"You gained {str(bet)}.\n\nYou now have {data[interaction.user.id]}.",color=interaction.user.color or discord.Color.random())
            await interaction.response.edit_message(embed=embed)
        else:
            data[interaction.user.id] = data[interaction.user.id] - bet
            embed=discord.Embed(description=f"You lost {str(bet)}.\n\nYou now have {data[interaction.user.id]}.",color=interaction.user.color or discord.Color.random())
            await interaction.response.edit_message(embed=embed)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.content == "helloyes":
        await message.channel.send("ye")
    if message.content == "bombflip":
        data[message.author.id] = 100
        embed = discord.Embed(description="You have 100 coins.",color=discord.Color.random())
        await message.channel.send(embed=embed, view=bomb_button())

client.run(TOKEN)
