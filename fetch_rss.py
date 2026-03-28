import feedparser
import requests
import json
import csv
import os
import re
import langdetect
from datetime import datetime
from collections import Counter

# RSS ve JSON kaynakları (KAYNAK, URL, KATEGORI, AGIRLIK)
SOURCES = {
    # Reddit - Tartışma odaklı (Yüksek etkileşim = Yüksek puan)
    "reddit_ask": {
        "url": "https://www.reddit.com/r/AskReddit/hot.json?limit=50",
        "kategori": "Sosyal/Tartışma",
        "agirlik": 1.5,
        "tip": "reddit"
    },
    "reddit_unpopular": {
        "url": "https://www.reddit.com/r/unpopularopinion/hot.json?limit=50",
        "kategori": "Sosyal/Fikir",
        "agirlik": 1.3,
        "tip": "reddit"
    },
    "reddit_wouldyourather": {
        "url": "https://www.reddit.com/r/WouldYouRather/hot.json?limit=50",
        "kategori": "Sosyal/Oyun",
        "agirlik": 1.4,
        "tip": "reddit"
    },
    "reddit_polls": {
        "url": "https://www.reddit.com/r/polls/hot.json?limit=50",
        "kategori": "Sosyal/Anket",
        "agirlik": 1.4,
        "tip": "reddit"
    },
    "reddit_funny": {
        "url": "https://www.reddit.com/r/funny/hot.json?limit=50",
        "kategori": "Eğlence/Mizah",
        "agirlik": 1.2,
        "tip": "reddit"
    },
    "reddit_movies": {
        "url": "https://www.reddit.com/r/movies/hot.json?limit=50",
        "kategori": "Sinema/Film",
        "agirlik": 1.3,
        "tip": "reddit"
    },
    "reddit_gaming": {
        "url": "https://www.reddit.com/r/gaming/hot.json?limit=50",
        "kategori": "Oyun/Genel",
        "agirlik": 1.3,
        "tip": "reddit"
    },
    "reddit_technology": {
        "url": "https://www.reddit.com/r/technology/hot.json?limit=50",
        "kategori": "Teknoloji/Haber",
        "agirlik": 1.2,
        "tip": "reddit"
    },
    "reddit_food": {
        "url": "https://www.reddit.com/r/food/hot.json?limit=50",
        "kategori": "Yaşam/Yemek",
        "agirlik": 1.2,
        "tip": "reddit"
    },
    "reddit_sports": {
        "url": "https://www.reddit.com/r/sports/hot.json?limit=50",
        "kategori": "Spor/Genel",
        "agirlik": 1.3,
        "tip": "reddit"
    },
    "reddit_music": {
        "url": "https://www.reddit.com/r/Music/hot.json?limit=50",
        "kategori": "Müzik/Genel",
        "agirlik": 1.3,
        "tip": "reddit"
    },
    "reddit_tv": {
        "url": "https://www.reddit.com/r/television/hot.json?limit=50",
        "kategori": "Dizi/TV",
        "agirlik": 1.3,
        "tip": "reddit"
    },
    
    # Pop Kültürü & Eğlence
    "buzzfeed_ent": {
        "url": "https://www.buzzfeed.com/entertainment.xml",
        "kategori": "Eğlence/Listicle",
        "agirlik": 1.0,
        "tip": "rss"
    },
    "vulture": {
        "url": "https://www.vulture.com/rss/all.xml",
        "kategori": "Kültür/Sanat",
        "agirlik": 1.1,
        "tip": "rss"
    },
    "theringer": {
        "url": "https://www.theringer.com/rss/pop-culture/index.xml",
        "kategori": "Kültür/Pop",
        "agirlik": 1.1,
        "tip": "rss"
    },
    "eonline": {
        "url": "https://www.eonline.com/rss/feed/index.xml",
        "kategori": "Magazin/Ünlü",
        "agirlik": 1.0,
        "tip": "rss"
    },
    "mentalfloss": {
        "url": "https://www.mentalfloss.com/rss.xml",
        "kategori": "Eğlence/Bilgi",
        "agirlik": 0.9,
        "tip": "rss"
    },
    "boredpanda": {
        "url": "https://www.boredpanda.com/feed/",
        "kategori": "Eğlence/Viral",
        "agirlik": 0.9,
        "tip": "rss"
    },
    
    # Oyun
    "polygon": {
        "url": "https://www.polygon.com/rss/index.xml",
        "kategori": "Oyun/Haber",
        "agirlik": 1.1,
        "tip": "rss"
    },
    "kotaku": {
        "url": "https://kotaku.com/rss",
        "kategori": "Oyun/Kültür",
        "agirlik": 1.1,
        "tip": "rss"
    },
    "ign": {
        "url": "https://www.ign.com/rss/articles.xml",
        "kategori": "Oyun/İnceleme",
        "agirlik": 1.1,
        "tip": "rss"
    },
    
    # Teknoloji
    "theverge": {
        "url": "https://www.theverge.com/rss/index.xml",
        "kategori": "Teknoloji/Haber",
        "agirlik": 1.0,
        "tip": "rss"
    },
    "producthunt": {
        "url": "https://www.producthunt.com/feed",
        "kategori": "Teknoloji/Ürün",
        "agirlik": 1.2,
        "tip": "rss"
    },
    "mashable": {
        "url": "https://mashable.com/feeds/rss/all",
        "kategori": "Teknoloji/Eğlence",
        "agirlik": 1.0,
        "tip": "rss"
    },
    
    # Global Haber & Magazin
    "tmz": {
        "url": "https://www.tmz.com/rss.xml",
        "kategori": "Magazin/Haber",
        "agirlik": 1.0,
        "tip": "rss"
    },
    "variety": {
        "url": "https://variety.com/feed/",
        "kategori": "Sinema/Endüstri",
        "agirlik": 1.1,
        "tip": "rss"
    },
    "hollywoodreporter": {
        "url": "https://www.hollywoodreporter.com/feed/",
        "kategori": "Sinema/Haber",
        "agirlik": 1.1,
        "tip": "rss"
    },
    "rollingstone": {
        "url": "https://www.rollingstone.com/feed/",
        "kategori": "Müzik/Kültür",
        "agirlik": 1.1,
        "tip": "rss"
    },
    "billboard": {
        "url": "https://www.billboard.com/feed/",
        "kategori": "Müzik/Liste",
        "agirlik": 1.2,
        "tip": "rss"
    },
    "pitchfork": {
        "url": "https://pitchfork.com/rss/news",
        "kategori": "Müzik/İnceleme",
        "agirlik": 1.1,
        "tip": "rss"
    },
    "collider": {
        "url": "https://collider.com/feed/",
        "kategori": "Sinema/Haber",
        "agirlik": 1.0,
        "tip": "rss"
    },
    
    # Onedio - Türkçe İçerik (Yüksek ağırlık çünkü hedef kitle TR)
    "onedio_gundem": {
        "url": "https://onedio.com/Publisher/publisher-gundem.rss",
        "kategori": "Haber/Gündem",
        "agirlik": 1.3,
        "tip": "rss"
    },
    "onedio_magazin": {
        "url": "https://onedio.com/Publisher/publisher-magazin.rss",
        "kategori": "Magazin/Ünlü",
        "agirlik": 1.4,
        "tip": "rss"
    },
    "onedio_dizifilm": {
        "url": "https://onedio.com/Publisher/publisher-dizi+%26+film.rss",
        "kategori": "Sinema/Dizi",
        "agirlik": 1.4,
        "tip": "rss"
    },
    "onedio_gaming": {
        "url": "https://onedio.com/Publisher/publisher-gaming.rss",
        "kategori": "Oyun/Eğlence",
        "agirlik": 1.3,
        "tip": "rss"
    },
    "onedio_teknoloji": {
        "url": "https://onedio.com/Publisher/publisher-teknoloji.rss",
        "kategori": "Teknoloji/Haber",
        "agirlik": 1.3,
        "tip": "rss"
    },
    "onedio_spor": {
        "url": "https://onedio.com/Publisher/publisher-spor.rss",
        "kategori": "Spor/Haber",
        "agirlik": 1.3,
        "tip": "rss"
    },
    "onedio_yemek": {
        "url": "https://onedio.com/Publisher/publisher-yemek.rss",
        "kategori": "Yaşam/Yemek",
        "agirlik": 1.2,
        "tip": "rss"
    },
    "onedio_yasam": {
        "url": "https://onedio.com/Publisher/publisher-yasam.rss",
        "kategori": "Yaşam/Tarz",
        "agirlik": 1.2,
        "tip": "rss"
    },
    "onedio_test": {
        "url": "https://onedio.com/Publisher/publisher-test.rss",
        "kategori": "Eğlence/Test",
        "agirlik": 1.3,
        "tip": "rss"
    },
    "onedio_goygoy": {
        "url": "https://onedio.com/Publisher/publisher-goygoy.rss",
        "kategori": "Eğlence/Goygoy",
        "agirlik": 1.2,
        "tip": "rss"
    },
}

