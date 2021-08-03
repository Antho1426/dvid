#!/usr/local/bin/python3.7

# downloader.py

# Python script containing the different algorithms used to download videos from
# various sources




## Required packages
import os
import re
import glob
from time import sleep
import shutil
import youtube_dl # pip3.7 install youtube_dl (version: youtube_dl 2020.12.9)
import urllib.request
from urllib.request import Request, urlopen
from termcolor import colored
#-- To work with web pages
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
# Importing utility and webdriver functions defined in utils.py
from utils.utils import (
    write_in_log_text_file,
    add_date_and_metadata,
)
# Importing the constants defined in config.py
import utils.config
from utils.config import (
    DOWNLOAD_DIRECTORY,
    DEFAULT_DOWNLOAD_DIRECTORY,
    YTMP3_URL,
    SAVE_AS_URL,
    GET_FVID_URL,
    EXPERTS_PHP_INSTA,
    SNAP_TIK,
    SAVE_FROM_INSTA,
    SAVE_FROM_DAILYMOTION,
    EXPERTS_PHP_PINT
)










## Universal downloaders

# Using you-get (cf.: https://github.com/soimort/you-get, https://pypi.org/project/you-get/0.3.8/) (pip3 install you-get)
def universal_downloader_you_get(url):

    # 1) Issuing the you-get Terminal command
    print('1) Issuing the you-get Terminal command')
    #  Example: you-get 'https://www.youtube.com/watch?v=jNQXAC9IVRw'
    number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY = len(glob.glob1(DOWNLOAD_DIRECTORY, "*.mp4"))
    command = 'you-get ' + url
    returned_value = os.system(command)

    if returned_value == 0: # if the video has successfully been downloaded

        # 2) In case the downloaded file has the ".webm" extension, converting it
        # into ".mp4"
        print('2) Eventually converting from ".webm" to ".mp4"')
        #  Example: ffmpeg -i "Me at the zoo.webm" -crf 23 "file.mp4"
        # Cf. info on "Converting WebM to MP4 Using FFmpeg" (https://blog.addpipe.com/converting-webm-to-mp4-with-ffmpeg/):
        # When encoding video with H.264, the video quality can be controlled using
        # a quantizer scale (crf value, crf stands for Constant Rate Factor) which
        # can take values from 0 to 51: 0 being lossless, 23 the default and 51 the
        # worst possible. So the lower the value the better the quality. You can
        # leave the default value or, for a smaller bitrate, you can raise the value
        webm_files = glob.glob(DOWNLOAD_DIRECTORY + "/*.webm")
        mp4_files = glob.glob(DOWNLOAD_DIRECTORY + "/*.mp4")
        webm_and_mp4_files = webm_files + mp4_files
        webm_and_mp4_files.sort(key=os.path.getmtime, reverse=True)
        new_video_file = webm_and_mp4_files[0]
        new_video_file_name = new_video_file.split('/')[-1]
        if '.webm' in new_video_file_name: # in case the downloaded video has the ".webm" extension, converting it into ".mp4"
            new_video_file_name_without_extension = new_video_file_name.replace('.webm','')
            command = 'ffmpeg -i "' + new_video_file_name + '" -crf 23 "' + new_video_file_name_without_extension + '.mp4"'
            returned_value = os.system(command)
            # Removing the ".webm" file
            os.remove(new_video_file)

        # 3) Adding the current date in front of the lastly downloaded video name
        # and writing url to metadata "Comments" part of the downloaded file
        print('3) Adding date and metadata')
        add_date_and_metadata(DOWNLOAD_DIRECTORY, url, number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY, number_of_videos_to_download=1)


# Using youtube_dl
def universal_downloader_youtube_dl(url):
    number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY = len(glob.glob1(DOWNLOAD_DIRECTORY, "*.mp4"))
    ydl_opts = {} # cf.: https://www.bogotobogo.com/VideoStreaming/YouTube/youtube-dl-embedding.php
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        # a) Downloading the video using youtube_dl
        print(' a) Downloading the video using youtube_dl')
        ydl.download([url]) # downloading the video

    # b) Adding the current date in front of the lastly downloaded video name
    # and writing url to metadata "Comments" part of the downloaded file
    print(' b) Adding date and metadata')
    add_date_and_metadata(DOWNLOAD_DIRECTORY, url,
                          number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY,
                          number_of_videos_to_download=1)



