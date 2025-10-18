
# Fetch YouTube channel video metadata using the YouTube Data API
import requests
import json
import os

# Set these values
API_KEY = os.getenv("YOUTUBE_API_KEY")
if not API_KEY:
    raise EnvironmentError("ERROR: YOUTUBE_API_KEY environment variable is not set. Set it and retry.")
CHANNEL_HANDLE_OR_ID = "@ColgateColombia"  # Can be a handle (e.g. @ColgateColombia) or channel ID (UC...)
OUTPUT_FILE = "scraping/extrac/youtube_channel_videos.json"
MAX_RESULTS = 50  # Max per API call (can paginate for more)

def fetch_youtube_videos(api_key, channel_id, max_results=50):
    base_url = "https://www.googleapis.com/youtube/v3/search"
    video_ids = []
    next_page_token = None
    while True:
        params = {
            "key": api_key,
            "channelId": channel_id,
            "part": "snippet",
            "order": "date",
            "maxResults": max_results,
            "type": "video"
        }
        if next_page_token:
            params["pageToken"] = next_page_token
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        for item in data.get("items", []):
            video_ids.append(item["id"]["videoId"])
        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    # Now fetch full details for all video IDs in batches of 50
    videos = []
    details_url = "https://www.googleapis.com/youtube/v3/videos"
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i:i+50]
        params = {
            "key": api_key,
            "id": ",".join(batch_ids),
            "part": "snippet"
        }
        response = requests.get(details_url, params=params)
        response.raise_for_status()
        data = response.json()
        for item in data.get("items", []):
            snippet = item["snippet"]
            videos.append({
                "videoId": item["id"],
                "title": snippet["title"],
                "description": snippet["description"],
                "publishedAt": snippet["publishedAt"],
                "url": f"https://www.youtube.com/watch?v={item['id']}"
            })
    return videos

def resolve_channel_id(api_key, handle_or_id):
    # If it looks like a channel ID, return as is
    if handle_or_id.startswith("UC") and len(handle_or_id) > 20:
        return handle_or_id
    # Remove @ if present
    handle = handle_or_id.lstrip("@")
    # Use search endpoint to find channel ID
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": api_key,
        "q": handle,
        "type": "channel",
        "part": "snippet",
        "maxResults": 1
    }
    response = requests.get(search_url, params=params)
    response.raise_for_status()
    data = response.json()
    items = data.get("items", [])
    if not items:
        raise ValueError(f"No channel found for handle: {handle_or_id}")
    channel_id = items[0]["id"]["channelId"]
    print(f"Resolved handle '{handle_or_id}' to channel ID: {channel_id}")
    return channel_id

def main():
    api_key = API_KEY
    channel_id = resolve_channel_id(api_key, CHANNEL_HANDLE_OR_ID)
    output_file = OUTPUT_FILE
    videos = fetch_youtube_videos(api_key, channel_id, MAX_RESULTS)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(videos)} videos to {output_file}")
    if len(videos) == 0:
        print("No videos found. Debugging raw API response...")
        # Make a single API call and print the raw response for inspection
        base_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "key": api_key,
            "channelId": channel_id,
            "part": "snippet",
            "order": "date",
            "maxResults": MAX_RESULTS,
            "type": "video"
        }
        response = requests.get(base_url, params=params)
        print("Raw API response:")
        print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    main()