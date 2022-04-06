from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Queue

import requests
from fake_headers import Headers
from tqdm import tqdm
import threading
import time
import string
import random

header = Headers(
    headers=True  # generate misc headers
)

letters = string.ascii_letters + string.digits
letters = list(letters)
random.shuffle(letters)
index = -1
inviteLength = 8
possibleCombination = len(letters) ** inviteLength
pb = tqdm(total=possibleCombination)


def generateRandomString(iteration):
    combos = []
    for i in range(inviteLength):
        combos.append(letters[iteration % len(letters)])
        iteration = iteration // len(letters)
    return ''.join(combos)


def nextInvite():
    global index, pb
    index += 1
    pb.update(1)
    return "https://discord.com/api/v9/invites/" + generateRandomString(index)


# prevent too much open files
file = open("invites.txt", "w")

print("Header sample")
for eeeeeeeeeeeee in range(3):
    print(header.generate())


def fetchProxy(secure=True):
    url = "https://api.proxyscrape.com/?request=getproxies&proxytype=https&timeout=1000&country=all&ssl=yes"
    if not secure:
        url = url.replace("https", "http")
    response = requests.get(url)
    wheeze = response.text.split("\r\n")
    listDict = []
    for i in wheeze:
        if i == "": continue
        if secure:
            i = "https://" + i
            listDict.append({"https": i})
        else:
            i = "http://" + i
            listDict.append({"http": i})
    return listDict


def do(name=0, rangeStart=0, rangeEnd=1):
    print(f'Thread {name} started with range {rangeStart} to {rangeEnd}')
    proxies = fetchProxy()
    print(f'Thread {name} fetched {len(proxies)} proxies')
    for i in range(rangeStart, rangeEnd):
        try:
            if i % len(proxies) == 0:
                proxies = fetchProxy()
                print(f'Thread {name} fetched {len(proxies)} proxies')
            url = nextInvite()
            proxy = random.choice(proxies)
            response = requests.get(url, headers=header.generate(), timeout=2000, proxies=proxy)

            if response.status_code == 200:
                file.write(response.text + "\n")
            elif response.status_code == 429:
                print(f'Thread {name} hit rate limit, sleeping for 10 seconds')
                time.sleep(10)
                continue
            elif response.status_code != 404:
                print(f'{url} returned {response.status_code}')
        except Exception as e:
            #print(e)
            #time.sleep(1)
            continue
    print(f'Thread {name} finished')


def main():
    workerCount = 10
    eachWorker = possibleCombination // workerCount
    print("Possible Combinations: " + str(possibleCombination))
    print("Workers: " + str(workerCount))
    print("Each Worker: " + str(eachWorker))
    thread = []
    for i in range(workerCount):
        thread.append(threading.Thread(target=do, args=(i, eachWorker * i, eachWorker * (i + 1))))
    for t in thread:
        t.start()
    for t in thread:
        t.join()
    file.close()


if __name__ == "__main__":
    main()