## YouTube downloader
def youtube_downloader(number_of_unrecognized_urls, url, textFileAsInput, driver):

    # 1) Checking the availability of the YouTube video
    print("1) Checking the availability of the YouTube video")
    driver.get(url)
    # Checking if error message at the top of the web page
    if "Video unavailable" in driver.page_source:  # if the YouTube video is not available anymore
        number_of_unrecognized_urls += 1
        # Printing the error to the console
        print("\n\n⚠️", colored(
            "Issue with URL n°{0}".format(number_of_unrecognized_urls).strip(), 'red') + ":\n" + url + "\nThis YouTube video is not available anymore!")
        if textFileAsInput:
            # Adding this URL to the log text file
            write_in_log_text_file("\n\n⚠️ Issue with URL n°{0}:\n".format(number_of_unrecognized_urls) + url + "\nThis YouTube video is not available anymore!")

    else : # if the YouTube video still exists
        print(' ✅ YouTube video available')

        # 2) Counting the current number of non-hidden files in the DOWNLOAD_DIRECTORY folder
        print('2) Counting the current number of non-hidden files in the DOWNLOAD_DIRECTORY folder')
        numfiles = sum(1 for f in os.listdir(DOWNLOAD_DIRECTORY) if os.path.isfile(os.path.join(DOWNLOAD_DIRECTORY, f)) and f[0] != '.')  # cf.: https://arstechnica.com/civis/viewtopic.php?f=20&t=1111535

        # 3) Navigating to YTMP3_URL
        print("3) Navigating to YTMP3_URL")
        driver.get(YTMP3_URL)

        # 4) Entering the url under "Please insert a valid video URL"
        print('4) Entering the url under "Please insert a valid video URL"')
        python_field = driver.find_element_by_xpath("//*[@id='input']")
        python_field.send_keys(url)

        # 5) Clicking on "mp4"
        print('5) Clicking on "mp4"')
        python_button = driver.find_element_by_xpath("//*[@id='mp4']")
        python_button.click()

        # 6) Clicking on "Convert"
        print('6) Clicking on "Convert"')
        python_button = driver.find_element_by_xpath("//*[@id='submit']")
        python_button.click()

        # 7) Checking if the button "Download" is clickable and then clicking it
        # Downloading the YouTube video
        print('7) Checking if the "Download" button is clickable and then clicking it')
        number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY = len(glob.glob1(DOWNLOAD_DIRECTORY, "*.mp4"))
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='buttons']/a[1]"))).click()

        # 8) Moving on only once the video has been retrieved
        print('8) Moving on only once the video has been retrieved')
        check_crdownload = 1
        while check_crdownload:
            sleep(1)
            print(' still downloading from YTMP3_URL...')
            cont = 1
            new_numfiles = sum(1 for f in os.listdir(DOWNLOAD_DIRECTORY) if os.path.isfile(os.path.join(DOWNLOAD_DIRECTORY, f)) and f[0] != '.')
            for f in os.listdir(DOWNLOAD_DIRECTORY):
                if os.path.isfile(os.path.join(DOWNLOAD_DIRECTORY, f)) and f[0] != '.' and f.endswith('.crdownload'):
                    #print('Currently downloading YouTube video from ytmp3.cc ...')  # i.e. encountered ".crdownload" extension
                    tag = 0
                else:
                    tag = 1
                cont = cont * tag
            if cont == 1 and new_numfiles == numfiles + 1:
                check_crdownload = 0

        # 9) Eventually moving the dowloaded video if the DOWNLOAD_DIRECTORY is not '/Users/anthony/Downloads'
        if (DOWNLOAD_DIRECTORY != DEFAULT_DOWNLOAD_DIRECTORY):
            print("9) Moving the dowloaded video to the DOWNLOAD_DIRECTORY")
            list_of_files_in_Downloads_folder = glob.glob(DEFAULT_DOWNLOAD_DIRECTORY+'/*')
            src_file_path = max(list_of_files_in_Downloads_folder, key=os.path.getctime)
            dest_file_path = src_file_path.replace(DEFAULT_DOWNLOAD_DIRECTORY, DOWNLOAD_DIRECTORY)
            shutil.move(src_file_path, dest_file_path)
            final_step = '10'
        else:
            final_step = '9'

        # 10) Adding the current date in front of the lastly downloaded video name
        # and writing url to metadata "Comments" part of the downloaded file
        # Moving back to the first tab anyway (in case a new tab popped up on the right in the sequence of tabs of the web driver)
        driver.switch_to.window(driver.window_handles[0])
        print("{0}) Adding date and metadata".format(final_step))
        add_date_and_metadata(DOWNLOAD_DIRECTORY, url,
                              number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY,
                              number_of_videos_to_download=1)



