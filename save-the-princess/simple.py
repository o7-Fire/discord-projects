#!/usr/bin/python3


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
    
m = int(input())
grid = {}
wherePrincess = None
whereMe = None
def parseInput():
    global wherePrincess, whereMe
    for x in range(0, m):
        inps = input().strip()
        inps = list(inps)
        for y in range(0, m): 
            inp = inps[y]
            #print(f'{x}, {y}: {inp}')
            if(inp == "m"):
                whereMe = Pos(x,y)
            elif(inp == "p"):
                wherePrincess = Pos(x,y)
            if wherePrincess is not None and whereMe is not None:
                return

def displayPathtoPrincess():
    global wherePrincess, whereMe
    dist = wherePrincess - whereMe
    up = dist.x < 0
    left = dist.y < 0
    for x in range(abs(dist.x)):
        if up:
            print("UP")
        else:
            print("DOWN")
    for y in range(abs(dist.y)):
        if left:
            print("LEFT")
        else:
            print("RIGHT")
        
parseInput()
displayPathtoPrincess()
