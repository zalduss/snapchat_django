# Imports
import json
import time
import random

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

# Modules
from scrape.driver import chrome_webdriver


# Django Imports
from django.db import IntegrityError

# Models
from download.models import Channel, VideoDetail


def scrape():
    driver = chrome_webdriver()
    # Fail-Ed Channel
    driver.get('https://www.snapchat.com/p/71ef7cb0-60b5-4930-b2de-3bc88fac5c7f')
    driver.implicitly_wait(10)
    
    # Load all video
    scroll_to_bottom(driver)
    
    extract_videos(driver.page_source)
 

def scroll_to_bottom(driver):
    time.sleep(random.randint(3, 5))
    curr_video_count = 0
    
    while True:
        
        videos = driver.find_elements(By.CLASS_NAME, "StoryListTile_container__Ttl7x")
        total_video_count = len(videos)
        
        if videos:
            # Execute script to scroll the last video into view
            driver.execute_script("arguments[0].scrollIntoView(true);", videos[-1])
            print("Scrolled to the last video in the list.")
            
            time.sleep(random.randint(5, 10))
            
            if curr_video_count == total_video_count:
                print("Current video and Total video count are the same. Breaking...")
                break
            
            curr_video_count = total_video_count;
            
        else:
            print("No videos found in the container.")
        
    time.sleep(random.randint(10, 15))


def extract_videos(html_content):
    
    # Get first loaded videos from json
    extract_json_videos(html_content)
    
    # Get rest of Channels videos
    
    
    
    
def extract_json_videos(html_content):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
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

    
    add_channel(channel_name, channel_id)

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

        video_details = (story_id, story_title, story_link, season_number, episode_number)
        
        add_video(channel_id, video_details)
        
        return stories

    # Create the output data structure

    

    return stories


def add_channel(channel_name, channel_id):
    print('Adding channel...')
    
    # Check if the channel already exists directly within this function
    if Channel.objects.filter(channel_id=channel_id).exists():
        print("Channel already exists. Skipping save.")
        return 
    
    try:
        channel = Channel(name=channel_name, channel_id=channel_id)
        channel.save()
        print("Channel successfully added to the database.") 

    except IntegrityError as e:
        print(f"Failed to add channel: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
   
def add_video(channel_id, video_details):
    story_id, story_title, story_link, season_number, episode_number = video_details
    
    channel = get_channel(channel_id)
    
    # Check if the video already exists
    if VideoDetail.objects.filter(video_id=story_id, channel=channel).exists():
        print("Video already exists. Skipping.")
        return
    
    try:
        video = VideoDetail(
            video_id=story_id,
            video_name=story_title,
            channel=channel,
            season=season_number,
            episode=episode_number,
            link=story_link
        )
        video.save()
        print("Video successfully added to the database.") 

    except IntegrityError as e:
        print(f"Failed to add video: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def get_channel(channel_id):
    # Retrieve the channel instance
    try:
        channel = Channel.objects.get(channel_id=channel_id)
        return channel
    except Channel.DoesNotExist:
        print("Channel does not exist. Cannot add video.")
        return
