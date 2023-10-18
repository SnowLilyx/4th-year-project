import random
import json
from tkinter import Tk

from selenium.webdriver.common.by import By
from scipy.stats import mannwhitneyu as mwu

YOUTUBE_PREFIX = "https://www.youtube.com/watch?v="
COOKIE_BUTTON = "yt-spec-button-shape-next"
SKIP_BUTTON = "ytp-ad-skip-button"
VISIT_AD = "ytp-ad-visit-advertiser-button"
PLAY = "ytp-play-button"
METADATA = "ytd-watch-metadata"
AUTOPLAY = "ytp-autonav-toggle-button"
NEXT_VIDEO = "ytd-watch-next-secondary-results-renderer"
SIGN_IN = "yt-spec-button-shape-next"
MENU_ICON = "guide-icon"

FIELD_NAMES = "Title Channel Tags Views Likes Subs".split()

PROBLEMS = ["Subscribe", "Join", "Share", "Save", "UNITED STATES",
            "Thanks", "Clip", "Description", "Unlisted", "Download"]

def suppress(f):
    """Supress errors in a function, instead returning None"""
    def inner(*args):
        try:
            return f(*args)
        except:
            return None
    return inner

# Wrappers around selenium functions that return None if an element
# can't be found rather than throwing an error

@suppress
def get_by_ID(obj, val):
    return obj.find_element(by=By.ID, value=val)

@suppress
def get_by_IDs(obj, val):
    return obj.find_elements(by=By.ID, value=val)

@suppress
def get_by_class(obj, val):
    return obj.find_element(by=By.CLASS_NAME, value=val)

@suppress
def get_by_classs(obj, val):
    return obj.find_elements(by=By.CLASS_NAME, value=val)

@suppress
def get_by_name(obj, val):
    return obj.find_element(by=By.NAME, value = val)

@suppress
def replay_state(play_button):
    return play_button.get_property("title") == "Replay"

def get_clipboard():
    "Mildly cursed way to get clipboard contents."
    x = Tk()
    s = x.clipboard_get()
    x.destroy()
    return s

def KMstr_to_int(s):
    s = s.replace(",", "")
    if "K" in s:
        return int(float(s[:-1])*1000)
    if "M" in s:
        return int(float(s[:-1])*1000000)
    if "B" in s:
        return int(float(s[:-1])*1000000000)
    return int(s)

def parse_metadata(s):
    lines = s.split("\n")
    print("Metadata\n", lines)

    for x in PROBLEMS:
        try:
            lines.remove(x)
        except ValueError:
            pass
    
    if s[0] == "#":
        tags = lines[0]
        lines = lines[1:]
    else:
        tags = None

    try:
        subs_line = [line for line in lines[2:] if " subs" in line][0]
        i = lines.index(subs_line)
        title = lines[i-2]
        channel = lines[i-1]
        subs = KMstr_to_int(lines[i].split(" ")[0])
        likes = (0 if lines[i+1] == "Like"
                 else KMstr_to_int(lines[i+1]))
        views = (0 if lines[i+2][0:2] == "No"
                 else KMstr_to_int(lines[i+2].split(" ")[0]))
    except:
        return {"Title":None, "Channel":None, "Tags":None,
                "Views":None,"Likes":None,"Subs":None}
    
    return {"Title":title,
            "Channel":channel,
            "Tags":tags,
            "Views":views,
            "Likes":likes,
            "Subs":subs}

def pick_first(l):
    if len(l) == 0:
        raise ValueError("Nothing new to click on?!?")
    return l[0]

def pick_random(l):
    x = 5
    if len(l) < 5:
        x = len(l)
    if len(l) == 0:
        raise ValueError("Nothing new to click on?!?")
    return l[random.randint(0, x-1)]


## Helpers for post-processing

def get_walk(n, i):
    with open(f"results{n}/vid_results{i}.txt", encoding="UTF-16") as f:
        res = json.load(f)
    return res

def get_run(n):
    res = []
    for i in range(50 if n<300 else 49):
        with open(f"results{n}/vid_results{i}.txt", encoding="UTF-16") as f:
            res.append(json.load(f))
    return res

def make_run_walk_table(n, index=True, **kwargs):
    data = get_run(n)
    res = [["index"] + list(range(len(data)))] if index else []
    for k, f in kwargs.items():
        t = [k]
        for walk in data:
            t.append(f(walk))
        res.append(t)
    return [[x[i] for x in res] for i in range(len(res[0]))]

