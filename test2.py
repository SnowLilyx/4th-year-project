import json

from watcher import Watcher
from accounts import *
from helpers import pick_first, pick_random

with open("homepage_vids.txt", encoding="UTF-16") as f:
    seeds = json.load(f)

for seed in [seeds[i] for i in [9]]:
    try:
        Watcher(302, account=None, choose_fn=pick_random, seed=seed)(1, 10)
    except:
        pass
