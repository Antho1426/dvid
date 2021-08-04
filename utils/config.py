#!/usr/local/bin/python3.7

# config.py

# Configuration file in which some paths, URLs and other constants are defined


## Required packages
from pathlib import Path


## Initialization of the first time using facebook_downloader_1 alternative
firstTimeFB1Alt = True
firstTimeLoggedInInsta = True



## Configurations
DOWNLOAD_DIRECTORY = '/Users/anthony/Downloads' # name of the folder in which we will put the downloaded video files (this can be adjusted by the user)
DEFAULT_DOWNLOAD_DIRECTORY = str(Path.home() / "Downloads")
GOOGLE = 'https://www.google.com/'
TEAM_STAMA = 'https://www.teamstama.com/'
YTMP3_URL = 'https://ytmp3.cc/'
SAVE_AS_URL = 'https://saveas.co'
GET_FVID_URL = 'https://www.getfvid.com'
EXPERTS_PHP_INSTA = 'https://www.expertsphp.com/instagram-reels-downloader.php'
SNAP_TIK = 'https://snaptik.app'
SAVE_FROM_INSTA = 'https://en.savefrom.net/download-from-instagram'
SAVE_FROM_DAILYMOTION = 'https://en.savefrom.net/10-how-to-download-dailymotion-video.html'
EXPERTS_PHP_PINT = 'https://www.expertsphp.com/pinterest-video-downloader.html'