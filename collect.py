import os
import csv
from datetime import datetime
from googleapiclient.discovery import build

API_KEY = os.environ.get("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=API_KEY)

# 수집 기준 메인 키워드 목록
BASE_KEYWORDS = ["장원영 추천템", "안유진 추천템", "카리나 추천템", "다이소 꿀템", "올리브영 추천"]

def get_expanded_keywords(base_keywords):
    """메인 키워드를 바탕으로 연관 쇼츠 검색어 확장"""
    expanded = set(base_keywords)
    for kw in base_keywords:
        try:
            # YouTube Search API로 연관 쇼츠 검색어 수집
            request = youtube.search().list(
                q=kw,
                part="snippet",
                type="video",
                videoDuration="short",
                maxResults=3
            )
            response = request.execute()
            for item in response.get("items", []):
                title = item["snippet"]["title"]
                # 제목에서 핵심 단어를 추출하여 연관 키워드로 간이 지정
                words = [w for w in title.split() if len(w) > 1]
                if words:
                    expanded.add(words[0])
        except Exception:
            pass
    return list(expanded)

def collect_shorts():
    filename = "shorts_history.csv"
    file_exists = os.path.isfile(filename)
    
    # 키워드 자동 확장 적용
    target_keywords = get_expanded_keywords(BASE_KEYWORDS)
    
    with open(filename, mode="a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "keyword", "video_id", "title", "channel_title", "view_count", "duration_sec"])

        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        for kw in target_keywords:
            try:
                # 쇼츠 검색 API 호출 (키워드당 상위 10개)
                search_res = youtube.search().list(
                    q=kw,
                    part="id,snippet",
                    type="video",
                    videoDuration="short",
                    maxResults=10
                ).execute()

                video_ids = [item["id"]["videoId"] for item in search_res.get("items", [])]

                if not video_ids:
                    continue

                # 상세 정보 (조회수, 재생시간) 가져오기
                videos_res = youtube.videos().list(
                    part="snippet,statistics,contentDetails",
                    id=",".join(video_ids)
                ).execute()

                for item in videos_res.get("items", []):
                    v_id = item["id"]
                    title = item["snippet"]["title"]
                    channel = item["snippet"]["channelTitle"]
                    views = int(item["statistics"].get("viewCount", 0))
                    
                    writer.writerow([now_str, kw, v_id, title, channel, views, 60])
            except Exception as e:
                print(f"Error collecting for keyword {kw}: {e}")

if __name__ == "__main__":
    collect_shorts()
