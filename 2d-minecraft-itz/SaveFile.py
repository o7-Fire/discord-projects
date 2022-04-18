import datetime
import json

import Game

currentVersion = 1
upgrade = {}


def save(game: Game, fileName: str):
    with open(fileName, 'w') as f:
        data = {
            'game': game.__dict__,
            'version': currentVersion,
            'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        f.write(json.dumps(data))


def load(game: Game, fileName: str):
    data = {}
    with open(fileName, 'r') as f:
        data = json.loads(f.read())
    game.__dict__ = data['game']
    while data['version'] < currentVersion:
        game = upgrade[data['version']](game)
        data['version'] += 1
    return game
