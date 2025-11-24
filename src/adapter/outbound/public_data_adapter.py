import os
import math
import requests
from typing import List
from application.port.outbound.event_port import EventPort
from domain.model.recommend_model import Festival

DATA_API_KEY = os.getenv("DATA_API_KEY")

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * (2 * math.asin(math.sqrt(a)))

class PublicDataAdapter(EventPort):

    def get_festivals(self, category: str, lat: float, lon: float) -> List[Festival]:
        url = "http://apis.data.go.kr/B551011/KorService2/searchKeyword2"
        params = {
            "serviceKey": DATA_API_KEY,
            "MobileOS": "ETC",
            "MobileApp": "festivalApp",
            "_type": "json",
            "numOfRows": 50,
            "pageNo": 1,
            "arrange": "C",
            "keyword": category,
        }

        res = requests.get(url, params=params)
        try:
            data = res.json()
        except Exception:
            return []

        festivals = []
        items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        for item in items:
            try:
                fest_lat = float(item.get("mapy", 0))
                fest_lon = float(item.get("mapx", 0))
                distance = haversine(lat, lon, fest_lat, fest_lon)
                if distance <= 50:
                    festivals.append(
                        Festival(
                            title=item.get("title", ""),
                            address=item.get("addr1", ""),
                            lat=fest_lat,
                            lon=fest_lon,
                            distance_km=round(distance, 2),
                            first_image=item.get("firstimage", ""),
                            tel=item.get("tel", ""),
                        )
                    )
            except Exception:
                continue

        festivals.sort(key=lambda x: x.distance_km)

        return festivals
