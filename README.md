# 🇹🇷 Turkish Repo Showcase

**Tam Otomatik GitHub Repo Keşif ve Paylaşım Sistemi**

Bu proje, yüksek kaliteli GitHub projelerini otomatik olarak keşfeden, Türkçe özet ve açıklama üreten, Twitter'da paylaşan ve Jekyll tabanlı bir arşiv sitesinde saklayan bir "Headless Content Machine"dir.

## 🏗️ Mimari

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Discovery     │────▶│   AutoPoster    │────▶│   Jekyll Site   │
│   (discovery.py)│     │   (autoposter.py)│     │   (docs/)       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   GitHub API              Claude AI               GitHub Pages
   Hacker News             Twitter API
```

## ✨ Özellikler

- 🔍 **Otomatik Keşif**: GitHub Trending ve Hacker News'den kaliteli projeler bulur
- 🤖 **AI Filtreleme**: Claude AI ile "greater good" projelerini seçer (meme coinleri ve niche kütüphaneleri filtreler)
- 🇹🇷 **Türkçe İçerik**: Tüm özet ve açıklamalar profesyonel Türkçe ile üretilir
- 🖼️ **Hero Image**: README'den otomatik görsel çıkarır
- 🐦 **Twitter Paylaşımı**: Görsel + özet + hashtag'lerle tweet atar
- 📚 **Jekyll Arşiv**: Her proje için kalıcı blog yazısı oluşturur
- ⏰ **Günlük Çalışma**: GitHub Actions ile her gün otomatik çalışır

## 🚀 Kurulum

### 1. Repository'yi Fork'la

Bu repo'yu kendi GitHub hesabınıza fork'layın.

### 2. GitHub Pages'i Etkinleştir

1. Settings → Pages
2. Source: `Deploy from a branch`
3. Branch: `main`, Folder: `/docs`
4. Save

### 3. Secrets Ekle

Repository Settings → Secrets and variables → Actions → New repository secret:

| Secret Adı | Açıklama |
|------------|----------|
| `ANTHROPIC_API_KEY` | [Anthropic Console](https://console.anthropic.com/)'dan API key |
| `TWITTER_API_KEY` | Twitter Developer Portal - API Key |
| `TWITTER_API_SECRET` | Twitter Developer Portal - API Secret |
| `TWITTER_ACCESS_TOKEN` | Twitter Developer Portal - Access Token |
| `TWITTER_ACCESS_TOKEN_SECRET` | Twitter Developer Portal - Access Token Secret |

> **Not:** `GITHUB_TOKEN` otomatik sağlanır, eklemenize gerek yok.

### 4. Twitter API Ayarları

Twitter Developer Portal'da:
1. App'iniz için **Read and Write** izinleri ayarlayın
2. OAuth 1.0a aktif olmalı (media upload için gerekli)
3. User authentication settings kısmında callback URL ekleyin

## 📁 Dosya Yapısı

```
turkish-repo-showcase/
├── .github/
│   └── workflows/
│       └── daily_engine.yml    # GitHub Actions workflow
├── docs/                       # Jekyll site
│   ├── _config.yml            # Jekyll ayarları
│   ├── _posts/                # Blog yazıları (otomatik oluşur)
│   ├── assets/
│   │   └── images/            # Hero görselleri (otomatik iner)
│   └── index.html             # Ana sayfa
├── discovery.py               # Repo keşif scripti
├── autoposter.py              # İçerik üretim ve paylaşım scripti
├── requirements.txt           # Python bağımlılıkları
├── queue.txt                  # İşlenecek repo kuyruğu
├── history.txt               # İşlenmiş repo geçmişi
└── README.md
```

## 🔧 Manuel Çalıştırma

### Yerel Test

```bash
# Bağımlılıkları kur
pip install -r requirements.txt

# Ortam değişkenlerini ayarla
export ANTHROPIC_API_KEY="your-key"
export TWITTER_API_KEY="your-key"
export TWITTER_API_SECRET="your-secret"
export TWITTER_ACCESS_TOKEN="your-token"
export TWITTER_ACCESS_TOKEN_SECRET="your-secret"
export GITHUB_TOKEN="your-token"  # İsteğe bağlı, rate limit için

# Keşfi çalıştır
python discovery.py

# Paylaşımı çalıştır
python autoposter.py
```

### GitHub Actions Manuel Tetikleme

1. Actions sekmesine git
2. "🤖 Daily Content Engine" workflow'unu seç
3. "Run workflow" butonuna tıkla
4. İsteğe bağlı ayarları yap:
   - `skip_discovery`: Keşfi atla, sadece kuyruktan işle
   - `process_count`: Kaç repo işlenecek (varsayılan: 1)

## ⚙️ Yapılandırma

### Keşif Parametreleri (discovery.py)

```python
MIN_STARS = 50        # Minimum yıldız sayısı
MAX_CANDIDATES = 20   # Değerlendirilecek max repo
```

### AI Filtreleme Kriterleri

**EVET denen projeler:**
- Geliştirici araçları ve verimlilik artırıcılar
- Geniş kitlelere hitap eden kütüphaneler/framework'ler
- Eğitim ve öğrenme kaynakları
- Gerçek sorunları çözen yenilikçi projeler

**HAYIR denen projeler:**
- Kripto/meme coin/NFT projeleri
- Çok niş backend kütüphaneleri
- Terk edilmiş veya düşük kaliteli projeler
- Spam veya self-promotional repolar

## 📊 Workflow Zamanlaması

Varsayılan: Her gün 08:00 İstanbul saati (05:00 UTC)

Değiştirmek için `.github/workflows/daily_engine.yml` dosyasında:

```yaml
schedule:
  - cron: '0 5 * * *'  # UTC saati
```

## 🐛 Sorun Giderme

### Twitter Paylaşımı Başarısız

1. API key'lerin doğru olduğundan emin olun
2. App'in Read+Write izinlerine sahip olduğunu kontrol edin
3. OAuth 1.0a'nın aktif olduğunu doğrulayın

### Görsel İndirilemiyor

Bazı repo'lar görselleri harici servislerden (CDN) sunuyor olabilir. Script en fazla 5 görsel URL'si dener.

### Queue Boş Kalıyor

- GitHub API rate limit'e takılmış olabilirsiniz
- `GITHUB_TOKEN` ekleyerek rate limit'i artırın
- Filtreleme kriterleri çok sıkı olabilir

## 📝 Lisans

MIT License - Dilediğiniz gibi kullanın ve değiştirin.

## 🤝 Katkıda Bulunma

Pull request'ler memnuniyetle karşılanır! Özellikle:
- Daha iyi Türkçe içerik üretimi
- Ek kaynak entegrasyonları (Product Hunt, Reddit, vb.)
- Gelişmiş filtreleme kriterleri

---

**Not:** Bu proje [Claude AI](https://www.anthropic.com) ve [GitHub Actions](https://github.com/features/actions) kullanmaktadır.
