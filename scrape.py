from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

import time
import json
import os
import random

from bs4 import BeautifulSoup


"""
1. Extract Preview video list of channel. This includes all the video that load at first and are in the json scrape portion of the .html
2. We are going to extract the videos id, title, season number, episode number
3. Extract all other videos on channel  
    - Scroll to bottom to get all videos loaded from that particular season. 
    - Going to take the videos that were extracted from preview and compare the season and episode number to the remaining videos
    - if season and episode number match skip, otherwise click on video and extract all info from that video
    - repeat until there are no more videos for that season
4. Check if there are more in a different season if so
    - 
"""


def main():
    # driver = chrome_webdriver()
    # driver.get("https://www.snapchat.com/p/71ef7cb0-60b5-4930-b2de-3bc88fac5c7f/2525901834393600")
    # driver.get("https://www.recapafteruse.co.uk/")
    # driver.implicitly_wait(10);
    
    #* 1. Scroll down and load all videos    
    # scroll_to_bottom(driver)
    
    # data = driver.page_source
    #* 2. Extract Preview videos from json 
    with open('content.html', 'r', encoding='utf-8') as f:
        data = f.read()
    videos_list = extract_video_list(data)
    
    
    #* 3. Iterate through video elements and compare if they already exist in videos list
    extract_channel_videos(data, videos_list)
    
    # with open("content.html", 'w', encoding='utf-8') as f:
        # f.write(driver.page_source)

    # with open("content.html", 'r', encoding='utf-8') as f:
        # data = f.read()

        # extract_video_list(data)

        
    # time.sleep(30)


# Chrome Driver web configurations
def chrome_webdriver():
    """Return a Chrome WebDriver object."""

    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    return driver


def scroll_to_bottom(driver):
    time.sleep(5)
    old_num_of_videos = 0
    while True:
        
        videos = driver.find_elements(By.CLASS_NAME, "StoryListTile_container__Ttl7x")
        new_num_of_videos = len(videos)
        
        if videos:
            # Execute script to scroll the last video into view
            driver.execute_script("arguments[0].scrollIntoView(true);", videos[-1])
            print("Scrolled to the last video in the list.")
            
            time.sleep(random.randint(5, 10))
            
            if old_num_of_videos == new_num_of_videos:
                break
            old_num_of_videos = new_num_of_videos;
        else:
            print("No videos found in the container.")
        
    print("outside")
    time.sleep(random.randint(10, 15))
   
    
def extract_video_list(data):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(data, 'html.parser')
    
    # Find the script element with id="__NEXT_DATA__"
    script_element = soup.find('script', id='__NEXT_DATA__')
    
    # Extract the JSON content from the script element
    json_data = script_element.string
    
    # Convert the JSON string to a Python dictionary
    data_dict = json.loads(json_data)
    
    # Extract Channel ID
    channel_id = data_dict.get('props', {}).get('pageProps', {}).get('pageLinks', []).get('snapchatCanonicalUrl', "").split("/")[-1]
    # Extract the Snapchat story array from the JSON data
    story_list = data_dict.get('props', {}).get('pageProps', {}).get('premiumStoryList', [])
    # Extract the title from "publicProfileInfo"
    channel_name = data_dict.get('props', {}).get('pageProps', {}).get('publicProfileInfo', {}).get('title', 'Unknown').strip()


    stories = []
    video_links = []
    for story in story_list:
        story.get('playerStory', {})
        story_id = story.get('playerStory', {}).get('storyId', {}).get('value', 'Unknown') # Video ID
        story_link = "https://www.snapchat.com/p/" + channel_id + "/" + story_id # Video Link
        story_title = story.get('playerStory', {}).get('storyTitle', {}).get('value', 'Unknown') # Video Name
        season_number = story['seasonNumber']
        episode_number = story['episodeNumber']

        stories.append({"VideoID": story_id, "VideoName": story_title, "VideoLink": story_link, "SeasonNumber": season_number, "Episode": episode_number})
        video_links.append(story_link)


    # Create the output data structure
    output_data = {
        "ChannelName": channel_name,
        "ChannelID": channel_id,
        "ChannelLink": "https://www.snapchat.com/p/" + channel_id,
        "Stories": stories
    }

    # Pretty-print the extracted data and write it to the output file
    output_file = channel_name + ".json"
    # output_path = os.path.join("content", output_file)
    # with open(output_file, 'w', encoding='utf-8') as file:
        # json.dump(output_data, file, indent=4, ensure_ascii=False)
    
    # print(f"Channels videos list has been extracted and saved to {output_file}")

    return stories
 
   
def extract_channel_videos(data, existing_videos):
    # with open('data.html', 'w', encoding='utf-8') as f:
        # f.write(data)
        
    with open('data.html', 'r', encoding='utf-8') as f:
        data = f.read()
    
    soup = BeautifulSoup(data, 'html.parser')
    
        
    video_elements = soup.select("div.StoryListTile_container__Ttl7x")

    for video in video_elements:
        video_title = video.select_one('span.StoryListTile_title__H3HQ6.StoryListTile_oneLineTruncation__sYZDD').text.strip()
        video_info_parent = video.select_one('div.StoryListTile_storyInfo__i9rqy.StoryListTile_oneLineTruncation__sYZDD')
        

        if video_info_parent:
            season_episode_info = video_info_parent.find_all('span')[1].text.strip()  # The second span contains the series and episode info
            # Split the text to extract numbers
            parts = season_episode_info.split(',')
            season_part = parts[0].strip()  # e.g., 'Series 3'
            episode_part = parts[1].strip()  # e.g., 'Episode 1'
            
            # Extract numerical values
            season_number = int(season_part.split(' ')[1])
            episode_number = int(episode_part.split(' ')[1])
            
            if not any(video['SeasonNumber'] == season_number and video['Episode'] == episode_number for video in existing_videos):
                new_video = {
                    'VideoName': video_title,
                    'SeasonNumber': season_number, 
                    'Episode': episode_number
                }
                
                existing_videos.append(new_video)
    
    new_list = json.dumps(existing_videos, indent=4)
    with open('new_list.json', 'w') as f:
        f.write(new_list)

        
    
    
         # print(True)
        
        
    # if not any(video['SeasonNumber'] == season_number and video['Episode'] == episode_number for video in existing_videos):
        # print(True)
    
    


    
    


if __name__ == "__main__":
    main()

