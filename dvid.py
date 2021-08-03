#!/usr/local/bin/python3.7



# dvid.py



#==================
debugModeOn = True
#==================



## Setting the current working directory automatically
import os
project_path = os.getcwd() # getting the path leading to the current working directory
os.getcwd() # printing the path leading to the current working directory
os.chdir(project_path) # setting the current working directory based on the path leading to the current working directory









## Required packages
import os
import sys
from tkinter import Tk # to eventually access the string situated in the clipboard
from tqdm import tqdm # for having a nice progress bar
from termcolor import colored
from argparse import ArgumentParser
from validator_collection import checkers # to validate URLs
# Importing the helper functions
# (Cf. "Import Python Files From Another Directory", https://gist.github.com/MRobertEvers/55a989b4883ea8d7715d2e156627f034)
from utils.utils import (
    remove_empty_lines,
    sort_urls,
    write_in_log_text_file,
    connected_to_internet,
    log_error,
    retrieve_url,
    notify,
    get_latest_webdriver
)
# Importing the constants defined in config.py
import utils.config
from utils.config import (
    DOWNLOAD_DIRECTORY
)
# Importing the downloaders
from utils.downloader import (
    universal_downloader_you_get,
    universal_downloader_youtube_dl,
    youtube_downloader,
    instagram_downloader,
    twitter_downloader,
    facebook_downloader_1,
    facebook_downloader_2,
    linkedin_downloader,
    tiktok_downloader,
    twitch_downloader,
    vimeo_downloader,
    dailymotion_downloader,
    zwanzig_minuten_downloader,
    pinterest_downloader
)





## Parsing the input argument
if not debugModeOn:
    #---
    parser = ArgumentParser(description="'dvid.py' is a Python program that\
    allows to download videos from various URLs.\
    The software currently supports videos hosted on following platforms: \
    YouTube, Instagram, Twitter, Facebook, LinkedIn, TikTok, Twitch, Vimeo, \
    Dailymotion. In case a video doesn't come from one of the above-mentioned \
    websites, the program still tries to download it using a default method \
    based on the 'youtube_dl' Python package.")
    parser.add_argument('--textFilePath', metavar='/path/to/your/text/file/my_text_file.txt', type=str, default='clipboard', help='download the video(s) based on the URLs situated in the text file')
    args = parser.parse_args()
    argsDottextFilePath = args.textFilePath
    #---
else: # in case we are in "debug mode"
    argsDottextFilePath = 'text file required'





## Initializations



# Moving to the "Downloads" directory
os.chdir(DOWNLOAD_DIRECTORY)

# Initializing the number of unrecognized URLs to '0'
number_of_unrecognized_urls = 0

# Getting the latest available webdriver version for Chrome at the very
# beginning of the program (so that the user can directly click on the "Allow"
# button in case we would need selenium)
print(colored('A) Getting latest web driver version...', 'magenta', 'on_grey', attrs=['bold', 'underline']))
try:
    driver = get_latest_webdriver()
except Exception as e:
    print("\n\n\n🙁 Process aborted... The web driver could not be set. Please make sure your computer is connected to internet.")
    # Posting macOS X notification
    notify(title='dvid.py',
           subtitle='Process aborted... ❌',
           message='The web driver could not be set. Please make sure your computer is connected to internet.',
           sound_path=project_path + "/Hero.wav")

    # Terminating the program right now
    sys.exit()

# Handling the input of the program
print(colored('B) Handling the input of the program', 'magenta', 'on_grey', attrs=['bold', 'underline']))

