from PIL import Image
import cv2
import random
import time

on = Image.open("on.png").resize((8,8))
off = Image.open("off.png").resize((8,8))

size = 100

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

newgrid()

while True:
    rendered = render()
    rendered.save("render.png")
    cv2.imshow("image", cv2.imread("render.png", cv2.IMREAD_COLOR))
    cv2.waitKey(1)
