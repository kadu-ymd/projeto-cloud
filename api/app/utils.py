import requests
from os import getenv
from dotenv import load_dotenv
from fastapi import HTTPException, status

def get_videos(api_key: str, api_url: str, n: int = 5):
    video_info: dict
    
    params = {
        "part": "snippet,contentDetails,statistics", 
        "chart": "mostPopular", # ver por vídeos de jogos, que atualizam mais constantemente
        "regionCode": "BR", 
        "maxResults": n, 
        "key": api_key
    }

    print(api_key, api_url)
    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        data = response.json()

        for video in data['items']:
            print(f"Título: {type(video['snippet']['title'])}")
            print(f"ID do vídeo: {type(video['id'])}")
            print(f"Descrição: {type(video['snippet']['description'])}")
            print(f"Visualizações: {type(video['statistics']['viewCount'])}")
            print("-----------")

            video_info = {
                "title": video['snippet']['title'],
                "video_id": video['id'],
                "description": video['snippet']['description'],
                "n_views": video['statistics']['viewCount']
            }
        return video_info
    else:
        return None