## Instagram downloader
def instagram_downloader(number_of_unrecognized_urls, url, textFileAsInput, driver, project_path):

    # 1) Checking the availability of the Instagram post
    print("1) Checking the availability of the Instagram post")
    driver.get(url)

    if utils.config.firstTimeLoggedInInsta:
        # Clicking on "Accept" to accept cookies from Instagram on the web driver
        print(' Clicking on "Accept" to accept cookies from Instagram')
        try:
            python_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div/div[2]/button[1]')))
            python_button.click()
        except Exception as e:
            print(colored('Warning!\n', 'cyan'),
                  'Web element "Accept" button not found. Error message: ', e)

        # Clicking on "Log In"
        print(' Clicking on "Log In"')
        python_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div/div/div/div[3]/div[1]/a')))
        python_button.click()

        # Entering Entering personal Instagram credentials
        print(' Entering personal Instagram credentials')
        instagram_credentials_text_file = open(project_path + '/utils/instagram_credentials.txt')
        lines = instagram_credentials_text_file.readlines()
        username = lines[0].replace('\n', '')
        password = lines[1]
        username_field = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="loginForm"]/div/div[1]/div/label/input')))
        username_field.send_keys(username)
        password_field = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="loginForm"]/div/div[2]/div/label/input')))
        password_field.send_keys(password)

        # Clicking on the "Log In" button
        print(' Clicking on the "Log In" button')
        log_in_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="loginForm"]/div/div[3]/button/div')))
        log_in_button.click()

        # Clicking on the "Not Now" button
        print(' Clicking on the "Not Now" button')
        not_now_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/div/div/div/button')))
        not_now_button.click()

        # Clicking on the second "Not Now" button
        print(' Clicking on the second "Not Now" button')
        not_now_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,'/html/body/div[4]/div/div/div/div[3]/button[2]')))
        not_now_button.click()

        # Setting the utils.config.firstTimeLoggedInInsta to False
        utils.config.firstTimeLoggedInInsta = False

    # Checking if error message at the top of the web page
    print(' Checking if error message at the top of the web page')
    if "Sorry, this page isn't available." in driver.page_source: # if the Instagram post is not available anymore
        number_of_unrecognized_urls += 1
        # Printing the error to the console
        print("\n\n⚠️", colored("Issue with URL n°{0}".format(number_of_unrecognized_urls).strip(), 'red') + ":\n" + url + "\nThis Instagram post is not available anymore!")
        if textFileAsInput:
            # Adding this URL to the log text file
            write_in_log_text_file("\n\n⚠️ Issue with URL n°{0}:\n".format(number_of_unrecognized_urls) + url + "\nThis Instagram post is not available anymore!")

    else: # if the Instagram post still exists
        print(' ✅ Instagram post available')

        # 2) Navigating to SAVE_FROM_INSTA
        print("2) Navigating to SAVE_FROM_INSTA")
        driver.get(SAVE_FROM_INSTA)

        # 3) Entering the url under "Paste your video link here"
        print("3) Entering URL")
        python_field = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="sf_url"]')))
        python_field.send_keys(url)

        # 4) Clicking on the "Download" button
        print('4) Clicking on the "Download" button')
        python_button = driver.find_element_by_xpath('//*[@id="sf_submit"]')
        python_button.click()

        # 5) Waiting while downloading the video(s)
        print('5) Waiting while generating source link(s)')
        # (Waiting while no ".mp4" nor ".jpg" file is available)
        number_of_retrieved_files = 0
        breaking_while = False
        elapsed_sec = 0
        while number_of_retrieved_files < 1:
            list_of_available_links = driver.find_elements_by_tag_name("a")
            for i in range(len(list_of_available_links)):
                if (list_of_available_links[i].get_attribute('data-type') == 'mp4' or list_of_available_links[i].get_attribute('data-type') == 'jpg'):
                    number_of_retrieved_files = 1
                    print(' data-type "mp4" or "jpg" found!')
                    breaking_while = True
                    break
            if breaking_while:
                break
            sleep(1)
            elapsed_sec += 1
            print(' SAVE_FROM_INSTA still processing since {0}[s]...'.format(elapsed_sec))
            if elapsed_sec % 10 == 0: # while "SAVE_FROM_INSTA" has not been able to process the url during 10[s] intervals, re-click the "Download" button
                print(' re-Clicked on the "Download" button')
                python_button = driver.find_element_by_xpath('//*[@id="sf_submit"]')
                python_button.click()

        # 6) Getting the title of the (series of) video(s)
        print('6) Getting post title')
        divs = driver.find_elements_by_tag_name("div")
        title_short = 'instagram_video' + url[0:int(len(url) / 2)]
        for i in range(len(divs)):
            if divs[i].get_attribute('class') == 'row title':
                title_whole = divs[i].get_attribute('title')
                # Bounding the size of "title_whole"
                if len(title_whole) > 50:
                    title_short = title_whole[0:50]
                else:
                    title_short = title_whole
                print(' title_short:', title_short)
                break

        # 7) Getting all the links on the web page
        print("7) Getting all the links on the web page")
        list_of_available_mp4_links = []
        list_of_available_links = driver.find_elements_by_tag_name("a")
        for i in range(len(list_of_available_links)):
            # print(list_of_available_links[i].get_attribute('data-type'))
            # Filtering out all the links leading to ".mp4" files only
            if (list_of_available_links[i].get_attribute('data-type') == 'mp4'):
                list_of_available_mp4_links.append(list_of_available_links[i])
        number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY = len(glob.glob1(DOWNLOAD_DIRECTORY, "*.mp4"))
        number_of_videos_to_download = len(list_of_available_mp4_links)
        if number_of_videos_to_download > 0:
            # 8) Downloading the videos by getting the source link from each of the video tag
            print('8) Downloading video(s)')
            current_video_number = 0
            # Retrieving each video one after the other
            for i in range(len(list_of_available_mp4_links)):
                current_video_number += 1
                print(' downloading video {0}/{1}'.format(current_video_number, len(list_of_available_mp4_links)))
                # Retrieving the current video
                source_link = list_of_available_mp4_links[i].get_attribute("href")
                # print(source_link)
                req = Request(source_link, headers={'User-Agent': 'XYZ/3.0'})
                response = urlopen(req, timeout=20).read()
                file_name = DOWNLOAD_DIRECTORY + '/' + title_short + '_' + str(current_video_number) + '.mp4'
                f = open(file_name, 'wb')
                f.write(response)
                f.close()

            # 9) Adding the current date in front of the lastly downloaded video name
            # and writing url to metadata "Comments" part of the downloaded file
            print('9) Adding date and metadata')
            add_date_and_metadata(DOWNLOAD_DIRECTORY, url,
                                  number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY,
                                  number_of_videos_to_download)

        else: # In case the Instagram post does NOT contain any video
            number_of_unrecognized_urls += 1
            # Printing the error to the console
            print("\n\n⚠️", colored("Issue with URL n°{0}".format(number_of_unrecognized_urls).strip(), 'red') + ":\n" + url + "\nThis Instagram post does NOT contain any video!")
            if textFileAsInput:
                # Adding this URL to the log text file
                write_in_log_text_file("\n\n⚠️ Issue with URL n°{0}:\n".format(number_of_unrecognized_urls) + url + "\nThis Instagram post does NOT contain any video!")


    return number_of_unrecognized_urls



