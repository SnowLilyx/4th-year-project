import json

from watcher import Watcher
from accounts import *
from helpers import pick_first, pick_random

with open("gaming_vids.txt", encoding="UTF-16") as f:
    seeds = json.load(f)

for seed in seeds:
    try:
        Watcher(116, account=dave, choose_fn=pick_random, seed=seed)(1, 10)
    except:
        pass