if argsDottextFilePath == 'clipboard': # in case we want to download only one video using the copied URL currently situated in the clipboard (this is only available when NOT in "debug mode")
    textFileAsInput = False

    # Retrieving the stored clipboard value
    clipboard_value = Tk().clipboard_get()

    # Checking if the validity of the URL
    url_validated = checkers.is_url(clipboard_value)

    if url_validated:
        lines = [clipboard_value]
        number_of_lines = 1

    else:
        print("\n\n\n🙁 Process aborted... Clipboard does NOT contain a valid URL!")
        # Posting macOS X notification
        notify(title='dvid.py',
               subtitle='Process aborted... ❌',
               message='Clipboard does NOT contain a valid URL!',
               sound_path=project_path + "/Hero.wav")

        # Terminating the program right now
        sys.exit()

else: # in case we have a text file containing a list of URLs as input
    textFileAsInput = True

    # Handling the text file
    if not debugModeOn: # if not in debug mode, we retrieve the custom text file path set by the user
        file_path = argsDottextFilePath
    else: # in case of the debug mode, the debug text file "urls_test.txt" situated at the root of the project is used
        file_path = project_path + '/urls_test.txt'
    file_name = file_path.split("/")[-1]
    # Removing all the empty lines
    remove_empty_lines(file_path)
    # Sorting the URLs
    sort_urls(file_path)
    # Opening the URLs text file
    file = open(file_path, "r")
    # Extracting the lines from the URLs text file
    lines = file.readlines()
    number_of_lines = len(lines)

    # Creating "log.txt" in the DOWNLOAD_DIRECTORY if the text file with the URLs is
    # not empty and if "log.txt" does not exist yet
    if number_of_lines > 0:
        logFilePath = str(DOWNLOAD_DIRECTORY) + '/' + 'log.txt'
        if not os.path.exists(logFilePath):
            with open(logFilePath, "w"):
                pass
        # Or erasing its content in case it already exists
        else:
            logFileTXT = open(logFilePath, "r+")
            logFileTXT.truncate(0)
            logFileTXT.close()
        # Writing the heading of the text file at the top of the text file:
        write_in_log_text_file("'log.txt' lists all the URLs that couldn't be handled to retrieve the linked video:\n")









