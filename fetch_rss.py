import feedparser
import requests
import json
import csv
import os
from datetime import datetime

# RSS ve JSON kaynakları
SOURCES = {
    # Reddit - Tartışma odaklı
    "reddit_ask": "https://www.reddit.com/r/AskReddit/hot.json?limit=50",
    "reddit_unpopular": "https://www.reddit.com/r/unpopularopinion/hot.json?limit=50",
    "reddit_wouldyourather": "https://www.reddit.com/r/WouldYouRather/hot.json?limit=50",
    "reddit_polls": "https://www.reddit.com/r/polls/hot.json?limit=50",
    "reddit_funny": "https://www.reddit.com/r/funny/hot.json?limit=50",
    "reddit_movies": "https://www.reddit.com/r/movies/hot.json?limit=50",
    "reddit_gaming": "https://www.reddit.com/r/gaming/hot.json?limit=50",
    "reddit_technology": "https://www.reddit.com/r/technology/hot.json?limit=50",
    "reddit_food": "https://www.reddit.com/r/food/hot.json?limit=50",
    "reddit_sports": "https://www.reddit.com/r/sports/hot.json?limit=50",
    "reddit_music": "https://www.reddit.com/r/Music/hot.json?limit=50",
    "reddit_tv": "https://www.reddit.com/r/television/hot.json?limit=50",
    
    # Pop Kültürü & Eğlence
    "buzzfeed_ent": "https://www.buzzfeed.com/entertainment.xml",
    "vulture": "https://www.vulture.com/rss/all.xml",
    "theringer": "https://www.theringer.com/rss/pop-culture/index.xml",
    "eonline": "https://www.eonline.com/rss/feed/index.xml",
    "mentalfloss": "https://www.mentalfloss.com/rss.xml",
    "boredpanda": "https://www.boredpanda.com/feed/",
    "upworthy": "https://www.upworthy.com/rss",
    
    # Oyun
    "polygon": "https://www.polygon.com/rss/index.xml",
    "kotaku": "https://kotaku.com/rss",
    "ign": "https://www.ign.com/rss/articles.xml",
    
    # Teknoloji
    "theverge": "https://www.theverge.com/rss/index.xml",
    "producthunt": "https://www.producthunt.com/feed",
    "mashable": "https://mashable.com/feeds/rss/all",
    
    # Google News
    "google_ent_tr": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtVnVHZ0pWVXlnQVAB?hl=tr&gl=TR&ceid=TR%3Atr",
    "google_art_tr": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FtVnVHZ0pWVXlnQVAB?hl=tr&gl=TR&ceid=TR%3Atr",
    "google_sport_tr": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pWVXlnQVAB?hl=tr&gl=TR&ceid=TR%3Atr",
    "google_ent_us": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en",
    "google_art_us": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en",
    
    # Global Haber & Magazin
    "cnn_ent": "https://www.cnn.com/entertainment/rss.xml",
    "bbc_ent": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
    "variety": "https://variety.com/feed/",
    "hollywoodreporter": "https://www.hollywoodreporter.com/feed/",
    "rollingstone": "https://www.rollingstone.com/feed/",
    "billboard": "https://www.billboard.com/feed/",
    "pitchfork": "https://pitchfork.com/rss/news",
    "tmz": "https://www.tmz.com/rss.xml",
    "people": "https://people.com/feed/",
    "usmagazine": "https://www.usmagazine.com/feed/",
    "ew": "https://ew.com/feed/",
    "tvguide": "https://www.tvguide.com/rss/news.xml",
    "collider": "https://collider.com/feed/",
    "indiewire": "https://www.indiewire.com/feed/",
    
    # Onedio - Türkçe İçerik
    "onedio_gundem": "https://onedio.com/Publisher/publisher-gundem.rss",
    "onedio_spor": "https://onedio.com/Publisher/publisher-spor.rss",
    "onedio_yazio": "https://onedio.com/Publisher/publisher-yazio.rss",
    "onedio_test": "https://onedio.com/Publisher/publisher-test.rss",
    "onedio_video": "https://onedio.com/Publisher/publisher-video.rss",
    "onedio_yemek": "https://onedio.com/Publisher/publisher-yemek.rss",
    "onedio_yasam": "https://onedio.com/Publisher/publisher-yasam.rss",
    "onedio_seyahat": "https://onedio.com/Publisher/publisher-seyahat.rss",
    "onedio_saglik": "https://onedio.com/Publisher/publisher-saglik.rss",
    "onedio_vitrin": "https://onedio.com/Publisher/publisher-vitrin.rss",
    "onedio_ekonomi": "https://onedio.com/Publisher/publisher-ekonomi.rss",
    "onedio_finans": "https://onedio.com/Publisher/publisher-finans.rss",
    "onedio_dizifilm": "https://onedio.com/Publisher/publisher-dizi+%26+film.rss",
    "onedio_tv": "https://onedio.com/Publisher/publisher-tv.rss",
    "onedio_goygoy": "https://onedio.com/Publisher/publisher-goygoy.rss",
    "onedio_magazin": "https://onedio.com/Publisher/publisher-magazin.rss",
    "onedio_gaming": "https://onedio.com/Publisher/publisher-gaming.rss",
    "onedio_teknoloji": "https://onedio.com/Publisher/publisher-teknoloji.rss",
    "onedio_egitim": "https://onedio.com/Publisher/publisher-egitim.rss",
    "onedio_kultur": "https://onedio.com/Publisher/publisher-genel+kultur.rss"
}