## Twitter downloader
def twitter_downloader(url):
    universal_downloader_you_get(url)



## Facebook downloader
def facebook_downloader_1(url, driver, project_path):

    try:
        try:
            universal_downloader_youtube_dl(url)

        # In case we get an error we use a web scraping method
        except Exception as e:
            print(colored('Warning!\n', 'cyan'), 'Current Facebook video could not be downloaded. Error message:\n', e)
            try:
                print('\nAlternative solution: using the website "saveas.co" to download this Facebook video...')
                facebook_downloader_2(url, driver)
            except:
                print('\nAlternative solution: using the website "getfvid.com" to download this Facebook video...')
                facebook_downloader_3(url, driver)

    # In case we get still an error with the two above methods
    # (This indicates that we might have a private video to download)
    # (Other info for downloading private Facebook video, cf.: "Reverse Engineering Facebook API: Private Video Downloader" (https://yasoob.me/2018/04/23/reverse-engineering-facebook-api-private-video-downloader/))
    except Exception as e:
        print(colored('Warning!\n', 'cyan'), 'Current Facebook video could not be downloaded. Error message:\n', e)
        print('\nAlternative solution: using the "Facebook private video download method" to download this Facebook video...')

        # 0) Eventually changing the url to a Facebook mobile url
        if ('https://www.' in url):
            url = url.replace('//www.','//m.')

        # 1) Navigating to the video URL itself
        print('1) Navigating to the video URL itself')
        driver.get(url)

        if utils.config.firstTimeFB1Alt:
            #---
            # 2) Clicking on "Accept All" (for accepting all cookies) (once it is present)
            print('2) Clicking on "Accept All"')
            try:
                python_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="accept-cookie-banner-label"]')))
                python_button.click()
            except Exception as e:
                print(colored('Warning!\n', 'cyan'), 'Web element "Accept All" button not found. Error message: ', e)

            # 3) Clicking on "Log in to Facebook"
            print('3) Clicking on "Log in to Facebook"')
            python_button = driver.find_element_by_xpath('//*[@id="root"]/div[1]/div/div/div[1]/div/a[1]/div')
            python_button.click()

            # 4) Entering personal Facebook credentials
            print('4) Entering personal Facebook credentials')
            facebook_credentials_text_file = open(project_path + '/utils/facebook_credentials.txt')
            lines = facebook_credentials_text_file.readlines()
            email_address = lines[0].replace('\n', '')
            password = lines[1]
            mobile_number_or_email_address_field = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="m_login_email"]')))
            mobile_number_or_email_address_field.send_keys(email_address)
            password_field = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="m_login_password"]')))
            password_field.send_keys(password)

            # 5) Optionally re-clicking on "Accept All" (for accepting all cookies) (once it is present)
            print('5) Optionally re-clicking on "Accept All"')
            try:
                python_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="accept-cookie-banner-label"]')))
                python_button.click()
            except Exception as e:
                print(colored('Warning!\n', 'cyan'), 'Web element "Accept All" button not found. Error message: ', e)

            # 6) Clicking on "Log In"
            print('6) Clicking on "Log In"')
            python_button = driver.find_element_by_xpath('//*[@id="u_0_4"]/button')
            python_button.click()

            # 7) Implicitly waiting a bit...
            print('7) Implicitly waiting a bit...')
            sleep(7) # works by waiting 5[s], but waiting 7[s] to be sure (web page loading speed depends on internet connection...)

            # 8) Reloading the url of interest
            print('8) Reloading the url of interest')
            driver.get(url)
            #---

            utils.config.firstTimeFB1Alt = False
            step_i = '9)'
            step_ii = '10)'
            step_iii = '11)'
            step_iv = '12)'

        else:
            step_i = '2)'
            step_ii = '3)'
            step_iii = '4)'
            step_iv = '5)'

        # 9) Clicking on the play button
        print('{0} Clicking on the play button'.format(step_i))
        python_button = driver.find_elements_by_class_name('_1o0y')[0]
        python_button.click()

        # 10) Extracting the video source link
        print('{0} Extracting the video source link'.format(step_ii))
        source_link = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'video'))).get_attribute("src")

        # 11) Retrieving video using urllib.request
        # (I.e. downloading the Facebook video)
        print('{0} Retrieving video using urllib.request'.format(step_iii))
        number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY = len(glob.glob1(DOWNLOAD_DIRECTORY, "*.mp4"))
        req = Request(source_link, headers={'User-Agent': 'XYZ/3.0'})
        response = urlopen(req, timeout=20).read()
        try:
            author_name_encoded = driver.find_element_by_xpath('/html/body/div[1]/div/div[4]/div/div[1]/div/div/div/div[1]/header/div[2]/div/div/div[1]/h3/span/strong/a')
        except:
            author_name_encoded = driver.find_element_by_xpath('//*[@id="mobile_injected_video_feed_pagelet"]/div/header/div[2]/div/div/div[1]/h3/span/strong/a')
        author_name = author_name_encoded.text
        try:
            publication_date_encoded = driver.find_element_by_xpath('/html/body/div[1]/div/div[4]/div/div[1]/div/div/div/div[1]/header/div[2]/div/div/div[1]/div/a/abbr')
        except:
            publication_date_encoded = driver.find_element_by_xpath('//*[@id="mobile_injected_video_feed_pagelet"]/div/header/div[2]/div/div/div[1]/div/a/abbr')
        publication_date = publication_date_encoded.text
        if ':' in publication_date:
            publication_date = publication_date.replace(":","h")
        if '/' in url[-10:]:
            end_of_url = url[-10:].replace('/','')
        else:
            end_of_url = url[-10:]
        video_name = author_name + ' - ' + publication_date + ' - ' + end_of_url
        file_name = DOWNLOAD_DIRECTORY + '/' + video_name + '.mp4'
        f = open(file_name, 'wb')
        f.write(response)
        f.close()

        # 12) Adding the current date in front of the lastly downloaded video name
        # and writing url to metadata "Comments" part of the downloaded file
        print('{0} Adding date and metadata'.format(step_iv))
        add_date_and_metadata(DOWNLOAD_DIRECTORY, url,
                              number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY,
                              number_of_videos_to_download=1)


