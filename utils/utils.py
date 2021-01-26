#!/usr/local/bin/python3.7

# utils.py

# Python script containing the helper and webdriver functions



## Required packages
import os
import glob
import platform
import datetime
import applescript
from time import sleep
from PIL import ImageGrab
from termcolor import colored
from selenium import webdriver
from playsound import playsound
from urllib.request import Request, urlopen
from webdriver_manager.chrome import ChromeDriverManager
# Importing the constants defined in config.py
from utils.config import (
    DOWNLOAD_DIRECTORY,
    GOOGLE
)



## Removing empty lines from text file
def remove_empty_lines(file_path):
    with open(file_path) as in_file, open(file_path, 'r+') as out_file:
        out_file.writelines(line for line in in_file if line.strip())
        out_file.truncate()



## Sorting the URLs by platform
def sort_urls(file_path):

    # Reading the text file
    with open(file_path, "r+") as file:
        lines = file.readlines()
        file.close()

        # Initializing the different lists
        youtu_list = []
        instagram_list = []
        twitter_list = []
        facebook_list = []
        facebook_story_list = []
        fb_list = []
        linkedin_list = []
        tiktok_list = []
        twitch_list = []
        vimeo_list = []
        dailymotion_list = []
        zwanzig_minuten_list = []
        pinterest_list = []
        others_list = []

        # Going through the lines and populating each list
        for i in range(len(lines)):
            if 'youtu' in lines[i]:
                youtu_list.append(lines[i])
                continue
            elif 'instagram' in lines[i]:
                instagram_list.append(lines[i])
                continue
            elif 'twitter' in lines[i]:
                twitter_list.append(lines[i])
                continue
            elif 'facebook' in lines[i]:
                if 'story' in lines[i]:
                    facebook_story_list.append(lines[i])
                else:
                    facebook_list.append(lines[i])
                continue
            elif 'fb' in lines[i]:
                fb_list.append(lines[i])
                continue
            elif 'linkedin' in lines[i]:
                linkedin_list.append(lines[i])
                continue
            elif 'tiktok' in lines[i]:
                tiktok_list.append(lines[i])
                continue
            elif 'twitch' in lines[i]:
                twitch_list.append(lines[i])
                continue
            elif 'vimeo' in lines[i]:
                vimeo_list.append(lines[i])
                continue
            elif 'dailymotion' in lines[i]:
                dailymotion_list.append(lines[i])
                continue
            elif 'www.20min.ch/video/' in lines[i]:
                zwanzig_minuten_list.append(lines[i])
                continue
            elif 'https://pin' in lines[i]:
                pinterest_list.append(lines[i])
            else:
                others_list.append(lines[i])

        # Composing the final list of sorted URLs
        lines_sorted = facebook_story_list\
                       + fb_list \
                       + facebook_list \
                       + tiktok_list \
                       + instagram_list \
                       + youtu_list \
                       + linkedin_list \
                       + dailymotion_list \
                       + twitter_list \
                       + twitch_list \
                       + vimeo_list \
                       + zwanzig_minuten_list \
                       + pinterest_list \
                       + others_list

        # Adding a '\n' at the end of each line
        for i in range(len(lines_sorted)):
            if lines_sorted[i][-1] != '\n':
                lines_sorted[i] = lines_sorted[i] + '\n'

        # Removing the '\n' of the last element of the list
        lines_sorted[-1] = lines_sorted[-1].replace('\n', '')

    # Writing the sorted URLs in the text file
    with open(file_path, "w") as file:
        file.writelines(lines_sorted)
        file.close()



## Writing in log text file
def write_in_log_text_file(log_message):
    logAllFilesTXT = open(str(DOWNLOAD_DIRECTORY) + '/' + 'log.txt', "a")
    logAllFilesTXT.write(log_message)
    logAllFilesTXT.close()



## Checking internet connection
def connected_to_internet():
    """
    Function returning 'True' if the computer is connected to internet and
    'False otherwise'
    Cf.: https://stackoverflow.com/questions/3764291/checking-network-connection
    """
    try:
        test_link = 'http://216.58.192.142' # IP addresses for google.com
        req = Request(test_link, headers={'User-Agent': 'XYZ/3.0'})
        urlopen(req, timeout=20).read()
        return True
    except Exception as e:
        return False



## Logging error
def log_error(e, number_of_unrecognized_urls, url, textFileAsInput):
    # Printing the error to the console
    print("\n\n⚠️", colored("URL issue n°{0}".format(number_of_unrecognized_urls).strip(), 'red') + ":\n" + url + "\nError message: {0}\n".format(e))
    if textFileAsInput:
        # Adding this URL to the log text file
        write_in_log_text_file("\n\n⚠️ URL issue n°{0}:\n".format(number_of_unrecognized_urls) + url + "\nError message: {0}".format(e))



## Retrieving URL from line of text file
def retrieve_url(lines, number_of_lines, iter):
    """
    Function to get rid of the "\n" at the end of all lines except the last one
    :param lines: list containing all the URLs present in the "urls.txt" text file
    :param number_of_lines: length of the "lines" list
    :param iter: iteration at which we are currently situated in the elements of the "lines" list
    :return: url string
    """
    if iter < (number_of_lines - 1):
        url = lines[iter]
        url = url[:-1]
    else:
        url = lines[-1]

    return url



