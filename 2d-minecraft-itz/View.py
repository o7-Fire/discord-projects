import nextcord as discord

from Game import Game


class Movement(discord.ui.Select):
    def __init__(self, game: Game):
        options = [
            discord.SelectOption(label='<', description='Move the character to the left', emoji='⬅'),
            discord.SelectOption(label='^', description='Move the character up', emoji='⬆'),
            discord.SelectOption(label='V', description='Move the character down', emoji='⬇'),
            discord.SelectOption(label='>', description='Move the character to the right', emoji='➡'),
        ]
        self.game = game
        super().__init__(placeholder='Movement', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        msg = interaction.message
        option = self.values[0]
        if option == '<':
            self.game.move_player('left')
        elif option == '>':
            self.game.move_player('right')
        elif option == '^':
            self.game.move_player('up')
        elif option == 'V':
            self.game.move_player('down')
        else:
            await msg.channel.send('Invalid option')
            return
        await self.game.render(interaction)


class Action(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='Inventory', description='Open inventory page', emoji='🧰'),
            discord.SelectOption(label='Crafting', description='Open crafting page', emoji='⚒'),
            discord.SelectOption(label='View recipes', description='Tells you all possible crafting recipes',
                                 emoji='⚒'),
            # discord.SelectOption(label='View Game', description='Open the game page', emoji='🕹️'),
            # discord.SelectOption(label='Save Game', description='Saves game to database', emoji='💾'),
            # discord.SelectOption(label='Load Game', description='Loads game from database', emoji='💾'),
        ]
        super().__init__(placeholder='Action', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        msg = interaction.message
        user = interaction.user
        option = self.values[0]


class DropdownView(discord.ui.View):
    def __init__(self, game: Game):
        super().__init__()
        self.add_item(Movement(game))
        self.add_item(Action())