def facebook_downloader_2(url, driver):

    # 1) Counting the current number of non-hidden files in the DOWNLOAD_DIRECTORY folder
    print('1) Counting the current number of non-hidden files in the DOWNLOAD_DIRECTORY folder')
    numfiles = sum(1 for f in os.listdir(DOWNLOAD_DIRECTORY) if os.path.isfile(os.path.join(DOWNLOAD_DIRECTORY, f)) and f[0] != '.')  # cf.: https://arstechnica.com/civis/viewtopic.php?f=20&t=1111535

    # 2) Navigating to SAVE_AS_URL
    print('2) Navigating to SAVE_AS_URL')
    driver.get(SAVE_AS_URL)

    # 3) Entering the url under "Please insert a valid video URL"
    print('3) Entering the url under "Please insert a valid video URL"')
    python_field = driver.find_element_by_xpath('//*[@id="form_download"]/div/input')
    python_field.send_keys(url)

    # 4) Clicking on "DOWNLOAD"
    print('4) Clicking on "DOWNLOAD"')
    python_button = driver.find_element_by_xpath('//*[@id="submit"]')
    python_button.click()

    # 5) Retrieving the clickable link from the "High Quality" button
    # (I.e. downloading the Facebook video)
    print('5) Retrieving the clickable link from the "High Quality" button')
    number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY = len(glob.glob1(DOWNLOAD_DIRECTORY, "*.mp4"))
    python_button = driver.find_element_by_xpath('/html/body/section/div/div/div/div[1]/div/div[5]/div/div/a[2]')
    video_link = python_button.get_attribute('href')
    driver.get(video_link)

    # 6) Moving on only once the video has been retrieved
    print('6) Moving on only once the video has been retrieved')
    check_crdownload = 1
    while check_crdownload:
        sleep(1)
        print(' still downloading from SAVE_AS_URL...')
        print()
        cont = 1
        new_numfiles = sum(1 for f in os.listdir(DOWNLOAD_DIRECTORY) if os.path.isfile(os.path.join(DOWNLOAD_DIRECTORY, f)) and f[0] != '.')
        for f in os.listdir(DOWNLOAD_DIRECTORY):
            if os.path.isfile(os.path.join(DOWNLOAD_DIRECTORY, f)) and f[0] != '.' and f.endswith('.crdownload'):
                # Currently downloading video...
                tag = 0
            else:
                tag = 1
            cont = cont * tag
        if cont == 1 and new_numfiles == numfiles + 1:
            check_crdownload = 0

    # 7) Eventually moving the dowloaded video if the DOWNLOAD_DIRECTORY is not '/Users/anthony/Downloads'
    if (DOWNLOAD_DIRECTORY != DEFAULT_DOWNLOAD_DIRECTORY):
        print("7) Moving the dowloaded video to the DOWNLOAD_DIRECTORY")
        list_of_files_in_Downloads_folder = glob.glob(DEFAULT_DOWNLOAD_DIRECTORY+'/*')
        src_file_path = max(list_of_files_in_Downloads_folder, key=os.path.getctime)
        dest_file_path = src_file_path.replace(DEFAULT_DOWNLOAD_DIRECTORY, DOWNLOAD_DIRECTORY)
        shutil.move(src_file_path, dest_file_path)
        final_step = '8'
    else:
        final_step = '7'

    # 8) Adding the current date in front of the lastly downloaded video name
    # and writing url to metadata "Comments" part of the downloaded file
    print("{0}) Adding date and metadata".format(final_step))
    add_date_and_metadata(DOWNLOAD_DIRECTORY, url,
                          number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY,
                          number_of_videos_to_download=1)