def make_walk_vid_table(n, i, index=True, **kwargs):
    data = get_walk(n, i)
    res = [["index"] + list(range(len(data)))] if index else []
    for k, f in kwargs.items():
        t = [k]
        for vid in data:
            t.append(f(vid))
        res.append(t)
    return [[x[i] for x in res] for i in range(len(res[0]))]

def make_run_vid_table(n, **kwargs):
    res = [[[]] + make_walk_vid_table(n, i, index=False, **kwargs)[1:]
           for i in range(1, 50 if n<300 else 49)]
    res = [x for y in res for x in y]
    return make_walk_vid_table(n, 0, index=False, **kwargs) + res

def make_whole_walk_table(filt=lambda x: True, **kwargs):
    ns = list(range(101, 107)) + list(range(201, 207)) + list(range(301, 307))
    ns = list(filter(filt, ns))
    res = [[[]] + make_run_walk_table(n, index=False, **kwargs)[1:]
           for n in ns[1:]]
    res = [x for y in res for x in y]
    return make_run_walk_table(ns[0], index=False, **kwargs) + res

def make_whole_run_table(filt=lambda x: True, index = True, **kwargs):
    ns = list(range(101, 107)) + list(range(201, 207)) + list(range(301, 307))
    ns = list(filter(filt, ns))
    res = [["index"] + list(ns)] if index else []
    for k, f in kwargs.items():
        t = [k]
        for n in ns:
            t.append(f(get_run(n)))
        res.append(t)
    return [[x[i] for x in res] for i in range(len(res[0]))]

def make_table(ns, index = True, **kwargs):
    res = [["index"] + list(range(len(ns)))] if index else []
    for k, f in kwargs.items():
        t = [k]
        for n in ns:
            t.append(f(n))
        res.append(t)
    return [[x[i] for x in res] for i in range(len(res[0]))]

def print_table_to_csv(table):
    print("\n".join([",".join([f'"{str(x)}"' for x in line]) for line in table]))

def run_sum(l):
    res = []
    for x in l:
        res += get_run(x)
    return res

RUNS = [100*i+j for i in range(1,4) for j in range(1, 7)]

def NO_ACC():
    return run_sum([101, 102, 201, 202, 301, 302])

def ACC():
    return run_sum([103, 104, 105, 106, 203, 204, 205, 206, 303, 304, 305, 306])

def FEMALE():
    return run_sum([103, 104, 203, 204, 303, 304])

def MALE():
    return run_sum([105, 106, 205, 206, 305, 306])

def GAMING():
    return run_sum([101, 102, 103, 104, 105, 106])

def FASHION():
    return run_sum([201, 202, 203, 204, 205, 206])

def HOMEPAGE():
    return run_sum([301, 302, 303, 304, 305, 306])

def PICK_FIRST():
    return run_sum([101, 103, 105, 201, 203, 205, 301, 303, 305])

def PICK_RANDOM():
    return run_sum([102, 104, 106, 202, 204, 206, 302, 304, 306])

def Table():

    def f(run):
        data = [x["Channel"] for y in run for x in y]
        return max(set(data), key=data.count)

    def g(run):
        data = [x["Channel"] for y in run for x in y]
        return data.count(max(set(data), key=data.count))

    def h(run):
        data = [x["Subs"] for y in run for x in y]
        return int(round(sum(data)/len(data), 0))

    def i(run):
        data = [x["Views"] for y in run for x in y]
        return int(round(sum(data)/len(data), 0))

    def j(run):
        data = [x[0]["Views"] for x in run]
        return int(round(sum(data)/len(data), 0))

    def k(run):
        data = [x[9]["Views"] for x in run]
        return int(round(sum(data)/len(data), 0))

    def l(run):
        data = [len(x["ads"]) for y in run for x in y]
        return round(sum(data)/len(data), 4)

    def m(run):
        def n(c, nxt):
            for x in nxt:
                if c in x:
                    return True
            return False
        
        data = [sum([1 if n(vid["Channel"], nxt) else 0
                     for nxt in vid["nexts"]])/5
                for walk in run for vid in walk] 
        return round(sum(data)/len(data), 4)

    tab = make_whole_run_table(modal_chan=f, modal_vids=g, subs=h, views=i,
                               fviews=j, lviews=k, ads=l, cluster=m)
    tab1 = make_table([NO_ACC(), ACC(), FEMALE(), MALE(), GAMING(), FASHION(),
                       HOMEPAGE(), PICK_FIRST(), PICK_RANDOM()],
                      modal_chan=f, modal_vids=g, subs=h, views=i,
                      fviews=j, lviews=k, ads=l, cluster=m)[1:]
    print_table_to_csv(tab+tab1)