def fetch_reddit_json(url, name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        posts = []
        for child in data['data']['children']:
            post = child['data']
            # Sadece self/text postları al (görselleri filtrele)
            if post.get('is_self', False) or len(post['title']) > 20:
                posts.append({
                    'source': name,
                    'type': 'reddit',
                    'title': post['title'],
                    'score': post['score'],
                    'comments': post['num_comments'],
                    'subreddit': post['subreddit'],
                    'url': f"https://reddit.com{post['permalink']}",
                    'popularity': post['score'] + (post['num_comments'] * 2)
                })
        return posts
    except Exception as e:
        print(f"❌ Reddit hata ({name}): {e}")
        return []

def fetch_rss(url, name):
    try:
        feed = feedparser.parse(url)
        posts = []
        for entry in feed.entries[:15]:
            posts.append({
                'source': name,
                'type': 'rss',
                'title': entry.title,
                'score': 0,
                'comments': 0,
                'subreddit': '',
                'url': entry.link,
                'popularity': 100  # RSS için varsayılan
            })
        return posts
    except Exception as e:
        print(f"❌ RSS hata ({name}): {e}")
        return []

def main():
    all_data = []
    
    print("📡 RSS/JSON verileri çekiliyor...")
    
    for name, url in SOURCES.items():
        print(f"🔍 {name} kontrol ediliyor...")
        
        if '.json' in url:
            data = fetch_reddit_json(url, name)
        else:
            data = fetch_rss(url, name)
        
        all_data.extend(data)
        print(f"   ✅ {len(data)} kayıt bulundu")
    
    # CSV'ye kaydet
    csv_file = 'trend_data.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        if all_data:
            writer = csv.DictWriter(f, fieldnames=['source', 'type', 'title', 'score', 'comments', 'subreddit', 'url', 'popularity'])
            writer.writeheader()
            writer.writerows(all_data)
            print(f"\n✅ Toplam {len(all_data)} kayıt {csv_file}'ye yazıldı")
        else:
            print("\n⚠️ Hiç veri çekilemedi")
    
    # Özet JSON oluştur
    summary = {
        'last_update': datetime.now().isoformat(),
        'total_records': len(all_data),
        'sources': {}
    }
    
    for item in all_data:
        src = item['source']
        if src not in summary['sources']:
            summary['sources'][src] = 0
        summary['sources'][src] += 1
    
    with open('summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Özet: {summary}")

if __name__ == "__main__":
    main()