def facebook_downloader_3(url, driver):

    # 1) Navigating to GET_FVID_URL
    print('1) Navigating to GET_FVID_URL')
    driver.get(GET_FVID_URL)

    # 2) Entering the url under "Please insert a valid video URL"
    print('2) Entering the url under "Enter Facebook Video URL ..."')
    python_field = driver.find_element_by_xpath('//*[@id="form_download"]/div/input')
    python_field.send_keys(url)

    # 3) Clicking on "DOWNLOAD"
    print('3) Clicking on "DOWNLOAD"')
    python_button = driver.find_element_by_xpath('//*[@id="btn_submit"]')
    python_button.click()

    # 4) Retrieving the clickable link from the "Download in HD Quality" button
    # (I.e. downloading the Facebook video)
    print('4) Retrieving the clickable link from the "Download in HD Quality" button')
    python_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div[1]/div/div[2]/div/div[3]/p[1]/a')))
    video_link = python_button.get_attribute('href')
    driver.get(video_link)

    # 5) Retrieving video using urllib.request
    # (I.e. downloading the Facebook video)
    print('5) Retrieving video using urllib.request')
    number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY = len(glob.glob1(DOWNLOAD_DIRECTORY, "*.mp4"))
    req = Request(video_link, headers={'User-Agent': 'XYZ/3.0'})
    response = urlopen(req, timeout=20).read()
    video_name = url.replace('https://www.facebook.com/', '')
    video_name = video_name.replace("/", '') # removing the '/' from the video_name
    file_name = DOWNLOAD_DIRECTORY + '/' + video_name + '.mp4'
    f = open(file_name, 'wb')
    f.write(response)
    f.close()

    # 6) Adding the current date in front of the lastly downloaded video name
    # and writing url to metadata "Comments" part of the downloaded file
    print('6) Adding date and metadata')
    add_date_and_metadata(DOWNLOAD_DIRECTORY, url,
                          number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY,
                          number_of_videos_to_download=1)



## LinkedIn downloader
def linkedin_downloader(url, driver):

    # 1) Navigating to EXPERTS_PHP_INSTA
    print('1) Navigating to EXPERTS_PHP_INSTA')
    driver.get(EXPERTS_PHP_INSTA)

    # 2) Entering the url under "Please insert a valid video URL"
    print('2) Entering the url under "Please insert a valid video URL"')
    python_field = driver.find_element_by_xpath('//*[@id="login-form"]/div/input')
    python_field.send_keys(url)

    # 3) Clicking on "DOWNLOAD"
    print('3) Clicking on "DOWNLOAD"')
    # python_button = driver.find_element_by_xpath('//*[@id="login-form"]/div/span/button')
    # python_button.click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="login-form"]/div/span/button'))).click()

    # 4) Getting source link from video tag
    print('4) Getting source link from video tag')
    source_link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#showdata > div:nth-child(2) > div:nth-child(2) > video > source'))).get_attribute("src")
    # Alternative:
    # driver.implicitly_wait(5)
    # source_link = driver.find_element_by_tag_name('source').get_attribute("src")
    # source_link = driver.find_element_by_xpath('//*[@id="showdata"]/div[2]/div[2]/video/source').get_attribute("src")

    # 5) Retrieving video using urllib.request
    # (I.e. downloading the video)
    print('5) Retrieving video using urllib.request')
    video_name = url.replace('https://www.linkedin.com/posts/','')
    if video_name[-1] == "/": # removing the last character of the "video_name" if it is a "/"
        video_name = video_name[:-1]
    number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY = len(glob.glob1(DOWNLOAD_DIRECTORY, "*.mp4"))
    urllib.request.urlretrieve(source_link, DOWNLOAD_DIRECTORY+'/'+video_name+'.mp4') # downloading the LinkedIn video

    # 6) Adding the current date in front of the lastly downloaded video name
    # and writing url to metadata "Comments" part of the downloaded file
    print('6) Adding date and metadata')
    add_date_and_metadata(DOWNLOAD_DIRECTORY, url,
                          number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY,
                          number_of_videos_to_download=1)



## TikTok downloader
def tiktok_downloader(url, driver):

    # 1) Navigating to SNAP_TIK
    print('1) Navigating to SNAP_TIK')
    driver.get(SNAP_TIK)

    # 2) Entering the url under "Please insert a valid video URL"
    print('2) Entering the url under "Please insert a valid video URL"')
    python_field = driver.find_element_by_xpath('/html/body/div[1]/div/div/div/div/div/div/form/div/input')
    python_field.send_keys(url)

    # 3) Clicking on the "DOWNLOAD" button
    print('3) Clicking on the "DOWNLOAD" button')
    # python_button = driver.find_element_by_xpath('//*[@id="icondl"]')
    # python_button.click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="icondl"]'))).click()

    # 4) Getting source link from video tag
    print('4) Getting source link from video tag')
    source_link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#download-block > div > a:nth-child(1)'))).get_attribute("href")

    # 5) Retrieving video using urllib.request
    # (I.e. downloading the TikTok post)
    print('5) Retrieving video using urllib.request')
    number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY = len(glob.glob1(DOWNLOAD_DIRECTORY, "*.mp4"))
    req = Request(source_link, headers={'User-Agent': 'XYZ/3.0'})
    response = urlopen(req, timeout=20).read()
    author_name_encoded = driver.find_element_by_xpath('/html/body/div[2]/section/div/div/div/article/div[3]/h1/a')
    author_name = author_name_encoded.text
    full_description_encoded = driver.find_element_by_xpath('/html/body/div[2]/section/div/div/div/article/div[3]/p[1]/span')
    full_description = full_description_encoded.text
    # Bounding the size of "full_description"
    if len(full_description) > 50:
        full_description_short = full_description[0:50]
    else:
        full_description_short = full_description
    video_name = author_name + ' - ' + full_description_short
    file_name = DOWNLOAD_DIRECTORY + '/' + video_name + '.mp4'
    f = open(file_name, 'wb')
    f.write(response)
    f.close()

    # 6) Adding the current date in front of the lastly downloaded video name
    # and writing url to metadata "Comments" part of the downloaded file
    print('6) Adding date and metadata')
    add_date_and_metadata(DOWNLOAD_DIRECTORY, url,
                          number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY,
                          number_of_videos_to_download=1)



