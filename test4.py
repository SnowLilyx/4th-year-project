import json

from watcher import Watcher
from accounts import *
from helpers import pick_first, pick_random

with open("gaming_vids.txt", encoding="UTF-16") as f:
    seeds = json.load(f)

for seed in [seeds[i] for i in [19]]:
    try:
        Watcher(104, account=carol, choose_fn=pick_random, seed=seed)(1, 10)
    except:
        pass