## Writing comment in metadata "Comments" part of file
# (in case the operating system on which the program is running is macOS)
def write_metadata_comment(file_path, comment):
    if platform.system() == 'Darwin':
        applescript.tell.app("Finder", f'set comment of (POSIX file "{file_path}" as alias) to "{comment}" as Unicode text')
    else:
        print(colored("Error!", 'red'), 'Writing comment in metadata "Comments" part of file is currently only supported for macOS.')



## Getting path of lastly downloaded video
def get_last_vid_path(DOWNLOAD_DIRECTORY):
    list_of_files_in_DOWNLOAD_DIRECTORY = glob.glob(DOWNLOAD_DIRECTORY + '/*')
    video_path = max(list_of_files_in_DOWNLOAD_DIRECTORY, key=os.path.getctime)

    return video_path



## Adding the current date in front of video name and writing comment in metadata "Comments" part of file
def add_date_and_metadata(DOWNLOAD_DIRECTORY, url, number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY, number_of_videos_to_download):

    # Computing the current date
    date = str(datetime.datetime.now()).split(" ")[0]

    # Waiting until (all) the video(s) of the current post is (are) downloaded
    current_number_of_mp4_files_in_DOWNLOAD_DIRECTORY = len(glob.glob1(DOWNLOAD_DIRECTORY,"*.mp4"))
    time_slept = 0
    while current_number_of_mp4_files_in_DOWNLOAD_DIRECTORY != number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY + number_of_videos_to_download:
        # Re-checking the current total number of ".mp4" files in DOWNLOAD_DIRECTORY
        current_number_of_mp4_files_in_DOWNLOAD_DIRECTORY = len(glob.glob1(DOWNLOAD_DIRECTORY, "*.mp4"))
        print(" video still downloading...")
        sleep(1)
        time_slept += 1
        if time_slept > 3600: # If after 1 hour, we still don't have the expected number of video(s)
            print(colored("Error!", 'red'), "Time exceeded while trying to download current video ({0}).".format(url))
            break

    if current_number_of_mp4_files_in_DOWNLOAD_DIRECTORY == number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY + number_of_videos_to_download:
        # Getting (all) the new video file(s) of the current post
        video_files = glob.glob(DOWNLOAD_DIRECTORY + "/*.mp4")
        video_files.sort(key=os.path.getctime, reverse=True)
        new_video_files = video_files[0:number_of_videos_to_download]

        for i in range(number_of_videos_to_download):
            # Renaming the video(s)
            current_video_name = new_video_files[i]
            new_video_name = DOWNLOAD_DIRECTORY + '/' + date + '_' + new_video_files[i].replace(DOWNLOAD_DIRECTORY + '/', '')
            os.rename(current_video_name, new_video_name)
            # Writing comment in metadata "Comments" part of file
            write_metadata_comment(new_video_name, url)



## Notifier function for posting macOS X notification
def notify(title, subtitle, message, sound_path):
    # Playing sound
    playsound(sound_path)
    # Displaying the Desktop notification
    t = '-title {!r}'.format(title)
    s = '-subtitle {!r}'.format(subtitle)
    m = '-message {!r}'.format(message)
    os.system('terminal-notifier {}'.format(' '.join([m, t, s])))



## Webdriver setting functions
def get_latest_webdriver():
    options = get_web_driver_options()
    #set_automation_as_head_less(options) # uncommenting this line makes the web driver run in the background (/!\ dvid.py is NOT conceived to work with the web driver running in the background, it has to be visible during the whole process! So please, leave this line commented!)
    set_ignore_certificate_error(options)
    set_browser_as_incognito(options)
    driver = get_chrome_web_driver(options)
    # Getting the resolution of the screen
    img = ImageGrab.grab()
    screen_width = img.size[0]
    screen_height = img.size[1]
    # Setting the size of the web driver window to half the size of the screen
    window_width = int(screen_width/4)
    window_height = screen_height
    driver.set_window_size(window_width, window_height)  # (240, 160) # driver.minimize_window() # driver.maximize_window()
    # Positioning the web driver window on the right-hand side of the screen
    driver.set_window_position(window_width, 0)
    # Navigating to GOOGLE
    driver.get(GOOGLE)

    return driver

def get_chrome_web_driver(options):
    # Using automatically the correct chromedriver by using the webdrive-manager (cf.: https://stackoverflow.com/questions/60296873/sessionnotcreatedexception-message-session-not-created-this-version-of-chrome)
    return webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

def get_web_driver_options():
    return webdriver.ChromeOptions()

def set_ignore_certificate_error(options):
    options.add_argument('--ignore-certificate-errors')

def set_browser_as_incognito(options):
    options.add_argument('--incognito')

# A headless browser is a web-browser without a graphical user interface.
# This program will behave just like a browser but will not show any GUI.
# Running WebDriver Automated Tests in headless mode provides advantages in
# terms of speed of execution of tests
# (With this enabled, everything will run in the BACKGROUND)
def set_automation_as_head_less(options):
    options.add_argument('--headless')