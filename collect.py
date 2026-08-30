import os
import csv
from datetime import datetime
import isodate
from googleapiclient.discovery import build

# GitHub Secrets에서 API 키 로드
API_KEY = os.environ.get("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=API_KEY)

KEYWORDS = ["장원영 추천템", "안유진 추천템", "카리나 추천템"]
filename = "shorts_history.csv"

# 헤더 확인 및 생성
file_exists = os.path.exists(filename)
if not file_exists:
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "keyword", "video_id", "title", "channel_title", "view_count", "duration_sec"])

now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

for kw in KEYWORDS:
    search_res = youtube.search().list(
        q=kw, part="snippet", type="video", maxResults=5, regionCode="KR"
    ).execute()
    
    video_ids = [item["id"]["videoId"] for item in search_res.get("items", []) if "videoId" in item.get("id", {})]

    if video_ids:
        videos_res = youtube.videos().list(
            part="contentDetails,statistics,snippet",
            id=",".join(video_ids)
        ).execute()
        
        with open(filename, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            for video in videos_res.get("items", []):
                duration_sec = isodate.parse_duration(video["contentDetails"]["duration"]).total_seconds()
                if duration_sec <= 60:
                    writer.writerow([
                        now_str,
                        kw,
                        video["id"],
                        video["snippet"]["title"],
                        video["snippet"]["channelTitle"],
                        int(video["statistics"].get("viewCount", 0)),
                        int(duration_sec)
                    ])

print(f"✅ 수집 완료: {now_str}")
