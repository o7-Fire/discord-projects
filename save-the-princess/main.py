"""Princess Peach is trapped in one of the four corners of a square grid. You are in the center of the grid and can
move one step at a time in any of the four directions. Can you rescue the princess?

Input Format

The first line contains an odd integer N denoting the size of the grid. The next N lines contain N characters each
denoting the grid in row-major order. Each cell is denoting by
'-' for an empty cell,
'p' for a cell containing the princess,
'm' for a cell containing the bot

Output Format

Output the moves you will take to rescue the princess in one go. The characters should be printed in the same order
in which you will move.
The valid moves are LEFT or RIGHT or UP or DOWN.
Sample Input

---
-m-
p--
Sample Output

DOWN
LEFT
"""
import asyncio
import os

import discord


class Pos(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # add arithmetic operators
    def __sub__(self, other):
        return Pos(self.x - other.x, self.y - other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f'({self.x}, {self.y})'


"""
X is actually going up and down
X 0 is the top 
Y 0 is the left
"""


class Grid(object):
    def __init__(self, input_str):
        if (input_str.endswith('\n')):
            input_str = input_str[:-1]
        lines = input_str.split("\n")
        n = len(lines)
        grid = {}
        for x in range(len(lines)):
            lines[x] = list(lines[x].strip())
            # check if grid is rectangular
            if len(lines[x]) != n:
                raise Exception(f'Grid is not rectangular, expected {n} columns, got {len(lines[x])}')
            for y in range(len(lines[x])):
                line = lines[x][y]
                if line == 'p':
                    self.princess = Pos(x, y)
                elif line == 'm':
                    self.bot = Pos(x, y)
                elif line == '-':
                    pass
                else:
                    raise Exception(f'Invalid character {line} on {x}, {y}')
                if x not in grid:
                    grid[x] = {}
                grid[x][y] = line
        # check if princess and bot are in the grid
        if self.princess is None or self.bot is None:
            raise Exception("Princess or bot not in grid")
        self.grid = grid
        self.n = n
        self.last_moves = []

    def solved(self):
        return self.princess == self.bot

    def update(self, nextS):
        botBefore = Pos(self.bot.x, self.bot.y)
        # left = y-1
        # right = y+1
        # up = x-1
        # down = x+1
        if nextS == 'LEFT':
            self.bot.y -= 1
        elif nextS == 'RIGHT':
            self.bot.y += 1
        elif nextS == 'UP':
            self.bot.x -= 1
        elif nextS == 'DOWN':
            self.bot.x += 1
        self.last_moves.append(nextS)
        try:
            self.grid[botBefore.x][botBefore.y] = 'x'
            self.grid[self.bot.x][self.bot.y] = 'm'
        except KeyError:
            raise Exception(f'Bot moved out of grid from {botBefore} to {self.bot}')

    def last_move(self):
        if len(self.last_moves) == 0:
            return "None"
        return self.last_moves[-1]


def nextSolution(princess_pos: Pos, bot_pos: Pos):
    dist = bot_pos - princess_pos
    # ignore if 0

    if abs(dist.y) > abs(dist.x) and dist.y != 0:
        if dist.y > 0:
            return 'LEFT'
        else:
            return 'RIGHT'
    else:
        if dist.x > 0:
            return 'UP'
        else:
            return 'DOWN'


letterToEmote = {
    '-': ':white_large_square:',
    'p': ':large_blue_diamond:',
    'x': ':black_large_square:',
    'm': ':robot:',
}


def gridToDiscordEmote(grid: Grid):
    emote_str = ""
    for row in grid.grid:
        for cell in grid.grid[row]:
            cell = grid.grid[row][cell]
            if cell not in letterToEmote:
                raise Exception(f'Invalid character {cell}')
            emote_str += letterToEmote[cell]
        emote_str += '\n'
    emote_str += "\n`Move: " + grid.last_move() + "`\n"
    return emote_str


import random


def calculateMaxGridSizeBasedOnEmote():
    textLimit = 2000  # should not be more than 2000
    base = len(letterToEmote['p'])
    base += len(letterToEmote['m'])
    based = len(letterToEmote['-'])
    if len(letterToEmote['x']) > based:
        based = len(letterToEmote['x'])
    gridSize = 1
    while True:
        size = base + (based * ((gridSize * gridSize) - 1))
        if size > textLimit:
            size = size - 1
            break
        gridSize += 1
    return gridSize


print(f'Max grid size: {calculateMaxGridSizeBasedOnEmote()}')


def randomGrid():
    n = random.randint(3, calculateMaxGridSizeBasedOnEmote() - 1)
    gridText = ""
    botPos = Pos(0, 0)
    princessPos = Pos(0, 0)
    while botPos == princessPos:
        botPos = Pos(random.randint(0, n - 1), random.randint(0, n - 1))
        princessPos = Pos(random.randint(0, n - 1), random.randint(0, n - 1))
    for x in range(n):
        for y in range(n):
            if x == botPos.x and y == botPos.y:
                gridText += "m"
            elif x == princessPos.x and y == princessPos.y:
                gridText += "p"
            else:
                gridText += "-"
        gridText += "\n"
    return gridText[:-1]


async def solve(grid: Grid, channel: discord.TextChannel):
    lastMessage = await channel.send(gridToDiscordEmote(grid))
    while not grid.solved():
        await asyncio.sleep(1)
        nextS = nextSolution(grid.princess, grid.bot)
        grid.update(nextS)
        await lastMessage.edit(content=gridToDiscordEmote(grid))

    await channel.send("Solved! in " + str(len(grid.last_moves)) + " moves")


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == 'test':
            await message.channel.send('test')
        if message.content.startswith("```save-the-princess"):
            input_str = message.content[len("```save-the-princess"):-len("```")]
            try:
                grid = Grid(input_str)
                await solve(grid, message.channel)
            except Exception as e:
                await message.channel.send(f"{e}")
        if message.content == "solve-random":
            try:
                grid = Grid(randomGrid())
                await solve(grid, message.channel)
            except Exception as e:
                await message.channel.send(f"{e}")


intents = discord.Intents.all()
client = MyClient(intents=intents)
client.run(os.environ['DISCORD_TOKEN'])