# Kategori alt türleri için anahtar kelimeler
KATEGORI_ANAHTARLARI = {
    "Spor": {
        "Futbol": ["messi", "ronaldo", "futbol", "galatasaray", "fenerbahçe", "beşiktaş", "premier", "laliga", "şampiyonlar ligi"],
        "Basketbol": ["nba", "lebron", "jordan", "basketbol", "euroleague"],
        "Tenis": ["federer", "nadal", "djokovic", "tenis", "wimbledon"],
        "Voleybol": ["voleybol", "filenin sultanları"],
        "Motor": ["f1", "formula 1", "verstappen", "hamilton", "yarış"]
    },
    "Müzik": {
        "Pop": ["taylor swift", "beyonce", "pop", "billie eilish", "ed sheeran"],
        "Rap/Hip-Hop": ["drake", "kendrick", "eminem", "rap", "hip-hop", "trap"],
        "Rock": ["rock", "metal", "indie rock"],
        "K-Pop": ["bts", "blackpink", "k-pop", "kpop"],
        "Türkçe": ["tarkan", "hadise", "aleyna", "türkçe pop", "arabesk"]
    },
    "Sinema": {
        "Marvel": ["marvel", "avengers", "iron man", "spiderman", "deadpool"],
        "DC": ["dc", "batman", "superman", "joker"],
        "Netflix": ["netflix", "dizi", "breaking bad", "stranger things"],
        "Film": ["oscar", "film", "sinema", "yönetmen"]
    },
    "Teknoloji": {
        "Mobil": ["iphone", "samsung", "android", "xiaomi", "telefon"],
        "Bilgisayar": ["macbook", "laptop", "pc", "windows", "apple silicon"],
        "Oyun": ["playstation", "xbox", "nintendo", "console"],
        "Yazılım": ["app", "uygulama", "ai", "yapay zeka", "chatgpt"]
    }
}

