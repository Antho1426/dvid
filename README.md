# dvid.py
Python program that automatically downloads a single video from a URL saved in
the clipboard or a list of videos from various URLs saved in a text file.

## Table of contents
* [1. Description](#1-description)
* [2. Getting started](#2-getting-started)
    * [2.1 Dependencies](#21-dependencies)
    * [2.2 Installing](#22-installing)
    * [2.3 Executing program](#23-executing-program)
* [3. Version history](#3-version-history)

<!-- toc -->

## 1. Description
`dvid.py` is a Python program that allows to download videos from various URLs.
The software currently supports videos hosted on following platforms:
- YouTube
- Instagram
- Twitter
- Facebook
- LinkedIn
- TikTok
- Twitch
- Vimeo
- Dailymotion
- 20 Minuten
- Pinterest

In case a video doesn't come from one of the above-mentioned websites, the
program still tries to download it using a default method based on the
`youtube_dl` Python package.

\
Important points to notice:
- Regarding Instagram posts, the program only downloads ".mp4" files. It does
  NOT download ".jpg" files (i.e. pictures and thumbnails).
- Verifying the availability of Instagram posts requires Instagram account
  credentials. These can be automatically retrieved in the `instagram_downloader`
  function by creating an `instagram_credentials.txt` file in the `utils` folder
  with your `username` and `password` on respectively the first and second line.
- Downloading private Facebook videos requires Facebook account credentials.
  These can be automatically retrieved in the `facebook_downloader_1`
  function by creating a `facebook_credentials.txt` file in the `utils` folder
  with your `email_address` and `password` on respectively the first and second
  line.
- The current date is added at the beginning of the name of each video.
- The corresponding URL of each video is copied to the "Comments" section of the
  video file meta information.


## 2. Getting started

### 2.1 Dependencies
* Tested on macOS Big Sur version 11.0.1
* Python 3.7

### 2.2 Installing
`pip install -r requirements.txt`

### 2.3 Executing program
- To access useful help messages, type following Terminal command at the
  root of the project:
  
  `python3.7 dvid.py -h`


- To download a single video from a URL saved in the clipboard, issue following
  command at the root of the project:
  
  `python3.7 dvid.py`

  The program will automatically get the clipboard stored
  URL and download its attached video.
  

- To download videos from a list of various URLs, create a text file containing
  all the URLs you are interested in. Make sure each URL is separated by a line
  break, get the path of the text file and issue following command at the root 
  of the project:
  
  `python3.7 dvid.py --textFilePath /path/to/your/text/file/my_text_file.txt`

  The program will automatically scroll through the list of URLs. For each URL,
  it will determine the source platform and retrieve the video using a
  dedicated method.

## 3. Version history
* 0.1
    * Initial release