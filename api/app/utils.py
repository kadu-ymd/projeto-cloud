import requests

def get_videos(api_key: str, api_url: str, n: int = 1):
    video_info: dict = {
        "title": None,
        "video_id": None,
        "description": None,
        "n_views": None
    }  
    
    params = {
        "part": "snippet,contentDetails,statistics", 
        "chart": "mostPopular",
        "regionCode": "BR", 
        "maxResults": n, 
        "key": api_key
    }

    print(api_key, api_url)
    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        data = response.json()

        for video in data['items']:

            video_info = {
                "title": video['snippet']['title'],
                "video_id": (video['id']),
                "description": video['snippet']['description'],
                "n_views": (video['statistics']['viewCount'])
            }
        return video_info
    else:
        return video_info
    
