# 4th-year-project
A copy of the code used in my 4th year project, an audit of the YouTube recommendation algorithm

This project includes 18 directories that the results were stored in, as json files as I felt creating a proper database was unnecessary for the scale of the project.

accounts.py - Stores the sign in details for the YouTube accounts used, passwords redacted
adgetter.py - Script for scraping the list of advert links collected by the main bot and returning the company running the advert
helpers.py - Some extra functions separated from the main script for neatness
testX.py - I had to create 6 different scripts to run up to 6 bots at the same time, they simply open the seed video list and run the class from watcher.py
watcher.py - The main script that watches the YouTube videos, scraping data as it goes. It watches a random homepage for 1 minute, then clicks on a recommended video at the side and watches that for one minute, repeat up to the walk length chosen. Optionally takes an account to sign into, a method of choosing from the recommended videos and a seed video to start the walk from instead of a homepage video.

fashion_vids.txt, gaming_vids.txt and homepage_vids.txt - Lists of 50 seed videos drawn from either the homepage, gaming section or fashion section of YouTube
ad_links.txt and ad_links_table.txt - A list of the links to adverts collected during the runs and a table mapping those links (removing duplicates) to the advertising company
data_spreadsheet.xlsx - A full spreadsheet detailing all the data collected along with various statistical tests ran on that data
