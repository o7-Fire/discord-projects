import json
import os
import random
import shutil

import discord

import SaveFile
from noise import pnoise2

grid_folder = "data/grid"
save_folder = "data/save"
GRID_SIZE_X = 10
GRID_SIZE_Y = 10


class Game(object):
    def __init__(self, player_id, resources=None):
        self.player_id = player_id
        self.current_grid = {}
        self.current_grid_x = 0
        self.current_grid_y = 0
        self.player = {
            'x': 0,
            'y': 0,
        }
        self.seed = random.randint(0, 100000)
        if resources is None:
            resources = {}
        self.resources = resources
        self.load()

    def get_grid_folder(self):
        fi = os.path.join(grid_folder, str(self.player_id))
        if not os.path.exists(fi):
            os.makedirs(fi)
        return fi

    def get_grid_file(self, gridX, gridY):
        return os.path.join(self.get_grid_folder(), str(gridX) + "-" + str(gridY) + ".json")

    def _save_current_grid(self):
        with open(self.get_grid_file(self.current_grid_x, self.current_grid_y), "w") as f:
            json.dump(self.current_grid, f)

    def get_grid(self):
        gridX = self.current_grid_x
        gridY = self.current_grid_y
        grid_file = self.get_grid_file(gridX, gridY)
        if self.current_grid_x == gridX and self.current_grid_y == gridY and len(self.current_grid) > 0:
            return self.current_grid
        elif os.path.exists(grid_file):
            with open(self.get_grid_file(gridX, gridY), "r") as f:
                jsonText = f.read()
                self.current_grid = json.loads(jsonText)
        else:
            self.current_grid = self.generate_grid(gridX, gridY)
        self.current_grid_x = gridX
        self.current_grid_y = gridY
        self._save_current_grid()
        return self.current_grid

    def generate_grid(self, gridX, gridY):
        grid = {}
        for y in range(0, GRID_SIZE_X):
            grid[y] = {}
            for x in range(0, GRID_SIZE_Y):
                blockType = int(pnoise2(gridX / self.seed / 4, gridY / self.seed / 4) * 75) + 5
                grid[y][x] = blockType
        return grid

    def move_player(self, direction):
        if direction == "up":
            self.player['y'] += 1
        elif direction == "down":
            self.player['y'] -= 1
        elif direction == "left":
            self.player['x'] -= 1
        elif direction == "right":
            self.player['x'] += 1
        else:
            raise Exception("Invalid direction: " + direction)
        localX = self.player['x'] % GRID_SIZE_X
        localY = self.player['y'] % GRID_SIZE_Y
        if localX < 0:
            self.current_grid_x = self.current_grid_x - 1
        if localY < 0:
            self.current_grid_y = self.current_grid_y - 1
        if localX >= GRID_SIZE_X:
            self.current_grid_x = self.current_grid_x + 1
        if localY >= GRID_SIZE_Y:
            self.current_grid_y = self.current_grid_y + 1
        self.get_grid()
        self.save()

    async def render(self, interaction: discord.Interaction = None):
        if len(self.current_grid) == 0:
            self.get_grid()
        text = ""
        not_found = []
        for localY in reversed(range(0, GRID_SIZE_Y)):
            for localX in range(0, GRID_SIZE_X):
                x = GRID_SIZE_X * self.current_grid_x + localX
                y = GRID_SIZE_Y * self.current_grid_y + localY
                block_id = self.current_grid[str(x)][str(y)]
                if x == self.player['x'] and y == self.player['y']:
                    block_id = "B"  # body
                if x == self.player['x'] and y == self.player['y'] + 1:
                    block_id = "H"  # head
                block_id = str(block_id)
                if block_id not in self.resources:
                    if block_id not in not_found:
                        not_found.append(block_id)
                    text += block_id
                else:
                    text += self.resources[block_id]
            text += "\n"
        if len(not_found) > 0:
            print("Resources Not found: " + str(not_found))
        if interaction is not None:

            embed = discord.Embed(title="Snake", description=text, color=0x00ff00)
            embed.set_author(name=str(interaction.user), icon_url=interaction.user.avatar.url)
            await interaction.message.edit(embed=embed)
        return text

    def get_save_file(self):
        folder = os.path.join(save_folder, str(self.player_id))
        if not os.path.exists(folder):
            os.makedirs(folder)
        return os.path.join(folder, "save.json")

    def save(self):
        SaveFile.save(self, self.get_save_file())

    def load(self):
        save_file = self.get_save_file()
        if os.path.exists(save_file):
            SaveFile.load(self, save_file)
        else:
            self.get_grid()

    def delete(self):
        # delete file and world
        os.remove(self.get_save_file())
        folder = os.path.join(save_folder, self.player_id)
        shutil.rmtree(folder)


if __name__ == '__main__':
    game = Game(1)
    resources = {}
    print(game.render(resources))
    game.move_player("up")
    print("\n")
    print(game.render(resources))