## Main loop
if number_of_lines > 0:
    print(colored('C) Scrolling through the list of URLs...', 'magenta', 'on_grey', attrs=['bold', 'underline']))
    iter = 0
    for i in tqdm(range(number_of_lines)):
        iter += 1

        # Checking internet connection
        if connected_to_internet():

            url = retrieve_url(lines, number_of_lines, i)
            print('\n --> Current URL: ', url)

            # ---------------------------------
            # YouTube case:
            if ('youtu' in url):
                try:
                    youtube_downloader(number_of_unrecognized_urls, url, textFileAsInput, driver)
                except Exception as e:
                    number_of_unrecognized_urls += 1
                    log_error(e, number_of_unrecognized_urls, url, textFileAsInput)

            # ---------------------------------
            # Instagram case:
            elif ('instagram' in url):
                try:
                    number_of_unrecognized_urls = instagram_downloader(number_of_unrecognized_urls, url, textFileAsInput, driver, project_path)
                except Exception as e:
                    number_of_unrecognized_urls += 1
                    log_error(e, number_of_unrecognized_urls, url, textFileAsInput)

            # ---------------------------------
            # Twitter case:
            elif ('twitter' in url):
                try:
                    twitter_downloader(url)
                except Exception as e:
                    number_of_unrecognized_urls += 1
                    log_error(e, number_of_unrecognized_urls, url, textFileAsInput)

            # ---------------------------------
            # Facebook case:
            elif ('facebook' in url):
                try:
                    facebook_downloader_1(url, driver, project_path)
                except Exception as e:
                    number_of_unrecognized_urls += 1
                    log_error(e, number_of_unrecognized_urls, url, textFileAsInput)
            elif ('fb.' in url):
                try:
                    facebook_downloader_2(url, driver)
                except Exception as e:
                    number_of_unrecognized_urls += 1
                    log_error(e, number_of_unrecognized_urls, url, textFileAsInput)

            # ---------------------------------
            # LinkedIn case:
            elif ('linkedin' in url):
                try:
                    linkedin_downloader(url, driver)
                except Exception as e:
                    number_of_unrecognized_urls += 1
                    log_error(e, number_of_unrecognized_urls, url, textFileAsInput)

            # ---------------------------------
            # TikTok case:
            elif ('tiktok' in url):
                try:
                    tiktok_downloader(url, driver)
                except Exception as e:
                    number_of_unrecognized_urls += 1
                    log_error(e, number_of_unrecognized_urls, url, textFileAsInput)

            # ---------------------------------
            # Twitch case:
            elif ('twitch' in url):
                try:
                    twitch_downloader(url)
                except Exception as e:
                    number_of_unrecognized_urls += 1
                    log_error(e, number_of_unrecognized_urls, url, textFileAsInput)

            # ---------------------------------
            # Vimeo case:
            elif ('vimeo' in url):
                try:
                    vimeo_downloader(url)
                except Exception as e:
                    number_of_unrecognized_urls += 1
                    log_error(e, number_of_unrecognized_urls, url, textFileAsInput)

            # ---------------------------------
            # Dailymotion case:
            elif ('dailymotion' in url):
                try:
                    dailymotion_downloader(url, driver)
                except Exception as e:
                    number_of_unrecognized_urls += 1
                    log_error(e, number_of_unrecognized_urls, url, textFileAsInput)

            # ---------------------------------
            # 20 Minuten case:
            elif ('www.20min.ch/video/' in url):
                try:
                    zwanzig_minuten_downloader(url, driver)
                except Exception as e:
                    number_of_unrecognized_urls += 1
                    log_error(e, number_of_unrecognized_urls, url, textFileAsInput)

            # ---------------------------------
            # Pinterest case:
            elif ('https://pin' in url):
                try:
                    pinterest_downloader(url, driver)
                except Exception as e:
                    number_of_unrecognized_urls += 1
                    log_error(e, number_of_unrecognized_urls, url, textFileAsInput)

            # ---------------------------------
            # Unrecognized case:
            else:

                # Ultimate try to download the video
                try:
                    universal_downloader_youtube_dl(url)

                # Logging error in case no method worked at all
                except Exception as e:
                    number_of_unrecognized_urls += 1
                    log_error(e, number_of_unrecognized_urls, url, textFileAsInput)


        else: # in case the computer is not connected to internet anymore
            print("\n\n\n🙁 Process aborted... The internet connection has been lost.")
            number_of_processed_urls = iter - 2
            if number_of_processed_urls < 0: number_of_processed_urls = 0
            # Posting macOS X notification
            notify(title='dvid.py',
                   subtitle='Process aborted... ❌',
                   message='The internet connection has been lost. The URLs could be successfully processed up to URL n°{0}.'.format(number_of_processed_urls),
                   sound_path=project_path + "/Hero.wav")

            # Quitting the useless web driver
            driver.quit()

            # Terminating the program right now
            sys.exit()


    # Once the 'for loop' is done, quitting web driver
    driver.quit()

    # Displaying success message
    print("\n\n\n🏆 💻 🎉 Process completed!")

    # Posting macOS X notification
    if number_of_lines == number_of_unrecognized_urls:
        notify(title='dvid.py',
               subtitle='Videos NOT downloaded ❌',
               message='The log text file is available in {0}'.format(DOWNLOAD_DIRECTORY),
               sound_path=project_path + "/Hero.wav")
    else:
        notify(title = 'dvid.py',
            subtitle = 'Videos downloaded ✅',
            message  = 'The videos are available in {0}'.format(DOWNLOAD_DIRECTORY),
            sound_path = project_path + "/Hero.wav")




# In case the text file with the URLs is empty, following error message is
# returned
else:
    if textFileAsInput:
        print(f"\n\n\n🙁 Process aborted... {file_name} is empty.")
        # Posting macOS X notification
        notify(title='dvid.py',
               subtitle='Process aborted... ❌',
               message='{0} is empty.'.format(file_name),
               sound_path=project_path + "/Hero.wav")