def detect_language(text):
    """Dil tespiti"""
    try:
        if not text or len(text) < 10:
            return "unknown"
        lang = langdetect.detect(text)
        return lang
    except:
        return "unknown"

def detect_subcategory(title, main_category):
    """Alt kategori tespiti"""
    title_lower = title.lower()
    
    if main_category in KATEGORI_ANAHTARLARI:
        for subcat, keywords in KATEGORI_ANAHTARLARI[main_category].items():
            if any(kw in title_lower for kw in keywords):
                return subcat
    
    # Ana kategoriden tahmin et
    for cat, subs in KATEGORI_ANAHTARLARI.items():
        for subcat, keywords in subs.items():
            if any(kw in title_lower for kw in keywords):
                return f"{cat}/{subcat}"
    
    return "Genel"

def calculate_popularity_reddit(score, comments, upvote_ratio=0.9):
    """Reddit için popülerlik hesaplama"""
    # Temel puan
    base = score + (comments * 3)
    
    # Yorum/oy oranı (tartışma yoğunluğu)
    engagement = 1 + (comments / max(score, 1))
    
    # Hot sıralaması bonusu (zaten popüler)
    hot_bonus = 1.2
    
    return int(base * engagement * hot_bonus)

def calculate_popularity_rss(source_agirlik, mention_count=1):
    """RSS için popülerlik hesaplama"""
    # RSS'te doğrudan sayı yok, kaynak ağırlığına göre
    base = 100 * source_agirlik
    
    # Birden fazla kaynakta geçiyorsa bonus
    cross_bonus = 1 + (mention_count * 0.2)
    
    return int(base * cross_bonus)