## Twitch downloader
def twitch_downloader(url):

    # 1) Adjusting the video URL
    print('1) Adjusting the video URL')
    if '?filter=highlights&sort=time' in url:
        url = url.replace('?filter=highlights&sort=time', '')

    # 2) Downloading video using youtube_dl
    print('2) Downloading video using youtube_dl')
    universal_downloader_youtube_dl(url)



## Vimeo downloader
def vimeo_downloader(url):
    universal_downloader_you_get(url)



## Dailymotion downloader
def dailymotion_downloader(url, driver):

    # 1) Navigating to SAVE_FROM_DAILYMOTION
    print("1) Navigating to SAVE_FROM_DAILYMOTION")
    driver.get(SAVE_FROM_DAILYMOTION)

    # 2) Entering the url under "Paste your video link here"
    print("2) Entering URL")
    python_field = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="sf_url"]')))
    python_field.send_keys(url)

    # 3) Clicking on the "Download" button
    print('3) Clicking on the "Download" button')
    python_button = driver.find_element_by_xpath('//*[@id="sf_submit"]')
    python_button.click()

    # 4) Waiting while downloading the video(s)
    print('4) Waiting while generating source link')
    # (Waiting until the final 'Download' button is visible)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="sf_result"]/div/div[1]/div[2]/div[2]/div[1]/a')))

    # 5) Getting the title of the video
    print('5) Getting video title')
    video_title_encoded = driver.find_element_by_xpath('//*[@id="sf_result"]/div/div[1]/div[2]/div[1]/div[1]')
    video_title = video_title_encoded.text
    # Bounding the size of "video_title"
    if len(video_title) > 50:
        video_title = video_title[0:50]
    else:
        video_title = video_title

    # 6) Extracting the video source link
    print('6) Extracting the video source link')
    # Getting all the links on the web page
    list_of_available_links = driver.find_elements_by_tag_name("a")
    for i in range(len(list_of_available_links)):
        #print(list_of_available_links[i].get_attribute('data-type'))
        # Filtering out all the links leading to ".mp4" files only
        if (list_of_available_links[i].get_attribute('data-type') == 'mp4'):
            source_link = list_of_available_links[i].get_attribute("href")
            break

    # 7) Downloading the video
    print('7) Downloading the video\n (This step might take some time depending on the length of the video, please be patient...)')
    number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY = len(glob.glob1(DOWNLOAD_DIRECTORY, "*.mp4"))
    if source_link[4] != 's': # eventually transforming the "http" into "https"
        source_link_modified = source_link[:4] + 's' + source_link[4:]
    req = Request(source_link_modified, headers={'User-Agent': 'XYZ/3.0'})
    response = urlopen(req, timeout=20).read()
    file_name = DOWNLOAD_DIRECTORY + '/' + video_title + '.mp4'
    f = open(file_name, 'wb')
    f.write(response)
    f.close()

    # 8) Adding the current date in front of the lastly downloaded video name
    # and writing url to metadata "Comments" part of the downloaded file
    print('8) Adding date and metadata')
    add_date_and_metadata(DOWNLOAD_DIRECTORY, url,
                          number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY,
                          number_of_videos_to_download=1)



