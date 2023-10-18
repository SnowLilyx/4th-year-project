import json

from watcher import *

class AdGetter(Watcher):
    def __call__(self, links):
        results = {}
        
        self.driver.get("https://www.youtube.com")
        time.sleep(3)

        self.reject_cookies()
        time.sleep(3)
        
        for link in links:
            try:
                res = self.get_ad_data(link)
                results[link] = res
            except Exception as e:
                print(e)
                results[link] = None
        self.save_results(results)
        self.driver.quit()

    def get_ad_data(self, link):
        self.driver.get(link)
        time.sleep(3)
        
        metadata_text = get_by_class(self.driver, METADATA).text
        if metadata_text is not None:
            data = parse_metadata(metadata_text)["Channel"]
            print(data)
        
        return data

    def save_results(self, results):
        print(results)
        with open("ad_links_conversion_table3.txt", "w", encoding="UTF-16") as f:
            json.dump(results, f)

    @staticmethod
    def get_links(f):
        with open(f, encoding="UTF-16") as f:
            links = json.load(f)
        return links

if __name__ == "__main__":
    with open("ad_links3.txt") as f:
        links = json.load(f)
        print(len(links))
    AdGetter(69)(links)
