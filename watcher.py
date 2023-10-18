import time
import json
import random
import csv
import os

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.mouse_button import MouseButton
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

from helpers import *
from accounts import *

# For basic usage just set these four variables and run this script
# If you want to do something else with it create a separate script that
# imports this one, and use the Watcher object for watching.

# Must have the helpers.py file in the same directory!!

WALK_LENGTH = 3 # Number of videos per walk
NUMBER_OF_WALKS = 1 # Number of walks to execute
WATCH_DURATION = 60 # seconds
CLOSE_BROWSER = True # Close browser between walks?

# Not closing is currently untested but *should* work.

# TODO: Watch it for a bit and try to figure out what's tripping it up
#       Add functionality to seed from categories rather than just homepage

class Watcher:
    """
    Usage: Watcher(i)(m, n)
    Performs m random walks of length n, saves the results in results{i}.
    Does not close browser between walks, make a new Watcher each time for this.
    """

    def __init__(self, index, account=None, choose_fn=pick_random, seed=None):
        self.ads_seen = []
        self.vids_watched = []
        self.autoplay = True
        self.logged_in = account is None

        self.index = index
        self.account = account

        self.next_strategy = choose_fn
        self.seed = seed

        self.driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()))
        
        self.driver.implicitly_wait(0.5)

    def get_ad_link(self, ad):
        try:
            ActionChains(self.driver)\
                .context_click(ad)\
                .move_to_element_with_offset(ad, 200, 15)\
                .click()\
                .perform()
        except:
            return None
        
        s = get_clipboard()
        if s[:17] == "https://youtu.be/":
            return s[17:]

        try:
            dic = eval(s.replace("true", "True").replace("false", "False"))
        except:
            return None
        else:
            if dic['ns'] == 'yt':
                return dic["addocid"]
        return None

    def skip_ad(self):
        skip = get_by_class(self.driver, SKIP_BUTTON)
        if skip is not None:
            try:
                skip.click()
            except:
                pass

    def login(self):
        buttons = get_by_classs(self.driver, SIGN_IN)
        sign_in_button = next(filter(lambda b: b.text == "Sign in", buttons))
        sign_in_button.click()
        time.sleep(2)
        
        box = get_by_ID(self.driver, "identifierId")
        box.send_keys(self.account.email)
        time.sleep(0.5)
        box.send_keys(Keys.ENTER)
        time.sleep(2)

        box = get_by_name(self.driver, "Passwd")
        box.send_keys(self.account.password)
        time.sleep(0.5)
        box.send_keys(Keys.ENTER)
        time.sleep(2)

        self.logged_in = True

    def reject_cookies(self):
        buttons = get_by_classs(self.driver, COOKIE_BUTTON)
        is_reject = lambda b: b.text == "Reject all"

        try:
            reject_button = next(filter(is_reject, buttons))
        except:
            pass
        else:
            reject_button.click()

    def setup_youtube(self):
        ActionChains(self.driver)\
            .key_down(Keys.CONTROL)\
            .send_keys("m")\
            .key_up(Keys.CONTROL)\
            .perform()
        
        self.driver.get("https://www.youtube.com")
        time.sleep(3)

        self.reject_cookies()
        time.sleep(3)

        if not self.logged_in:
            self.login()

        if self.seed is None:
            self.load_homepage_video()
        else:
            self.load_from_seed()

        for _ in range(5):
            if(self.disable_autoplay()):
                break

    def load_homepage_video(self):
        vids = []
        for vid in get_by_IDs(self.driver, "content")[1:]:
            try:
                v = get_by_ID(vid, "video-title-link")
                if v is not None:
                    vids.append(v)
            except:
                pass
        vids[random.randint(0, 7)].click()
        time.sleep(3)

    def load_from_seed(self):
        self.driver.get(self.seed)
        time.sleep(3)

        get_by_class(self.driver, PLAY).click()
        time.sleep(1)
        
    def disable_autoplay(self):
        autoplay = get_by_class(self.driver, AUTOPLAY)
        if autoplay is None:
            return False
        if autoplay.get_dom_attribute("aria-checked") == "true":
            try:
                autoplay.click()
            except:
                pass
            else:
                self.autoplay = False
        return True

    def get_ad_data(self):
        ad_links = []
        done = 0

        while done < 5:
            ad = get_by_class(self.driver, VISIT_AD)
            if ad is None:
                done += 1
            else:
                ad_link = self.get_ad_link(ad)
                if ad_link is not None and ad_link not in ad_links:
                    ad_links.append(ad_link)

                self.skip_ad()

            time.sleep(1)

        for ad_link in ad_links:
            self.ads_seen.append(YOUTUBE_PREFIX + ad_link)

    def watch_video(self):     
        self.get_ad_data()

        metadata_text = get_by_class(self.driver, METADATA).text
        if metadata_text is not None:
            vid_data = parse_metadata(metadata_text)

        started = time.time()

        while True:
            if time.time() - started > WATCH_DURATION:
                break
            
            play_button = get_by_class(self.driver, PLAY)
            if play_button is not None and replay_state(play_button):
                break
            
            if self.autoplay:
                self.disable_autoplay()
                
            ad = get_by_class(self.driver, VISIT_AD)
            if ad is None:
                time.sleep(2)
            else:
                self.get_ad_data()

        print("Done watching")

        vid_data["link"] = self.driver.current_url
        
        if self.account is None:
            next_vids = get_by_classs(self.driver, NEXT_VIDEO)[2:7]
        else:
            for i in range(3, 8):
                try:
                    next_vids = get_by_IDs(get_by_classs(self.driver,
                                            NEXT_VIDEO)[i], "dismissible")[:5]
                    if len(next_vids) > 0:
                        print(i)
                        break
                except:
                    pass

        vid_data["ads"] = [ad for ad in self.ads_seen]
        self.ads_seen = []
        
        vid_data["nexts"] = [n.text.split("\n") for n in next_vids]
        
        try:
            vid_data["next_links"] = [
              get_by_ID(n, "thumbnail").get_property("href") for n in next_vids]
        except:
            pass
        
        self.vids_watched.append(vid_data)
        
        self.next_strategy(next_vids).click()

    def save_results(self):
        print("Writing data:")
        print(self.vids_watched)
        
        sdir = f"results{self.index}"
        if not os.path.exists(sdir):
            os.mkdir(sdir)

        i = 0
        while os.path.exists(sdir+f"/vid_results{i}.txt"):
            i += 1
        
        vidfp = sdir+f"/vid_results{i}.txt"
        with open(vidfp, "w", newline='', encoding="UTF-16") as f:
            json.dump(self.vids_watched, f)
            #writer = csv.DictWriter(f, fieldnames=FIELD_NAMES)
            #writer.writeheader()
            #writer.writerows(self.vids_watched)

    def __call__(self, m, n):
        for _ in range(m):
            try:
                self.setup_youtube()
                for _ in range(n):
                    self.watch_video()
            except Exception as e:
                print(e)
            finally:
                self.save_results()
        self.driver.quit()


if __name__ == "__main__":
    if CLOSE_BROWSER:
        for _ in range(NUMBER_OF_WALKS):
            w = Watcher(0, alice)
            w(1, WALK_LENGTH)
    else:
        w = Watcher(0)
        w(NUMBER_OF_WALKS, WALK_LENGTH)