def fetch_reddit_json(source_key, config):
    """Reddit JSON verisi çek"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        r = requests.get(config["url"], headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        posts = []
        
        for child in data['data']['children']:
            post = child['data']
            
            # İçerik varsa al (kısalt)
            content = post.get('selftext', '')[:500] if post.get('is_self') else ''
            
            # Popülerlik hesapla
            pop_score = calculate_popularity_reddit(
                post['score'], 
                post['num_comments'],
                post.get('upvote_ratio', 0.9)
            )
            
            # Ana kategori
            main_cat = config["kategori"].split('/')[0]
            
            posts.append({
                'kaynak': source_key,
                'kaynak_tipi': 'Reddit',
                'baslik': post['title'],
                'icerik': content,
                'populerlik_puani': pop_score,
                'populerlik_kaynagi': f"Upvote: {post['score']}, Yorum: {post['num_comments']}",
                'dil': detect_language(post['title'] + ' ' + content),
                'kategori_ana': main_cat,
                'kategori_alt': detect_subcategory(post['title'], main_cat),
                'url': f"https://reddit.com{post['permalink']}",
                'zaman': datetime.now().isoformat()
            })
        return posts
    except Exception as e:
        print(f"❌ Reddit hata ({source_key}): {e}")
        return []

def fetch_rss(source_key, config):
    """RSS verisi çek"""
    try:
        feed = feedparser.parse(config["url"])
        posts = []
        
        for entry in feed.entries[:15]:
            # İçerik özetini al
            content = entry.get('summary', entry.get('description', ''))[:500]
            
            # Popülerlik hesapla
            pop_score = calculate_popularity_rss(config["agirlik"])
            
            # Ana kategori
            main_cat = config["kategori"].split('/')[0]
            
            posts.append({
                'kaynak': source_key,
                'kaynak_tipi': 'RSS',
                'baslik': entry.title,
                'icerik': content,
                'populerlik_puani': pop_score,
                'populerlik_kaynagi': f"Kaynak ağırlığı: {config['agirlik']}",
                'dil': detect_language(entry.title + ' ' + content),
                'kategori_ana': main_cat,
                'kategori_alt': detect_subcategory(entry.title, main_cat),
                'url': entry.link,
                'zaman': datetime.now().isoformat()
            })
        return posts
    except Exception as e:
        print(f"❌ RSS hata ({source_key}): {e}")
        return []

def main():
    all_data = []
    print(f"[{datetime.now()}] 🚀 Veri çekimi başlıyor...")
    
    for source_key, config in SOURCES.items():
        print(f"🔍 {source_key} ({config['kategori']})...")
        
        if config["tip"] == "reddit":
            data = fetch_reddit_json(source_key, config)
        else:
            data = fetch_rss(source_key, config)
        
        all_data.extend(data)
        print(f"   ✅ {len(data)} kayıt")
    
    # CSV dosya adı: YılAyGünSaatDakikaSaniye_BBRssToCsv.csv
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    csv_filename = f"{timestamp}_BBRssToCsv.csv"
    
    # CSV yaz
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        if all_data:
            writer = csv.DictWriter(f, fieldnames=[
                'kaynak', 'kaynak_tipi', 'baslik', 'icerik', 
                'populerlik_puani', 'populerlik_kaynagi',
                'dil', 'kategori_ana', 'kategori_alt',
                'url', 'zaman'
            ])
            writer.writeheader()
            writer.writerows(all_data)
            print(f"\n✅ {csv_filename} oluşturuldu: {len(all_data)} kayıt")
        else:
            print("\n⚠️ Hiç veri çekilemedi")
    
    # Özet JSON
    summary = {
        'dosya_adi': csv_filename,
        'son_guncelleme': datetime.now().isoformat(),
        'toplam_kayit': len(all_data),
        'kaynaklar': {}
    }
    
    for item in all_data:
        src = item['kaynak']
        if src not in summary['kaynaklar']:
            summary['kaynaklar'][src] = 0
        summary['kaynaklar'][src] += 1
    
    with open('summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Özet: {len(all_data)} kayıt, {len(summary['kaynaklar'])} kaynak")
    print(f"📁 Dosya: {csv_filename}")

if __name__ == "__main__":
    main()
