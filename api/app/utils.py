import requests
import jwt
from hashlib import sha256

def get_videos(api_key: str, api_url: str, n: int = 1) -> dict[str, str | None]:
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
    
def hash_password(password: str) -> str:
    return sha256(password.encode("utf-8")).hexdigest()

def jwt_encode(payload: dict, secret_key: str, ha: str) -> str:
    return jwt.encode(payload, secret_key, ha)

def jwt_decode(jwt_token: str, secret_key: str, ha: str) -> dict:
    return jwt.decode(jwt_token, secret_key, ha)

def verify_token(jwt_token: str, secret_key: str, ha: str) -> bool:
    is_valid: bool = False
    
    try:
        payload = jwt_decode(jwt_token, secret_key, ha)
    except:
        payload = None

    if payload:
        is_valid = True

    return is_valid