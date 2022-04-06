import json
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

lastFetchProxy1Time = 0
lastFetchProxy1 = []


def fetchProxy1(secure=True):
    global lastFetchProxy1Time, lastFetchProxy1
    if time.time() - lastFetchProxy1Time < 60:
        return lastFetchProxy1

    url = "https://api.proxyscrape.com/?request=getproxies&proxytype=https&timeout=2000&country=all&ssl=yes"
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
    lastFetchProxy1Time = time.time()
    lastFetchProxy1 = listDict
    print(f"Fetched {len(listDict)} proxies")
    return listDict


lastFetchProxy2Time = 0
lastFetchProxy2 = []


def fetchProxy2():
    global lastFetchProxy2Time, lastFetchProxy2
    if time.time() - lastFetchProxy2Time < 60:
        return lastFetchProxy2
    lastFetchProxy2Time = time.time()
    url = "https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=lastChecked&sort_type=desc&speed=fast&protocols=http%2Chttps"
    response = requests.get(url)
    data = json.loads(response.text)
    lastFetchProxy2 = []
    for dat in data["data"]:
        da = {}
        for protocol in dat["protocols"]:
            da[protocol] = protocol + "://" + dat["ip"] + ":" + str(dat["port"])
        lastFetchProxy2.append(da)
    print(f"Fetched {len(lastFetchProxy2)} proxies")
    return lastFetchProxy2


def fetchProxy():
    l = [fetchProxy1(), fetchProxy2()]
    return l


def do(name=0, rangeStart=0, rangeEnd=1):
    print(f'Thread {name} started with range {rangeStart} to {rangeEnd}')
    proxies = fetchProxy()

    for i in range(rangeStart, rangeEnd):
        try:

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
            # print(e)
            # time.sleep(1)
            continue
    print(f'Thread {name} finished')


def main():
    workerCount = 100
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