## 20 Minuten downloader
def zwanzig_minuten_downloader(url, driver):

    # 1) Navigating to the url
    print('1) Navigating to the url')
    driver.get(url)
    # Optionally clicking on the little black cross in case the "Registrieren, up to date sein und Teil unserer Community werden" window pops up
    try:
        black_cross_button = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, '//*[@id="modal"]/div/div/div/div/div[1]/div[2]')))
        black_cross_button.click()
    except Exception as e:
        print(colored('Warning!\n', 'cyan'), 'Black cross web element button not found. The pop up window might not have shown up. Error message: ', e)

    # 2) Playing the video
    print('2) Playing the video')
    play_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/div/div/div/article/section[1]/figure/div')))
    play_button.click()
    sleep(2)

    # 3) Waiting until the end of the publicity
    print('3) Waiting until the end of the publicity')
    # Getting the start index of all the video tag currently present in the web page
    page_source = driver.page_source
    start_idx = [m.start() for m in re.finditer('<video ', page_source)]
    # Getting the content of all the video tag
    video_tags_content_list = []
    for i in range(len(start_idx)):
        j = start_idx[i] + len('<video ')
        current_video_tag_content = ''
        while(page_source[j] != '>'):
            current_video_tag_content += page_source[j]
            j += 1
        video_tags_content_list.append(current_video_tag_content)
    # Wait while the string "src="https://unityvideo.appuser.ch/video/" is NOT present in one of the video tags
    # (I.e. waiting as long as the advertisement is not over)
    while True:
        sleep(2)
        # Getting the content of all the video tags again...
        #---
        page_source = driver.page_source
        start_idx = [m.start() for m in re.finditer('<video ', page_source)]
        # Getting the content of all the video tag
        video_tags_content_list = []
        for i in range(len(start_idx)):
            j = start_idx[i] + len('<video ')
            current_video_tag_content = ''
            while (page_source[j] != '>'):
                current_video_tag_content += page_source[j]
                j += 1
            video_tags_content_list.append(current_video_tag_content)
        #---
        if any('src="https://unityvideo.appuser.ch/video/' in video_tag_content for video_tag_content in video_tags_content_list):
            break
    print(' ✅ Publicity over!')

    # 4) Getting the src attribute of the video tag
    print('4) Getting the src attribute of the video tag')
    # 4.1) Retrieving the page source
    print(' 4.1) Retrieving the page source')
    page_source = driver.page_source
    # 4.2) Locating the beginning of the string 'src="https://unityvideo.appuser.ch/video/' in the page source
    print(' 4.2) Locating the beginning of the string src="https://unityvideo.appuser.ch/video/ in the page source')
    start_idx = page_source.find('src="https://unityvideo.appuser.ch/video/') + len('src="')
    # 4.3) Extracting the src attribute of the video tag
    print(' 4.3) Extracting the src attribute of the video tag')
    end_idx = start_idx
    while True:
        char = page_source[end_idx]
        if char == '"':
            break
        else:
            end_idx += 1
    source_link = page_source[start_idx:end_idx]
    print('  retrieved source_link:', source_link)

    # 5) Retrieving video using urllib.request
    # (I.e. downloading the 20 Minuten video)
    print('5) Retrieving video using urllib.request')
    number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY = len(glob.glob1(DOWNLOAD_DIRECTORY, "*.mp4"))
    req = Request(source_link, headers={'User-Agent': 'XYZ/3.0'})
    response = urlopen(req, timeout=20).read()
    #---
    # Creating a translation dictionary based on the reserved characters list
    reserved_characters_list = ['/', "\\", '?', '%', '*', ':', '|', '"', '<', '>', '.', ',', ';', '=', '#', '&', '{', '}', '`', '\n']
    translation_dict = {}
    for i in range(len(reserved_characters_list)):
        if reserved_characters_list[i] == '\n':
            translation_dict[reserved_characters_list[i]] = ' - '
        else:
            translation_dict[reserved_characters_list[i]] = ''
    # Retrieving the title from the web page
    title_encoded = driver.find_element_by_xpath('//*[@id="__next"]/div/div/div/div/article/section[2]/header/h1')
    title = title_encoded.text
    # Mapping the dicrtionary onto the title to remove the unwanted characters
    video_name = title.translate(str.maketrans(translation_dict))
    file_name = DOWNLOAD_DIRECTORY + '/' + video_name + '.mp4'
    #---
    f = open(file_name, 'wb')
    f.write(response)
    f.close()

    # 6) Adding the current date in front of the lastly downloaded video name
    # and writing url to metadata "Comments" part of the downloaded file
    print('6) Adding date and metadata')
    add_date_and_metadata(DOWNLOAD_DIRECTORY, url,
                          number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY,
                          number_of_videos_to_download=1)



## Pinterest downloader
def pinterest_downloader(url, driver):

    # 1) Getting video title
    print('1) Getting video title')
    # Creating a translation dictionary based on the reserved characters list
    reserved_characters_list = ['/', "\\", '?', '%', '*', ':', '|', '"', '<', '>', '.', ',', ';', '=', '#', '&', '{', '}', '`', '\n']
    translation_dict = {}
    for i in range(len(reserved_characters_list)):
        if reserved_characters_list[i] == '\n':
            translation_dict[reserved_characters_list[i]] = ' - '
        else:
            translation_dict[reserved_characters_list[i]] = ''
    driver.get(url)
    video_title_encoded = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="desktopWrapper"]/div[2]/div/div/div[2]/div[1]/div[2]/div[2]/div[2]/div/div[2]/div/h1')))
    video_title = video_title_encoded.text
    video_title_translated = video_title.translate(str.maketrans(translation_dict))
    print(' Video title: "{0}"'.format(video_title_translated))

    # 2) Navigating to EXPERTS_PHP_PINT
    print('2) Navigating to EXPERTS_PHP_PINT')
    driver.get(EXPERTS_PHP_PINT)

    # 3) Entering the url
    print('3) Entering the url')
    python_field = driver.find_element_by_xpath('//*[@id="login-form"]/div/input')
    python_field.send_keys(url)

    # 4) Clicking on "DOWNLOAD"
    print('4) Clicking on "DOWNLOAD"')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="login-form"]/div/span/button'))).click()

    # 5) Getting source link from video tag
    print('5) Getting source link from video tag')
    source_link = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH,'//*[@id="showdata"]/div[5]/table/tbody/tr[1]/td[1]/a'))).get_attribute("href")

    # 6) Retrieving video using urllib.request
    # (I.e. downloading the Pinterest post)
    print('6) Retrieving video using urllib.request')
    number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY = len(glob.glob1(DOWNLOAD_DIRECTORY, "*.mp4"))
    req = Request(source_link, headers={'User-Agent': 'XYZ/3.0'})
    response = urlopen(req, timeout=20).read()
    file_name = DOWNLOAD_DIRECTORY + '/' + video_title_translated + '.mp4'
    f = open(file_name, 'wb')
    f.write(response)
    f.close()

    # 7) Adding the current date in front of the lastly downloaded video name
    # and writing url to metadata "Comments" part of the downloaded file
    print('7) Adding date and metadata')
    add_date_and_metadata(DOWNLOAD_DIRECTORY, url,
                          number_of_mp4_files_already_in_DOWNLOAD_DIRECTORY,
                          number_of_videos_to_download=1)